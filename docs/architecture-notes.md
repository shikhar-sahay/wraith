# System Architecture Notes

## Current Architecture

Wraith now uses local LLM inference on the EC2 host instead of relying on OpenAI or Gemini as the primary response backend.

```text
Internet
  -> AWS EC2
  -> Beelzebub Core
  -> SSH Honeypot on port 2222
  -> LLMHoneypot Plugin
  -> Ollama local inference service
  -> qwen2.5:0.5b
  -> Dynamic terminal response
  -> Structured telemetry logging
```

This architecture removes paid API dependency and makes the honeypot more suitable for continuous exposure to real-world SSH attack traffic.

---

## Components

- AWS EC2 Ubuntu host
- Beelzebub core runtime
- SSH honeypot service exposed on port `2222`
- LLMHoneypot plugin layer
- Ollama local inference service on port `11434` internal to the host
- `qwen2.5:0.5b` local model
- Structured telemetry/event logging

---

## Flow

1. External attacker connects to the EC2 instance on SSH port `2222`.
2. Beelzebub accepts the honeypot session.
3. The SSH strategy routes attacker input to the LLMHoneypot plugin.
4. The plugin sends the command context to local Ollama inference.
5. Ollama runs `qwen2.5:0.5b` and returns a generated shell response.
6. Beelzebub returns the fake terminal output to the attacker.
7. The session activity is captured as structured telemetry.

---

## Active Services

Only the following services are confirmed active in the current MVP deployment:

| Service | Port | Exposure | Purpose |
|---------|------|----------|---------|
| Beelzebub core | internal | local process | Honeypot orchestration |
| SSH honeypot | 2222 | public internet | Attacker interaction |
| Ollama | 11434 | internal only | Local LLM inference |

Other default Beelzebub services should not be treated as active unless they are explicitly enabled in deployment.

---

## Design Goal

To simulate a realistic Linux environment that adapts dynamically using LLM-generated responses, increasing attacker engagement time and telemetry quality while keeping inference local, free, and sustainable for long-running research deployment.

---

## Current Technical Limitation

The MVP is functional, but shell realism is not perfect yet. Some generated command outputs can be inconsistent, such as fake paths returned by `pwd`. This is a prompt-engineering and shell-state modeling issue inside the LLM plugin, not a deployment failure.
