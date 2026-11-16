# 人类指导的编译器优化、复盘、重设计与 pass 移植

本指南提供可复制的提示词，串起：正确的 V1 → 多轮优化及实践记录 →
跨轮次复盘 → 设计并实现正确的 V2 → 将 V1 的 pass 移植到 V2。

## 使用前说明

- 在生成编译器项目中运行 agent；工作流仓库只存放 skill，不存放生成编译器。
- 提示词中的工作流路径是 `/path/to/compiler-agent-workflow`。
  如果 checkout 在别处，复制前替换该前缀。
- 将 `【……】` 替换为实际选择或绝对路径。记录路径应指向相应项目的
  `docs/compiler-agent/`，跨项目引用时保留项目、版本和证据来源。
- V1、V2 是示例版本名称。循环不变量外提、访存优化和向量化只是可能的方向，
  不能当作已经观察到的瓶颈、收益或架构缺陷。
- 每个代码块是一条可单独发送的提示词。按需选择阶段，每阶段由人类发起；
  不需要把完整流程一次性交给 agent，也不强制固定优化轮数。
- skill 支持直接的人类指导会话，不要求创建 manager 任务或改变状态机。
  已在引擎管理下运行时仍保留其契约，不能把手工报告当作 gate 通过，
  也不能靠提示词让未满足的验收条件自动通过。

## 流程导航

