---
title: "Amass"
aliases: ["amass", "OWASP Amass"]
tags: [tree/tooling, cyber/tooling/offensive/osint/amass, type/tool, difficulty/hard]
Domain: "[[OSINT & Reconnaissance Tools]]"
Color: "#708090"
verified: 2026-09-05
---

# Amass

> [!abstract] Note of [[OSINT & Reconnaissance Tools]]
> Amass maps one target's whole DNS estate into a graph, and its single most important property is that it straddles the passive/active line — one flag turns invisible third-party lookups into thousands of queries at the target's own resolvers. This note covers what each mode touches, the finding certificate transparency hands you for free, and why the tool is as valuable pointed at your own domains.

OWASP Amass is the deep subdomain-enumeration and attack-surface-mapping engine. It fuses dozens of passive sources (certificate transparency, DNS aggregators, ASN/WHOIS, web archives) and optional active techniques (DNS brute-force, permutations) into one deduplicated graph of a target's DNS estate — far broader than any single source.

> [!warning] Passive by default, active on request
> `amass enum` is largely passive; `-active` and `-brute` send traffic to the target's infrastructure. Decide which mode you're in *before* you run.

## Parent Learning Order
theHarvester -> Amass -> Shodan

## Mapping one target's DNS estate into a graph

> *Is Amass a passive tool?*
>
> Hold your answer — the section below is the response.

Amass is the **depth** tool — where theHarvester casts a wide net, Amass exhaustively maps one target's DNS estate into a graph.

But note *where* Amass sits on the map: it **straddles the passive/active line**. Its default enumeration is passive (querying cert transparency, DNS datasets, archives — the target sees nothing). The moment you add `-brute` or `-active`, it starts sending DNS queries and probes *to the target itself* — crossing into active recon, where you appear in their logs. Understanding which side of that line a given command lives on is the single most important thing about Amass.

## Passive first, then active inside scope

Passive first — quiet and free:

```shell-session
operator@kali:~$ amass enum -passive -d meridian.test -o subs.txt
vpn.meridian.test
api.meridian.test
staging.meridian.test
internal-dev.meridian.test     ← "internal" name leaked via a public certificate
operator@kali:~$ wc -l subs.txt
147 meridian.test subdomains
```

Then, *in scope*, go active to find names no public source knows:

```shell-session
operator@kali:~$ amass enum -active -brute -d meridian.test -w wordlist.txt
```

`intel` gathers ASNs/orgs; `-df` scopes to specific domains; the graph database (`amass db`) lets you track how the surface changes over time.

## The flag that turns quiet recon into logged traffic

The passive/active distinction is not academic — it's the difference between invisible and logged:

```shell-session
# PASSIVE — third parties only, target sees nothing
operator@kali:~$ amass enum -passive -d meridian.test
[reads crt.sh, DNS datasets, web archives]     ← 0 packets to meridian.test's DNS

# ACTIVE/BRUTE — thousands of DNS queries STRAIGHT AT the target's resolvers
operator@kali:~$ amass enum -brute -d meridian.test -w big-wordlist.txt
[a1.meridian.test? a2.meridian.test? ...]       ← Meridian's DNS logs light up
```

**The deliberate break:** a beginner runs `amass enum -brute` on a "passive recon" engagement, assuming Amass is always passive, and dumps tens of thousands of DNS lookups onto the target's authoritative servers — noisy, potentially disruptive, and outside a passive scope. Same tool, two utterly different footprints, separated by one flag. Always run `-passive` first (it's quiet, free, and often finds the "internal-dev" names leaked in certificates), and only cross into `-active`/`-brute` when the RoE authorizes touching the target. The corollary discovery from the passive run above — an `internal-*` hostname exposed in a public TLS certificate — is exactly the kind of finding cert transparency hands you for free, no active probing required.

**How you'd spot it:** the flag is the finding, so read the command before the output. `-passive` touches third-party sources only; `-brute` and `-active` send queries to the target's own authoritative servers. From the target's side it is unmistakable — tens of thousands of NXDOMAIN responses from one resolver inside a short window.

## Security Implications

**Passive enumeration leaves nothing on the target, which is the security point, not a gap.** The names Amass finds passively come from certificate transparency, DNS datasets and archives — the target's own logs never see the query, so there is no telemetry to detect and nothing to alert on. Exposure that leaks this way cannot be caught at the perimeter; it can only be managed at the source, which is why the defensive answer is to run Amass against your own domains before an attacker does.

**Certificate transparency is the leak that needs no probing.** The `internal-dev` name above came from a public TLS certificate: every certificate an organisation is issued is published to append-only CT logs, so an internal hostname put behind a public cert is public the moment the cert exists. Monitoring CT for your own domains turns that from an attacker's free finding into a defender's alert.

**`-brute` and `-active` cross into logged traffic and possible disruption.** They send queries straight at the target's authoritative servers — tens of thousands of NXDOMAINs from one resolver — so the mode is a scope decision, not a preference, and running it under a passive RoE is an out-of-scope act, not an aggressive one.

## Summary

You should now be able to:

- Distinguish Amass from theHarvester on depth versus breadth, and explain why Amass produces a *graph*.
- Write the command for a quiet, in-scope first pass, and name what turns it active.
- Explain exactly what changes between `amass enum -passive` and `-brute`, and why the distinction is a scope/OPSEC decision.

---
> 🔼 Up: [[OSINT & Reconnaissance Tools]]
