# Outputs

All generated artifacts are written to `artifacts/`.

| Artifact | Description |
|---|---|
| `routing_policy_use_case.csv` | Candidate routing proposal per `use_case`. |
| `routing_backtest_summary.csv` | Review verdict for the candidate routing policy versus baseline traffic. |
| `drift_report.csv` | Temporal early-vs-recent drift signals using PSI and total-variation distance. |
| `triage_threshold_policy.json` | Selected review threshold, expected workload, cost summary, and operating-mode warning. |
| `triage_baseline_comparison.csv` | Comparison against review-none, review-all, top-K, and selected-threshold policies. |
| `triage_actions_preview.csv` | Ranked preview of interactions that would enter the review queue. |
| `triage_threshold_curve.csv` | Threshold sweep for capacity and cost trade-off review. |
| `decision_artifact.json` | Strict machine-readable audit record for automation and traceability. |

## Operational note

These outputs are **review-ready artifacts**. They are intended to support controlled validation, shadow testing, and rollout review. They should not be treated as automatic production deployment instructions.
