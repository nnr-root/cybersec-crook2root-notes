---
title: "Web Application Testing Tools"
tags: [tree/tooling, cyber/tooling/offensive/web, cyber/moc]
Domain: "[[Offensive Tools]]"
Color: "#708090"
verified: 2026-09-05
---

# Web Application Testing Tools

Tools for inspecting, replaying, transforming, and carefully automating HTTP behavior.

```mermaid
flowchart LR
    B["Browser / API client"] --> P["Intercept and replay"]
    P --> T["Authorized application"]
    P --> D["Differential evidence"]
```

- [[curl]]
- [[Postman]]
- [[Burp Suite]]
- [[OWASP ZAP]]
- [[Nikto]]
- [[WPScan]]
- [[SQLmap]]

```shell-session
operator@lab:~$ printf '%s\n' 'Host: app.example.test' 'X-C2R-Test: authorized'
Host: app.example.test
X-C2R-Test: authorized
```

---
> 🔼 Up: [[Offensive Tools]]
