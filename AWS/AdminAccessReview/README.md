# AWS IAM Group Membership Auditor

This project retrieves and displays all users who belong to a specified AWS IAM group. It is useful for auditing privileged access, validating IAM configurations, and supporting security/compliance workflows.

---

## Overview

The script connects to AWS using the `boto3` SDK and:

- Queries a specified IAM group (Admins) 
- Retrieves all users assigned to that group  
- Prints each username to the console   

This allows security teams to quickly confirm who holds elevated permissions in an AWS environment.

---

## Script Example

```python
import boto3

# Choose the IAM group name
GROUP_NAME = "Administrators"

# Create an IAM client
iam = boto3.client("iam")

print(f"=== Users in IAM group: {GROUP_NAME} ===")

# Get the group
response = iam.get_group(GroupName=GROUP_NAME)

# Extract the list of users
users = response["Users"]

# Print users
if not users:
    print("No users in this group.")
else:
    for user in users:
        print(user["UserName"])
```
