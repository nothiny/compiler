# The operator corpus — what it is and how it is used

> 可整段替换 `KICKOFF_FULL.md` 的 `## The operator corpus — what it is and how it is used`
> （原 125–304 行）。这里的事实都来自语料仓库的实测，不是估计。

## 0. 三个数

| 量 | 值 | 含义 |
|---|---|---|
| 算子 | **500** = dev 400 + perf 100 | 输入单位是**文件**，不是函数 |
| case | **2734** = dev 2192 + perf 542 | `(算子, shape, dtype)` |
| 编译身份 | **2161** | 真正的编译单元：源码 + dtype + constexpr meta + launch cfg，**不含 shape/grid** |

`cases/identity = 1.26`。总编译时间 ≈ `身份数 × 单次成本`，所以**只减 case 没用**，
要减身份数或单次成本 —— 两个旋钮都在语料里，不在编译器里。

v3 是**声明的推理子集**（前向-only、无 fp8、无 tf32/`input_precision`，fp32 dot 为
IEEE；浮点 case 覆盖 fp32/fp16/bf16 三种推理 dtype，bf16 是 perf 车道主 dtype）；五条原则、包含与排除的构造见 `docs/SUBSET.md`，选区与前后对比见
`docs/SUITE_V3.md`。池是 1000 算子 / 5612 case（不在本镜像内），held-out 是其中
500 个（按 origin 记在维护分支的 `suite/heldout.json`，发布包不含）。

## 1. Layout

```
ops/
  suite/manifest.json          500 个算子的机器可读清单(路径/特征/成本/来源)
  suite/dev/                   400 个正确性算子,语义尺寸(18 个验证过的 shape override)
  suite/perf/                  100 个性能算子;稳态计时尺寸由 workload.json 解析
  suite/heldout.json           500 个 held-out 算子(按 origin;仅维护分支)
  docs/SUBSET.md               声明的推理子集:五条原则、包含/排除的构造
  docs/SUITE_V3.md             选区方法、前后对比、覆盖、验证状态、评估协议
  docs/SUITE_V2.md             上一版(目标无关),历史
  docs/COVERAGE_MATRIX.md      算子 × 特征表
  README.md                    每个算子一行
  docs/API_INVENTORY.md        每个 tl.* 构造,按组列出(生成物)
  harness/                     runner —— 不是算子
    compiler_api/
      AGENT_GUIDE.md           怎么把编译器接进来(先读)
      RUNBOOK.md               怎么最快编译、三条车道、16 进程怎么接
      COMPILE_CONTRACT.md      适配器协议(identity/compile/launch/cost/cache_key)
      README.md                Device 协议与 case 字段细节
      run_cases.py             枚举/运行全部 case,四状态反馈,增量续跑
      gate.py                  编译经济学门禁(退出码即 gate)
      identity.py              编译身份普查(--identities / --schedule)
      device.py / reference.py Device 协议 shim / torch 参考装置
    benchmark/                 run.py(计时)、report.py、size.py
    opslib/                    共享实现;tests/ harness 测试
```

**输入是 `suite/dev` + `suite/perf`，不是 `harness/` 下的任何东西。** 扫描前先声明：

```bash
python -m compiler_agent operator-set \
  --glob 'suite/dev/*.py,suite/perf/*.py' --source ops/README.md
python -m compiler_agent ingest-ops
```

选材来源池不在本镜像内，**不是**本次运行的输入；`suite/` 里的文件是选区后的副本，
`provenance.json` 记录了每个文件的上游路径与 sha256（只作溯源，不需要访问）。

## 2. 每个算子的契约

一个算子文件 = 一段 docstring + 字面量 `OPERATOR` + 一个 `@triton.jit`（少数带一个
辅助 kernel）+ 一个 case 层（`SHAPES` / `DTYPES` / `ref` / `make_case`）。
`ref` 用 NumPy 给出期望值；`make_case` 还给出 `meta`（constexpr）、`grid`、
`pointer_dtypes`（bf16 的指针类型）和 `launch_meta`。

**不要修改算子文件来让某个实现通过。** 改 `ref` 的数值语义、放宽容差、删 case
都是禁止的；只允许"这个构造本就不支持"的显式声明 + 诊断。

## 3. 编译器如何消费一个 case

`Device` 五个方法：`alloc` / `upload` / `download` / `pointer` / `launch`。
`run_cases.py` 负责 case 构造、staging、启动、回读、与 NumPy 对拍。

**关键事实**：一次 shape 扫描的成本是
`O(不同 dtype × constexpr × launch 配置)`，**不是** `O(shape 数)` —— 新 shape 落进
一个已见过的值类别时，只多一次 launch 和一次比较。这个结论现在可以直接测量，
不用推理：`--dry-run --identities`。

## 4. Compiling it cheaply —— 两个旋钮都是你的

总门禁时间 = `编译次数 × 单次成本`。语料既不固定前者也不固定后者，
所以下面三条是**硬规则**，不是优化建议。

1. **按身份编译，不按 case 编译。** 新 shape 落进已见身份 = 一次 launch + 一次比较。
   验收：`--dry-run --identities` 里 `cases/id ≥ 1.25`。若 cache key 里含
   grid 或 shape（`audit-memory` 里的 "wall-time trap" 就是这个），它不可能达标。
