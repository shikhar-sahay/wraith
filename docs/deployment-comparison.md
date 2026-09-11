# Deployment Comparison - Mumbai vs US-East

## Experimental context

Two geographically separate, Internet-facing SSH honeypot deployments with different interaction backends were operated under the "Ghost Cloud: LLM Honeypots in AWS" track (`Adaptive SSH Honeypot for Real-World Attack Telemetry Collection on AWS`).

- **Mumbai (`ap-south-1`, `wraith-honeypot`, `t3.micro`, Ubuntu 24.04):** Beelzebub SSH on `2222` with **local LLM-assisted behavior** (Ollama `qwen2.5:0.5b` via `LLMHoneypot` plugin). Intended to evaluate adaptive LLM deception. Period `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z` (24 dated reports + `cumulative.md` in `reports/mumbai/`).

- **US-East (`us-east-1`, `wraith-us-east-static`, historically `100.27.226.37`):** Beelzebub SSH on `2222` fronting the **deterministic Wraith interactive shell** (`wraith/server.py`, `wraith/filesystem.py`, `wraith/telemetry.py` etc., JSONL `wraith_logs/events.jsonl`). Intended to evaluate lightweight deterministic interaction. Period `2026-07-12T18:02:32.608023+00:00` - `2026-09-06T18:14:25.210796+00:00` cumulative, with 14 dated daily reports in `reports/us-east/` (including 4 `N/A` days with 0 sessions after exclusion).

Reports for both deployments were regenerated from surviving logs with researcher test traffic excluded (Mumbai: `49.207.63.82`, `49.207.60.111`, `49.207.58.88`; US-East: those plus `223.187.126.163`, `223.187.121.20`, `1.2.3.4`).

## Comparison table (verified metrics only)

