import json
import os
from datetime import datetime, timezone

import boto3

ec2 = boto3.client("ec2")
s3 = boto3.client("s3")
sns = boto3.client("sns")

BUCKET_NAME = os.environ["BUCKET_NAME"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]

HIGH_RISK_PORTS = {
    20, 21, 22, 23, 25, 110, 135, 143, 445,
    1433, 1434, 3000, 3306, 3389, 4333, 5000,
    5432, 5500, 5601, 8080, 8088, 8888, 9200, 9300
}


def lambda_handler(event, context):
    print("Incoming event:")
    print(json.dumps(event, default=str))

    detail = event.get("detail", {})
    event_name = detail.get("eventName")

    relevant_events = {
        "AuthorizeSecurityGroupIngress",
        "ModifySecurityGroupRules",
        "CreateSecurityGroup"
    }

    if event_name not in relevant_events:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Ignored event",
                "event_name": event_name
            })
        }

    group_id = extract_group_id(detail)

    if not group_id:
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "No security group ID found"
            })
        }

    findings = evaluate_security_group(group_id)

    evidence = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_name": event_name,
        "security_group_id": group_id,
        "aws_region": detail.get("awsRegion"),
        "actor_arn": detail.get("userIdentity", {}).get("arn"),
        "source_ip": detail.get("sourceIPAddress"),
        "noncompliant": len(findings) > 0,
        "matched_rules": findings
    }

    evidence_key = write_evidence(evidence)

    if evidence["noncompliant"]:
        send_alert(evidence, evidence_key)

    return {
        "statusCode": 200,
        "body": json.dumps(evidence)
    }


def extract_group_id(detail):
    request_params = detail.get("requestParameters", {})

    if request_params.get("groupId"):
        return request_params["groupId"]

    group_ids = request_params.get("groupIdSet", {}).get("items", [])
    if group_ids:
        return group_ids[0]

    return None


def evaluate_security_group(group_id):
    response = ec2.describe_security_groups(GroupIds=[group_id])
    security_groups = response.get("SecurityGroups", [])

    if not security_groups:
        return []

    sg = security_groups[0]
    matched_rules = []

    for perm in sg.get("IpPermissions", []):
        protocol = perm.get("IpProtocol")
        from_port = perm.get("FromPort")
        to_port = perm.get("ToPort")

        if from_port is None or to_port is None:
            continue

        risky_ports = set(range(from_port, to_port + 1)).intersection(HIGH_RISK_PORTS)
        if not risky_ports:
            continue

        for ip_range in perm.get("IpRanges", []):
            cidr = ip_range.get("CidrIp")
            if cidr == "0.0.0.0/0":
                matched_rules.append({
                    "protocol": protocol,
                    "from_port": from_port,
                    "to_port": to_port,
                    "cidr": cidr,
                    "matched_high_risk_ports": sorted(risky_ports)
                })

        for ipv6_range in perm.get("Ipv6Ranges", []):
            cidr = ipv6_range.get("CidrIpv6")
            if cidr == "::/0":
                matched_rules.append({
                    "protocol": protocol,
                    "from_port": from_port,
                    "to_port": to_port,
                    "cidr": cidr,
                    "matched_high_risk_ports": sorted(risky_ports)
                })

    return matched_rules


def write_evidence(evidence):
    timestamp = datetime.now(timezone.utc).strftime("%Y/%m/%d/%H%M%S")
    key = f"ec2-19-detections/{timestamp}.json"

    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=key,
        Body=json.dumps(evidence, indent=2).encode("utf-8"),
        ContentType="application/json"
    )

    return key


def send_alert(evidence, evidence_key):
    ports = sorted({
        port
        for rule in evidence["matched_rules"]
        for port in rule["matched_high_risk_ports"]
    })

    cidrs = sorted({rule["cidr"] for rule in evidence["matched_rules"]})

    message = f"""
EC2.19-style exposure detected

Security Group: {evidence['security_group_id']}
Region: {evidence['aws_region']}
Event: {evidence['event_name']}

Matched high-risk ports: {", ".join(map(str, ports))}
Public source(s): {", ".join(cidrs)}

Actor: {evidence['actor_arn']}
Source IP: {evidence['source_ip']}
Time: {evidence['timestamp']}

Evidence:
s3://{BUCKET_NAME}/{evidence_key}
""".strip()

    sns.publish(
        TopicArn=SNS_TOPIC_ARN,
        Subject=f"[ALERT] Public SG Exposure - {evidence['security_group_id']}",
        Message=message
    )