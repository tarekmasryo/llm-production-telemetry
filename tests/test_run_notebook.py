import os
from pathlib import Path

import pytest

from scripts.run_notebook import NotebookRunner, RunParams


def test_apply_env_respects_existing_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SLA_MS", "123")
    runner = NotebookRunner()
    runner._apply_env({"SLA_MS": 999, "DAILY_COST_BUDGET_USD": 50})
    assert os.environ["SLA_MS"] == "123"
    assert os.environ["DAILY_COST_BUDGET_USD"] == "50"


def test_load_config_requires_mapping(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text("- a\n- b\n", encoding="utf-8")
    runner = NotebookRunner()
    with pytest.raises(ValueError):
        runner._load_config(p)


def test_run_sets_env_and_calls_execute(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    data_dir = tmp_path / "data"
    out_dir = tmp_path / "out"
    cfg = tmp_path / "cfg.yaml"
    nb = tmp_path / "nb.ipynb"
    executed = tmp_path / "executed.ipynb"

    data_dir.mkdir()
    nb.write_text("{}", encoding="utf-8")
    cfg.write_text("SLA_MS: 2000\n", encoding="utf-8")

    called = {"ok": False}

    def _fake_execute(_nb: Path, _executed: Path, _timeout: int) -> None:
        called["ok"] = True
        _executed.write_text("{}", encoding="utf-8")

    runner = NotebookRunner()
    monkeypatch.setattr(runner, "_execute_notebook", _fake_execute)

    params = RunParams(
        data_dir=data_dir,
        out_dir=out_dir,
        config=cfg,
        notebook=nb,
        executed=executed,
        timeout=1,
    )

    runner.run(params)

    assert called["ok"] is True
    assert os.environ["LLMOPS_DATA_DIR"] == str(data_dir)
    assert os.environ["OUT_DIR"] == str(out_dir)
    assert executed.exists()
