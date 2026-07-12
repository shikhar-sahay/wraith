# Ghost Cloud: LLM Honeypots in AWS

## Project Overview

Ghost Cloud is a research repository for collecting attacker behavior from multiple AWS honeypot deployments. The project began with the original Mumbai deployment and now also includes the Wraith deployment in us-east-1. Both remain documented because they serve different research paths and are intentionally preserved side by side.

The shared objective is to observe how attackers interact with realistic SSH honeypots, compare behavior across deployments, and store evidence in a form that is easy to analyze later.

## Research Objectives

- Capture reconnaissance, privilege escalation, persistence, and malware download attempts
- Record attacker IPs, SSH client fingerprints, command execution, and response behavior
- Compare how attackers behave across the Mumbai and Wraith deployments
- Preserve a deterministic, low-maintenance telemetry pipeline for repeatable analysis

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

The Mumbai deployment is the original documented honeypot environment and remains valid. It represents the earlier AWS-based research setup and is kept in the repository as the baseline deployment.

See:
- [docs/aws-deployment-notes.md](docs/aws-deployment-notes.md)
- [docs/architecture-notes.md](docs/architecture-notes.md)

### Wraith Deployment

The Wraith deployment is the newer additive deployment in us-east-1. It runs Beelzebub SSH as the attacker-facing honeypot and uses a custom Python telemetry server to collect structured JSONL events.

Wraith highlights:

- AWS EC2 hosted honeypot environment
- Beelzebub SSH honeypot on the attack surface
- Python telemetry server for structured session logging
- JSONL storage for session and command events
- Markdown report generation with generate_report.py
- systemd persistence through beelzebub.service and wraith.service

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

## Future Work

- Expand the experiment corpus for both deployments
- Add richer report summaries for command sequences and session duration
- Compare attacker behavior across Mumbai and Wraith over longer periods
- Preserve the current deterministic simulator while extending the telemetry analysis layer
