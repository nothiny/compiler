# a100c 使用文档

`a100c` 是面向 A100 目标（RV64GC / lp64d，RVV 1.0 VLEN=1024 ELEN=64，IME 矩阵扩展）
的单算子原生编译器：它把 `ops/` 语料库中的 Triton `@triton.jit` kernel 连同其 case
参数编译成一个**独立的 ELF64 小端 RISC-V 可执行文件**。Python 只参与编译、打包和
结果比较；编译产物本身不启动、不嵌入、不调用 Python——它是一个带预编译 C 运行时
（线程池、bundle 读取、stage barrier）的完整原生程序。

```
源码 (AST) → 特化 → TIR → 基础优化 → grid 模型 → 执行计划
          → MIR → 合法化 → 指令选择 → 寄存器分配 → 汇编发射
          → 交叉 as + ld + 预编译 runtime → operator_exec (ELF64 RISC-V)
```

**两个执行端点，同一份产物**：

| 端点 | 用途 | 入口 |
|---|---|---|
| QEMU 用户态模拟器（`-cpu max,vlen=1024`） | 项目声明的**功能正确性验收**端点：执行 + 与参考数值比对 | `tools/run_scan.py`（§2） |
| K3 开发板真机（CPU 8-15，A100 核） | 实硅验证 / 性能测量 | `board-perf-pack*/run.sh`（§5） |

产物在两个端点上的 CLI、状态 JSON、输入输出契约完全一致。

---

## 1. 环境准备

所有工具路径都声明在项目根目录的 `.env` 中（交叉工具链、sysroot、QEMU、
`A100_COMPILER_FACTORY` 等）。大多数入口会自动读取它；手动写 Python 时先导出：

```bash
cd /home/i_yinzida/compiler-a100-experiment-001
set -a; . ./.env; set +a
```

关键变量：

| 变量 | 含义 |
|---|---|
| `A100_CROSS_PREFIX` | 交叉工具链前缀（`riscv64-unknown-linux-gnu-`） |
| `A100_SYSROOT` | 交叉链接用的 sysroot |
| `A100_QEMU` / `A100_QEMU_CPU` | QEMU 用户态模拟器及 CPU 型号；**仅 host 模拟执行需要**，真机用不到 |
| `A100_COMPILER_FACTORY` | `a100c.factory:make_compiler`，原生设备的编译器入口 |
| `A100C_CACHE_DIR` | 产物缓存根目录（默认 `a100c/cache`） |
| `A100_COMPUTE_THREADS` | 原生设备默认 worker 数（1/2/4/8，默认 1） |
| `A100_EXECUTION_TIMEOUT` | 单 case 执行墙钟上限（秒，默认 120） |

---

## 2. 快速开始（QEMU 端点）：一条命令编译并运行一个算子

`tools/run_scan.py` 是模拟器端的日常入口：枚举 case → 按"编译身份"去重 → 编译 →
打包 → QEMU 执行 → 按 case 自己声明的比较策略对比参考输出。它自己加载 `.env`
和 `PYTHONPATH`：

```bash
# 编译 + 运行 + 比较一个算子的全部 (shape, dtype) case
python3 tools/run_scan.py run --operator suite/dev/absolute_kernel.py

# 用 4 个 worker 执行（同一个产物，不需要重新编译）
python3 tools/run_scan.py run --operator suite/dev/absolute_kernel.py --threads 4

# 只跑前 N 个 case；或整个分组
python3 tools/run_scan.py run --group suite/dev --limit 50
python3 tools/run_scan.py run --group suite/perf
```

`--operator` 接受项目相对（`ops/suite/dev/x.py`）、语料相对（`suite/dev/x.py`）
或绝对路径，可重复给出。每个 case 输出一行状态：`PASS`（执行并比对通过）、
`COMPILE_REFUSED`（带源位置的编译期拒绝，见 §8）、`LAUNCH_FAIL` / `TIMEOUT` /
`MISMATCH` / `CASE_FAIL` / `EVIDENCE_FAIL`。退出码 `0` = 本轮跑完（单 case 失败
是记录行，不是退出失败）。

全量扫描（带断点续跑）：

