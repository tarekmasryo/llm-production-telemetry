from pathlib import Path

import pandas as pd
import pytest

from scripts.generate_sample_data import SampleDataGenerator, SampleGenParams
from scripts.validate_data import TelemetryDataValidator


def test_validator_passes_on_generated_sample(tmp_path: Path) -> None:
    out_dir = tmp_path / "sample"
    params = SampleGenParams(n_users=10, n_sessions=20, n_interactions=60)
    SampleDataGenerator(seed=7).generate(out_dir, params)

    TelemetryDataValidator().validate(out_dir)


def test_validator_fails_on_duplicate_primary_key(tmp_path: Path) -> None:
    out_dir = tmp_path / "sample"
    params = SampleGenParams(n_users=10, n_sessions=20, n_interactions=60)
    SampleDataGenerator(seed=7).generate(out_dir, params)

    p = out_dir / "llm_system_interactions.csv"
    df = pd.read_csv(p)
    df.loc[1, "interaction_id"] = df.loc[0, "interaction_id"]
    df.to_csv(p, index=False)

    with pytest.raises(ValueError):
        TelemetryDataValidator().validate(out_dir)
