---
title: "Cloud Red Team Operations"
tags: [tree/offensive, cyber/offensive/red-team/cloud, cyber/moc]
Domain: "[[Red Team Operations]]"
Color: "#DC143C"
---

# Cloud Red Team Operations

```mermaid
flowchart TD
    I["Cloud identity"] --> P["IAM policy/trust"]
    P --> C["Control plane"]
    C --> D["Data/workloads"]
    C --> X["Cross-account paths"]
```

## 🗺️ Zero-to-Mastery Learning Path

1. [[Cloud Identity Operations]]
2. [[Cloud Control Plane Operations]]
3. [[Cloud Persistence Simulation]]
4. [[Cloud Data Access Simulation]]

---
> 🔼 Up: [[Red Team Operations]]
