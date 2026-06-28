# System Architecture Notes

## Components

- Beelzebub Core Runtime
- SSH Strategy Handler
- LLMHoneypot Plugin Layer
- AWS EC2 Host

---

## Flow

1. External attacker connects to EC2 SSH port 2222
2. Beelzebub intercepts session
3. SSH strategy routes input to plugin
4. LLM backend generates response
5. Response returned as fake terminal output
6. Full session logged as telemetry

---

## Design Goal

To simulate a realistic Linux environment that adapts dynamically using LLM-generated responses, increasing attacker engagement time and telemetry quality.