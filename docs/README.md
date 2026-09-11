# Documentation Index

This folder contains canonical research and engineering documentation for Ghost Cloud. Start with `../README.md` for the project overview, then use this index to navigate.

## Overview

- [Architecture Notes](architecture-notes.md) - Deployment model, Mumbai vs Wraith comparison, Wraith components verified against `wraith/` code, event flow
- [Methodology](methodology.md) - Research goal, baseline vs interactive rationale, regions, port separation, exclusion policy, telemetry sources, session definitions, report generation, comparison limitations
- [Telemetry Pipeline](telemetry-pipeline.md) - Wraith deterministic events (`session_started`/`command_executed`/`session_ended`), storage locations, report output, operational notes, deployment status

## Deployments

- [AWS Deployment Notes](aws-deployment-notes.md) - Shared infra, Mumbai `ap-south-1` `t3.micro` vs Wraith `us-east-1` `100.27.226.37`, service table, persistence, workflow
- **Infrastructure:** `../infra/aws-setup.md`, `../infra/ec2-configuration.md`, `../infra/security-groups.md`, `../deploy/README.md` (systemd, Beelzebub patch)

## Results

- [Mumbai Results](mumbai-results.md) - `ap-south-1` Ollama `qwen2.5:0.5b`, period `2026-07-03` - `2026-07-26`, 773 IPs, 942 sessions, 15153 logins, 1 command, 51 sec latency
- [US-East Results](us-east-results.md) - `us-east-1` deterministic shell, period `2026-07-12` - `2026-09-06`, 12 IPs, 12 sessions, 21103 commands, skew analysis
- [Deployment Comparison](deployment-comparison.md) - Observational comparison table, engagement vs volume vs diversity vs reliability, caveats (different regions/periods/populations, not controlled)

## Incidents

- [Mumbai Resource Exhaustion](mumbai-incident.md) - 2026-07-26 OOM `llama-server` ~629 MB, `systemd-journald`/`snapd` watchdog, guest-networking `169.254.169.254` degraded, `2026-09-10` reboot
- [US-East SSH Recovery](us-east-recovery.md) - Masked `ssh.socket -> /dev/null`, `ssh.service` not enabled, offline EBS repair with snapshot via helper instance, verification

## Operations

- [Experiment Workflow](experiment-workflow.md) - Layout `reports/mumbai/` and `reports/us-east/`, workflow, deployment mapping, preservation rule
- [Simulator Architecture](simulator-architecture.md) - Deterministic shell `wraith/server.py:88` 30+ commands, filesystem, persona, telemetry, planned vs implemented (no Redis, no LLM fallback)

## Proposals and Reports

- `project-proposal.pdf` - Original research proposal (Adaptive SSH Honeypot)
- `../reports/mumbai/cumulative.md` - Mumbai cumulative report (24+1 reports, test traffic excluded)
- `../reports/us-east/cumulative.md` - US-East cumulative report (14+1 reports, 6 test IPs excluded)

## Key Links

- Implementation: `../wraith/` (`server.py`, `filesystem.py`, `parser.py`, `telemetry.py`), `../run_server.py`, `../demo_fake_shell.py`, `../tests/test_fake_shell.py`
- Deployment: `../deploy/beelzebub-simulator.service`, `../deploy/beelzebub_command_plugin.go`
- Reports: `../reports/mumbai/`, `../reports/us-east/`
- Scripts: `../scripts/generate_report.py` (Mumbai), `../scripts/generate_report_us_east.py` (Wraith)
