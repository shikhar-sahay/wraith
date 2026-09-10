# Experiment Workflow

## Purpose

This repository keeps experiment output for both the Mumbai LLM-adapted deployment and the Wraith static-shell deployment.

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

The current historical experiment files remain preserved in the repository root under `experiments/`. They should not be deleted or overwritten. New Wraith reports are generated under `reports/` and can then be organized into the deployment-specific experiment folders when curated.

## Workflow

1. Run the selected honeypot deployment.
2. Collect raw telemetry.
3. Exclude known test traffic when needed.
4. Generate a Markdown report for the day or cumulative period.
5. Store the report in the appropriate deployment folder.
6. Add manual notes after reviewing attacker behavior.

## Deployment Mapping

| Deployment | Experiment target | Notes |
|------------|-------------------|-------|
| Mumbai | `experiments/mumbai/` | Recovered Beelzebub + local Ollama `qwen2.5:0.5b` outputs - 24 dated reports (July 1 validation + July 3-26 observation) + cumulative (773 IPs, 942 sessions, 15,153 logins, 1 command) |
| Wraith | `reports/` and `experiments/wraith/` | Generated Markdown reports and deployment-specific archives from the static shell deployment |

## Report Sources

- Mumbai reports originate from raw Beelzebub logs via `scripts/generate_report.py` (local Ollama `qwen2.5:0.5b` path) and land in `experiments/mumbai/` (July 1 is validation-only; July 5 intentionally absent)
- Wraith reports originate from `wraith_logs/` and `generate_report.py`, then land in `reports/`

## Preservation Rule

Do not remove or overwrite existing experiment results. New Wraith results should be added alongside the historical Mumbai artifacts.