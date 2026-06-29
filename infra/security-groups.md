# Security Groups

## Current Rules

| Port | Protocol | Source | Purpose |
|------|----------|--------|---------|
| `22` | TCP | Administrator IP only | Real SSH administration |
| `2222` | TCP | Public internet | SSH honeypot exposure |

## Internal-Only Services

Ollama listens on port `11434` for local inference, but it should remain internal to the EC2 host and must not be opened publicly in the security group.

## Exposure Model

The current MVP intentionally exposes only the SSH honeypot service to attackers:

```text
Attacker -> EC2 public IP:2222 -> Beelzebub SSH honeypot
```

Administrative SSH remains separated on port `22` and restricted to the administrator IP.

## Notes

- Do not expose Ollama directly to the internet.
- Do not document or open default Beelzebub services unless they are actively deployed and verified.
- Additional honeypot ports should be added only after the service is intentionally enabled and logging is confirmed.
