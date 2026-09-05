---
title: Cloud Storage Misconfigurations
aliases:
  - S3 Misconfiguration
  - Blob Storage Security
  - Public Bucket
tags:
  - tree/cloud
  - cyber/content
  - difficulty/practitioner
Domain:
  - "[[Cloud Storage & Workload Security]]"
Color: "#FABED4"
verified: 2026-09-05
---

# Cloud Storage Misconfigurations

> [!abstract] One sentence
> Cloud object storage is the most consistently misconfigured cloud resource — a single "public read" toggle exposes every object in the bucket to the entire internet with no authentication.

**Before you read:** You are mapping the external attack surface of meridian.test. A DNS record points `assets.meridian.test` to `meridian-assets.s3.eu-west-1.amazonaws.com`. What is the first thing you check, and what could you find? Hold your answer.

## Parent Learning Order
[[Cloud Storage & Workload Security]] → **Cloud Storage Misconfigurations** → [[Container & Kubernetes Security]]

---

## The Bucket Permission Model

Every major cloud object store (AWS S3, Azure Blob Storage, GCP Cloud Storage) has two permission layers that both need to be correct:

| Layer | AWS S3 | Azure Blob | GCP GCS |
|---|---|---|---|
| Account-level block | Block Public Access (4 flags) | Storage account public blob access toggle | Uniform bucket-level access |
| Resource-level policy | Bucket policy / ACL | Container access level | Bucket IAM policy |

The misconfiguration always follows the same pattern: an operator disables the account-level block for a legitimate reason (e.g. hosting a static website), then forgets to re-enable it, leaving all current and future buckets open by default.

---

## Recon: Discovering Buckets

### DNS and Certificate Transparency

```bash
# Subdomain enumeration pointing to S3
subfinder -d meridian.test -silent | grep "s3\|blob\|storage"
# assets.meridian.test → meridian-assets.s3.eu-west-1.amazonaws.com

# Certificate transparency — buckets referenced in TLS SANs
curl -s "https://crt.sh/?q=%.meridian.test&output=json" |   python3 -m json.tool | grep name_value | grep -i s3
```

### Direct Bucket Enumeration

```bash
# AWS — check if bucket is public
aws s3 ls s3://meridian-assets --no-sign-request
# 2026-08-01 14:22:10      54321 employee-handbook.pdf
# 2026-08-15 09:10:44    1024000 q3-financial-projections.xlsx
# ← public read: any unauthenticated user can list and download

# Download all objects
aws s3 sync s3://meridian-assets ./meridian-assets --no-sign-request

# Azure — check blob container public access
curl -s "https://meridianfreight.blob.core.windows.net/backups?restype=container&comp=list"
# Returns XML listing if anonymous access is enabled

# GCP
gsutil ls gs://meridian-backups
gsutil -m cp -r gs://meridian-backups ./  # exfiltrate all
```

---

## What Attackers Find in Exposed Buckets

Across public bucket exposures (HackerOne reports, bug bounty write-ups, breach disclosures), the most valuable content types are:

| Content type | Impact | Example indicators |
|---|---|---|
| Database backups | Full data breach — credentials, PII | `*.sql.gz`, `*.dump`, `backup-*.tar` |
| Application secrets | Credential compromise | `.env`, `config.json`, `secrets.yml` |
| Private keys / certs | TLS impersonation, code signing | `*.pem`, `*.key`, `id_rsa` |
| Internal documents | Business intelligence, M&A data | `*.xlsx`, `*.docx` with non-public names |
| Software build artefacts | Supply-chain: tamper and re-upload | `*.jar`, `*.zip`, deployed Lambda packages |
| Log files | Credentials in query strings, tokens | `access.log`, `error.log` |
| Terraform state | Infrastructure map + embedded secrets | `terraform.tfstate` |

```bash
# High-value file hunting in a synced bucket
find ./meridian-assets -name "*.env" -o -name "*.pem" -o -name "*.tfstate"      -o -name "*backup*" -o -name "*secret*" -o -name "*password*" | head -30

# Grep for API keys / tokens in text files
grep -rE "(AKIA[0-9A-Z]{16}|ghp_[a-zA-Z0-9]{36}|xox[baprs]-)" ./meridian-assets/ 2>/dev/null
```

> [!tip] The analogy, and where it breaks
> A public S3 bucket is like a filing cabinet someone put on the street with the drawer open. Everything is readable and, unless logging is enabled, no one knows you looked.
>
> **The deliberate break:** unlike a filing cabinet, an S3 bucket can also be *writable* to anonymous users. A write-accessible bucket lets an attacker replace a JavaScript bundle, a Terraform state file, or a Lambda deployment package — turning storage access into code execution.

---

## Write Access: Supply-Chain via Storage

```bash
# Check if the bucket allows anonymous PUT
aws s3 cp ./malicious.js s3://meridian-assets/app.min.js --no-sign-request
# If this succeeds: every user of the web app now loads attacker-controlled JS

# Check for pre-signed URL abuse — URLs with ?X-Amz-Signature= in outbound traffic
# A pre-signed URL grants time-limited access; if the expiry is long or the URL is leaked:
curl "https://meridian-assets.s3.eu-west-1.amazonaws.com/invoice.pdf?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Expires=604800&X-Amz-Signature=abc123..."
# Valid for 7 days — if URL is in a log file or email, attacker reuses it
```

---

## Remediation and Detection

```bash
# AWS — enable Block Public Access at account level (prevents all future bypasses)
aws s3control put-public-access-block   --account-id 123456789012   --public-access-block-configuration     BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# Audit current bucket policies for public statements
aws s3api get-bucket-policy --bucket meridian-assets |   python3 -c "import sys,json; p=json.load(sys.stdin)['Policy']; print(p)" |   python3 -m json.tool | grep -A3 '"Principal": "\*"'
# Any Principal: * with Effect: Allow = public access

# Enable S3 Access Logs and push to a separate logging bucket
aws s3api put-bucket-logging --bucket meridian-assets   --bucket-logging-status '{"LoggingEnabled":{"TargetBucket":"meridian-logs","TargetPrefix":"s3/"}}'
```

**Detection:** AWS Security Hub and GuardDuty both alert on public bucket policy changes. AWS Macie scans bucket contents for PII and credential patterns automatically — enable it on buckets containing sensitive data.

---

## Security Implications

- **Blast radius scales with content:** an exposed bucket containing compiled frontend JavaScript is a supply-chain incident; one containing Terraform state is a complete infrastructure map and likely a credential theft; one containing a database backup is a full data breach — triage by content, not just exposure.
- **Logging gap:** S3 server access logging is off by default; without it there is no way to determine whether an exposed bucket was accessed before remediation.
- **Compliance:** GDPR Article 32 requires appropriate technical controls; a public bucket containing EU resident PII is a reportable breach within 72 hours of discovery.

---

## Summary

- Public bucket misconfigurations arise when account-level Block Public Access is disabled and bucket or container ACLs are left open; both layers must be correct — a restrictive bucket policy is bypassed by a permissive ACL.
- Recon uses DNS enumeration, certificate transparency, and direct unauthenticated listing; high-value targets inside exposed buckets are database backups, `.env` files, private keys, Terraform state, and build artefacts.
- Write access to a storage bucket escalates from data exfiltration to supply-chain compromise — an attacker who can overwrite a JavaScript bundle or Lambda deployment package controls code execution for every user or service consuming it.

---
> 🔼 Up: [[Cloud Storage & Workload Security]]
