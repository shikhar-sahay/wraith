# AWS Infrastructure Setup

## Account Security

* Root MFA enabled
* Zero spend budget configured
* Billing alerts configured
* IAM user created for operational access

## Compute Infrastructure

* EC2 instance type: t3.micro
* Region: ap-south-1
* Ubuntu Server deployed
* Elastic IP attached

## Network Configuration

Port 22/tcp
Restricted to administrator IP only

Port 2222/tcp
Exposed publicly for SSH honeypot traffic

## Deployment

* SSH access verified
* Go runtime installed
* Beelzebub repository cloned
* Framework compiled successfully
* SSH deception runtime deployed successfully
