# 编译器 Agent 指南

本文的读者是**写编译器的 agent**。语料对你**只读**;维护语料的说明在
`../AGENTS.md`(本目录),与你无关。

> ## 三条硬规则(先于本文其它一切)
>
> 1. **语料只读**。不改任何算子文件、`ref`、容差、`SHAPES`/`DTYPES`、harness、`suite/manifest.json`、
>    `catalog.json`、`suite/perf/workload.json`。case 过不了就修编译器。
> 2. **不得借用 Triton 的编译栈**。你的 `Device.launch` 不得调用 `kernel[grid](...)`、
>    `triton.compile`、`kernel.run`/`warmup` 或 `triton.compiler`/`triton.backends`。随包的
>    `cuda` / `torch-gpu` 设备正是这么做的——它们是**参考装置与性能基线**,包一层它们能全绿,
>    但那不是编译器。
> 3. **输出写进你的项目仓库**:`--report` 与 `--out-dir` 都指向项目目录,不要写进语料。

下文中 `ops/` 指语料根目录(在 workflow 项目里就是 `ops/`)。所有命令在语料根目录执行。

---

## 0. 一分钟上手

```bash
# 1) 规模:每组多少算子 / case(不需要 GPU)
python3 harness/compiler_api/run_cases.py --dry-run --group-order

# 2) (可选,需要 NVIDIA GPU)用参考装置确认 harness 与 case 本身无误
python3 harness/compiler_api/run_cases.py --device cuda --group basic

# 3) 换成你的编译器
python3 harness/compiler_api/run_cases.py --device yourmod:make_device --group basic
```

`yourmod` 要能被 import:把你的项目目录和 `ops/harness` 都放进 `PYTHONPATH`
(你的 `Device` 子类需要 `from compiler_api.device import Device`)。

---

## 1. 输入是什么

**输入只有两个目录**,共 **500 个算子 / 2893 个 case / 1422 个编译身份**:

| 组 | 内容 |
|---|---|
| `suite/dev/*.py` | 400 个正确性算子,多数维度 <=128(41 个有 257 的尾块维、9 个保留上游 600-4100 宽度):访存与掩码、逐元素、归约、scan、dot 流水线、动态循环、间接寻址、attention、卷积、chunked 线性注意力 |
| `suite/perf/*.py` | 100 个性能算子(memory / reduction / compute 三类),真稳态尺寸;正确性同样要对 |

`suite/manifest.json` 是每个算子的机器可读清单(特征 / 交互 / case 数 / 来源);
`harness/` 下的 `.py` **不是算子**,不要把它们当作输入统计或编译。workflow 里声明算子集合用:
`operator-set --glob 'suite/dev/*.py,suite/perf/*.py'`。

**要实现哪些构造**:[`../../docs/API_INVENTORY.md`](../../docs/API_INVENTORY.md) 列出两组 kernel 用到的
全部 `tl.*` / `triton.*` 构造和每组的使用文件数(从 AST 生成,与语料同步)。它是语言的一个
**样本**:清单里的每一项都必须支持或明确拒绝;清单外的构造也不意味着可以不支持。

### 1.1 一个算子文件

```python
"""argmax: 每行最大值的下标 ...(用途、模式说明)"""
OPERATOR = {"name": "argmax", "group": "basic", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["reduce.argmax", "memory.load.masked", ...]}
# 注:OPERATOR 里的 group 记的是选材时的上游 tier(溯源用)。
# 本语料的输入分组由所在目录决定:`suite/dev/` 或 `suite/perf/`。
COPIED_FROM = {...}          # 或 SOURCE = {...} / BENCH_SOURCE = {...}:来源记录

import numpy as np
import triton
import triton.language as tl

@triton.jit                  # ① 编译单元:你只编译这一个函数的 AST
def argmax_kernel(x_ptr, out_ptr, n_cols, BLOCK: tl.constexpr):
    ...

SHAPES = ((64, 1000), (1, 1), (3, 17), (8, 4096))   # ② case 层:第一项是典型用法
DTYPES = ("float32", "float16", "bfloat16")
def ref(args, meta): ...             # 纯 numpy 参考实现
def make_case(shape=None, dtype=None, seed=None): ...
```

编译器可以依赖的约束(`harness/tests/test_normalized_corpus.py` 锁定):

- 每个文件**恰好一个** `@triton.jit`(可能带 `@triton.autotune` 包装);
- 只用公开 `tl.*`:没有 `tl.extra` / `tl.math` / libdevice;
- 零 `import torch`;
- `OPERATOR` 是字面量,对编译器没有语义。

### 1.2 `suite/manifest.json`:不用解析 AST 的索引

每个算子一条:`operator`(相对 `ops/` 的路径,即 `suite/dev/…` 或 `suite/perf/…`)、`group`、`kernel` 名、`parameters`
(`[{name, kind}]`,`kind ∈ {pointer, scalar, constexpr}`)、`constexpr_values`、`grid`
(`[int,...]` 或 `{"kind": "callable"}`)、`outputs`、`output_dtypes`、`shapes`、`dtypes`、
`autotune`、`cases_declared` / `cases_constructible`。

- **参数不能按名字猜类型**:指针、运行时标量、编译期值三类实体要分开。
- manifest 只取首个 case 的 `grid` / `constexpr_values`;**权威来源是 `make_case(shape, dtype)`**。
- manifest 是生成物,不要重新生成它。

### 1.3 case 字段(编译 + 启动所需的全部信息)

| 字段 | 含义 |
|---|---|
| `kernel` | 要编译的 `@triton.jit` 函数对象(`kernel.fn` 是 Python 函数,可取源码 / AST) |
| `args` | 运行时实参:指针 = numpy 数组,标量 = Python/numpy 标量 |
| `meta` | constexpr 实参 |
| `grid` | 启动 grid(tuple 或 `lambda meta:`) |
| `outputs` | 需要回读比较的缓冲名 |
| `expected` / `comparison` | 参考结果 / 每个输出的比较策略(`rtol`、`atol`、`equal_nan`、精确比较) |
| 可选 `launch_meta` | `num_warps` / `num_stages` 等启动配置 |
| 可选 `pointer_dtypes` | 设备指针 dtype 与 host 数组不同(bf16:host float32 → cast;host uint16 → view) |
| 可选 `launches` | 同一组缓冲、不同运行时参数的多次启动,按顺序执行后统一回读 |
| 可选 `allocations` / `pointer_table_relocations` / `pointer_relocations` | 指针表:把某块缓冲的设备地址写进另一块缓冲 |

---

## 2. 怎么接入:实现一个 `Device`

```python
from compiler_api.device import Device

class MyDevice(Device):
    def alloc(self, shape, dtype): ...            # 分配设备缓冲
    def upload(self, array, dtype=None): ...      # host -> device(dtype 来自 pointer_dtypes)
    def download(self, buffer): ...               # device -> host,dtype/shape 与 host 缓冲一致
    def pointer(self, buffer): ...                # 设备地址(默认 buffer.data_ptr())
    def launch(self, kernel, grid, positional, keywords): ...
        # 在这里做你自己的 lowering + 执行:
        # positional 已按 kernel 形参顺序绑定好;keywords 已含 launch_meta

def make_device():
    return MyDevice()
```

`--device yourmod:make_device`:可调用就无参调用,否则直接当 `Device` 对象用。

可选钩子(不实现就退回默认):

| 钩子 | 不实现时 | 什么时候需要 |
|---|---|---|
| `upload_aliased(group, pointer_types)` | 含共享内存参数的 case 直接报错(不会静默算错) | 两个参数名指向同一块 host 内存时:一次分配 + 偏移视图 |
| `compare(buffer, expected, policy)` | 下载回 host 对拍 | 想在设备上对拍、只回读标量;必须逐位复刻 `np.isclose` |
| `timer()` | bench 退回 host 计时(记录标 `timer: "host"`) | 设备端计时 |
| `properties()` | bench 要求显式 `--llc-bytes` | 返回 `{"name", "llc_bytes", "sm_count", ...}` |
| `release(buffers)` | 依赖 GC | bench 的大缓冲,每个 entry 后显式释放 |

参考实现(只抄内存管理,不抄 `launch`):`harness/opslib/devices/cuda.py`(cuda-python,无 torch)。
两个已知深坑,参考装置都踩过:

1. **特化缓存的 key 不能用对象身份**。按 `id(obj)` 缓存的特化在对象被回收、地址复用后会
   拿到别的 dtype 的产物——fp16 的代码跑在 fp32 指针上,静默只写半个缓冲。key 必须是
   dtype / constexpr / 对齐的**值**。
2. **共享内存的参数上传后必须仍是一块存储**(实现 `upload_aliased`),否则 in-place 语义丢失。

---

## 3. 正确性反馈:`run_cases.py`

```bash
# 某一组
python3 harness/compiler_api/run_cases.py --device yourmod:make_device --group suite/dev
# 两组依次跑,每组一行汇总
python3 harness/compiler_api/run_cases.py --device yourmod:make_device --group-order --report /tmp/correctness.json
# 只跑指定算子(可重复)
python3 harness/compiler_api/run_cases.py --device yourmod:make_device --operator suite/dev/attention_score.py
# 分片并行:N 个子进程,每片一个 GPU,合并后的报告与不分片时逐行一致
python3 harness/compiler_api/run_cases.py --device yourmod:make_device --jobs 4 --gpus 0,1,2,3 --report /tmp/correctness.json
```

不带 `--group` / `--group-order` 时跑全部两组(`suite/dev` + `suite/perf`)。
`--jobs` 不能与 `--group-order` 同用。

每个 `(算子, shape, dtype)` 一个状态:

