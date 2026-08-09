---
title: "Web Injection Testing"
tags: [tree/offensive, cyber/offensive/web/injection, cyber/moc]
Domain: "[[Web Application Penetration Testing]]"
Color: "#DC143C"
---

# Web Injection Testing

Injection occurs when untrusted data changes the grammar or semantics of an interpreter. Testing must trace input through transformations to a specific sink.

```mermaid
flowchart LR
    I["Input"] --> V["Validation"]
    V --> T["Transformation"]
    T --> S["Interpreter sink"]
    S --> O["Differential observation"]
```

## 🗺️ Zero-to-Mastery Learning Path

1. [[SQL Injection]]
2. [[NoSQL Injection]]
3. [[ORM Injection]]
4. [[Operating System Command Injection]]
5. [[Server-Side Template Injection]]
6. [[LDAP Injection]]
7. [[XPath Injection]]
8. [[CRLF Injection]]
9. [[SSI Injection]]

---
> 🔼 Up: [[Web Application Penetration Testing]]
