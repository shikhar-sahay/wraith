# Mumbai Experiment - Beelzebub + Local LLM (Adaptive SSH Honeypot)

Adaptive SSH Honeypot for Real-World Attack Telemetry Collection on AWS - Mumbai deployment (CyberDefenders track "Ghost Cloud: LLM Honeypots in AWS").

## What this experiment was

An Internet-facing SSH honeypot deployed on AWS to collect unsolicited, real-world SSH attack telemetry and to evaluate an adaptive/interactive honeypot that uses a local LLM for shell deception versus a static/traditional baseline. This directory preserves the recovered, regenerated dataset and reports after the July 26 operational interruption.

## Deployment architecture

- **Region:** `ap-south-1` (Mumbai)
- **EC2 host:** `wraith-honeypot` - `t3.micro`, Ubuntu 24.04 LTS
- **Honeypot framework:** Beelzebub
- **SSH honeypot port:** `2222` (Internet-facing)
- **Administrative SSH:** `22` (restricted to operator IP)
- **LLM backend:** Local Ollama `qwen2.5:0.5b`
- **Pipeline:** Internet SSH traffic -> Beelzebub (port 2222) -> Ollama LLM plugin for shell responses -> raw Beelzebub logs -> `scripts/generate_report.py` -> Markdown reports in this directory

## Observation period and report coverage

- **Confirmed attacker-observation period:** `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z` (July 3 through July 26, 2026)
- **Clean report set (24 dated reports + cumulative):**
  `2026-07-01.md`, `2026-07-03.md`, `2026-07-04.md`, `2026-07-06.md`, `2026-07-07.md`, `2026-07-08.md`, `2026-07-09.md`, `2026-07-10.md`, `2026-07-11.md`, `2026-07-12.md`, `2026-07-13.md`, `2026-07-14.md`, `2026-07-15.md`, `2026-07-16.md`, `2026-07-17.md`, `2026-07-18.md`, `2026-07-19.md`, `2026-07-20.md`, `2026-07-21.md`, `2026-07-22.md`, `2026-07-23.md`, `2026-07-24.md`, `2026-07-25.md`, `2026-07-26.md`, `cumulative.md`
- **July 1 - pre-observation / validation:** Period `N/A`, unique IPs `0`, sessions `0`, login attempts `0`, LLM calls `6`. Contains LLM-performance activity only; no attacker events. Do not treat as start of telemetry collection.
- **July 2 - no surviving report:** No telemetry source recovered for this date; no report generated. This gap is expected and not fabricated.
- **July 5 - intentionally deleted:** An old stale `2026-07-05.md` was removed because no surviving July 5 telemetry source supports it. Do not recreate it.

All dated reports and `cumulative.md` were regenerated from raw Beelzebub logs. Test traffic from known operator IPs was excluded at generation time: `49.207.63.82`, `49.207.60.111`, `49.207.58.88`.

## Cumulative dataset (authoritative metrics)

Source: `cumulative.md` - Period `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z`, test traffic excluded.

| Metric | Value |
|--------|-------|
| Unique observed source IPs | 773 |
| Total sessions | 942 |
| Login attempts (credential guesses) | 15,153 |
| Sessions with commands | 1 |
| Total commands executed | 1 |
| Avg LLM response latency | 51,094 ms |
| Avg tokens generated | 27.7 |

Wording note: use "unique source IPs" / "observed source addresses" / "Internet hosts observed" - not "773 sophisticated attackers."

## Major findings

- **Telemetry finding:** The deployment attracted substantial automated SSH scanning and credential-guessing (15k+ login attempts across 773 source IPs) but only one recorded session progressed to post-authentication command execution (`echo 1 > /dev/null && cat /bin/echo` from `47.113.113.162`). Engagement depth was minimal. This is itself a meaningful result for adaptive-honeypot research.
- **Infrastructure finding:** Running a local LLM (`qwen2.5:0.5b` via Ollama) on a `t3.micro` is operationally fragile under sustained Internet exposure (see July 26 incident).
- **Deception finding:** Pure LLM-based terminal emulation showed response inconsistency and rate limiting under repeated trivial input, supporting Wraith's later hybrid design.

## July 26 operational interruption

- **~17:17-17:18 UTC:** Ollama triggered the Linux OOM killer; `llama-server` killed (RSS ~629 MB); `systemd-journald` and `snapd` watchdog failures. Kernel message: `Out of memory: Killed process ... (llama-server)`.
- **Beelzebub did not immediately crash** and continued processing SSH activity until the last confirmed attacker event at `2026-07-26T17:23:56Z`.
- **~17:44 UTC:** Guest reported `169.254.169.254` unreachable, DNS via `127.0.0.53` misbehaving, SSM agent unable to reach AWS endpoints; cron/sysstat continued. Best-supported interpretation: OOM/resource exhaustion followed by degraded guest networking that interrupted external honeypot connectivity and stopped telemetry collection.
- **Instance lifetime:** EC2 remained running July 17 - September 10 without intentional stop. Rebooted September 10: SSH `22`, honeypot `2222`, Beelzebub, and Ollama all recovered normally.
- Use precise language: *resource exhaustion, OOM condition, degraded guest networking, telemetry interruption* - not unqualified "server crashed."

## Observed LLM limitation (pre-outage)

Shortly before telemetry stopped, source IP `39.105.172.20` repeatedly reconnected and issued `echo -e "\x6F\x6B"` (285 sessions on July 26). The Beelzebub `LLMHoneypot` plugin logged `Rate limit exceeded` / `plugin "LLMHoneypot" execute error: rate limited`. The local `qwen2.5:0.5b` backend returned inconsistent responses to the same command (e.g., `command not found`, malformed explanations, escaped Unicode). This is documented as a limitation of pure LLM-based shell emulation, not as the cause of the outage (OOM/network degradation was the confirmed infrastructure cause).

## Limitations

- LLM inference on `t3.micro` (approx. 1 GB RAM class) was not operationally reliable for sustained LLM-backed SSH deception under observed Internet load; mean latency 51 s and the July 26 OOM indicate limited reliability on this `t3.micro` configuration.
- Single-command post-auth dataset limits conclusions about interactive attacker behavior; results characterize the scanning/brute-force phase.
- No geographic or actor attribution is claimed beyond observed source IPs and SSH client strings.

## Relationship to Wraith adaptive-shell work

The Mumbai result directly motivates Wraith's architecture: use deterministic shell behavior for normal Linux commands and reserve the LLM as a controlled fallback/adaptive layer, rather than relying on the LLM for every terminal response. Mumbai remains the Beelzebub + local-LLM baseline; Wraith (`us-east-1`, static-shell + telemetry pipeline) is the additive structured-telemetry path documented under `experiments/wraith/` and `reports/`.

## Reproducibility

```bash
# Regenerate a daily report (example: July 3)
python scripts/generate_report.py /path/to/beelzebub/logs --exclude-ip 49.207.63.82 --exclude-ip 49.207.60.111 --exclude-ip 49.207.58.88 --no-geo --out-dir experiments/mumbai --out-file 2026-07-03.md

# Regenerate cumulative report
python scripts/generate_report.py /path/to/beelzebub/logs --all --exclude-ip 49.207.63.82 --exclude-ip 49.207.60.111 --exclude-ip 49.207.58.88 --no-geo --out-dir experiments/mumbai --out-file cumulative.md
```

`--out-file` works for both daily and cumulative modes; `--no-geo` skips `ip-api.com` lookups for offline regeneration. `2026-07-05.md` must remain absent.

## Preservation rule

Do not delete or overwrite the recovered Mumbai reports except via deliberate regeneration from raw logs as documented above.
