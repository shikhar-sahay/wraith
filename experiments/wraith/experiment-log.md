# Wraith Experiment Log

## 29 June 2026

### LLM Backend Migration

Migrated the active Wraith backend away from hosted cloud inference and onto local Ollama inference.

Backend phases tested:

| Phase | Backend | Result |
|-------|---------|--------|
| 1 | OpenAI API | Blocked by paid API, billing, and quota constraints |
| 2 | Gemini | Free tier quotas too restrictive for sustained honeypot traffic |
| 3 | Ollama | Adopted as current backend |

Current active model:

```text
qwen2.5:0.5b
```

Reasons for adopting Ollama:

- Fully free local inference
- No API keys required
- No hosted quota limits
- Better suited for continuous internet-facing honeypot operation

### Infrastructure Update

Expanded the EC2 EBS volume from 8GB to 15GB to support Ollama and local model storage.

### Functional Validation

Confirmed current MVP state:

- AWS EC2 instance running
- Beelzebub installed and functioning
- SSH honeypot exposed on port `2222`
- External SSH connections reach the honeypot
- LLMHoneypot plugin enabled
- Ollama installed locally
- `qwen2.5:0.5b` installed locally
- SSH commands generate dynamic LLM responses
- Structured telemetry/event logging operational

### Current Technical Limitation

Terminal realism is functional but imperfect. Some command outputs can be unrealistic or inconsistent, including fake path behavior for commands such as `pwd`. The next refinement target is prompt engineering and shell-state consistency inside the LLM plugin.

---

## 03-08 July 2026

### Observation Summary

Across the first week of Wraith operation, the honeypot consistently attracted automated SSH reconnaissance and password-spraying traffic. Most activity originated from China and used libssh or OpenSSH client stacks, with one particularly intense burst on 06 July that generated more than 12,000 login attempts. No successful logins or command executions were observed during this period, which suggests the service was primarily being probed for weak credentials rather than exploited further.

### Key Takeaways

- The honeypot is successfully attracting internet-facing SSH scanning traffic.
- Attackers appear to rely on scripted tooling and common password lists rather than interactive human access.
- The absence of command execution indicates the current deception layer is still effective at blocking progression beyond authentication.
- The next refinement target remains stronger lure content and more realistic shell behavior to increase engagement if a password is guessed.

---

## 28 June 2026

### Infrastructure Deployment

Completed initial AWS deployment and security hardening.

### Framework Deployment

Successfully cloned and compiled Beelzebub framework.

### SSH Service Deployment

Configured isolated SSH service on port 2222.

### Validation

External SSH connection successfully reached deception service.

Command used:

```bash
ssh -p 2222 anything@13.207.110.30
```

Observed behavior:

SSH handshake successful and password prompt returned.

Status:

Wraith successfully exposed to public internet.