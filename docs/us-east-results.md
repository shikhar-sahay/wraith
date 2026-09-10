# US-East Wraith Deployment - Results Analysis

## Deployment context

- **Region:** `us-east-1` (Virginia), instance `wraith-us-east-static` (historically `100.27.226.37`)
- **Honeypot framework:** Beelzebub SSH layer on port `2222` fronting the Wraith deterministic shell
- **Wraith shell:** Local Python implementation in `wraith/` (`server.py`, `filesystem.py`, `parser.py`, `session_identity.py`, `persona.py`, `privesc.py`, `registry.py`, `telemetry.py`) - deterministic responses, per-session in-memory filesystem, seeded persona variation
- **Relationship:** Beelzebub accepts the SSH session and forwards commands to `wraith/server.py` via HTTP `/command` (`run_server.py` on `127.0.0.1:8080`); Beelzebub integration via `deploy/beelzebub_command_plugin.go` and `deploy/beelzebub-simulator.patch`
- **Experiment timeframe:** Reports cover `2026-07-12` through `2026-09-07` on days with Wraith activity; cumulative period `2026-07-12T18:02:32.608023+00:00` - `2026-09-06T18:14:25.210796+00:00` (cumulative report excludes `2026-09-07` due to its `N/A` period handling; see daily reports)
- **Data represented:** JSONL application telemetry (`wraith_logs/events.jsonl`) with `session_started`, `command_executed` (fields: `attacker_ip`, `client`, `command`, `response`, `cwd`, `latency_ms`, `timestamp`), and `session_ended`; reports generated via `scripts/generate_report_us_east.py`
- **Known test traffic excluded:** `49.207.63.82`, `49.207.60.111`, `49.207.58.88`, `223.187.126.163`, `223.187.121.20`, `1.2.3.4` (researcher-controlled and synthetic test addresses). Exclusion is applied at session level in `extract_sessions`.

## Verified cumulative metrics (source: `reports/us-east/cumulative.md`, test traffic excluded)

| Metric | Value |
|--------|-------|
| Unique attacker IPs | 12 |
| Total sessions | 12 |
| Sessions with commands | 11 |
| Total commands executed | 21103 |
| Unique SSH clients | 4 |
| Observation period (cumulative) | 2026-07-12T18:02:32.608023+00:00 - 2026-09-06T18:14:25.210796+00:00 |
| Daily reports on disk | 15 files (including `cumulative.md`; 14 dated daily reports) |

**Daily breakdown (from committed daily reports):**

| Date | IPs | Sessions | Commands | Note |
|------|-----|----------|----------|------|
| 2026-07-12 | 1 | 1 | 0 | `unknown` IP/client, no commands |
| 2026-07-13 | 0 | 0 | 0 | `N/A` period, no activity |
| 2026-07-14 | 0 | 0 | 0 | `N/A` period |
| 2026-07-17 | 0 | 0 | 0 | `N/A` period |
| 2026-07-19 | 0 | 0 | 0 | `N/A` period |
| 2026-07-25 | 1 | 1 | 63 | Single reconnaissance loop |
| 2026-07-28 | 1 | 1 | 1 | Single probe |
| 2026-08-04 | 1 | 1 | 1877 | Includes large echo loop |
| 2026-08-05 | 3 | 3 | 14905 | Largest day; 14785 from `8.217.18.158` echo loop + 119 from `159.223.186.191` |
| 2026-08-07 | 2 | 2 | 2 | Two single-command sessions |
| 2026-08-23 | 2 | 2 | 504 | Two sessions |
| 2026-08-25 | 1 | 1 | 42 | Single session |
| 2026-09-06 | 1 | 1 | 3681 | Includes 3709-command session from `178.128.36.18` (report period truncated at 06th) |
| 2026-09-07 | 1 | 1 | 28 | `N/A` period, not in cumulative period; `178.128.36.18` again, 15/13 uname/uptime loop |

