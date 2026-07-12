# Deploy

This folder contains deployment-related documentation and service definitions.

## Files

- `ubuntu-setup.sh` - Ubuntu setup steps for the Wraith deployment
- `beelzebub-simulator.service` - systemd unit for the honeypot service path
- `beelzebub_command_plugin.go` - reference integration helper kept as documentation support
- `beelzebub-simulator.patch` - captured patch for the Beelzebub integration path

## Notes

- The Mumbai deployment remains documented separately.
- The Wraith deployment uses systemd for persistence and runs independently from the terminal once enabled.