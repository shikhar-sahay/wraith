# Mumbai Experiment Log - Beelzebub + Local LLM (ap-south-1)

Chronological record of the Mumbai honeypot deployment, subsequent operational interruption, and dataset recovery. Dates are included only where supported by telemetry or repository evidence.

## Deployment and validation

- **Host:** `wraith-honeypot` - AWS EC2 `t3.micro`, Ubuntu 24.04 LTS, region `ap-south-1` (Mumbai).
- **Honeypot:** Beelzebub on SSH port `2222` (Internet-facing); administrative SSH on `22` restricted to operator IP.
- **LLM backend:** Local Ollama `qwen2.5:0.5b`.
- **2026-07-01 - Pre-observation / validation activity:** Report shows Period `N/A`, unique IPs `0`, sessions `0`, login attempts `0`, LLM calls `6` (avg 3,245 ms, 26.8 tokens). No attacker events present. Interpreted as pre-attack LLM testing/validation, not start of telemetry collection.

## First observed real-world traffic

- **2026-07-03T18:59:13Z - First surviving attacker telemetry.** `2026-07-03.md` records 2 unique source IPs, 22 sessions, 598 login attempts (first Internet-facing evidence after validation).

## Prolonged Internet exposure (2026-07-03 through 2026-07-26)

- **Continuous Internet exposure** with daily reports generated from Beelzebub logs. The honeypot collected unsolicited SSH credential-guessing and scanning traffic throughout this window.
- **Report set (surviving):** `2026-07-03.md`, `2026-07-04.md`, `2026-07-06.md` through `2026-07-26.md` (no surviving report for July 2; see below). Each daily report was regenerated from raw logs with test IPs excluded (`49.207.63.82`, `49.207.60.111`, `49.207.58.88`).
- **Telemetry character:** Heavy automated activity; only one session across the entire period progressed to command execution (recorded in cumulative data).

## Report collection - gaps and exclusions

- **July 2:** No surviving telemetry source; no dated report exists. Gap is documented and not filled with fabricated data.
- **July 5:** Old incorrectly generated report `2026-07-05.md` was identified as stale (no supporting telemetry source) and intentionally deleted. The clean dataset contains no July 5 report.

## July 26 - Resource exhaustion and telemetry interruption

- **~2026-07-26T17:17-17:18Z - OOM condition:** Local Ollama invoked the Linux OOM killer; `llama-server` killed (RSS ~629 MB); `systemd-journald` and `snapd` watchdog failures. Kernel evidence: `Out of memory: Killed process ... (llama-server)`.
- **Beelzebub remained alive** and continued processing SSH activity until at least the last confirmed attacker event at **2026-07-26T17:23:56Z**.
- **~2026-07-26T17:44Z - Guest networking degraded:** `169.254.169.254` unreachable, DNS via `127.0.0.53` misbehaving, Amazon SSM agent unable to reach AWS endpoints; cron/sysstat continued. Interpretation: local LLM caused severe memory pressure and OOM; OS and Beelzebub survived, but degraded networking prevented further external honeypot connectivity and therefore stopped telemetry collection.
- **Pre-outage observation:** Source IP `39.105.172.20` repeatedly reconnected and issued `echo -e "\x6F\x6B"` (285 sessions on July 26). Plugin logged `Rate limit exceeded` / `plugin "LLMHoneypot" execute error: rate limited`; local `qwen2.5:0.5b` returned inconsistent responses (command-not-found, malformed explanations, escaped Unicode). Documented as a limitation of pure LLM-based terminal emulation; not the cause of the outage (OOM/network degradation is the confirmed cause).
- **Instance lifetime:** EC2 remained running from approximately July 17 until September 10 without intentional stop (not a crash of the host).

## September 10 - Recovery

- **2026-09-10 - Instance rebooted.** After reboot: SSH `22` reachable, honeypot `2222` reachable, Beelzebub started normally, Ollama started normally.

## Regeneration and cumulative dataset recovery

- **2026-09-11 - Full recovery/regeneration from raw Beelzebub logs:** All surviving Mumbai reports were regenerated via `scripts/generate_report.py` (with `--out-file` support for both daily and cumulative modes, test-IP exclusion, `--no-geo` where applicable). Commit `a0aae0c` ("Regenerate Mumbai honeypot telemetry reports") produced the clean 24-report set plus `cumulative.md`.
- **2026-09-11 - Stale July 5 report removal** confirmed as part of regeneration.
- **Cumulative dataset (final):** Period `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z`; 773 unique observed source IPs, 942 sessions, 15,153 login attempts, 1 session with commands, 1 total command executed (`echo 1 > /dev/null && cat /bin/echo` from `47.113.113.162`), avg LLM latency 51,094 ms, avg tokens 27.7 - see `cumulative.md` for full tables. Test traffic excluded.
- **2026-09-11 - Generator fix:** `scripts/generate_report.py` updated so `--out-file` help string reads "Custom output filename" (not "used with --all") and so zero-activity days (e.g., July 1) report "No attacker login attempts or command execution were recorded for this period." instead of "Attackers are currently in the brute-force phase." Cumulative generator now emits research notes distinguishing measurement findings from infrastructure observations.

## References

- `experiments/mumbai/README.md` - deployment summary and findings
- `experiments/mumbai/cumulative.md` - aggregated telemetry and research notes
- `experiments/mumbai/2026-07-*.md` - daily reports (24 files)
- `scripts/generate_report.py` - report generator
- Root `README.md` and `docs/` for project-wide context (Wraith adaptive-shell work builds on the Mumbai limitations documented here)
