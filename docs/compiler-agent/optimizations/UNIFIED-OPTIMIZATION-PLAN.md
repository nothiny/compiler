# 统一优化计划：跨家族动态指令开销削减（softmax / elementwise / attention / matmul）

> 状态：**计划**（分析阶段产物；主树零代码改动，引擎状态未触碰）。本文把四个家族轮的
> 优化思路去重合并为一个可执行的统一序列：matmul（已完成一轮，`0f84bdc` + `f69be1d`
> 已合入）、attention（方案 + 6 case 实测画像）、softmax（候选 #1 已完整设计并双重验证）、
> elementwise（vector-poly 已设计 + 数值验证，INDEX 中状态 designed+validated/未实施）。
> 实施等待用户指令；实施时以**当时 HEAD** 重新锚定全部基线（T044 修复波在飞行中）。
>
> 判据口径：QEMU 模拟执行代理指标——**每调用 guest 动态指令数**（主指标；校准过的
> QEMU 10 per-insn 插件 + `--repeats` 稳态差分），spill/reload 次数与流量、冗余访存
> （副指标）。不以 QEMU 墙钟为判据、不换算真机加速比、不主张任何 engine gate / G9；
> correctness_only 验收原样保留。结论只表述"动态指令开销降低 X% / spill 流量减少 Y"，
> 附逐 case 前后表；QEMU 墙钟仅辅助记录。

## 0. 不变量（全程有效）

- 不改 case / reference / 容差；**无算子名分派**（守卫一律是结构性的：`(fn, sew)`、
  语义类 × IR 形态，`tools/check_no_name_dispatch.py --witness` 必须失败）。
- 整数 / 索引 / 布尔结果精确；浮点遵守每个 case 声明的比较策略。
- 每个变换一个行为级开关、**进 artifact 身份**（缓存天然隔离），加 git revert 构成
  回退双保险（L3/L14）。
- `/tmp` 探针纪律先行（L4/L6）：数值网格扫描 + 固定 QEMU
  （jdsk-qemu-10.0.2，`-cpu max,vlen=1024,elen=64,vext_spec=v1.0`）执行探针双跑；
  原型不达标不进树。
- 三方对照：baseline / 开关-off / 开关-on 同身份指标对比；off 位与基线的
  program.S 逐行（asm_join 字节）同一性是对照证据。
- 修复流（engine T044/T045+ 的 correctness 轨道）与本优化流**分离**：优化轮的正确性
  口径是"自家 scoped scan 全 PASS + 全量 2734 无新增 non-PASS（存量参照组明确列出）"，
  不掩盖、不替代修复流。
- 记录：`optimizations/<family>/candidates/<name>/RECORD.md` + ROUND.md + INDEX.md
  更新；收尾用 compiler-design-retrospective 复盘（lessons 从 L17 续编号）。

## 1. 优化思路总结

### 1.1 一句话

四个家族每调用动态指令的 **85-95% 是编译器自产的包装代码**，真实计算（向量算术 +
IME）只占 5-10%（最极端：flash_varlen f16 每调用 95.3 万条指令，其中 IME 矩阵指令
仅 320 条，0.03%）。两大结构性根因：

1. **vmath 逐元素 libm 展开（第一瓶颈）**：`math.exp/exp2/log/log2/erf/floor` 无向量
   形式 → lowering 发 `vmath` MIR op → `a100c/backend/emit.py:1073` 展开为"栈中转 +
   逐元素标量循环 + libm 调用（PLT + 函数体，fp32 走 double 内部路径）"，每元素
   ~40-150 条动态指令。vmath 普查（499 identities）：expf 72 ids / 19 算子、
   logf 34/7、floorf 19/3、exp2f 15/3、erff 13/4、sin/cos ~19/3。
2. **lowering 之后的循环体内重物化**（TIR 优化不可见，TIR LICM fired=0 已证）：
   sconst 常量重物化 15-25%（`vectorize.py` 纯标量树每用重算）、vsetvli 区域 churn
   7-15%、地址乘法树每迭代重建 8-15%、slt+bne 谓词对、分配器"块入口存、每用前
   reload"2-10%（`allocate.py:644`）、operator_entry 派发骨架 10-15%。

次要类：窄数据逐 lane 回退（fp16 2D 仿射访存，10-30%，T014 QEMU 缺陷规避）、
pack/staging 循环残余（B-pack 已修，A-staging 与每列 ~12 条准备仍在）。

