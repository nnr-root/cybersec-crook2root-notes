---
title: "BloodHound"
aliases: ["bloodhound", "SharpHound"]
tags: [tree/tooling, cyber/tooling/offensive/ad/bloodhound, type/tool, difficulty/hard]
Domain: "[[Active Directory & Windows Attack Tools]]"
Color: "#708090"
---

# BloodHound

BloodHound turns Active Directory from a list of objects into a **graph of attack paths**. A collector (SharpHound) enumerates users, groups, sessions, ACLs, and trusts; BloodHound loads them into a graph database where a query answers the only question that matters: *what is the shortest path from what I control to Domain Admin?* It finds abuse chains no human would spot by reading object lists.

> [!warning] Authorized operations only
> Collection is read-heavy LDAP/SMB enumeration of every domain object. Run only in scope; session and ACL data is sensitive engagement evidence.

## Parent Learning Order
Impacket -> NetExec -> BloodHound -> Responder

## Active Directory as a directed graph

> *You have a complete list of every group membership in the domain. Why is that not the same as knowing your path to Domain Admin?*
>
> Hold your answer — the section below is the response.

BloodHound is the **map** — the step that tells you *which* technique to run next.

The core idea: AD is a directed graph. Nodes are users, computers, and groups; **edges** are permissions — `MemberOf`, `AdminTo`, `HasSession`, `GenericAll`, `CanRDP`. A path along those edges from your foothold to Domain Admin *is* an attack plan. What looks like a flat directory is really a web of transitive rights, and BloodHound computes the shortest route through it — often three unexpected hops a human would never connect.

## Collect, import, mark owned, query

Collect with SharpHound (from Windows) or the Python/Rust collector (from Linux), then import the JSON/zip into the BloodHound UI:

```shell-session
operator@kali:~$ bloodhound-python -u jdoe -p Summer2024 -d corp.local -ns 10.10.20.10 -c All
INFO: Found 412 users, 89 computers, 57 groups
INFO: Compressed output written to 20260810_bloodhound.zip
```

Import, **mark your owned nodes** ("Mark as Owned"), then run a pre-built query — *"Shortest Paths to Domain Admins from Owned Principals."* An edge like `svc_sql —GenericAll→ DC01` tells you the exact abuse (here: an ACL takeover). Right-click any edge for BloodHound's built-in "help" describing the technique and the command to run (usually an **Impacket** or PowerShell one-liner).

## Possible paths versus reachable ones

The graph shows what's *possible*; it does not prove what's *reachable right now*:

```text
Path found:  jdoe →(MemberOf)→ Helpdesk →(HasSession on WS30)→ admin_bob →(AdminTo)→ DC01
```

**The deliberate break:** that path depends on the edge `HasSession on WS30` — meaning admin_bob had a session on WS30 *when SharpHound collected*. Sessions are a **point-in-time snapshot**; by the time you act, bob may have logged off and the path evaporates. Likewise a `CanRDP` edge is only useful if you *also* have bob's credential and network reachability to the box. BloodHound ranks by graph distance, not by feasibility — the "shortest" path may need a vanished session while a "longer" `GenericAll` ACL path (which is permanent and needs no session) is actually the easy win. The skill is reading edges by *durability*: ACL edges (GenericAll, WriteDacl, GenericWrite) are stable and preferred; session/RDP edges are opportunistic and perishable. Re-collect for fresh sessions, and always verify feasibility before committing to a path.

**How you'd spot it:** check the edge type before planning around a path. `HasSession` and `CanRDP` depend on a state that may already be gone; `MemberOf`, `GenericAll` and `GenericWrite` are ACL facts that persist until someone changes them. Read the collection timestamp alongside — a session-dependent path in week-old data is a lead, not a route.

## Summary

You should now be able to:

- Explain why modelling AD as a graph of edges is more powerful than reading group memberships.
- Turn a collected graph into an attack plan in two steps.
- Explain why the "shortest path" isn't always the easiest, contrasting a session-dependent edge with an ACL edge.

---
> 🔼 Up: [[Active Directory & Windows Attack Tools]]
