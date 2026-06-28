```markdown
# AWS Deployment Notes

## Infrastructure

- EC2 Ubuntu instance
- Public SSH exposure:
  - Port 22 → Admin access
  - Port 2222 → Honeypot SSH service

---

## Services Running

| Service | Port | Purpose |
|--------|------|--------|
| Beelzebub Core | internal | orchestration engine |
| SSH Honeypot | 2222 | attacker interaction |
| Prometheus | 2112 | metrics (optional) |

---

## Deployment Steps

```bash
git clone <repo-url>
cd beelzebub

go mod download
go build -o beelzebub .

./beelzebub run \
  --conf-core ./configurations/beelzebub.yaml \
  --conf-services ./configurations/services/