### 1.2 瓶颈分类学（四轮实测汇总）

| 开销类 | 实测占比（各 case 范围） | 根因层 | 对应候选 |
|---|---|---|---|
| vmath 逐元素 libm 调用 | softmax-f16 84.2%+PLT 5.0%；elementwise erf/gelu ~89%；attention 2-26%（exp-heavy 类决定性） | lowering 发 vmath + emit 标量展开 | **W1** |
| sconst 常量重物化 | 15-27%（linear-dropout 4.09M/15.3M） | lowering 循环体内合成；TIR 看不见 | W3（+W2 策略层） |
| vsetvli 区域 churn | 7-15%（linear-dropout 2.11M=14%） | 混合宽度 pass 每转换重开区域 | W3 |
| 标量地址/mask 算术 | 8-15%（vbinx 43.6k/call 等） | 每访问整树重建（L13） | W3 / W4 |
| 分支谓词物化（slt+bne 对） | 9216-73728 次/调用 | 计数循环界已知仍每迭代判 | W3 |
| reload/remat（"frame"[op-1]） | 2-10%（522K/调用，已归因分配器重物化） | allocate.py 每用前 reload + lowering 每用重算 | W2-P2 |
| 窄数据逐 lane 回退 | fp16 case 10-30% | T014 QEMU e64 索引缺陷规避 | W2-C8 |
| operator_entry 骨架 | 10-15%（未归属） | 疑 grid 求值/program-id/范围循环脚手架 | W4-C6 |
| pack/staging 循环 | matmul pack-b 曾 31%（已修）；A-staging 残余 | 逐列护栏+窄化+vsetvli | W2-P1b |

### 1.3 方法论（四轮共用，全部已建好、零新建）

观测链：QEMU 全量指令插件 → `insn_manifest.py` pc 级 origin 联结 →
`collect_metrics.py` 稳态差分 → `analyze_blocks.py` 块归属 → `compare_metrics.py`
前后对比（`tools/profiling/`，口径文档在 `matmul/tooling/TOOLING.md`）。
模型可信度校准：matmul 轮"手工变换 = 编译器变换上限"实验（预测 -27.5% vs 实测
-28.0%）通过，后续模型估算可信。

## 2. 统一候选清单（去重后）

**关键去重点**：vmath 向量多项式被三个 session 各自设计了一遍（attention C1 =
TIR-pass 版 / softmax 候选 #1 / elementwise vector-poly），开关名与覆盖面都不同
（`A100C_PASS_TRANSCENDENTAL` / `A100C_MATH_APPROX` / `A100C_VMATH_LIBM`）。
**必须收敛为一个实现**，避免 `vectorize.py` 冲突面三分。建议以 lowering-local 版为
基底（softmax #1 + elementwise 并集）：零契约变更、emit/legalise/select/allocate
零改动、验证最充分；attention 的 TIR-pass 版搁置（TIR constprop 已在 lowering 前
折叠常量 exp，pass 化无额外收益，却多一次契约修订）。

### W1 · 统一 vmath 向量多项式（最高优先；零契约变更；2× 目标主承担者）

- **位置**：`a100c/lower/vectorize.py::_vector_math_unary`（sqrt/rsqrt 早退之后、
  fn-map 之前），按 `(fn, sew)` 结构分派。
- **覆盖**：`exp/exp2/log/log2/erf/floor` @ sew==32（三份设计的并集）；
  `sin/cos/ceil` 与 sew==64（fp64）**留 vmath/libm**（本轮证据只覆盖 fp32）。
  `_scalar_math_unary` 经 splat-compute-extract 自动获得同行为。
- **算法**：SLEEF 式自含多项式（只借鉴算法，**不引入 SLEEF 二进制依赖**），
  NaN / ±Inf / denormal 全部显式 select（与 gcc fast-math 的有意差别，项目语义
  要求；不依赖 vfmin/vfmax 的 NaN 语义）。
