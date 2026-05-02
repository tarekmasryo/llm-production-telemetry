# Changelog

## v1.0.3
- Stripped committed notebook outputs and execution counts for cleaner GitHub diffs.
- Aligned notebook metadata with the Python 3.11 project target.
- Added a CI guard that fails when notebook outputs are committed.
- Uploaded generated review artifacts from the CI smoke run.

## v1.0.2
- Replaced the notebook with the final Kaggle-ready version.
- Updated README wording from rollout-focused language to review-ready operational artifacts.
- Documented all generated artifacts, including routing backtest and triage threshold curve outputs.
- Aligned case-study wording with the final notebook conclusions and safe rollout path.

## v1.0.1
- Refactored CLI scripts to small OOP components without changing CLI flags.
- Applied notebook import and formatting cleanup.

## v1.0.0
- Added production-style repo structure, CI, pre-commit config, and pinned dependencies.
- Added sample telemetry generator and integrity validator.
- Added headless notebook runner with YAML-configurable policy knobs.
