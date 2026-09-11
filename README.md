# Ghost Cloud: LLM Honeypots in AWS

## Project Overview

Ghost Cloud is a research repository for collecting attacker behavior from multiple AWS honeypot deployments. The Mumbai deployment is the LLM adaptation path, using a local Ollama backend with `qwen2.5:0.5b` to generate interactive shell responses on a `t3.micro` (Ubuntu 24.04, Beelzebub on port 2222). The Wraith deployment in `us-east-1`/Virginia is the deterministic static-shell path. Both remain documented because they serve different research goals and are intentionally preserved side by side.

The shared objective is to observe how attackers interact with realistic SSH honeypots, compare behavior across deployments, and store evidence in a form that is easy to analyze later.

**Proposal vs implementation vs experiments:** The original proposal is in `docs/project-proposal.pdf` (Adaptive SSH Honeypot). What was actually built is the Wraith deterministic shell in `wraith/` (`server.py:88` 30+ commands, `filesystem.py`, `telemetry.py`) with Beelzebub integration (`deploy/`). Completed experiments are Mumbai (`ap-south-1`, `2026-07-03` - `2026-07-26`, `reports/mumbai/`) and US-East (`us-east-1`, `2026-07-12` - `2026-09-06`, `reports/us-east/`). Current conclusions are observational (see `docs/deployment-comparison.md` caveat) and documented in `docs/mumbai-results.md`/`docs/us-east-results.md`.

## Quick Links for Review / Showcase

**Deployment Comparison and Findings (canonical):** [docs/deployment-comparison.md](docs/deployment-comparison.md) - side-by-side table, Overall Experimental Consensus, Showcase Summary

**Primary report artifacts (directly comparable):** [reports/mumbai/cumulative.md](reports/mumbai/cumulative.md) (24+1 reports, `ap-south-1`) and [reports/us-east/cumulative.md](reports/us-east/cumulative.md) (14+1 reports, `us-east-1`)

**Detailed results:** [docs/mumbai-results.md](docs/mumbai-results.md) | [docs/us-east-results.md](docs/us-east-results.md) | **Methodology:** [docs/methodology.md](docs/methodology.md)

**Incidents:** [docs/mumbai-incident.md](docs/mumbai-incident.md) (2026-07-26 OOM) | [docs/us-east-recovery.md](docs/us-east-recovery.md) (masked `ssh.socket`)

## Research Objectives

- Capture reconnaissance, privilege escalation, persistence, and malware download attempts
- Record attacker IPs, SSH client fingerprints, command execution, and response behavior
- Evaluate limitations of conventional or purely LLM-driven honeypot behavior on constrained cloud instances
- Develop a more realistic adaptive SSH shell (deterministic semantics with optional controlled LLM assistance)
- Preserve a deterministic, low-maintenance telemetry pipeline for repeatable analysis
- Compare static/traditional behavior versus richer interactive Wraith behavior (observational comparison documented in `docs/deployment-comparison.md` after recovery of both deployments; caveat: different regions/periods, not a controlled causal experiment)

## System Architecture

```mermaid
flowchart LR
	A[Internet attacker] --> B[SSH entry point]
	B --> C{Deployment}
	C --> D[Mumbai deployment]
	C --> E[Wraith deployment]
	D --> F[Existing Beelzebub-based workflow]
	E --> G[Beelzebub SSH honeypot]
	G --> H[Wraith Python telemetry server]
	H --> I[JSONL telemetry under wraith_logs/]
	I --> J[generate_report.py]
	J --> K[Markdown reports under reports/]
```

## Deployment Overview

### Mumbai Deployment

The Mumbai deployment is the LLM-adapted honeypot environment and remains valid. It ran in `ap-south-1` (Mumbai) on `wraith-honeypot` (`t3.micro`, Beelzebub on `2222`, Ollama `qwen2.5:0.5b`) and is the adaptive baseline for interactive shell behavior. Recovered dataset: `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z`, 773 unique observed source IPs, 942 sessions, 15,153 login attempts, but only 1 session progressed to command execution: indicating heavy automated credential-guessing with minimal engagement depth. Local LLM inference was observed to be operationally fragile on `t3.micro` (OOM/resource exhaustion and degraded networking ended telemetry on July 26). See `reports/mumbai/cumulative.md` and `docs/mumbai-results.md` for the full 24-report recovered set.

