# Report Generation

This folder contains two report generators with different input schemas. They are intentionally separate, not duplicates.

## `generate_report.py` - Mumbai (Beelzebub logs)

- **Input:** Beelzebub raw JSONL with `event` envelope (`Status` `Stateless`/`Start`/`Interaction`, `SourceIp`, `User`, `Password`, `Client`, `DateTime`, `Command`/`CommandOutput`, `msg` with `total_duration`)
- **Output:** `reports/mumbai/` daily `YYYY-MM-DD.md` and `cumulative.md` (Markdown with Summary, Attacking IPs, Credentials, Commands, Session Details, Clients, Research Notes)
- **Test traffic excluded:** `49.207.63.82`, `49.207.60.111`, `49.207.58.88` via `--exclude-ip` (session and login filtering)
- **Usage:**
  ```bash
  python scripts/generate_report.py /path/to/beelzebub/logs --exclude-ip 49.207.63.82 --exclude-ip 49.207.60.111 --exclude-ip 49.207.58.88 --no-geo --out-dir reports/mumbai --out-file 2026-07-03.md
  python scripts/generate_report.py /path/to/beelzebub/logs --all --exclude-ip ... --no-geo --out-dir reports/mumbai --out-file cumulative.md
  ```
- **Behavior:** `--out-file` works for both daily and cumulative (`if args.out_file: fname=args.out_file elif args.all: fname=cumulative.md else date.md`); `--out-dir` alone names daily by current UTC date (use `--out-file` for historical dates); `--all` combines `logs*` files from input directory; `--no-geo` skips `ip-api.com` lookup; zero-activity `2026-07-01.md` uses `No attacker login attempts...` wording

## `generate_report_us_east.py` - US-East (Wraith JSONL)

- **Input:** Wraith application JSONL `wraith_logs/events.jsonl` with `event` (`session_started`, `command_executed`, `session_ended`), `session_id`, `attacker_ip`, `client`, `command`, `response`, `cwd`, `latency_ms`, `timestamp`
- **Output:** `reports/us-east/` daily and `cumulative.md` (Summary, Attacking IPs, Commands, Suspicious Commands, Session Details, Clients)
- **Test traffic excluded:** `49.207.63.82`, `49.207.60.111`, `49.207.58.88`, `223.187.126.163`, `223.187.121.20`, `1.2.3.4` via `--exclude-ip` (session-level filtering in `extract_sessions`)
- **Usage:**
  ```bash
  python scripts/generate_report_us_east.py /path/to/wraith_logs --exclude-ip 49.207.63.82 --exclude-ip ... --no-geo --out-dir reports/us-east --out-file 2026-08-05.md
  python scripts/generate_report_us_east.py /path/to/wraith_logs --all --exclude-ip ... --no-geo --out-dir reports/us-east --out-file cumulative.md
  ```
- **Behavior:** Same `--out-file`/`--all`/`--no-geo` semantics as Mumbai generator after fix (previously daily `--out-file` was ignored, now general); historical daily reports required explicit `--out-file` redirection because `--out-dir` alone uses current UTC date; cumulative `--all` combines `logs*` JSONL files

## Reproducibility

- Mumbai reports in `experiments/mumbai/` were regenerated from surviving Beelzebub logs with three excluded IPs and `--no-geo` (see `docs/mumbai-results.md`)
- US-East reports in `reports/us-east/` were regenerated from preserved `raw-data-us-east/events.jsonl` (gitignored, backup `wraith-us-east-telemetry-backup-*.tar.gz` gitignored) with six excluded IPs (see `docs/us-east-results.md` and `docs/us-east-recovery.md`)
- Raw `*.jsonl` and `raw-data-us-east/` remain gitignored; only Markdown reports are versioned
- Verify before committing: `python -m py_compile scripts/generate_report*.py` and `python -m unittest tests/test_fake_shell.py` (4 tests)

## Why two generators?

Different input schemas (Beelzebub `Status`/`SourceIp` vs Wraith `event`/`session_id`) and different session definitions (Mumbai counts `Stateless` logins vs Wraith counts `session_started`) prevent a single generic generator without loss of fidelity. They share Markdown output structure and `--out-file`/`--no-geo` options for consistency.
