---
title: "Network Discovery Tools"
tags: [tree/tooling, cyber/tooling/offensive/discovery, cyber/moc]
Domain: "[[Offensive Tools]]"
Color: "#708090"
---

# Network Discovery Tools

Tools for finding reachable hosts and transport endpoints at controlled rates.

```mermaid
flowchart LR
    S["Approved address scope"] --> F["Fast discovery"]
    F --> V["State validation"]
    V --> E["Structured endpoint inventory"]
```

- [[Nmap]]
- [[Masscan]]
- [[RustScan]]

```shell-session
operator@lab:~$ printf '%s\n' '192.0.2.0/28' > approved-scope.txt
operator@lab:~$ wc -l approved-scope.txt
1 approved-scope.txt
```

---
> 🔼 Up: [[Offensive Tools]]
