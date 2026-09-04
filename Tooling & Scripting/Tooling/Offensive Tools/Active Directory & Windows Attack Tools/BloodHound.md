---
title: "BloodHound"
aliases: ["bloodhound", "SharpHound"]
tags: [tree/tooling, cyber/tooling/offensive/ad/bloodhound, type/tool, difficulty/hard]
Domain: "[[Active Directory & Windows Attack Tools]]"
Color: "#708090"
---

# BloodHound

> [!abstract] Note of [[Active Directory & Windows Attack Tools]]
> BloodHound is the map that decides which technique to run next. This note covers the graph model underneath it, the two very different collection methods and the very different noise they make, why the shortest path is often the wrong one, and what the collection leaves in a defender's logs.

BloodHound turns Active Directory from a list of objects into a **graph of attack paths**. A collector (SharpHound) enumerates users, groups, sessions, ACLs, and trusts; BloodHound loads them into a graph database where a query answers the only question that matters: *what is the shortest path from what I control to Domain Admin?* It finds abuse chains no human would spot by reading object lists.

> [!warning] Authorized operations only
> Collection is read-heavy LDAP/SMB enumeration of every domain object. Run only in scope; session and ACL data is sensitive engagement evidence.

## Parent Learning Order
Impacket -> NetExec -> BloodHound -> Responder -> Mimikatz

## Active Directory as a directed graph

> *You have a complete list of every group membership in the domain. Why is that not the same as knowing your path to Domain Admin?*
>
> Hold your answer — the section below is the response.

BloodHound is the **map** — the step that tells you *which* technique to run next.

The core idea: AD is a directed graph. Nodes are users, computers, and groups; **edges** are permissions — `MemberOf`, `AdminTo`, `HasSession`, `GenericAll`, `CanRDP`. A path along those edges from your foothold to Domain Admin *is* an attack plan. What looks like a flat directory is really a web of transitive rights, and BloodHound computes the shortest route through it — often three unexpected hops a human would never connect.

## Collect, import, mark owned, query

Collect with SharpHound (from Windows) or the Python/Rust collector (from Linux), then import the JSON/zip into the BloodHound UI:

```shell-session
operator@kali:~$ bloodhound-python -u r.okonkwo -p 'Summer2024!' -d meridian.test -ns 10.10.20.10 -c All
INFO: Found AD domain: meridian.test
INFO: Connecting to LDAP server: dc01.meridian.test
INFO: Found 412 users, 89 computers, 57 groups
INFO: Querying computer: WS-014.meridian.test
INFO: Querying computer: WS-030.meridian.test
INFO: Querying computer: FS01.meridian.test
INFO: Compressed output written to 20260810_bloodhound.zip
```

Those per-computer lines are the important half and are examined below — the domain-wide facts come from one LDAP conversation with the DC, but sessions and local admin membership do not exist in LDAP at all.

Import, **mark your owned nodes** ("Mark as Owned"), then run a pre-built query — *"Shortest Paths to Domain Admins from Owned Principals."* An edge like `svc_backup —GenericAll→ DC01` tells you the exact abuse (here: an ACL takeover). Right-click any edge for BloodHound's built-in "help" describing the technique and the command to run (usually an **Impacket** or PowerShell one-liner).

### What the pre-built queries actually are

The interface is a front end to a **Neo4j** graph database, and every canned query is Cypher. Knowing that is the difference between using BloodHound and interrogating it, because the questions worth asking on a real engagement are rarely on the menu:

```cypher
MATCH p = shortestPath(
  (n:User {owned:true})-[*1..]->(g:Group {name:"DOMAIN ADMINS@MERIDIAN.TEST"})
) RETURN p
```

```text
(r.okonkwo) -[MemberOf]-> (HELPDESK@MERIDIAN.TEST)
            -[HasSession]-> (WS-030.MERIDIAN.TEST)
            -[AdminTo]-> (admin_bob@MERIDIAN.TEST)
            -[MemberOf]-> (DOMAIN ADMINS@MERIDIAN.TEST)
```

Two properties of that query are worth reading rather than copying. `shortestPath` optimises for **hop count** and nothing else — it has no notion of how likely a hop is to still work. And `[*1..]` traverses **any** edge type, so a path through a session that existed for four minutes ranks equal with a path through an ACL that has existed for four years.

Both are fixable in the query itself, which is the main reason to learn Cypher here. Restricting the traversal to durable edge types asks a different and usually better question:

```cypher
MATCH p = shortestPath(
  (n:User {owned:true})-[:MemberOf|AdminTo|GenericAll|GenericWrite|WriteDacl|Owns*1..]->
  (g:Group {name:"DOMAIN ADMINS@MERIDIAN.TEST"})
) RETURN p
```

The second query returns fewer paths and better ones.

## Possible paths versus reachable ones

