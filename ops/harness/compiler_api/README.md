# compiler_api:统一、无 torch 的算子执行接口

把"算子文件"和"编译器 runtime"解耦:算子文件只描述 **一个 `@triton.jit` + 一个 numpy case**;
设备分配、host↔device 拷贝、启动、回读、对比都在 harness 里,由你实现一个很小的 `Device`
接口接入。接口与执行路径零 torch。

**怎么用、怎么拿反馈**见 [`AGENT_GUIDE.md`](AGENT_GUIDE.md)(写编译器的 agent 先读它)。
**怎么编译得最快、三条车道、并行驱动怎么接**见 [`RUNBOOK.md`](RUNBOOK.md);
**适配器要实现什么协议**见 [`COMPILE_CONTRACT.md`](COMPILE_CONTRACT.md)。本文是接口细节的参考。

```bash
python3 harness/compiler_api/run_cases.py --dry-run --identities   # case 3465 / identity 1511
python3 harness/compiler_api/gate.py --device cuda --report runs/gate.json   # 门禁,退出码 0/1
```

## 文件

```
harness/compiler_api/
  AGENT_GUIDE.md    写编译器的 agent 的指南(先读)
  RUNBOOK.md        怎么用、怎么最快编译、并行驱动怎么接
  COMPILE_CONTRACT.md  适配器协议(identity/compile/launch/cost/cache_key)
  README.md         本文:接口细节
  run_cases.py      枚举并运行全部 case,四状态反馈(正确性入口)
  gate.py           编译门禁:时间/身份/失败类判定,写 JSON 报告,退出码 0/1
  identity.py       编译身份普查(--identities / --schedule)
  manifest.py       生成 ../../manifest.json(语料维护者用)
  api_inventory.py  生成 ../../docs/API_INVENTORY.md(语料维护者用)
  device.py         shim → opslib.device:Device 协议、run_case、stage_case
  reference.py      shim → opslib.devices.torch_ref:torch 基线装置
```

## `Device` 协议

```python
class Device:
    def alloc(self, shape, dtype) -> Buffer: ...
    def upload(self, array: np.ndarray, dtype=None) -> Buffer: ...
    def download(self, buffer: Buffer) -> np.ndarray: ...
    def pointer(self, buffer: Buffer) -> int: ...          # 默认 buffer.data_ptr()
    def launch(self, kernel, grid, positional, keywords) -> None: ...
```

- `alloc(shape, dtype)`:按声明的指针 dtype 分配;`dtype` 是字符串(`"float32"`、`"bfloat16"`…)
  或 numpy dtype。
- `upload(array, dtype=None)`:`dtype` 是 case 里 `pointer_dtypes` 声明的指针类型,`None` 表示与
  `array.dtype` 相同。bf16:host `float32` → cast;host `uint16` → 位视图。只实现
  `upload(array)` 也可以,`run_case` 会检测签名。
- `download(buffer)`:返回与 host 缓冲同 dtype / shape 的 numpy;bf16 方向与 upload 对称。
- `launch(kernel, grid, positional, keywords)`:`positional` 已按 kernel 形参顺序绑定(numpy 标量
  已转 Python 标量);`keywords` 已含 `launch_meta`;autotune 提供的 constexpr 已跳过,由你的
  autotune 实现填入。
- `Buffer` 只需 `data_ptr()`、`dtype`、`shape`。

可选钩子(`upload_aliased`、`compare`、`timer`、`properties`、`release`)的语义见
[`AGENT_GUIDE.md`](AGENT_GUIDE.md) §2。

## `run_case` / `stage_case`

```python
from compiler_api.device import run_case, stage_case
actual = run_case(case, device)      # -> {output_name: np.ndarray}
staged = stage_case(case, device); staged.launch(); staged.outputs()
```

步骤:取 `{**allocations, **args}` 中的 numpy 缓冲,按 `pointer_dtypes` 逐个 upload(共享内存的
参数走 `upload_aliased`)→ 应用指针表 relocation → 对 `case["launches"]` 中的每个覆盖(默认
一次)绑定实参并 `launch` → download 每个 output。

指针表:
- `pointer_table_relocations`:`{table, entry, allocation, byte_offset}`,把 `allocation` 的设备
  地址写进 `table` 的第 `entry` 项;
- `pointer_relocations`(旧 schema):dict `{table: [{index, allocation, element_offset}]}` 或
  list `[{table_arg, element_index, allocation_arg, byte_offset}]`。

## Python API

```python
from compiler_api.run_cases import enumerate_cases, run_all

for spec, shape, dtype in enumerate_cases("all", group="medium"):
    ...
rows = run_all(my_device, group="basic")    # 每行 {operator, group, shape, dtype, status, detail}
```

`run_all` 的 case 来自 golden 缓存(`use_golden=False` 强制重建);`shard=(i, n)` 只保留枚举序号
`≡ i (mod n)` 的 case。

## 参考装置

| `--device` | 实现 | 用途 |
|---|---|---|
| `cuda` | `opslib/devices/cuda.py`:cuda-python、raw `cudaMalloc`、设备侧对拍、event 计时 | 无 torch 的装置正确性对照 |
| `torch-gpu` | `opslib/devices/torch_ref.py`:torch CUDA 张量 | stock Triton 性能基线 |
| `cpu` | `CpuDevice`:缓冲即 numpy,需要注入 launcher | CPU 后端接入骨架 |

两个 GPU 参考装置的 `launch` 都调用 stock Triton:它们是装置与基线,**不是**编译器的实现模板。
