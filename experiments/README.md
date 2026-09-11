# Experiments

This folder stores experiment artifacts for both deployments in Ghost Cloud.

## Current Contents

- **Mumbai (`ap-south-1`, `t3.micro`, Beelzebub + Ollama `qwen2.5:0.5b`)** in `mumbai/`: 24 dated reports + `cumulative.md` (period `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z`, 773 IPs, 942 sessions, 15153 logins, 1 command), `README.md`, `experiment-log.md`; see `docs/mumbai-results.md` and `docs/mumbai-incident.md`
- **Wraith US-East (`us-east-1`, `100.27.226.37`, deterministic shell)** in `us-east/`: experiment notes (`README.md`, `experiment-log.md`) for the Wraith deterministic shell; daily and cumulative reports are in `reports/us-east/` (`docs/us-east-results.md`)
- **No top-level `cumulative.md` or `experiment-log.md`** - each deployment has its own

## Organization

```text
experiments/
  mumbai/        (24 reports + cumulative, Beelzebub logs, 2026-07-03 - 2026-07-26)
  us-east/       (README + experiment-log for Wraith deterministic shell, 2026-07-12 - 2026-09-06)
reports/
  us-east/       (14 daily + cumulative, Wraith JSONL, 12 IPs, 21103 commands)
```

Historical Mumbai files in `reports/mumbai/` and Wraith US-East reports in `reports/us-east/` are preserved and should not be deleted or overwritten except via deliberate regeneration (`scripts/generate_report.py` for Mumbai, `scripts/generate_report_us_east.py` for US-East). `2026-07-05.md` remains absent; `2026-07-01.md` is validation-only.

## Related Docs

- [Experiment Workflow](../docs/experiment-workflow.md)
- [Telemetry Pipeline](../docs/telemetry-pipeline.md)
- [Mumbai Results](../docs/mumbai-results.md) and [Mumbai Incident](../docs/mumbai-incident.md)
- [US-East Results](../docs/us-east-results.md) and [US-East Recovery](../docs/us-east-recovery.md)
- [Deployment Comparison](../docs/deployment-comparison.md)