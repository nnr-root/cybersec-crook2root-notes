---
title: Methodologies & Frameworks
aliases:
  - Pentest Methodologies
  - Security Testing Frameworks
  - Penetration Testing Frameworks
tags:
  - tree/offensive
  - cyber/moc
Domain: "[[Penetration Testing]]"
Color: "#DC143C"
---

# Methodologies & Frameworks

> [!abstract] Lifecycle branch
> Governance and mental models that make an assessment repeatable, legal, measurable, and useful to defenders.

```mermaid
flowchart TD
    S["Scope and authorization"] --> T["Threat and adversary model"]
    T --> M["Testing methodology"]
    M --> E["Evidence and risk model"]
    E --> R["Report, remediation, retest"]
```

## 🗺️ Zero-to-Mastery Learning Path

1. [[Penetration Testing Fundamentals]]
2. [[Rules of Engagement & Scoping]]
3. [[Penetration Testing Standards & Frameworks]]
4. [[Cyber Kill Chain]]
5. [[Threat Modeling & MITRE ATT&CK]]

## Practical artifact

```text
Assessment ID: ENT-2026-042
Scope owner: Security Assurance
Method: PTES + NIST SP 800-115 controls
Threat model: External actor and compromised employee
Evidence clock: UTC
Stop authority: Engagement lead and SOC duty manager
```

---
> 🔼 Up: [[Penetration Testing]]