See:
- [experiments/mumbai/README.md](experiments/mumbai/README.md) (experiment log) and [reports/mumbai/cumulative.md](reports/mumbai/cumulative.md) (reports)
- [docs/aws-deployment-notes.md](docs/aws-deployment-notes.md)
- [docs/architecture-notes.md](docs/architecture-notes.md)

### Wraith Deployment

The Wraith deployment is the deterministic shell path. Code for the adaptive shell is implemented locally in `wraith/` and is exercised via `demo_fake_shell.py` and unit tests. The cloud instance `wraith-us-east-static` in `us-east-1` (public IP historically `100.27.226.37`, honeypot port `2222`) was recovered after an admin SSH outage (masked `ssh.socket`, see `docs/us-east-recovery.md`) via offline EBS repair with snapshot. It produced real-world telemetry: 12 unique attacker IPs, 12 sessions, 11 with commands, 21103 commands from `2026-07-12` to `2026-09-06` (`reports/us-east/`; test traffic excluded via `scripts/generate_report_us_east.py`). See `docs/us-east-results.md` and `reports/us-east/cumulative.md`.

Wraith highlights (local implementation verified, cloud telemetry recovered):

- Deterministic fake Linux shell (session identity, parser, filesystem, persona, privesc simulation, registry, telemetry) - `wraith/server.py:88` handles 30+ commands
- Python telemetry server for structured session logging (`wraith/server.py`, JSONL under `wraith_logs/`)
- JSONL storage for session and command events (`wraith/telemetry.py` `events.jsonl`)
- Markdown report generation with `scripts/generate_report_us_east.py` (Wraith JSONL) and `scripts/generate_report.py` (Mumbai Beelzebub logs)
- Systemd persistence definitions in `deploy/` (`beelzebub-simulator.service`); Beelzebub and Wraith services verified active after recovery

## Telemetry Pipeline

```mermaid
flowchart TD
	A[Attacker interaction] --> B[SSH honeypot]
	B --> C[Telemetry collection]
	C --> D[JSONL event storage]
	D --> E[generate_report.py]
	E --> F[Markdown experiment report]
```

Wraith telemetry currently captures:

- `session_started`
- `command_executed`
- `session_ended`

Collected fields include attacker IP, client string, command, response, cwd, latency_ms, and timestamps.

## Experiment Workflow

1. Deploy the selected honeypot environment on AWS.
2. Allow attacker traffic to interact with the SSH service.
3. Collect structured JSONL telemetry.
4. Exclude test traffic when needed.
5. Generate daily or cumulative Markdown reports.
6. Review the reports and append manual notes in the experiment log.

## Documentation Map

- **Start here:** `docs/README.md` index, then `docs/methodology.md` for methodology
- **Deployments:** `docs/aws-deployment-notes.md`, `infra/aws-setup.md`, `deploy/README.md`
- **Results:** `docs/mumbai-results.md` (`reports/mumbai/` 24+1 reports), `docs/us-east-results.md` (`reports/us-east/` 14+1 reports), `docs/deployment-comparison.md` (observational comparison)
- **Incidents:** `docs/mumbai-incident.md` (2026-07-26 OOM), `docs/us-east-recovery.md` (masked `ssh.socket`)
- **Architecture & Operations:** `docs/architecture-notes.md`, `docs/simulator-architecture.md`, `docs/telemetry-pipeline.md`, `docs/experiment-workflow.md`
- **Proposal:** `docs/project-proposal.pdf`

## Repository Structure

- [README.md](README.md) - project overview and deployment summary
- [docs/](docs) - see `docs/README.md` index; key docs: `methodology.md`, `mumbai-results.md`, `us-east-results.md`, `deployment-comparison.md`, `mumbai-incident.md`, `us-east-recovery.md`
- [experiments/](experiments) - Mumbai reports `reports/mumbai/` (24+1, `2026-07-03` - `2026-07-26`), Wraith notes `experiments/us-east/` (`README.md`/`experiment-log.md`)
- [reports/](reports) - Wraith US-East reports `reports/us-east/` (14+1, `2026-07-12` - `2026-09-06`)
- `wraith_logs/` - raw JSONL telemetry (gitignored, backup `raw-data-us-east/` gitignored)
- [deploy/](deploy) - deployment service definitions and Beelzebub patch (`beelzebub-simulator.service`)
- [infra/](infra) - AWS infrastructure notes
- [scripts/](scripts) - `generate_report.py` (Mumbai Beelzebub logs) and `generate_report_us_east.py` (Wraith JSONL)
- [wraith/](wraith) - deterministic shell implementation (`server.py`, `filesystem.py`, `parser.py`, `telemetry.py`)
- [tests/](tests) - `test_fake_shell.py` (4 tests)

