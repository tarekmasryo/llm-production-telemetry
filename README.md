<h2 style="margin:0 0 10px 0;">LLM Production Telemetry — Decision‑Grade Observability</h2>
<div style="margin:0 0 14px 0; opacity:0.9;">
  An <b>operator decision notebook</b>: turn noisy LLM telemetry into <b>ship‑ready policies</b> —
  SLO/budget burn → hotspots → routing backtest → drift checks → capacity‑aware triage → <code>DecisionArtifact</code>.
</div>

---

## What this repo is 🧭
This repo contains a <b>production‑minded notebook</b> that converts multi‑table LLM telemetry into <b>versionable policy artifacts</b> you can:

- review like configs ✅
- deploy behind feature flags 🚦
- monitor + rollback safely 🔁

This is not “EDA for pretty charts”. It is a <b>decision pipeline</b>.

---

## What you will produce 📦
The notebook writes outputs to <code>artifacts/</code>:

- <code>routing_policy_use_case.csv</code> — routing policy per <code>use_case</code> (cost‑aware + SLO‑aware)
- <code>drift_report.csv</code> — drift signals across windows (PSI / total‑variation distance)
- <code>triage_threshold_policy.json</code> — capacity‑aware review threshold (risk × unit costs × workload)
- <code>triage_actions_preview.csv</code> — ranked review‑queue preview in the evaluation window
- <code>decision_artifact.json</code> — strict JSON summary designed for automation/auditability

---

## Data inputs 🗃️
<b>Required</b> (CSV):
- <code>llm_system_interactions.csv</code>
- <code>llm_system_sessions_summary.csv</code>
- <code>llm_system_users_summary.csv</code>

<b>Optional</b> (CSV, ignored if missing):
- <code>llm_system_prompts_lookup.csv</code>
- <code>llm_system_instruction_tuning_samples.csv</code>

Schema notes: see <code>docs/schema.md</code>.

<b>Discovery order</b> (first hit wins):
<code>$LLMOPS_DATA_DIR</code> → <code>./</code> → <code>./data</code> → <code>/mnt/data</code> → <code>/kaggle/input</code>

---

## How to run ⚙️
### Option A — Kaggle
1) Add your dataset (or upload the CSVs).
2) Open <code>LLM_Production_Telemetry.ipynb</code> and click <b>Run All</b>.
3) Download outputs from <code>artifacts/</code>.

### Option B — Local (interactive)
Recommended: <b>Python 3.11+</b>

```bash
python -m venv .venv
# Windows (PowerShell): .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

python -m pip install -U pip
pip install -r requirements.txt
```

(Optional) dev tooling:
```bash
pip install -r requirements-dev.txt
```

Point the notebook to your CSVs:
- Windows (PowerShell)
  ```powershell
  $env:LLMOPS_DATA_DIR="D:\\path\\to\\csvs"
  ```
- macOS/Linux
  ```bash
  export LLMOPS_DATA_DIR=/path/to/csvs
  ```

Open the notebook:
```bash
jupyter notebook
```

### Option C — Headless execution (CI‑friendly)
Generate sample telemetry (safe to share), validate, then execute:

```bash
python scripts/generate_sample_data.py --out-dir data/sample --n-users 300 --n-sessions 500 --n-interactions 2400 --seed 42
python scripts/validate_data.py --data-dir data/sample
python scripts/run_notebook.py --data-dir data/sample --out-dir artifacts --config configs/default.yaml
```

---

## Windowing & leakage protection 🧠
- If a <code>split</code> column exists (<code>train/val/test</code>), the notebook uses it.
- Otherwise, it uses a <b>session‑safe time split</b> so sessions never leak across windows.

---

## Notebook flow (reader path) 🔎
1) Integrity gates (PK/FK + token sanity)
2) Health snapshot (failure/SLA/cost + missingness)
3) Budget burn over time
4) Hotspots + risk slices (where it breaks)
5) Routing policy + backtest (policy candidates + impact estimate)
6) Drift report (what changed between windows)
7) Triage threshold (calibrated risk → capacity‑aware decision)
8) DecisionArtifact (machine‑readable summary)

---

## Configuration knobs 🧩
Policy knobs live in <code>configs/default.yaml</code> and are mirrored to environment variables.
Environment variables take precedence over YAML.

Example overrides:
- Windows (PowerShell)
  ```powershell
  $env:SLA_MS="2000"
  $env:DAILY_COST_BUDGET_USD="50"
  python scripts/run_notebook.py --data-dir data/sample --out-dir artifacts
  ```
- macOS/Linux
  ```bash
  export SLA_MS=2000
  export DAILY_COST_BUDGET_USD=50
  python scripts/run_notebook.py --data-dir data/sample --out-dir artifacts
  ```

---

## Quality gates ✅
Run inside the venv:

```bash
ruff check .
ruff format --check .

pytest --cov=scripts --cov-report=term-missing
```

Pre-commit (requires a Git repo; ZIP users can run <code>git init</code> first):
```bash
pre-commit install
pre-commit run --all-files
```

---

## Important disclaimers ⚠️
- <b>Routing backtest has selection bias.</b> This is an observational estimate from historical behavior — treat it as a candidate policy to test behind a flag.
- <b>Missing cost/latency can distort decisions.</b> If your telemetry drops these fields at non‑trivial rates, add stop‑ship gates or estimate via pricing + tokens.
- <b>Triage is post‑call failure triage.</b> The label is <code>is_failure</code>, not a generic “needs_human_review” signal unless your schema defines it.

---

## Repo structure 🧱
```text
llm-production-telemetry/
├─ LLM_Production_Telemetry.ipynb
├─ artifacts/                      # generated outputs (gitignored)
├─ configs/
│  └─ default.yaml                 # policy knobs (SLA/budgets/capacity)
├─ data/
│  └─ sample/                      # synthetic, safe-to-share telemetry
├─ docs/
│  ├─ schema.md
│  └─ outputs.md
├─ scripts/
│  ├─ generate_sample_data.py
│  ├─ validate_data.py
│  └─ run_notebook.py
└─ .github/workflows/ci.yml
```

---

## License
MIT — see <code>LICENSE</code>.
