This lab demonstrates how to implement preventive cloud governance controls using AWS Service Control Policies (SCPs) across Development and Production environments.

## Step 1: Create AWS Accounts

From the **management account**:

1. Open **AWS Organizations**
2. Go to **Accounts**
3. Click **Add an AWS account**
4. Choose **Create an AWS account**
5. Create:

   * `Dev-Account`
   * `Prod-Account`
6. Use unique email addresses for each account

Example:

```text
yourname+dev@gmail.com
yourname+prod@gmail.com
```

## Step 2: Create Organizational Units

1. In **AWS Organizations**, go to **Organizational units**
2. Under **Root**, create:

   * `Development`
   * `Production`

## Step 3: Move Accounts into the Correct OUs

1. Go to **AWS Organizations -> Accounts**
2. Select the Dev account
3. Click **Move**
4. Move it to **Development**
5. Repeat for Prod and move it to **Production**

## Step 4: Access the Member Accounts

Use the role created by AWS Organizations:

```text
OrganizationAccountAccessRole
```

To access the Dev account:

1. Log into the management account as an IAM admin user
2. Choose **Switch Role**
3. Enter:

   * Dev account ID
   * `OrganizationAccountAccessRole`

If it does not work immediately, wait a few minutes and retry. New accounts and trust relationships sometimes take time to propagate.

## Step 5: Verify SCPs Are Enabled

1. In **AWS Organizations**, go to **Policies**
2. Select **Service control policies**
3. Confirm SCPs are enabled

## Step 6: Create Development SCP - Restrict EC2 Instance Types

This SCP allows only approved low-cost instance types in Development.

### Policy: `Dev-Restrict-EC2-Instance-Types`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyUnapprovedInstanceTypes",
      "Effect": "Deny",
      "Action": "ec2:RunInstances",
      "Resource": "arn:aws:ec2:*:*:instance/*",
      "Condition": {
        "StringNotEquals": {
          "ec2:InstanceType": [
            "t2.micro",
            "t3.micro",
            "t3.small"
          ]
        }
      }
    }
  ]
}
```

### Purpose

* Controls cloud costs
* Standardizes development compute usage
* Prevents oversized instances from being launched

### Attach To

* `Development` OU

### Test

* `t2.micro` -> allowed
* `t3.micro` -> allowed
* `t3.large` -> denied

## Step 7: Create Development SCP - Restrict Regions

This SCP restricts development activity to `us-east-1` and `us-east-2`.

### Policy: `Dev-Restrict-Regions`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DevRegionRestriction",
      "Effect": "Deny",
      "NotAction": [
        "iam:*",
        "organizations:*",
        "route53:*",
        "cloudfront:*",
        "support:*"
      ],
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": [
            "us-east-1",
            "us-east-2"
          ]
        }
      }
    }
  ]
}
```

### Purpose

* Limits data and resource sprawl
* Supports governance boundaries
* Reduces attack surface

### Attach To

* `Development` OU

### Test

* Launch resources in `us-east-1` -> allowed
* Launch resources in `us-east-2` -> allowed
* Launch resources in `us-west-2` -> denied


## Step 8: Create Production SCP - Protect CloudTrail

This SCP prevents users in Production from disabling or deleting CloudTrail.

### Policy: `Prod-Protect-CloudTrail`

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyCloudTrailTampering",
      "Effect": "Deny",
      "Action": [
        "cloudtrail:StopLogging",
        "cloudtrail:DeleteTrail"
      ],
      "Resource": "*"
    }
  ]
}
```
### Purpose

* Protects audit logs
* Supports incident response and accountability
* Prevents loss of visibility in Production

### Attach To

* `Production` OU

### Test

* Attempt to stop logging -> denied
* Attempt to delete trail -> denied
