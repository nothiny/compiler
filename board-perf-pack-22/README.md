# board-perf-pack-22 — K3 开发板 A100 核心性能测试包（22 个板上验证过的 case）

28 case 完整包的**板级干净子集**：产物（ELF）与输入包（bundle）与完整包完全一致，
只移除了 6 个在真实开发板上失败的 case。所有 22 个 case：

- 在固定 QEMU 端点下与独立参考按原始容差比对通过（发货前逐个验证，1/8 线程）；
- 在真实 K3 开发板 CPU 8-15（A100 核）上正常运行并采集过 1/8 线程数据
  （`summary-20261110-123441.tsv`，本轮包即按该结果筛选）。

## 在板上运行

```bash
tar xzf board-perf-pack-22.tar.gz && cd board-perf-pack-22
./run.sh                        # taskset 8-15，threads 1 和 8，单次调用 600s 超时保护
A100_REPEATS_MULT=5 ./run.sh    # 放大 repeats
A100_THREADS="1 2 4 8" ./run.sh
```

结果：`results/summary-*.tsv`（case/threads/us_per_iter/pool_init/最小 worker items）、
`results/raw-*.log`（runtime 完整 JSON）。

板上依赖：riscv64 glibc、`taskset`、bash5+（`EPOCHREALTIME`）。`run.sh` 已内置
`timeout 600`：任何单次调用超时记 FAIL 继续跑，不会卡死。

## 22 个 case

| 类别 | case（算子 / dtype / shape / repeats） |
|---|---|
| 计算 | matmul_f16 (IME) · matmul_bf16 · matmul_f32 · matmul_t2_bf16——各 (256,256,256)×30；dq_matmul_bf16 (256,32)×200；chunk_ret_bf16 (8,2,16,32,32)×100 |
| 访存 | gelu_f32 (262144,)×500 · add_gelu_f16 (262144,)×500 · swiglu_bf16 (4096,64)×500 · relu_strided_bf16 (262144,)×500 · gather_i8/i32/i64 (32768,8)×500 · signbit_i32 (262144,)×500 |
| 归约 | rmsnorm_bf16 · argmax_bf16 · max_f16 · mean_f32 · l2norm_f16——各 (64,1024)×1000 |
| 补充 | hardsig_i16 (97,)×2000 · any_bool (126,)×2000 · atomic_bitmap_i32 (16,128)×1000 |

仅 `matmul_f16` 的 dot 走 IME 矩阵指令（`smt.vfwmadot`），其余全部为纯 RVV 1.0 + RV64。

## 已知限制（引用数据时保留）

1. **gelu_f32 / add_gelu_f16 / swiglu_bf16 的 t1 计时可能失败**（板上单线程重复执行
   一致性问题，待修）：失败时该 case 只有 t8 数据，run.sh 会记 FAIL 后继续。
2. µs/iter 含 runtime 每次-repeat 的输入快照恢复 + 输出比对（各一趟 bundle 流量）；
   matmul 类可忽略，带宽密集类实际算子时间约为显示值一半。
3. hardsig_i16 / any_bool 尺寸过小（97/126 元素），计时为纯开销噪声，仅作 dtype 覆盖。
4. 板上不做与参考的数值比对（正确性由"同一二进制+输入在 QEMU 下与参考比对通过 +
   runtime 重复一致性自检"保证）。

## 移除记录（6 个，勿删本节——这是板级兼容性工作清单）

| case | 移除原因（板上实测） |
|---|---|
| attn_causal_bf16 | SIGILL，首次执行即挂（exp/log 数学路径） |
| flash_dec_bf16 | 同上 |
| softmax_bf16 | 同上 |
| logsumexp_f32 | 同上 |
| tanh_bf16 | warmup 通过，重复执行一致性失败（t1、t8 均如此） |
| conv_gelu_bf16 | conv codegen 病态慢，计时轮超 600s（QEMU 下同样异常慢，非板子问题） |

这 6 个是"模拟器通过、实硅失败"的实硅兼容性问题（QEMU `-cpu max` 是功能模型，
对手写编码器的保留位宽松；实硅严格），定位与修复在编译器侧进行；完整包
`board-perf-pack/` 仍保留它们用于调试。

## 重新生成（宿主机）

```bash
python3 board-perf-pack-22/stage_pack.py   # CASES 已裁剪为 22 个；走 a100c 编译缓存
```
