# Video Cheat Sheet - Wraith (One Page)

**Keep beside you while recording. All values verified.**

## Section Order (10-15 min)

A Opening 40s | B Research 40s | C Arch 70s | D Wraith code 90s | E Mumbai 60s | F US-East 60s | G Telemetry 40s | H Behavior 60s | I Comparison 60s | J Mumbai OOM 45s | K US-East recovery 60s | L Findings 45s | M Limitations 30s | N Future 30s | O Walkthrough 80s | P Closing 30s

## Verified Metrics - Mumbai (`ap-south-1`, Beelzebub + Ollama `qwen2.5:0.5b`, `t3.micro` Ubuntu 24.04)

- Period: `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z` (24+1 reports `reports/mumbai/`), `2026-07-01` validation 0/0 +6 LLM calls
- 773 unique observed source IPs, 942 sessions, 15,153 login attempts (`Stateless`), 1 session with commands (0.11%), 1 recorded command (`47.113.113.162` `russh_0.51.1` `echo 1 > /dev/null && cat /bin/echo` 6s), 646 LLM calls, mean 51,094 ms (51 sec), range 451 - 3,886,405 ms, 27.7 tokens, excluded `49.207.63.82` etc.

## Verified Metrics - US-East (`us-east-1`, `100.27.226.37`, Beelzebub + Wraith deterministic `wraith/server.py`)

- Period: `2026-07-12` - `2026-09-06` (14 daily + `cumulative.md` `reports/us-east/`), 12 filtered sessions, 11 with commands (91.7%), 21103 total commands, 18 exact unique command strings (whitespace-exact), 4 clients (`Go` dominant)
- Per-session all 12 sorted `[0,1,1,1,1,42,63,119,133,371,3709,16662]` median 52.5 mean 1758.6 (`21103/12`); bearing 11 sorted `[1,1,1,1,42,63,119,133,371,3709,16662]` median 63 mean 1918.5 (`21103/11`); min 0 max 16662 min bearing 1
- Dominant: `echo -e "\x6F\x6B"` 16662 of 21103 = 79.0% (16662/21103, single repeated command) from predominantly one session `8.217.18.158` `89c5852b`; remaining 7-command battery (`/bin/./uname`, `uptime -p`, `lspci VGA/3D`, `nvidia-smi`) repeated 9-529 times; `df -h` etc. 6 each plus three low-frequency strings (one observed twice: `echo 1 > /dev/null && cat /bin/echo` (2), and two singletons: `echo 1 && cat /bin/echo` (1) and the `bash --help` composite (1)); excluded 6 IPs
- Measured deterministic command responses in the available telemetry were sub-millisecond (approximately 0.03-0.12 ms in the measured sample, e.g., session `89c5852b` via `wraith/telemetry.py` `latency_ms`), not inferred and not generalized to every command/session without evidence

## Never Confuse

- 21,103 raw command events vs 18 exact unique strings vs ~7 semantic patterns
- 16,662 repeated echo loop (single session) vs diverse interaction
- Daily total 1877 (2026-08-04 single session) vs per-session list (verified list has no 1877 as filtered per-session; 1877 is daily total)
- 773 IPs != 773 human attackers (automated scanners)
- `Stateless` logins (Mumbai) vs `session_started` sessions (US-East) - not directly comparable
- Observational comparison, not controlled A/B (different regions ap-south-1 vs us-east-1, periods 23 vs 56 days, populations: Mumbai 773 source IPs from broad Beelzebub telemetry vs US-East 12 filtered Wraith sessions, backends, telemetry semantics - not directly comparable)

## Do Not Claim -> Correct Wording

