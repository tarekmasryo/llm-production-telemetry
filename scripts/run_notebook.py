import argparse
import asyncio
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import nbformat
import yaml
from nbconvert.preprocessors import ExecutePreprocessor


@dataclass(frozen=True)
class RunParams:
    data_dir: Path
    out_dir: Path
    config: Path
    notebook: Path
    executed: Path
    timeout: int


class NotebookRunner:
    def __init__(self, kernel_name: str = "python3") -> None:
        self._kernel_name = kernel_name
        self._ensure_windows_event_loop_policy()

    def run(self, params: RunParams) -> None:
        if params.config.exists():
            cfg = self._load_config(params.config)
            self._apply_env(cfg)

        os.environ["LLMOPS_DATA_DIR"] = str(params.data_dir)
        os.environ["OUT_DIR"] = str(params.out_dir)

        params.out_dir.mkdir(parents=True, exist_ok=True)
        self._execute_notebook(params.notebook, params.executed, params.timeout)

    def _ensure_windows_event_loop_policy(self) -> None:
        if sys.platform.startswith("win"):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    def _load_config(self, path: Path) -> dict:
        obj = yaml.safe_load(path.read_text(encoding="utf-8"))
        if obj is None:
            return {}
        if not isinstance(obj, dict):
            raise ValueError("Config must be a mapping (YAML dict)")
        return obj

    def _apply_env(self, cfg: dict) -> None:
        for k, v in cfg.items():
            if v is None:
                continue
            os.environ.setdefault(str(k), str(v))

    def _execute_notebook(self, notebook_path: Path, executed_path: Path, timeout: int) -> None:
        nb = nbformat.read(str(notebook_path), as_version=4)
        ep = ExecutePreprocessor(timeout=timeout, kernel_name=self._kernel_name)
        ep.preprocess(nb, {"metadata": {"path": str(notebook_path.parent)}})
        executed_path.parent.mkdir(parents=True, exist_ok=True)
        nbformat.write(nb, str(executed_path))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=str, default="data/sample")
    ap.add_argument("--out-dir", type=str, default="artifacts")
    ap.add_argument("--config", type=str, default="configs/default.yaml")
    ap.add_argument("--notebook", type=str, default="LLM_Production_Telemetry.ipynb")
    ap.add_argument(
        "--executed", type=str, default="artifacts/LLM_Production_Telemetry.executed.ipynb"
    )
    ap.add_argument("--timeout", type=int, default=900)
    args = ap.parse_args()

    runner = NotebookRunner()
    params = RunParams(
        data_dir=Path(args.data_dir),
        out_dir=Path(args.out_dir),
        config=Path(args.config),
        notebook=Path(args.notebook),
        executed=Path(args.executed),
        timeout=int(args.timeout),
    )
    runner.run(params)


if __name__ == "__main__":
    main()
