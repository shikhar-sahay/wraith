# Experiment Methodology

## Research goal

Ghost Cloud investigates adaptive SSH honeypot behavior on AWS by deploying Internet-facing SSH honeypots, collecting real-world attacker telemetry, and comparing conventional/LLM-driven responses against a deterministic interactive shell. The goal is to observe credential guessing, scanning, session and command activity, evaluate limitations of purely LLM-driven behavior on constrained cloud instances, and develop a more realistic adaptive SSH shell.

## Baseline vs interactive rationale

- **Mumbai baseline (`ap-south-1`, `t3.micro`, Beelzebub + local Ollama `qwen2.5:0.5b`):** Tests whether a local LLM can emulate shell responses for every interaction. Intended as an adaptive/LLM-assisted path.
- **US-East interactive (`us-east-1`, `wraith-us-east-static` `100.27.226.37`, Beelzebub + Wraith deterministic shell `wraith/server.py`):** Tests whether deterministic, per-session stateful shell semantics (filesystem, parser, persona, privesc) provide more reliable and efficient interaction without per-command LLM inference.

The comparison is intentionally **observational rather than controlled A/B** - see Limitations.

## AWS regions and exposure methodology

- **Mumbai:** `ap-south-1`, instance `wraith-honeypot`, Ubuntu 24.04, `t3.micro`, Elastic IP, EBS 8 GB -> 15 GB for Ollama. Exposure: `2222/tcp` public honeypot, `22/tcp` admin restricted to operator IP, `11434/tcp` Ollama internal only. Period `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z` (24 reports).
- **US-East:** `us-east-1`, instance `wraith-us-east-static`, historically `100.27.226.37`, same port separation (`2222` honeypot public, `22` admin restricted). Period `2026-07-12` - `2026-09-06` (14 daily reports, 12 with activity). Both were unsolicited Internet traffic.

## Port separation and access

- Honeypot `2222` is public internet-facing and handled by Beelzebub.
- Admin `22` is restricted to operator IP via security group; Wraith honeypot continued on `2222` while US-East admin `22` was inaccessible due to masked `ssh.socket` (see `docs/us-east-recovery.md`), proving logical separation.

## Traffic exclusion policy

- **Mumbai:** `49.207.63.82`, `49.207.60.111`, `49.207.58.88`
- **US-East:** those three plus `223.187.126.163`, `223.187.121.20`, `1.2.3.4` (synthetic `1.2.3.4` from local tests)
- Exclusion is applied at parse time (`excluded_ips` set in `scripts/generate_report*.py`, session-level for Wraith), and is noted as `Test traffic excluded: Yes` in reports. Filtered metrics are the source of truth for documented results.

## Telemetry sources

- **Beelzebub raw events (Mumbai):** JSONL with `event` envelope, `Status` (`Stateless` for login attempts, `Start` for sessions, `Interaction` for commands), `SourceIp`, `SourcePort`, `User`, `Password`, `Client`, `DateTime`, `Command`/`CommandOutput`, `msg` with `total_duration`/`eval_count` for LLM stats. Raw logs are not committed; reports are generated via `scripts/generate_report.py`.
- **Wraith application events (US-East):** JSONL `wraith_logs/events.jsonl` with `event` (`session_started`, `command_executed`, `session_ended`), `session_id`, `attacker_ip`, `client`, `command`, `response`, `cwd`, `latency_ms`, `timestamp`, `duration_seconds`, `commands`. Produced by `wraith/telemetry.py` (`TelemetryLogger`) via `wraith/server.py` (`FakeShellServer`/`FakeShellSession`). Raw `raw-data-us-east/` and `*.tar.gz` are gitignored; only Markdown reports in `reports/us-east/` are versioned.
- **Generated Markdown reports:** `experiments/mumbai/` (24+1) and `reports/us-east/` (14+1) with Summary, Attacking IPs, Credentials/Commands, Session Details, Clients, Research Notes. Period derived from `min`/`max` DateTime across non-excluded events.

