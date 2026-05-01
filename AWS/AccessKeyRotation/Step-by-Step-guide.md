
# Step-by-Step Build Guide

This guide walks through how to build the IAM access key rotation compliance alerting workflow step by step.

## Prerequisites

Before building this workflow, make sure the following are in place.
- AWS Config
- AWS Security Hub
- Amazon EventBridge
- AWS Lambda
- Amazon SNS
- Amazon S3
- IAM roles and policies

The following services should be enabled:

- **AWS Config** enabled
- **Security Hub** enabled
- **CloudTrail** enabled
- **EventBridge** available on the default event bus

### Storage and alerting

You will need:

- an **S3 bucket** for evidence files
- an **SNS topic** with a confirmed email subscription for alerts

### Lambda requirements

You will need a Lambda execution role with permission to:

- write logs to CloudWatch
- write objects to S3
- publish messages to SNS


## Step 1 — Verify the Access Key Rotation Config Rule

This guide assumes the AWS Config managed rule **`access-keys-rotated`** is already enabled and identifying non-compliant IAM users.

The goal of this step is to confirm that AWS Config is already detecting IAM users who have access keys older than 90 days.

### Navigate to AWS Config

1. Open the **AWS Management Console**
2. Navigate to **AWS Config**
3. Select **Rules** from the left navigation menu
4. Locate the rule `access-keys-rotated`

If the rule is not present, add it:

1. Click **Add rule**
2. Search for `access-keys-rotated`
3. Select the rule
4. Set the parameter `maxAccessKeyAge` to `90`
5. Click **Next** and save the rule

## Step 2 — Verify the Finding in Security Hub

### Navigate to Security Hub

1. Open the **AWS Management Console**
2. Navigate to **Security Hub**
3. Select **Findings**
4. Filter by control ID **IAM.3** or search for `access-keys-rotated`


## Step 3 — Create an S3 Bucket for Evidence Storage

Name: `access-key-rotation-evidence`

This stores evidence artifacts for each access key rotation compliance finding in Amazon S3.
These JSON files act as an audit trail showing when a non-compliant IAM user was detected.

Each file will contain details about the Security Hub finding, including:

- IAM user involved
- Compliance status
- AWS account ID
- Severity
- Timestamp

Evidence files will be written into the following prefix:
```
access-key-rotation-evidence/2026-03-10-14-02-13.json
```


## Step 4 — Create an SNS Topic for Alert Notifications

The next step is to create an Amazon SNS topic that will send alert notifications when a non-compliant access key rotation finding is detected.

The Lambda function will publish messages to this topic whenever it processes a relevant Security Hub finding.

### Create the SNS topic

1. Open the **AWS Management Console**
2. Navigate to **Amazon SNS**
3. Select **Topics** > **Standard**
4. Click **Create topic**

| Name | `access-key-rotation-alerts` |

Next, create a subscription so alerts are sent to your email. Click your topic > Subscriptions > Create subscription > Protocol > Email
> **Endpoint** (insert your email for alerts here)

## Step 5 — Create the Lambda Execution Role

The Lambda function needs permission to interact with other AWS services.
This role will allow Lambda to:
- Write evidence files to **Amazon S3**
- Send alert messages to **Amazon SNS**
- Write execution logs to **CloudWatch Logs**

1. Navigate to IAM
2. AWS Console → IAM → Roles → Create role
3. Select the trusted entity
   - Choose: AWS Service
   - Use Case: Lambda
4. Click Next → Next → Role name: `access_key_rotation_check`

