# EC2 Configuration

## Host

- Platform: AWS EC2
- Operating system: Ubuntu server
- Region: `ap-south-1`
- Instance type: `t3.micro`
- Elastic IP: attached

## Storage

The EC2 volume was expanded from 8GB to 15GB because the original disk size was too small for local Ollama model storage.

Filesystem expansion commands used on the instance:

```bash
sudo growpart /dev/nvme0n1 1
sudo resize2fs /dev/nvme0n1p1
```

## Runtime Components

- Go runtime for building Beelzebub
- Beelzebub deception framework
- LLMHoneypot plugin
- Ollama local inference service
- `qwen2.5:0.5b` local model

## Active Ports

| Port | Service | Exposure |
|------|---------|----------|
| `22` | Real SSH admin access | Restricted |
| `2222` | SSH honeypot | Public |
| `11434` | Ollama API | Internal only |

## Current Status

- Beelzebub compiled successfully
- SSH honeypot reachable externally on port `2222`
- Ollama installed locally
- `qwen2.5:0.5b` installed locally
- Local inference working
- Structured telemetry/event logging operational
