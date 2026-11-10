# Matmul-family baseline correctness scan (round precondition)

- 目的：用户声明全部 case 已修复（2026-11-10）；本 scan 在当前 HEAD 上对
  matmul 族做独立验证，同时作为优化轮的正确性基线锚点。
- 基线：git `3ed513e`（见 CONTEXT.txt），threads=1，seed=30（驱动默认），
  golden 缓存启用。
- 命令（由 report.json 的 `command` 字段完整记录）：
  `python3 tools/run_scan.py run --report .../baseline/scan/report.json
   --journal .../baseline/scan/journal.jsonl --threads 1 --operator <57 个
  matmul 族算子>`（算子清单：`../operators-matmul-family.txt`）。
- 结果：**312/312 PASS**（0 失败、0 超时、0 拒绝）。
  - census：312 cases → 251 identities（全语料 2734/2161）。
  - 编译：252 次（60 cache 命中），冷编译中位 ~2.0 s。
  - checks：compile_count_le_identity_census_1_25x、
    artifact_identities_le_identity_census_1_25x、
    compile_count_equals_artifact_identities、cache_hit_is_fast、
    report_complete、resource_instruction_families_covered 全部 true
    （代表 resource case：matmul_k32_fast_kernel_f2eeb00c [128] float16）。
- 逐 case 机器可读证据：`report.json`（含 per-case identity/artifact_key/
  launch_seconds），`journal.jsonl`，`scan.log`（后台任务日志副本见
  /tmp/zcode-bash-lqWlYf/.../call_178c493aa3e348c4af2b3d5e-stdout.log）。
- 结论：matmul 族在 HEAD=3ed513e 上正确性前提满足（单 worker 口径；
  多 worker 由本轮末的完整输入回归与指标采集的 1/2/4/8 运行覆盖）。
