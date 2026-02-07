import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class SampleGenParams:
    n_users: int
    n_sessions: int
    n_interactions: int


class SampleDataGenerator:
    def __init__(self, seed: int) -> None:
        self._rng = np.random.default_rng(seed)

    def generate(self, out_dir: Path, params: SampleGenParams) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)

        users = self._make_users(params.n_users)
        sessions = self._make_sessions(users, params.n_sessions)
        interactions = self._make_interactions(sessions, params.n_interactions)
        sessions_summary = self._aggregate_sessions(interactions)
        users_summary = self._aggregate_users(interactions)

        interactions.to_csv(out_dir / "llm_system_interactions.csv", index=False)
        sessions_summary.to_csv(out_dir / "llm_system_sessions_summary.csv", index=False)
        users_summary.to_csv(out_dir / "llm_system_users_summary.csv", index=False)

    def _make_users(self, n_users: int) -> pd.DataFrame:
        return pd.DataFrame({"user_id": [f"u{idx:05d}" for idx in range(1, n_users + 1)]})

    def _make_sessions(self, users: pd.DataFrame, n_sessions: int) -> pd.DataFrame:
        sessions = pd.DataFrame(
            {
                "session_id": [f"s{idx:06d}" for idx in range(1, n_sessions + 1)],
                "user_id": self._rng.choice(users["user_id"], size=n_sessions, replace=True),
            }
        )
        sessions["split"] = self._rng.choice(
            ["train", "val", "test"], size=n_sessions, p=[0.7, 0.15, 0.15]
        )
        return sessions

    def _make_interactions(self, sessions: pd.DataFrame, n_interactions: int) -> pd.DataFrame:
        use_cases = ["support", "search", "summarization", "coding", "analytics"]
        tiers = ["free", "pro", "enterprise"]
        channels = ["web", "mobile", "api"]
        regions = ["us", "eu", "mena", "apac"]
        segments = ["consumer", "smb", "enterprise"]

        provider_to_model = {
            "openai": "gpt",
            "anthropic": "claude",
            "google": "gemini",
            "local": "llama",
        }
        providers = list(provider_to_model.keys())

        combos = [(uc, prov, provider_to_model[prov]) for uc in use_cases for prov in providers]
        reps = int(np.ceil(n_interactions / len(combos)))
        combo_rows = (combos * reps)[:n_interactions]
        self._rng.shuffle(combo_rows)

        inter_session_idx = self._rng.integers(0, len(sessions), size=n_interactions)
        inter_sessions = sessions.iloc[inter_session_idx].reset_index(drop=True)

        start = pd.Timestamp("2025-01-01", tz="UTC")
        day_offsets = self._rng.integers(0, 60, size=n_interactions)
        sec_offsets = self._rng.integers(0, 24 * 3600, size=n_interactions)
        timestamps = (
            start + pd.to_timedelta(day_offsets, unit="D") + pd.to_timedelta(sec_offsets, unit="s")
        )

        prompt_tokens = self._rng.integers(40, 400, size=n_interactions)
        completion_tokens = self._rng.integers(20, 700, size=n_interactions)
        total_tokens = prompt_tokens + completion_tokens

        base_latency = self._rng.normal(loc=900, scale=200, size=n_interactions).clip(150, 8000)
        latency_ms = (
            base_latency + total_tokens * self._rng.normal(loc=1.6, scale=0.4, size=n_interactions)
        ).clip(150, 12000)
        tokens_per_second = (total_tokens / (latency_ms / 1000)).clip(1, 500)

        temperature = self._rng.uniform(0.0, 1.2, size=n_interactions).round(2)
        top_p = self._rng.uniform(0.6, 1.0, size=n_interactions).round(2)
        max_tokens = self._rng.integers(128, 2048, size=n_interactions)
        retry_index = self._rng.integers(0, 3, size=n_interactions)

        tool_calls_count = self._rng.poisson(lam=0.3, size=n_interactions)

        cost_per_1k = self._rng.choice(
            [0.002, 0.004, 0.006], size=n_interactions, p=[0.5, 0.3, 0.2]
        )
        cost_usd = (total_tokens / 1000.0) * cost_per_1k

        response_quality_score = self._rng.uniform(0.2, 1.0, size=n_interactions).round(3)
        user_feedback_score = (
            self._rng.normal(loc=0.2, scale=0.6, size=n_interactions).clip(-1, 1).round(3)
        )

        p_flag = 0.02
        safety_block_flag = self._rng.random(n_interactions) < (p_flag * 0.4)
        hallucination_flag = self._rng.random(n_interactions) < (p_flag * 0.8)
        toxicity_flag = self._rng.random(n_interactions) < (p_flag * 0.2)
        formatting_error_flag = self._rng.random(n_interactions) < (p_flag * 0.5)
        tool_error_flag = self._rng.random(n_interactions) < (p_flag * 0.5)
        latency_timeout_flag = self._rng.random(n_interactions) < (p_flag * 0.6)

        failure_type = np.array(["none"] * n_interactions, dtype=object)
        failure_type = np.where(safety_block_flag, "safety_block", failure_type)
        failure_type = np.where(hallucination_flag, "hallucination", failure_type)
        failure_type = np.where(toxicity_flag, "toxicity", failure_type)
        failure_type = np.where(formatting_error_flag, "formatting_error", failure_type)
        failure_type = np.where(tool_error_flag, "tool_error", failure_type)
        failure_type = np.where(latency_timeout_flag, "latency_timeout", failure_type)
        is_failure = failure_type != "none"

        return pd.DataFrame(
            {
                "interaction_id": [f"i{idx:07d}" for idx in range(1, n_interactions + 1)],
                "session_id": inter_sessions["session_id"].astype(str).values,
                "user_id": inter_sessions["user_id"].astype(str).values,
                "timestamp_utc": pd.to_datetime(timestamps, utc=True),
                "split": inter_sessions["split"].values,
                "use_case": [r[0] for r in combo_rows],
                "model_provider": [r[1] for r in combo_rows],
                "model_name": [r[2] for r in combo_rows],
                "account_tier": self._rng.choice(tiers, size=n_interactions),
                "channel": self._rng.choice(channels, size=n_interactions),
                "region": self._rng.choice(regions, size=n_interactions),
                "segment": self._rng.choice(segments, size=n_interactions),
                "latency_ms": latency_ms.round(2),
                "prompt_tokens": prompt_tokens.astype(int),
                "completion_tokens": completion_tokens.astype(int),
                "total_tokens": total_tokens.astype(int),
                "tokens_per_second": tokens_per_second.round(2),
                "cost_usd": cost_usd.round(6),
                "tool_calls_count": tool_calls_count.astype(int),
                "temperature": temperature,
                "top_p": top_p,
                "max_tokens": max_tokens.astype(int),
                "retry_index": retry_index.astype(int),
                "response_quality_score": response_quality_score,
                "user_feedback_score": user_feedback_score,
                "failure_type": failure_type,
                "is_failure": is_failure.astype(bool),
                "is_failure_was_missing": np.zeros(n_interactions, dtype=bool),
                "safety_block_flag": safety_block_flag.astype(bool),
                "hallucination_flag": hallucination_flag.astype(bool),
                "toxicity_flag": toxicity_flag.astype(bool),
                "formatting_error_flag": formatting_error_flag.astype(bool),
                "tool_error_flag": tool_error_flag.astype(bool),
                "latency_timeout_flag": latency_timeout_flag.astype(bool),
            }
        )

    def _aggregate_sessions(self, interactions: pd.DataFrame) -> pd.DataFrame:
        return interactions.groupby("session_id", as_index=False).agg(
            user_id=("user_id", "first"),
            start_timestamp_utc=("timestamp_utc", "min"),
            end_timestamp_utc=("timestamp_utc", "max"),
            session_total_cost_usd=("cost_usd", "sum"),
            session_total_tokens=("total_tokens", "sum"),
            session_total_requests=("interaction_id", "size"),
            session_total_failures=("is_failure", "sum"),
            split=("split", "first"),
        )

    def _aggregate_users(self, interactions: pd.DataFrame) -> pd.DataFrame:
        return interactions.groupby("user_id", as_index=False).agg(
            user_total_cost_usd=("cost_usd", "sum"),
            user_total_requests=("interaction_id", "size"),
            user_total_failures=("is_failure", "sum"),
        )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", type=str, default="data/sample")
    ap.add_argument("--n-users", type=int, default=200)
    ap.add_argument("--n-sessions", type=int, default=350)
    ap.add_argument("--n-interactions", type=int, default=2400)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    generator = SampleDataGenerator(seed=args.seed)
    params = SampleGenParams(
        n_users=args.n_users,
        n_sessions=args.n_sessions,
        n_interactions=args.n_interactions,
    )
    generator.generate(Path(args.out_dir), params)


if __name__ == "__main__":
    main()
