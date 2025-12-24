import json
import boto3
import os

securityhub = boto3.client("securityhub")
bedrock = boto3.client("bedrock-runtime")
s3 = boto3.client("s3")

BUCKET = os.environ["EVIDENCE_BUCKET"]
MODEL_ID = os.environ["MODEL_ID"]

def lambda_handler(event, context):
    # 1. Get active Security Hub findings
    response = securityhub.get_findings(
        Filters={
            "RecordState": [{"Value": "ACTIVE", "Comparison": "EQUALS"}]
        },
        MaxResults=40
    )

    findings = response.get("Findings", [])

    # 2. Condense findings
    condensed = [
        {
            "Title": f.get("Title"),
            "Severity": (f.get("Severity") or {}).get("Label"),
            "ResourceId": (f.get("Resources") or [{}])[0].get("Id"),
            "Region": f.get("Region"),
            "Remediation": ((f.get("Remediation") or {}).get("Recommendation") or {}).get("Text")
        }
        for f in findings
    ]

    # 3. Build Bedrock prompt
    prompt = f"""
Create an executive-level AWS security risk summary based only on these findings.

Output in Markdown with:
- Executive Summary
- Top Risks
- Recommended Actions

Findings:
{json.dumps(condensed, indent=2)}
"""

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1000,
        "temperature": 0.2,
        "messages": [{"role": "user", "content": prompt}]
    }

    # 4. Invoke Bedrock
    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        body=json.dumps(payload),
        contentType="application/json",
        accept="application/json"
    )

    body = json.loads(response["body"].read())
    report_md = "\n".join(
        block["text"] for block in body.get("content", []) if block["type"] == "text"
    )

    # 5. Write single report to S3 (no folders)
    s3.put_object(
        Bucket=BUCKET,
        Key="securityhub-risk-report.md",
        Body=report_md,
        ContentType="text/markdown"
    )

    return {
        "status": "success",
        "findings_count": len(condensed,
        ),
        "output_file": "securityhub-risk-report.md"
    }
