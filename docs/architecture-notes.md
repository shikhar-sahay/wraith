# System Architecture Notes

## Deployment Overview

Wraith is documented here as two separate deployments that coexist:

- Deployment 1: the existing valid deployment that remains in place
- Deployment 2: the new additive deployment in us-east-1 that introduces the deterministic fake shell simulator

## Deployment 1: Existing Valid Deployment

This deployment remains the original Wraith deployment and continues to be treated as valid infrastructure.

```text
Internet attacker
  -> Existing Beelzebub deployment
  -> SSH honeypot service
  -> Existing operational telemetry and service configuration
```

## Deployment 2: New Simulator Deployment

Deployment 2 uses a deterministic fake shell simulator on the EC2 host rather than any runtime LLM backend.

```text
Internet attacker
  -> AWS EC2 (us-east-1)
  -> Beelzebub core
  -> SSH honeypot on port 2222
  -> Fake shell simulator (Python)
  -> Realistic Linux-style output
  -> Structured JSONL telemetry
```

This new architecture keeps the deployment simple, offline, and maintainable while still producing believable attacker-facing terminal behavior.

---

## Components

- AWS EC2 Ubuntu host in us-east-1
- Beelzebub core runtime
- SSH honeypot service exposed on port 2222
- Local Python simulator modules for session state and shell responses
- JSONL telemetry logging for future sync to the analysis workstation

---

## Flow

1. An external attacker connects to the EC2 instance on SSH port 2222.
2. Beelzebub accepts the honeypot session.
3. The shell simulator handles the attacker command stream.
4. The simulator returns a realistic Linux-style response and updates session state.
5. Beelzebub logs the interaction to JSONL telemetry.
6. The attacker continues interacting with the fake environment.

---

## Active Services

Only the following services are intended to be active in the new deployment path:

| Service | Port | Exposure | Purpose |
|---------|------|----------|---------|
| Beelzebub core | internal | local process | Honeypot orchestration |
| SSH honeypot | 2222 | public internet | Attacker interaction |
| Telemetry output | local JSONL | internal | Structured session logging |

Other Beelzebub services should not be treated as active unless they are explicitly enabled and verified.

---

## Design Goal

To simulate a realistic Ubuntu server environment that is deterministic, low-maintenance, and useful for research telemetry without relying on external AI systems.

---

## Current Status

The simulator supports session state, a fake filesystem, basic command responses, fake downloads, privilege escalation simulation, and structured logging. It is intentionally designed to be extended in future milestones rather than over-engineered up front.
