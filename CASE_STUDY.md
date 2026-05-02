# Case Study — LLM Production Telemetry

## Overview

This project turns noisy LLM telemetry into **operator-review artifacts**:

**SLO/budget burn → hotspots → routing backtest → temporal drift checks → capacity-aware triage → `DecisionArtifact`.**

It includes:

- a decision-grade notebook: `LLM_Production_Telemetry.ipynb`
- a telemetry validator CLI
- a synthetic sample-data generator
- a headless notebook runner for smoke tests and CI

## The problem

LLM systems fail as operational systems, not only as models:

- latency spikes under load while average quality looks stable
- one provider or model becomes expensive for a specific use case
- routing changes help one slice but regress another
- retries and long completions quietly increase cost
- tool errors or formatting failures cluster in narrow segments

A useful LLMOps workflow needs to identify these issues before a policy is rolled out.

## What this repo does

The notebook converts telemetry into reviewable evidence:

1. **Integrity gates** — validate primary keys, foreign keys, timestamps, and token accounting.
2. **Health snapshot** — summarize failures, SLA breaches, latency, cost, and missingness.
3. **Budget burn** — show reliability, latency, and cost pressure over time.
4. **Hotspots and slices** — identify the use cases, tiers, models, and providers driving risk.
5. **Routing backtest** — compare a candidate routing proposal against historical baseline traffic.
6. **Temporal drift report** — compare early and recent windows using PSI and total-variation distance.
7. **Triage threshold** — select a review threshold based on capacity, false-negative cost, and unit review cost.
8. **DecisionArtifact** — export a strict JSON summary for review and traceability.

## Definition of done

A successful run should:

- pass integrity checks
- generate all expected artifacts under `artifacts/`
- make the routing recommendation explicit
- compare triage policy against simple baselines
- mark risky outcomes as `review_required` instead of treating them as automatic rollout instructions

## Outputs

Expected outputs are documented in [`docs/outputs.md`](docs/outputs.md).

The most important final artifact is:

```text
decision_artifact.json
```

It records whether the current run is clean or requires review, and why.

## Design choices

- **Synthetic sample data** keeps the repo safe to share.
- **Strict validation** prevents analysis on broken telemetry.
- **Review-ready language** avoids overclaiming rollout readiness.
- **Headless execution** makes the notebook easier to smoke-test in CI.
- **Simple baselines** make triage policy conclusions easier to audit.

## Limitations

- The sample telemetry is synthetic and should not be interpreted as real production billing, incident, or customer data.
- Routing backtests are observational and may be biased by historical traffic assignment.
- A candidate routing policy should be tested in shadow mode before rollout.
- Production deployments should add privacy controls, access controls, retention policies, redaction, monitoring, and rollback governance.

## Suggested next steps

- Add weekly baseline comparison reports.
- Add release gates for cost, latency, failure rate, and review queue load.
- Add provider pricing configuration for more realistic cost simulation.
- Export an HTML or PDF run report for stakeholders.
