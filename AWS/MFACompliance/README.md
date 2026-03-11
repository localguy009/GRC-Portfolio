## Project Overview

This project implements an automated detection and alerting workflow for IAM users that are non-compliant with the AWS Config rule **`mfa-enabled-for-iam-console-access`**.

When AWS Config detects a user with console access who does not have MFA enabled, the result is surfaced as a **Security Hub CSPM finding** for control **IAM.5**.

The automation monitors Security Hub **New** findings. When a finding transitions to the **NEW** workflow state, an Amazon EventBridge rule triggers a Lambda function that:

- parses the Security Hub finding
- extracts the affected IAM user
- stores an evidence artifact in **Amazon S3**
- sends a notification through **Amazon SNS**

This workflow creates an automated audit trail and alerting mechanism for MFA compliance violations using an event-driven architecture.

## Security Framework Alignment

This project maps to compliance frameworks by enforcing strong authentication controls and detecting identity misconfigurations.
- NIST SP 800-53 Rev. 5
- CIS AWS Foundations Benchmark
- PCI DSS v4.0
- SOC 2 Trust Services Criteria

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

- **AWS Config** – Evaluates IAM user compliance with MFA requirements  
- **AWS Security Hub** – Aggregates and normalizes security findings  
- **Amazon EventBridge** – Captures Security Hub events and triggers automation  
- **AWS Lambda** – Processes findings and generates alerts  
- **Amazon SNS** – Sends alert notifications  
- **Amazon S3** – Stores evidence artifacts  
- **AWS IAM** – Provides access control for the automation components




