# Backend Integration Notes

## Deployment Context

Wraith now has two deployment contexts that should be treated separately:

- Deployment 1: the existing valid deployment with its earlier operational setup
- Deployment 2: the newer additive deployment that uses a deterministic fake shell simulator instead of an LLM backend

## Current Implementation for Deployment 2

The newer Wraith deployment uses a deterministic fake shell simulator instead of an LLM backend.

Current backend:

| Field | Value |
|-------|-------|
| Provider | Local Python simulator |
| Runtime | Deterministic code, no external model |
| Inference location | Local EC2 instance |
| API key required | No |
| Cloud quota dependency | No |
| Endpoint | Local Python module |

Ollama, OpenAI, and Gemini are not active deployment dependencies for Deployment 2. They are retained only as historical references in earlier experiments and do not replace the existing Deployment 1 setup.

---

## Active SSH Honeypot Configuration

The SSH honeypot should integrate with the local Python simulator as the response layer for attacker commands.

```text
Beelzebub -> local shell simulator -> structured JSONL telemetry
```

The integration is intentionally simple so future work can replace the local module with a richer backend without changing the overall architecture.

---

## Backend Evolution

### Phase 1: OpenAI

OpenAI API integration was tested earlier, but a runtime LLM backend is no longer part of the active deployment.

### Phase 2: Gemini

Gemini was evaluated as a lower-cost cloud alternative; it is not part of the current design.

### Phase 3: Deterministic Simulator (Current)

The project now uses a local Python shell simulator because it is:

- deterministic and predictable
- cheap to run
- easy to maintain
- suitable for offline honeypot research
- compatible with the current us-east-1 deployment model

---

## Current Status

The simulator covers common Linux-style commands, a fake filesystem, per-session state, privilege escalation prompts, and fake-download logging. It is designed to be extended with richer telemetry and more realistic behaviors over time.
