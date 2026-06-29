# LLM Backend Integration Notes

## Current Implementation

The active Wraith deployment uses the Beelzebub `LLMHoneypot` plugin with local Ollama inference.

Current backend:

| Field | Value |
|-------|-------|
| Provider | Ollama |
| Model | `qwen2.5:0.5b` |
| Inference location | Local EC2 instance |
| API key required | No |
| Cloud quota dependency | No |
| Local endpoint | `http://localhost:11434/api/chat` |

OpenAI and Gemini are not active deployment dependencies. They were evaluated during development and should be treated as optional legacy/provider experiments only.

---

## Active SSH Honeypot Configuration

The active SSH honeypot service (`configurations/services/ssh-2222.yaml`) is configured to use Ollama:

```yaml
plugin:
  llmProvider: "ollama"
  llmModel: "qwen2.5:0.5b"
  rateLimitEnabled: true
  rateLimitRequests: 10
  rateLimitWindowSeconds: 60
```

The `llmProvider: "ollama"` setting routes requests to the local Ollama server at `http://localhost:11434/api/chat`.

---

## Backend Evolution

### Phase 1: OpenAI

OpenAI API integration was tested first. It was not suitable for the active MVP because paid API access, billing, and quota requirements blocked sustained testing.

### Phase 2: Gemini

Gemini was tested as a lower-cost cloud alternative. Free tier quotas were too restrictive for real-world honeypot exposure and sustained attack traffic.

### Phase 3: Ollama (Current)

The project migrated to Ollama local inference using `qwen2.5:0.5b`.

Reasons for the migration:

- Fully free inference
- No API keys
- No cloud quota limits
- Offline local execution
- Better fit for continuous honeypot deployment
- Small model footprint that works on the current EC2 instance

---

## Model Size Notes

The EC2 instance has limited RAM, so model size matters. `qwen2.5:0.5b` is the active model because it fits the current resource constraints while still enabling dynamic responses.

| Model | Size | Works on free tier? |
|-------|------|---------------------|
| `qwen2.5:0.5b` | about 397 MB | Yes, active model |
| `qwen2.5:3b` | about 2 GB | Borderline |
| `qwen2.5:7b` | about 4.7 GB | Not suitable for current instance |
| `gemini-2.0-flash` | cloud-hosted | Not active; quota limited |

---

## Current Limitation

Local inference works, but prompt engineering still needs improvement. Some terminal outputs can be unrealistic or state-inconsistent, such as `pwd` returning unexpected fake paths. This is the main technical refinement area for the next iteration.
