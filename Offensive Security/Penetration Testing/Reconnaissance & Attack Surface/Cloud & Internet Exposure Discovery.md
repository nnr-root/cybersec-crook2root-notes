---
title: "Cloud & Internet Exposure Discovery"
aliases: ["Internet Exposure Discovery", "Shodan Recon", "Cloud Asset Discovery"]
tags: [tree/offensive, cyber/offensive/recon/cloud, type/technique, difficulty/medium]
Domain: "[[Reconnaissance & Attack Surface]]"
Color: "#DC143C"
verified: 2026-09-05
---

# ☁️ Cloud & Internet Exposure Discovery

> [!warning] Authorized simulation only
> Internet-wide scan databases (Shodan, Censys) let you read what *others* already scanned — passive with respect to the target. But confirming a finding by connecting to it is active recon requiring scope. Never access an exposed asset (an open bucket, a database) beyond confirming it exists.

## Parent Learning Order
Passive Reconnaissance & OSINT -> DNS & Subdomain Reconnaissance -> Active Reconnaissance & Port Scanning -> Cloud & Internet Exposure Discovery

## Someone Already Scanned the Internet

> *You want a target's exposed assets without sending them a single packet. Possible?*
>
> Hold your answer — the section below is the response.

You do not need to scan the whole Internet to find a target's exposed assets — **someone already did**. Services like **Shodan** and **Censys** continuously scan every routable address, fingerprint what they find, and make it searchable. Querying them is *passive* with respect to your target: the packets came from the scanner, not you. This is the cloud-era evolution of recon, because the modern attack surface is not a tidy perimeter — it is a sprawl of cloud instances, storage buckets, forgotten VMs, and SaaS integrations that no firewall fully contains.

The discipline of finding all of it — continuously — is **Attack Surface Management (ASM)**. Offensively it finds the way in; defensively it is how an organization discovers the asset it forgot it owned.

> [!tip] The analogy, and where it breaks
> Shodan is like a real-estate database that already photographed every building's exterior, so you search "buildings with an unlocked side door in this city" instead of walking every street. The analogy breaks because the photos are *live and specific* — Shodan returns the actual software version and open ports of a specific host, not a generic image, so a search can surface a specific vulnerable device directly.

**Prerequisites:** ports and services, passive recon, and basic cloud concepts (public IP ranges, object storage).

## The Modern Surface: Why the Perimeter Dissolved

Traditional recon assumed a perimeter — a block of the organization's IPs behind a firewall. Cloud broke that model:

| Old surface | Cloud surface |
| --- | --- |
| Owned IP ranges | Ephemeral cloud IPs from shared provider pools |
| Servers in a data center | Instances spun up and forgotten by any team |
| Files on internal shares | Object-storage buckets, public by misconfiguration |
| Known applications | SaaS integrations, each its own login and surface |

The consequence: an organization often does not know its own attack surface, because any engineer with a cloud account can create an exposed asset in minutes. This is why **discovery** — not just scanning a known range — is the core skill.

## Internet-Wide Search: Reading Others' Scans

Shodan and Censys index the Internet by service fingerprint. The queries are precise:

```text
# Shodan query examples (run in the Shodan web UI or API):
org:"Example Corp"                        # assets attributed to an org
ssl.cert.subject.cn:"example.com"         # hosts serving a cert for the domain
http.title:"Dashboard" org:"Example Corp" # exposed admin dashboards
product:MongoDB "example.com"             # exposed databases
```

The API is queryable read-only:

```bash
# host lookup for a public IP (read-only; reveals what Shodan already saw)
curl -s "https://internetdb.shodan.io/203.0.113.20"
```

```text
{"cpes":[],"hostnames":["example.com"],"ip":"203.0.113.20","ports":[80,443],"tags":[],"vulns":[]}
```

`internetdb.shodan.io` is a free, unauthenticated endpoint returning ports, hostnames, and known CVEs Shodan already observed for an IP — all without you scanning anything. `"ports":[80,443]` and an empty `"vulns"` is the clean result; a real finding would list open management ports and CVE identifiers.

## Cloud Asset Discovery: Buckets and Beyond

