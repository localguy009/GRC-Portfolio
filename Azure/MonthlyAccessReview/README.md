# Azure GRC Automation – Global Admin Monthly Report

This project automates the monthly export of Entra ID Global Administrators using an Azure Automation Runbook, a User-Assigned Managed Identity (UAMI), and Microsoft Graph.  

## Project Overview

This automation removes manual effort review of Global Administrators by:

- Exporting a clean list of Global Admins 
- Emailing the results to the IT Security team  
- Running automatically on a monthly schedule
- Authenticating securely with UAMI (no stored secrets)  
## Prerequisites

Before deploying this automation, ensure you have the following:

- An active Azure subscription
- Permission to create and manage:
  - Automation Accounts
  - User-Assigned Managed Identities (UAMI)
  - Azure Role Assignments  
  - Microsoft Graph API application permissions

## Architecture Components

- Azure Automation Account 
- User-Assigned Managed Identity (UAMI)*with Graph permissions  
- PowerShell Runbook  
- Scheduled job to trigger monthly  
- Email delivery (Graph Mail.Send or shared mailbox)  
- Microsoft Graph API

