# EC2 Configuration

## Host

- **Mumbai (`wraith-honeypot`):** Platform: AWS EC2, Operating system: Ubuntu 24.04 LTS, Region: `ap-south-1`, Instance type: `t3.micro`, Elastic IP: attached - completed
- **Wraith historical (`wraith-us-east-static`):** Region: `us-east-1`, historically `100.27.226.37` - currently inaccessible, recovery pending; not yet validated

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

- **Mumbai (`ap-south-1`):** Beelzebub compiled successfully, SSH honeypot reachable externally on port `2222` during `2026-07-03` - `2026-07-26`, Ollama `qwen2.5:0.5b` installed locally, local inference working with high latency and eventual OOM, structured telemetry operational - completed and investigated
- **Wraith (`us-east-1` historical):** Local shell implementation verified (`wraith/` + tests), but cloud instance `wraith-us-east-static` is pending recovery (admin `22` refused, SSM unavailable); no cloud telemetry validated yet
