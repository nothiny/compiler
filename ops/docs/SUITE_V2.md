# 开发语料 v2:500 算子 / 2893 case

> **已被 v3 取代。** v3 (`SUITE_V3.md` + `SUBSET.md`) 把语料改成「声明的推理子集」:
> 前向-only(去掉 106 个 backward,其中 64 个在 v2 里)、去掉 fp8/tf32/`input_precision`、
> 按结构收敛到 1000 个池算子,工作输入仍是 500(400 dev + 100 perf)/1545 case,
> held-out 是池中另外 500 个。本文保留为 v2 的历史记录。

目标不是"更多算子",而是**用最少的程序覆盖最多的可复用编译器能力**,并留出干净的
holdout。本文是审计、分类学、选区方法、验证状态、评估协议与时间估计的汇总;
机器可读版本是 [`../suite/manifest.json`](../suite/manifest.json),逐算子特征表是
[`COVERAGE_MATRIX.md`](COVERAGE_MATRIX.md)。

## 0. 结果一览

| | 值 |
|---|---|
| 开发语料(dev) | **400 算子 / 1717 case**(多数维度 <=128;41 个保留 257 的尾块用例,9 个保留上游 600-4100 宽度) |
| 性能车道(perf) | **100 算子 / 1176 case**(`suite/perf/`,真尺寸,不进正确性 gate) |
| 合计 | **500 算子 / 2893 case** |
| 编译身份(meta 口径) | **1422**(cases/identity = 2.03;去掉 shape 派生 constexpr 后 1217) |
| 语义特征覆盖 | **76 / 76** |
| 特征交互覆盖 | **1649 / 1663** |
| 已验证 | stock Triton 3.8,2893 / 2893 PASS |

构成(历史选材事实;这些来源池不在本镜像内):现有 basic/medium/hard 保留 242
(去重后),从 hidden 池选入 **162**(155 + 2026-10-23 补齐的 7 个,见 §4.1),bench 100 作为性能车道。未入选的 1088 个
hidden 算子构成 holdout。`ops/` 目录本身是自包含的,`suite/` 就是全部输入。

## 1. 审计:筛选前的 350 个开发算子在覆盖什么、冗余在哪(历史记录)

用 AST 抽特征(`harness/opslib/features.py`,不执行、不看算子名),对 1659 个
候选(350 + 1309)统计:

- **特征分布极度集中**:`arith.add` 1653、`mem.store` 1639、`mem.load` 1621、
  `construct.arange` 1598 —— 前 6 个特征覆盖 >90% 的算子,而
  `red.sort`(2)、`red.histogram`(2)、`red.scan`(5)、`shape.broadcast`(5)、
  `mem.padding`(5)、`red.keep_dims`(6)、`index.rank3plus`(3)、
  `hint.static_assert`(3) 几乎是空白。
- **冗余**:按 (特征集 + 精确算子签名 + tile 秩) 指纹,1659 个候选只有 1379 个
  不同指纹 —— **280 个是近重复**(同代码不同名、同结构不同注释)。
- **覆盖率饱和点**:贪心最大覆盖在 **74 个算子**就把 76 个特征和 1662/1663 个
  交互全覆盖了。结论:**"再多 100 个逐元素算子"的边际覆盖是 0**;
  400 个的价值在"同能力、不同写法"的结构多样性,不在特征数。
- **shape 规模污染**:hidden 池里大量算子带性能尺寸(`16384`、`256x512x2048`),
  既拖编译也拖 NumPy 参考;已统一裁到 `<=128`(41 个保留 257 的尾块维、9 个上游大宽度,见 §4)。

## 2. 分类学(76 个特征 + 交互)

