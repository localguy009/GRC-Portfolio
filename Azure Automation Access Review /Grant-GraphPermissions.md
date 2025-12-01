# **Granting Microsoft Graph Permissions for the Managed Identity**

This guide provides instructions for assigning the required Microsoft Graph application permissions to the User-Assigned Managed Identity (UAMI) used by the Azure Automation runbook.

Some Azure tenants restrict granting these permissions through the portal.  
If you cannot add the Graph permission or grant admin consent through the UI, this script will

## **Where to Run the Script**

The script must be executed in **Azure Cloud Shell (PowerShell)**.

```powershell
# Authenticate (must be run first)
Connect-MgGraph -Scopes "Directory.ReadWrite.All"
```
```powershell
# Managed Identity's Service Principal Object ID
$spId = "<INSERT-MANAGED-IDENTITY-SP-OBJECT-ID>"

# Get the Microsoft Graph service principal
$graph = Get-MgServicePrincipal -Filter "appId eq '00000003-0000-0000-c000-000000000000'"

# Assign Directory.Read.All to the MI
New-MgServicePrincipalAppRoleAssignment `
    -ServicePrincipalId $spId `
    -PrincipalId $spId `
    -ResourceId $graph.Id `
    -AppRoleId (
        $graph.AppRoles |
        Where-Object { $_.Value -eq "Directory.Read.All" -and $_.AllowedMemberTypes -contains "Application" }
    ).Id
```
