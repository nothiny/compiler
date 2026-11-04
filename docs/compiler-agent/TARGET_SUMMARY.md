# A100 项目知识摘要

当前只验收正确性，不要求性能指标、计时输出、加速比、调优 sweep 或测量驱动的性能优化轮次。
通用优化仍是正常编译器实现：CSE、DCE、常量折叠与传播、复制传播、强度削减和 LICM
须按合法性条件接入默认编译路径，并验证变换和完整结果；不能因不要求性能指标而省略。

本项目只让 K3 A100 执行生成的计算代码。多核支持和适用矩阵算子的 IME 路径均为必需；单核是调试与对照配置。系统和 workflow 可以运行在其他核心。

## 必须带入实现的事实

| 项目 | 已读资料的结论 | 实现影响 |
|---|---|---|
| 向量能力 | A100 VLEN=1024，RVV 1.0 | 根据实际宽度处理向量布局与尾块 |
| 普通矩阵 | INT4 8×32×8；INT8 8×16×8；FP16/BF16 8×8×8，浮点累加 FP32 | 布局和 lowering 必须区分指令族 |
| 寄存器 | 当前矩阵实现 LMUL=1；目的与输入不重叠；双寄存器目的偶数对齐 | 约束贯穿指令选择与分配 |
| 隐式状态 | v0/v1 的稀疏/缩放用途与 MCPM 浮点格式选择 | 显式跟踪隐式操作数和控制状态 |
| 多核资源 | Preview 描述矩阵引擎由两个计算核心共享 | 不把八个工作线程当成八份独立矩阵吞吐；上板确认配对 |
| 本地存储 | 手册标注每 cluster 1.5 MB scratchpad | 不能误当成每线程私有容量；可用量和分配接口待测 |
| 标称性能 | 60 TOPS 限定 INT4 sparse | 不能直接用于浮点或普通稠密算子目标 |
| 软件示例 | 官方推理示例用 8–15 核心编号与显式资源分配 | 只是示例，必须探测实际允许集合 |

精确来源见下方来源索引，版本和摘要见 `target-material/manifest.json`；运行时由 agent 读取原文并记录 Fact。归档不等于逐页审阅：本次提炼重点为 CPU 手册 A100 章节、矩阵规范第 1–2 章和编码约束、官方并行推理章节，以及 Preview 共享计算章节。其他章节可搜索后按需阅读。中文/英文同一规范都已归档。遇到冲突同时保留来源并解析适用范围。

## 多核实现要求

使用持久工作线程池；任务数和线程数独立。当前 QEMU 验证 guest 线程的实际分工；上板后只在实测识别的 A100 集合放置工作线程。矩阵乘优先分配互不重叠的输出 tile；共享输入打包须明确生产、可见、读取和释放时机。跨线程归约需要显式合并，遵守输入比较策略。记录每个工作线程完成的单位、观察到的核心以及实际工作区间，不能以创建线程数替代并行证据。

线程数、输出分块、寄存器分块、打包布局及共享引擎放置须保证覆盖、数据可见性和计算结果正确。保留 1/2/4/8 工作者的可配置路径；实际 sweep 只使用当前允许集合支持的配置。小问题允许选择少量工作线程，但完整交付必须在足够大的代表性算子上证明多核实际工作。不能把独立测试用例并发执行当作生成代码并行。

## 矩阵路径要求

矩阵指令必须出现在选中并执行的变体里。保存最终反汇编或指令清单、产物校验值、运行日志和参考比较结果。普通向量/标量路径覆盖不适合矩阵指令的操作、形状和尾块。矩阵指令清单中的静态出现不能单独证明动态执行；需要归因时增加执行轨迹或采样。

对包含打包、线程调度、同步、合并和搬运的完整算子比较输出，并验证重复调用状态。无需计时或性能对比。整数、索引和布尔精确；浮点误差上限完全来自算子输入，不从硬件峰值或优化目标反推。

## 仍需验证

当前 `ops/` 是 `ops-gpu-v3` 的已记录派生语料：500 个算子、2734 个 case，来源与修改记录见 `CORPUS_LOCK.json` 和 `A100_CORPUS_DERIVATION.json`。
开发入口是固定版本的功能模拟器，安装版本及实际指令测试见
`REFERENCE_ENVIRONMENT.json` 和 `TOOLCHAIN_PROBES.json`。环境探针不是编译器交付。
当前派生语料的完整 Triton CPU 执行结果见 `A100_REFERENCE_AUDIT.json`；历史扫描留在来源准备项目中。参考后端错误不能作为题目无效或候选编译器错误的证据。

本项目尚未编写实际编译器，也未执行开发板验证。物理核心编号、线程启用、共享引擎
配对及 TCM/DMA 软件接口仍待确认。BF16 IME 在固定模拟器上存在格式控制
验证缺口；不得用 FP16、普通向量或参考后端通过替代 BF16 矩阵指令的执行证明。
不得自动清理其他进程的资源或照抄旧平台编号。

## Conditional design guidance

- 前提：存在足够多互不重叠的输出块。收益：简化同步并支持多核。成本：需要验证工作覆盖及共享资源访问同步。采用后必须形成 Decision。
- 前提：打包成本能由计算量或权重复用摊薄。收益：利用矩阵扩展。成本：额外存储、打包和尾块处理。验证普通路径与矩阵路径各自的结果及指令执行。
- 前提：已验证本地存储和搬运接口及可见性。收益：复用与重叠。成本：容量、同步、资源占用。不能在这些事实缺失时假定 TCM/DMA 可用。

## 来源索引

以下为准备阶段已阅读的原始资料定位，不是预创建的 workflow Fact 或任务。

- The K3 product description specifies eight A100 AI cores.
  来源：`docs/compiler-agent/target-material/sources/432da714bd719f3506e3fb28b39f1f35fa1a8f54702382d66e010ec92acb30f6/root_overview.md.search.txt:1 [version 3ea42a6af47f2595428e2870122829dc5e8fc856]`。
- The A100 core supports RVV 1.0 with VLEN = 1024 bits.
  来源：`docs/compiler-agent/target-material/sources/ff2340c355516e190769949abbfe57d2121efbe72326b5fc65b166f6cd55d90d/08_cpu.md.search.txt:50 [version 3ea42a6af47f2595428e2870122829dc5e8fc856]`。
- The A100 manual specifies 32 KB instruction and data L1 caches per core, 1 MB L2 per cluster, and 1.5 MB scratchpad per cluster.
  来源：`docs/compiler-agent/target-material/sources/ff2340c355516e190769949abbfe57d2121efbe72326b5fc65b166f6cd55d90d/08_cpu.md.search.txt:50 [version 3ea42a6af47f2595428e2870122829dc5e8fc856]`。
- The advertised 60 TOPS A100 figure is qualified as INT4 sparse; it is not a measured bound for every workload.
  来源：`docs/compiler-agent/target-material/sources/ff2340c355516e190769949abbfe57d2121efbe72326b5fc65b166f6cd55d90d/08_cpu.md.search.txt:50 [version 3ea42a6af47f2595428e2870122829dc5e8fc856]`。
- The public v0.6 matrix instruction specification explicitly lists A100 support for integer, FP16/BF16, sparse, block-scaled and sliding-window sub-extensions; K1 examples are not the A100 support contract.
  来源：`docs/compiler-agent/target-material/sources/bd69e01a6280ae5ab4493ea82b0e819fb34f093da43c264fc3be3c6291a8c6c8/ime_extension.md.search.txt:206 [version 2b3894e983a295ed0278bc625867e0c132e0e259]`。
- Current matrix instruction implementations require LMUL = 1; matrix destination registers must not overlap source registers.
  来源：`docs/compiler-agent/target-material/sources/bd69e01a6280ae5ab4493ea82b0e819fb34f093da43c264fc3be3c6291a8c6c8/ime_extension.md.search.txt:329 [version 2b3894e983a295ed0278bc625867e0c132e0e259]`。
