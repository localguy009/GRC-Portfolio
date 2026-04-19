# AWS Multi-Account Guardrails with Service Control Policies (SCPs)

## Overview

This lab demonstrates how to implement preventive cloud governance controls using AWS Service Control Policies (SCPs) across Development and Production environments.

The project simulates a real-world multi-account AWS architecture and shows how governance requirements can be enforced through non-bypassable controls at the organizational level.

---


## Objectives

- Build a multi-account AWS Organization
- Separate Development and Production environments using OUs
- Implement preventive guardrails using SCPs
- Enforce cost, region, and security controls
- Validate that controls work through testing

---

## Controls Implemented

###  Development Guardrails

**EC2 Instance Restrictions**
- Limits instance types to approved low-cost options
- Prevents oversized or unnecessary compute usage

**Region Restrictions**
- Allows deployments only in:
  - `us-east-1`
  - `us-east-2`
- Reduces data sprawl and limits attack surface

---

###  Production Guardrails

**CloudTrail Protection**
- Prevents:
  - StopLogging
  - DeleteTrail
- Ensures audit logging cannot be disabled

## Framework Alignment

This implementation aligns with common GRC frameworks:

### NIST SP 800-53
- **AC-3** – Access Enforcement  
- **AC-6** – Least Privilege  
- **AU-2 / AU-6** – Audit Logging  
- **CM-5 / CM-6** – Configuration Control  


