# EC2.19 Control Automation – Detection & Evidence Project

## Architecture
EventBridge → Lambda → S3 (evidence) + SNS (alerts)


## Step 1: Create S3 Bucket for Evidence

1. Go to S3
2. Click Create bucket
3. Name:ec2-19-evidence

## Step 2: Create SNS Topic for Alerts

1. Go to SNS
2. Click Topics
3. Click Create topic
4. Select Standard
5. Name: ec2-19-alerts
### Add Subscription
1. Open the topic
2. Click **Create subscription**
3. Protocol: `Email`
4. Endpoint: your email
5. Confirm the subscription via email



## Step 3: Create IAM Role for Lambda

1. Go to **IAM → Roles → Create role**
2. Select:
- AWS service
Use case: Lambda
  Attach Managed Policy
 AWSLambdaBasicExecutionRole


 ### Add Inline Policy

Replace `YOUR_SNS_TOPIC_ARN` with your actual ARN.

```json
{
"Version": "2012-10-17",
"Statement": [
 {
   "Sid": "DescribeSecurityGroups",
   "Effect": "Allow",
   "Action": [
     "ec2:DescribeSecurityGroups"
   ],
   "Resource": "*"
 },
 {
   "Sid": "WriteEvidenceToS3",
   "Effect": "Allow",
   "Action": [
     "s3:PutObject"
   ],
   "Resource": "arn:aws:s3:::ec2-19-evidence/*"
 },
 {
   "Sid": "PublishToSNS",
   "Effect": "Allow",
   "Action": [
     "sns:Publish"
   ],
   "Resource": "YOUR_SNS_TOPIC_ARN"
 }
]
}
```

RoleName: lambda-ec2-19-monitor-role

## Step 4: Create Lambda Function

Go to AWS Lambda

Click Create function

Choose Author from scratch

### Configuration

- **Function name:**  
  `ec2-19-monitor`

- **Runtime:**  
  `Python 3.12`

- **Permissions:**  
  Use existing role

- **Select:**  
  `lambda-ec2-19-monitor-role`

---

## Step 5: Configure Environment Variables

Go to:

`Lambda → Configuration → Environment variables`

### Add:

| Key            | Value               |
|----------------|--------------------|
| BUCKET_NAME    | ec2-19-evidence    |
| SNS_TOPIC_ARN  | your SNS ARN       |

---

## Step 6: Add Lambda Code

Paste the project code from `lambda.py`

Click Deploy
---

## Step 7: Create EventBridge Rule

This triggers the Lambda when security group rules change.

Go to:

`EventBridge → Rules → Create rule`

### Name:
`ec2-19-sg-change-monitor`

### Event Source

- Select **Event pattern**
- Choose **Custom Pattern**

```json
{
  "source": ["aws.ec2"],
  "detail-type": ["AWS API Call via CloudTrail"],
  "detail": {
    "eventSource": ["ec2.amazonaws.com"],
    "eventName": [
      "AuthorizeSecurityGroupIngress",
      "ModifySecurityGroupRules",
      "CreateSecurityGroup"
    ]
  }
}
```
## Target

- Select your Lambda function:  
  `ec2-19-monitor`

## Step 8: Allow EventBridge to Invoke Lambda

- AWS usually configures this automatically  
- Verify the Lambda is attached as a target  



## Step 9: Test the Control

### Create a test violation:

Go to:

`EC2 → Security Groups`


1. Select a security group  
2. Add inbound rule:
   - **Type:** Custom TCP  
   - **Port:** 3389  
   - **Source:** 0.0.0.0/0  

## Expected Result

- Lambda function executes  
- Evidence JSON is written to S3  
- SNS alert email is received  