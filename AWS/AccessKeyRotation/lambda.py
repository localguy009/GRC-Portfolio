import json
import os
import boto3
from datetime import datetime

# AWS service clients
s3 = boto3.client("s3")
sns = boto3.client("sns")

# Environment variables (configured in Lambda settings)
BUCKET_NAME = os.environ["BUCKET_NAME"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]

# Controls monitored by this function
CONTROL_ID_MATCH = "IAM.3"
CONFIG_RULE_MATCH = "access-keys-rotated"


def lambda_handler(event, context):

    print("Received event from Security Hub")

    findings = event.get("detail", {}).get("findings", [])

    if not findings:
        print("No findings detected in event")
        return {"status": "no_findings"}

    processed = []

    for finding in findings:

        title = finding.get("Title", "")
        severity = finding.get("Severity", {}).get("Label", "UNKNOWN")
        finding_id = finding.get("Id", "unknown-finding")

        compliance = finding.get("Compliance", {})
        control_id = compliance.get("SecurityControlId", "")
        compliance_status = compliance.get("Status", "")

        product_fields = finding.get("ProductFields", {})
        config_rule_name = product_fields.get("aws/config/ConfigRuleName", "")
        config_compliance_type = product_fields.get("aws/config/ConfigComplianceType", "")

        workflow_status = finding.get("Workflow", {}).get("Status", "")
        record_state = finding.get("RecordState", "")

        resources = []
        for r in finding.get("Resources", []):

            username = (
                r.get("Details", {})
                .get("AwsIamUser", {})
                .get("UserName")
            )

            resources.append(username or r.get("Id", "unknown-resource"))

        is_iam3_control = control_id == CONTROL_ID_MATCH
        is_config_rotation_rule = config_rule_name == CONFIG_RULE_MATCH

        if not (is_iam3_control or is_config_rotation_rule):
            continue

        # Only process active findings
        if workflow_status != "NEW":
            continue

        if record_state != "ACTIVE":
            continue

        # Only alert when failing / noncompliant
        if compliance_status not in ["FAILED", "WARNING"] and config_compliance_type != "NON_COMPLIANT":
            continue

        evidence = {
            "control_id": control_id or None,
            "config_rule": config_rule_name or None,
            "title": title,
            "severity": severity,
            "workflow_status": workflow_status,
            "record_state": record_state,
            "compliance_status": compliance_status or None,
            "config_compliance_type": config_compliance_type or None,
            "resources": resources,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        key = f"access-key-rotation-evidence/{datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S')}.json"

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=json.dumps(evidence, indent=2).encode("utf-8"),
            ContentType="application/json"
        )

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="Access Key Rotation Compliance Finding Detected",
            Message=json.dumps(evidence, indent=2)
        )

        processed.append({
            "finding_id": finding_id,
            "s3_key": key
        })

        print(f"Processed finding: {finding_id}")

    if not processed:
        return {"status": "no_access_key_rotation_findings_matched"}

    return {
        "status": "processed",
        "count": len(processed),
        "items": processed
    }
