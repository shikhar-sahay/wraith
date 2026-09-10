# Mumbai Incident - Resource Exhaustion and Telemetry Interruption

## Summary

On `2026-07-26` the Mumbai honeypot (`wraith-honeypot`, `ap-south-1`, `t3.micro`, Ubuntu 24.04, Beelzebub `2222` + local Ollama `qwen2.5:0.5b`) experienced resource exhaustion from local LLM inference that triggered a kernel OOM condition. The honeypot and OS did not simply crash. Beelzebub remained alive for ~6 minutes after the OOM kill, but guest-networking subsequently degraded, preventing further external telemetry. The instance remained powered on until a `2026-09-10` reboot restored full service. Telemetry was preserved and reports were regenerated.

## Timeline (UTC, `2026-07-26`)

- **~17:17-17:18:** Local Ollama invoked the Linux OOM killer
  - `llama-server` killed, observed RSS ~629 MB
  - `systemd-journald` watchdog failure
  - `snapd` watchdog failure
  - Kernel log: `Out of memory: Killed process ... (llama-server)` (indicator, not attacker action)

- **17:17-17:23:** Honeypot and OS remained alive
  - Beelzebub did **not** immediately terminate
  - Honeypot continued processing events until at least last confirmed attacker event `2026-07-26T17:23:56Z` (from `cumulative.md` period and `2026-07-26.md`)
  - Normal `cron`/`sysstat` activity continued afterward (evidence OS not crashed)

- **~17:44:** Guest-network degradation observed
  - `169.254.169.254` (instance metadata service) became unreachable from the guest
  - DNS through `127.0.0.53` reported problems
  - SSM agent could not reach AWS endpoints
  - OS still executing scheduled work, but external honeypot connectivity was no longer viable

- **2026-07-26 17:23:56Z:** Last confirmed surviving attacker event; telemetry collection stopped thereafter (no reports after `2026-07-26.md`)

- **2026-07-26 - 2026-09-10:** EC2 instance remained powered on, not intentionally stopped; boot history shows continuous uptime until reboot

- **2026-09-10:** Reboot performed
  - Administrative SSH `22` became reachable (restricted to operator IP)
  - Honeypot `100.27.226.37:2222` (Mumbai public IP, not to be confused with US-East `100.27.226.37` historical) became reachable (in Mumbai context, `wraith-honeypot` public IP)
  - Beelzebub started normally
  - Ollama `qwen2.5:0.5b` started normally

## Root cause analysis

- **Resource exhaustion:** Local `qwen2.5:0.5b` inference on `t3.micro` (~1 GB RAM class) under sustained Internet-facing load from `2026-07-03` to `2026-07-26` (773 IPs, 942 sessions, 15153 logins) accumulated memory pressure. Average LLM latency 51,094 ms and 646 calls indicate substantial overhead.
- **OOM condition:** Kernel OOM killer terminated `llama-server` (~629 MB RSS). This is a resource-isolation failure, not a compromise.
- **Guest-network degradation:** Secondary effect after OOM; `systemd-journald` and `snapd` pressure plus networking stack degradation prevented external honeypot connectivity, even though Beelzebub and cron remained alive briefly.
- **Not the cause:** Plugin rate limiting (`Rate limit exceeded`, `plugin "LLMHoneypot" execute error: rate limited` from `39.105.172.20` `echo -e "\x6F\x6B"` loop with 285 sessions on `2026-07-26` and inconsistent `qwen2.5:0.5b` responses) was an observed LLM terminal limitation **before** the outage, not the outage cause. Stronger infrastructure evidence is OOM/resource exhaustion followed by guest-network degradation.
- **Not a crash:** Avoid wording `server crashed`. Use precise: `resource exhaustion`, `OOM condition`, `degraded guest networking`, `telemetry interruption`, `operational reliability limitation` on this `t3.micro` configuration.

## Telemetry impact

- No attacker telemetry after `2026-07-26T17:23:56Z` exists; daily reports `2026-07-27` through `2026-09-09` are not present (not fabricated).
- `2026-07-01` remains validation-only (0 IPs, 0 sessions, 6 LLM calls)
- `2026-07-05.md` remains intentionally absent (stale without source)
- All 24 dated reports plus `cumulative.md` were regenerated from surviving Beelzebub logs via `scripts/generate_report.py` with test IPs `49.207.63.82`, `49.207.60.111`, `49.207.58.88` excluded.
- No log data was altered; reports are reproducible.

## Recovery implications and lessons

- Lightweight deterministic interaction is valuable for resource-constrained deployments (`t3.micro` cannot sustain per-connection `qwen2.5:0.5b` inference).
- LLM-backed honeypots need explicit resource isolation and limits (memory, concurrency, timeout) to avoid OOM on small instances.
- Telemetry pipelines should separate raw volume from normalized engagement and preserve reports reproducibly (EBS snapshot not needed here; Mumbai recovery was log regeneration, unlike US-East EBS repair).
- Administrative access separation (`22` restricted) was correct and unaffected; the failure was guest-internal resource exhaustion, not security-group exposure.
- Backups and reproducible report generation proved essential for preserving the experiment despite the interruption.

## Relationship to US-East and Wraith

Mumbai's failure directly motivates Wraith's hybrid direction: deterministic shell semantics first (`wraith/server.py` etc.), with optional controlled LLM assistance rather than per-command LLM emulation. US-East's Wraith deployment (`us-east-1`, `100.27.226.37`) uses this deterministic path and did not exhibit OOM, indicating better resilience and operational simplicity, though it experienced a separate operational failure (masked `ssh.socket`, see `docs/us-east-recovery.md`) - also an operational reliability lesson, not a security result.
