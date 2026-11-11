# board-perf-pack — K3 开发板 A100 核心性能测试包

本包是**项目所有者（用户）主导的板级测量**，不属于编译器 correctness 工作流的
验收证据；`manifest.json` 里的 QEMU 冒烟记录只是发货前的自检，不进任何 gate。

## 板级事实（用户确认）

- 开发板 `allow_cpu` 默认只允许 CPU **0-7**（系统核）；
- CPU **8-15** 是 8 个 **A100 AI 计算核**（与已归档的 K3 官方推理示例一致）；
- 因此 `run.sh` 把每次执行都用 `taskset -c 8-15` 钉在 A100 核上，并在当前
  cgroup 不含 8-15 时尝试把 `cpuset.cpus` 写成 8-15（需要 root；可用
  `A100_CPUS` 覆盖）。

## 内容

```
run.sh          板上一键测量脚本（1 线程 vs 8 线程，taskset 8-15）
cases.conf      可跑的 case 列表（name:repeats，stage_pack.py 生成）
bin/<name>/operator_exec     每个 case 的独立 RISC-V ELF（riscv64, lp64d, 动态链接 glibc）
cases/<name>/bundle.bin      该 case 的输入数据包（a100-native-io/v1，自包含）
cases/<name>/bundle.json     输入包的 host 侧元数据（取回输出时用）
manifest.json   每个 case 的来源/shape/dtype/ELF sha256/缓存命中/QEMU 冒烟结果
stage_pack.py   （宿主机用）重新生成本包的脚本
```

## 在板上运行

```bash
tar xzf board-perf-pack.tar.gz && cd board-perf-pack
./run.sh                     # 默认测 threads=1 和 threads=8，输出 us/iter 与加速比
A100_REPEATS_MULT=5 ./run.sh # 把每个 case 的 repeats 放大 5 倍（更稳的平均）
A100_THREADS="1 2 4 8" ./run.sh
```

结果落在 `results/summary-*.tsv`（每行：case、threads、us/iter、pool_init、
最小 worker items）和 `results/raw-*.log`（runtime 的完整 JSON 行，含每个
worker 的 `items`——8 线程时每个 worker 的 items 都应大于 0，否则并行没干活）。

板上依赖：`riscv64` glibc（ELF 解释器 `/lib/ld-linux-riscv64-lp64d.so.1`，
需要 `libc.so.6`/`libm.so.6`）、`taskset`、bash 5+（`EPOCHREALTIME`）或
coreutils `date +%s%N`。先跑 `ldd bin/gelu_f32/operator_exec` 确认能解析。

## case 选择（28 个 case：计算 / 访存 / 归约 × 8 种 dtype）

所有算子均来自上一轮全量扫描 **100% PASS** 的算子；perf 车道 shape 取自
`ops/suite/perf/workload.json` 的 `source_validated_shape`（stock Triton 审计
过的稳态尺寸），int16/bool/atomic 三个补充 case 用其扫描通过的原 shape。

**计算（compute，9 个）**

| case | 算子 | shape | dtype | 测什么 |
|---|---|---|---|---|
| matmul_f16 | matmul.py | (256,256,256) | fp16 | 稠密 matmul，**IME fp16 路径**（smt.vfwmadot） |
| matmul_bf16 | matmul.py | (256,256,256) | bf16 | 同 shape 对照：bf16 走**向量 FP32 路径** |
| matmul_f32 | matmul.py | (256,256,256) | fp32 | IEEE fp32 dot（向量路径） |
| matmul_t2_bf16 | matmul_triton2.py | (256,256,256) | bf16 | 第二种 matmul 骨架（不同 tiling） |
| dq_matmul_bf16 | dequantize_matmul.py | (256,32) | bf16 | 反量化 + matmul |
| attn_causal_bf16 | attn_fwd_causal.py | (1,8,256,64) | bf16 | causal attention（8 头对 8 worker） |
| flash_dec_bf16 | flash_decode.py | (1,8,256,64) | bf16 | decode attention（KV cache 形态） |
| chunk_ret_bf16 | chunk_retention.py | (8,2,16,32,32) | bf16 | chunk 线性注意力（循环携带 dot） |
| conv_gelu_bf16 | gelu_conv2d.py | (512,) | bf16 | 卷积窗口寻址 + 激活 |

**访存（memory，9 个）**

