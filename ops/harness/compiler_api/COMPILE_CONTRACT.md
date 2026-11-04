# COMPILE_CONTRACT — 编译器适配器要实现的接口

这份文件是**你的编译器**（或驱动它的 workflow）与语料库之间的唯一契约。
实现了它，`gate.py` / `run_cases.py` / 并行驱动就能驱动你编译和运行；没实现，
就只能用 `--device cuda`（stock Triton）测"语料本身贵不贵"。

**不要为了接这个接口去改编译器的语义**。接口只有一层薄适配，通常 ≤200 行。

---

## 1. 五个方法

```python
class CompileBackend(Protocol):
    def identity(self, src: str, case: dict, tier: str = "meta") -> str: ...
    def compile(self, src: str, case: dict, budget_s: float | None = None) -> Artifact: ...
    def launch(self, artifact: Artifact, staged: StagedCase) -> None: ...
    def cost_hint(self, identity: str) -> float | None: ...
    def cache_key(self) -> str: ...
```

### 1.1 `identity(src, case, tier)` — 最重要

返回**编译身份**：一个字符串，两个 case 编辑出同一份机器码就必须相同。

组成（`tier="meta"`，默认口径）：

```
source path + kernel name
  + 每个指针实参的 **设备 dtype**（bfloat16 case 在 host 上是 float32 存储，
    但指针是 bfloat16 —— 必须用 case["pointer_dtypes"] 里的覆盖值）
  + 每个标量实参的 Triton 特化类别（int: ==1 / div-16 / other；float: dtype）
  + case["meta"] 与 case["launch_meta"] 里的每个 constexpr
```

**不含** `shape`、`grid`、case 的数值内容（buffer 内容不影响代码）。

`compiler_api/identity.py` 里有参考实现，可以直接复用：

```python
from compiler_api import identity
ident = identity.case_identity("hard/matmul_kernel.py", case, tier="meta")
```

tier 的口径（用于对账，语料侧已经实现）：

| tier | 含义 | 现状（3465 case） |
|---|---|---|
| `dtype` | 只看指针 dtype | 482 |
| `triton` | + int 特化（==1 / div-16） | 1109 |
| `meta` | + 全部 constexpr | **1511**（目标口径） |
| `structural` | meta 去掉 shape 派生项（诊断用） | 1264 |

如果你的编译器把某些 `meta` 当运行时标量，请在文档里写清，并用 `structural`
口径对账 —— **但是不要**让 `identity()` 返回比"真实编译次数"更粗的值，
否则驱动会错误地复用 artifact。

### 1.2 `compile(src, case, budget_s)`

编译并返回一个不透明 `Artifact`（缓存句柄、模块对象、文件路径都行）。

- `budget_s`：超时就抛 `CompileBudgetExceeded`，**不要**静默继续。
  驱动会把它记成 `COMPILE_BUDGET_EXCEEDED` 失败行（归因编译器）。
- 必须**幂等**：同 `identity` 再调一次应当命中缓存（驱动会这么用）。
- 不许在里面做数值对拍、不许写日志到 stdout（stdout 是给报告用的）。

### 1.3 `launch(artifact, staged)`

把输入 buffer 与参数按 `staged` 绑好后启动 kernel。约定：

- `staged` 由 `opslib.device.stage_case(case, device)` 产出，提供
  `staged.arguments()`（位置实参顺序与 kernel 签名一致）与 `staged.outputs()`；
- **不得**在这里做比较/参考计算；参考值由 harness 用 NumPy 算；
- 必须真正把 kernel 跑完再返回（否则 `compare` 读到未写内存）。

`opslib/devices/cuda.py` 里的 `CudaDevice.launch` 是最小的合法实现样板：

```python
def launch(self, kernel, grid, positional, keywords=None):
    kernel[grid](*positional, **(keywords or {}))
```

### 1.4 `cost_hint(identity)` / 1.5 `cache_key()`

- `cost_hint`：上一轮实测的编译秒数（没有就 `None`）。驱动用它做**重尾优先**排序，
  makespan 由尾部决定，这个数直接决定调度质量。
- `cache_key`：影响 codegen 的版本指纹。**不要**用"整个编译器目录的 sha256"
  （改一行注释就会让全部 artifact 失效）；用真正影响输出的那些文件的哈希。

---

## 2. 接进 harness

### 2.1 方式 A：`module:attr`（推荐，零改动）

```bash
python3 harness/compiler_api/gate.py --device mypkg.adapter:CudaBackend
```

`make_device` 会 `import mypkg.adapter`，取 `CudaBackend()` 作为 `Device`。
适配器只要满足 `opslib.device.Device`：

```python
class Device(Protocol):
    name: str
    def stage(self, case) -> StagedCase: ...      # 或直接用 stage_case 的默认实现
    def launch(self, kernel, grid, positional, keywords=None) -> None: ...
    def fetch(self, buffer) -> np.ndarray: ...
```

### 2.2 方式 B：直接调 `run_all`

```python
from compiler_api.run_cases import run_all
rows = run_all(my_device, group="basic", compile_budget=10.0)
```

