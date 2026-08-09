---
title: "Core Network Services"
aliases: ["Network Services", "Infrastructure Services"]
tags:
  - tree/networking
  - cyber/networking/services
  - cyber/moc
Domain:
  - "[[Networking]]"
Color: "#42D4F4"
---

# 🛎️ Core Network Services

> [!abstract] Services branch
> The infrastructure protocols everything else silently depends on: turning names into addresses, agreeing what time it is, discovering neighbours, moving mail, and reporting state. Each was designed for a cooperative network, and each is now a control point worth attacking precisely because so much trusts it without checking.

```mermaid
flowchart LR
    D["Name resolution"] --> S["Securing name resolution"]
    S --> L["Local discovery fallbacks"]
    L --> T["Time synchronization"]
    T --> M["Mail transport"]
    M --> N["Management & telemetry"]
```

## 🗺️ Zero-to-Mastery Learning Path

1. [[DNS Resolution & Records]]
2. [[DNS Security & Encrypted Transports]]
3. [[Local Name Resolution & Service Discovery]]
4. [[Network Time Synchronization]]
5. [[Email Transport Protocols]]
6. [[Network Management Protocols]]

---
> 🔼 Up: [[Networking]]