- **设计合并点（各 session 已修的 bug，合并时不可丢）**：
  - softmax 版四个关键决定：floor 分裂（f∈[0,1)，避 rne 分裂在 n=128 时的 +Inf
    位模式角点）；魔数 **12582912.0（1.5·2^23）**（2^23 对负 t 取整到半整数）；
    指数域 clamp [0,255]；NaN 显式传播。
  - elementwise 版：k1+k2 二分缩放（denormal 渐进下溢 + k=128→+inf）；溢出/下溢
    select 必须判**原始 x**（魔数在 |y|≥2^22 失效）；logf 的 atanh 级数 **×2 不能
    漏**、次正规输入 −23·ln2 修正；floorf 三分支（中间带 2x 奇偶判别）；erff 分段
    （1≤|x|<4 尾部基底必须 t=1/z）+ NaN 守卫。
  - 合并后**重跑**：离线逐 op f32 序列模拟（union 网格：dense/logspace/边沿/特殊值
    ±0/±inf/NaN/denormal/FLT_MAX/√2/nextafter(1) + 语料实际参数分布，对照语料最紧
    容差对 (1e-4,1e-4)/(2e-4,2e-5) 的裕度）+ QEMU 探针双跑（序列全 e32/m1，避开
    已知 vmv.v.i/x SIGILL 类）。
  - 参考口径教训：参考值必须取 **f32 输入**的函数值（f64 格点直接算会把输入舍入
    误报成误差，x≈1 处虚报 2.7e-3）。
- **实现形态**：全部用既有 repertoire 形式（vbin / vunary / vfmacc / vcmp / vsel /
  vmovv / _splat_const），legalise/select/allocate 原生处理；整型与浮点 op 共享同一
  (sew,lmul,vl) 区域 → **多项式体内零 vsetvli 切换**；Horner 每步 vfmacc 的 vd =
  该步系数预置 splat（无操作数重叠，规避 emit.py pre-copy 路径）；f32↔i32 视图
  切换照 `_convert_vector` 的区域舞步（T034 教训：v0 pin 紧邻消费者）。
- **开关**：统一命名与极性——`A100C_VMATH_LIBM=1` 为回退位（默认向量近似），照
  `matrix_scalar_pack` 三处接线（`driver.py` env→option→身份段 + `vectorize.py`
  身份镜像 + `factory.py` 透传）。
- **数值裕度（已验证的各版结果）**：elementwise 版 err ≤4.2e-7 vs 范围容差 2e-3
  （≥500×，floorf 0 误差/420 万点）；softmax 版最差 err/bound = 0.0385（26×）。
- **预期（判据口径）**：exp 路径每元素 ~40-150 条 → ~1.2 条/元素（-95%+）；
  softmax-f16 全 call **-80% 量级**；elementwise 超越函数 case **-93~-97%**
  （纯逐元素 0.0%，即未触碰路径的对照证据）；attention (a)(c) 类 exp 段 -95%+。

### W2 · lowering / allocator 局部修正（零契约变更；matmul / attention 主战场）

- **P1 pack-b 全瓦片 peel**（matmul；**-28% 已 /tmp 实测**，模型校准通过）：
  运行时一次判断 `n0+tn ≤ N ∧ krem ≥ tk` → 8 列直线 vlse+vse（36 条/列 → 4 条/列
  + 每 K 步 11 条公共）；尾瓦片走原护栏慢路径。**边界**：手工版只对全瓦片 identity
  正确（128³ 恰好全瓦片所以 scan 全过）；编译器版必须带运行时判断 + 慢路径回退。
- **P1b A 行 staging peel**（matmul；~-18%，模型 + mtile dump 实证）：全瓦片时删
  每行 8 条 mask 计算 + vmerge（vle 直通），地址递归化。
- **C8 窄数据仿射访存向量化**（attention fp16；-10~30%）：地址可证均匀字节步长 /
  内维连续时用 `vlse16/vsse16` 或逐行 `vle16/vse16` 替代 T014 逐 lane 标量走；
  属已声明 "wide-access selection from proven contiguity" 职责；matmul 轮配方直接
  移植（`$compiler-pass-porting`，探针证据已有）。
- **P2/C3 分配器 loop-depth 感知 reload/remat**（条件候选）：`allocate.py` 的
  `_loop_depths` 现成；"frame"[op-1] 已归因为分配器重物化（522K/调用）。热循环内
  不逐用 reload。**仅当 W1 落地后复测 reload 仍显著时启动**；影响全语料 → 全量回归
  把关。

### W3 · MIR `mir-optimize` 阶段（契约变更：DesignIssue → 修订 → 独立复审）

