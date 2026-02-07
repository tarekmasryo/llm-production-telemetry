# Telemetry schema (minimum contract)

This notebook expects **three required tables**. Optional tables are ignored if missing.

## 1) `llm_system_interactions.csv` (required)

**Grain:** one row per model interaction.

Minimum columns:
- `interaction_id` (string) — primary key
- `session_id` (string) — FK → `sessions_summary.session_id`
- `user_id` (string) — FK → `users_summary.user_id`
- `timestamp_utc` (timestamp) — request time (UTC)
- `is_failure` (bool) — whether the interaction failed

Strongly recommended:
- `latency_ms` (float)
- `cost_usd` (float)
- `prompt_tokens`, `completion_tokens`, `total_tokens` (ints) with the invariant:
  `total_tokens = prompt_tokens + completion_tokens`
- `use_case`, `account_tier`, `channel`, `model_provider`, `model_name`, `region`, `segment` (categoricals)
- flags (bool): `safety_block_flag`, `hallucination_flag`, `toxicity_flag`, `formatting_error_flag`,
  `tool_error_flag`, `latency_timeout_flag`

Optional:
- `split` with values in `{train,val,test}` (session-safe). If missing, a time split is used.

## 2) `llm_system_sessions_summary.csv` (required)

**Grain:** one row per session.

Minimum columns:
- `session_id` (string) — primary key

Recommended:
- `user_id` (string)
- `start_timestamp_utc`, `end_timestamp_utc` (timestamps)
- `session_total_cost_usd`, `session_total_tokens`, `session_total_requests`, `session_total_failures`

## 3) `llm_system_users_summary.csv` (required)

**Grain:** one row per user.

Minimum columns:
- `user_id` (string) — primary key

Recommended:
- `user_total_cost_usd`, `user_total_requests`, `user_total_failures`