`rows` 每行：`{operator, group, shape, dtype, identity, status, detail,
launch_seconds, seconds, rss_mb?}`。

**`launch_seconds` 的语义**：该 case 的 launch 耗时。一个身份的**第一条** case
的 `launch_seconds` 就是它的编译成本（后面的命中缓存），`gate.py` 就是这么算
`compile.total_s / p50 / p99 / max` 的。所以：**缓存命中必须真的快**，不要把
"每次 launch 都重新 codegen"的实现接进来，否则 gate 会把每一行都记成编译。

---

## 3. `schedule.json`（并行驱动的输入）

```bash
python3 harness/compiler_api/run_cases.py --dry-run --identities --schedule runs/schedule.json
```

```json
{
  "tier": "meta",
  "identities": 1511,
  "cases": 3465,
  "items": [
    {
      "identity": "54f6b31e0c0d",
      "operator": "basic/sum.py",
      "kernel": "sum_kernel",
      "cost_hint_s": null,
      "cases": [{"shape": [2, 128], "dtype": "float32"}]
    }
  ]
}
```

约束：

- `items` 已按 `(-cost_hint_s, -len(cases), operator)` 排序（LPT，重尾优先）；
- 一个 `identity` 只出现一次；`cases` 是该身份覆盖的全部 case；
- 驱动拿 `(operator, shape, dtype)` 用 `opslib.runner.load_operator` +
  `op.make_case(shape=..., dtype=..., seed=30)` 重建 case（与 harness 完全一致）。

**并行驱动必须遵守**：

| 要求 | 原因 |
|---|---|
| 任务单元 = item（身份） | 按 case 投递会重复编译 |
| 每 worker 独立 cache 分片 | 16 进程争同一把锁/同一目录会互相拖慢 |
| 每 worker 批量吃身份 | `import compiler` 0.2 s × case 数是纯浪费（4426 case ≈ 13 min） |
| 超预算/异常只记该 item，继续 | 一个身份不该中止整轮 |
| 回填 `cost_hint_s` | 下一轮排序才准 |

---

## 4. `gate.json`（门禁输出）

```json
{
  "device": "cuda",
  "group": "all",
  "cases": 3465,
  "identities": 1511,
  "cases_per_identity": 2.29,
  "statuses": {"PASS": 3465},
  "failures": {},
  "compiler_defects": {},
  "compile": {
    "identities_measured": 1511,
    "total_s": 2280.0, "p50_s": 0.6, "p90_s": 19.5,
    "p99_s": 195.0, "max_s": 1193.0, "over_budget": 0
  },
  "wall_seconds": 2400.0,
  "top_offenders": [
    {"identity": "…", "seconds": 1193.0,
     "operator": "hard/matmul_kernel.py", "shape": [17, 33, 1000], "dtype": "bfloat16"}
  ],
  "checks": {"no_failures": true, "dedupe": true, "p99": false,
             "wall": false, "budget": true},
  "passed": false
}
```

失败类（`status`）：`CASE_FAIL` / `MISMATCH` / `LAUNCH_FAIL` / `TIMEOUT` /
`COMPILE_BUDGET_EXCEEDED` / `OOM`。

**归因规则**（workflow 应当照这个判）：

| 状态 | 归因 | 动作 |
|---|---|---|
| `CASE_FAIL` | 语料 | 修算子文件（`make_case`/`ref`） |
| `MISMATCH` | 先语料后编译器 | 先用 `--device torch-gpu` 或 CPU 解释器确认参考值 |
| `LAUNCH_FAIL` | 编译器 | 设备未接线 / launch 未生效 |
| `TIMEOUT` | 编译器或语料 | 看 `launch_seconds` 区分：慢 = 编译；hang = 查 kernel |
| `COMPILE_BUDGET_EXCEEDED` | **编译器** | 修编译（vreg 膨胀、无谓展开）或声明不支持并给诊断 |
| `OOM` | 编译器 | 同上 |

`COMPILE_BUDGET_EXCEEDED` 与 `OOM` **永远不能**归因为"corpus defect"，
否则 agent 会学会"让慢 case 失败"来让 gate 变绿。

---

## 5. 验收（实现完之后必须过的四条）

```bash
# 1. 身份口径与真实编译次数一致(≤1.25×)
python3 harness/compiler_api/run_cases.py --dry-run --identities   # 看 cases/id

# 2. 单组内循环通
python3 harness/compiler_api/run_cases.py --device mypkg.adapter:CudaBackend --group basic

# 3. 冷全量门禁通
rm -rf /tmp/cc && python3 harness/compiler_api/gate.py \
    --device mypkg.adapter:CudaBackend --compile-budget 10 \
    --max-wall 900 --max-p99 10 --report runs/gate.json

# 4. 断点续跑不重复编译
python3 harness/compiler_api/run_cases.py --device mypkg.adapter:CudaBackend \
    --group basic --journal runs/j.jsonl --resume
```

第 3 步的 `compile.identities_measured` 应当等于 `identities`（1511）而不是
`cases`（3465）。如果相等的是后者，说明 `launch()` 每次都在重新编译。