- "Wraith proved deterministic is better" -> "Observed behavior differed substantially; US-East observed deeper post-auth than Mumbai, but experiments were not controlled equivalents, so not causal superiority"
- "21,103 unique commands" -> "21,103 command events, 18 exact unique strings, ~7 patterns, 79.0% one loop"
- "21,103 meaningful interactions" -> "11 sessions with commands, median 63 bearing, heavily skewed"
- "Mumbai server crashed / EC2 stopped July 26" -> "Resource exhaustion OOM killed llama-server ~629 MB 17:17, Beelzebub alive until last honeypot interaction ~17:23:56Z, guest-networking 169.254.169.254 degraded ~17:44, external telemetry ceased, reboot Sep 10, OS not crashed"
- "Redis persistence was implemented" -> "Per-session in-memory `wraith/filesystem.py` only, no Redis (planned, persona.py lists redis service name only)"
- "Production LLM fallback existed" -> "Deterministic `wraith/server.py` 30+ commands, no LLM in production; LLM fallback planned as optional hybrid (Mumbai used per-command Ollama)"
- "Both deployments were controlled A/B" -> "Observational comparison, different regions/periods/populations, not controlled"
- "773 human attackers" -> "773 unique observed source IPs (automated scanners, Go/OpenSSH_7.4/libssh)"
- "ssh.socket mask was caused by attacker" -> "Masked ssh.socket -> /dev/null and no ssh.service boot path - operational boot-configuration error, not attacker, honeypot 2222 remained active"

## Best Code to Show (one sentence each)

- `wraith/server.py:88` `handle_command` - 30+ deterministic handlers (`pwd` -> cwd, `whoami` -> user), predictable vs LLM inconsistent
- `wraith/filesystem.py:9` `FakeFilesystem` `PurePosixPath` per-session isolated, `mkdir`/`ls`/`cat` - files disappear after session
- `wraith/parser.py:16` `CommandParser.parse` shlex - correct `echo -e` verbatim handling
- `wraith/telemetry.py:9` `TelemetryLogger` append-only `events.jsonl` `session_started`/`command_executed`/`session_ended`
- `wraith/privesc.py:7` + `server.py:237` `sudo` flow to `root@db-prod-01`
- `deploy/beelzebub_command_plugin.go:1` - Beelzebub -> Wraith HTTP `/command` bridge
- `run_server.py:1` `start_http_server 127.0.0.1:8080` - local server

## Safe Demo Commands (use only these, all supported)

```bash
git status
git log --oneline -12
python -m unittest tests/test_fake_shell.py -v
python -m py_compile scripts/generate_report.py scripts/generate_report_us_east.py
python demo_fake_shell.py  # shows Wraith locally: whoami, pwd, mkdir, ls, sudo
```

**Fake-shell sequence (verified against `wraith/server.py:88` and `wraith/filesystem.py:9`, only supported commands, state-consistent):**
`whoami` -> `admin` (user `admin`); `pwd` -> `/home/admin` (cwd); `mkdir /tmp/demo` -> `mkdir: created directory '/tmp/demo'` (creates per-session dir, visible via `ls /tmp`); `ls /tmp` -> `demo` (shows per-session state); `cd /tmp/demo` -> (no output, cwd changes to `/tmp/demo`); `pwd` -> `/tmp/demo` (verifies `cd`); `cat /etc/os-release` -> `PRETTY_NAME="Ubuntu 22.04 LTS"` (file exists per `filesystem.py:26`); `uname -a` -> `Linux db-prod-01 5.15.0-105-generic ...` (`server.py:109`); `sudo whoami` -> `[sudo] password for admin:` then `root@db-prod-01:~#` after second attempt (`privesc.py:7`). Note: `touch demo.txt` creates `/demo.txt` (not visible via `ls` due to `filesystem.py` not adding to parent), so use `mkdir`/`ls /tmp` to demonstrate state change, not `touch`+`ls`.

## Best Attacker Examples (source file, why, what not to infer)

- Mumbai single `echo 1 > /dev/null && cat /bin/echo` from `47.113.113.162` `reports/mumbai/cumulative.md` - only post-auth, shows scanning dominates, not diverse
- US-East `echo -e "\x6F\x6B"` 16662 from `8.217.18.158` `reports/us-east/cumulative.md` - liveness check, high volume not engagement, 79.0% skew
- US-East 7-command battery `167.71.226.227` 63 cmds `reports/us-east/cumulative.md` - host resource discovery (uname, uptime, lspci, nvidia-smi), automated 9 iterations, not manual

## Comparison One-Liners (for table)

