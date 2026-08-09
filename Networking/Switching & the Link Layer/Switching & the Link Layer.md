---
title: "Switching & the Link Layer"
aliases: ["Layer 2", "Switching", "Ethernet Networking"]
tags:
  - tree/networking
  - cyber/networking/layer2
  - cyber/moc
Domain:
  - "[[Networking]]"
Color: "#42D4F4"
---

# 🔗 Switching & the Link Layer

> [!abstract] Switching branch
> The layer where frames are built, where switches learn who is where, and where almost every protocol was designed with no authentication whatsoever. Local-segment trust is assumed by default at Layer 2, which is why this branch ends with the controls that replace that assumption with evidence.

```mermaid
flowchart LR
    E["Frame format"] --> S["Switch learning & forwarding"]
    S --> A["Address resolution"]
    A --> V["Segmentation with VLANs"]
    V --> L["Loop prevention"]
    L --> C["Authentication & integrity controls"]
```

## 🗺️ Zero-to-Mastery Learning Path

1. [[Ethernet & Frame Structure]]
2. [[MAC Addressing & Switch Operation]]
3. [[ARP & Neighbor Discovery]]
4. [[VLANs & Trunking]]
5. [[Spanning Tree & Loop Prevention]]
6. [[Link Layer Security Controls]]

---
> 🔼 Up: [[Networking]]
