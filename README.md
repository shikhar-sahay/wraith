# Ghost Cloud: LLM Honeypots in AWS

## Project Overview

Ghost Cloud is a research repository for collecting attacker behavior from multiple AWS honeypot deployments. The Mumbai deployment is the LLM adaptation path, using a local Ollama backend with `qwen2.5:0.5b` to generate interactive shell responses on a `t3.micro` (Ubuntu 24.04, Beelzebub on port 2222). The Wraith deployment in `us-east-1`/Virginia is the deterministic static-shell path. Both remain documented because they serve different research goals and are intentionally preserved side by side.

The shared objective is to observe how attackers interact with realistic SSH honeypots, compare behavior across deployments, and store evidence in a form that is easy to analyze later.

## Research Objectives

- Capture reconnaissance, privilege escalation, persistence, and malware download attempts
- Record attacker IPs, SSH client fingerprints, command execution, and response behavior
- Evaluate limitations of conventional or purely LLM-driven honeypot behavior on constrained cloud instances
- Develop a more realistic adaptive SSH shell (deterministic semantics with optional controlled LLM assistance)
- Preserve a deterministic, low-maintenance telemetry pipeline for repeatable analysis
- Intended comparison: static/traditional behavior versus richer interactive Wraith behavior (pending US-East recovery; not yet supported by complete comparative data)

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

The Mumbai deployment is the LLM-adapted honeypot environment and remains valid. It ran in `ap-south-1` (Mumbai) on `wraith-honeypot` (`t3.micro`, Beelzebub on `2222`, Ollama `qwen2.5:0.5b`) and is the adaptive baseline for interactive shell behavior. Recovered dataset: `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z`, 773 unique observed source IPs, 942 sessions, 15,153 login attempts, but only 1 session progressed to command execution: indicating heavy automated credential-guessing with minimal engagement depth. Local LLM inference was observed to be operationally fragile on `t3.micro` (OOM/resource exhaustion and degraded networking ended telemetry on July 26). See `experiments/mumbai/` for the full 24-report recovered set and research notes.

See:
- [experiments/mumbai/README.md](experiments/mumbai/README.md)
- [experiments/mumbai/cumulative.md](experiments/mumbai/cumulative.md)
- [docs/aws-deployment-notes.md](docs/aws-deployment-notes.md)
- [docs/architecture-notes.md](docs/architecture-notes.md)

### Wraith Deployment

The Wraith deployment is the newer deterministic shell path. Code for the adaptive shell is implemented locally in `wraith/` and is exercised via `demo_fake_shell.py` and unit tests. The historical cloud instance `wraith-us-east-static` in `us-east-1` (public IP historically `100.27.226.37`, honeypot port `2222`) is currently inaccessible and recovery is pending (admin port `22` refused, EC2 Instance Connect failed, SSM unavailable due to missing role configuration; serial console reaches a Linux login prompt). Until recovery, Wraith is documented as a local deterministic simulator with a Beelzebub integration path, not as a completed comparative dataset.

Wraith highlights (implemented locally, cloud validation pending):

- Deterministic fake Linux shell (session identity, parser, filesystem, persona, privesc simulation, registry, telemetry)
- Python telemetry server for structured session logging (`wraith/server.py`, JSONL under `wraith_logs/`)
- JSONL storage for session and command events
- Markdown report generation with `scripts/generate_report.py`
- Systemd persistence definitions in `deploy/` (`beelzebub-simulator.service`) - deployment to EC2 pending recovery

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

## Repository Structure

- [README.md](README.md) – project overview and deployment summary
- [docs/](docs) – architecture, telemetry, deployment, and background notes
- [experiments/](experiments) – daily and cumulative experiment reports
- [reports/](reports) – generated Markdown reports for Wraith experiments
- [wraith_logs/](wraith_logs) – raw JSONL telemetry output from the Wraith deployment
- [deploy/](deploy) – deployment documentation and service definitions
- [infra/](infra) – AWS environment notes and operational guidance
- [scripts/](scripts) – report generation utilities
- [wraith/](wraith) – simulator runtime used by the Wraith deployment

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

- Mumbai AWS deployment on `wraith-honeypot` (`t3.micro`, `ap-south-1`, Ubuntu 24.04, Beelzebub on `2222`, local Ollama `qwen2.5:0.5b`)
- Recovery of surviving Mumbai telemetry and regeneration of 24 dated reports + `cumulative.md` (period `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z`, `experiments/mumbai/`)
- Cumulative analysis: 773 unique observed source IPs, 942 sessions, 15,153 login attempts, 1 session with commands (1 command: `echo 1 > /dev/null && cat /bin/echo` from `47.113.113.162`)
- Investigation of July 26 operational failure (OOM resource exhaustion and degraded guest networking, September 10 reboot recovery)
- Development of Wraith deterministic shell components (`wraith/` - filesystem, parser, session identity, persona, privesc, registry, telemetry, server) with local demo and tests

**In progress**

- Recovery of US-East instance `wraith-us-east-static` (`us-east-1`, historically `100.27.226.37`) and validation of its telemetry (currently inaccessible)
- End-to-end validation of Wraith on cloud (Beelzebub integration via `deploy/`)

**Pending / future**

- Final static-vs-interactive comparison after US-East recovery (not yet supported by complete comparative data)
- Session persistence evaluation beyond per-session in-memory state (no Redis persistence implemented)
- Final consolidated research analysis and engagement-depth assessment

## Future Work

- Complete US-East recovery and incorporate its telemetry after validation
- Conduct the intended static-vs-interactive comparison only after both datasets are available
- Add richer report summaries for command sequences and session duration
- Preserve the current deterministic simulator while extending the telemetry analysis layer
