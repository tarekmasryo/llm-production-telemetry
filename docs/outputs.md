# Outputs

All generated artifacts are written to `artifacts/`.

- `routing_policy_use_case.csv`
  - Per-use-case routing policy candidate (cost-aware + SLO-aware).

- `drift_report.csv`
  - Drift signals across time windows (PSI / total-variation distance) to flag policy decay.

- `triage_threshold_policy.json`
  - Capacity-aware review threshold policy (risk × unit costs × workload).

- `triage_actions_preview.csv`
  - Ranked preview of interactions that would be routed to manual review in the evaluation window.

- `decision_artifact.json`
  - Strict machine-readable summary for automation/auditability.
