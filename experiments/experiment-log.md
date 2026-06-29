# Experiment Log

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
