#  EC2.19: Security Groups with Public Exposure Contro – Automated Detection & Evidence Pipeline

## 📌 Project Overview

This project demonstrates how to operationalize a cloud security control through **continuous monitoring, automated detection, and real-time evidence generation**.

## Architecture
EventBridge → Lambda → S3 (evidence) + SNS (alerts)

The solution focuses on identifying high-risk AWS security group misconfigurations, such as unrestricted access to sensitive ports (e.g., RDP on port 3389 exposed to the internet), which can significantly increase an organization’s attack surface.

Using an event-driven architecture, the control operates continuously in the background:

- **Detection:** AWS EventBridge monitors CloudTrail activity for security group changes in real time  
- **Evaluation:** A Lambda function is automatically triggered to assess the configuration against defined risk conditions  
- **Evidence Generation:** Structured JSON evidence is created for every relevant event and stored in Amazon S3 for audit readiness  
- **Alerting:** SNS notifications provide immediate visibility into potential security risks  


## Control Objective
Prevent and detect **unauthorized or overly permissive network exposure** in AWS environments.

## Control Mapping

### 🔹 NIST SP 800-53
- **AC-4**: Information Flow Enforcement  
- **CM-7**: Least Functionality  
- **SI-4**: System Monitoring  
- **AU-6**: Audit Review, Analysis, and Reporting  

### 🔹 CIS Controls v8
- **Control 4**: Secure Configuration of Enterprise Assets  
- **Control 13**: Network Monitoring and Defense 
