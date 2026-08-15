---
title: "Active Directory & Windows Attack Tools"
tags: [tree/tooling, cyber/tooling/offensive/ad, cyber/moc]
Domain: "[[Offensive Tools]]"
Color: "#708090"
---

# Active Directory & Windows Attack Tools

> [!warning] Authorized operations only
> These tools operate against domain identities and authentication protocols. Use only inside an authorized engagement with a scoped domain, and prefer a purpose-built lab (e.g. GOAD or a throwaway domain) over any production directory.

Active Directory is the identity backbone of most enterprises, and its attack surface is *protocol* rather than *port*: NTLM and Kerberos, LDAP, SMB, and the trust relationships between them. This category holds the instruments that enumerate those relationships, capture and relay authentication, and map the paths from a low-privileged foothold to Domain Admin.

```mermaid
flowchart LR
    P["Poison / capture (Responder)"] --> H["NetNTLM hashes"]
    H --> R["Relay or crack"]
    E["Authenticated enum (NetExec)"] --> G["Graph attack paths (BloodHound)"]
    G --> X["Execute / dump secrets (Impacket)"]
```

## Tools in this category

- [[Impacket]]
- [[NetExec]]
- [[BloodHound]]
- [[Responder]]

```text
Capture identity -> enumerate the domain -> graph the shortest path to DA -> execute/collect under scope
```

The techniques these tools automate are taught in **Offensive Security → Active Directory & Identity Exploitation**; this branch documents the instruments themselves.

---
> 🔼 Up: [[Offensive Tools]]
