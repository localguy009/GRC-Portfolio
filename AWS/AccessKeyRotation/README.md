## Project Overview

This project implements an automated detection and alerting workflow for IAM users that are non-compliant with the AWS Config rule **`access-keys-rotated`**.

When AWS Config detects an IAM user with an access key older than 90 days, the result is surfaced as a **Security Hub CSPM finding** for control **IAM.3**.

The automation monitors Security Hub **New** findings. When a finding transitions to the **NEW** workflow state, an Amazon EventBridge rule triggers a Lambda function that:

- parses the Security Hub finding
- extracts the affected IAM user
- stores an evidence artifact in **Amazon S3**
- sends a notification through **Amazon SNS**

This workflow creates an automated audit trail and alerting mechanism for access key rotation compliance violations using an event-driven architecture.

## Security Framework Alignment

This project maps to compliance frameworks by enforcing credential management hygiene and detecting long-lived access keys that increase the blast radius of a compromise.

- NIST SP 800-53 — IA-5 (Authenticator Management)
- CIS AWS Foundations Benchmark
- PCI DSS (Detective monitoring and audit evidence)
- SOC 2 — Detective (Security monitoring and alerting, Logical Access monitoring)

## Architecture

```text
AWS Config
   |
   v
Security Hub (Finding Generated)
   |
   v
EventBridge Rule
   |
   v
AWS Lambda
   |-- Store evidence -> Amazon S3
    -- Send alert -> Amazon SNS
```

## AWS Services Used

- **AWS Config** – Evaluates IAM access key age against the 90-day rotation threshold
- **AWS Security Hub** – Aggregates and normalizes security findings
- **Amazon EventBridge** – Captures Security Hub events and triggers automation
- **AWS Lambda** – Processes findings and generates alerts
- **Amazon SNS** – Sends alert notifications
- **Amazon S3** – Stores evidence artifacts
- **AWS IAM** – Provides access control for the automation components
