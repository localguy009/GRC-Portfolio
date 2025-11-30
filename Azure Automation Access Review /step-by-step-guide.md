### 1. Create a User-Assigned Managed Identity (UAMI)

1. In the Azure portal, search for Managed Identities.
2. Click Create → select User-assigned.
3. Choose your **Subscription and Resource Group.
4. Give it a name (e.g., `uami-graph-global-admin-review`).
5. Select the same Region you plan to use for your Automation Account.
6. Click Review + create → **Create.
7. After creation, copy the Client ID (you’ll use this in the runbook config).

### 2. Grant Microsoft Graph API Permissions to the UAMI
Note: If portal-based consent is restricted in your environment, see Grant-GraphPermissions.md for a PowerShell method to assign the same permissions.
1. Go to Microsoft Entra ID → Enterprise applications.
2. Search for and open your User-Assigned Managed Identity.
3. Go to Permissions / **API permissions.
4. Click Add a permission → Microsoft Graph → Application permissions.
5. Add the following permissions:
   - `Directory.Read.All`
6. Click add permissions.
7. Click *Grant admin consent for the tenant


### 4. Create an Azure Automation Account

1. In the Azure portal, search for Automation Accounts.
2. Click Create.
3. Select your Subscription and Resource Group.
4. Name it (global-admin-review`).
5. Choose the same Region as your UAMI.
6. Set Runbook runtime to PowerShell 7.2
8. Click Review + create** → Create.

### 5. Attach the UAMI to the Automation Account

1. Open your Automation Account.
2. Go to Identity → User assigned.
3. Click + Add user assigned.
4. Select your UAMI and click Add.
Note: This step makes the UAMI available to your runbook so it can authenticate to Microsoft Graph using 'Connect-MgGraph -Identity

### 6. Create the Runbook

1. In the Azure Portal, go to Automation Accounts.  
2. Select your Automation Account.  
3. In the left-hand menu, go to Process Automation → Runbooks → Create a runbook.  
4. Enter a name such as:  
   `Invoke-GlobalAdminAccessReview`  
5. Set Runbook type to PowerShell.  
6. Set Runtime version to PowerShell 7.2 (or the latest available).  
7. Click Create.


### 7. Import Microsoft Graph PowerShell Modules
 **Note:** The default Microsoft Graph modules in Azure Automation (and the ones shown in the Modules Gallery)  
do **not** work with PowerShell 7.2.  
They will cause authentication failures such as:
- Invalid JWT access token
- Authentication needed. Please call Connect-MgGraph.
Because of this, you must manually import the compatible Microsoft Graph module versions using Azure Cloud Shell.
Run the following commands to import the correct module versions into your Automation Account:

```powershell
# Optional but recommended: Import Az.Accounts (required for New-AzAutomationModule operations)
$moduleName = "Az.Accounts"
$moduleVersion = "2.13.1"

New-AzAutomationModule `
    -AutomationAccountName "<YOUR-AUTOMATION-ACCOUNT>" `
    -ResourceGroupName "<YOUR-RESOURCE-GROUP>" `
    -Name $moduleName `
    -ContentLinkUri "https://www.powershellgallery.com/api/v2/package/$moduleName/$moduleVersion" `
    -RuntimeVersion "7.2"


# Import Microsoft.Graph.Authentication (stable version)
$moduleName = "Microsoft.Graph.Authentication"
$moduleVersion = "2.25.0"

New-AzAutomationModule `
    -AutomationAccountName "<YOUR-AUTOMATION-ACCOUNT>" `
    -ResourceGroupName "<YOUR-RESOURCE-GROUP>" `
    -Name $moduleName `
    -ContentLinkUri "https://www.powershellgallery.com/api/v2/package/$moduleName/$moduleVersion" `
    -RuntimeVersion "7.2"


# Import Microsoft.Graph (main module bundle)
$moduleName = "Microsoft.Graph"
$moduleVersion = "2.25.0"

New-AzAutomationModule `
    -AutomationAccountName "<YOUR-AUTOMATION-ACCOUNT>" `
    -ResourceGroupName "<YOUR-RESOURCE-GROUP>" `
    -Name $moduleName `
    -ContentLinkUri "https://www.powershellgallery.com/api/v2/package/$moduleName/$moduleVersion" `
    -RuntimeVersion "7.2"

```

### 8.0 Create the App Registration for Email

1. In the Azure Portal, go to Microsoft Entra ID  
2. Select App registrations  
3. Click New registration  
4. Enter a name such as `Automation-AdminReview-Email`  
5. For Supported account types, leave the default: Accounts in this organizational directory only  
6. Leave Redirect URI blank (not required for this scenario)  
7. Click Register


### **8.1 Create a Client Secret**
1. In the Azure Portal, go to Microsoft Entra ID  
2. Select App registrations  
3. Click the App Registration you created for email 
4. In the left-hand menu, select Certificates & secrets  
5. Click New client secret  
6. Enter a name (e.g., AutomationEmailSecret)  
7. Choose an expiration period (12–24 months recommended)  
8. Copy the secret immediately — you will not be able to view it again

### **8.2 Assign Microsoft Graph API Permissions**

Go to **API permissions** → **Add a permission** → **Microsoft Graph**.

Add the following:

| Permission | Type | Purpose |
|-----------|-------|---------|
| **Mail.Send** | Application | Allows sending email as any user (required for `/sendMail`) |
1. Click **Grant admin consent**  
2. Ensure each permission shows:  
   **Granted for \<Your Tenant\>**  

### **8.3 Store the Credentials in Azure Automation**

1. Go to your Automation Account 
2. Navigate to Shared Resources → Credentials
3. Click + Add a credential
4. Configure the credential as follows:

| Field | Value |
|-------|--------|
| **Name** | `EmailSenderCredential` |
| **User name** | App Registration **Client ID** |
| **Password** | App Registration **Client Secret** |

This credential will be securely retrieved by your runbook.

## 9. Add the Runbook Script

Now that the environment, permissions, and modules are configured, you can add the PowerShell automation script to the runbook.

1. Navigate back to Automation Accounts  
2. Select your Automation Account you created   
3. Navigate to Process Automation → Runbooks  
4. Click on your runbook you created 
5. Click Edit at the top
6. Paste in your full PowerShell automation script (See Invoke-GlobalAdminAccess.ps1)
7. Click Save > Test Pane. (This allows you to test your script)
Confirm:
 - UAMI connects successfully  
- Global Admin list is retrieved  
- Email sends successfully  
- No “Invalid JWT token” errors (means modules are correct)  

Once the test succeeds:
Click Publish 

Your runbook is now active and ready to be triggered manually or by a schedule.

## 10. Automate the Runbook to Run Monthly
With the runbook published, the final step is to create a schedule so the Global Admin Access Review runs automatically every month.
1. Go to your Automation Account
2. In the left-hand menu, select:  
   Process Automation → Runbooks
3. Click your runbook 
4. At the top, select **Schedules
5. Click + Add a schedule
6. Click Link a schedule to your runbook
7. Select + Create a new schedule 
8. Configure the schedule as you desire

Your Global Admin Access Review is now fully automated:
- Reports generated monthly  
- Delivered via email  
- Provides audit-ready evidence for GRC reviews  




