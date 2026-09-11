# Video Showcase Plan - Wraith

**Goal:** Record a polished 10-15 minute technical video. This plan is evidence-driven and uses only repository code, docs, and generated reports. Keep narration natural: "I built / I deployed / I observed / I compared / I found."

**Repository frozen at:** `9fe1397` Polish final deployment comparison metrics (see `git log --oneline -12`)

---

## A. Opening / Project Overview (0:00-0:40, 40s)

- **Objective:** Establish track, problem, and what Wraith is
- **Say:** "This is Wraith, Ghost Cloud track, Adaptive SSH Honeypot for Real-World Attack Telemetry Collection on AWS. I investigated Internet SSH deception by building a deterministic interactive shell and comparing it against an LLM-backed baseline across two AWS regions."
- **Open:** `README.md:1` Project Overview + Research Objectives
- **Show:** `README.md` top, `docs/project-proposal.pdf` title page (if visible)
- **Visible:** Track title, `wraith/` folder in explorer
- **Type:** Talking-head + repo walkthrough

## B. Research Objective (0:40-1:20, 40s)

- **Say:** "The problem is that SSH honeypots either use static banners or per-command LLM calls that are costly and inconsistent on small EC2. I wanted to see what real attackers do and whether deterministic shell semantics first, with optional LLM assistance, is more reliable."
- **Open:** `README.md:9` Proposal vs Implementation vs Experiments, `docs/methodology.md:1` Research goal
- **Show:** Methodology bullet list, baseline vs interactive rationale
- **Type:** Narration + `docs/methodology.md`

## C. Architecture (1:20-2:30, 70s)

- **Say:** "Internet SSH -> Beelzebub on 2222 -> Wraith API/service -> parser -> deterministic handlers -> virtual filesystem -> response -> telemetry -> reports. Mumbai used Ollama qwen2.5:0.5b per command; US-East used Wraith deterministic."
- **Open:** `docs/architecture-notes.md:1` Deployment Model + `docs/simulator-architecture.md:7` Intended Architecture diagram + `wraith/server.py:88` `handle_command`
- **Show:** Mermaid `flowchart LR` in `architecture-notes.md:14` and `simulator-architecture.md:7`, `wraith/server.py:88-252` handler list
- **Duration:** 70s
- **Type:** Architecture diagram + code

## D. Wraith Implementation (2:30-4:00, 90s) - BEST CODE

- **Objective:** Show deterministic shell, not dump files
- **Snippets:**
  - `wraith/server.py:88-125` `handle_command` + `pwd`/`whoami`/`id`/`hostname` (deterministic, why it matters: predictable vs LLM inconsistency)
  - `wraith/filesystem.py:9-25` `FakeFilesystem` `PurePosixPath` per-session isolated (why: per-session state, no Redis)
  - `wraith/parser.py:16-21` `CommandParser.parse` shlex (why: correct arg handling, `echo -e` verbatim)
  - `wraith/telemetry.py:9-19` `TelemetryLogger` append-only `events.jsonl` (why: structured `session_started`/`command_executed`/`session_ended`)
  - `wraith/privesc.py:7` `PrivilegeEscalationSimulator` + `wraith/server.py:237` `sudo` flow (why: simulated escalation to `root@db-prod-01`)
  - `deploy/beelzebub_command_plugin.go:1` (why: Beelzebub -> Wraith HTTP `/command` bridge)
  - `run_server.py:1` `start_http_server 127.0.0.1:8080` (why: local server, `wraith_logs/`)
- **Say:** One sentence per snippet, e.g., "This handler returns cwd directly, not via LLM, so `pwd` is always consistent."
- **Show:** Code with line numbers, highlight function/class
- **Type:** Code walkthrough + terminal `demo_fake_shell.py` (if time)

## E. Mumbai Experiment (4:00-5:00, 60s)

