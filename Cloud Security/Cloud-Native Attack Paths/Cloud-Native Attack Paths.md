---
title: Cloud-Native Attack Paths
aliases:
  - Cloud Attack Paths Branch
tags:
  - tree/cloud
  - cyber/moc
Domain:
  - "[[Cloud Security]]"
Color: "#FABED4"
---

# 🛣️ Cloud-Native Attack Paths

> [!abstract] The Branch
> Cloud-native services expose metadata APIs, assume-role endpoints, and secrets managers — each an attacker pivot point reachable from a compromised workload.

## Learning Path

```mermaid
flowchart LR
    A["🛣️ Cloud-Native Attack Paths"]
    A --> B["SSRF to Metadata & Credential Theft"]
    A --> C["Cloud Lateral Movement"]
    style A fill:#111,stroke:#FABED4,color:#FABED4
```

1. [[SSRF to Metadata & Credential Theft]] — IMDSv1 vs IMDSv2; Azure IMDS; GCP metadata server; token exfiltration via SSRF
2. [[Cloud Lateral Movement]] — cross-account role chaining; resource-based policy abuse; VPC peering pivots

> [!note] Planned notes
> Content notes for this branch are coming soon.

---
> 🔼 Up: [[Cloud Security]]
