# Deployment Comparison - Mumbai vs US-East

## Experimental context

Two geographically separate, Internet-facing SSH honeypot deployments with different interaction backends were operated under the "Ghost Cloud: LLM Honeypots in AWS" track (`Adaptive SSH Honeypot for Real-World Attack Telemetry Collection on AWS`).

- **Mumbai (`ap-south-1`, `wraith-honeypot`, `t3.micro`, Ubuntu 24.04):** Beelzebub SSH on `2222` with **local LLM-assisted behavior** (Ollama `qwen2.5:0.5b` via `LLMHoneypot` plugin). Intended to evaluate adaptive LLM deception. Period `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z` (24 dated reports + `cumulative.md` in `experiments/mumbai/`).

- **US-East (`us-east-1`, `wraith-us-east-static`, historically `100.27.226.37`):** Beelzebub SSH on `2222` fronting the **deterministic Wraith interactive shell** (`wraith/server.py`, `wraith/filesystem.py`, `wraith/telemetry.py` etc., JSONL `wraith_logs/events.jsonl`). Intended to evaluate lightweight deterministic interaction. Period `2026-07-12T18:02:32.608023+00:00` - `2026-09-06T18:14:25.210796+00:00` cumulative, with 14 dated daily reports in `reports/us-east/` (including 4 `N/A` days with 0 sessions after exclusion).

Reports for both deployments were regenerated from surviving logs with researcher test traffic excluded (Mumbai: `49.207.63.82`, `49.207.60.111`, `49.207.58.88`; US-East: those plus `223.187.126.163`, `223.187.121.20`, `1.2.3.4`).

## Comparison table (verified metrics only)

| Dimension | Mumbai (`ap-south-1`) | US-East (`us-east-1`) | Directly comparable? |
|-----------|------------------------|------------------------|----------------------|
| **AWS region** | `ap-south-1` | `us-east-1` | Yes (different geography) |
| **Experiment period** | `2026-07-03` - `2026-07-26` (23 days, 24 reports) | `2026-07-12` - `2026-09-06` (56 days, activity on 8 days) | No - different exposure windows |
| **Interaction backend** | Local Ollama `qwen2.5:0.5b` per-command LLM emulation | Deterministic Wraith shell (`wraith/server.py:88` 30+ commands) | Yes (design difference) |
| **Unique attacker/source IPs** | 773 unique observed source IPs | 12 unique attacker IPs | Yes, but populations differ (Mumbai saw broad scanning, US-East saw focused sessions) |
| **Total SSH/login activity** | 15,153 login attempts (`Stateless` events) + 942 sessions | 12 total sessions (Wraith JSONL counts sessions, not individual password guesses) | **No** - different counting (Mumbai Beelzebub `Stateless` vs Wraith `session_started`) |
| **Total sessions** | 942 | 12 | Yes, but different honeypot populations and periods |
| **Sessions with post-auth commands** | 1 (0.11%) | 11 (91.7%) | Yes |
| **Raw command count** | 1 | 21103 | Yes, but heavily skewed (see engagement) |
| **Unique SSH clients** | Not directly reported as `Unique clients` (SSH Client Versions: `SSH-2.0-Go` 13928, `OpenSSH_7.4` 1181, etc.) | 4 (`SSH-2.0-Go` dominant, `SSH-2.0-russh_0.51.1`, `SSH-2.0-makiko`, `unknown`) | Partial - different report schemas |
| **Response latency** | Mean 51,094 ms (51 sec), range 451 ms - 3,886,405 ms, 646 LLM calls | Sub-millisecond deterministic (e.g., `0.03` - `0.12 ms` in session `89c5852b`) | No - different measurement (LLM inference vs in-memory) |
| **Operational stability** | OOM on `t3.micro` killed `llama-server` (~629 MB RSS) at `2026-07-26T17:17-17:18Z`, guest-networking degraded `169.254.169.254` at `17:44`, telemetry stopped `17:23:56Z`, reboot `2026-09-10` | Deterministic shell remained stable; separate admin SSH outage due to masked `ssh.socket -> /dev/null` and disabled `ssh.service`, repaired via EBS offline fix with snapshot | Different failure modes, both operational not attacker-caused |
| **Major observed attacker behavior** | Credential scanning (top passwords `AyaKuyaSKRR` 25, `123456` 23), single `echo 1 > /dev/null && cat /bin/echo` from `47.113.113.162` `russh_0.51.1`, pre-outage `echo -e "\x6F\x6B"` loop from `39.105.172.20` with inconsistent LLM responses and `Rate limit exceeded` | Sustained post-auth loops: `echo -e "\x6F\x6B"` 16662 (78.9% of total, `8.217.18.158`), 7-command host discovery battery (`/bin/./uname -s -v -n -r -m`, `uptime -p`, `lspci | grep VGA`..., `nvidia-smi` pipelines) repeated 9-529 times, `df -h`, `hostname`, `nproc` etc. | Qualitative, not causal |
| **Notable failure mode** | Resource exhaustion from LLM inference on `t3.micro` | Masked `ssh.socket` disabling admin SSH boot activation | - |

