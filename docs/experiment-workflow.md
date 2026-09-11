# Experiment Workflow

## Purpose

This repository keeps experiment output for both the Mumbai LLM-adapted deployment (completed and recovered) and the Wraith deterministic shell deployment (local implementation verified; cloud recovered with telemetry in `reports/us-east/`).

## Experiment Layout

Recommended structure:

```text
experiments/
  mumbai/        (24 reports + cumulative, Beelzebub + Ollama qwen2.5:0.5b)
  us-east/       (experiment notes for Wraith deterministic shell)
reports/
  us-east/       (14 daily + cumulative, Wraith JSONL via wraith/telemetry.py)
```

The recovered Mumbai files in `experiments/mumbai/` (24 dated reports + `cumulative.md`, period `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z`) are preserved and should not be deleted or overwritten except via deliberate regeneration from raw Beelzebub logs. `2026-07-05.md` must remain absent and `2026-07-01.md` is validation-only. Wraith reports in `reports/us-east/` (14 daily + `cumulative.md`, period `2026-07-12` - `2026-09-06`, see `docs/us-east-results.md`) are likewise preserved after recovery via `scripts/generate_report_us_east.py`; they are organized from `wraith_logs/events.jsonl` (gitignored `raw-data-us-east/`).

## Workflow

1. Run the selected honeypot deployment (both Mumbai `t3.micro` and Wraith `us-east-1` have completed observation periods).
2. Collect raw telemetry (Mumbai: Beelzebub logs; Wraith: `wraith_logs/events.jsonl` via `wraith/telemetry.py`).
3. Exclude known test traffic when needed (Mumbai: `49.207.63.82`, `49.207.60.111`, `49.207.58.88`; Wraith: those plus `223.187.126.163`, `223.187.121.20`, `1.2.3.4`).
4. Generate a Markdown report for the day or cumulative period (`scripts/generate_report.py` for Mumbai, `scripts/generate_report_us_east.py` for Wraith, both with `--out-file` and `--no-geo`).
5. Store the report in the appropriate deployment folder (`experiments/mumbai/` Mumbai, `reports/us-east/` Wraith).
6. Add manual notes after reviewing attacker behavior (see `experiments/mumbai/cumulative.md` and `reports/us-east/cumulative.md` Research Notes; comparison in `docs/deployment-comparison.md`).

## Deployment Mapping

| Deployment | Experiment target | Notes |
|------------|-------------------|-------|
| Mumbai | `experiments/mumbai/` | Recovered Beelzebub + local Ollama `qwen2.5:0.5b` outputs - 24 dated reports (July 1 validation + July 3-26 observation) + cumulative (773 IPs, 942 sessions, 15,153 logins, 1 command) |
| Wraith | `reports/us-east/` and `experiments/us-east/` | Wraith deterministic shell reports - 14 daily + cumulative in `reports/us-east/` (period `2026-07-12` - `2026-09-06`, 12 IPs, 21103 commands, see `docs/us-east-results.md`) |

## Report Sources

- Mumbai reports originate from raw Beelzebub logs via `scripts/generate_report.py` (local Ollama `qwen2.5:0.5b` path) and land in `experiments/mumbai/` (July 1 is validation-only; July 5 intentionally absent)
- Wraith reports originate from `wraith_logs/events.jsonl` via `scripts/generate_report_us_east.py` (Wraith JSONL) and land in `reports/us-east/` (daily via `--out-file` redirection, cumulative via `--all`)

## Preservation Rule

Do not remove or overwrite existing experiment results. Both Mumbai (`experiments/mumbai/`) and Wraith (`reports/us-east/`) results are preserved alongside the historical artifacts. Comparative analysis is documented as an observational comparison in `docs/deployment-comparison.md` (not a controlled causal experiment).

## US-East Status

Instance `wraith-us-east-static` in `us-east-1` (historically `100.27.226.37`, port `2222`) was recovered via offline EBS repair (masked `ssh.socket -> /dev/null` removed, `ssh.service` enabled, snapshot before repair - see `docs/us-east-recovery.md`). Telemetry preserved in `reports/us-east/` (12 IPs, 12 sessions, 21103 commands). Comparative analysis is now available but remains observational due to differing regions, periods, and populations.