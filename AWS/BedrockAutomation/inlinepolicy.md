```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "ReadSecurityHubFindings",
      "Effect": "Allow",
      "Action": "securityhub:GetFindings",
      "Resource": "*"
    },
    {
      "Sid": "InvokeBedrockModel",
      "Effect": "Allow",
      "Action": "bedrock:InvokeModel",
      "Resource": "*"
    },
    {
      "Sid": "WriteReportToS3",
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
    }
  ]
}
```
