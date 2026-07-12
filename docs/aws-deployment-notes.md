# AWS Deployment Notes

This repository documents two deployments. Deployment 1 is the existing valid deployment that remains in place. Deployment 2 is the newer additive deployment that introduces the deterministic simulator and is being documented separately.

## Infrastructure

- AWS EC2 Ubuntu server
- Region: `us-east-1`
- Instance role: public SSH honeypot host
- Public SSH exposure:
  - Port `22`: admin SSH access, restricted by security group
  - Port `2222`: public SSH honeypot service
- Storage: standard Ubuntu EBS volume sized for logs and telemetry

---

## Deployment 1: Existing Valid Deployment

This remains the original production-style deployment and is not being replaced by the work below.

## Deployment 2: New Simulator Deployment

Only the following services are documented as active in the new deployment path:

| Service | Port | Exposure | Purpose |
|---------|------|----------|---------|
| Beelzebub core | internal | local process | Honeypot orchestration |
| SSH honeypot | 2222 | public internet | Attacker interaction |
| Telemetry output | local JSONL | internal | Session logging |

Do not assume other Beelzebub services are active unless they are explicitly enabled and verified.

---

## Python Simulator Deployment

The active shell backend for Deployment 2 is a local deterministic Python simulator. It does not require Ollama or any external model endpoint and is added alongside the existing Deployment 1 setup.

```bash
cd /home/ubuntu/wraith
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 demo_fake_shell.py
```

The simulator writes structured JSONL events under the local telemetry directory.

---

## Beelzebub Deployment

```bash
git clone <repo-url>
cd beelzebub

go mod download
go build -o beelzebub .
```

The honeypot should be configured to route attacker sessions into the local simulator integration rather than the previous LLMHoneypot provider path.

Run Beelzebub with the active service configuration:

```bash
./beelzebub run
```

---

## Verified Deployment State

- External SSH connections reach the honeypot on port `2222`
- Password prompt and SSH interaction are reachable from the public internet
- The local Python simulator is serving shell responses deterministically
- Structured telemetry/event logging is operational
- No runtime LLM provider is required for the active deployment
