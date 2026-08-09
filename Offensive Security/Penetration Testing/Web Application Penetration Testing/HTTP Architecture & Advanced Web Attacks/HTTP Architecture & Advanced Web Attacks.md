---
title: "HTTP Architecture & Advanced Web Attacks"
tags: [tree/offensive, cyber/offensive/web/http, cyber/moc]
Domain: "[[Web Application Penetration Testing]]"
Color: "#DC143C"
---

# HTTP Architecture & Advanced Web Attacks

```mermaid
flowchart LR
    C["Client"] --> E["CDN / WAF"]
    E --> G["Gateway / proxy"]
    G --> O["Origin"]
    O --> CACH["Cache / upstream services"]
```

## 🗺️ Zero-to-Mastery Learning Path

1. [[Server-Side Request Forgery]]
2. [[HTTP Request Smuggling]]
3. [[Web Cache Attacks]]
4. [[WAF Testing & Bypass Methodology]]

---
> 🔼 Up: [[Web Application Penetration Testing]]
