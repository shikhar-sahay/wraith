# Experiment Workflow

## Purpose

This repository keeps experiment output for both the Mumbai LLM-adapted deployment (completed and recovered) and the Wraith deterministic shell deployment (local implementation verified; cloud recovery pending).

## Experiment Layout

Recommended structure:

```text
experiments/
  mumbai/
    existing reports
  wraith/
    daily reports
reports/
  generated Markdown reports
```

The recovered Mumbai files in `experiments/mumbai/` (24 dated reports + `cumulative.md`, period `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z`) are preserved and should not be deleted or overwritten except via deliberate regeneration from raw Beelzebub logs. `2026-07-05.md` must remain absent and `2026-07-01.md` is validation-only. New Wraith reports, when cloud telemetry becomes available after US-East recovery, will be generated under `reports/` and organized into `experiments/wraith/` when curated. Until then, Wraith has no cloud research artifact beyond local tests.

## Workflow

1. Run the selected honeypot deployment (Mumbai completed; Wraith local verified, cloud pending).
2. Collect raw telemetry (Mumbai: Beelzebub logs; Wraith: `wraith_logs/events.jsonl` via `wraith/telemetry.py`).
3. Exclude known test traffic when needed (Mumbai: `49.207.63.82`, `49.207.60.111`, `49.207.58.88`).
4. Generate a Markdown report for the day or cumulative period (`scripts/generate_report.py` with `--out-file` and `--no-geo`).
5. Store the report in the appropriate deployment folder (`experiments/mumbai/` validated; `experiments/wraith/` and `reports/` pending US-East data).
6. Add manual notes after reviewing attacker behavior (see `experiments/mumbai/cumulative.md` Research Notes for Mumbai methodology).

## Deployment Mapping

| Deployment | Experiment target | Notes |
|------------|-------------------|-------|
| Mumbai | `experiments/mumbai/` | Recovered Beelzebub + local Ollama `qwen2.5:0.5b` outputs - 24 dated reports (July 1 validation + July 3-26 observation) + cumulative (773 IPs, 942 sessions, 15,153 logins, 1 command) |
| Wraith | `reports/` and `experiments/wraith/` | Generated Markdown reports and deployment-specific archives from the static shell deployment |

## Report Sources

- Mumbai reports originate from raw Beelzebub logs via `scripts/generate_report.py` (local Ollama `qwen2.5:0.5b` path) and land in `experiments/mumbai/` (July 1 is validation-only; July 5 intentionally absent)
- Wraith reports originate from `wraith_logs/` and `generate_report.py`, then land in `reports/`

## Preservation Rule

Do not remove or overwrite existing experiment results. New Wraith cloud results, after recovery and validation, should be added alongside the historical Mumbai artifacts. Comparative static-vs-interactive analysis remains pending until US-East telemetry is available and should not be presented as completed.

## US-East Status

Instance `wraith-us-east-static` in `us-east-1` (historically `100.27.226.37`, port `2222`) is currently inaccessible (port `22` refused, EC2 Instance Connect failed, SSM unavailable due to missing role configuration; serial console reaches a Linux login prompt). Recovery is in progress. Do not fabricate US-East telemetry or claim that the intended Mumbai-vs-Wraith comparison has been completed.