- **Say:** "Mumbai ap-south-1 t3.micro Beelzebub + local Ollama qwen2.5:0.5b on 2222, admin 22 restricted. Period 2026-07-03 to 2026-07-26, 24 reports, plus 2026-07-01 validation with 0 logins and 6 LLM calls. Test traffic 49.207.63.82 etc. excluded."
- **Open:** `experiments/mumbai/README.md:9` Deployment architecture + `reports/mumbai/cumulative.md:4` Period + `docs/mumbai-results.md:13` Verified metrics
- **Show:** `reports/mumbai/cumulative.md` Summary table (773, 942, 15153, 1, 1, 51094 ms, 27.7, 646), `reports/mumbai/2026-07-01.md` 0/0 validation
- **Type:** Report table + docs

## F. US-East Experiment (5:00-6:00, 60s)

- **Say:** "US-East us-east-1 wraith-us-east-static 100.27.226.37 deterministic Wraith via Beelzebub 2222. Period 2026-07-12 to 2026-09-06, 14 daily + cumulative, 12 filtered sessions, 11 with commands, 21103 commands, 18 exact unique strings, 4 clients. Six test IPs excluded including 1.2.3.4. Raw 79% is one echo loop."
- **Open:** `reports/us-east/cumulative.md:1` Summary + `docs/us-east-results.md:13` Verified metrics
- **Show:** `reports/us-east/cumulative.md` Summary (12,12,11,21103,4) and Command distribution (echo 16662 79.0%)
- **Type:** Report table

## G. Telemetry Pipeline (6:00-6:40, 40s)

- **Say:** "Mumbai Beelzebub raw logs Status Stateless/Start/Interaction with total_duration vs US-East Wraith JSONL event/session_id/attacker_ip/command/response/cwd/latency_ms. Both via scripts/generate_report with --out-file and --no-geo, test IP exclusion, gitignored raw-data."
- **Open:** `docs/telemetry-pipeline.md:7` Flow + `docs/methodology.md:16` Telemetry sources + `wraith/telemetry.py:9`
- **Show:** Mermaid `flowchart TD`, `wraith_logs/events.jsonl` example (one line, blur IPs if needed), `scripts/README.md`
- **Type:** Diagram + telemetry JSON

## H. Real Attacker Behavior (6:40-7:40, 60s)

- **Say:** "Mumbai was credential scanning: top AyaKuyaSKRR 25, 123456 23, broad Go/OpenSSH scanners, only one post-auth echo. US-East was automated loops: 79% echo -e probes from 8.217.18.158 single session, plus 7-command host discovery battery repeated 9-529 times."
- **Open:** `reports/mumbai/cumulative.md` Credentials Attempted + `reports/us-east/cumulative.md` Commands Executed + Session Details `89c5852b` echo loop and `167.71.226.227` 63-command battery
- **Show:** Tables, highlight `echo -e`, `/bin/./uname`, `nvidia-smi`, `lspci`
- **Type:** Report tables
- **Do not claim:** 21103 unique interactions (correct: 18 exact strings)

## I. Deployment Comparison (7:40-8:40, 60s)

- **Say:** Use table verbally: "Mumbai 773 IPs 942 sessions 15153 logins 1 command 51 sec mean latency vs US-East 12 IPs 12 sessions 21103 commands but 79% one loop. Not directly comparable: different login counting, 23 vs 56 days, regions, populations."
- **Open:** `docs/deployment-comparison.md:13` Comparison table (23 dimensions)
- **Show:** Table, highlight Dominant pattern, Post-auth engagement, Response latency rows
- **Type:** Table walkthrough

## J. Mumbai OOM Incident (8:40-9:25, 45s)

- **Say (under 45s):** "On July 26 around 17:17 resource pressure from local Ollama triggered OOM, kernel killed llama-server ~629 MB, systemd-journald/snapd watchdog stressed, Beelzebub stayed alive until last honeypot interaction ~17:23:56Z, then guest-networking 169.254.169.254 degraded around 17:44, external telemetry ceased, not a full EC2 crash, recovered Sep 10 reboot."
- **Open:** `docs/mumbai-incident.md:7` Timeline + `reports/mumbai/cumulative.md` period
- **Show:** Timeline bullet list, kernel log phrasing
- **Type:** Docs + report

