# LLM-SSH Honeypot on AWS

## Overview

This project deploys an LLM-powered SSH honeypot using the Beelzebub deception framework on AWS EC2. It is designed to simulate realistic interactive Linux environments in order to study real-world attacker behavior and collect structured telemetry from malicious SSH sessions.

Unlike traditional static honeypots, this system integrates Large Language Models (LLMs) to dynamically generate terminal responses, increasing realism and enabling deeper attacker interaction analysis.

## Key Features

- Fully functional SSH honeypot deployed on AWS EC2
- LLM-powered command response generation (OpenAI / Ollama compatible)
- Multi-service deception framework (SSH, HTTP, TCP, Telnet)
- Structured telemetry logging of attacker sessions
- Plugin-based architecture for extensibility
- Support for static, adaptive, and persistent deception modes

## Research Goals

- Evaluate whether LLM-driven honeypots increase attacker engagement
- Compare static vs adaptive deception models
- Analyze SSH attack behavior across real-world IP sources
- Measure session depth, duration, and interaction complexity
- Investigate whether realism affects credential brute-force behavior

## Current Status

- SSH honeypot deployed and functional on AWS EC2
- Beelzebub framework running with LLMHoneypot plugin enabled
- Telemetry logging verified
- LLM backend integration currently requires valid API key and billing-enabled provider

## Known Limitation

- LLM provider currently requires paid API quota (OpenAI exhausted during testing)
- System falls back to static responses ("command not found") when LLM is unavailable