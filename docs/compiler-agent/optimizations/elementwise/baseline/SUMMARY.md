# Elementwise-family baseline（本轮正确性前提与画像）

- 发起：用户指令（2026-11-10），人类直接指导的优化轮；引擎状态保持不动
  （T044 在飞，本轮不派发引擎任务、不写引擎状态、不主张任何 gate 通过；
  correctness_only 验收不变）。判据为 QEMU 模拟执行的 guest 动态指令数
  等代理指标，不以墙钟/真实硬件加速比为目标。
- 范围：ops/suite/manifest.json 的 family=elementwise_reduce 去除
  red.*/pat.persistent_reduce/pat.reduce_broadcast/pat.softmax/misc.rng/
  mem.atomic tag → **134 算子 / 683 cases**（纯逐元素点态映射类：
  激活、逐元素算术及其融合；语料无裸 vector_add，最近代表 add_value/
  add_gelu/mul_sub）。清单：`operators-elementwise-family.txt`。
- 基线锚点：主仓库 HEAD `4217b79`（源码树与 HEAD 一致，仅 docs/未跟踪
  文件差异；softmax 轮基线亦在此 HEAD 验证 146/146）。
- 正确性前提：scoped scan **683/683 PASS**（t1，seed=30，golden 缓存；
  命令记录于 report.json）。工作副本 /tmp/opt-ew（git f4b4ae7）。
- 观测口径：matmul 轮工具链复用（tools/profiling/ 全套：QEMU 10 插件
  per-PC/per-vcpu/分类计数、insn_manifest 字节同一性联结、--repeats 差分
  稳态口径）；副本内校准复跑通过（straight/loop/vendor 全部精确）。
- 基线画像（13 代表 case，t1，动态指令/调用）：gelu/erf f32 ~69-70k、
  pow 79k、selu/sigmoid ~54-55k、tanh f16 55k、softplus 15k、
  swiglu f16 16k；纯逐元素（add_value/relu/sqrt/mul_relu/leaky_relu/
  relu_strided）2.0-3.4k。主瓶颈 = vmath 逐元素 libm 调用展开
  （56/134 算子含 math.transcendental；普查见 vmath_census.json）。
- 主瓶颈候选设计（未实施，用户自行实现）：见
  `../candidates/vector-poly/DESIGN.md`。
