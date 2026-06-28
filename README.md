# Wraith: LLM-SSH Honeypot on AWS

## Overview

Wraith is an LLM-powered SSH honeypot system deployed on AWS EC2 using the Beelzebub deception framework. It is designed to simulate realistic interactive Linux environments in order to study real-world attacker behavior and collect structured telemetry from malicious SSH sessions.

Unlike traditional static honeypots, Wraith integrates Large Language Models (LLMs) to dynamically generate terminal responses, increasing realism and enabling deeper analysis of attacker interaction patterns and decision-making behavior.

---

## What This Project Does

Wraith deploys fake SSH services on AWS that attract real-world attackers and log their activity in detail. Instead of returning static or predefined responses, the system uses LLMs to simulate a real Linux shell environment, making interactions more believable and increasing the depth of collected threat intelligence.

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
| LLM Backend | OpenAI / Ollama (extensible) |
| Session State | In-memory (current phase) |
| Logging | Structured JSON telemetry |

---