# AWS Deployment Notes

This repository documents two deployments. The Mumbai deployment remains the original reference deployment, and the Wraith deployment is the newer additive path in us-east-1.

## Shared AWS Infrastructure

- AWS EC2 Ubuntu server
- Region: `us-east-1` for the Wraith deployment
- Instance role: public SSH honeypot host
- Public SSH exposure:
  - Port `22`: admin SSH access, restricted by security group
  - Port `2222`: public SSH honeypot service
- Storage: EBS volume sized for logs, telemetry, and reports

## Mumbai Deployment

The Mumbai deployment is preserved as the original documented AWS honeypot setup and remains valid. It is the LLM-adapted path, using local Ollama with `qwen2.5:0.5b` for interactive shell responses on `wraith-honeypot` (`t3.micro`, Ubuntu 24.04, `ap-south-1`, Beelzebub on `2222`). The recovered attacker-observation period is `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z` (773 source IPs, 942 sessions, 15,153 login attempts, 1 command executed); see `experiments/mumbai/`.

See:
- [docs/architecture-notes.md](architecture-notes.md)
- [docs/llm-backend-notes.md](llm-backend-notes.md)

## Wraith Deployment

The Wraith deployment adds a deterministic telemetry pipeline alongside the existing project history.

| Service | Port | Exposure | Purpose |
|---------|------|----------|---------|
| beelzebub.service | internal | local process | SSH honeypot orchestration |
| wraith.service | internal | local process | JSONL telemetry server |
| SSH honeypot | 2222 | public internet | Attacker interaction |
| telemetry output | local JSONL | internal | Session and command logging |
| reports/ | filesystem path | local only | Markdown experiment reports |

Do not assume other services are active unless they are explicitly enabled and verified.

### Wraith runtime layout

```mermaid
flowchart LR
    A[Attacker] --> B[EC2 host]
    B --> C[Beelzebub SSH honeypot]
    C --> D[Wraith telemetry service]
    D --> E[wraith_logs/ JSONL]
    E --> F[generate_report.py]
    F --> G[reports/]
```

### Wraith persistence

The Wraith deployment is intended to run under systemd so it can remain active after disconnecting from the terminal.

- `beelzebub.service` keeps the SSH honeypot available
- `wraith.service` keeps telemetry collection available

## Mumbai vs Wraith

| Aspect | Mumbai | Wraith |
|--------|--------|--------|
| Goal | LLM-adapted research deployment | Additive structured-telemetry deployment |
| Telemetry | Existing operational notes | JSONL session and command events |
| Report generation | Existing experiment summaries | generate_report.py Markdown reports |
| Runtime model | Local Ollama `qwen2.5:0.5b` on `t3.micro` (operationally fragile under load; see `experiments/mumbai/`) | Deterministic static SSH shell and telemetry pipeline |

## Deployment Workflow

### Mumbai

The Mumbai deployment is the historical LLM baseline and should continue to be documented as the Beelzebub + local Ollama `qwen2.5:0.5b` adaptation path (see `experiments/mumbai/README.md` for the July 26 OOM/networking interruption and September 10 recovery).

### Wraith

1. Deploy Beelzebub and the Wraith telemetry service on the EC2 host.
2. Enable the systemd services.
3. Confirm SSH access through port `2222`.
4. Collect JSONL telemetry under `wraith_logs/`.
5. Generate Markdown reports into `reports/`.

## Setup References

- [infra/aws-setup.md](../infra/aws-setup.md)
- [infra/ec2-configuration.md](../infra/ec2-configuration.md)
- [infra/security-groups.md](../infra/security-groups.md)
- [docs/telemetry-pipeline.md](telemetry-pipeline.md)
