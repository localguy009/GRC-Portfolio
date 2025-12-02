# GRC Professional Portfolio:

## About Me

Hello, I'm Matt — a Governance, Risk, and Compliance (GRC) professional with a focus on cloud security. I'm passionate about building secure cloud environments, aligning security initiatives with business objectives, and ensuring compliance with industry standards and regulations.

I’m a U.S. Navy veteran with a background in Special Operations and I bring that same discipline, adaptability, and mission-driven mindset into my GRC work.
I currently work at Club Car LLC, where I support cloud governance, security automation and compliance initiatives across the organization. 

## Repository Structure
```
GRC_Portfolio/
│
├── AWS/                         # AWS cloud automation projects
│   ├── AdminAccessReview/       # IAM admin access review automation
│   └── S3EncryptionCheck/       # S3 encryption compliance check
│
└── Azure/                       # Azure cloud automation projects
    └── MonthlyAccessReview/     # Automated Azure Global Admin monthly access review

```

## Contact Information

- **Email**: matthew.connelly094@gmail.com
- **LinkedIn**: https://www.linkedin.com/in/matt-connelly-/
## Technical Skills
### Cloud Platforms
- Azure
- Amazon Web Services (AWS)
  
### Security & Compliance
- AWS Security Services (GuardDuty, Security Hub, IAM, CloudWatch, CloutTrail)
- Azure Security & Governance: Entra ID, Azure Automation (Runbooks), User-Assigned Managed Identities (UAMI), Microsoft Graph API, Azure Policy
- Risk Assessment and Management
- Security Control Implementation

### Tools & Technologies
- EDR (CrowdStrike) SIEM (Splunk, CrowdStrike NGSIEM)
- Scripting and Automation (Python, Powershell)
- Email Security (Abnormal AI, KnowBe4)
- Identity Access Management (Sailpoint)
- Vulnerabiltiy Scanns (Qualys, Tenable)
- Ticketing (ServiceNow)

## Certifications
- Certified Information Systems Security Professional (CISSP)
- Cisco Certified Network Associate (CCNA)
- CompTIA Security +

## Projects
### Azure Global Admin Automated Report
- Built an automated Azure Runbook leveraging a User-Assigned Managed Identity (UAMI) and Microsoft Graph PowerShell to extract all Global Administrator accounts from Entra ID.
- Implemented a recurring monthly job that exports results, generates audit-ready evidence, and emails the report to the IT Security team for mandated access reviews.
- [🔗 View Project on GitHub](https://github.com/localguy009/GRC-Portfolio/tree/main/Azure/MonthlyAccessReview)

### AWS IAM Group Membership Auditor
- Developed a Python script using boto3 to automatically retrieve all users belonging to the Administrators IAM group 
- Enables quick auditing of privileged access by programmatically identifying users assigned to high-privilege IAM groups.
- - [🔗 View Project on GitHub](https://github.com/localguy009/GRC-Portfolio/tree/main/AWS/AdminAccessReview)
 
 ### AWS S3 Encryption Compliance Checker 
 - Developed a Python script to automatically check all S3 buckets in an AWS account and determine whether server-side encryption (SSE) is enabled.
 - [🔗 View Project on GitHub](https://github.com/localguy009/GRC-Portfolio/tree/main/AWS/S3EncryptionCheck)

