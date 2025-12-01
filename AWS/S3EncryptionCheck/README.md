# S3 Encryption Compliance Checker
This project is a Python-based tool that scans all S3 buckets in an AWS account and reports whether each bucket has **server-side encryption (SSE)** enabled. It uses the AWS SDK for Python (`boto3`) to retrieve bucket configurations and identify buckets that are unencrypted. 
### **AWS Skills**
- Programmatically interacting with AWS services using `boto3`
- Understanding S3 encryption types (SSE-S3, SSE-KMS, DSSE-KMS)
- Working with IAM policies and AWS error codes
- Detecting common S3 misconfigurations

Below is the script with all of my personal notes included.  
I'm using these comments to track my learning, explain each line in simple terms,  
and build a deeper understanding of Python and AWS as I grow.

See S3.py for full script without #comment blocks 

```python
# Import the AWS SDK for Python (boto3) to interact with AWS services
# Import ClientError to properly handle AWS API errors
import boto3
from botocore.exceptions import ClientError

# Create an S3 client object that allows us to call S3 APIs
s3 = boto3.client("s3")

response = s3.list_buckets()           # Ask AWS for a list of all buckets.
buckets = response.get("Buckets", [])  # Get the bucket list from the response. 
                                       # If the list is missing, use an empty list so the script keeps running
# Check if the account has any buckets

if not buckets:                        # If the buckets list is empty...
    print("No S3 buckets found.")      # Print a message and exit
else:
                                       # Loop through each bucket returned by AWS
    for bucket in buckets:  
        name = bucket["Name"]          # Extract the bucket's name from the dictionary   

        try:
            # try to get encryption settings
            s3.get_bucket_encryption(Bucket=name)          # Attempt to fetch encryption config for this bucket
            print(name, "- ENCRYPTED")                     # If no error occurs, the bucket is encrypted
        except ClientError as e:                           # Catch errors from AWS API calls
            code = e.response["Error"]["Code"]             # Extract the AWS error code
# AWS returns this specific error when the bucket has NO encryption
            if code == "ServerSideEncryptionConfigurationNotFoundError":
                print(name, "- NOT ENCRYPTED")             # Bucket is unencrypted
            else:
  # Any other error (e.g., AccessDenied, unknown error)
                print(name, "- COULD NOT CHECK")           # Could not determine encryption status
```