| 维度 | 特征 |
|---|---|
| A 算术/类型 | `arith.{add,sub,mul,div,mod,pow,neg}`、`cmp.compare`、`logic.{bool,bitwise}`、`math.{transcendental,sqrt_rsqrt,abs,round,clamp}`、`cast.{explicit,to_fp32,to_fp16}`、`dtype.{int,uint}` |
| B 内存/索引 | `mem.{load,store,masked_load,masked_store,other,boundary_check,padding,blockptr,cache_hint,volatile,alignment_hint,atomic}`、`index.{rank2,rank3plus,multi_offset}` |
| C 形状/布局 | `shape.{reshape,trans,expand,broadcast,split_join}`、`construct.{arange,zeros,full}`、`select.where` |
| D 归约/依赖 | `red.{sum,maxmin,argmaxmin,custom,scan,sort,histogram,axis,multi_axis,keep_dims}` |
| E 控制流 | `flow.{loop,dynamic_range,static_range,tl_range,while,if,if_pid}`、`tune.{autotune,loop_pragma}` |
| F 矩阵/分块 | `dot.{matmul,acc,precision_kw,out_dtype}`、`hint.static_assert` |
| G 组合能力(派生) | `pat.{softmax,normalize,matmul_epilogue,dot_reduce,reduce_broadcast,masked_both,blockptr_boundary,k_loop,persistent_reduce}` |
| H 高级 | `mem.atomic`、`red.scan`、`red.sort`、`red.histogram`、`misc.rng`、`misc.barrier` |

**交互** = 一个算子里出现的特征对(如 `red.sum+mem.masked_load`、
`dot.matmul+shape.trans`)。它比单特征更能暴露"实现对了 A 也对了 B,但 A∘B 错"
这类缺陷 —— 那也是编译器泛化失败最常见的形态。

**明确不支持**(按 `AGENTS.md`,不进语料):`dot_scaled`/fp4、int4、
`inline_asm_elementwise`、TMA descriptor、`tl.extra`/`tl.math`/libdevice、
`tl.tanh`/`tl.pow`/`tl.bool`。抽取器把这 47 个文件直接标为 excluded。

## 3. 选区方法(可重跑)

选材脚本 `select_suite.py` / `materialize_suite.py` / `shrink_shapes.py` /
`expand_cases.py` **不在本镜像内**(它们需要 `basic/ medium/ hard/ hidden/` 这些池),
只在语料维护仓库里运行。复现方法(维护仓库内):

```bash
python3 harness/tools/select_suite.py --fast --target 400 \
        --seed-pool basic,medium,hard --fill-pool hidden --keep-bench \
        --manifest suite/manifest.json --report docs/COVERAGE_MATRIX.md
```

1. **seed**:现有语料(basic/medium/hard,共 250)按指纹去重后保留 242,保住已验证内容;
2. **fill**:从 hidden 池按 `Σ 1/(1+log2 频次)`(稀有特征权重)/ case 数的静态分排序,
   每个"特征集"至多 3 个,取 158 个 → dev 400;
3. **bench** 100 作为性能车道整体并入 → 500;
4. 全过程约 10 s(单遍排序,无迭代式多样性优化 —— 那版慢 30 倍且收益不可见)。

选中的算子**文件级复制**进 `suite/dev`、`suite/perf`,原文逐字节不变,
`provenance.json` 记录 origin 与 sha256,便于检测漂移。

## 4. 验证状态(stock Triton 3.8,不涉及任何自研编译器)

```bash
python3 harness/compiler_api/run_cases.py --device cuda --allow-torch \
    --manifest suite/manifest.json --jobs 8 --case-timeout 60
```

| 项 | 结果 |
|---|---|
| 首轮 2930 case | PASS 2850,失败 80(`CASE_FAIL` 57 / `LAUNCH_FAIL` 17 / `MISMATCH` 6) |
| 失败原因 | 全是**裁剪 shape 撞上算子自身约束**:按 shape 查表的 `KeyError`(如 `(124,)`)、`K/M 必须是 BLOCK=16 的倍数`、少数数值不符 |
| 处理 | 从 `SHAPES` 删除对应 shape(不使用"跳过/放宽容差"),受影响的 22 个算子复验 **70/70 PASS**;7 个算子所有 shape 都不可用 → 从语料剔除 |
| 最终 | **2850 / 2850 PASS** |

**没有验证的**:目标硬件上的可执行性、编译期行为(newops/updateops)——按你的要求,
这一轮只用 Triton 3.8 验语义正确性。

### 4.1 补齐到 500(2026-10-23)

§4 剔除 7 个后 dev 是 393 个;从 hidden 池补回 7 个,dev = 400、合计 500。