**Object storage** (S3, Azure Blob, GCS) is the most common cloud exposure. Buckets are often named predictably (`example-backups`, `example-prod-data`), and a public-read bucket lists its contents to anyone. The *discovery* is guessing names and checking existence — the *finding* is a public bucket:

```bash
# check whether a bucket name exists and its access (read-only HEAD)
curl -s -o /dev/null -w "%{http_code}\n" "https://example-assets.s3.amazonaws.com/"
```

```text
403
```

`403` means the bucket exists but is not public-listable — the safe result. `404` means no such bucket; `200` means **public listing enabled**, a finding. Note you confirmed existence without accessing contents; enumerating or downloading objects is a line you do not cross without explicit authorization.

```mermaid
flowchart TD
    O["Org name + domain (from passive recon)"] --> S["Search Shodan/Censys: org, cert, product"]
    O --> B["Guess cloud asset names: buckets, instances"]
    S --> E["Exposed services: ports, versions, known CVEs"]
    B --> P["Public buckets / storage"]
    E --> M["Continuous ASM: the surface, monitored"]
    P --> M
    M --> N["Prioritize: what is exposed AND vulnerable?"]
```

## Why a cloud IP may not be your target's tomorrow

- **Attribution is hard in the cloud.** A cloud IP is drawn from a shared provider pool — today it is the target's, next week someone else's. Confirm ownership (via certificate CN, hostname, or content) before attributing, or you will test a stranger's asset.
- **Stale index data.** Shodan's data is as old as its last scan of that host — a listed port may be closed now, and a closed one may have opened since. Treat it as a lead, confirm liveness within scope.
- **Buckets: existence vs. access.** A `403` (exists, private) is not a finding; only a `200` listing or readable objects is. Reporting the mere existence of a bucket as a vulnerability is a false positive.
- **The surface changes hourly.** Cloud assets are ephemeral, so a one-time discovery is stale immediately. This is why ASM must be *continuous*, not a single scan.

**The deliberate break:** an asset appearing in an internet-wide index reads as an asset that exists now and belongs to whoever the record says it does.

Those records are **historical**, and cloud addresses are recycled between tenants continuously. A result showing an exposed service may describe a host that was decommissioned months ago, or — far worse — an address that now belongs to an entirely different organisation who will experience your scoped, authorised testing as an unsolicited attack. The index answers what was true when the scanner passed, and says nothing about today or about ownership.

**How you'd spot it:** re-resolve and re-confirm before touching anything: `whois` and the ASN for current ownership, and a scoped live check for current state. The specific hazard worth naming is a hostname harvested from an old certificate that has not resolved in a year, whose historical address now serves somebody else's application.

## Security Implications — Detection & Defense

- **You cannot detect the Shodan query**, because the target was scanned by a third party, not you — the same undetectable-collection problem as passive recon. The defense is again *reducing exposure*, not detecting the search.
- **Continuous self-ASM is the primary control.** An organization must run these exact discovery techniques against itself, continuously, to find the forgotten instance or public bucket before an attacker does. "We don't know what we have exposed" is the root failure.
- **Cloud guardrails prevent the exposure at creation:** organization-wide policies blocking public buckets, service control policies restricting public IP assignment, and mandatory tagging so every asset has an owner. These stop the misconfiguration rather than hunting it later.
- **Certificate and DNS hygiene** (from earlier leaves) limits how easily assets are attributed to the organization in the first place.
- **The asymmetry favors the attacker** — they need one exposed asset; the defender must find all of them — which is exactly why automated, continuous ASM exists.

## Summary

You should now be able to:

- Explain why you don't need to scan the Internet yourself, why the cloud dissolved the traditional perimeter, and what Attack Surface Management is.
- Query Shodan's data for a host's ports and known CVEs, check a bucket's exposure by HTTP status, and attribute a cloud IP to the correct owner before acting.
- Explain why the Shodan query is undetectable at the target and why continuous self-ASM plus cloud guardrails — not scan detection — are the defense; describe the attacker/defender asymmetry that makes automated discovery necessary.

---
> 🔼 Up: [[Reconnaissance & Attack Surface]]