```bash
python3 tools/run_scan.py run \
  --report docs/compiler-agent/SCAN_<id>/run/report.json \
  --run-id <id> --journal docs/compiler-agent/SCAN_<id>/run/journal.jsonl

# 中断后续跑（不重编译已完成身份）：
python3 tools/run_scan.py run --journal .../journal.jsonl --resume [--retry-failed]
```

其他常用参数：`--case-timeout <秒>`、`--resource-threads {2,4,8}`、
`--fault-inject ID[:KIND]`、`--seed`、`--no-golden`。

---

## 3. 编译单个算子（Python API）

编译入口是 `compile_case(case) -> artifact`。`case` 是语料 harness 的
`make_case()` 产物（一个 dict），编译器只消费执行契约，**永远拿不到期望输出**：

```python
import importlib.util, json

from a100c.factory import make_compiler   # 生产路径（含基础优化 pass）

spec = importlib.util.spec_from_file_location(
    "op", "ops/suite/dev/absolute_kernel.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

case = module.make_case(shape=(97,), dtype="float32", seed=30)

compiler = make_compiler()
art = compiler.compile_case(case)        # 同一身份第二次调用是纯缓存命中

print(art.executable)    # a100c/cache/<key>/operator_exec
print(art.sha256)
print(art.cache_hit)
```

case payload 的主要字段：`kernel`、`args`（ndarray/标量输入）、`allocations`
（输出缓冲）、`grid`、`meta`（constexpr 等）、`comparison`（每个输出的比较器/
rtol/atol）。`expected`/`oracle_args` 只用于比较，进入编译器前被剥掉。

---

## 4. 运行编译产物（通用契约）

产物是一个原生进程：

```
operator_exec --bundle <bundle.bin> --threads <1|2|4|8> [--repeats <k>]
```

输入输出全部走 `bundle.bin`（`a100-native-io/v1` 格式，由
`a100_support/native_io.py` 的 `pack_case` 打包、`unpack_outputs` 解包）。
进程在 stdout 打一行状态 JSON：

```json
{"runtime":"a100rt/v1","status":"ok","threads":4,"repeats":3,
 "pool_initializations":1,"repeats_all_equal":true,
 "workers":[{"id":0,"guest_tid":123,"items":25},{"id":1,...}],
 "bundle_bytes":8192}
```

- `workers[w].items`：每个 worker 实际处理的工作量（分区由程序运行时从
  `--threads` 计算，同一份 ELF 对 1/2/4/8 通用）。
- `--repeats k`：同一 case 独立执行 k 次（每次先恢复输入快照再执行），
  `repeats_all_equal` 校验 k 次结果一致——重复调用正确性的直接证据。
- 退出码：`0` ok；`2` 用法；`3` bundle 拒绝；`4` 资源；`5` repeat 不一致；
  `6` 输出同步失败。被信号杀死时 shell 显示 128+信号号（如 **132 = SIGILL**）。

### QEMU 端点的两种跑法

```python
# A. 原生设备协议（推荐，打包/执行/回读全自动）
import a100_support.native_device as nd
device  = nd.NativeExecutableDevice(compiler, threads=4)
staged  = device.stage_case(case)   # 编译(或缓存命中) + 打包
staged.launch()                     # 经 run-riscv.sh 在 QEMU 中执行
outputs = staged.outputs()          # dict: 输出名 -> ndarray
```

```python
# B. 手动（看清产物到底是什么）
from pathlib import Path
from a100_support.native_io import pack_case, unpack_outputs
stage = Path("/tmp/mycase"); stage.mkdir(parents=True, exist_ok=True)
pack_case(case, stage)               # 写出 stage/bundle.bin
```

```bash
a100_support/run-riscv.sh a100c/cache/<key>/operator_exec \
    --bundle /tmp/mycase/bundle.bin --threads 4 --repeats 3
# run-riscv.sh = qemu-riscv64 -L $A100_SYSROOT -cpu $A100_QEMU_CPU <参数>
```

真机端点见下一节——产物、bundle、CLI、JSON 契约与上面完全一致。

---

## 5. 真机（K3 开发板）运行

### 5.1 板级事实（实测确认）

- K3 = 8×X100 通用核 + 8×A100 AI 核，Linux 以 16 核统一视图暴露；
  **CPU 0-7 = X100（系统默认域，`allow_cpu` 默认限在这里），CPU 8-15 = A100**
  （VLEN=1024，带 IME 矩阵扩展；官方推理示例即用 8-15）。
- 编译产物必须钉在 8-15 上跑（`taskset -c 8-15`）；X100 上没有 `smt.*`
  矩阵指令，IME 路径的算子会 SIGILL。
- 产物是动态链接的 riscv64 glibc（lp64d），板子 rootfs 需兼容；先
  `ldd bin/<case>/operator_exec` 确认能解析。

### 5.2 最快路径：现成测试包

项目里有两个打包好的真机测试包（编译好的 ELF + 输入 bundle + 运行脚本）：

| 包 | 内容 | 适用 |
|---|---|---|
| `board-perf-pack-22.tar.gz` | **22 个板上验证过的 case**（计算/访存/归约 × 8 种 dtype） | 日常真机测试（推荐） |
| `board-perf-pack.tar.gz` | 28 个 case（多 6 个：见 §5.6 已知问题） | 兼容性调试 |

```bash
# 宿主机：
scp board-perf-pack-22.tar.gz <board>:

# 板子上：
tar xzf board-perf-pack-22.tar.gz && cd board-perf-pack-22
./run.sh
```

`run.sh` 的行为：每次执行都 `taskset -c 8-15`；每个 case 跑 `--threads 1` 和
`--threads 8` 两组（先 warmup + runtime 自检，再计时 repeats 循环）；单次调用
有 600 秒超时保护（-22 包已内置）；结果写 `results/summary-*.tsv`
（case/threads/us_per_iter/pool_init/最小 worker items）和
`results/raw-*.log`（完整状态 JSON）。

环境变量：`A100_CPUS=8-15`（CPU 列表）、`A100_THREADS="1 8"`（线程档）、
`A100_REPEATS_MULT=<n>`（repeats 倍率）。`cases.conf` 每行 `name:repeats`，
`#` 开头跳过。

### 5.3 进不了 8-15 怎么办（亲和性设置速查）

`taskset` 无法越过 cgroup（亲和性 = taskset 请求 ∩ cgroup 允许）。按顺序试：

```bash
# ① 让脚本自己修（检测到限制时以 root 把当前 cgroup 写成 8-15）
sudo ./run.sh

# ② 新建一个允许 8-15 的 cgroup 来跑（不改任何现有文件）
sudo systemd-run --scope -p AllowedCPUs=8-15 ./run.sh

# ③ 手动扩自己所在的 cgroup（cgroup v2；注意 sudo 要包住重定向）
CG=/sys/fs/cgroup$(sed -n 's/^0:://p' /proc/self/cgroup)
sudo sh -c "echo 8-15 > $CG/cpuset.cpus"      # 或写 0-15 更温和

# ④ 厂商机制（K3 设计为"应用显式标注才进 AI 域"）：
SPACEMIT_PERFER_CORE_ID="8,9,10,11,12,13,14,15" ./run.sh
#    跑一个长任务后 grep Cpus_allowed_list /proc/<pid>/status 验证是否生效

# ⑤ 容器场景：容器启动时 --cpuset-cpus=8-15
```

验证：`grep Cpus_allowed_list /proc/self/status` 应显示 `8-15` 或 `0-15`。

### 5.4 从零生成自己的真机测试包

编辑 `board-perf-pack/stage_pack.py` 的 `CASES` 表（每行
`名字, 语料相对路径, shape, dtype, 板上 repeats`），然后：

```bash
python3 board-perf-pack/stage_pack.py
```

它对每个 case：按 harness 契约构造 case → 经 `a100c.factory` 编译（缓存命中
则不重编）→ 打包 bundle → **发货前在 QEMU 下以 1/8 线程执行并与参考数值按原始
容差比对**（冒烟不通过的 case 自动剔除出 `cases.conf`）→ 生成 `manifest.json`。
shape 建议取 `ops/suite/perf/workload.json` 的 `source_validated_shape`
（稳态尺寸：单次执行毫秒级、repeats 循环秒级）。

### 5.5 计时口径

`us_per_iter` = 计时循环总时长 / repeats。循环内每次 repeat 除算子本身外，
runtime 还做一次输入快照 memcpy + 输出一致性 memcmp（各一趟 bundle 流量）：
matmul 类可忽略；带宽密集类（elementwise/gather）实际算子时间约为显示值一半。
进程启动、线程池创建被 repeats 摊销（`pool_init` 应为 1）。

### 5.6 已知问题（2026-11-10 实测，使用时注意）

28 case 包中有 6 个在真机失败而 QEMU 通过（-22 包已剔除它们）：

| case | 现象 | 状态 |
|---|---|---|
| attn_causal / flash_decode / softmax / logsumexp | SIGILL（exp/log 数学路径，疑似编码保留位或 vsetvli 配置实硅不接受） | 待定位修复 |
| tanh | warmup 通过，重复执行一致性失败（t1、t8） | 待修 |
| conv_gelu | conv codegen 病态慢，计时轮超时（QEMU 下同样异常慢） | 待修 |

另外：`gelu / add_gelu / swiglu` 的**单线程**计时轮可能因重复一致性失败（t8 正常）；
板上不做参考数值比对（正确性口径 = QEMU 比对通过 + runtime 重复一致性自检）。

### 5.7 常见问题排查

| 症状 | 原因 | 处理 |
|---|---|---|
| `warmup exit 132` | SIGILL：该 case 用了此核不支持的指令（X100 上跑 IME case，或 §5.6 的 exp/log 问题） | 确认在 8-15 上；仍 132 则属已知问题清单 |
| 某个 case 卡很久 | 慢（非死锁）或死锁 | `top` 按 1：CPU 8-15 满载=慢（等/降 repeats）；全空闲=死锁，记录后杀 |
| `taskset: failed to set affinity` | cgroup 限在 0-7 | §5.3 |
| 输出比预期慢 8 倍以上 | 跑在了 0-7（X100）上 | `grep Cpus_allowed_list /proc/self/status` |

---

## 6. 缓存与产物布局

缓存根目录默认 `a100c/cache/`（可用 `A100C_CACHE_DIR` 覆盖），每个身份一个
sha256 key 目录：

```
a100c/cache/<key>/
├── operator_exec            # ELF64 小端 RISC-V 可执行文件（可直接拷上板）
├── program.S                # 完整程序级汇编，每条指令带 [opN] 源位置标注
├── artifact.json            # 身份、sha256、各阶段统计、编译耗时
├── stage.tir.txt            # 前端 TIR dump
├── stage.passes.txt         # 基础优化 pass 的重写统计
├── stage.plan.txt           # grid 模型 / 分区 / 参数布局 / 目标模型
├── stage.mir.lowered.txt    # lowering 后的 MIR
├── stage.mir.legalized.txt  # 合法化后的 MIR
├── stage.mir.allocated.txt  # 寄存器分配后的 MIR + 分配结果
└── stage.selection.txt      # 每个操作的指令选择结果
```

**缓存身份（key）= 特化身份 + 编译器修订（代码摘要）+ 目标模型 + 编译选项 +
参数布局摘要（+ pass 配置）**。shape、grid 数值、缓冲内容、标量值、worker 数
一律**不进 key**：同一身份的所有 case 共享一份产物，所有线程数共用同一份 ELF。

---

## 7. 优化开关与检查工具

六个基础优化 pass（常开，legality 条件下总是有益）可以用环境变量单独关掉，
开关会改变缓存 key：

```bash
A100C_PASS_CSE=off        # 公共子表达式消除
A100C_PASS_DCE=off        # 死代码消除
A100C_PASS_CONSTPROP=off  # 常量折叠/传播
A100C_PASS_COPYPROP=off   # 拷贝传播
A100C_PASS_STRENGTH=off   # 强度削减
A100C_PASS_LICM=off       # 循环不变量外提
# 取值 off/0/false/no；全部关闭时的产物与裸驱动字节一致
```

