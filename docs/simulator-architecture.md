# Deterministic Fake Shell Simulator

## Purpose

Wraith now documents two deployment contexts. The Mumbai deployment is the LLM-adapted path, backed by local Ollama `qwen2.5:0.5b` on `t3.micro` (Beelzebub on `2222` in `ap-south-1`; see `experiments/mumbai/` for the July 26 OOM and networking limitation), while the US-East deployment is a deterministic shell simulator. The simulator is designed to behave like a believable Ubuntu 22.04 server for research purposes while never executing commands on the real host. Code is in `wraith/` and is verified locally; cloud instance `wraith-us-east-static` (`us-east-1`, `100.27.226.37`) was recovered via EBS repair (see `docs/us-east-recovery.md`) and produced `reports/us-east/` telemetry (12 IPs, 21103 commands).

## Intended Architecture

```
Internet attacker
  -> SSH (Beelzebub on 2222)
  -> Session handling (wraith/session_identity.py, wraith/randomizer.py)
  -> Parser (wraith/parser.py, shlex-based)
  -> Deterministic command implementation (wraith/server.py)
  -> State update (identity, filesystem, registry, privesc)
  -> Response
  -> Telemetry (wraith/telemetry.py -> wraith_logs/events.jsonl)
  -> Optional adaptive or LLM fallback (planned, not production-complete)
  -> JSONL telemetry
```

## Implemented Components (verified in repository)

- **Session identity and management:** `wraith/session_identity.py` (`SessionIdentity` with `session_id`, `attacker_ip`, `client`, `cwd`, `user`, `hostname`, `root_mode`, `history`, `environment`), `wraith/randomizer.py` (seeded `SessionRandomizer`), `wraith/server.py:24` (`FakeShellServer.create_session` with `TelemetryLogger` and `session_started` event)
- **Command parsing:** `wraith/parser.py:16` (`CommandParser.parse`, shlex, `ParsedCommand`)
- **Fake filesystem:** `wraith/filesystem.py:9` (`FakeFilesystem` with `PurePosixPath`, per-session `entries` and `files`, `mkdir`/`touch`/`ls`/`cat`/`cp`/`mv`/`rm`, `exists`, isolated per `FakeShellSession`)
- **Fake users and environment:** `wraith/session_identity.py:13` (`admin`, `db-prod-01`, `HOSTNAME`/`HOME`/`PATH` etc.), `wraith/server.py:99` deterministic outputs for `whoami`, `id`, `hostname`, `env`/`printenv`
- **Deterministic command behavior:** `wraith/server.py:88` (`handle_command` with 30+ commands: `pwd`, `whoami`, `id`, `hostname`/`hostnamectl`, `uname`, `lscpu`, `free`, `df`, `ps`, `top`, `env`, `history`, `cd`, `mkdir`, `ls`, `cat`, `touch`, `rm`, `cp`, `mv`, `head`/`tail`, `find`, `grep`, `ip a`, `ifconfig`, `ss`, `netstat`, `systemctl`, `wget`/`curl` simulated download, `sudo`/`su`)
- **Networking behavior:** `wraith/network_backend.py:8` (`NetworkBackend.simulate_fetch`, logs without real network access), `wraith/server.py:212` (`wget`/`curl` creates `/tmp/payload.sh` and records via `registry.record_download`)
- **Fake process and system information:** `wraith/server.py:119` (`ps`, `top`, `lscpu`, `free` with `65536` etc., `df`, `systemctl`, `banner` via `wraith/persona.py`)
- **Telemetry:** `wraith/telemetry.py:9` (`TelemetryLogger`, append-only `wraith_logs/events.jsonl`, `session_started`/`command_executed`/`session_ended` with `attacker_ip`, `client`, `command`, `response`, `cwd`, `latency_ms`, `timestamp`)
- **Privilege escalation simulation:** `wraith/privesc.py:7` (`PrivilegeEscalationSimulator`) and `wraith/server.py:237` (`sudo`/`su` flow, `root@db-prod-01:~#`, `sudo_attempts`)
- **Randomized and persona state:** `wraith/randomizer.py:8`, `wraith/persona.py:7` (`MachinePersona` `db-prod-01`, Ubuntu 22.04, 16 cores, 64 GB RAM, services `mysql`/`redis`/`docker` etc., seeded variation per session)
- **Integration and server layer:** `wraith/integration.py`, `wraith/server.py:280` (`start_http_server` on `127.0.0.1:8765` or `run_server.py` on `8080` with `/command` POST), `deploy/beelzebub_command_plugin.go`, `deploy/beelzebub-simulator.patch`
- **Command registry:** `wraith/registry.py:8` (`Registry` tracking `downloads` and `reverse_shells` via `record_download`/`record_reverse_shell` for `scp`/`ssh`/`wget`/`curl`)

## Key Behavior (verified)

- No runtime AI, Ollama, OpenAI, Gemini, or external model is used in the current `wraith/server.py` path; all responses are deterministic.
- Each SSH session gets a seeded randomizer so the machine appears slightly different per connection (verified in `wraith/server.py:62`).
- Files created during a session exist only in that session's in-memory `FakeFilesystem` and disappear when the session object ends; there is no cross-session disk persistence.
- Privilege escalation is simulated with a short fake `sudo`/`su` flow (`wraith/privesc.py`).
- Network commands are logged via `registry` and simulated, never executed on the host (`wraith/network_backend.py`, `wraith/server.py:212`).
- Local verification: `demo_fake_shell.py` (creates session `203.0.113.10` and runs `pwd`/`whoami`/`mkdir`/`ls`/`sudo`) and `tests/test_fake_shell.py` (4 tests: session context, `mkdir`/`ls`, `sudo` escalation, HTTP `/command` endpoint) pass.

## Planned but Not Production-Complete

- **Cross-session persistence via Redis or disk:** Not implemented. `wraith/filesystem.py` is per-session in-memory only; no Redis code present in `wraith/` (only service name in `persona.py:19`). Documented as future work.
- **Adaptive or LLM fallback:** Architecture intends deterministic semantics first with optional controlled LLM assistance for uncovered commands; no Ollama or OpenAI integration exists in `wraith/server.py` (intended flow: parser -> deterministic implementation -> optional LLM fallback). The Mumbai deployment used direct LLM emulation (local Ollama `qwen2.5:0.5b`) and its limitations motivate this hybrid direction; Wraith's fallback remains planned.
- **Cloud deployment on `wraith-us-east-static`:** Instance `wraith-us-east-static` (`us-east-1`, `100.27.226.37:2222`) was recovered (masked `ssh.socket` removed, `ssh.service` enabled) and produced telemetry from `2026-07-12` to `2026-09-06` (`reports/us-east/` 12 IPs, 21103 commands); observational comparison is in `docs/deployment-comparison.md` (caveat: different regions/periods, not controlled).

## Relationship to Mumbai

Mumbai (`ap-south-1`, `t3.micro`, Beelzebub + local Ollama `qwen2.5:0.5b`) collected 773 source IPs and 15,153 logins but only 1 command execution, with mean LLM latency 51,094 ms and OOM on July 26 (see `experiments/mumbai/`). Wraith addresses those limitations by prioritizing deterministic shell behavior; adaptive behavior is a controlled extension, not the sole source of terminal responses.
