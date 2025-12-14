# AWS Access Review 

This project retrieves and displays all users who belong to a specified AWS IAM group. It is useful for auditing privileged access, validating IAM configurations, and supporting security/compliance workflows.

---

## Overview

The script connects to AWS using the `boto3` SDK and:

- Queries a specified IAM group (Admins) 
- Retrieves all users assigned to that group  
- Prints each username to the console   

This allows you to quickly confirm who holds elevated permissions in an AWS environment.

---

## Script Example below. Additonal comments have been add to showcase my learning
See Admin.py for less comments

```python
import boto3   # Allows Python to interact with AWS services

# IAM group we want to inspect
GROUP_NAME = "Administrators"

# Create an IAM client object to call IAM APIs
iam = boto3.client("iam")

print(f"=== Users in IAM group: {GROUP_NAME} ===")

# Call the IAM API to get group details (returns a dictionary)
response = iam.get_group(GroupName=GROUP_NAME)

# "Users" is a key in the response dict that contains a list of user objects
users = response["Users"]

# Print results
if not users:
    print("No users in this group.")
else:
    for user in users:
        # Each user is a small dictionary; we pull just the username
        print(user["UserName"])

```
