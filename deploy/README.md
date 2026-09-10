# Deploy

This folder contains deployment-related documentation and service definitions for the Wraith cloud path (local implementation verified; cloud instance `wraith-us-east-static` recovered via EBS repair, see `docs/us-east-recovery.md`).

## Files

- `ubuntu-setup.sh` - Ubuntu setup steps for the Wraith deployment (local verification)
- `beelzebub-simulator.service` - systemd unit for the honeypot service path (verified active after `wraith-us-east-static` recovery)
- `beelzebub_command_plugin.go` - reference integration helper kept as documentation support (Beelzebub -> `wraith/server.py` HTTP `/command`)
- `beelzebub-simulator.patch` - captured patch for the Beelzebub integration path

## Notes

- The Mumbai deployment (`ap-south-1`, `t3.micro`, Beelzebub + local Ollama `qwen2.5:0.5b`, period `2026-07-03T18:59:13Z` - `2026-07-26T17:23:56Z`) remains documented separately in `experiments/mumbai/`.
- The Wraith deterministic shell is implemented locally (`wraith/`, `run_server.py`, `demo_fake_shell.py`, `tests/test_fake_shell.py`); cloud instance `wraith-us-east-static` (`us-east-1`, `100.27.226.37`) was recovered (masked `ssh.socket` removed, `ssh.service` enabled, snapshot before repair) and produced `reports/us-east/` telemetry (12 IPs, 21103 commands, see `docs/us-east-results.md`).
- Wraith uses systemd for persistence (`beelzebub-simulator.service`) and runs independently from the terminal once enabled - verified active after recovery.