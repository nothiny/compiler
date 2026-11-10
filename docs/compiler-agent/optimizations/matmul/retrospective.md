# 设计复盘：matmul 优化轮 + 既有 emission-peephole 轮

- 来源与覆盖： 本项目仅有的两轮优化记录——(A) emission peephole（提交
  `0f84bdc`，无独立记录文件，以提交说明为准，已在 INDEX 标注）；(B) 本轮
  matmul vector-pack（提交 `f69be1d`，完整记录
  candidates/vector-pack/RECORD.md）。证据根：docs/compiler-agent/
  optimizations/matmul/。复盘不修改代码/契约/引擎状态，不开新轮。
- 证据限制： 两轮均在单机固定 QEMU（jdsk-qemu-10.0.2）上测量；判据为
  guest 动态指令计数（确定性量，已校准），多 worker 自旋计数非确定（已
  标注）；向量访存字节数为模型值；(A) 轮只有静态条数证据（其提交说明
  自称 -10% 静态指令），无动态画像——(B) 轮的基线画像补上了这一缺口。
  本轮未触及 vector-fp32 路径（fp32/bf16 dot）的 staging 成本
  （fusedgn-f32 画像 other 63.5%），未探索。

## 经验表

| # | 实践 | 性质与机制 | 证据 | 边界 | 置信度 | 后续动作 | 对 pass 的影响 |
|---|---|---|---|---|---|---|---|
| L1 | **好（架构）**：发射器默认逐行 `[opN]` 溯源 + renumber 序 MIR dump + artifact 缓存自带全阶段 dump | 任何生成指令可零改动地归因到 MIR op/源位置/循环块，归因成本≈0，画像驱动优化可行 | 本轮联结器（insn_manifest.py）零编译器改动建成 pc 级归因（字节同一性校验） | 溯源按"序列首 op"有相邻噪声（定量以插件类别为准） | 已观察（本轮） | 后继编译器保留：每条发射指令携带 IR 溯源应是默认契约 | 一切画像驱动 pass 的前提 |
| L2 | **好（架构）**：模块自带 repertoire 行即数据（"adding an operation is a table edit"） | 新指令形式不动选择器/发射器主干；本轮 vlse 行经通用模板路径发射 | matrix.py:ime_repertoire_rows + test_lower_matrix 8 项新检查全过 | 双标量操作数模板角色（rs1/rs2）需通用映射支持（已有） | 已观察（本轮） | 保留；后继沿用"表驱动指令形式" | 表驱动使新形式 pass（此处为 lowering 变换）接入成本低 |
| L3 | **好（架构）**：进入 artifact 身份的 lowering 开关（witness 旗标模式的推广） | 同修订下可编译出可对照的两套行为且缓存键安全隔离；回退有行为级与提交级双保险 | A100C_MATRIX_PACK=scalar：pq 循环恢复 12 处、6/6 PASS；身份行 `matrix-scalar-pack` | 开关必须进缓存身份否则同键异码（本轮已正确接线 driver→factory→LowerOptions） | 已观察（本轮） | 保留；后继把"每个语义开关进 artifact 身份"作为不变量 | on/off 对照是 pass 验证的标准件 |
| L4 | **坏（架构/过程）**：**未绑定探针范围的否定结论成为优化锁** | matrix.py 注释"the strided column read has no safe vector form at the native widths"实际只对应索引式缺陷（e64 索引+窄数据 SEGFAULT），却把跨步形式一并锁死——该打包占动态指令 29-80% | 本轮探针证明 vlse/vsse 全形态 PASS（probe-strided.S）；归因见 BOTTLENECKS.json B1 | 否定结论当时可能确实只探过索引式；问题是**未记录范围** | 已观察（本轮解锁并获益 -30.6%~-79.1%） | 后继：目标能力否定断言必须引用其探针范围与版本；画像归因命中"被声称不可能"的路径时应先复检探针覆盖 | 解锁了本轮整个变换 |
| L5 | **坏（架构）**：**TIR 优化在 lowering 之前，而重物化在 lowering 之后产生** | matmul 上 TIR LICM/强度削减 0 次触发：常量/地址/区域切换/spill 拆分全部由 lowering 与分配器合成；emitter peephole 又只能删静态重复（(A) 轮已证其对动态循环体无效：本轮基线 65% 动态指令集中在一条无静态冗余的标量循环里） | stage.passes.txt（licm fired=0）；(A) 轮 vs (B) 轮基线画像 | (B) 轮选择在产生者（matrix.py 打包决策）处修复而非新增 MIR pass——架构契约 mir/v1 的 pass 列表为空，加 pass 属语义契约变更 | 已观察 | 后继设计决策：要么 lowering 自带循环感知（本轮路线，逐模式修），要么设立 post-lowering MIR 循环 pass 阶段（契约变更，现有测量证据已可支撑该提案：残留 k-loop 35% + chunk 17.5% + B2 类） | MIR 循环不变量外提 + IV/地址递归是后继最高价值 pass（需效应/区域/spill 合法性分析） |
| L6 | **条件（目标）**：仿真器缺陷类必须进入目标模型 | 已知：索引式窄数据 SEGFAULT（记录在案）；本轮新增：vmv.v.i 与 vmv.v.x @ e64/m2 SIGILL（probe-e64m2.S，avl 16/32 皆然）；跨步形式此前从未探针 | PROBES.md 双探针 | "QEMU 实现 RVV 1.0"≠可用；缺陷类与指令形态相关 | 已观察（本轮） | 后继：按访存/寄存器形态类建立探针矩阵并作为 lowering 可查询的表 | 任何依赖新指令形式的 pass 先过探针门 |
| L7 | **坏（数据结构，次要）**：标量回退路径仍用乘法从 IV 重建地址 | 每元素 ~14 条可降为 ~8-9（递增指针 + 常量外提） | program.S pq 循环体 | 回退路径现已非热点（默认走向量）；仅在未来需要时修 | 已观察 | 低优先级保留 | — |
| L8 | **好（过程）**：`--repeats` 差分（1 vs 1+R）分离 init/稳态；确定性计数 + 双跑校准 | 代理指标轮的可复现判据基座 | collect_metrics + phase-a 校准 | 多 worker 自旋非确定——单独标记，不平均、不冒充 | 已观察 | 保留；后继把"计数确定性校准"作为指标基建第一步 | — |

