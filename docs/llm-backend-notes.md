# LLM Backend Integration Notes

## Current Implementation

The system uses the `LLMHoneypot` plugin which supports:

- OpenAI Chat Completions API
- Ollama local inference server (optional)

---

## Configuration (Per Service)

Each SSH/HTTP/TCP service defines its LLM backend like this:

```yaml
plugin:
  llmProvider: "openai"
  llmModel: "gpt-4o"
  openAISecretKey: ""
  rateLimitEnabled: true
  rateLimitRequests: 10
  rateLimitWindowSeconds: 60