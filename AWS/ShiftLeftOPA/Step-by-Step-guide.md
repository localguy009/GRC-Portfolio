# Step-by-Step Build Guide

This guide walks through how to use OPA and Rego to enforce security policies against Terraform infrastructure before it is ever deployed to AWS. You will intentionally deploy misconfigured infrastructure, watch the policies catch it, fix the violations, and confirm everything passes.

---


## Prerequisites

Before starting, make sure the following tools are installed on your machine.

| Tool | Purpose | Install |
|------|---------|---------|
| Terraform | Generates the infrastructure plan | [terraform.io](https://developer.hashicorp.com/terraform/downloads) |
| conftest | Runs OPA policies against the plan | [conftest.dev](https://www.conftest.dev/install/) |
| AWS CLI | Authenticates to AWS | [aws.amazon.com/cli](https://aws.amazon.com/cli/) |

You will also need:
- An AWS account with credentials configured (`aws configure`)
- A default VPC in `us-east-1` (AWS creates this by default)

---

## Step 1 — Clone the Repository

```bash
git clone https://github.com/localguy009/GRC-Portfolio.git
cd GRC-Portfolio/AWS/ShiftLeftOPA
```

---

## Step 2 — Review the Project Structure

Before running anything, take a few minutes to understand what is here.

```
ShiftLeftOPA/
├── main.tf                        # Terraform with intentional violations
├── policies/
│   ├── deny_open_ssh.rego         # Blocks port 22 open to 0.0.0.0/0
│   ├── deny_open_rdp.rego         # Blocks port 3389 open to 0.0.0.0/0
│   └── deny_public_s3.rego        # Blocks S3 public access block being disabled
├── check.sh                       # Script that runs the full evaluation
└── README.md
```

Open `main.tf` and read through it. You will notice three intentional violations marked with comments. These simulate what an engineer might accidentally deploy.

Open each `.rego` file in the `policies/` folder. Each one contains a rule that checks for one specific misconfiguration.

---

## Step 3 — Understand What the Policies Are Checking

Before running the check, it helps to understand what each policy does.

### deny_open_ssh.rego
Looks at every `aws_security_group` resource in the Terraform plan. If any ingress rule allows port 22 from `0.0.0.0/0`, the policy fires and blocks the deploy.

**Why this matters:** Exposing SSH to the entire internet is one of the most common entry points for attackers.

### deny_open_rdp.rego
Same logic as SSH but checks port 3389. RDP is the Windows remote desktop protocol.

**Why this matters:** Open RDP is frequently exploited in ransomware attacks.

### deny_public_s3.rego
Looks at every `aws_s3_bucket_public_access_block` resource. If `block_public_acls` or `block_public_policy` is set to `false`, the policy fires.

**Why this matters:** Public S3 buckets have caused some of the largest data breaches in cloud history.

---

## Step 4 — Initialize Terraform

Run the following command to download the AWS provider plugin.

```bash
terraform init
```

You should see output ending with:

```
Terraform has been successfully initialized!
```

---

## Step 5 — Run the Security Check

Run the check script. This will generate a Terraform plan, convert it to JSON, and evaluate it against all three Rego policies.

```bash
chmod +x check.sh
./check.sh
```

### What is happening behind the scenes

```
terraform plan      → generates what AWS would build
terraform show      → converts that plan to JSON
conftest test       → OPA reads the JSON and evaluates each Rego policy
```

### Expected output — violations found

You should see three failures, one for each intentional misconfiguration in `main.tf`.

```
FAIL - tfplan.json - main - DENIED: aws_security_group.web_server allows SSH (port 22) from 0.0.0.0/0 — restrict to a known IP range.
FAIL - tfplan.json - main - DENIED: aws_security_group.web_server allows RDP (port 3389) from 0.0.0.0/0 — restrict to a known IP range.
FAIL - tfplan.json - main - DENIED: aws_s3_bucket_public_access_block.data has block_public_acls disabled — S3 buckets must block public access.
FAIL - tfplan.json - main - DENIED: aws_s3_bucket_public_access_block.data has block_public_policy disabled — S3 buckets must block public access.

4 tests, 0 passed, 0 warnings, 4 failures, 0 exceptions
```

This is the expected result. Nothing has been deployed to AWS. The policies caught the violations before anything was applied.

---

## Step 6 — Fix the Violations

Now open `main.tf` and fix each violation one at a time.

### Fix 1 — Remove open SSH

Find the ingress block for port 22 and replace `0.0.0.0/0` with a specific IP range.

**Before:**
```hcl
ingress {
  description = "SSH"
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}
```

**After:**
```hcl
ingress {
  description = "SSH"
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["10.0.0.0/8"]
}
```

### Fix 2 — Remove open RDP

Find the ingress block for port 3389 and apply the same fix.

**Before:**
```hcl
ingress {
  description = "RDP"
  from_port   = 3389
  to_port     = 3389
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]
}
```

**After:**
```hcl
ingress {
  description = "RDP"
  from_port   = 3389
  to_port     = 3389
  protocol    = "tcp"
  cidr_blocks = ["10.0.0.0/8"]
}
```

### Fix 3 — Block public S3 access

Find the `aws_s3_bucket_public_access_block` resource and set all values to `true`.

**Before:**
```hcl
resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = false
  block_public_policy     = false
  ignore_public_acls      = false
  restrict_public_buckets = false
}
```

**After:**
```hcl
resource "aws_s3_bucket_public_access_block" "data" {
  bucket                  = aws_s3_bucket.data.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}
```

---

## Step 7 — Run the Check Again

```bash
./check.sh
```

### Expected output — all clear

```
4 tests, 4 passed, 0 warnings, 0 failures, 0 exceptions
```

All policies pass. The infrastructure is now safe to deploy.

---

## Step 8 — Deploy the Infrastructure (Optional)

If you want to deploy the compliant infrastructure to your AWS account:

```bash
terraform apply
```

Review the plan output and type `yes` to confirm.

To tear it down when finished:

```bash
terraform destroy
```

---

## What You Just Did

| Action | What It Demonstrates |
|--------|---------------------|
| Wrote Rego policies | Policy-as-code: security rules are version controlled just like application code |
| Generated a Terraform plan | Infrastructure decisions are captured before anything is deployed |
| Evaluated the plan with OPA | Security is enforced at the earliest possible point in the workflow |
| Fixed violations and re-ran | The feedback loop that shift left security is built around |

---

## NIST SP 800-53 Control Mapping

| Policy | Control | Control Name |
|--------|---------|--------------|
| Deny Open SSH | AC-17 | Remote Access |
| Deny Open RDP | AC-17 | Remote Access |
| Deny Open SSH / RDP | CM-7 | Least Functionality |
| Deny Public S3 | AC-3 | Access Enforcement |
| Deny Public S3 | SC-28 | Protection of Information at Rest |