**Attacking IPs (cumulative):**

| IP | Sessions | Commands | Client |
|----|----------|----------|--------|
| 8.217.18.158 | 1 | 16662 | SSH-2.0-Go |
| 178.128.36.18 | 1 | 3709 | SSH-2.0-Go |
| 159.89.188.217 | 1 | 371 | SSH-2.0-Go |
| 159.223.186.191 | 1 | 119 | SSH-2.0-Go |
| 167.71.226.227 | 1 | 63 | SSH-2.0-Go |
| 221.131.139.70 | 1 | 42 | SSH-2.0-Go |
| 157.230.53.146 | 1 | 133 | SSH-2.0-Go |
| 159.203.181.169 | 1 | 1 | SSH-2.0-russh_0.51.1 |
| 192.42.116.47 | 1 | 1 | SSH-2.0-Go |
| 47.238.161.58 | 1 | 1 | SSH-2.0-makiko |
| 8.217.177.33 | 1 | 1 | SSH-2.0-russh_0.51.1 |
| unknown | 1 | 0 | unknown |

**Command distribution (cumulative, top):**

| Command | Count | Share |
|---------|-------|-------|
| `echo -e "\x6F\x6B"` | 16662 | 78.9% |
| `/bin/./uname -s -v -n -r -m` | 687 | 3.3% |
| `uptime -p` | 685 | 3.2% |
| `lspci | grep VGA | cut -f5- -d ' '` | 668 | 3.2% |
| `lspci | grep VGA -c` | 620 | 2.9% |
| `nvidia-smi -q | grep "Product Name" | head -n 1 | awk ...` | 579 | 2.7% |
| `lspci | grep "3D controller" | cut -f5- -d ' '` | 578 | 2.7% |
| `nvidia-smi -q | grep "Product Name" | awk ... | grep . -c` | 578 | 2.7% |

Remaining commands (6 occurrences each): `df -h`, `hostname`, `ssh -V`, `nproc`, `uname -a`, `free -h | grep Mem`, `echo 'bash_test_12345' && echo 'second_line'`; two singletons plus two variants of `echo 1 > /dev/null && cat /bin/echo`.

**Dominant source:** `8.217.18.158` (SSH-2.0-Go) contributes 16662 of 21103 commands (78.9%) in a single session `89c5852b` that consists entirely of the `echo -e "\x6F\x6B"` loop. Removing this loop leaves 4441 commands across the other 11 sessions.

## Behavioral analysis

- **Repeated `echo -e "\x6F\x6B"` probes:** The clear automation signal. Appears as a liveness or shell-capability check (hex `0x6F 0x6B` decodes to ASCII `ok`). In Wraith it returns `-e \x6F\x6B` (deterministic `echo` handling in `wraith/server.py:224` joins args verbatim). High-volume loops (16662 in one session, 14785 on 2026-08-05) indicate scripted validation, not manual exploration. Do not equate this volume with deep engagement.

- **System reconnaissance loops:** The 63-command session on `2026-07-25` (`167.71.226.227`) and the 3709-command session on `2026-09-06` (`178.128.36.18`) repeat a 7-command battery on each iteration:
  1. `/bin/./uname -s -v -n -r -m` (nonstandard path - Wraith correctly returns `command not found`)
  2. `uptime -p` (not implemented - `command not found`)
  3. `lspci | grep VGA | cut -f5- -d ' '` (not implemented)
  4. `lspci | grep VGA -c`
  5. `nvidia-smi -q | grep "Product Name" | head -n 1 | awk ...`
  6. `lspci | grep "3D controller" | cut -f5- -d ' '`
  7. `nvidia-smi -q | grep "Product Name" | awk ... | grep . -c`

  This battery probes kernel version, uptime, and GPU/PCI hardware - classic host resource discovery (likely crypto-mining or ML-host fingerprinting). The repeated nature (9 iterations in the 63-command session, ~529 iterations in the 3709-command session) shows automated capability testing, not diverse manual interaction.

