<#
Monthly Global Administrator access review automation

This runbook:
- Authenticates to Microsoft Graph using a User-Assigned Managed Identity (UAMI)
- Queries Entra ID Global Administrator role membership
- Generates an HTML report
- Sends results via email using an App Registration (client credential flow)

All sensitive IDs and email addresses have been removed for security.
#>

# UAMI client ID (replace with your own when deploying)
$UamiClientId = "<UAMI-CLIENT-ID>"

# Tenant ID (replace with your own when deploying)
$TenantId  = "<TENANT-ID>"

# Name of Automation Account PSCredential used for App Registration email sender
$CredName  = "<AUTOMATION-CREDENTIAL-NAME>"

# Sender and recipient email address (generic placeholders)
$FromAddress = "<SENDER@DOMAIN.COM>"
$ToAddress   = "<RECIPIENT@DOMAIN.COM>"

# Email subject
$Subject = "Monthly Global Administrator Access Review"


# ===========================
# 1. READ GLOBAL ADMINS USING UAMI
# ===========================

Write-Output "Connecting to Microsoft Graph with UAMI for directory read..."

Connect-MgGraph -Identity -ClientId $UamiClientId -NoWelcome

try {
    # Get Global Administrator directory role
    $gaRole = Get-MgDirectoryRole -Filter "displayName eq 'Global Administrator'" |
              Select-Object -First 1

    if (-not $gaRole) {
        throw "Global Administrator role not found in this tenant."
    }

    Write-Output "Found Global Administrator role with Id: $($gaRole.Id). Pulling members..."

    $members = Get-MgDirectoryRoleMember -DirectoryRoleId $gaRole.Id

    if (-not $members) {
        Write-Output "No members found in Global Administrator role."
        $adminUsers = @()
    }
    else {
        # Resolve directory objects to full user objects
        $adminUsers = foreach ($m in $members) {
            try {
                Get-MgUser -UserId $m.Id -ErrorAction Stop
            }
            catch {
                $null   # Ignore service principals + non-user objects
            }
        }

        $adminUsers = $adminUsers | Where-Object { $_ -ne $null } | Sort-Object DisplayName
    }

    Write-Output "Resolved $($adminUsers.Count) Global Administrator user(s)."
}
finally {
    Disconnect-MgGraph
    Write-Output "Disconnected UAMI Graph session."
}


# ===========================
# 2. BUILD HTML REPORT BODY
# ===========================

if ($adminUsers.Count -gt 0) {
    $rows = foreach ($a in $adminUsers) {
        "<tr><td>$($a.DisplayName)</td><td>$($a.UserPrincipalName)</td></tr>"
    }

    $adminTable = @"
<table border='1' cellpadding='6' cellspacing='0' style='border-collapse: collapse; font-family: Arial, sans-serif; font-size: 12px;'>
<tr style='background-color: #f2f2f2;'>
    <th align='left'>Name</th>
    <th align='left'>User Principal Name</th>
</tr>
$rows
</table>
"@
}
else {
    $adminTable = "<p><i>No active users are currently assigned the Global Administrator role.</i></p>"
}

$bodyHtml = @"
<p>Hello,</p>
<p>Below is the current list of users assigned the <b>Global Administrator</b> role as of <b>$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</b>:</p>
$adminTable
<p>This email was generated automatically by Azure Automation.</p>
"@


# ===========================
# 3. GET OAUTH TOKEN FOR APP REGISTRATION (CLIENT CREDENTIALS)
# ===========================

Write-Output "Retrieving App Registration client ID and secret from Automation credential..."

$creds = Get-AutomationPSCredential -Name $CredName
if (-not $creds) {
    throw "Automation credential '$CredName' not found."
}

$ClientId     = $creds.UserName
$ClientSecret = $creds.GetNetworkCredential().Password

Write-Output "Requesting OAuth 2.0 token for Microsoft Graph..."

$tokenResponse = Invoke-RestMethod -Method POST -Uri "https://login.microsoftonline.com/$TenantId/oauth2/v2.0/token" -Body @{
    client_id     = $ClientId
    client_secret = $ClientSecret
    scope         = "https://graph.microsoft.com/.default"
    grant_type    = "client_credentials"
}

$accessToken = $tokenResponse.access_token
if (-not $accessToken) {
    throw "Failed to obtain access token."
}

Write-Output "Access token obtained successfully."


# ===========================
# 4. SEND EMAIL VIA GRAPH /sendMail
# ===========================

Write-Output "Building and sending email payload..."

$headers = @{
    "Authorization" = "Bearer $accessToken"
    "Content-Type"  = "application/json"
}

$messagePayload = @{
    message = @{
        subject = $Subject
        body    = @{
            contentType = "HTML"
            content     = $bodyHtml
        }
        toRecipients = @(
            @{
                emailAddress = @{
                    address = $ToAddress
                }
            }
        )
    }
    saveToSentItems = $true
}

$jsonBody = $messagePayload | ConvertTo-Json -Depth 10

Invoke-RestMethod -Method POST `
    -Uri "https://graph.microsoft.com/v1.0/users/$FromAddress/sendMail" `
    -Headers $headers `
    -Body $jsonBody

Write-Output "Global Administrator access review email sent."