四个带"反证"的工程检查（`--witness` 注入缺陷后**必须**非零退出）：

```bash
python3 tools/check_no_name_dispatch.py [--witness]  # 不得按算子/内核名分支（required）
python3 tools/check_numeric_policy.py   [--witness]  # 容差/参考必须读自 case
python3 tools/check_masked_tails.py     [--witness]  # 尾部掩码不得越界访问
python3 tools/check_stage_barriers.py   [--witness]  # 跨 worker 可见性必须有 barrier
```

---

## 8. 拒绝行为（诊断而非静默出错）

前端声明了 107 个构造 / 280 个参数的支撑面。超出支撑面或在当前目标上非法的
构造，编译器以 `PipelineError` 拒绝，并携带**源位置（`文件:行:列`）和构造名**
（"located refusal"）；在扫描里记为 `COMPILE_REFUSED` 行，不会崩溃、不会猜测、
也不会回退到参考实现。MIR 验证器同样会在每个后端阶段后复查（含 IME 操作数
合法性：LMUL=1、vs1 行主序 A、vs2 列主序 B、MUL_C=2 时 vd 偶数、无目的/源
重叠等）。

---

## 9. 测试

每个测试模块独立可运行（自带 sys.path 引导），退出码即结论：

```bash
python3 a100c/tests/test_e2e_slice.py       # 端到端垂直切片：编译→QEMU→比较
python3 a100c/tests/test_driver_cache.py    # 缓存身份 / 编译一次语义
python3 a100c/tests/test_compile_sweep.py   # 全语料编译清扫
python3 a100c/tests/test_repeated_calls.py  # --repeats 重复调用一致性
python3 a100c/tests/test_final_regression.py
```

分层覆盖（`a100c/tests/` 下）：前端/IR（`test_frontend_surface` `test_specialize`
`test_frontend_types` `test_frontend_shapes` `test_grid_model` `test_tir_verifier`
`test_mir_verifier`）、优化（`test_passes_basic`）、lowering（`test_lower_vector`
`test_lower_scalar` `test_lower_matrix` `test_control_flow` `test_reductions`
`test_memory_forms` `test_atomics` `test_layout_ops` `test_conversions`
`test_math_ops` `test_rng` `test_matrix_breadth`）、后端/运行时（`test_legalize`
`test_select` `test_allocate` `test_emit` `test_build` `test_runtime_smoke`）、
端到端/证据（`test_e2e_slice` `test_driver_cache` `test_compile_sweep`
`test_scan_report` `test_evidence_files` `test_repeated_calls` `test_ime_evidence`
`test_final_regression`）。

---

## 10. 典型完整流程

```bash
cd /home/i_yinzida/compiler-a100-experiment-001

# ── 模拟器（功能正确性验收端点）──────────────────────────────
# ① 单算子调试：编译 + 执行 + 比较
python3 tools/run_scan.py run --operator suite/dev/absolute_kernel.py --threads 1
python3 tools/run_scan.py run --operator suite/dev/absolute_kernel.py --threads 4

# ② 看中间产物（读缓存目录）
ls a100c/cache/<key>/        # program.S、stage.*.txt、artifact.json

# ③ 全量回归（断点续跑）
python3 tools/run_scan.py run \
    --report docs/compiler-agent/SCAN_<id>/run/report.json \
    --run-id <id> --journal docs/compiler-agent/SCAN_<id>/run/journal.jsonl

# ── 真机（K3 开发板，A100 核 8-15）──────────────────────────
# ④ 直接用现成包（22 个板上验证过的 case）
scp board-perf-pack-22.tar.gz <board>:
#    板上：tar xzf board-perf-pack-22.tar.gz && cd board-perf-pack-22 && ./run.sh

# ⑤ 自定义 case 集重新生成包（编辑 stage_pack.py 的 CASES 后）
python3 board-perf-pack/stage_pack.py && tar -czf my-pack.tar.gz board-perf-pack/

# ── 工程自检 ────────────────────────────────────────────────
python3 tools/check_no_name_dispatch.py
python3 tools/check_numeric_policy.py
python3 tools/check_masked_tails.py
python3 tools/check_stage_barriers.py
```
