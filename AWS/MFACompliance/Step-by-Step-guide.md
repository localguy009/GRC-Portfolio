
# Step-by-Step Build Guide  

This guide walks through how to build the MFA compliance alerting workflow step by step.
  
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


## Step 1 — Verify MFA Non-Compliant IAM Users

This guide assumes the AWS Config managed rule **`mfa-enabled-for-iam-console-access`** is already enabled and identifying non-compliant IAM users.

The goal of this step is to confirm that AWS Config is already detecting IAM users who have console access but do not have MFA enabled.

### Navigate to AWS Config

1. Open the **AWS Management Console**
2. Navigate to **AWS Config**
3. Select **Rules** from the left navigation menu
4. Locate the rule `mfa-enabled-for-iam-console-access`
## Step 2 — Verify the Finding in Security Hub

### Navigate to Security Hub

1. Open the **AWS Management Console**
2. Navigate to **Security Hub**
3. Select **Findings**
4. Locate **`mfa-enabled-for-iam-console-access`** rule


## Step 3 — Create an S3 Bucket for Evidence Storage
Name: mfa_compliance_evidence
This stores evidence artifacts for each MFA compliance finding in Amazon S3.  
These JSON files act as a audit trail showing when a non-compliant IAM user was detected.

Each file will contain details about the Security Hub finding, including:

- IAM user involved
- Compliance status
- AWS account ID
- Severity
- Timestamp

Evidence files will be written into the following prefix:
mfa-evidence/2026-03-10-14-02-13.json


## Step 4 — Create an SNS Topic for Alert Notifications

The next step is to create an Amazon SNS topic that will send alert notifications when a non-compliant MFA finding is detected.

The Lambda function will publish messages to this topic whenever it processes a relevant Security Hub finding.

### Create the SNS topic

1. Open the **AWS Management Console**
2. Navigate to **Amazon SNS**
3. Select **Topics** > **Standard** 
4. Click **Create topic**

| Name | `mfa-compliance-alerts`

Next, create a subscription so alerts are sent to your email. Click your topic > subscriptions > Create subscription > protocol>Email
> **endpoint (insert your email for alerts here)**

## Step 5 — Create the Lambda Execution Role

The Lambda function needs permission to interact with other AWS services.  
This role will allow Lambda to:
- Write evidence files to **Amazon S3**
- Send alert messages to **Amazon SNS**
- Write execution logs to **CloudWatch Logs**
1. Navigate to IAM
2. AWS Console → IAM → Roles → Create role
3. Select the trusted entity
Choose: AWS Service
Use Case: Lambda 
Next --> Next --> role name: mfa_compliance_check

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
      "Resource": "arn:aws:s3:::mfa_compliance_evidence/*"
    },
    {
      "Sid": "PublishToSNSTopic",
      "Effect": "Allow",
      "Action": [
        "sns:Publish"
      ],
      "Resource": "arn:aws:sns:<region>:<account-id>:mfa-compliance-alerts"
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

The Lambda function processes Security Hub findings related to MFA compliance.  
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
|-------|------|
| Function type | Author from scratch |
| Function name | `mfa_finding_handler` |
| Runtime | Python 3.x |
| Architecture | x86_64 (default) |
| Execution role | Use existing role |
| Existing role | `mfa_compliance_check` 

### Configure environment variables

Next, add environment variables that allow the Lambda function to locate the S3 bucket and SNS topic.

1. Open the Lambda function.
2. Select **Configuration → Environment variables**
3. Click **Edit**
4. Add the following variables:

| Key | Value |
|----|------|
| `BUCKET_NAME` | `mfa_compliance_evidence` |
| `SNS_TOPIC_ARN` | `arn:aws:sns:<region>:<account-id>:mfa-compliance-alerts` |


## Step 7 — Add the Lambda Function Code

The next step is to add the Python script that processes MFA compliance findings.

The Lambda function will:

- process Security Hub findings related to MFA compliance
- identify IAM users that are non-compliant
- store evidence artifacts in **Amazon S3**
- send alert notifications using **Amazon SNS**

### Upload the Lambda code

The full Lambda implementation is included in this repository: lambda.py
### Add the code to the Lambda function

1. Open the **AWS Management Console**
2. Navigate to **AWS Lambda**
3. Select the function **`mfa_finding_handler`**
4. Go to the **Code** tab
5. Replace the default Lambda code with lambda.py
6. Click deploy


### — Test the Lambda Function
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
        "AwsAccountId": "1234567",
        "Title": "MFA should be enabled for all IAM users that have a console password",
        "Severity": {
          "Label": "MEDIUM"
        },
        "Compliance": {
          "SecurityControlId": "IAM.5",
          "Status": "FAILED"
        },
        "Workflow": {
          "Status": "NEW"
        },
        "RecordState": "ACTIVE",
        "Resources": [
          {
            "Id": "tes_user_no_mfa"
          }
        ]
      }
    ]
  }
}
```
If the function is configured correctly, the test should:generate a JSON evidence file in S3 & send a notification through SNS

## Step 8 — Create the EventBridge Rule & Define the Target 
1. Open the AWS Management Console
2. Navigate to Amazon EventBridge
3. Select Rules
4. Click Create rule then Configure

### Configure the rule

| Setting | Value |
|-------|------|
| Rule name | `mfa_securityhub_trigger` |
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
4. From the **Function dropdown**, select mfa_securityhub_trigger
5. Leave **Additional settings** as default unless you want to configure input transformation.
6. Click **Next**
7. Review the configuration
8. Click **Create rule**
Once created, EventBridge will automatically invoke the **mfa_securityhub_trigger Lambda function** whenever the defined Security Hub event occurs.

## Step 9 — Add the required resource-based policy to invoke the Lambda function.
 
1. Navigate to AWS Lambda
2. Select the function `mfa_finding_handler`
3. Open Configuration → Permissions
4. Locate Resource-based policy

Add a policy statement allowing EventBridge to invoke the Lambda function.
```json
{
  "Version": "2012-10-17",
  "Id": "default",
  "Statement": [
    {
      "Sid": "allow-mfa-trigger",
      "Effect": "Allow",
      "Principal": {
        "Service": "events.amazonaws.com"
      },
      "Action": "lambda:InvokeFunction",
      "Resource": "arn:aws:lambda:<region>:<account-id>:function:mfa_finding_handler",
      "Condition": {
        "ArnLike": {
          "AWS:SourceArn": "arn:aws:events:<region>:<account-id>:rule/mfa_securityhub_trigger"
        }
      }
    }
  ]
}
```

Replace the following placeholders with values from your environment:
- <region>
- <account-id>	             
After completing the setup, the MFA compliance automation workflow should now be operational.


## How to Trigger a Test Finding

You can trigger the automation by intentionally creating a non-compliant user.

Example test scenario:

1. Create a test IAM user with **console access**
2. Do **not enable MFA**
3. Wait for **AWS Config** to evaluate the rule
4. This generates a Security Hub finding:
5. SNS alert will trigger and evidence will be saved to S3


## Trigger the Event from Security Hub CSPM

Once the finding appears in Security Hub, you can manually trigger the workflow by updating the finding status.

1. Open **AWS Security Hub**
2. Navigate to **CSPM → Findings**
3. Locate the IAM.5 finding for the non-compliant user
4. Select the finding
5. Change the **Workflow Status**

Example: NEW --> RESOLVED --> NEW

