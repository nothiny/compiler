# 观测工具链（matmul 优化轮）

判据量：**guest 动态指令执行次数**（QEMU 10 插件 per-insn exec 回调），
非墙钟、非 TB 翻译数、非宿主 perf；QEMU 墙钟仅辅助记录。

## 组成（全部为本轮新增文件，零编译器改动、零 a100_support 改动）

| 文件 | 作用 |
|---|---|
| `tools/profiling/full_instruction_counts.c` | QEMU 插件（API v4）：对每条翻译出的 guest 指令注册 exec 回调；按 PC 哈希去重（一个 PC 一行，跨 TB 翻译安全）；厂商 `smt.*` 编码解码照抄既有探针（stock disassembler 不认识）；集中式类别表（ime/vec-config/vec-mem/vec-arith/scalar-load/scalar-store/atomic/scalar-arith/branch/system）；输出含每行原始 mnemonic（离线可审计、可重分桶）、每 vcpu 计数、vcpu 汇总。 |
| `tools/profiling/build_plugin.sh` | 用与 `a100_support/probes.py` 相同的 include 标志编译插件（从 `.env` 推导）。 |
| `tools/profiling/validate/straight.S` `loop.S` `vendor.S` | 解析已知动态计数的校准程序（freestanding、静态、`_start`+ecall 退出；`-march=rv64gcv` 同项目 ASFLAGS）。 |
| `tools/profiling/validate_counts.py` | 口径校准：汇编→QEMU+插件→精确断言（类别、per-PC、per-vcpu、确定性双跑、objdump 静态交叉核对）。 |
| `tools/profiling/insn_manifest.py` | 编译器侧联结器：`program.S` 的 `[opN]` 注释（发射器默认溯源）× `stage.mir.allocated.txt`（renumber 序=op 序）× `as -alh` listing（源行→地址，`li` 伪展开归同行）× `nm`/`objdump -s` 仿射偏移+**字节同一性校验**（重汇编 .text 必须与已交付 ELF 的程序区逐字节一致，否则拒绝联结）。origin 标签：spill/reload/vec-config/const-materialization/scalar-mem/vec-mem/vec-arith/branch/frame/op:*；运行时区按 `a100rt_*` 等符号归属；字节数为模型值（标量 8B；向量 VLEN/8×lmul@vlmax），明确标注。 |
| `tools/profiling/collect_metrics.py` | 采集器：按验收 scan 同路径 staging（native_device+factory，golden 输入，seed=30 同 scan）；`--repeats 1` 与 `--repeats 1+R` 两次 QEMU 运行之差 /R = **稳态每调用画像**（loader/pool/bundle init 对消）；输出指标 JSON（见下）。 |
| `tooling/sweep.sh`（本目录） | 代表子集批量采集（resume-safe）。 |

## 口径校准结果（phase-a/validation.json，全部精确通过）

- straight（12 条静态）：每 PC 恰执行 1 次，类别逐条吻合。
- loop（1000 次×8 条体）：总动态 8006 = 4+8×1000+2，类别与 per-PC
  多重集 {1000×8, 1×6} 精确吻合；双跑计数一致（确定性）。
- vendor：`smt.vmadot`(i8) 经编码解码计入 ime 类（12 条程序：5 标量
  算术+3 vec-config+1 vec-arith+3 vec-mem+1 ime+1 system）。
- 版本：qemu-riscv64 10.0.2（jdsk），plugin API v4，gcc 11.4.0，
  交叉工具链 toolchain-1.1.2（`-march=rv64gcv` 同 a100c/runtime/build.py）。
- 已知限制：可执行文件为动态链接——loader 指令计入总量但落在程序
  符号区之外（单独归入 loader/unknown 桶，不与程序指令混淆）；
  向量访存字节数为 vlmax 模型值（分配器仅在常量 vl 区 spill）。

## 采集器输出的指标（metrics.json，每 case×threads 一份）

- `runs.r1/r2`：原始两次运行的总量/类别/per-vcpu/QEMU 命令/墙钟/运行时
  末行 JSON（运行时自校验 `repeats_all_equal`）。
- `steady_state`：每调用总量、init 总量、每调用类别分解、不可整除 PC
  增量计数（barrier 自旋等非确定性的诚实标志）。
- `program_region`：origin/opcode 每调用分解、spill/reload 指令数与
  模型字节、vsetvli 静态 (sew,lmul) 分布+动态执行数、静态帧/spill/寄存器
  统计（来自 artifact.json stages）。
- `runtime_region_per_call` / `loader_unknown_per_call`：按符号的运行时
  开销（pool/barrier 自旋可单独分析）。
- `hot_pcs_per_call`：top40 热 PC（origin/opcode/源位置/asm 文本）。

## 使用

```bash
set -a; . ./.env; set +a
python3 tools/profiling/validate_counts.py          # 口径校准
python3 tools/profiling/collect_metrics.py \
  --operator suite/dev/matmul_kernel.py --shape 128,128,128 \
  --dtype float16 --threads 1 --steady-repeats 5 --out <dir>
bash docs/compiler-agent/optimizations/matmul/tooling/sweep.sh   # 子集批量
```

## 迭代记录（诚实保留）

1. 首版 vendor.S 用裸字 `0xe200302b` → guest SIGILL（exit -4）：
   该常量只是探针掩码匹配的一个实例，非可执行配置。改为镜像
   `vector_matrix.S` 的已知良好形态（e32/m2 累加器清零、e8/m1 操作数、
   vd 偶数）后通过。裸字尝试记录于本节。
2. 向量访存不接受立即数偏移（`vle8.v v8,8(sp)` 非法）→ 显式 a1/a2
   物化基址。
3. `insn_manifest.parse_program_s` 首版以 4 空格缩进判指令——但发射器的
   op 行无缩进（仅 render() 的 workspace/指令点行有），导致 program 区
   几乎全部漏联结（8/7374）。修正为"非注释/指令点/标签即指令"。
4. collect_metrics 首版 per-pc 循环变量名 `row` 遮蔽 case row →
   KeyError，已改名。
