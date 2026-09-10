# US-East Recovery - Operational Findings

## Summary

The US-East Wraith honeypot (`wraith-us-east-static`, `us-east-1`, historically `100.27.226.37:2222`) continued to accept honeypot connections and record telemetry while administrative SSH became inaccessible. The failure was an operational boot-configuration error, not attacker activity. Recovery was performed offline via EBS disk repair with a safety snapshot, restoring admin access without loss of honeypot telemetry.

## Deployment context

- **Instance:** `wraith-us-east-static` (`us-east-1`)
- **Honeypot port:** `2222` (Beelzebub fronting Wraith deterministic shell) - verified as continuing to accept connections during the incident
- **Admin port:** `22` (restricted to operator IP)
- **Telemetry:** `wraith_logs/events.jsonl` on the instance EBS root volume

## Failure observed

- `100.27.226.37:2222` remained reachable and produced `reports/us-east/` telemetry throughout the period (12 sessions, 21103 commands from `2026-07-12` to `2026-09-06`)
- `100.27.226.37:22` returned `connection refused`
- EC2 Instance Connect failed
- SSM was unavailable (instance lacked a usable instance-management role/credentials)
- Serial console reached a Linux login prompt, confirming the OS was running

## Root cause (verified on recovered disk)

- ` /etc/systemd/system/ssh.socket -> /dev/null` (masked)
- `ssh.service` had no active boot activation path (no enabled unit or socket activation)
- Effect: `sshd` was not started at boot, so port `22` was not listening, while the honeypot on `2222` (Beelzebub + `wraith/server.py` via `deploy/beelzebub-simulator.service`) remained active as a separate service

This was a service boot-configuration error, not evidence of compromise or resource exhaustion. Do not attribute the outage to attacker action.

## Recovery procedure

1. **Telemetry preservation:** `wraith_logs/events.jsonl` was identified on the EBS root volume and preserved before any repair; a local backup archive `wraith-us-east-telemetry-backup-20260910-222309.tar.gz` is retained (gitignored) and was used to regenerate `reports/us-east/` via `scripts/generate_report_us_east.py` with test IPs excluded (`49.207.63.82`, `49.207.60.111`, `49.207.58.88`, `223.187.126.163`, `223.187.121.20`, `1.2.3.4`).

2. **Safety snapshot:** A safety snapshot of the original root EBS volume was created before any modification, allowing rollback.

3. **Offline disk repair via helper instance:**
   - Stopped the original instance (no termination)
   - Detached its root EBS volume
   - Attached it as a secondary volume to a temporary recovery helper instance
   - Mounted the volume and removed the mask: `rm /mnt/recovery/etc/systemd/system/ssh.socket` (which had been a symlink to `/dev/null`)
   - Ensured `ssh.service` is enabled for boot: `systemctl enable ssh.service` (creates appropriate `wants` symlink under `/etc/systemd/system`)
   - Verified no residual `ssh.socket` mask remains

4. **Restore:**
   - Detached the repaired volume from the helper
   - Reattached it as the root volume of the original instance
   - Started the original instance

5. **Verification:**
   - Admin SSH `22` became reachable again
   - Honeypot `100.27.226.37:2222` remained reachable
   - Systemd verified: `systemctl is-enabled ssh.service` now enabled, `ssh.socket` no longer masked
   - Beelzebub and Wraith (`wraith/server.py` via `run_server.py`/`systemd`) services were verified as active (`systemctl is-active beelzebub`/`wraith` or equivalent)
   - Telemetry file `wraith_logs/events.jsonl` intact; cumulative report regenerated and matches preserved data (12 IPs, 12 sessions, 21103 commands)

## Operational lessons

- Administrative access must remain logically and configurationally separate from honeypot services; a misconfigured `ssh.socket` mask must not be allowed to disable admin access.
- Service boot configuration (`systemctl is-enabled`, `ssh.socket`/`ssh.service` state) should be validated immediately after deployment and after any manual systemd changes (`systemctl daemon-reload` and reboot test).
- Backups and reproducible report generation are essential: the EBS snapshot and the committed `reports/us-east/` (generated via `scripts/generate_report_us_east.py --all --no-geo`) preserved the experiment despite the admin-access outage.
- Raw telemetry archives (`*.tar.gz`, `raw-data-us-east/`, `*.jsonl`) remain gitignored and are not committed; only derived Markdown reports are versioned, keeping the repository reproducible without exposing raw data.

## Relationship to experiment results

The recovery incident is operational and separate from the security experiment. No evidence indicates attacker exploitation caused the `ssh.socket` mask. All US-East results in `docs/us-east-results.md` and `reports/us-east/cumulative.md` were collected while the honeypot was continuously operational; the admin outage did not interrupt honeypot telemetry.

## Reproducibility

- Reports: `scripts/generate_report_us_east.py` with `--exclude-ip` for the six test IPs and `--out-file` redirection for daily reports; cumulative via `--all`.
- Recovery: Snapshot ID and helper instance details are operational and not committed; the procedure above is documented for repeatability without exposing credentials.
