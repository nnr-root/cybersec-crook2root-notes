---
title: "SIEM & Detection Engineering Tools"
tags: [tree/tooling, cyber/tooling/defensive/detection-engineering, cyber/moc]
Domain: "[[Defensive Tools]]"
Color: "#708090"
---

# SIEM & Detection Engineering Tools

Search, correlation, portable detection logic, testing, deployment, and feedback from investigations.

```mermaid
flowchart LR
    S["Data sources"] --> N["Normalization"]
    N --> D["Detection logic"]
    D --> A["Alert"]
    A --> T["Triage feedback"]
    T --> D
```

- [[Splunk Basics]]
- [[Sigma]]

```text
rule -> test corpus -> platform conversion -> deployment -> alert review -> tuning
```

---
> 🔼 Up: [[Defensive Tools]]
