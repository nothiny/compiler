# Reviewing an optimization batch

Use the project's architecture contract as the single reviewed declaration.
Explain the chosen transformations, legality, shared analyses, fallback,
measurement method and rollback boundary. Several passes may reuse modules and
analyses; the worker chooses their organization from the actual compiler.

Proposal notes are optional. They do not grant review approval or require a
separate task. If contract semantics change, edit the existing contract and
obtain independent review of the complete batch under the project's review
requirements. For engine-managed work, the manager uses review-input/review-report;
a direct human-guided session does not need an engine task or scope change. Do not implement against an unreviewed changed
contract. Design defects go to the planner through a DesignIssue.

Choose profitability checks, switches, trace counters and calibration probes
when they help test the change. The workflow does not mandate one module,
proposal, witness or task per pass or model term. Preserve historical contract
metadata while editing. Current full input comparison and digest-bound,
comparable improvement remain required for acceptance.
