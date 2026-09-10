# Mumbai Deployment - Results Analysis

## Deployment context

- **Region:** `ap-south-1` (Mumbai), instance `wraith-honeypot` (`t3.micro`, Ubuntu 24.04)
- **Framework:** Beelzebub SSH on port `2222` (Internet-facing), admin `22` restricted to operator IP
- **LLM backend:** Local Ollama `qwen2.5:0.5b` via Beelzebub `LLMHoneypot` plugin (internal `11434`)
- **SSH honeypot configuration:** Beelzebub compiled from source, `LLMHoneypot` enabled, `qwen2.5:0.5b` model installed, dynamic LLM responses verified before exposure
- **Observation period:** `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z` (attacker telemetry); `2026-07-01` is validation-only (0 IPs, 0 sessions, 0 logins, 6 LLM calls, period `N/A`)
- **Known excluded test traffic:** `49.207.63.82`, `49.207.60.111`, `49.207.58.88` (researcher-controlled, excluded via `excluded_ips` in `scripts/generate_report.py`)
- **Reporting methodology:** Surviving Beelzebub JSONL logs parsed via `scripts/generate_report.py` (`extract_sessions` `Stateless`/`Start`/`Interaction`, `extract_llm_stats` on `total_duration`); daily reports `experiments/mumbai/2026-07-*.md` (24 files, `2026-07-05.md` intentionally absent - stale without source, `07-02` no source), cumulative `experiments/mumbai/cumulative.md` via `--all --out-file cumulative.md` with `--no-geo` for offline regeneration

## Verified cumulative metrics (source: `experiments/mumbai/cumulative.md`, test traffic excluded)

| Metric | Value |
|--------|-------|
| Unique observed source IPs | 773 |
| Total sessions | 942 |
| Login attempts (credential guesses) | 15,153 |
| Sessions with commands | 1 |
| Total commands executed | 1 |
| Average LLM response latency | 51,094 ms |
| Average tokens generated | 27.7 |
| Total LLM calls | 646 |
| Observation period | 2026-07-03T18:59:13Z - 2026-07-26T17:23:56Z |

**Daily activity pattern (selected):**

- `2026-07-01`: 0 IPs, 0 sessions, 0 logins, 6 LLM calls - validation
- `2026-07-03`: 2 IPs, 22 sessions, 598 logins - first Internet traffic
- Daily reports `2026-07-06` - `2026-07-26` show sustained scanning (hundreds of logins per day, early-July burst >12k not in Mumbai but consistent volume)
- `2026-07-26`: last day, 71 IPs, 285 sessions, 405 logins, 0 commands (but includes 285 sessions from `39.105.172.20` `echo -e` loop before outage)

**Post-authentication session:**

- **IP:** `47.113.113.162`, **Client:** `SSH-2.0-russh_0.51.1`, **Session:** `7bb45dfc` (6s duration)
- **Command:** `echo 1 > /dev/null && cat /bin/echo` (response `1`, recorded in `cumulative.md` `Commands Executed` and `Session Details`)
- This is the sole recorded command execution across 942 sessions (0.11% of sessions).

## Behavioral interpretation

- **Credential scanning volume:** 15,153 login attempts from 773 source IPs, dominated by `SSH-2.0-Go` (13,928 in cumulative `SSH Client Versions`) and `SSH-2.0-OpenSSH_7.4` (1,181), with `SSH-2.0-libssh_0.7.4` (28) - automated mass scanners and credential-guessing, consistent with `Credentials Attempted` table (top: `AyaKuyaSKRR` 25, `123456` 23, etc., long tail of dictionary passwords).

- **Post-authentication engagement:** Extremely limited - 1 session, 1 command. The deployment captured the scanning/credential-guessing phase, not meaningful shell interaction. This is a valid research result, not a reporting artifact (Beelzebub `Interaction` events correctly captured where they occurred).

- **LLM response behavior:** On `t3.micro` local `qwen2.5:0.5b`, mean latency 51,094 ms (51 seconds), fastest 451 ms, slowest 3,886,405 ms (64 minutes) - shows extreme variance and overhead. Average 27.7 tokens per call, 646 calls total. Latency and OOM together indicate `qwen2.5:0.5b` was not operationally reliable on this configuration under sustained Internet exposure (`docs/mumbai-incident.md`).

- **Latency and rate-limiting observations:** `docs/mumbai-incident.md` notes `Rate limit exceeded` and `plugin "LLMHoneypot" execute error: rate limited` from `39.105.172.20` `echo -e "\x6F\x6B"` loop (285 sessions on 2026-07-26). Responses were inconsistent (`command not found`, malformed explanations, escaped Unicode) - limitation of unconstrained LLM terminal emulation, not outage cause.

- **Operational reliability:** Local inference on `t3.micro` (~1 GB RAM class) proved fragile: ~629 MB RSS `llama-server` killed by OOM, `systemd-journald`/`snapd` watchdog failures, then guest-networking degraded (`169.254.169.254` unreachable, DNS `127.0.0.53` failure, SSM unreachable). See `docs/mumbai-incident.md` for precise sequence: Beelzebub stayed alive until `2026-07-26T17:23:56Z`, cron/sysstat continued, resource exhaustion then networking degradation - not a simple crash.

- **Suitability:** For this `t3.micro` configuration, pure LLM emulation for every shell interaction is not suitable for sustained Internet-facing deployment due to latency, memory pressure, and shell-semantic inconsistency. This directly motivates Wraith's hybrid: deterministic shell semantics first, optional controlled LLM assistance (`wraith/server.py` deterministic, LLM fallback planned not production).

## Limitations

- Single-command dataset limits conclusions about engagement depth or session persistence; characterizes scanning phase only.
- No geographic/human-actor attribution beyond source IPs/client strings; 773 source addresses are not 773 distinct human attackers.
- Observations are specific to this Mumbai `t3.micro` `qwen2.5:0.5b` configuration and exposure period; not generalizable to all LLM honeypots.