## Session definitions

- **Mumbai (Beelzebub):** `Stateless` = login attempt (password guess), `Start` = session start (ID, IP, user, client), `Interaction` = command execution within session. Metrics: `Unique IPs` = distinct `SourceIp` across sessions+logins, `Total sessions` = `Start` count, `Login attempts` = `Stateless` count, `Sessions with commands` = sessions where `commands` non-empty.
- **US-East (Wraith):** `session_started` = new `session_id` (hash of IP/client/timestamp), `command_executed` = parsed command via `wraith/parser.py` (shlex), `session_ended` = `exit` or timeout. Metrics: `Unique attacker IPs` = distinct `attacker_ip`, `Total sessions` = distinct `session_id`, `Sessions with commands` = sessions where `commands` non-empty, `Total commands` = sum of `commands` lengths. Login attempt counts are **not** directly comparable (Mumbai counts password guesses, Wraith counts sessions).

## Report generation

- **Mumbai:** `scripts/generate_report.py` against Beelzebub logs: `python scripts/generate_report.py /path/to/logs --exclude-ip 49.207.63.82 --exclude-ip ... --no-geo --out-dir experiments/mumbai --out-file 2026-07-03.md` daily; cumulative `python scripts/generate_report.py /path/to/logs --all --no-geo --out-dir experiments/mumbai --out-file cumulative.md` (combines `logs*` files from input directory).
- **US-East:** `scripts/generate_report_us_east.py` against Wraith JSONL: daily via explicit `--out-file` redirection (because `--out-dir` alone names by current UTC date), cumulative via `--all` (combines `logs*` JSONL files). Both scripts support `--out-file` for daily and cumulative, `--no-geo` to skip `ip-api.com`, and zero-activity wording `No attacker login attempts...` for `2026-07-01.md`-like validation intervals.
- **Limitations:** Daily `--out-dir` naming by current UTC date is retained for backward compatibility; historical daily report regeneration uses explicit `--out-file`. Geo lookup is rate-limited to 45 req/min and optional.

## Filtered vs raw metrics

Documented metrics are filtered (test IPs excluded). Raw volume (e.g., US-East 21103 total commands) includes high-volume automated loops (`echo -e "\x6F\x6B"` 79.0% - 16662/21103 from predominantly one session); normalized engagement is `sessions with commands` (Mumbai 1, US-East 11) and exact unique command strings (Mumbai 1 vs US-East 18). Reports distinguish raw total from sessions with commands and unique clients.

## Comparison limitations and observational nature

The Mumbai and US-East deployments differed in geography (`ap-south-1` vs `us-east-1`), exposure duration (23 vs 56 days, different activity windows), backend type (Ollama `qwen2.5:0.5b` per-command vs deterministic `wraith/server.py`), attacker population (773 broad scanners vs 12 focused sessions), telemetry semantics (Beelzebub `Stateless` vs Wraith `session_started`), session definitions, and infrastructure conditions (OOM vs masked `ssh.socket`). Results in `docs/deployment-comparison.md` are therefore presented as an **observational comparison**, not a controlled causal experiment, with explicit caveats and without universal claims (e.g., not `deterministic universally better`).

## Reproducibility

- Mumbai raw Beelzebub logs remain on the instance (not committed); reports are reproducible via `scripts/generate_report.py` with excluded IPs and `--no-geo` as above.
- US-East raw `wraith_logs/events.jsonl` is preserved locally in `raw-data-us-east/` (gitignored) and backup `wraith-us-east-telemetry-backup-*.tar.gz` (gitignored); reports in `reports/us-east/` are the committed reproducible artifact.
- All documented metrics are taken directly from committed reports (`experiments/mumbai/cumulative.md`, `reports/us-east/cumulative.md`) and daily reports, not from uncommitted raw files.
