---
title: "Penetration Testing Lifecycle"
aliases: ["Penetration Testing Lifecycle", "Pentest Lifecycle"]
tags:
  - tree/offensive
  - cyber/moc
Domain: "[[Offensive Security]]"
Color: "#DC143C"
---

# Penetration Testing Lifecycle

> [!abstract] Major pillar of [[Offensive Security]]
> The complete enterprise assessment lifecycle. Methodology, evidence, and attack reasoning live here; product manuals and CLI references remain in **Tooling & Scripting**. Evasion and command-and-control remain exclusively in **Red Team Operations**.

```mermaid
flowchart TD
    M["Methodologies & Frameworks"] --> R["Reconnaissance & Attack Surface"]
    R --> V["Vulnerability Assessment"]
    V --> N["Network Penetration Testing"]
    N --> AD["Active Directory & Identity Exploitation"]
    AD --> W["Web Application Penetration Testing"]
    W --> API["API & Modern Protocol Testing"]
    API --> P["Wireless & Physical Penetration Testing"]
    P --> X["Post-Exploitation & Persistence"]
    X --> RP["Reporting & Purple Teaming"]
    RP --> G["Guided Assessments"]
```

## 🗺️ Zero-to-Mastery Learning Path

1. [[Methodologies & Frameworks]]
2. [[Reconnaissance & Attack Surface]]
3. [[Vulnerability Assessment]]
4. [[Network Penetration Testing]]
5. [[Active Directory & Identity Exploitation]]
6. [[Web Application Penetration Testing]]
7. [[API & Modern Protocol Testing]]
8. [[Wireless & Physical Penetration Testing]]
9. [[Post-Exploitation & Persistence]]
10. [[Reporting & Purple Teaming]]
11. [[Guided Assessments]]

---
> 🔼 Up: [[Offensive Security]]
