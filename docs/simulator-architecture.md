# Deterministic Fake Shell Simulator

## Purpose

Wraith now documents two deployment contexts. The Mumbai deployment is the LLM-adapted path, backed by Ollama and the Gwen model, while the us-east-1/Virginia deployment uses a local deterministic shell simulator. The simulator is designed to behave like a believable Ubuntu 22.04 server for research purposes while never executing commands on the real host.

## Architecture

```text
Internet attacker
  -> SSH
  -> Beelzebub
  -> Fake shell simulator
  -> realistic Linux output
  -> JSONL telemetry
```

## Components

- Session management: per-connection state with isolated filesystem and history
- Filesystem: fake POSIX-style directory tree for the length of a session
- Parser: simple shell-like command parsing
- Registry: stores download URLs, reverse shell payloads, and other telemetry markers
- Persona: machine metadata such as hostname, OS, CPU, RAM, and services
- Network backend: simulated fetches and outbound behavior without real network access
- Telemetry logger: appends structured JSONL events for later syncing

## Key Behavior

- No runtime AI, Ollama, OpenAI, Gemini, or external model is used in the static-shell deployment.
- Each SSH session gets a seeded randomizer so the machine appears slightly different per connection.
- Files created during a session disappear when the session ends.
- Privilege escalation is simulated with a short fake sudo/su flow.
- Network commands are logged and simulated, never executed.