| 算子 | 选它的理由 | case |
|---|---|---:|
| `reversed_cumsum` | 新交互 `arith.neg+tune.autotune`(选材打分里唯一还能补上新交互、且不违反尺寸规则的候选) | 7 |
| `nanmedian_ascend_histogram_count_kernel` | `red.histogram` 原来只有 1 个算子覆盖,池中唯一的另一个 | 6 |
| `blocked_jacobi_rank_kernel` | 结构多样性(选材第二阶段:离已选算子最远、成本低) | 6 |
| `tril_inplace_zero_tile_kernel` | 同上;原地写回 + 三角掩码 | 7 |
| `triton_conv2d_fwd` | 同上;卷积 + 动态循环 | 7 |
| `lu_factor_info_kernel` | 同上;按轴归约 + 选主元 | 6 |
| `triangular_inverse_kernel` | 同上;上/下三角两条分支 + 动态循环(shape 是选择阶数与分支的编号,不是张量轴) | 4 |

没选的高分候选:两个 matmul(`make_case` 把 N 写死为 32768,违反 dot 类 `M,N,K <= 128`)、
`matmul_4096_kernel_1b0e3d4b`(`BLOCK_N=256` 且无掩码,尺寸至少 256)、`flat_radix_init_kernel`
(只写初值,shape 只改一个 constexpr,每个 shape 都是新身份)、`fht_kernel_256_1d_native`(不读 shape,
只有 1 个 case)、以及只写一个标量的几个 1-case kernel。

case 按维护仓库里 `expand_cases.py` 的规则扩充(该脚本不在本镜像内):只加 shape、不加 dtype,每个新 shape 是已有 shape
的小幅变化(退化轴、奇数尾块、非整除),全部语义尺寸。`lu_factor_info_kernel` 的 case 层要求
batch >= 3,不满足的 3 个 shape 换成了满足的(不改算子)。验证:43 个 case 在 `--device cuda`
(`reversed_cumsum` 加 `--allow-torch`,autotune 的已知例外)与 `--device torch-gpu` 上全部 PASS。
文件按字节从 hidden 复制,只改 `SHAPES`;`suite/dev/provenance.json` 记录来源与来源文件的 sha256。

## 5. 评估协议(dev vs holdout)

- **dev** = `suite/`(500 算子),编译器开发只能看这些;
- **holdout** = hidden 池中未被选中的 **1088** 个(池中现有 1250 个,按 `origin` 路径排除 162 个已入选者);
- 抽样方式:按**算子族**与**特征交互**分层抽样,不要随机抽近重复变体
  (随机会高估泛化);
- 评估指标:编译成功率、正确率、按特征/交互分桶的失败率、以及"未见交互"的失败率;
- **不得**把 holdout 内容并入 dev;`suite/manifest.json` 的 `origin` 字段就是排除清单。

## 6. 时间估计

编译身份 1422(meta),2893 case。三个后端的估计:

| 后端 | 编译次数 | 单线程 | 16 并发 | 依据 |
|---|---:|---:|---:|---|
| stock Triton 3.8 | 1422 | **8–12 min** | **1.5–2 min** | basic 组实测 264 身份 96 s(0.36 s/身份) |
| updateops(按身份) | 1422 | **30–40 min** | **4–6 min** | 瘦身后 updateops ≈ 1.2–1.8 s/身份 |
| newops(按 case,grid 进键) | 2893 | **40–50 min** | **5–7 min** | 实测 ~0.9–1.1 s/case |

前提:**shape 已裁到语义尺寸**。若不裁(hidden 原始 shape),单个算子就能吃掉
100–1200 s(newops 实测 `17x33x1000` = 1193 s),整轮变小时级。

## 7. 局限

1. 特征/交互是 AST 近似,不证明语义;`pat.*` 是启发式派生,不能当规格用。
2. 覆盖饱和(74 个算子)说明"再加算子"的边际收益递减 —— 400 个的价值是结构多样性,
   不是覆盖率;这一点只能靠 holdout 实验验证,不能靠本文断言。
3. 裁 shape 后少数算子失去了大 K / 大 seq 路径;真尺寸只在 `suite/perf/` 出现,
   所以"大 shape 下的编译问题"不在这个语料的证据范围里。
4. `suite/` 中的 162 个算子来自 hidden 池,若将来要用 hidden 做随机测试,
   必须按 `origin` 排除它们(manifest 已记录)。
