# AWS Deployment Notes

## Infrastructure

- AWS EC2 Ubuntu server
- Instance class: free-tier oriented deployment
- Region: `ap-south-1`
- Elastic IP attached
- EBS volume expanded from 8GB to 15GB for local Ollama model storage
- Public SSH exposure:
  - Port `22`: real administrator SSH access, restricted to administrator IP
  - Port `2222`: public SSH honeypot service

---

## Confirmed Active Services

Only the following services are documented as active in the current deployment:

| Service | Port | Exposure | Purpose |
|---------|------|----------|---------|
| Beelzebub core | internal | local process | Honeypot orchestration |
| SSH honeypot | 2222 | public internet | LLM-powered attacker interaction |
| Ollama | 11434 | internal only | Local inference for `qwen2.5:0.5b` |

Do not assume default Beelzebub HTTP, LDAP, SMB, MCP, maze, or metrics services are active unless they are explicitly enabled and verified.

---

## Disk Expansion

The original 8GB EBS volume was expanded to 15GB to support local model storage for Ollama.

AWS Console path:

```text
EC2 -> Volumes -> Modify Volume -> 15GB
```

Instance filesystem expansion:

```bash
sudo growpart /dev/nvme0n1 1
sudo resize2fs /dev/nvme0n1p1
```

---

## Ollama Setup

Ollama is installed locally on the EC2 host and is required for the current architecture.

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull qwen2.5:0.5b
```

Ollama runs as a local service and exposes its inference API on `localhost:11434`. The honeypot does not require OpenAI or Gemini credentials in the current deployment.

---

## Beelzebub Deployment

```bash
git clone <repo-url>
cd beelzebub

go mod download
go build -o beelzebub .
```

The active SSH honeypot service is configured for local Ollama inference:

```yaml
plugin:
  llmProvider: "ollama"
  llmModel: "qwen2.5:0.5b"
  rateLimitEnabled: true
  rateLimitRequests: 10
  rateLimitWindowSeconds: 60
```

Run Beelzebub with the active service configuration:

```bash
./beelzebub run
```

---

## Verified Deployment State

- External SSH connections reach the honeypot on port `2222`
- Password prompt/SSH interaction is reachable from the public internet
- LLMHoneypot plugin is enabled
- Ollama local inference is functioning
- SSH commands generate dynamic LLM responses
- Structured telemetry/event logging is operational