- **形态**：lowering→legalization 之间新阶段（mir/v1 → mir/v1）。mir/v1 的 pass
  列表**现在为空**——这是 ARCHITECTURE_CONSTRAINTS 的语义变更，必须走
  DesignIssue → 契约修订（加阶段 / pass / analyses 职责行 / 测试声明）→ 独立复审
  后才实施（与 W1 无契约冲突，可分批；若同批修订则一次过审）。
- **内容**（matmul P0 + attention C2 + softmax 候选 #2 的并集）：
  1. **mir-licm**：CFG 自然环检测（显式 CFG + block 参数，回边 + 支配树）+ 循环
     不变量外提（sconst、地址基、vid）。合法性：MIR 纯整数运算可推测（RISC-V
     add/mul 不陷）；**绝不外提访存**（投机故障）；vsetvli 初版不外提（region
     一致性是 MIR verifier 不变式——本 pass 最大技术风险点，需 per-point region
     状态建模 + witness 测试）。
  2. **mir-sr（IV/地址强度削减）**：回边仿射 IV（i = i + c）识别 → 循环体内
     base + i×S 地址树改写为 block-param 指针递归 p += S（`_emit_pack_loops` 已
     示范该机制；i 另有他用则双维护或放弃）。`begin_counted_loop` 携带界——现成
     分析输入。
  3. **计数循环谓词消解 + 旋转**：slt+bne 每迭代谓词在界已知时折叠/移出。
  4. **vsetvli 循环级外提**（并入或独立小 pass）：循环体内无区域切换 op 时合法
     （verifier 现成），vec-config 4-9% → 循环外常数次。
- **打击面**：sconst + vsetvli + 地址 ≈ 全部 case 的 35-50%；**泛化到 ragged / 小
  shape / 其它算子族**（手工 peel 覆盖不到的部分）；softmax W2/W3（常量重物化 +
  区域抖动，linear-dropout 上 ≈53%）同根因自动获益；attention C5（bQ staging 每
  n_block 重做）由 LICM + workspace 常量偏移别名证明覆盖。
- **开关**：`A100C_MIR_OPT=off`（或逐 pass `A100C_MIRPASS_*`）进身份；测试
  `test_mir_passes.py`（合法性 / 拒绝 / 不变性）。

### W4 · 条件 / 后续（按复测决定，本轮不承诺）

- **C6/P7 归属补齐**：operator_entry 派发骨架 10-15%（harness 侧 origin 联结，
  /tmp 纯分析可完成）→ 大概率也是 W3 的外提对象。
- **softmax W4/W5**：连续访问 unit-stride 化（`vunit_load` MIR 已有）+ 指针递归 +
  工作区往返消除（arange/常量张量 scatter→gather）。
- **softmax W6**：同域 chunk 循环融合（复杂度最高，max-then-exp 需 2 遍但物化+max、
  exp+sum+div+store 可各自融合）。
- **sin/cos 多项式**（19 ids 仍走 libm；erff 已并入 W1）。
- **matmul P6 瓦片形状按形状类扫选**（plan 层，现成指标链扫 BLOCK 组合；诚实标注：
  指令数最优 ≠ 真机最优，产物是候选表不是承诺）。
- **已降级 / 合并项（勿重复做）**：C4 vector-fp32 dot staging → 降级（实测 f32
  case 开销与 f16 同类 sconst/vsetvli/libm，dot FMA 本身很小，W1/W3 自动覆盖）；
  C5 A-staging 外提 → 并入 W3；C7 归约降低重写 → 被 C8 取代（vslide/vextract 风暴
  实测源自 T014 窄数据回退，非归约路径）。
- **明确不做**：P8 K-loop 软件流水 / 双缓冲（指令数判据下不可见甚至为负——判据
  盲区，留待判据扩展到真机/周期级模型再排期）；SLEEF 二进制依赖；fp64 vmath 改动；
  fast-math 式 finite-only 假设；按 case 容差分派。

## 3. 分家族目标与投影（判据 = 每调用 guest 动态指令）

