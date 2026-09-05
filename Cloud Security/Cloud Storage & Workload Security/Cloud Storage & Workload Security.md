---
title: Cloud Storage & Workload Security
aliases:
  - Cloud Storage Branch
tags:
  - tree/cloud
  - cyber/moc
Domain:
  - "[[Cloud Security]]"
Color: "#FABED4"
---

# 🗄️ Cloud Storage & Workload Security

> [!abstract] The Branch
> Object storage buckets, container registries, and serverless runtimes share a common failure mode: they are internet-reachable and frequently misconfigured during rapid deployment.

## Learning Path

```mermaid
flowchart LR
    A["🗄️ Cloud Storage & Workload Security"]
    A --> B["Cloud Storage Misconfigurations"]
    A --> C["Container & Kubernetes Security"]
    style A fill:#111,stroke:#FABED4,color:#FABED4
```

1. [[Cloud Storage Misconfigurations]] — public S3/Blob buckets; pre-signed URL abuse; bucket policy confusion
2. [[Container & Kubernetes Security]] — privileged pods; host path mounts; RBAC escalation; etcd exposure

> [!note] Planned notes
> Content notes for this branch are coming soon.

---
> 🔼 Up: [[Cloud Security]]