*If a metric is collected differently between deployments, it is marked as not directly comparable rather than forced to a number.*

## Engagement comparison

- **Mumbai primarily captured credential-scanning behavior.** 773 source IPs and 15,153 login attempts (from `experiments/mumbai/cumulative.md`) indicate broad automated password spraying. Only 1 of 942 sessions (0.11%) reached `Interaction` with 1 recorded command, so engagement depth was minimal - a valid result showing the scanning phase dominates Internet SSH exposure for this configuration.

- **US-East captured sustained post-authentication command execution.** 11 of 12 sessions (91.7%) had commands, with 21103 total commands (`reports/us-east/cumulative.md`). However, raw volume overstates diversity.

- **US-East command volume is heavily skewed by automated repeated probes.** `echo -e "\x6F\x6B"` (78.9%, 16662) is a single-command liveness check loop in one session (`8.217.18.158` `89c5852b`). The remaining 7-command resource-discovery battery (`/bin/./uname` nonstandard path, `uptime -p`, `lspci` VGA/3D controller, `nvidia-smi` Product Name pipelines) was repeated 9 times in a 63-command session (`167.71.226.227`) and ~529 times in a 3709-command session (`178.128.36.18`). Removing the large echo loop leaves 4441 commands across 11 sessions, still with low unique command diversity (~20 distinct strings, most sessions use 1 or 7 distinct commands, median 91, mean 1758 skewed).

- **Raw command count is not the same as unique or meaningful interaction.** Normalized engagement: Mumbai 1 unique command and 1 session; US-East ~20 unique commands but most are repetitions of the same 7. Both deployments saw limited manual-looking interaction (no `cd`/`ls` navigation, `wget`/`curl` downloads, or `chmod`/`useradd` persistence in Wraith JSONL; Mumbai had no such activity beyond the single echo).

- **Some US-East sessions still demonstrate deeper environment reconnaissance than Mumbai.** The 63-, 119-, 504-, 3709-, and 1877-command sessions show systematic host resource discovery (kernel `uname`, uptime, `lspci` VGA, `nvidia-smi` GPU detection, `df -h`, `hostname`, `nproc`, `free -h`) - more sustained reconnaissance than Mumbai's single `echo 1 > /dev/null && cat /bin/echo`, though still automated and shallow compared to interactive human exploitation.

## Reliability comparison

- **Local LLM inference cost and resource pressure:** Mumbai local `qwen2.5:0.5b` on `t3.micro` incurred mean 51,094 ms latency and ~629 MB RSS, leading to OOM and `systemd-journald`/`snapd` watchdog failures at `2026-07-26T17:17Z` (see `docs/mumbai-incident.md`). US-East deterministic shell latency is sub-millisecond (e.g., 0.03 ms) with negligible memory overhead (`wraith/server.py` in-memory), indicating better efficiency on the same instance class.

- **t3.micro limitations:** Mumbai's failure shows `t3.micro` (~1 GB RAM class) is not suitable for per-connection LLM emulation under sustained Internet load without strict isolation (memory limits, concurrency caps, timeouts). The deterministic shell avoids this class of failure.

- **Deterministic shell efficiency:** Wraith's `wraith/server.py:88` handles 30+ commands deterministically via `wraith/parser.py` and `wraith/filesystem.py` (per-session `PurePosixPath` CRUD), `wraith/privesc.py` `sudo`/`su` simulation, `wraith/network_backend.py` simulated fetch, and `wraith/telemetry.py` append-only JSONL. Tests `tests/test_fake_shell.py` (session context, `mkdir`/`ls`, `sudo` escalation, HTTP `/command`) pass, confirming operational simplicity.