## K. US-East SSH Recovery (9:25-10:25, 60s)

- **Say (under 60s):** "Port 2222 honeypot stayed up while admin 22 was refused; EC2 Instance Connect and SSM failed, serial console showed login. Root cause was masked ssh.socket -> /dev/null and ssh.service with no boot activation. Fix was EBS snapshot, stop instance, detach root volume, attach to helper in same AZ, remove mask, enable ssh.service, reattach, boot, verify 22 and Beelzebub/Wraith active via telemetry."
- **Open:** `docs/us-east-recovery.md:5` Root cause + Recovery procedure
- **Show:** Diagram of EBS repair, `systemctl is-enabled` verification
- **Type:** Docs walkthrough

## L. Findings (10:25-11:10, 45s)

- **Say:** "Mumbai shows scanning dominates and local LLM on t3.micro is costly and unstable; US-East shows deterministic shell captures more post-auth reconnaissance but raw volume is skewed; both are automated, not clearly human."
- **Open:** `docs/deployment-comparison.md:74` Overall Experimental Consensus
- **Show:** Consensus bullets
- **Type:** Narration + table

## M. Limitations (11:10-11:40, 30s or 10s version)

- **30s:** "This is observational, not controlled A/B: different regions, 23 vs 56 days, attacker populations, telemetry semantics, backend. IP not human, Mumbai single-command limits depth, US-East 18 unique but 79% one loop, t3.micro qwen2.5:0.5b specific, no Redis persistence, no production LLM fallback."
- **10s:** "Observational, different regions and periods, IP not human, raw 21k is 18 unique with 79% one loop, t3.micro specific, no Redis/LLM fallback in production."
- **Open:** `README.md:141` Key Limitations
- **Type:** Talking-head

## N. Future Work (11:40-12:10, 30s)

- **Say:** Rank High: Redis reconnect persistence, optional LLM fallback hybrid; Medium: normalized engagement metrics, controlled multi-region deployments; Low: bot-family clustering, resource-aware inference. All grounded in proposal vs implementation gaps."
- **Open:** `README.md:149` Future Work
- **Type:** Narration

## O. Repository Walkthrough (12:10-13:30, 80s)

- **Order:** `README.md` (Quick Links) 10s -> `docs/architecture-notes.md` (model + components `wraith/server.py:88`) 10s -> `wraith/server.py` (deterministic handler) 10s -> `wraith/filesystem.py` (isolated) 5s -> `wraith/telemetry.py` 5s -> `experiments/mumbai/README.md` + `reports/mumbai/cumulative.md` (773/1) 10s -> `experiments/us-east/README.md` + `reports/us-east/cumulative.md` (12/21103) 10s -> `docs/deployment-comparison.md` (table + consensus) 10s -> `docs/mumbai-incident.md` + `docs/us-east-recovery.md` 5s -> `tests/test_fake_shell.py` + `git log --oneline -12` 5s
- **Say:** One sentence per click as in D-H
- **Type:** Repo walkthrough

## P. Closing (13:30-14:00, 30s/40s)

- **Say (40s):** "I built Wraith deterministic shell integrated with Beelzebub, deployed across Mumbai LLM-backed and US-East deterministic on AWS, collected 773 vs 12 IPs over multi-week periods, compared scanning vs post-auth reconnaissance, learned deterministic is lightweight and resilient while local LLM on t3.micro is costly, with observational limitations and future hybrid work. All reports, methodology, and recovery are documented and reproducible via scripts/generate_report*.py."
- **Open:** `README.md` Current Status
- **Type:** Talking-head + `git status` clean

---

**Durations:**
- **8-minute compressed:** A(20s) + C(40s) + D(60s, 2 snippets) + E+F(40s combined) + H(40s) + I(40s) + J+K(30s combined) + L(20s) + O(30s) + P(20s) = ~8 min (skip B,G,M,N details)
- **15-minute fuller:** All sections A-P as above + terminal `python -m unittest`, `git log`, and `demo_fake_shell.py` `whoami`/`pwd`/`ls` demo (30s extra)