## 补充经验（L9–L15，本轮会话内观察，供重写指导）

| # | 实践 | 性质与机制 | 证据 | 边界 | 置信度 | 后续动作 |
|---|---|---|---|---|---|---|
| L9 | **好（架构）**：单一发射咽喉点 + 拒绝即定位 | emit(text, op, note) 一处收口使每行可溯源、peephole 可单点后置；PipelineError 携带 (loc, construct)，COMPILE_REFUSED/TIMEOUT/MISMATCH 皆为记录态——"坏 case 是数据" | emit.py:410；本轮 pc 归因零改动建成 | — | 已观察 | 保留 |
| L10 | **好（架构）**：见证测试一等公民 | witness 降级构建（去掩码/去屏障/去原子重定向）必须使对应检查**失败**——性质被证明而非被声称 | witness 旗标 + tools/check_* --witness 退出非零 | — | 已观察 | 保留 |
| L11 | **坏（架构）**：双 lowering 构建器栈 | matrix.py 存在两套平行构建器（_Ctx/_DotLowering 与 _Composed/_MatrixIface），_vid/_narrow32/_guard/region 各复制两份，打包也有两份实现——本轮只修了 composed 路径 | matrix.py:642/689 与 1722/1758 的重复助手；_emit_pack_loops vs _pack_b_columns | 语料当前只走 composed 路径（_sc_ 块 0%） | 已观察 | 重写收敛为**单一 lowering 接口**，消除双实现漂移风险 |
| L12 | **坏（策略）**：无成本感知的重物化/reload | "纯标量树每次使用重物化"（vectorize.py:436/566）与分配器"每用前 reload"对冷代码省寄存器、对热循环是灾难 | 旗舰 case sconst 2.8M（21%）+ sreload 2.16M（16%）/调用 | 该策略动机正确（寄存器压力），缺的是循环深度/热度感知 | 已观察 | 重写采用代价感知决策（至少按循环深度分层），两侧都要实测 |
| L13 | **坏（codegen）**：全树地址重算 | 地址 = base + i×stride 每迭代用乘法重建，而块参数机制本可携带递归（_emit_pack_loops 就在用） | pq 循环体 12-14 条/元素 vs 递归可到 ~8 | 已被本轮向量化取代为主路径；残留在回退路径 | 已观察 | 发射循环时同步做 IV 强度削减（或并入 L5 的 MIR pass） |
| L14 | **好（基建）**：缓存键全依赖 + dump 零风险 | 键 = 特化身份 + 代码文件修订摘要 + 选项身份 + 参数布局；dump 默认开且不入 ELF 身份 | 本轮前后对照与 scalar 开关对照全程身份安全，无脏缓存复用 | — | 已观察 | 保留为不变量：**每个语义开关必须进 artifact 身份** |
| L15 | **好（运行时）**：自包含原生运行时协议 | --bundle/--threads/--repeats + 快照恢复 + 末行 JSON（含 repeats_all_equal 自校验） | --repeats 差分干净分离 init/稳态；每次执行自带正确性侧信号 | — | 已观察 | 保留 |
| L16 | **坏（伸缩性）**：编译时间无预算监控 | 修复波后 6 个语料 case 编译 >185s 超预算（deconv3d/complex_svd 类），冷编译长尾 12s+，无编译时间回归跟踪 | regression/full-input 归因运行 | 超因（展开膨胀？）是假设 | 部分观察 | 重写加入编译时间回归门 + 代码生成体积预算 |