| case | 算子 | shape | dtype | 测什么 |
|---|---|---|---|---|
| gelu_f32 | gelu.py | (262144,) | fp32 | 纯带宽 elementwise（erf） |
| tanh_bf16 | tanh.py | (262144,) | bf16 | 超越函数带宽 |
| add_gelu_f16 | add_gelu.py | (262144,) | fp16 | 双输入融合激活 |
| swiglu_bf16 | swiglu_fwd.py | (4096,64) | bf16 | swiglu（门控） |
| relu_strided_bf16 | relu_strided_buffer.py | (262144,) | bf16 | **跨步（非连续）访问** |
| gather_i8 | gather_1d.py | (32768,8) | int8 | 随机 gather（索引密集） |
| gather_i32 | gather_1d.py | (32768,8) | int32 | 同上，int32 |
| gather_i64 | gather_1d.py | (32768,8) | int64 | 同上，int64 |
| signbit_i32 | signbit_bitwise_and.py | (262144,) | int32 | 整型位运算带宽 |

**归约（reduction，7 个）**

| case | 算子 | shape | dtype | 测什么 |
|---|---|---|---|---|
| rmsnorm_bf16 | fast_rms_layernorm.py | (64,1024) | bf16 | 行归约 norm（LLM 典型） |
| argmax_bf16 | argmax.py | (64,1024) | bf16 | argmax（索引归约） |
| max_f16 | max.py | (64,1024) | fp16 | max 归约 |
| mean_f32 | mean.py | (64,1024) | fp32 | mean 归约 |
| softmax_bf16 | softmax.py | (64,1024) | bf16 | 行 softmax（max+exp+sum） |
| logsumexp_f32 | logsumexp.py | (64,1024) | fp32 | logsumexp（数值敏感归约） |
| l2norm_f16 | l2_norm_triton2.py | (64,1024) | fp16 | L2 norm |

**补充 dtype / 特性（3 个）**

| case | 算子 | shape | dtype | 测什么 |
|---|---|---|---|---|
| hardsig_i16 | hardsigmoid_kernel_2.py | (97,) | int16 | int16 数据路径 |
| any_bool | any_kernel_2.py | (126,) | bool | 布尔数据路径 |
| atomic_bitmap_i32 | atomic_bitmap.py | (16,128) | int32 | **原子操作**（8 worker 争用） |

dtype 覆盖：fp32 / fp16 / bf16 / int8 / int16 / int32 / int64 / bool 共 8 种。
说明：① 语料子集中没有 int8 的 `tl.dot` 算子（量化类算子都是 bf16 存储），
所以**本包不含 IME int8（smt.vmadot）数据点**；IME 路径由 matmul_f16
（smt.vfwmadot）代表。② conv 用 (512,)：语料 conv 的稳态尺寸 (4096,) 在
QEMU 功能仿真下超出验证时限（>600s），无法发货前比对，故缩小到可验证尺寸；
板上如需更大 conv，改 `stage_pack.py` 里该 case 的 shape 重新生成即可。

## 测量口径（诚实说明）

- `us/iter` = 计时循环总时长 / repeats。循环内每次 repeat 除算子本身外，
  runtime 还会做一次**输入快照恢复 memcpy + 输出一致性 memcmp**（各一趟
  bundle 大小的内存流量）。对 matmul 类计算密集 case 可忽略；对
  gelu/rmsnorm 这类带宽密集 case，实际算子时间约为 us/iter 的一半左右。
- 进程启动、bundle mmap、线程池创建已被 repeats 摊销（`pool_init` 应为 1）。
- runtime 自带 repeat 一致性自检（不一致会以 `repeat-mismatch` 非零退出），
  但**板上不做与参考的数值比较**。发货前每个 (ELF, bundle) 对在固定 QEMU
  端点以 threads=1 和 8 各执行一次并与该 case 的独立参考按原策略比对通过
  （见 `manifest.json` 的 `smoke` 字段）。
- fp16 与 bf16 的路径差异是**编译期决定**（bf16 IME 的仿真器格式控制缺口
  使 bf16 dot  lowering 到向量 FP32 路径），板上跑的 bf16 二进制同样走向量
  路径；两组数据的差就是 IME 路径与向量路径的真实差距。

## 重新生成（宿主机）

```bash
python3 board-perf-pack/stage_pack.py    # 编译走 a100c 缓存；未命中会现编
```

注意：本包反映打包时刻的编译器状态（修复轮进行中，上一轮全量扫描仍有 62
个失败 case，不含本包算子）。要出正式数字，等全量回归变绿后重新生成。
