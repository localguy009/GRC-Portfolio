## Prerequisites

Before starting, make sure you have:

- An AWS account with permissions to create and manage:
  - AWS Lambda
  - IAM roles/policies
  - Amazon S3 buckets/objects
  - AWS Security Hub
  - Amazon Bedrock model access (InvokeModel)


- **Lambda environment variables** planned:
  - `EVIDENCE_BUCKET` = your S3 bucket name
  - `MODEL_ID` = your Bedrock model ID


## Step 1 — Enable AWS Security Hub

AWS Security Hub is the source of security findings used by this project. The Lambda function will query active Security Hub findings, so Security Hub must be enabled before continuing.

1. Sign in to the AWS Management Console
2. Navigate to Security Hub
3. Click Enable Security Hub. Enable at least one security standard so findings are generated

## Step 3 — Create the IAM Role for the Lambda Function

The Lambda function requires an execution role with permissions to read Security Hub findings, invoke Amazon Bedrock, write the report to S3, and publish logs to CloudWatch.


1. Open the AWS Management Console
2. Navigate to IAM → Roles
3. Click Create role
4. Select AWS service as the trusted entity
5. Choose Lambda as the use case
6. Click Next

### Attach Basic Logging Permissions

Attach the managed policy:
- `AWSLambdaBasicExecutionRole`

This allows the function to write logs to CloudWatch.

### Add Inline Policy 
See inlinepolicy.md

## Step 4 — Create the Lambda Function

In this step, you will create the Lambda function that retrieves Security Hub findings, invokes Amazon Bedrock, and writes the generated risk report to S3.


1. Open the AWS Management Console
2. Navigate to AWS Lambda
3. Click Create function
4. Select Author from scratch

### Function Configuration

- Function name: `securityhub-bedrock-risk-report`
- Runtime: Python 3.11 or Python 3.12
- Execution role:  
  - Select Use an existing role
  - Choose the IAM role created in **Step 3**

Click Create function

---

### Update Function Settings (Recommended)

After the function is created:

1. Go to Configuration → General configuration
2. Click Edit
3. Set:
   - **Timeout**: 60 seconds  
   - **Memory**: 512 MB (or higher if desired)
4. Save changes


### Validation

- Confirm the function exists and shows **Active**
- Confirm the correct IAM role is attached
- Confirm the runtime is Python 3.x

Do **not** add code yet — that will be done in the next step.

## Step 5 — Configure Lambda Environment Variables

1. In the **AWS Lambda** console, open your function
2. Navigate to **Configuration → Environment variables**
3. Click **Edit**
4. Add the following variables:

   - **Key**: `EVIDENCE_BUCKET`  
     **Value**: `<your-s3-bucket-name>`

   - **Key**: `MODEL_ID`  
     **Value**: `<your-bedrock-model-id>`


## Step 6 — Add and Deploy the Lambda Code

1. In the **AWS Lambda** console, open your function  
2. Navigate to the **Code** tab  
3. In the inline editor, replace any existing code with the contents of **`lambda.py`** from this repository  
4. Click **Deploy**

### Test and Run

- Create a test event (any empty or dummy JSON is sufficient)
- Run the function and confirm the execution completes successfully
- Verify the file **`securityhub-risk-report.md`** is created in the configured S3 bucket

A successful run confirms that Security Hub findings were retrieved, analyzed by Amazon Bedrock, and written to S3 as a structured Markdown report.