Create an Inline Policy
(replace region & account-id)
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "WriteEvidenceToS3",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::access-key-rotation-evidence/*"
    },
    {
      "Sid": "PublishToSNSTopic",
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:<region>:<account-id>:access-key-rotation-alerts"
    },
    {
      "Sid": "CloudWatchLogging",
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "*"
    }
  ]
}
```

## Step 6 — Create the Lambda Function

The Lambda function processes Security Hub findings related to access key rotation compliance.
When a non-compliant finding is detected, the function will:

- extract the affected IAM user
- store evidence in **Amazon S3**
- send an alert through **Amazon SNS**


### Create the Lambda function

1. Open the **AWS Management Console**
2. Navigate to **AWS Lambda**
3. Click **Create function**

### Configure the function

Choose the following settings:

| Setting | Value |
|---------|-------|
| Function type | Author from scratch |
| Function name | `access_key_rotation_handler` |
| Runtime | Python 3.11 |
| Architecture | x86_64 (default) |
| Execution role | Use existing role |
| Existing role | `access_key_rotation_check` |

### Configure environment variables

Next, add environment variables that allow the Lambda function to locate the S3 bucket and SNS topic.

1. Open the Lambda function
2. Select **Configuration → Environment variables**
3. Click **Edit**
4. Add the following variables:

| Key | Value |
|-----|-------|
| `BUCKET_NAME` | `access-key-rotation-evidence` |
| `SNS_TOPIC_ARN` | `arn:aws:sns:<region>:<account-id>:access-key-rotation-alerts` |


## Step 7 — Add the Lambda Function Code

The next step is to add the Python script that processes access key rotation compliance findings.

The Lambda function will:

- process Security Hub findings related to access key rotation compliance
- identify IAM users with access keys older than 90 days
- store evidence artifacts in **Amazon S3**
- send alert notifications using **Amazon SNS**

### Upload the Lambda code

The full Lambda implementation is included in this repository: lambda.py

### Add the code to the Lambda function

1. Open the **AWS Management Console**
2. Navigate to **AWS Lambda**
3. Select the function **`access_key_rotation_handler`**
4. Go to the **Code** tab
5. Replace the default Lambda code with lambda.py
6. Click **Deploy**


### Test the Lambda Function

You can test the Lambda function directly using a sample Security Hub finding.

1. In the Lambda console, select **Test**
2. Create a new **test event**
3. Use the following sample event:

```json
{
  "detail": {
    "findings": [
      {
        "Id": "test-finding-001",
        "AwsAccountId": "123456789012",
        "Title": "IAM user access keys should be rotated every 90 days or less",
        "Severity": {
          "Label": "MEDIUM"
        },
        "Compliance": {
          "SecurityControlId": "IAM.3",
          "Status": "FAILED"
        },
        "Workflow": {
          "Status": "NEW"
        },
        "RecordState": "ACTIVE",
        "Resources": [
          {
            "Id": "arn:aws:iam::123456789012:user/test_user_old_key"
          }
        ]
      }
    ]
  }
}
```

If the function is configured correctly, the test should: generate a JSON evidence file in S3 & send a notification through SNS

## Step 8 — Create the EventBridge Rule & Define the Target

1. Open the AWS Management Console
2. Navigate to Amazon EventBridge
3. Select Rules
4. Click **Create rule** then **Configure**

### Configure the rule

| Setting | Value |
|---------|-------|
| Rule name | `access_key_securityhub_trigger` |
| Event bus | `default` |
| Rule type | Rule with an event pattern |

### Define the Event Pattern

```json
{
  "source": ["aws.securityhub"],
  "detail-type": ["Security Hub Findings - Imported", "Security Hub Findings - Updated"]
}
```

### Define the Target

This tells EventBridge what action to take when the rule is triggered.

1. Scroll to the **Target** section
2. For **Target type**, select **AWS service**
3. For **Select a target**, choose **Lambda function**
4. From the **Function dropdown**, select `access_key_rotation_handler`
5. Leave **Additional settings** as default
6. Click **Next**
7. Review the configuration
8. Click **Create rule**

Once created, EventBridge will automatically invoke the **access_key_rotation_handler Lambda function** whenever the defined Security Hub event occurs.

> **Note:** When you select a Lambda function as the target in EventBridge via the console, AWS automatically adds the required resource-based policy to allow EventBridge to invoke the function. No manual policy configuration is needed.

## Two Ways to Trigger a Test Finding

### Method 1 — Create a Non-Compliant IAM User

You can generate a real finding by creating a test user with an access key and waiting for AWS Config to flag it. However, since the rule evaluates key age, a newly created key will not immediately be non-compliant.

A faster alternative is to temporarily set `maxAccessKeyAge` to `1` on the Config rule, which will flag any key older than one day. After confirming the workflow fires, reset the parameter back to `90`.

---

### Method 2 — Trigger from Security Hub (Faster)

The faster method is to update the workflow status of an existing finding.

1. Open **AWS Security Hub**
2. Navigate to **CSPM → Findings**
3. Locate the **IAM.3** finding (`access-keys-rotated`)
4. Select the finding
5. Change the **Workflow Status**

Example:

NEW → RESOLVED → NEW

When the finding transitions from **RESOLVED back to NEW**, the automation triggers:

- **SNS alert is sent**
- **Evidence is saved to S3**

This approach is useful for testing because it triggers immediately without waiting for AWS Config evaluation.
