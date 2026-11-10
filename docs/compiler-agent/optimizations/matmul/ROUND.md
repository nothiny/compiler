# Matmul 优化轮（人类直接指导 / 代理指标判据）

- 发起： 用户指令（2026-11-10），直接人类指导的优化任务。引擎状态保持不动
  （本轮开始时 T044 仍在飞行；本轮不派发引擎任务、不写引擎状态、不主张任何
  engine gate / G9 通过；correctness_only 验收保持原样）。因本环境中非引擎
  子代理派发不可用（Agent 派发仅限引擎 dispatch），全部工作在指导会话内
  直接完成——$optimization skill 明确支持该路线。
- 判据： QEMU 模拟执行中可验证的代理指标——guest 动态指令开销、编译器引入的
  动态 spill/reload 次数与流量、冗余访存。不以 QEMU e2e 墙钟为主目标，
  不换算真实硬件加速比；QEMU 时间仅辅助记录。
- 基线锚点： commit `3ed513e`（tracked 工作区干净）。回退边界 = 该提交 +
  本轮新增提交（见"提交记录"）；同修订内另有 `A100C_MATRIX_PACK=scalar`
  开关（进入 artifact 身份）作为行为级回退。
- 范围： OPERATOR_INVENTORY.md 中 family=matmul 的 57 算子 / 312 case。
  `triu_batch_kernel`/`gram_jacobi_sym_kernel` 无 `dot.matmul`，排除。

## 执行摘要

1. **正确性前提**： matmul 族 312/312 PASS @ `3ed513e`（baseline/scan/）。
2. **观测链**（tooling/）： QEMU 全量动态指令插件（已知循环数程序精确
   校准）+ pc 级联结器（字节同一性校验）+ 稳态差分采集 + 块级归属。
3. **基线画像**（baseline/metrics/，21 组）： 标量类占 66-85%；B2 类
   （循环内物化）普遍。
4. **瓶颈**（baseline/profile/）： IME B 操作数列主序标量打包占动态指令
   29-80%（`_pack_b_columns`）。
5. **门控探针**（tooling/PROBES.md）： vlse/vsse 全形态在固定 QEMU 下
   PASS；新约束：vmv.v.i/vmv.v.x @ e64/m2 SIGILL。
6. **候选**（candidates/vector-pack/）： 每列 1×`vlse`+1×`vse` 替代逐元素
   循环；宽度 guard + 标量回退 + 开关。**接受（保留）**。
7. **复测**（candidates/vector-pack/comparison.json）： IME 路径逐 case
   动态指令 **-30.6% ~ -79.1%**（k64 -79.1%、plain-128 -69.1%、多 worker
   t4 -68.3%）；非 IME 路径（fp32/bf16/grouped）**生成代码逐行一致、
   指标 0.0% 变化**；reload 流量 -67 ~ -85%；pack-q 块 8.72M→0，
   k-loop 绝对值精确不变（隔离性）。
8. **完整输入回归**（regression/full-input/）： 结果回填于下节。

## 完整输入回归（2734 cases，threads=1 + 代表 resource 证据）

- 结果： **2726 PASS / 2 MISMATCH / 6 TIMEOUT**（2734 全枚举、0 missing；
  report_complete ✓、resource_instruction_families_covered ✓——代表 case
  的 IME 见证在多 worker 下仍满足）。report/journal 见本目录。
- 8 个 non-PASS 的归因（**三重证据，全部为 HEAD=3ed513e 存量问题，与本轮
  改动无关**）：
  1. `chunk_gdn2_fwd_kernel_intra_token_parallel` fp32 ×2 MISMATCH——其 dot
     为 fp32 → vector-fp32 路径，本轮改动不可达，且该路径生成代码已证
     逐行一致；引擎 T045 的既定范围（fp16/bf16 PASS——2970701 部分修复
     的印证）。**与"全部已修好"声明的差异如实记录**。
  2. `complex_svd_pick_orthonormal_v [17]` ×3 与 `deconv3d_fwd [1,4,8,8,8]`
     ×3 编译预算超时（干净重试仍 ~185s 超时；非争用）。
  - 证据 b： `A100C_MATRIX_PACK=scalar`（同修订、基线等价打包路径）下
    6 个超时全部复现（attribution-scalar-pack.json）。
  - 证据 c： 真·基线 worktree（3ed513e，独立缓存冷编译）下 8 个 non-PASS
    **全部复现**（attribution-baseline-3ed513e.json）。
  - 判读： fix wave（T042-T044/2970701/0f84bdc/3ed513e）之后从未跑过全量
    scan（引擎记录的失败清单来自修复前）；这 8 个是修复波引入/遗留、
    尚未被引擎重新归档的存量问题（6 个超时疑与 T044 的 conv 族代码
    变重有关，留给引擎的后续修复轮验证）。
- `compile_count_equals_artifact_identities=false` 为跨 run 缓存复用的
  正常表现（1844 本进程编译 + 264 个本修订已缓存 identity = 2108 artifact
  identities；cache_hits 890 = 进程内共享 identity 的 case）。

## 保留/回退决策

**保留（KEEP）**。依据：matmul 族 312/312 PASS；完整输入回归除 8 个已
归因为存量的 non-PASS 外 2726 全 PASS；同口径指标 IME 路径 -30.6%~-79.1%、
非 IME 路径零变化；回退路径双保险（revert 提交或 `A100C_MATRIX_PACK=scalar`
行为级开关，后者已验证 6/6 PASS）。

## 提交记录

- `f69be1d` [opt] IME B-operand pack: strided vector load replaces the
  scalar copy loops（292 文件：编译器 6 文件 + 测试 + tools/profiling
  观测链 + 本证据目录；不含可复现的二进制产物）。
  回退 = `git revert f69be1d`，或设置 `A100C_MATRIX_PACK=scalar`（行为级，
  已验证 6/6 PASS）。

## 证据布局

- `baseline/`： operators 清单、scan（312/312）、profile 三工件、metrics
  （16 case t1 + 3 case 1/2/4/8，含 blocks.json 块级归属）。
- `tooling/`： 观测链全部代码使用说明（TOOLING.md）、口径校准
  （phase-a/）、探针（probe-strided.S / probe-e64m2.S / PROBES.md）、
  sweep.sh。
- `candidates/vector-pack/`： scan（312/312）、metrics、comparison.json、
  RECORD.md（按 optimization-record 指南）。
- `regression/full-input/`： 全量回归。
- `retrospective.md`： 跨轮综合（compiler-design-retrospective）。
- 索引： `../optimizations/INDEX.md` + `docs/compiler-agent/OPTIMIZATION.md`。

## 观测口径

guest 动态指令（QEMU 10 插件 per-insn exec 回调；jdsk-qemu-10.0.2 用户态，
-cpu max,vlen=1024,elen=64,vext_spec=v1.0）；已知循环数小程序精确校准；
spill/reload 由编译器侧 origin 清单 × 动态 PC 计数联结；静态汇编条数、TB
翻译数、宿主 perf 指令数不作替代；多 worker 自旋非确定性单独标记分析；
向量访存字节数为模型值（vlmax 口径）并标注。