| 状态 | 含义 | 说明 |
|---|---|---|
| `PASS` | 编译 + 运行 + 对比通过 | 目标 |
| `CASE_FAIL` | `make_case` 抛错 | 语料侧问题(当前全部 case 都可构造,应为 0) |
| `LAUNCH_FAIL` | 你的 `Device.launch`(或上传/回读)抛错 | 编译器缺 lowering / 运行错误 |
| `MISMATCH` | 跑通但与 `ref` 不一致 | 语义 lowering 错 |
| `TIMEOUT` | 单 case 超过 `--case-timeout` | 编译慢(`launch_seconds` 大)或 kernel 挂住 |
| `OOM` | 超过 `--case-memory-mb` 或真 OOM | 编译器侧(vreg/PTX 爆炸) |
| `COMPILE_BUDGET_EXCEEDED` | 首次编译超过 `--compile-budget` | 编译器缺陷:修编译或声明不支持,**不许删 case** |

`--report` 每个 case 一行:
`{operator, group, shape, dtype, identity, status, detail, launch_seconds, seconds, rss_mb?}`;
`identity` 是该 case 的编译身份,`launch_seconds` 是它的启动耗时(一个身份的第一条
case 的 `launch_seconds` 就是这次编译的成本)。按 status / dtype /
算子 / `parameters[*].kind` 聚合,就是"还差哪些能力"。

**torch 拦截**:除 `torch-*` 设备外,`run_cases.py` 默认在 `sys.meta_path` 上拦截 `torch`
(任何 `import torch` 报 ImportError),保证"不依赖 torch"由运行器强制。`--allow-torch` 关掉,
`--block-torch` / `OPS_BLOCK_TORCH=1` 对任何设备强制打开。

---

## 4. 性能:`harness/benchmark/run.py`

性能测试**复用 `suite/perf/` 的 100 个算子**:每个在**稳态 shape**(由执行设备的末级缓存推导,
约 8×LLC 的工作集;计算密集型用固定大 shape)上计时,只比 **kernel 时间**,与 stock Triton
的同一 kernel 逐项对比。门槛:**每类(memory / reduction / compute)geomean 加速比 ≥ 0.80**。

```bash
EVID=<项目仓库>/bench-evidence

# 1) stock Triton 基线(同机同 shape;需要 torch)
python3 harness/benchmark/run.py --device torch-gpu --baseline --out-dir $EVID

# 2) 你的编译器:先对拍、后计时
python3 harness/benchmark/run.py --device yourmod:make_device --out-dir $EVID

# 3) 逐类 geomean 加速比
python3 harness/benchmark/report.py --results-dir $EVID --out $EVID/BENCH_SUMMARY.json
```

- 主指标 `kernel_s` 是设备端计时的 **median**;`compile_s` 是首次 launch(含编译)。
- **只有对拍过的记录计分**:`--no-verify` 的编译器记录是 `verified: false`,不进 geomean。
- `report.py` 只在两边 `operator_sha256` **和** shape 都一致时配对;不一致的列为 stale,
  不进 geomean——这是刻意的防错,基线过期就重跑第 1 步。
- 只跑一个类 / 一个 entry:`--group memory`、`--only <id>`;只对拍不计时:`--verify-only`。
- 方法学细节见 [`../benchmark/README.md`](../benchmark/README.md)。

---

## 5. golden 缓存:第二次运行为什么快

`(算子文件, 共享代码, shape, dtype, seed)` 完全决定 case,所以输入与期望值缓存在
`$HOME/.cache/ops-golden`(`OPS_GOLDEN_DIR` 可改;这是运行时缓存目录,与语料无关),第二次运行直接读。对拍结果与是否命中缓存无关。

| 现象 | 对策 |
|---|---|
| 语料更新后第一次变慢 | 正常:内容寻址的 key 变了;`python3 -m opslib golden --prune` 清旧条目 |
| 怀疑缓存脏了 | `--no-golden` 强制重建 |
| perf 车道第一次跑慢 | 先并行预构建:`python3 -m opslib golden --build --workload suite/perf/workload.json -j 16` |
| 缓存超过上限 | 总量上限 `OPS_GOLDEN_MAX_TOTAL`(默认 64 GiB,LRU);bench 稳态 case 很大,上限要大于实际总量 |

(`python3 -m opslib ...` 需要 `PYTHONPATH=harness`。)

---

## 6. 已知情况

- **autotune 算子在 `--device cuda` 上是 `LAUNCH_FAIL`**:stock Triton 的 autotuner 计时时会
  `import torch`,而 cuda 参考装置拦截了 torch。这是参考装置的限制,不是 case 的问题;
  `--device torch-gpu` 上它们通过。你的编译器要自己实现 autotune 的配置选择。
- 少数 case 的指针表里含 host 地址(如 `suite/dev/grouped_gemm_kernel.py`),每次构造的字节不同,
  因此不进 golden 缓存;这不影响对拍。

---

## 7. 常见坑

- **指针 `+ i` 是元素偏移**,不是字节偏移。
- **省略 `other` 的 masked load 结果未定义**,不能默认补零;`tl.where` 不能代替 masked load。
- **bf16 指针的两种 host 语义**:host float32 → cast;host uint16 → 位视图。回读方向要对称。
- **`case["launches"]` 存在时**按顺序复用同一组缓冲多次启动,再统一回读。
- **不支持就明确报错**(文件 / 行、API、原因),不要静默补零、删 load、忽略 mask,
  也不要为了通过去改 `ref`。