| 家族 | 范围与正确性前提 | 基线画像（实测） | W1 后 | 全栈（W1+W2+W3）后 | 2× 判定 |
|---|---|---|---|---|---|
| softmax_xent | 25 算子 / 146 case；146/146 PASS @4217b79 | softmax-f16 245k/call（libm 体 84.2% + PLT 5.0%）；linear-dropout-f16 15.33M（最重；sconst 27% + vsetvli 14%） | exp 段 -98%，全 call -80% 量级 | 3-4× | 达标，裕度大 |
| elementwise | 134 算子 / 683 case；683/683 PASS @4217b79 | erf/gelu f32 ~70k（erf 机制 89%）；pow 79k；selu/sigmoid/tanh 54-55k；纯逐元素 2.0-3.4k | 超越函数 case -93~-97%；纯逐元素 0% | 同左（W3 再收常量/区域开销） | 远超 |
| attention | 20 算法 / 135 case（文档口径；分类明细 24+57+78=159 与总数不符，重锚时以 scoped scan 实数校正）；范围内存量 non-PASS chunk_gdn2 fp32 ×2 属修复流 T045 | flash_varlen f16 953k（IME 320 条=0.03%）；naive 920k；perf/attn 2459k；gqa f32 1378k；chunk_abc 1000k | (a) 融合 matmul 24 case：exp 段 -95%+，~3-7×；(c) 归约式 78：~3-5×；(b) chunk 线性 57：~1.5-3× | (a)(c) 4-8× / 4-6×；(b) 2-4×（gqa f32 2.5-4×） | 2× 目标 1.5-3× 裕度；不达标 case 给"数学下限"归因（FMA 地板），不虚报 |
| matmul | 家族 312/312 PASS；flagship 128³ f16 为测量锚 | 原始 13.28M → 轮 1 后 4.11M（`f69be1d` 已合入） | （无 vmath 主导项） | P1（实测 -28%）→2.96M；+P1b →~2.2M（1.9×）；+P2 →~2.0M（**2.05× 跨线**）；+W3 →~1.9M（2.2×；对原始 6.8×） | 跨线于 P2；ragged/小 shape 靠 W3 泛化 |

全量回归参照组（"无新增 non-PASS"口径的存量）：@4217b79 报告 2726/2734 PASS，
存量 8 个（chunk_gdn2 fp32 ×2、complex_svd/deconv3d 编译超时 ×6，matmul 轮已三重
归因）；实施时以当时 HEAD 重建参照组（T044 落地后可能变化）。

## 4. 实施序列（获批后；每步落袋为安，可中途停止）

1. **前置（半天，零编译器改动）**：确认 T044 落地后的新 HEAD；重锚基线（各家族
   scoped scan + 代表子集指标：softmax 44 组、elementwise 13 case、attention
   6 case × dtype 路径 × 1/2/4/8 worker——全部复用 `tools/profiling/` 现成链）；
   W1 合并版设计定稿（§2.W1 的合并点 + 重跑离线验证与探针）。
2. **W1 统一 vmath 多项式**：/tmp 原型复核（合并版系数 + 探针）→ 实现
   （`vectorize.py` 为主 + `driver.py`/`factory.py` 接线 + `test_math_ops.py` 扩展
   + `analyze_blocks.py` vmath 分类）→ 三方对照 → scoped scans（146 + 683 + 135）
   → 指标复测 → 全量 2734 → 记录（RECORD.md + INDEX + 复盘 L17+）。
3. **W2 第一批**：matmul P1 + P1b（312 case scan + 触发检查：program.S 中 pb 展开
   形态 + 快/慢路径、ragged 正确性单测）；attention C8（135 case scan）。可与其它
   session 并行，`vectorize.py` 冲突面串行化。
4. **W2 第二批（条件）**：P2/C3 复测后决定。
5. **W3**：DesignIssue → 契约修订（mir-optimize 阶段 + mir/v1 pass 列表 + analyses
   职责行 + `test_mir_passes.py` 声明）→ 独立复审 → 实施 → 同序列验证。
6. **W4** 按复测与扫描决定；每轮收尾：全量 2734（threads=1 + 代表 resource/IME
   见证；多 worker 由指标采集覆盖）+ 证据落盘 + 复盘。

## 5. 验证协议（所有候选统一）

1. **触发证据**：候选位 stage dump / program.S 形态断言（如无 vmath、pb 展开形态）；
   开关-off 位与基线逐行 / asm_join 字节同一性。
2. **合法 / 拒绝**：a100c/tests 全跑（含新增：IR 级 on/off 序列断言、执行级双开关
   对拍、身份键变更）+ 四个 behaviour 检查（no-name-dispatch `--witness` 必须）。