| Dimension | Mumbai Deployment | US-East Wraith Deployment | Directly comparable? |
|-----------|-------------------|---------------------------|----------------------|
| **Deployment name** | Mumbai deployment | US-East Wraith deployment | Yes |
| **AWS region** | `ap-south-1` | `us-east-1` | Yes (different geography) |
| **Backend** | Beelzebub + local Ollama `qwen2.5:0.5b` | Beelzebub + deterministic Wraith shell `wraith/server.py` | Yes (LLM-backed vs deterministic) |
| **Interaction model** | LLM per-command emulation (adaptive) | Deterministic shell with per-session state (`wraith/filesystem.py`, `wraith/session_identity.py`) | Yes |
| **Instance class** | `t3.micro` (Ubuntu 24.04) | `t3.micro` (Ubuntu 24.04) | Yes - both `t3.micro` per `infra/aws-setup.md` and `infra/ec2-configuration.md` |
| **Observation period** | `2026-07-03` - `2026-07-26` (23 days, 24 reports `reports/mumbai/`) | `2026-07-12` - `2026-09-06` (56 days, activity on 8 days, 14 reports `reports/us-east/`) | No - different windows |
| **Primary telemetry source** | Beelzebub raw logs (`Status` `Stateless`/`Start`/`Interaction`, `total_duration`) | Wraith JSONL `wraith_logs/events.jsonl` (`session_started`/`command_executed`/`session_ended`, `latency_ms`) | **No** - different schemas |
| **Unique observed IPs** | 773 unique observed source IPs | 12 unique attacker IPs | Yes, but populations differ (broad scanning vs focused) |
| **Sessions** | 942 | 12 | Yes, but different populations/periods |
| **Login attempts** | 15,153 (`Stateless` events) | Not reported as logins (Wraith counts sessions) | **No** - different counting |
| **Sessions with commands** | 1 (0.11%) | 11 (91.7%) | Yes |
| **Total command events** | 1 | 21103 | Yes, but heavily skewed |
| **Exact unique command strings** | 1 | 18 (whitespace-exact; ~7 semantic patterns) | Yes |
| **Commands/session median** | 0 (all 942, mostly 0) / 1 (bearing) | 52.5 (all 12, sorted `[0,1,1,1,1,42,63,119,133,371,3709,16662]`) / 63 (bearing 11, sorted `[1,1,1,1,42,63,119,133,371,3709,16662]`) | Yes, with denominator noted |
| **Commands/session mean** | ~0.001 (all) / 1 (bearing) | 1758.6 (all, `21103/12`) / 1918.5 (bearing, `21103/11`) | Yes, with denominator noted |
| **Dominant traffic pattern** | Credential scanning (top `AyaKuyaSKRR` 25, `123456` 23) | `echo -e "\x6F\x6B"` 16662 (79.0% of 21103, predominantly `8.217.18.158` single session) + 7-command host discovery battery repeated 9-529 times | Qualitative |
| **Post-auth engagement** | Negligible - 1 session `47.113.113.162` `echo 1 > /dev/null && cat /bin/echo` (6s) | Multiple sessions with reconnaissance (`/bin/./uname`, `uptime -p`, `lspci`, `nvidia-smi`, `df -h`, `hostname`, `nproc`) | Qualitative |
| **Client/tooling indicators** | `SSH-2.0-Go` 13928, `OpenSSH_7.4` 1181, `libssh_0.7.4` 28 (mass scanners) | 4 clients: `SSH-2.0-Go` dominant (9 sessions), `russh_0.51.1` 2, `makiko` 1, `unknown` 1 | Partial - different schemas |
| **Response latency** | Mean 51,094 ms (51 sec), range 451 ms - 3,886,405 ms, 646 LLM calls, 27.7 tokens | Sub-millisecond deterministic measured via `latency_ms` (e.g., `0.03` - `0.12 ms` in session `89c5852b`, `wraith/telemetry.py`) | **No** - LLM inference vs in-memory |
| **Operational behavior** | OOM `llama-server` ~629 MB at `2026-07-26T17:17-17:18Z`, `systemd-journald`/`snapd` watchdog, guest-networking `169.254.169.254` degraded at `17:44`, last recorded honeypot interaction at approximately `17:23:56Z` with external honeypot telemetry ceasing afterward, reboot `2026-09-10` | Deterministic shell stable throughout; separate admin `22` outage (masked `ssh.socket -> /dev/null`, no `ssh.service` boot path) repaired via EBS offline fix with snapshot, honeypot `2222` remained active | Different modes, both operational not attacker-caused |
| **Major failure/recovery event** | Mumbai `t3.micro` resource exhaustion - reboot `2026-09-10` | US-East `ssh.socket` mask - offline EBS repair (see `docs/us-east-recovery.md`) | - |
| **Persistence/state model** | No session persistence beyond Beelzebub `Interaction` logging | Per-session in-memory `wraith/filesystem.py` (`PurePosixPath`), no Redis persistence (planned) | Not comparable |
| **LLM usage** | Local Ollama `qwen2.5:0.5b` per-command, high latency, inconsistent responses, `Rate limit exceeded` | No LLM in production (`wraith/server.py` deterministic); LLM fallback planned as optional adaptive layer (not implemented) | Yes |
| **Primary research takeaway** | Large-scale credential scanning, minimal post-auth, high LLM cost/instability on `t3.micro` | Sustained post-auth reconnaissance with low diversity, high raw volume skewed, lightweight deterministic resilience | Observational |

*If a metric is collected differently between deployments, it is marked as not directly comparable rather than forced to a number.*

## Engagement comparison

- **Mumbai primarily captured credential-scanning behavior.** 773 source IPs and 15,153 login attempts (from `reports/mumbai/cumulative.md`) indicate broad automated password spraying. Only 1 of 942 sessions (0.11%) reached `Interaction` with 1 recorded command, so engagement depth was minimal - a valid result showing the scanning phase dominates Internet SSH exposure for this configuration.

- **US-East captured sustained post-authentication command execution.** 11 of 12 sessions (91.7%) had commands, with 21103 total commands (`reports/us-east/cumulative.md`). However, raw volume overstates diversity.

