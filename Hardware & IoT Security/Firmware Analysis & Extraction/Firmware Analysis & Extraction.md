---
title: Firmware Analysis & Extraction
aliases:
  - Firmware Branch
  - Firmware Security
tags:
  - tree/hardware
  - cyber/moc
Domain:
  - "[[Hardware & IoT Security]]"
Color: "#9A6324"
---

# 💾 Firmware Analysis & Extraction

> [!abstract] The Branch
> Firmware is the lowest software layer of an embedded device — extracting it reveals the OS, filesystem, credentials, and cryptographic material that all higher-layer security depends on.

## Learning Path

```mermaid
flowchart LR
    A["💾 Firmware Analysis & Extraction"]
    A --> B["Firmware Extraction & Analysis"]
    style A fill:#111,stroke:#9A6324,color:#9A6324
```

1. [[Firmware Extraction & Analysis]] — physical and logical extraction methods; binwalk filesystem carving; hardcoded credential hunting

---
> 🔼 Up: [[Hardware & IoT Security]]
