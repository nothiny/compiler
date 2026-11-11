# Softmax-family baseline correctness scan (round precondition)

- 目的：本轮（softmax 优化轮）的正确性前提——在当前 HEAD 上对
  softmax_xent 家族做独立验证，作为优化轮的正确性基线锚点。
- 基线：git `4217b79`（见 CONTEXT.txt；自 `f69be1d` 起仅 docs 提交，
  编译器代码与 matmul 候选版一致），threads=1，seed=30（驱动默认），
  golden 缓存启用。
- 命令（完整记录于 report.json 的 `command` 字段）：
  `set -a; . ./.env; set +a; python3 tools/run_scan.py run
   --report .../softmax/baseline/scan/report.json
   --journal .../softmax/baseline/scan/journal.jsonl --threads 1
   --operator <25 个 softmax_xent 族算子>`（清单：`../operators-softmax-family.txt`）。
- 结果：**146/146 PASS**（0 失败、0 超时、0 拒绝、0 missing）。
  - census：146 cases → 125 identities（全语料 2734/2161）。
  - 编译：0 次（146 缓存命中——今日 matmul 轮全量回归已编译全部
    identity；`compile_count_equals_artifact_identities=false` 为跨 run
    缓存复用的正常表现，非缺陷）。
  - checks：`compile_count_le_identity_census_1_25x`、
    `artifact_identities_le_identity_census_1_25x`、`cache_hit_is_fast`、
    `report_complete` 为 true。
  - `resource_instruction_families_covered=false`：**预期**。scoped 扫描的
    代表 resource case（`matmul_k32_fast_kernel_f2eeb00c [128] float16`，
    IME 见证）不在本家族算子集内；resource 契约为 set 级覆盖
    （commit 3ed513e），由本轮末的完整输入回归提供。
- 观测口径校准（同日复跑，全部精确通过）：straight/loop/vendor
  （`python3 tools/profiling/validate_counts.py`，证据
  `../../matmul/tooling/phase-a/validation.json`，副本见本目录
  `validation-phase-a.json`）。
- 结论：softmax 家族在 HEAD=4217b79 上正确性前提满足（单 worker 口径；
  多 worker 由本轮末的完整输入回归与指标采集的 1/2/4/8 运行覆盖）。