- **US-East command volume is heavily skewed by automated repeated probes.** `echo -e "\x6F\x6B"` (79.0%, 16662 of 21103, `16662/21103`) is a single repeated command from predominantly one session (`8.217.18.158` `89c5852b` contributed 16662 of that total; this single pattern accounts for 79.0% of all command events, therefore total count is highly skewed). The remaining 7-command resource-discovery battery (`/bin/./uname` nonstandard path, `uptime -p`, `lspci` VGA/3D controller, `nvidia-smi` Product Name pipelines) was repeated 9 times in a 63-command session (`167.71.226.227`) and ~529 times in a 3709-command session (`178.128.36.18`). Removing the large echo loop leaves 4441 commands across the other 11 sessions, still with low diversity: 18 exact unique command strings overall (see `docs/us-east-results.md` skew analysis; most sessions use 1 or 7 distinct patterns). Among all 12 filtered sessions sorted `[0, 1, 1, 1, 1, 42, 63, 119, 133, 371, 3709, 16662]` median is 52.5 and mean is 1758.6 (`21103/12`); among the 11 command-bearing sessions median is 63 and mean is 1918.5 (`21103/11`).

- **Raw command count is not the same as unique or meaningful interaction.** Normalized engagement: Mumbai 1 exact unique command and 1 session; US-East 18 exact unique command strings (whitespace-exact; ~7 semantic patterns) but most volume is repetition of the same 1 or 7 patterns. Both deployments saw limited manual-looking interaction (no `cd`/`ls` navigation, `wget`/`curl` downloads, or `chmod`/`useradd` persistence in Wraith JSONL; Mumbai had no such activity beyond the single echo).

- **Some US-East sessions still demonstrate deeper environment reconnaissance than Mumbai.** The 63-, 119-, 133-, 371-, and 3,709-command sessions show systematic host resource discovery (kernel `uname`, uptime, `lspci` VGA, `nvidia-smi` GPU detection, `df -h`, `hostname`, `nproc`, `free -h`) - more sustained reconnaissance than Mumbai's single `echo 1 > /dev/null && cat /bin/echo`, though still automated and shallow compared to interactive human exploitation.

## Reliability comparison

- **Local LLM inference cost and resource pressure:** Mumbai local `qwen2.5:0.5b` on `t3.micro` incurred mean 51,094 ms latency and ~629 MB RSS, leading to OOM and `systemd-journald`/`snapd` watchdog failures at `2026-07-26T17:17Z` (see `docs/mumbai-incident.md`). US-East deterministic shell latency is sub-millisecond (e.g., 0.03 ms) with negligible memory overhead (`wraith/server.py` in-memory), indicating better efficiency on the same instance class.

- **t3.micro limitations:** Mumbai's failure shows `t3.micro` (~1 GB RAM class) is not suitable for per-connection LLM emulation under sustained Internet load without strict isolation (memory limits, concurrency caps, timeouts). The deterministic shell avoids this class of failure.

- **Deterministic shell efficiency:** Wraith's `wraith/server.py:88` handles 30+ commands deterministically via `wraith/parser.py` and `wraith/filesystem.py` (per-session `PurePosixPath` CRUD), `wraith/privesc.py` `sudo`/`su` simulation, `wraith/network_backend.py` simulated fetch, and `wraith/telemetry.py` append-only JSONL. Tests `tests/test_fake_shell.py` (session context, `mkdir`/`ls`, `sudo` escalation, HTTP `/command`) pass, confirming operational simplicity.

- **Resilience and operational simplicity:** Mumbai external honeypot telemetry ceased after approximately `2026-07-26T17:23:56Z` (last recorded honeypot interaction) following OOM then guest-networking degradation (`169.254.169.254` at `17:44`), requiring reboot `2026-09-10`; US-East honeypot remained operational for 56 days (through `2026-09-06`) despite admin SSH outage, because honeypot `2222` and Wraith services are separate from `ssh.service`. US-East's outage was a boot-configuration error (masked `ssh.socket -> /dev/null`, `ssh.service` not enabled), repaired offline via EBS mount and snapshot (see `docs/us-east-recovery.md`) - also an operational lesson, not a security result.

