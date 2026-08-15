---
title: "Enumeration & Service Interaction Tools"
tags: [tree/tooling, cyber/tooling/offensive/enumeration, cyber/moc]
Domain: "[[Offensive Tools]]"
Color: "#708090"
---

# Enumeration & Service Interaction Tools

Tools for discovering content, varying HTTP inputs, and interacting with TCP/UDP services after scope is established.

```mermaid
flowchart LR
    E["Confirmed endpoint"] --> P["Path / parameter enumeration"]
    E --> S["Protocol interaction"]
    P --> C["Candidate inventory"]
    S --> C
```

- [[Gobuster]]
- [[ffuf]]
- [[feroxbuster]]
- [[dirsearch]]
- [[Netcat]]
- [[enum4linux]]

```shell-session
operator@lab:~$ printf '%s\n' health api admin > approved-paths.txt
operator@lab:~$ wc -w approved-paths.txt
3 approved-paths.txt
```

---
> 🔼 Up: [[Offensive Tools]]