2. **不要让 constexpr 跟着 shape 变。** `EVEN_M`、`NTILES`、`NUM_K_BLOCKS` 这类
   派生常量让 **160 / 2161** 个身份凭空出现。shape 一律当运行时标量，
   除非 lowering 真的需要它是常量。
3. **超过预算的编译 = 编译器缺陷。** 用 `--compile-budget 10`；超预算的行是
   `COMPILE_BUDGET_EXCEEDED`。要么修编译（vreg 膨胀、无谓展开），
   要么显式声明不支持并给诊断。**永远不许删 case 来让门禁变绿。**

预算（全部由代码强制，不靠人记）：

| 车道 | 范围 | 预算 |
|---|---|---|
| **dev** | 一组 / 一个算子（内循环） | ≤ 5 min |
| **gate** | 整个 suite，冷跑 | ≤ 15 min，身份级 p99 ≤ 10 s |
| **perf** | 只 `suite/perf` | 独立车道，永不阻塞 gate |

## 5. 正确性 harness（四状态反馈 + 增量）

命令一律从 `ops/` 执行。

```bash
# 枚举与身份普查(唯一的真实规模来源;不编译)
python3 harness/compiler_api/run_cases.py --manifest suite/manifest.json --dry-run --identities

# 一组 / 一个算子(内循环)
python3 harness/compiler_api/run_cases.py --device mycompiler:make_device --group basic

# 全量:可断点续跑,journal 每完成一个 case 落一行,--resume 只补增量
python3 harness/compiler_api/run_cases.py --device mycompiler:make_device \
    --manifest suite/manifest.json --jobs 4 --gpus 0,1,2,3 \
    --journal runs/correctness.jsonl --resume --retry-failed \
    --case-timeout 60 --compile-budget 10 --report correctness.json

# 编译经济学门禁(退出码即结论)
python3 harness/compiler_api/gate.py --device mycompiler:make_device \
    --manifest suite/manifest.json --compile-budget 10 \
    --max-wall 900 --max-p99 10 --report gate.json
```

每个 case 报一个状态：**PASS / CASE_FAIL / LAUNCH_FAIL / MISMATCH / TIMEOUT /
COMPILE_BUDGET_EXCEEDED / OOM**。按状态、dtype、算子聚合，就得到
"还缺什么"的清单。参考装置（`--device cuda`，torch-free；`--device torch-gpu`）
跑 stock Triton —— 先用它证明 harness 本身是对的，再相信某个失败。
已知例外：**autotune 算子在 torch-free 参考装置上会失败**（stock Triton 的
autotuner 会 import torch），这是装置的局限，不是编译器的失败；需要它们时加
`--allow-torch`。

## 6. 失败归因（必须照这个判）

| 状态 | 归因 | 动作 |
|---|---|---|
| `CASE_FAIL` | **语料** | 修算子文件（`make_case` / `ref`） |
| `MISMATCH` | 先语料后编译器 | 先用 `--device torch-gpu` 确认参考值 |
| `LAUNCH_FAIL` | **编译器** | 设备未接线 / launch 提前返回 |
| `TIMEOUT` | 编译器或语料 | 看 `launch_seconds`：慢 = 编译；挂住 = 查 kernel |
| `COMPILE_BUDGET_EXCEEDED` | **编译器** | 修编译或声明不支持并给诊断 |
| `OOM` | **编译器** | 同上；用 `--case-memory-mb` 把爆炸限制在单个 case |

`COMPILE_BUDGET_EXCEEDED` 与 `OOM` **永远不能**归因为"corpus defect"，
否则 agent 会学会"让慢 case 失败"来让门禁变绿。

## 7. 怎么工作语料（三条车道，不是两条 loop）

| 车道 | 输入 | 频率 | 通过标准 |
|---|---|---|---|
| **dev** | `--group` 或 `--operator` | 每次改动 | 全 PASS，≤5 min |
| **gate** | `--manifest suite/manifest.json` | 每个 vertical slice / 每轮 | 全 PASS，`gate.py` 五个 check 全绿，≤15 min |
| **perf** | `suite/perf` | 阶段末 | 见"性能必须是完成条件"一节 |

顺序：先按算子索引做 vertical slice（每类先跑 1 个算子），再跑组，再跑全量；
**任何一环红了就停下来修**，不要把红的留到最后。

## 8. Counting

```
500 算子 = dev 400 + perf 100
2734 case = dev 2192 + perf 542
2161 编译身份(cases/identity 1.26;去掉 shape 派生 constexpr 后 2001)
覆盖:75 个语义特征全中(声明的推理子集),1612/1612 个特征交互
池是 1000 算子 / 5612 case;held-out 是池中的 500 个(不在发布包内)
```

数字一律来自 `--dry-run --identities`（用 `record-case-totals` 记录），
**不要手抄**。一个组的执行 case 数为 0 是 harness 缺陷，不是"覆盖够了"。

## 9. 上游文档（不要在本文件里重复它们）

- `ops/harness/compiler_api/RUNBOOK.md` —— 最快编译的 8 条、三条车道、
  16 进程驱动的 5 条规则、排错表。
- `ops/harness/compiler_api/COMPILE_CONTRACT.md` —— 适配器五个方法、
                `identity()` 的四口径、`schedule.json`（并行驱动任务表）
                与 `gate.json` 的 schema、实现完的 4 条验收命令。
- `ops/docs/SUITE_V2.md` —— 选区方法（为什么是这 500 个）、覆盖矩阵、
  验证状态、dev/holdout 评估协议。
