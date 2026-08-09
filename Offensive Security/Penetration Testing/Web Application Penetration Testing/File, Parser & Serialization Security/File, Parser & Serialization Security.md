---
title: "File, Parser & Serialization Security"
tags: [tree/offensive, cyber/offensive/web/parsers, cyber/moc]
Domain: "[[Web Application Penetration Testing]]"
Color: "#DC143C"
---

# File, Parser & Serialization Security

```mermaid
flowchart LR
    U["Upload / path / document"] --> P["Parser"]
    P --> O["Object or filesystem"]
    O --> E["Execution / disclosure / mutation"]
```

## 🗺️ Zero-to-Mastery Learning Path

1. [[File Inclusion & Path Traversal]]
2. [[File Upload Security Testing]]
3. [[Insecure Deserialization Testing]]
4. [[XML External Entity Testing]]

---
> 🔼 Up: [[Web Application Penetration Testing]]
