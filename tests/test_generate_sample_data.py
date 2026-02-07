from pathlib import Path

import pandas as pd

from scripts.generate_sample_data import SampleDataGenerator, SampleGenParams


def test_generate_sample_data_writes_required_files(tmp_path: Path) -> None:
    out_dir = tmp_path / "sample"
    params = SampleGenParams(n_users=10, n_sessions=20, n_interactions=50)
    SampleDataGenerator(seed=42).generate(out_dir, params)

    paths = [
        out_dir / "llm_system_interactions.csv",
        out_dir / "llm_system_sessions_summary.csv",
        out_dir / "llm_system_users_summary.csv",
    ]
    for p in paths:
        assert p.exists()

    interactions = pd.read_csv(out_dir / "llm_system_interactions.csv")
    for col in [
        "interaction_id",
        "session_id",
        "user_id",
        "timestamp_utc",
        "use_case",
        "model_provider",
        "latency_ms",
    ]:
        assert col in interactions.columns
