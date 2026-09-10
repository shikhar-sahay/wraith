# Wraith Telemetry Pipeline

## Purpose

This document explains how the Wraith deterministic shell records SSH attacker activity and turns it into Markdown reports. It applies to the Wraith implementation verified locally (`wraith/` -> `wraith_logs/` -> `reports/`) and to the recovered cloud instance `wraith-us-east-static` (`us-east-1`, `100.27.226.37`, `reports/us-east/` 12 sessions, see `docs/us-east-results.md`). The Mumbai deployment (`ap-south-1`, Beelzebub + local Ollama `qwen2.5:0.5b`) uses raw Beelzebub logs directly via `scripts/generate_report.py` -> `experiments/mumbai/` and is documented separately.

## Flow

```mermaid
flowchart TD
    A[Attacker interaction] --> B[SSH honeypot]
    B --> C[Telemetry collection]
    C --> D[JSONL event storage]
    D --> E[generate_report.py]
    E --> F[Markdown experiment report]
```

## Event Types

### session_started

Created when a new session begins.

Fields:

- `event`
- `session_id`
- `attacker_ip`
- `client`
- `timestamp`

### command_executed

Created for each simulated command.

Fields:

- `event`
- `session_id`
- `attacker_ip`
- `client`
- `command`
- `response`
- `cwd`
- `latency_ms`
- `timestamp`

### session_ended

Created when the SSH session finishes.

Fields:

- `event`
- `session_id`
- `attacker_ip`
- `client`
- `duration_seconds`
- `commands`
- `timestamp`

## Storage Locations

- `wraith_logs/` contains raw JSONL telemetry
- `reports/` contains generated Markdown output

## Report Output

`scripts/generate_report.py` is used to transform the JSONL telemetry (Wraith) or Beelzebub logs (Mumbai) into experiment reports that summarize:

- total sessions
- unique observed source IPs
- SSH client strings
- command counts and frequency (Mumbai: 1 command total; Wraith: 21103 total, 78.9% `echo -e "\x6F\x6B"` loop, see `docs/us-east-results.md`)
- suspicious command patterns (`nvidia-smi`, `lspci` GPU detection)
- session duration statistics (Wraith sub-millisecond, Mumbai 51 sec mean LLM latency)

Verification: `wraith/telemetry.py` appends `events.jsonl` and is exercised by `tests/test_fake_shell.py` and `demo_fake_shell.py`; Mumbai validated via 24 reports, Wraith via `reports/us-east/` after `docs/us-east-recovery.md` EBS repair.

## Operational Notes

- Each line in the JSONL file should be a single JSON object; Mumbai Beelzebub logs are JSONL with `event` envelope.
- Malformed lines are ignored safely during parsing.
- Telemetry is designed to be append-only so the report pipeline can be rerun later (`--out-file` and `--no-geo` supported).
- Both Mumbai (`experiments/mumbai/`) and Wraith (`reports/us-east/`) are validated research artifacts after recovery; Wraith cloud reports were regenerated via `scripts/generate_report_us_east.py` with six excluded IPs and `--out-file` redirection for daily reports.