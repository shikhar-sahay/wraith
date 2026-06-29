# Cost Monitoring

## Current Cost Strategy

Wraith is designed to keep the active MVP deployment as close to free-tier operation as possible.

The major cost-related architecture change is the migration away from paid cloud LLM APIs. The current backend uses Ollama locally on the EC2 instance with `qwen2.5:0.5b`, so normal honeypot interaction does not generate OpenAI, Gemini, or other hosted inference charges.

## AWS Controls

- Zero spend budget configured
- Billing alerts configured
- Free-tier oriented EC2 deployment
- EBS volume expanded from 8GB to 15GB to support local model storage

## LLM Cost Notes

| Backend | Current role | Cost concern |
|---------|--------------|--------------|
| Ollama + `qwen2.5:0.5b` | Active backend | No per-request API cost |
| OpenAI | Historical/optional legacy support | Paid API and quota requirements |
| Gemini | Historical experiment | Free tier quotas too restrictive |

## Monitoring Focus

- EC2 runtime hours
- EBS storage usage after expansion to 15GB
- Elastic IP billing behavior if the instance is stopped
- Unexpected outbound data transfer
- Any accidental reintroduction of hosted LLM API usage
