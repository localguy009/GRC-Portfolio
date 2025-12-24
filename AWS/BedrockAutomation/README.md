# AWS Security Hub Risk Reporting with Amazon Bedrock

## Overview

This project demonstrates how Amazon Bedrock can be used to generate executive-level security risk summaries from AWS Security Hub findings. I built a Lambda function that retrieves and condenses active findings, then invokes a Bedrock-hosted large language model to analyze risk and produce a structured Markdown report.

**High-level flow:**

1. AWS Security Hub collects and normalizes security findings.
2. AWS Lambda retrieves active Security Hub findings.
3. Findings are condensed to reduce noise and token usage.
4. Amazon Bedrock (Claude) analyzes the findings and generates:
   - Executive Summary
   - Top Risks
   - Recommended Actions
5. The findings report is written to Amazon S3 as audit-ready evidence.


## What the Lambda Function Does

- Pulls active findings from AWS Security Hub
- Extracts only security-relevant fields:
  - Finding title
  - Severity
  - Affected resource
  - Region
  - Remediation recommendation
- Builds a structured prompt for Amazon Bedrock
- Generates an **executive-level risk report
- Stores the report in S3 as `securityhub-risk-report.md`

---

## Example Output Structure

The generated report includes:

```text
## Executive Summary
High-level overview of the current AWS security posture.

## Top Risks
Prioritized security risks based on severity and impact.

## Recommended Actions
Clear, actionable remediation steps.
