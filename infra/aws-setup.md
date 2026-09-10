# AWS Infrastructure Setup

## Account Security

- Root MFA enabled
- Zero spend budget configured
- Billing alerts configured
- IAM user created for operational access

## Compute Infrastructure

- **Mumbai:** EC2 instance type: `t3.micro`, Region: `ap-south-1` (`wraith-honeypot`, Ubuntu 24.04), Elastic IP attached, EBS volume expanded from 8GB to 15GB for Ollama `qwen2.5:0.5b` storage - completed and documented in `experiments/mumbai/`
- **Wraith historical:** Instance `wraith-us-east-static`, Region `us-east-1`, historically `100.27.226.37` - currently inaccessible, recovery pending (see `docs/aws-deployment-notes.md`); no Wraith cloud telemetry validated yet

## Network Configuration

| Port | Exposure | Purpose |
|------|----------|---------|
| `22/tcp` | Restricted to administrator IP | Real SSH administration |
| `2222/tcp` | Public internet | SSH honeypot traffic |
| `11434/tcp` | Internal only | Ollama local inference API |

Ollama should not be publicly exposed. It is used locally by the Beelzebub LLMHoneypot plugin.

## Deployment

- SSH access verified
- Go runtime installed
- Beelzebub repository cloned
- Framework compiled successfully
- SSH deception runtime deployed successfully on port `2222`
- Ollama installed locally on the EC2 instance
- `qwen2.5:0.5b` model installed
- Dynamic LLM responses verified
- Structured telemetry/event logging verified

## Active Architecture

```text
Internet -> AWS EC2 -> Beelzebub -> SSH Honeypot -> LLMHoneypot Plugin -> Ollama -> qwen2.5:0.5b
```
