# Reports

This folder stores generated Markdown experiment reports.

## Contents

- **US-East Wraith (`us-east-1`, `100.27.226.37`)** in `us-east/`: 14 daily reports + `cumulative.md` (period `2026-07-12` - `2026-09-06`, 12 IPs, 12 sessions, 21103 commands, see `../docs/us-east-results.md`)
- Mumbai reports are **not** in `reports/` - they are preserved in `reports/mumbai/` (24 reports + `cumulative.md`, period `2026-07-03` - `2026-07-26`, see `../docs/mumbai-results.md`)
- Cumulative summaries and daily reports are generated via `scripts/generate_report.py` (Mumbai Beelzebub logs) and `scripts/generate_report_us_east.py` (Wraith JSONL)

## Notes

- Raw telemetry stays in `wraith_logs/` (and gitignored `raw-data-us-east/` with backup `wraith-us-east-telemetry-backup-*.tar.gz`); only Markdown reports are versioned.
- Historical Mumbai artifacts in `experiments/mumbai/` remain preserved; `2026-07-05.md` remains absent.
- Reports here should not overwrite preserved historical experiment files; use `--out-file` for explicit daily naming and `--all` for cumulative.
- See `docs/deployment-comparison.md` for Mumbai vs US-East observational comparison.
