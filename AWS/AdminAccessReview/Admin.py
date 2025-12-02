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
