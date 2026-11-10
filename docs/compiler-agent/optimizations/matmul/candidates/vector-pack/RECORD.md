# 候选记录：IME B 操作数打包向量化（vector-pack）

## Goal and outcome

- 请求范围：用户指令的 matmul 优化轮（代理指标判据：guest 动态指令开销、
  spill/reload 流量、冗余访存；不以 QEMU 墙钟为目标，不主张真实硬件
  加速比或 engine gate）。
- 候选：`_pack_b_columns` 的 B 操作数列主序打包从逐元素标量循环改为
  每列一次跨步向量载入（`vlse`）+ 一次单位存储。
- 基线修订：`3ed513e`（工作区含本轮改动之前的 HEAD）。
  候选修订：本轮工作区（matrix.py/vectorize.py/driver.py/factory.py/
  emit.py/test_lower_matrix.py 改动，提交哈希见 ROUND.md 提交记录）。
- 状态：**accepted（保留）**——312/312 matmul 族 PASS、逐 case 动态指令
  -30.6%~-79.1%（IME 路径）、非 IME 路径 0.0% 变化、全量回归见
  ../../regression/full-input/。

## Why this optimization

- 观测（baseline/profile/BOTTLENECKS.json）：IME 路径 fp16 case 的
  pb/pq 打包循环占每调用动态指令 29-80%（k64 79.7%）；每 16 位元素
  ~14 条标量指令。归因：a100c/lower/matrix.py `_pack_b_columns` 的
  标量逐元素拷贝（模块注释记录"the strided column read has no safe
  vector form at the native widths"）。
- 该约束的实际来源是固定 QEMU 的**索引式**缺陷（e64 索引 + 子 32 位
  数据 SEGFAULT，vectorize.py:2579）；跨步形式从未被探针。本轮探针
  （tooling/probe-strided.S）证明 vlse/vsse 全形态在该 QEMU 下正确执行。
- 选择 lowering 层而非新 pass 的依据：打包循环在 TIR 层不存在（LICM
  fired=0）、MIR 无 pass 阶段（架构契约 mir/v1 passes 为空）、emitter
  无法重构循环；成本产生于 matrix.py 自身的打包决策（其声明职责内）。
  备选方案（索引式 gather / 新 MIR pass / 仅优化标量循环体）的否决
  理由见 baseline/profile/OPTIMIZATION_RECOMMENDATION.json。

## Transformation and reuse contract

- 结构匹配：B 打包的源访问是均匀字节步长（N*esz）+ 受护栏计数
  rem ≤ tk ≤ vlmax；目标列连续且已零填充全部 tk lane。
- 语义前提：零填充语义不变（vl=rem 的 vse 只覆盖 rem 个 lane，
  其余保持零——与标量前缀拷贝逐位一致）；rem==0 时 vlse/vse 为无操作
  （探针验证 avl 0）；元素地址 esz 对齐（src0 与步长均为 esz 倍数）。
- 合法/拒绝：region 契约扩展（`_STRIDE_MEM_OPCODES`：vloads8/16 在
  (sew,1) 区域执行；错区域/非 i64 步长/错结果宽度 → IME_REGION/
  IME_SHAPE 拒绝，单测覆盖）。宽度 guard：`in_width ∈ {8,16}`；
  其它（int4 nibble 等）走原标量路径。
- 开关与回退：`A100C_MATRIX_PACK=scalar`（CompileOptions.
  matrix_scalar_pack → LowerOptions → _Composed.pack_vector=False）
  强制标量路径；进入 artifact 身份（"matrix-scalar-pack"）产生独立
  缓存条目。已验证：开关下 pq 循环恢复 12 处、6/6 PASS。
- 实现文件：a100c/lower/matrix.py（表/行/验证/`_pack_b_columns`/
  `_Composed.pack_vector`）、a100c/lower/vectorize.py 与 a100c/driver.py
  （选项+身份）、a100c/factory.py（传递）、a100c/backend/emit.py
  （调度集合一行）、a100c/tests/test_lower_matrix.py（8 项新检查）。
  发射经通用模板路径（`vlse{sew}.v {vd}, 0({rs1}), {rs2}`），emit 无
  专用分支。
- 目标相关部分：vlse/vsse 是 RVV 1.0 标准形式（该目标 VLEN=1024）；
  仿真器证据绑定固定 QEMU（jdsk-qemu-10.0.2）。可移植部分：跨步
  gather 替代逐元素拷贝的结构变换与运行时 vl 区域用法。

