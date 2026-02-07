import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RequiredFiles:
    interactions: str = "llm_system_interactions.csv"
    sessions: str = "llm_system_sessions_summary.csv"
    users: str = "llm_system_users_summary.csv"


class TelemetryDataValidator:
    def __init__(self, required: RequiredFiles | None = None) -> None:
        self._required = required or RequiredFiles()

    def validate(self, data_dir: Path) -> None:
        files = self._required
        missing = [
            name
            for name in [files.interactions, files.sessions, files.users]
            if not (data_dir / name).exists()
        ]
        if missing:
            raise FileNotFoundError(f"Missing required file(s) in {data_dir}: {missing}")

        interactions = self._read_csv(data_dir / files.interactions)
        sessions = self._read_csv(data_dir / files.sessions)
        users = self._read_csv(data_dir / files.users)

        self._validate_primary_keys(interactions, sessions, users)
        self._validate_foreign_keys(interactions, sessions, users)
        self._validate_token_invariant(interactions)

        print("OK: integrity gates passed")

    def _read_csv(self, path: Path) -> pd.DataFrame:
        return pd.read_csv(path)

    def _validate_primary_keys(
        self, interactions: pd.DataFrame, sessions: pd.DataFrame, users: pd.DataFrame
    ) -> None:
        for df, key, name in [
            (interactions, "interaction_id", "interactions"),
            (sessions, "session_id", "sessions"),
            (users, "user_id", "users"),
        ]:
            if key not in df.columns:
                raise ValueError(f"Missing PK column {key} in {name}")
            if df[key].astype(str).duplicated().any():
                raise ValueError(f"PK not unique: {name}.{key}")

    def _validate_foreign_keys(
        self, interactions: pd.DataFrame, sessions: pd.DataFrame, users: pd.DataFrame
    ) -> None:
        interactions = interactions.copy()
        sessions = sessions.copy()
        users = users.copy()

        interactions["session_id"] = interactions["session_id"].astype(str)
        interactions["user_id"] = interactions["user_id"].astype(str)
        sessions["session_id"] = sessions["session_id"].astype(str)
        users["user_id"] = users["user_id"].astype(str)

        if not set(interactions["session_id"]).issubset(set(sessions["session_id"])):
            raise ValueError("FK failed: interactions.session_id -> sessions.session_id")
        if not set(interactions["user_id"]).issubset(set(users["user_id"])):
            raise ValueError("FK failed: interactions.user_id -> users.user_id")

    def _validate_token_invariant(self, interactions: pd.DataFrame) -> None:
        token_cols = ["prompt_tokens", "completion_tokens", "total_tokens"]
        if not all(c in interactions.columns for c in token_cols):
            return

        pt = pd.to_numeric(interactions["prompt_tokens"], errors="coerce")
        ct = pd.to_numeric(interactions["completion_tokens"], errors="coerce")
        tt = pd.to_numeric(interactions["total_tokens"], errors="coerce")
        mask = pt.notna() & ct.notna() & tt.notna()
        if int(mask.sum()) == 0:
            return

        ok = np.isclose(tt[mask], pt[mask] + ct[mask])
        if not bool(ok.all()):
            raise ValueError(
                "Token invariant failed: total_tokens != prompt_tokens + completion_tokens"
            )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=str, default="data/sample")
    args = ap.parse_args()

    TelemetryDataValidator().validate(Path(args.data_dir))


if __name__ == "__main__":
    main()