- **Host resource discovery:** Commands above are supplemented on days with broader coverage (`2026-08-04`, `2026-08-05`) by 6-occurrence probes: `df -h`, `hostname`, `ssh -V`, `nproc`/`/proc/cpuinfo`, `uname -a`, `free -h | grep Mem`, `echo bash_test_12345`. These are environment reconnaissance, not exploitation.

- **Filesystem or shell interaction:** Minimal. No `ls`, `cat /etc/passwd`, `wget`/`curl` downloads, or `chmod`/`useradd` persistence attempts were recorded in the Wraith JSONL (those are present as empty categories in the suspicious-commands table but not observed). The only non-probe commands are `echo 1 > /dev/null && cat /bin/echo` (2 occurrences in 2026-08-05) and `echo "bash --help; ..."` piped to `sh` (1 occurrence). All returned `1` or `command not found`, handled deterministically.

- **Skew:** Raw command count (21103) overstates meaningful diversity. Unique commands in cumulative: ~20 distinct command strings. Normalized engagement: 11 sessions with commands, median commands per session (excluding the 16662 outlier) is 63-119; mean is skewed to ~1758 by the large loop.

**Distinction:**

- **Automated loops:** `echo -e` single-command loops (8.217.18.158) and 7-command resource batteries (178.128.36.18, 167.71.226.227) - high volume, low diversity.
- **Reconnaissance:** Host resource discovery as above - systematic but shallow.
- **Capability testing:** `/bin/./uname` with nonstandard path, `nvidia-smi` pipeline - checks for shell robustness and hardware.
- **Manual-looking interaction:** Not observed at scale; no interactive `cd`/`ls` navigation, no iterative file edits, no manual error recovery.
- **One-off probes:** `echo 1 > /dev/null && cat /bin/echo` and the `bash --help` composite - single-shot shell probes.

## Session-level interpretation

- **Interactive sessions:** 11 of 12 sessions had commands; 1 session (`unknown` on 2026-07-12) had 0.
- **Command counts:** Heavily skewed. Sorted: 1,1,1,1,42,63,119,133,371,504,3709,16662. Median 91, mean 1758, unique commands 1-7 per session (most sessions use 1 or 7 distinct commands).
- **Long-running automated sessions:** `8.217.18.158` (16662 commands, latency ~0.03-0.12 ms per command, sub-millisecond deterministic shell), `178.128.36.18` (3709 commands), `159.89.188.217` (371 commands). These are not human-typed; timing and repetition indicate scripts.
- **Limitations:** Raw telemetry is ignored locally (`raw-data-us-east/` is gitignored and contains a backup tarball `wraith-us-east-telemetry-backup-20260910-222309.tar.gz`; not committed). Committed reports are the only reproducible source. Session duration fields are `N/A` in all but `2026-08-23`/`2026-08-05` due to missing `duration_seconds` in JSONL for some sessions; average/longest duration is not reliably derivable from committed reports alone. Where duration is `N/A`, analysis relies on command count.

## Reporting methodology and limitations

- Generation: `scripts/generate_report_us_east.py` (Wraith JSONL) with `extract_sessions` filtering at session level; test IPs excluded as above. Daily reports were regenerated with explicit `--out-file` redirection because normal `--out-dir` mode names output by current UTC date; cumulative `--all` combines `logs*`-like JSONL files from the input directory.
- Not directly comparable to Mumbai Beelzebub logs in raw `login attempts` (Mumbai reports 15153 login attempts from `Stateless` events; Wraith JSONL counts sessions, not individual password guesses).
- The `N/A` periods on 2026-07-13, 14, 17, 19 correspond to 0 sessions/IPs after exclusion; they are not missing data.
- The cumulative period ending 2026-09-06 excludes the 2026-09-07 single session (period `N/A` in its daily report) due to timestamp handling; daily report is authoritative for that day.
