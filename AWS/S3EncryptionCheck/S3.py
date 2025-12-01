import boto3
from botocore.exceptions import ClientError

s3 = boto3.client("s3")

# get all buckets
response = s3.list_buckets()
buckets = response.get("Buckets", [])

if not buckets:
    print("No S3 buckets found.")
else:
    for bucket in buckets:
        name = bucket["Name"]

        try:
            # try to get encryption settings
            s3.get_bucket_encryption(Bucket=name)
            print(name, "- ENCRYPTED")
        except ClientError as e:
            code = e.response["Error"]["Code"]
            if code == "ServerSideEncryptionConfigurationNotFoundError":
                print(name, "- NOT ENCRYPTED")
            else:
