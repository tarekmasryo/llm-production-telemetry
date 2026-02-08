# Case Study — LLM Production Telemetry (Decision-Grade Observability)

## Overview
This project turns messy LLM telemetry into **operator decisions**:
SLO/budget burn → hotspots → routing backtests → drift checks → capacity-aware triage → a versionable `DecisionArtifact`.

It includes:
- a decision-first notebook (`LLM_Production_Telemetry.ipynb`)
- a strict telemetry validator (CLI)
- a small, share-safe sample generator for smoke runs

## The real problem
LLM systems do not fail like classic ML models. They fail as **systems**:
- latency spikes under load while quality looks unchanged
- prompt/model changes improve one slice but regress another
- cost grows quietly via longer outputs or retries
- tool-calling errors appear only in specific scenarios
- one provider outage forces a routing decision under pressure

If you only track aggregate quality, you learn about regressions after users do.

## Goals (definition of done)
**Functional goals**
- Validate telemetry tables and joins (minimum contract).
- Produce decision views: **SLO + budget burn**, **hotspots**, **risk slices**, **routing policy candidates**, and **drift deltas**.

**Engineering goals**
- Fail fast when telemetry is broken (missing columns, duplicated IDs, invalid joins).
- Keep analysis reproducible and CPU-friendly.
- Provide two entry points: **CLI validation** and **notebook execution**.

## Data contract (minimum viable telemetry)
Telemetry is represented as three CSV tables (see `docs/schema.md`):

- `llm_system_interactions.csv` (required): per-interaction records (latency, tokens, costs, outcomes)
- `llm_system_sessions_summary.csv` (required): session-level rollups
- `llm_system_users_summary.csv` (required): user-level rollups

The validator enforces required files, required columns, primary-key uniqueness, and join integrity.

## Approach
### 1) Integrity first
Run validation before analysis to catch:
- missing files / columns
- duplicated IDs
- invalid joins across tables

This prevents building conclusions on corrupted telemetry.

### 2) Decision views (not presentation-first charts)
The notebook is structured around operator decisions:
- **Health snapshot:** failure rates, SLA breaches, cost/latency distribution
- **Budget burn:** cost over time and the drivers behind it
- **Hotspots + slices:** where quality/cost/latency breaks (domain × scenario × model/provider)
- **Routing backtests:** candidate policies and expected impact
- **Drift checks:** what changed between windows
- **Triage threshold:** capacity-aware decisioning from calibrated risk signals

### 3) Outputs
Runs produce reusable outputs under `./artifacts/` (tables and figures used to support release decisions).
See `artifacts/README.md` for expected outputs.

## Usage
Setup and execution steps are documented in `README.md`.

Minimal flow:
- Validate: `python scripts/validate_data.py --data-dir <csv_dir>`
- Run the notebook (interactive or headless) and export outputs to `./artifacts/`

## Limitations
- Telemetry schemas vary across stacks; this repo enforces a strict minimum contract.
- Some attributions depend on what your logs include (tool errors, provider metadata, routing labels).
- This repository provides an analysis workflow; production deployments should add access controls, redaction, and retention policies.

## Next steps
- Add a release gate policy: slice-quality thresholds + max cost/latency budgets.
- Track weekly baselines and regressions (drift alerts).
- Integrate into CI: block merges when validation fails or key metrics regress.