- **Tradeoff:** LLM offers potential realism for uncovered commands but with high infrastructure overhead and shell-semantic inconsistency (Mumbai `echo -e` inconsistent responses, `Rate limit exceeded`); deterministic shell offers predictable, auditable responses and resilience but requires explicit command coverage (Wraith correctly returns `command not found` for `/bin/./uname`, `uptime` etc., which is accurate for missing binaries but reveals the honeypot is not a full OS).

## Research interpretation

The Mumbai LLM-backed deployment predominantly captured credential-scanning behavior and experienced substantial inference overhead (51 sec mean latency, OOM on `t3.micro`), while the US-East deterministic Wraith deployment captured multiple post-authentication sessions with sustained reconnaissance and command activity (11 sessions, 21103 commands, though 79.0% - 16662/21103 - is one repeated `echo -e` loop from a single session).

**Caveat:** The deployments differed in region (`ap-south-1` vs `us-east-1`), exposure period (23 vs 56 days), implementation (Ollama `qwen2.5:0.5b` per-command emulation vs `wraith/server.py` deterministic), and observed attacker population (773 broad scanners vs 12 focused sessions), so the results should be treated as an **observational comparison rather than a controlled causal experiment**. Differences in geography, time, and attacker population confound any direct causal claim about backend type. No claim is made that deterministic shells are universally better than LLM honeypots, that Wraith definitively caused higher engagement, or that the LLM model itself was solely responsible for Mumbai's lower post-auth interaction.

## Overall Experimental Consensus

### Internet behavior

Both deployments were rapidly discovered by automated SSH activity. The majority of activity was automated rather than clearly human-operated. Credential scanning alone is not equivalent to meaningful post-auth engagement - Mumbai's 15,153 logins produced 1 command, and US-East's 21103 commands were 79.0% one repeated probe.

### Mumbai

Mumbai observed broad credential-scanning activity (773 IPs). Despite high login volume, post-auth engagement was negligible: only one recorded command-bearing session (`47.113.113.162` `echo 1 > /dev/null && cat /bin/echo`) occurred. The LLM-backed design introduced high inference latency (mean 51,094 ms, range 451 - 3,886,405 ms, 646 calls, 27.7 tokens) and substantial resource cost on `t3.micro`. The July 26 OOM/resource event (`llama-server` ~629 MB, `systemd-journald`/`snapd` watchdog, guest-networking `169.254.169.254` degraded) demonstrated an operational limitation of running local LLM inference in this constrained environment.

### US-East

US-East Wraith captured substantially more post-auth command activity within its observed Wraith sessions (11 of 12 sessions, 21103 commands, 18 exact unique strings). However, raw count was highly skewed: 79.0% came from one repeated `echo -e "\x6F\x6B"` probe (`8.217.18.158` single session, see skewed analysis), and only 18 exact command strings were observed. The interesting finding is therefore not `21k commands`. The stronger finding is that several sessions with 63, 119, 133, 371, and 3,709 commands proceeded beyond authentication into repeated host and environment reconnaissance (`/bin/./uname`, `uptime -p`, `lspci`, `nvidia-smi`, `df -h`, `hostname`, `nproc`, `free -h`).

### Architecture

Deterministic shell simulation provided predictable responses, low computational overhead (sub-millisecond `latency_ms` measured, not inferred), controllable fake environment (`wraith/filesystem.py` per-session), structured telemetry (`wraith/telemetry.py`), and resilience against arbitrary LLM output. LLM-backed interaction potentially offers greater flexibility, but the Mumbai implementation demonstrated high latency, inconsistent responses (`command not found`, malformed explanations, `Rate limit exceeded` from `39.105.172.20` loop), resource pressure, and operational instability on `t3.micro`.

### Research conclusion

The two deployments demonstrate differing operational and behavioral characteristics. The US-East Wraith deployment observed substantially deeper post-auth activity than the Mumbai deployment, while the Mumbai LLM-backed deployment exposed significant resource and latency costs. Because the experiments were not controlled equivalents, these observations characterize the deployments rather than establish causal superiority. Geography, observation windows, attacker populations, telemetry/session semantics, and backend implementation all differed, so results should be treated as an observational comparison (see Methodology).