3. **家族 scoped scan** 全 PASS（命令在各 baseline/scan 的 command 字段）。
4. **全量 2734**（`tools/run_scan.py` 无过滤）："无新增 non-PASS"，存量参照组明确
   列出；新增失败 → 修复或回退并记录。
5. **同口径指标复测**：代表 case × 1/2/4/8 worker；on/off 对照一并报告；多 worker
   总量不用于证明"并行加速"。
6. **记录**：按 optimization-record 指南落盘 + INDEX.md + OPTIMIZATION.md 更新 +
   compiler-design-retrospective（lessons 续编号）。

## 6. 风险与回退（汇总）

| 风险 | 缓解 | 回退 |
|---|---|---|
| W1 数值边界（exp→整型 cast 的 exact case / 溢出位模式角点） | 离线 union 网格先行 + 全量回归把关 | `A100C_VMATH_LIBM=1`（身份隔离，缓存安全） |
| W1 寄存器压力（多项式临时值 → spill 增） | 监控 spill 计数；必要时按 vl 子块分块求值并诚实报告 tradeoff | 同上 |
| W1 个别 case 容差失败 | 升多项式次数 / 查边沿；仍不行则默认翻转为 libm、vector 变 opt-in（记录决策；**禁止按 case 容差分派**） | 同上 |
| W3 region 一致性破坏 | MIR verifier 强制 + witness 测试 + 逐 pass 独立开关 | `A100C_MIR_OPT=off` |
| P1 peel 对 ragged case 错误 | 运行时全瓦片判断 + 护栏慢路径回退（手工版边界已明确）；ragged 单测 | 开关回慢路径 |
| 2× 在 vector-fp32 / chunk 类不达标 | W2/W3 兜底；仍不达给 FMA 地板归因 | 不虚报 |
| 实施期 HEAD 变化（T044 / 修复波 / 其它 session） | 每步重锚基线；`vectorize.py`/`pipeline.py` 冲突面串行化 | — |

## 7. 协调决策点（待用户裁断）

1. **C1/vmath-poly 归属收敛**：三个 session 的重叠设计合并为 W1 一个实现（本计划
   建议：lowering-local、函数并集、单开关 `A100C_VMATH_LIBM`）；softmax 轮的
   baseline/metrics/验证工件全部复用为 W1 的 softmax 侧输入。
2. **实施顺序**：默认 W1 → W2 → W3（W1 收益面最大且零契约）；若 matmul 优先，
   则 P1+P1b+P2 已可跨 2× 线（~2.05×），W1 随后。
3. **W3 契约批次**：单独过审，还是与后续可能的 TIR 层修订合并一次过审。

## 8. 证据索引（绝对路径）

- 统一计划：本文档。
- matmul：`docs/compiler-agent/optimizations/matmul/`（baseline/tooling/
  candidates/vector-pack/regression/full-input/retrospective.md L1-L8 + 复盘
  L9-L16）；/tmp 实测现场 `/tmp/a100c-opt2/`（peel-metrics/、改版 program.S、
  base/peel 两份 scan report；worktree @4217b79，可用 `git worktree remove` 清理）。
- attention：`/tmp/attn_metrics/`（6 代表 case：flash-f16/f32、naive-f16、
  perfattn-f16、gqa-f32、chunkabc-f16 + collect.sh）。
- softmax：`docs/compiler-agent/optimizations/softmax/`（baseline 146 全套 + 44 组
  metrics + tooling/sweep.sh）；`/tmp/softmax-opt/`（fit_validate_emit.py、
  numerics-report.json、probe-mathapprox.S/.o、OPTIMIZATION-PLAN.md 即候选 #1
  全文）。
- elementwise：`docs/compiler-agent/optimizations/elementwise/`（baseline 683 全套 +
  13 case metrics + vmath_census.json；tooling/fit_math_coeffs.py；
  candidates/vector-poly/DESIGN.md）；瓶颈现场
  `a100c/cache/63f20fc874428ac43ab7e3a8e8aa916b33fbe1da09e1098318cf36159497e2a4/program.S:123-142`。
- 已合入基础：OPT-EMIT-PEEPHOLE（`0f84bdc`，静态 ~-10%）、OPT-MATMUL-BPACK
  （`f69be1d`，IME 路径动态 -30.6~-79.1%、reload 流量 -67~-85%）。