- **Resilience and operational simplicity:** Mumbai telemetry stopped at `2026-07-26T17:23:56Z` due to OOM then guest-networking degradation (`169.254.169.254` at `17:44`), requiring reboot `2026-09-10`; US-East honeypot remained operational for 56 days (through `2026-09-06`) despite admin SSH outage, because honeypot `2222` and Wraith services are separate from `ssh.service`. US-East's outage was a boot-configuration error (masked `ssh.socket -> /dev/null`, `ssh.service` not enabled), repaired offline via EBS mount and snapshot (see `docs/us-east-recovery.md`) - also an operational lesson, not a security result.

- **Tradeoff:** LLM offers potential realism for uncovered commands but with high infrastructure overhead and shell-semantic inconsistency (Mumbai `echo -e` inconsistent responses, `Rate limit exceeded`); deterministic shell offers predictable, auditable responses and resilience but requires explicit command coverage (Wraith correctly returns `command not found` for `/bin/./uname`, `uptime` etc., which is accurate for missing binaries but reveals the honeypot is not a full OS).

## Research interpretation

The Mumbai LLM-backed deployment predominantly captured credential-scanning behavior and experienced substantial inference overhead (51 sec mean latency, OOM on `t3.micro`), while the US-East deterministic Wraith deployment captured multiple post-authentication sessions with sustained reconnaissance and command activity (11 sessions, 21103 commands, though 78.9% is a single automated loop).

**Caveat:** The deployments differed in region (`ap-south-1` vs `us-east-1`), exposure period (23 vs 56 days), implementation (Ollama `qwen2.5:0.5b` per-command emulation vs `wraith/server.py` deterministic), and observed attacker population (773 broad scanners vs 12 focused sessions), so the results should be treated as an **observational comparison rather than a controlled causal experiment**. Differences in geography, time, and attacker population confound any direct causal claim about backend type. No claim is made that deterministic shells are universally better than LLM honeypots, that Wraith definitively caused higher engagement, or that the LLM model itself was solely responsible for Mumbai's lower post-auth interaction.

## Practical lessons

- Lightweight deterministic interaction is valuable for resource-constrained deployments (`t3.micro`); per-connection LLM inference without isolation risks OOM.
- LLM-backed honeypots need explicit resource isolation and limits (memory, concurrency, timeout) if used, even with small models like `qwen2.5:0.5b`.
- Telemetry pipelines should separate raw volume from normalized engagement (unique commands, sessions with commands, median per session) and note skew from automated loops (`echo -e` dominates US-East).
- Repeated automated commands should be normalized in analysis (e.g., report both raw 21103 and de-duplicated ~20 distinct, and note `8.217.18.158` outlier).
- Administrative access (`22` restricted) must remain logically separate from honeypot services (`2222`); US-East honeypot's continuity during admin outage shows correct separation, but boot configuration must be validated (`systemctl is-enabled ssh.service`, no `ssh.socket` mask, `daemon-reload` and reboot test).
- Service boot configuration should be validated after deployment and after any manual systemd changes.
- Backups and reproducible report generation are essential: Mumbai reports regenerated via `scripts/generate_report.py` with `--out-file`/`--no-geo` and test IP exclusion; US-East preserved via EBS snapshot and `scripts/generate_report_us_east.py` with six excluded IPs, `raw-data-us-east/` gitignored, only Markdown reports committed.

## Reproducibility

- **Mumbai:** `scripts/generate_report.py` against surviving Beelzebub logs, excluded `49.207.63.82`, `49.207.60.111`, `49.207.58.88`, daily via `--out-dir` `--out-file`, cumulative via `--all --out-file cumulative.md`.
- **US-East:** `scripts/generate_report_us_east.py` against `wraith_logs/events.jsonl`, excluded six IPs, daily via explicit `--out-file` redirection (because `--out-dir` names by current UTC date), cumulative via `--all` combining `logs*` files from input directory.
- Comparative numbers above are taken directly from committed `experiments/mumbai/cumulative.md` and `reports/us-east/cumulative.md` and daily reports; no raw telemetry (`*.jsonl`, `raw-data-us-east/`, `*.tar.gz`) is committed.
