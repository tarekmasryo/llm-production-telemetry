# 🧭 LLM Production Telemetry — Decision-Grade Observability

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Notebook](https://img.shields.io/badge/Notebook-Kaggle%20ready-20BEFF)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Portfolio%20grade-success)

An operator-focused notebook that turns noisy LLM telemetry into **review-ready operational artifacts**:

**SLO/budget burn → hotspots → routing backtest → temporal drift checks → capacity-aware triage → `DecisionArtifact`.**

This is not a generic EDA notebook. It is a decision workflow for reviewing whether an LLM system is becoming slower, riskier, more expensive, or harder to operate.

---

## ✨ What this repo demonstrates

This project shows how to analyze LLM production telemetry with an operator mindset:

- ✅ Validate multi-table telemetry before analysis
- 📊 Monitor failure rate, latency, token volume, and cost
- 🔥 Identify risky use cases, providers, models, and account tiers
- 🧪 Backtest a candidate routing policy against baseline traffic
- 🌊 Detect temporal drift between early and recent windows
- 🧑‍💻 Build a capacity-aware triage threshold for review queues
- 🧾 Export a strict JSON `DecisionArtifact` for review and automation

The goal is not to claim that every candidate policy is ready to deploy. The goal is to produce evidence that helps decide whether to **keep baseline behavior, run shadow validation, or stop a rollout**.

---

## 🧠 Notebook story

You are the on-call operator for an LLM system. Telemetry is noisy, budgets are limited, and failures can carry operational risk.

The notebook answers three practical questions:

1. Are we burning reliability, latency, or cost budgets — and where?
2. Does a candidate routing policy meet rollout-review criteria in the evaluation window?
3. What triage threshold balances review capacity against missed-failure risk?

---

## 📦 Review-ready outputs

Generated files are written to `artifacts/`:

| Output | Purpose |
|---|---|
| `routing_policy_use_case.csv` | Candidate routing proposal per `use_case` |
| `routing_backtest_summary.csv` | Review verdict versus baseline traffic |
| `drift_report.csv` | Temporal early-vs-recent drift signals |
| `triage_threshold_policy.json` | Selected review threshold and operating-mode warning |
| `triage_baseline_comparison.csv` | Review-none, review-all, top-K, and selected-threshold comparison |
| `triage_actions_preview.csv` | Ranked preview of review candidates in the evaluation window |
| `triage_threshold_curve.csv` | Threshold sweep for capacity and cost trade-off review |
| `decision_artifact.json` | Machine-readable audit record for automation and traceability |

These artifacts are **review-ready operational evidence**. Any policy change should be validated in shadow mode before rollout.

---

## 🗃️ Data inputs

The notebook expects three required CSV files:

| File | Grain |
|---|---|
| `llm_system_interactions.csv` | One row per LLM interaction |
| `llm_system_sessions_summary.csv` | One row per session |
| `llm_system_users_summary.csv` | One row per user |

Optional CSVs are ignored if missing:

- `llm_system_prompts_lookup.csv`
- `llm_system_instruction_tuning_samples.csv`

Schema details are documented in [`docs/schema.md`](docs/schema.md).

The repo includes synthetic sample telemetry under `data/sample/` for local smoke tests.

---

## ⚙️ How to run

### Option A — Kaggle

1. Upload or attach the telemetry dataset.
2. Open `LLM_Production_Telemetry.ipynb`.
3. Click **Run All**.
4. Review generated files in `artifacts/`.

The notebook searches for data in this order:

```text
$LLMOPS_DATA_DIR → ./ → ./data → /mnt/data → /kaggle/input
```

### Option B — Local notebook

Recommended: **Python 3.11+**

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

python -m pip install -U pip
pip install -r requirements.txt
jupyter notebook LLM_Production_Telemetry.ipynb
```

To point the notebook to local CSVs:

```bash
export LLMOPS_DATA_DIR=/path/to/csvs
```

Windows PowerShell:

```powershell
$env:LLMOPS_DATA_DIR="D:\path\to\csvs"
```

### Option C — Headless smoke run

```bash
python scripts/generate_sample_data.py --out-dir data/sample --n-users 300 --n-sessions 500 --n-interactions 2400 --seed 42
python scripts/validate_data.py --data-dir data/sample
python scripts/run_notebook.py --data-dir data/sample --out-dir artifacts --config configs/default.yaml
```

---

## 🧪 Quality checks

Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

Run checks:

```bash
ruff check .
ruff format --check .
pytest --cov=scripts --cov-report=term-missing
pre-commit run --all-files
```

The notebook is committed without outputs so GitHub diffs stay clean. The GitHub Actions workflow runs linting, tests, sample-data generation, data validation, a notebook-output guard, a headless notebook smoke execution, and uploads the generated review artifacts.

---

## 🧱 Repository structure

```text
llm-production-telemetry/
├─ LLM_Production_Telemetry.ipynb
├─ CASE_STUDY.md
├─ README.md
├─ CHANGELOG.md
├─ LICENSE
├─ configs/
│  └─ default.yaml
├─ data/
│  └─ sample/
│     ├─ llm_system_interactions.csv
│     ├─ llm_system_sessions_summary.csv
│     └─ llm_system_users_summary.csv
├─ docs/
│  ├─ outputs.md
│  └─ schema.md
├─ scripts/
│  ├─ generate_sample_data.py
│  ├─ run_notebook.py
│  └─ validate_data.py
├─ tests/
└─ .github/workflows/ci.yml
```

---

## ⚠️ Important limitations

- The bundled sample data is synthetic and intended for analytics, benchmarking, and portfolio use.
- Routing backtests are observational; they can be biased by historical traffic assignment.
- Triage is modeled as post-call failure review, not a universal human-review label.
- Production use should add access controls, retention policies, redaction, monitoring, and rollout governance.

---

## ✅ Safe operationalization path

1. Treat exported artifacts as candidates.
2. Keep baseline routing if the candidate fails the backtest.
3. Run candidate policies in shadow mode before rollout.
4. Deploy only behind a feature flag and rollback switch.
5. Monitor budget burn, drift, failure rate, cost, and queue load in the next window.

---

## 📄 Case study

See [`CASE_STUDY.md`](CASE_STUDY.md) for the project narrative, problem framing, and implementation approach.

---

## 📜 License

MIT — see [`LICENSE`](LICENSE). Dataset licensing should be specified separately wherever the dataset is published.