- Traffic volume: Mumbai observed broad credential-scanning traffic from 773 source IPs (15,153 logins), while the filtered US-East Wraith dataset contained 12 sessions, 11 of which executed commands (different counting: Beelzebub Stateless logins vs Wraith session_started)
- Engagement: Mumbai 1/942 (0.11%) vs US-East 11/12 (91.7%) but US-East heavily skewed
- Command diversity: Mumbai 1 vs US-East 18 exact (7 patterns)
- Latency: Mumbai 51 sec mean (646 calls) vs US-East sub-ms measured 0.03-0.12 ms
- Resource cost: Mumbai OOM ~629 MB t3.micro vs Wraith negligible in-memory
- Reliability: Mumbai guest-networking degraded, US-East ssh.socket mask separate
- Statefulness: Both per-session, no Redis, Wraith per-session filesystem
- Recovery: Mumbai Sep 10 reboot, US-East EBS snapshot helper

## Incident Narrations (verbatim)

**Mumbai 45s:** "Around 17:17 resource pressure from local Ollama triggered OOM, kernel killed llama-server ~629 MB, systemd-journald/snapd watchdog stressed, Beelzebub stayed alive until last honeypot interaction around 17:23:56Z, then guest networking for 169.254.169.254 degraded around 17:44, external telemetry ceased, not a full EC2 crash, recovered September 10 reboot."

**US-East 60s:** "Port 2222 honeypot stayed up while admin 22 was refused; EC2 Instance Connect and SSM failed, serial console showed login. Root cause was masked ssh.socket pointing to /dev/null and ssh.service with no boot activation. Fix was EBS snapshot, stop instance, detach root volume, attach to helper in same AZ, remove mask, enable ssh.service, reattach, boot, verify 22 and Beelzebub/Wraith active."

## Key Links for Walkthrough

`README.md` Quick Links -> `docs/architecture-notes.md` -> `wraith/server.py:88` -> `wraith/filesystem.py:9` -> `wraith/telemetry.py:9` -> `reports/mumbai/cumulative.md` Summary -> `reports/us-east/cumulative.md` Summary -> `docs/deployment-comparison.md` table -> `docs/mumbai-incident.md` + `docs/us-east-recovery.md` -> `tests/test_fake_shell.py`

## Closing Takeaway (30s)

"I built Wraith deterministic shell with Beelzebub, deployed Mumbai LLM-backed (ap-south-1, 2026-07-03 - 2026-07-26) and US-East deterministic (us-east-1, 2026-07-12 - 2026-09-06), observed Mumbai showed broad credential scanning with very little post-auth interaction, while the US-East Wraith dataset captured multiple command-bearing reconnaissance sessions (11 of 12 sessions), learned deterministic is lightweight and resilient while local LLM on t3.micro is costly, with observational limitations and future hybrid work. All reports, methodology, and recovery are documented and reproducible."

## Video Titles (10 options)

1. Wraith: Building and Evaluating an Adaptive SSH Honeypot on AWS
2. Wraith: Real-World SSH Attack Telemetry with Deterministic and LLM-Backed Honeypots
3. Ghost Cloud - LLM Honeypots in AWS: Mumbai and US-East Deployments Compared
4. Adaptive SSH Honeypots: Deterministic Wraith vs Local LLM on t3.micro
5. Collecting Real-World SSH Telemetry with Beelzebub and Wraith
6. From Credential Scanning to Command Loops: Analyzing SSH Honeypot Data
7. Operational Lessons from Internet-Facing SSH Honeypots on AWS
8. Deterministic vs LLM-Backed SSH Deception: An Observational Comparison
9. Wraith: A Lightweight Deterministic Shell for SSH Honeypots
10. SSH Honeypot Telemetry: Mumbai and US-East Experiments with Wraith

## Files to Open On Screen (no secrets)

- `README.md:1` overview + Quick Links
- `docs/architecture-notes.md:1` model + `wraith/server.py:88`
- `reports/mumbai/cumulative.md:1` Summary 773/1
- `reports/us-east/cumulative.md:1` Summary 12/21103 + 18
- `docs/deployment-comparison.md:13` table
- `docs/README.md` index
- Terminal: `git log --oneline -12`, `python -m unittest -v`, `demo_fake_shell.py` (blur IPs if needed, no private keys)
