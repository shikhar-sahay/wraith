# Wraith

Wraith is a cloud-native adaptive SSH deception framework built on top of Beelzebub for collecting and analyzing real-world attacker telemetry.

The project focuses on deploying interactive SSH honeypots on AWS infrastructure, integrating adaptive LLM-generated responses, collecting attacker interaction data, and analyzing real-world attack behavior.

## Objectives

* Deploy a publicly accessible SSH honeypot on AWS EC2
* Simulate realistic attacker interaction using LLM-powered deception
* Collect and persist attacker telemetry
* Analyze attacker behavior patterns and command execution
* Compare static vs adaptive honeypot effectiveness

## Stack

* AWS EC2
* Beelzebub
* SSH Deception Runtime
* Python Telemetry Processing
* Amazon S3 Log Storage
* Grafana / Prometheus (planned)
* LLM Integration (planned)

## Current Status

* AWS infrastructure deployed
* EC2 instance running
* Elastic IP configured
* Security groups configured
* Beelzebub compiled successfully
* SSH deception service live on port 2222