| 阶段 | 工作项目 | 使用的 skill | 主要交付 |
|---|---|---|---|
| [1. 首轮诊断](#step-1) | V1 | optimization、profile-to-compiler-pass | 基线、profile、候选建议 |
| [2. 实施并记录](#step-2) | V1 | 同上及记录指南 | pass、执行比较、测量、实践记录 |
| [3. 继续多轮](#step-3) | V1 | 同上 | 相互链接的多轮记录 |
| [4. 总结经验](#step-4) | V1 | compiler-design-retrospective | lesson id、设计建议、复用清单 |
| [5. 设计 V2](#step-5) | V2 | compiler-planning | 架构、经验映射、实施任务 |
| [6. 实现正确 V2](#step-6) | V2 | plan-review、coding、testing、final-validation | 经审查的设计、完整正确性证据 |
| [7. 评估旧 pass](#step-7) | V2 | compiler-pass-porting | 适用性与接口映射 |
| [8. 移植并验证](#step-8) | V2 | compiler-pass-porting、optimization | 移植结果、当前测量、迁移经验 |
| [9. 可选的再次复盘](#step-9) | V2 | compiler-design-retrospective | 经 V2 验证或修正的设计经验 |

<a id="step-1"></a>
## 1. 从正确的 V1 开始，先诊断

在 V1 项目发送。诊断结束后，你选择值得实施的候选。

```text
V1 已完成正确性开发，现在开展独立性能优化。

请读取并使用：
/path/to/compiler-agent-workflow/skills/optimization/SKILL.md
/path/to/compiler-agent-workflow/skills/profile-to-compiler-pass/SKILL.md

本次只做诊断和建议，不修改编译器代码：
1. 检查已有完整输入执行与比较报告是否对应当前版本；
   若证据缺失或过期，先说明缺口，不宣称当前正确，也不进入优化实施。
2. 检查实际工具与执行环境，建立可复现的性能基线。
3. 根据目标和算子库选择代表性工作负载，对实际生成程序做 profiling，
   把热点关联到生成代码、IR 和编译决策，区分观测与原因推断。
4. 优先考虑已有 pass 的配置，其次是通用新 pass，
   最后考虑 lowering、代码生成或 runtime 细节；例外需说明证据。
5. 给出候选优化、合法性条件、预期机制、风险和推荐顺序。

保存原始报告、命令、版本与建议到当前项目的 docs/compiler-agent/ 下。
不要修改 reference、比较策略、目标输入或引擎策略。
返回诊断及证据路径，然后停止，等我选择实施方向。
```

<a id="step-2"></a>
## 2. 选择一个候选，实施、验证并记录实践

用上一阶段的实际报告和候选替换占位符。候选可以是已有 pass 配置，
也可以是通用新 pass。若候选涉及语义契约变化，保留项目要求的审查边界。

```text
请读取并使用：
/path/to/compiler-agent-workflow/skills/optimization/SKILL.md
/path/to/compiler-agent-workflow/skills/profile-to-compiler-pass/SKILL.md

根据诊断报告：【V1 诊断报告的绝对路径】
实施候选：【候选 id 和优化名称】。
只完成这个候选及必要的集成，不扩展为其他优化或架构重设计。

先检查已有 pass 是否能覆盖；按 IR 结构实现通用机制，
明确合法性、分析依赖和失效规则、顺序与交互，保留开关或等效比较方式。
若涉及已审查语义契约变化，先走项目的变更和审查流程。
完成实际变换的 IR 证据、相关合法与拒绝条件检查、完整输入执行比较，
以及 profiler 外可比较、可复现的前后性能测量。
保留要求的多核和适用专用指令路径，不修改原始 reference、case 或容差。
没有稳定收益时修复或回退，保留失败证据。

按以下指南写优化记录并更新索引：
/path/to/compiler-agent-workflow/skills/optimization/references/optimization-record.md

记录为什么做、原始证据、变换机制、正确性和性能结果，
以及本次暴露的架构与具体数据结构的 good practice / bad practice。
每项判断引用代码或实验依据，说明适用条件和取舍，区分事实与假设；
没有支持的发现就明确说没有，不凑好坏实践。
留下下一代编译器可复用的算法、分析接口、语义前提、测试和迁移条件。

返回代码、报告、优化记录和索引路径，完成后停止，不自动开始下一轮。
```

### 实践记录的具体程度

以下仅为表达形式示例，不能直接作为项目结论：

| 可能的发现 | 应提供的证据 | 给下一代的建议 |
|---|---|---|
| 显式副作用接口有利于安全移动表达式 | pass 使用位置、合法/拒绝案例、IR | 保留统一查询接口及其语义 |
| 分析失效处理分散导致遗漏 | 实际修改点、失效错误或重复维护记录 | 评估统一失效管理及其代价 |
| lowering 过早丢失布局信息 | 信息丢失前后 IR、受阻的匹配 | 在相关 pass 前保留所需信息 |

“IR 很好”“数据结构不灵活”不足以指导重设计。实现方便与运行更快也应分别举证。

<a id="step-3"></a>
## 3. 继续第二轮、第三轮或更多轮

每轮先诊断，再由你选择候选，随后重复第 2 步。上一轮结论并不保证下一轮适用。

```text
在 V1 开始下一轮独立优化。请读取并使用：
/path/to/compiler-agent-workflow/skills/optimization/SKILL.md
/path/to/compiler-agent-workflow/skills/profile-to-compiler-pass/SKILL.md

已有优化索引：【V1 优化索引的绝对路径】。
先阅读相关记录和当前正确性、性能证据，再选择下一个值得解决的问题。
已有 profile 足够且仍适用时复用，不足或瓶颈改变时补充针对性 profiling。
先给建议，不修改编译器代码；说明候选与已有 pass 的顺序和交互。
不要为了增加轮数重复做实验，也不要把历史测量描述为当前测量。
保存本轮诊断并返回候选和证据路径，等我选择后再实施。
```

选定候选后，用第 2 步提示词指定本轮报告和候选，并加上：

```text
在新记录中链接相关历史记录，保留失败、回退和未完成的尝试。
说明新证据是否支持、限制或推翻之前的架构及数据结构判断。
不要覆盖旧结果，更新索引后停止。
```

<a id="step-4"></a>
## 4. 汇总多轮 good practice / bad practice

当你认为经验足够时，在 V1 发起一次复盘；没有固定轮数门槛。

```text
请读取并使用：
/path/to/compiler-agent-workflow/skills/compiler-design-retrospective/SKILL.md

分析优化索引：【V1 优化索引的绝对路径】
及其相关记录、代码、IR 和执行证据。
本次只做复盘，不改编译器代码、架构契约、引擎状态或验收范围，
也不自动启动新实验。

请综合架构和数据结构的 good practice / bad practice：
1. 给出记录覆盖范围，纳入失败、回退、未完成尝试和反例。
2. 区分重复问题、单次局部问题、推断和未经验证的假设；
   同一实验派生的多份报告不能算多份独立证据。
3. 每条经验分配稳定 lesson id，链接记录、版本、代码与证据。
4. 给出下一代编译器应保留、改变或调查的设计，以及适用条件和取舍。
5. 列出值得移植的 pass，其语义、分析和顺序依赖，以及缺失能力。

按 skill 指引保存到当前项目 docs/compiler-agent/，更新索引。
返回复盘路径、优先建议和证据限制，然后停止，不自动重设计。
```

<a id="step-5"></a>
## 5. 在独立项目中设计 V2

先准备独立的 V2 项目和目标描述、算子库。让 agent 可以读取 V1 历史；
历史记录是参考知识，不增加第三个必需输入。在 V2 项目发送：

```text
这是独立的 V2 编译器项目。请读取并使用：
/path/to/compiler-agent-workflow/skills/compiler-planning/SKILL.md

当前项目的两个输入：
目标描述：【V2 目标描述的绝对路径】
算子库：【V2 算子库的绝对路径】
参考 V1 复盘：【V1 复盘的绝对路径】，以及其中引用的优化记录。
V1 仅作为只读来源。

本次设计 V2 架构和实施任务，暂不编写编译器代码：
1. 按当前目标和完整算子语义决定 IR、数据结构、分析接口、
   pass manager、lowering、代码生成和 runtime 边界。
2. 对重要决定注明采用哪条 lesson、在 V2 的适用性、取舍及待验证假设。
3. 为选定旧 pass 列出所需能力、接口和集成位置；
   不照搬旧 IR 名称，也不为每条历史建议增加框架。
4. 实施目标是交付正确编译器，保留要求的基础 pass、多核和适用专用指令。
   性能调优与旧 pass 的性能移植另行发起，不自动追加优化阶段。

不修改引擎策略或自动改变验收范围；如现有契约与请求冲突，明确指出。
将设计、lesson 映射和实施任务保存在 V2 的 docs/compiler-agent/。
提交设计及待决事项供我评审，然后停止。
```

<a id="step-6"></a>
## 6. 审查设计，实现并验证正确的 V2

人类对齐方向不能替代项目要求的独立架构审查。先发送：

```text
我同意 V2 的设计方向：【设计文件的绝对路径】。
请读取并使用：
/path/to/compiler-agent-workflow/skills/plan-review/SKILL.md

按项目规定完成独立架构审查，检查完整输入覆盖、接口、实施依赖和验证路径。
本次只审查，不编写编译器代码；返回实际 verdict、依据和需修正事项。
不要把我的方向确认当作独立审查通过，也不要自动开始实施。
```

处理审查意见、完成必要复审后，再发送：

```text
V2 设计和审查结果：
【设计文件的绝对路径】
【当前有效的审查报告绝对路径】

请按已审查设计实施，读取并使用：
/path/to/compiler-agent-workflow/skills/coding/SKILL.md
/path/to/compiler-agent-workflow/skills/testing/SKILL.md
/path/to/compiler-agent-workflow/skills/final-validation/SKILL.md

完成规划内的正确性实现和全部输入执行比较，保留基础 pass、要求的
多核及适用专用指令路径。若发现设计缺陷，走项目的变更与复审流程。
不自动进入性能调优，不移植尚未纳入实施授权的性能 pass。
不改变原始 case、reference 或比较策略。

将实现进展、命令和证据按项目要求保存在 docs/compiler-agent/。
交付当前编译器版本、构建/执行命令、完整 case manifest 和比较报告。
构建成功不算执行通过；缺失运行条件时明确保留待验证状态。
完成正确性交付后停止。
```

<a id="step-7"></a>
## 7. 在 V2 评估一个旧 pass

V2 当前完整正确性证据齐备后，从复盘清单中选择一个 pass。在 V2 发送：

```text
请读取并使用：
/path/to/compiler-agent-workflow/skills/compiler-pass-porting/SKILL.md

评估将以下 V1 pass 移植到当前 V2：
源 pass 代码：【V1 pass 的绝对路径】
优化记录：【V1 优化记录的绝对路径】
相关复盘：【V1 复盘的绝对路径】
V2 完整正确性报告：【V2 报告的绝对路径】

本次只评估，不修改编译器代码。保持 V1 只读。
先检查 V2 是否已有等效 pass 或可配置机制。
给出源到目标的结构匹配、语义前提、分析接口、修改/失效规则、
pipeline 顺序、目标约束、测试和 fallback 的对应关系。
明确哪些算法可复用、哪些接口需适配、哪些能力缺失或不适用。

判断是否能省略完整 profiling，以及仍需哪些最小证据。
历史收益不能作为 V2 的性能结论；不要将旧 profile 改标为 V2 数据。
保存适用性评估至 V2 的 docs/compiler-agent/，返回建议后停止。
```

<a id="step-8"></a>
## 8. 实施移植，验证收益并修正经验

评估适合后发送。若需要架构语义变化，应先完成相关设计处理及审查。

```text
根据适用性评估：【V2 评估报告的绝对路径】
实施其中的 pass：【pass 名称或 id】，只完成这一项移植。

请读取并使用：
/path/to/compiler-agent-workflow/skills/compiler-pass-porting/SKILL.md
/path/to/compiler-agent-workflow/skills/optimization/SKILL.md

保持 V1 只读，在 V2 保存回退边界，保留无关改动。
复用适用算法和测试，补充接口映射、合法性和拒绝条件的检查。
接入 V2 的 pass 基础设施，处理分析失效、顺序、guard 和 fallback，
保留开关或等效对照，以及变换实际触发的前后 IR 证据。

已有证据足够时不重复完整 profiling；缺失或异常时只补必要的
针对性观察，并记录省略或补充的原因。需要新 profile 时使用：
/path/to/compiler-agent-workflow/skills/profile-to-compiler-pass/SKILL.md

执行当前版本的完整输入比较和可复现的前后性能测量，
在必要时比较 pass-off/on，区分集成改动和 pass 本身的效果。
不改 case、reference 或容差，保留要求的多核与适用专用指令路径。
分别报告是否成功移植、是否保持正确、是否存在可复现收益；
没有收益时按 optimization 规则修复或回退并保留记录。

按优化记录指南在 V2 新建记录并更新索引：
/path/to/compiler-agent-workflow/skills/optimization/references/optimization-record.md

链接 V1 记录和 lesson id，记录哪些 V2 设计帮助了移植，
哪些仍造成障碍，哪些旧经验被支持、限制或推翻，以及新的迁移条件。
不要修改 V1 历史。返回结果和证据路径，然后停止。
```

后续 pass 可按需重复第 7、8 步，不必默认全量移植，也不能用一个 pass 的
结果替其他 pass 证明合法性或性能收益。

<a id="step-9"></a>
## 9. 可选：对照 V1 与 V2 再次复盘

```text
请读取并使用：
/path/to/compiler-agent-workflow/skills/compiler-design-retrospective/SKILL.md

对照以下历史，总结 V2 是否解决了 V1 的设计问题：
V1 复盘：【绝对路径】
V1 优化索引：【绝对路径】
V2 优化/移植索引：【绝对路径】

重点核验原 lesson 的设计建议是否真正落地、移植障碍是否减少，
以及哪些新问题或反例出现。实现便利、正确性与运行性能分别举证，
不要把硬件、工作负载或测量环境差异归因于架构变化。
保留原 lesson id 的关联，明确哪些经验被支持、修正或仍未验证。

只在 V2 的 docs/compiler-agent/ 写新的复盘并更新索引，
不修改 V1 历史，不重构代码，不启动 V3。返回结论及证据限制后停止。
```