The graph shows what's *possible*; it does not prove what's *reachable right now*:

```text
Path found:  jdoe →(MemberOf)→ Helpdesk →(HasSession on WS30)→ admin_bob →(AdminTo)→ DC01
```

**The deliberate break:** that path depends on the edge `HasSession on WS30` — meaning admin_bob had a session on WS30 *when SharpHound collected*. Sessions are a **point-in-time snapshot**; by the time you act, bob may have logged off and the path evaporates. Likewise a `CanRDP` edge is only useful if you *also* have bob's credential and network reachability to the box. BloodHound ranks by graph distance, not by feasibility — the "shortest" path may need a vanished session while a "longer" `GenericAll` ACL path (which is permanent and needs no session) is actually the easy win. The skill is reading edges by *durability*: ACL edges (GenericAll, WriteDacl, GenericWrite) are stable and preferred; session/RDP edges are opportunistic and perishable. Re-collect for fresh sessions, and always verify feasibility before committing to a path.

**How you'd spot it:** check the edge type before planning around a path. `HasSession` and `CanRDP` depend on a state that may already be gone; `MemberOf`, `GenericAll` and `GenericWrite` are ACL facts that persist until someone changes them. Read the collection timestamp alongside — a session-dependent path in week-old data is a lead, not a route.

## Two collections, two completely different noise profiles

The single most consequential operational choice is what to collect, because the methods differ in kind rather than degree.

**LDAP-only collection** (`-c DCOnly`) asks the domain controller for objects, group memberships, ACLs, trusts and SPNs. It is one authenticated conversation with one host, and every domain-joined machine makes LDAP queries all day.

**Session and local-admin collection** (`-c Session,LocalAdmin`, included in `-c All`) cannot come from LDAP, because neither fact lives in the directory. Who is logged on to `FS01` is known only to `FS01`. So the collector connects to **every computer object in the domain** over SMB and calls `NetSessionEnum` and `NetWkstaUserEnum` against each one.

```text
-c DCOnly       1 host contacted    (the DC, over LDAP)
-c All         90 hosts contacted    (the DC, plus an SMB call to every computer object)
```

That is the whole stealth question in two lines. One workstation opening an SMB session to all eighty-nine other machines inside a few minutes is a pattern with no legitimate counterpart — no user, no backup agent and no inventory tool touches every host from a workstation. It is trivially detectable by anyone looking, and it is what makes the difference between a collection nobody notices and an engagement that ends on day one.

The mitigations are ordinary and worth stating plainly: prefer `DCOnly` unless session data is genuinely needed, collect from a host where that traffic is plausible, and use `--jitter` and `--throttle` so the calls are not a burst. Sessions are also the perishable data, so a stealthy engagement often collects `DCOnly` early and takes sessions late, narrowly, and only for the handful of hosts a candidate path actually needs.

## Security Implications

**The collection is the detectable event, not the analysis.** Once the zip is on the operator's machine, every query runs locally against Neo4j and produces no traffic at all. Everything a defender can see happened during collection, which is why the collection choices above matter more than anything done afterwards.

**On the DC, the signal is query shape rather than volume.** LDAP from a workstation is normal; a single client retrieving every user, every group, every computer and the full `nTSecurityDescriptor` of each in one session is not. Enabling **LDAP diagnostic logging** for expensive and inefficient searches (field engineering event 1644) surfaces exactly this class, and it is off by default.

**On the member hosts, the signal is the fan-out.** Each `NetSessionEnum` leaves a network logon on the target — event **4624 type 3** with the collecting account — and share access shows as **5140/5145** against `IPC$`. One account producing that on ninety machines within minutes is the finding, and it is a rule about the *count of distinct destinations per source*, not about any single event.

**Session data is a privacy and evidence obligation, not just a finding.** A completed graph records who was logged on where and when, across the whole estate. It is engagement evidence, it identifies individuals, and it should be handled and destroyed on the same terms as any other collected credential material.

**Defenders should run it first.** BloodHound is at least as valuable to the owner of the directory as to an attacker, because the shortest path from a random workstation to Domain Admin is a number an organisation can measure, act on and re-measure. Removing one ACL edge often deletes hundreds of paths at once, and nothing else in the AD toolkit gives that kind of leverage.

## Summary

You should now be able to:

- Explain why modelling AD as a graph of edges is more powerful than reading group memberships, and turn a collected graph into an attack plan in two steps.
- Write a Cypher query directly rather than using a canned one, and explain why constraining the traversal to durable edge types asks a better question than `shortestPath` over any edge.
- Explain why the "shortest path" isn't always the easiest, contrasting a session-dependent edge with an ACL edge; state why `-c All` contacts every computer in the domain while `-c DCOnly` contacts one, and describe the detection that follows from that fan-out.

---
> 🔼 Up: [[Active Directory & Windows Attack Tools]]