## 重写检查清单（按上表浓缩）

1. **观测**：每条发射指令携带 IR 溯源（L1/L9）；计数口径先校准再用（L8）。
2. **分层**：优化阶段必须覆盖"lowering 之后产生"的成本——要么 lowering 自带循环感知，要么设立 MIR 循环 pass 阶段（L5，本轮实测残差 k-loop 35%/chunk 17.5%/B2 类支撑该提案）。
3. **目标**：否定断言绑定探针范围（L4）；按指令形态类建探针矩阵并供 lowering 查询（L6）。
4. **策略**：重物化/reload 带代价模型（L12）；地址用递归不用乘法（L13）。
5. **形式**：指令形式表驱动（L2）；开关进身份（L3/L14）；单一构建器栈（L11）。
6. **验证**：见证测试（L10）；自校验运行时（L15）；编译时间回归（L16）。

## 后继设计建议（按优先级）

1. **残留瓶颈处置**（本轮实测残差：flagship 4.11M/调用中 pack-b 外层列循环
   31%、k-loop 35%、chunk 17.5%）：pack-b 每列 ~12 条标量准备（guard/rem/
   narrow32/vsetvli/vlse/vse）可向"批量列打包"演进（跨步形态覆盖 2D 布局
   或段式访存），需独立合法性检查；k-loop/chunk 的循环不变量与 IV 递归则
   指向 L5 的 post-lowering MIR 循环 pass 提案。
2. **vector-fp32 路径的 staging 成本**（fp32/bf16 dot；fusedgn-f32 画像
   other 63.5%）未被本轮覆盖——下一个画像驱动的候选。
3. **探针范围纪律**（L4/L6）：把"否定断言绑定探针范围"写入目标描述的
   维护规则。
4. **pass 复用清单**：本项目无可复用 pass（TIR pass 对该成本类不可见；
   (A) 轮是 emitter 局部变换）。可移植资产是**变换配方**而非 pass：
   跨步 gather 替代逐元素拷贝，前提 = 均匀字节步长 + 受护栏计数 +
   预零填充连续 staging + 目标探针证据（见 RECORD.md 移植节）。

## 与 (A) 轮的关系

(A) 的 vsetvli/li 去重在 (B) 的基线里仍是默认启用且有效（OPT-VLI 依赖
AVL 常量值比较——因为 vectorize 为每个 vsetvli 造全新 sconst vreg，寄存器
号比较永不匹配；L1 的溯源机制正是发现这一点的工具）。(B) 未撤销 (A)；
两轮互补：(A) 删静态重复，(B) 消动态循环体。(A) 尝试失败的跨块 vsetvli
传播与载入前移调度（均禁用留在代码中）提示 emitter 层做控制流敏感优化
的边际收益已尽——支持 L5 的分层结论。