- For MUL_C = 2, the matrix destination register is even-numbered and occupies vd and vd+1. Sliding-window instructions additionally require an even-numbered vs1.
  来源：`docs/compiler-agent/target-material/sources/bd69e01a6280ae5ab4493ea82b0e819fb34f093da43c264fc3be3c6291a8c6c8/ime_extension.md.search.txt:329 [version 2b3894e983a295ed0278bc625867e0c132e0e259]`。
- Sparse and scale-enabled matrix instructions use v0/v1 for specialized mask or scale roles, and MCPM.BF16 selects floating format for the relevant paths.
  来源：`docs/compiler-agent/target-material/sources/bd69e01a6280ae5ab4493ea82b0e819fb34f093da43c264fc3be3c6291a8c6c8/ime_extension.md.search.txt:398 [version 2b3894e983a295ed0278bc625867e0c132e0e259]`。
- A100 dense matrix tile shapes M×K×N are 8×32×8 for INT4, 8×16×8 for INT8, and 8×8×8 for FP16/BF16 inputs with FP32 output.
  来源：`docs/compiler-agent/target-material/sources/bd69e01a6280ae5ab4493ea82b0e819fb34f093da43c264fc3be3c6291a8c6c8/ime_extension.md.search.txt:371 [version 2b3894e983a295ed0278bc625867e0c132e0e259]`。
- A100 structured sparse matrix tile shapes M×K×N are 8×64×8 for INT4 and 8×32×8 for INT8; sparsity is an instruction and data-layout contract, not permission to discard arbitrary values.
  来源：`docs/compiler-agent/target-material/sources/bd69e01a6280ae5ab4493ea82b0e819fb34f093da43c264fc3be3c6291a8c6c8/ime_extension.md.search.txt:371 [version 2b3894e983a295ed0278bc625867e0c132e0e259]`。
- Input packing and result interpretation must follow the instruction-specific tile layout; mathematical transpose notation does not itself require a separate software transpose.
  来源：`docs/compiler-agent/target-material/sources/bd69e01a6280ae5ab4493ea82b0e819fb34f093da43c264fc3be3c6291a8c6c8/ime_extension.md.search.txt:437 [version 2b3894e983a295ed0278bc625867e0c132e0e259]`。
- The official K3 inference guide describes eight AI cores and a spacemit-tcm-smi utility for monitoring resource use; concurrent inference must partition resources to avoid conflicts.
  来源：`docs/compiler-agent/target-material/sources/160a000a6d680a485400bcd5d41461504f1f9ecd16081bce885e94b4f714540b/llama.cpp.md.search.txt:284 [version 2b3894e983a295ed0278bc625867e0c132e0e259]`。
- Official inference examples use AI core IDs 8–15 and explicit affinity configuration. This is a documented software example, not proof of the IDs or interfaces on the eventual board.
  来源：`docs/compiler-agent/target-material/sources/160a000a6d680a485400bcd5d41461504f1f9ecd16081bce885e94b4f714540b/llama.cpp.md.search.txt:319 [version 2b3894e983a295ed0278bc625867e0c132e0e259]`。
- The architecture Preview describes the tensor core and IME 2.0 INT/FP engines as shared by two compute cores. The production pairing and availability must be confirmed on the actual board.
  来源：`docs/compiler-agent/target-material/sources/9564d4ba5ed9a64d71c0c7e5bf0c8f7d74ed717fd0aa71265328f8c1eaea8c91/K3_architecture_preview.pdf.search.txt:746 [version Preview 2026-01-29]`。
- The official compiler guide describes a packed view interface, matrix dot operation, and CPU execution driver; these are reference integration options, not a decision to call an existing compiler as this implementation.
  来源：`docs/compiler-agent/target-material/sources/f97e5fa486885796bd4c24b204159f6c959cfe87015e5516c87d78ed9fc201d7/triton.md.search.txt:1 [version 2b3894e983a295ed0278bc625867e0c132e0e259]`。
