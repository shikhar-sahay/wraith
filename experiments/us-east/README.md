# Wraith Experiments

This folder documents the Wraith deterministic shell deployment artifacts; the cloud instance `wraith-us-east-static` (`us-east-1`, `100.27.226.37`) has been recovered (see `docs/us-east-recovery.md`) and produced telemetry in `reports/us-east/` (14 daily + `cumulative.md`, see `docs/us-east-results.md`).

## Contents

- Daily reports in `reports/us-east/` (period `2026-07-12` - `2026-09-06`, 12 IPs, 12 sessions, 21103 commands)
- Cumulative summary `reports/us-east/cumulative.md` (test traffic excluded: `49.207.63.82`, `49.207.60.111`, `49.207.58.88`, `223.187.126.163`, `223.187.121.20`, `1.2.3.4`)
- Observational comparison against Mumbai in `docs/deployment-comparison.md` (caveat: different regions/periods, not a controlled causal experiment)

## Status

- **Local implementation:** Complete (`wraith/server.py`, `wraith/filesystem.py`, `wraith/telemetry.py` etc., per-session filesystem, deterministic command handling; `tests/test_fake_shell.py` pass).
- **Cloud deployment:** Instance `wraith-us-east-static` recovered via offline EBS repair (masked `ssh.socket` removed, `ssh.service` enabled); Beelzebub and Wraith services verified active; telemetry preserved in `reports/us-east/`.
- **Comparative analysis:** Observational comparison completed in `docs/deployment-comparison.md`; not a controlled causal experiment.

## Workflow

1. Collect raw JSONL telemetry in `wraith_logs/` on the recovered EC2 host.
2. Generate Markdown reports into `reports/` via `scripts/generate_report.py`.
3. Copy or organize curated Wraith experiment outputs here when validated.
