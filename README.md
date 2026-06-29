# Wraith: LLM-Powered SSH Honeypot on AWS

## Overview

Wraith is an LLM-powered SSH honeypot system deployed on AWS EC2 using the Beelzebub deception framework. It is designed to simulate realistic interactive Linux environments in order to study real-world attacker behavior and collect structured telemetry from malicious SSH sessions.

Unlike traditional static honeypots, Wraith integrates Large Language Models (LLMs) to dynamically generate terminal responses, increasing realism and enabling deeper analysis of attacker interaction patterns and decision-making behavior.

The current implementation uses **Ollama running locally on the EC2 instance** with the `qwen2.5:0.5b` model. Wraith no longer depends on paid cloud LLM APIs for the active MVP deployment.

---

## What This Project Does

Wraith deploys a fake SSH service on AWS that attracts real-world attackers and logs their activity in detail. Instead of returning static or predefined responses, the system routes attacker commands through Beelzebub's LLMHoneypot plugin to a local Ollama model, generating dynamic Linux terminal responses and structured telemetry.

Current high-level flow:

```text
Internet -> AWS EC2 -> Beelzebub -> SSH Honeypot -> LLMHoneypot Plugin -> Ollama -> qwen2.5:0.5b -> Dynamic Terminal Output -> Structured Telemetry Logging
```

The current MVP is deployed and functioning: external SSH connections reach the honeypot on port `2222`, local LLM inference is working, and structured event logging has been confirmed.

---

## Research Goals

- Evaluate whether LLM-powered honeypots increase attacker engagement compared to static systems
- Compare different LLM backend strategies for response generation
- Analyze SSH attack patterns across real-world internet sources
- Measure session depth, duration, and interaction complexity
- Investigate whether increased realism affects credential brute-force behavior and persistence

---

## Tech Stack

| Component | Tool |
|----------|------|
| Cloud | AWS EC2 |
| Honeypot Framework | Beelzebub |
| Active LLM Backend | Ollama local inference |
| Active Model | qwen2.5:0.5b |
| Session State | In-memory (current phase) |
| Logging | Structured JSON telemetry |

---

## Current Deployment State

- AWS EC2 Ubuntu server deployed and reachable
- Security groups configured for admin SSH and public honeypot SSH
- Beelzebub framework installed and running
- SSH honeypot exposed on port `2222`
- Ollama installed locally on the EC2 instance
- `qwen2.5:0.5b` model installed locally
- LLM-generated terminal responses confirmed
- Structured telemetry/event logging confirmed

---

## LLM Backend Status

OpenAI and Gemini were evaluated during development, but they are not the active deployment backend. OpenAI required paid API access, and Gemini's free tier quotas were too restrictive for sustained honeypot traffic.

The active backend is Ollama because it is free, local, offline-capable, and avoids API keys or quota limits.

---

## Current Limitation

The honeypot is functional, but terminal realism still needs refinement. Some generated shell outputs, such as inconsistent fake paths from commands like `pwd`, can be unrealistic. The next technical focus is prompt engineering inside the LLM plugin to improve shell-state consistency.
