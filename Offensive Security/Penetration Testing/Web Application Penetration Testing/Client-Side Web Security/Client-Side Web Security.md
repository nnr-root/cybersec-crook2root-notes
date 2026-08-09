---
title: "Client-Side Web Security"
tags: [tree/offensive, cyber/offensive/web/client-side, cyber/moc]
Domain: "[[Web Application Penetration Testing]]"
Color: "#DC143C"
---

# Client-Side Web Security

Browser security depends on origins, execution contexts, DOM sinks, cookies, navigation, framing, storage, and cross-origin policy.

```mermaid
flowchart TD
    U["Untrusted source"] --> D["DOM / JavaScript"]
    D --> X["Execution sink"]
    B["Browser security model"] --> D
    P["CSP / SameSite / CORS"] --> B
```

## 🗺️ Zero-to-Mastery Learning Path

1. [[CORS & Clickjacking]]
2. [[Cross-Site Scripting]]
3. [[CSRF & SameSite Testing]]
4. [[Prototype Pollution & DOM Security]]

---
> 🔼 Up: [[Web Application Penetration Testing]]
