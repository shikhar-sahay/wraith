# Wraith Experiments

This folder will document the Wraith deterministic shell deployment artifacts after cloud recovery. Code is implemented locally in `wraith/` and verified via `demo_fake_shell.py` and `tests/test_fake_shell.py`; the historical cloud instance `wraith-us-east-static` (`us-east-1`, `100.27.226.37`) is pending recovery.

## Intended Contents

- Daily reports generated from `wraith_logs/` (pending US-East telemetry)
- Cumulative summaries built from Wraith JSONL telemetry (pending)
- Notes comparing attacker behavior against the Mumbai deployment (intended static-vs-interactive comparison, not yet supported by complete data)

## Status

- **Local implementation:** Complete (`wraith/server.py`, `wraith/filesystem.py`, `wraith/telemetry.py` etc., per-session filesystem, deterministic command handling).
- **Cloud deployment:** Historical instance `wraith-us-east-static` previously accepted connections on `100.27.226.37:2222` but is currently inaccessible (see `docs/aws-deployment-notes.md`); no Wraith cloud telemetry has been incorporated yet.
- **Comparative analysis:** Pending until US-East recovery and validation; do not present Mumbai-vs-Wraith comparison as completed.

## Workflow (after recovery)

1. Collect raw JSONL telemetry in `wraith_logs/` on the recovered EC2 host.
2. Generate Markdown reports into `reports/` via `scripts/generate_report.py`.
3. Copy or organize curated Wraith experiment outputs here when validated.
