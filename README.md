# GRC Professional Portfolio:

## About Me

Hello, I'm Matt — I currently work at Club Car LLC, where I support cloud governance, security automation and compliance initiatives across the organization.
I'm passionate about building secure cloud environments, aligning security initiatives with business objectives, and ensuring compliance with industry standards and regulations through automation. 

I’m a U.S. Navy veteran with a background in Special Operations and I bring that same discipline, adaptability, and mission-driven mindset into my GRC work.


## Repository Structure
```
GRC_Portfolio/
│── README.md                     # You are here
├── AWS/                          # AWS cloud automation projects
│   ├── AdminAccessReview/        # IAM admin access review automation
│   ├── S3EncryptionCheck/        # S3 encryption compliance check
│   └── BedrockAutomation/        # Bedrock risk reporting
│   └── MFA Compliance/           # Automated detection for non compliant users
└── Azure/                        # Azure cloud automation projects
    └── MonthlyAccessReview/      # Azure Global Admin monthly access review

```

## Contact Information

- **Email**: matthew.connelly094@gmail.com
- **LinkedIn**: https://www.linkedin.com/in/matt-connelly-/

### Cloud Platforms
- Azure
- Amazon Web Services (AWS)

## Certifications
- Certified Information Systems Security Professional (CISSP)
- Cisco Certified Network Associate (CCNA)
- CompTIA Security +

## Projects
### Azure Global Admin Automated Report
- Built an automated Azure Runbook leveraging a User-Assigned Managed Identity (UAMI) and Microsoft Graph PowerShell to extract all Global Administrator accounts from Entra ID.
- Implemented a recurring monthly job that exports results, generates audit-ready evidence, and emails the report to the IT Security team for mandated access reviews.
- [🔗 View Project on GitHub](https://github.com/localguy009/GRC-Portfolio/tree/main/Azure/MonthlyAccessReview)

### AWS Access Review
- Developed a Python script using boto3 to automatically retrieve all users belonging to the Administrators IAM group 
- Enables quick auditing of privileged access by programmatically identifying users assigned to high-privilege IAM groups.
- [🔗 View Project on GitHub](https://github.com/localguy009/GRC-Portfolio/tree/main/AWS/AdminAccessReview)
 
 ### AWS S3 Encryption Compliance Checker 
 - Developed a Python script to automatically check all S3 buckets in an AWS account and determine whether server-side encryption (SSE) is enabled.
 - [🔗 View Project on GitHub](https://github.com/localguy009/GRC-Portfolio/tree/main/AWS/S3EncryptionCheck)

### AWS Bedrock Automation 
- Built a Lambda function that retrieves and condenses Security Hub active findings, then invokes a Bedrock-hosted  model to analyze risk and produce a structured report.
- [🔗 View Project on GitHub](https://github.com/localguy009/GRC-Portfolio/tree/main/AWS/BedrockAutomation)