## Setup Instructions

For local simulator development and verification:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python demo_fake_shell.py
```

For the deployed Wraith stack, enable the systemd services on the Ubuntu EC2 instance and keep the simulator and honeypot running independently from the terminal.

## Current Status

**Completed**

- Mumbai AWS deployment on `wraith-honeypot` (`t3.micro`, `ap-south-1`, Ubuntu 24.04, Beelzebub on `2222`, local Ollama `qwen2.5:0.5b`) - 24 dated reports + `cumulative.md` in `reports/mumbai/` (period `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z`, 773 IPs, 942 sessions, 15153 logins, 1 command from `47.113.113.162`)
- Recovery of surviving Mumbai telemetry and regeneration via `scripts/generate_report.py` (test traffic excluded); investigation of July 26 OOM resource exhaustion and degraded guest networking with `2026-09-10` reboot recovery (`docs/mumbai-incident.md`)
- Development of Wraith deterministic shell components (`wraith/` - filesystem, parser, session identity, persona, privesc, registry, telemetry, server) with local demo `demo_fake_shell.py` and tests `tests/test_fake_shell.py`
- US-East AWS deployment `wraith-us-east-static` (`us-east-1`, `100.27.226.37:2222`) - 14 daily reports + `cumulative.md` in `reports/us-east/` (period `2026-07-12` - `2026-09-06`, 12 IPs, 12 sessions, 11 with commands, 21103 commands, see `docs/us-east-results.md`)
- US-East recovery from masked `ssh.socket -> /dev/null` via offline EBS repair with snapshot, telemetry preserved and verified (`docs/us-east-recovery.md`)
- Observational comparison between Mumbai (LLM-assisted) and US-East (deterministic Wraith) documented in `docs/deployment-comparison.md` (caveat: different regions/periods, not a controlled causal experiment)
- Analysis docs: `docs/mumbai-results.md`, `docs/us-east-results.md`, `docs/mumbai-incident.md`, `docs/deployment-comparison.md`

**Pending / future**

- Session persistence evaluation beyond per-session in-memory state (no Redis persistence implemented - `wraith/filesystem.py` is per-session)
- Final consolidated research analysis after extended observation if additional deployments are run
- Optional controlled LLM fallback as adaptive layer (planned, not production-complete in `wraith/server.py`)

## Key Limitations

- Observational comparison only - Mumbai and US-East differed in region, period, backend, attacker population, and telemetry semantics (see `docs/methodology.md`); not a controlled A/B experiment
- Mumbai single-command dataset (1 of 942 sessions) limits engagement-depth conclusions; characterizes scanning phase
- US-East 21103 raw commands overstate diversity (79.0% - 16662/21103 is one repeated `echo -e "\x6F\x6B"` loop from predominantly one session `8.217.18.158`; 18 exact unique command strings with whitespace-exact counting)
- No geographic/human-actor attribution beyond source IPs/client strings; `t3.micro` LLM observations specific to `qwen2.5:0.5b` on that configuration
- Wraith per-session filesystem is in-memory only (no Redis persistence) and `port`/`cwd` handling is simulated; no LLM fallback in production (`wraith/server.py` deterministic)

## Future Work

- Extend observation with additional regions or longer exposure if resources permit
- Add normalized engagement metrics to report generators and validate additional Wraith commands
- Preserve deterministic simulator while optionally adding controlled LLM fallback for uncovered commands (planned, not production)
- Validate `systemctl is-enabled ssh.service` and no `ssh.socket` mask on every deployment (see `docs/us-east-recovery.md` lesson)

## Reproducibility

- Mumbai: `python scripts/generate_report.py /path/to/beelzebub/logs --exclude-ip 49.207.63.82 --exclude-ip 49.207.60.111 --exclude-ip 49.207.58.88 --no-geo --out-dir reports/mumbai --out-file 2026-07-03.md` daily; cumulative `--all --out-file cumulative.md`
- US-East: `python scripts/generate_report_us_east.py /path/to/wraith_logs --exclude-ip 49.207.63.82 --exclude-ip ... --no-geo --out-dir reports/us-east --out-file 2026-08-05.md` daily; cumulative `--all`
- Tests: `python -m unittest tests/test_fake_shell.py` (4 tests) and `python demo_fake_shell.py`; `python -m py_compile scripts/generate_report*.py`
