---
title: "Defensive Tools"
aliases: ["Defensive Armory"]
tags: [tree/tooling, cyber/tooling/defensive, cyber/moc]
Domain: "[[Tooling]]"
Color: "#708090"
---

# Defensive Tools

> [!abstract] Purpose-driven defensive Armory
> Tools are grouped by the evidence or control they provide: packets, endpoint events, analytics, content classification, and network detection.

```mermaid
flowchart TD
    D["Defensive Tools"] --> PA["Packet Analysis Tools"]
    D --> ET["Endpoint Telemetry Tools"]
    D --> SD["SIEM & Detection Engineering Tools"]
    D --> MC["Malware & Content Analysis Tools"]
    D --> NM["Network Detection & Monitoring Tools"]
```

## Purpose categories

- [[Packet Analysis Tools]]
- [[Endpoint Telemetry Tools]]
- [[SIEM & Detection Engineering Tools]]
- [[Malware & Content Analysis Tools]]
- [[Network Detection & Monitoring Tools]]

```text
Collect trustworthy evidence -> normalize -> detect -> investigate -> contain -> improve
```

---
> 🔼 Up: [[Tooling]]
