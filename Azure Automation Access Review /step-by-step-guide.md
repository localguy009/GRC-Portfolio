### 1. Create a User-Assigned Managed Identity (UAMI)

1. In the Azure portal, search for **Managed Identities**.
2. Click **Create** → select **User-assigned**.
3. Choose your **Subscription** and **Resource Group**.
4. Give it a name (e.g., `uami-graph-global-admin-review`).
5. Select the same **Region** you plan to use for your Automation Account.
6. Click **Review + create** → **Create**.
7. After creation, copy the **Client ID** (you’ll use this in the runbook config).

### 2. Grant Microsoft Graph API Permissions to the UAMI

1. Go to **Microsoft Entra ID** → **Enterprise applications**.
2. Search for and open your **User-Assigned Managed Identity**.
3. Go to **Permissions** / **API permissions**.
4. Click **Add a permission** → **Microsoft Graph** → **Application permissions**.
5. Add the following permissions:
   - `Directory.Read.All`
6. Click **Add permissions**.
7. Click **Grant admin consent** for the tenant


### 4. Create an Azure Automation Account

1. In the Azure portal, search for **Automation Accounts**.
2. Click **Create**.
3. Select your **Subscription** and **Resource Group**.
4. Name it (global-admin-review`).
5. Choose the same **Region** as your UAMI.
6. Set **Runbook runtime** to **PowerShell 7.2**
8. Click **Review + create** → **Create**.

### 5. Attach the UAMI to the Automation Account

1. Open your **Automation Account**.
2. Go to **Identity** → **User assigned**.
3. Click **+ Add user assigned**.
4. Select your **UAMI** and click **Add**.