## Validation and measurements

- 环境：jdsk-qemu-10.0.2 用户态 qemu-riscv64，-cpu max,vlen=1024,
  elen=64,vext_spec=v1.0；golden 输入 seed=30；判据量=guest 动态指令
  执行次数（per-insn exec 回调，phase-a 校准）。
- 正确性：matmul 族 312/312 PASS（scan/report.json，全部检查 true，
  含 IME 指令族覆盖）；单测 7 套 + 新增 8 项全 PASS；开关对照 6/6
  PASS；完整输入回归（2734 cases）见 ../../regression/full-input/
  （结果回填于 ROUND.md）。
- 触发验证：新 program.S 中 `vlse16.v` 4 处、`.Lpq` 块 0 处
  （开关下 vlse 0 处、pq 12 处）。
- 同口径前后对比（comparison.json，逐 case）：

| case（threads=1） | base | cand | 变化 | reload |
|---|---|---|---|---|
| k64-f16 | 41.74M | 8.71M | **-79.1%** | 2727K→425K |
| plain-128-f16 | 13.28M | 4.11M | **-69.1%** | 2156K→329K |
| atb-f16 | 27.09M | 8.74M | -67.7% | 4783K→853K |
| tril-f16 | 14.24M | 5.06M | -64.5% | 1662K→349K |
| plain-ragged-f16 | 3.64M | 1.34M | -63.1% | 230K→71K |
| abt-f16 | 11.61M | 4.73M | -59.3% | 1400K→297K |
| rms-f16 | 1.92M | 0.78M | -59.6% | 140K→54K |
| batched-tail-f16 | 2.02M | 0.87M | -56.8% | 130K→49K |
| batched-f16 | 0.28M | 0.13M | -51.9% | 17K→7K |
| triton2-f16 | 0.32M | 0.18M | -44.3% | 31K→9K |
| linact-f16 | 0.47M | 0.33M | -30.6% | 27K→6K |
| plain-128-f16 (t4) | 13.44M | 4.26M | -68.3% | — |
| fusedgn-f32 / grouped-f16 / plain-128-bf16 / plain-128-f32 | — | — | **0.0%** | 不变 |

- 机制确认（plain-128-f16 的块级归属，blocks.json）：pack-q
  8,716,288 → **0**；k-loop 1,453,056 → 1,453,056（精确不变——变换
  隔离性）；pack-b 1,101,824 → 1,298,432（+18%：每列 gather 序列的
  固定开销，换来内层 8.7M 消除）。**主要代价即此**：外层列循环的
  每列标量准备（guard/rem/narrow32/vsetvli/vlse/vse ~12 条/列）成为
  残留瓶颈（候选后占 31%）。
- 多 worker：t4 总量同幅下降；t2/t8 存在 barrier 自旋非确定性
  （逐 PC 稳态增量不可整除，如实标记 PROBLEMS；原始 r1/r2 与总量
  保留在 metrics.json）——自旋类开销按用户要求单独分析，不计入
  本表结论。
- 未测量项：真实硬件时间（本轮判据明确排除）；向量访存字节数为
  模型值（vlmax 口径）。
- 噪声规则：计数为确定性量（校准双跑一致）；单 worker 前后为
  同配置同种子同身份匹配对比。

## Good practices and bad practices

- **好（观察）**：发射器默认的 `[opN]` 溯源注释 + renumber 序 MIR dump
  使零改动建成 pc 级联结（含字节同一性校验）——归因成本极低。
- **好（观察）**：矩阵模块的自带 repertoire 行注册（"adding an
  operation is a table edit"）让新指令形式不需要动选择器。
- **好（观察）**：`--repeats` 差分（r1 vs r2）干净分离 init 与稳态。
- **坏（观察，已修）**：模块注释把"无安全向量形式"记成结论，实际
  只探针过索引式——**负面结论必须与探针范围绑定**，否则会像本例
  一样把 60-80% 的可优化成本锁死四年（该注释从垂直切片时代留存）。
- **坏（观察）**：逐元素标量循环里用 `mul` 从循环变量重建地址而非
  递增指针（即便保留标量路径也本可减半）——回退路径的改进空间
  留作后续。
- 移植配方（摘要）：需要 (1) 跨步访存指令或等价 gather；(2) 运行时
  vl 的区域机制（vsetvli AVL 取自 vreg）；(3) 打包源的均匀步长与
  受护栏计数这两个结构性质；(4) 仿真器/硬件的跨步形式执行证据。
  详见 retrospective.md。
