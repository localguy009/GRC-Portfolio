# Shift Left Security — Terraform + OPA/Rego

Enforces AWS infrastructure security policies before deployment using Open Policy Agent (OPA) and Rego. Engineers cannot deploy infrastructure that exposes public attack surface without a policy violation firing first.

---

## Theme

**Minimize public exposure.**

Before any Terraform change reaches AWS, OPA evaluates the plan against three policies. If a violation is found, the deploy is blocked.

---

## Policies

| Policy | File | What It Blocks |
|--------|------|----------------|
| Deny Open SSH | `policies/deny_open_ssh.rego` | Security groups allowing port 22 from `0.0.0.0/0` |
| Deny Open RDP | `policies/deny_open_rdp.rego` | Security groups allowing port 3389 from `0.0.0.0/0` |
| Deny Public S3 | `policies/deny_public_s3.rego` | S3 buckets with public access block disabled |

---

## How It Works

```
terraform plan → tfplan.json → conftest (OPA) → PASS or DENY
```

1. Engineer writes Terraform and runs `check.sh`
2. Terraform generates a plan and converts it to JSON
3. OPA reads the plan and evaluates it against each Rego policy
4. Any violation prints a denial message and exits with a non-zero code
5. Nothing is applied until all policies pass

---

## Prerequisites

- [Terraform](https://developer.hashicorp.com/terraform/downloads)
- [conftest](https://www.conftest.dev/install/)
- AWS credentials configured (`aws configure`)

---

## Usage

```bash
chmod +x check.sh
./check.sh
```

### Example Output — Violations Found

```
FAIL - tfplan.json - main - DENIED: aws_security_group.web_server allows SSH (port 22) from 0.0.0.0/0
FAIL - tfplan.json - main - DENIED: aws_security_group.web_server allows RDP (port 3389) from 0.0.0.0/0
FAIL - tfplan.json - main - DENIED: aws_s3_bucket_public_access_block.data has block_public_acls disabled

3 tests, 0 passed, 0 warnings, 3 failures
```

### Example Output — All Clear

```
3 tests, 3 passed, 0 warnings, 0 failures
```

---

## NIST SP 800-53 Control Mapping

| Policy | Control | Control Name |
|--------|---------|--------------|
| Deny Open SSH | AC-17 | Remote Access |
| Deny Open RDP | AC-17 | Remote Access |
| Deny Open SSH / RDP | CM-7 | Least Functionality |
| Deny Public S3 | AC-3 | Access Enforcement |
| Deny Public S3 | SC-28 | Protection of Information at Rest |

---

## Project Structure

```
ShiftLeftOPA/
├── main.tf                      # Demo Terraform with intentional violations
├── policies/
│   ├── deny_open_ssh.rego       # Blocks port 22 open to the internet
│   ├── deny_open_rdp.rego       # Blocks port 3389 open to the internet
│   └── deny_public_s3.rego      # Blocks S3 public access block being disabled
├── check.sh                     # Runs plan → JSON → OPA evaluation
└── README.md
```

---

## Why This Matters

Misconfigurations are the leading cause of cloud security incidents. Open SSH, open RDP, and public S3 buckets are consistently in the top findings across AWS environments. This project enforces guardrails at the point where engineers are writing infrastructure code — before anything is deployed — rather than detecting violations after the fact.