## Showcase Summary

- Built Wraith, a deterministic interactive SSH deception layer (`wraith/server.py`, `wraith/filesystem.py`, `wraith/parser.py`, `wraith/telemetry.py`) integrated with Beelzebub (`deploy/beelzebub_command_plugin.go`, `deploy/beelzebub-simulator.service`)
- Deployed Internet-facing honeypots across Mumbai (`ap-south-1`, `t3.micro`, Beelzebub + local Ollama `qwen2.5:0.5b`) and US-East (`us-east-1`, `100.27.226.37`, Beelzebub + deterministic Wraith)
- Collected real-world SSH login and command telemetry over multi-week observation periods (`2026-07-03` - `2026-07-26` Mumbai 773 IPs, `2026-07-12` - `2026-09-06` US-East 12 IPs) with test traffic excluded and reproducible Markdown reports (`reports/mumbai/`, `reports/us-east/`)
- Compared an LLM-backed interaction architecture against the deterministic Wraith shell (observational, not controlled)
- Observed large-scale credential scanning (Mumbai 15,153 logins), automated reconnaissance, repeated host-capability probing (7-command battery, `echo -e` loops), and command skew (79.0% single loop, 18 unique strings)
- Identified operational limitations of local LLM inference on constrained EC2 resources (51 sec mean latency, OOM, 64.8 min max) and the resilience of lightweight deterministic simulation (sub-millisecond measured)
- Implemented telemetry reporting (`scripts/generate_report.py`, `scripts/generate_report_us_east.py` with `--out-file`/`--no-geo`), experiment isolation (`reports/mumbai/` logs vs `reports/`), recovery procedures (EBS snapshot, `ssh.socket` mask fix), and reproducible documentation (`docs/methodology.md`, `docs/deployment-comparison.md`)

## Practical lessons

- Lightweight deterministic interaction is valuable for resource-constrained deployments (`t3.micro`); per-connection LLM inference without isolation risks OOM.
- LLM-backed honeypots need explicit resource isolation and limits (memory, concurrency, timeout) if used, even with small models like `qwen2.5:0.5b`.
- Telemetry pipelines should separate raw volume from normalized engagement (unique commands, sessions with commands, median per session) and note skew from automated loops (`echo -e` dominates US-East).
- Repeated automated commands should be normalized in analysis (e.g., report both raw 21103 and exact 18 distinct command strings with whitespace-exact counting, and note `8.217.18.158` single-session outlier contributing 79.0% of volume).
- Administrative access (`22` restricted) must remain logically separate from honeypot services (`2222`); US-East honeypot's continuity during admin outage shows correct separation, but boot configuration must be validated (`systemctl is-enabled ssh.service`, no `ssh.socket` mask, `daemon-reload` and reboot test).
- Service boot configuration should be validated after deployment and after any manual systemd changes.
- Backups and reproducible report generation are essential: Mumbai reports regenerated via `scripts/generate_report.py` with `--out-file`/`--no-geo` and test IP exclusion; US-East preserved via EBS snapshot and `scripts/generate_report_us_east.py` with six excluded IPs, `raw-data-us-east/` gitignored, only Markdown reports committed.

## Reproducibility

- **Mumbai:** `scripts/generate_report.py` against surviving Beelzebub logs, excluded `49.207.63.82`, `49.207.60.111`, `49.207.58.88`, daily via `--out-dir` `--out-file`, cumulative via `--all --out-file cumulative.md`.
- **US-East:** `scripts/generate_report_us_east.py` against `wraith_logs/events.jsonl`, excluded six IPs, daily via explicit `--out-file` redirection (because `--out-dir` names by current UTC date), cumulative via `--all` combining `logs*` files from input directory.
- Comparative numbers above are taken directly from committed `reports/mumbai/cumulative.md` and `reports/us-east/cumulative.md` and daily reports; no raw telemetry (`*.jsonl`, `raw-data-us-east/`, `*.tar.gz`) is committed.
