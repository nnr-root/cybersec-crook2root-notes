---
title: "theHarvester"
aliases: ["theharvester"]
tags: [tree/tooling, cyber/tooling/offensive/osint/theharvester, type/tool, difficulty/medium]
Domain: "[[OSINT & Reconnaissance Tools]]"
Color: "#708090"
---

# theHarvester

> [!abstract] Note of [[OSINT & Reconnaissance Tools]]
> theHarvester is the breadth pass: one command fanned across many public sources, merging what third parties already know about a domain into a first list of emails and hosts, with zero packets to the target. This note covers choosing a source set, why an empty result is usually a missing API key rather than an empty target, and why every harvested host and email needs re-verification before it enters an active phase.

theHarvester aggregates a target's public footprint — emails, subdomains, hosts, and sometimes employee names — by querying many passive sources (search engines, certificate transparency, DNS datasets, PGP key servers) through one interface. It is the fast first pass that turns a company name into a starting attack surface without touching the target.

> [!warning] Passive OSINT only
> Results come from third parties, not the target. Harvested emails feed *authorized* phishing simulations within scope — never spam.

## Parent Learning Order
theHarvester -> Amass -> Shodan

## One command fanned out across public sources

> *One command, fanned out across many public sources. Is theHarvester optimising for depth or breadth?*
>
> Hold your answer — the section below is the response.

theHarvester is the **breadth** tool of passive recon — one command that fans out across many public sources and merges what they know about a domain.

Its place in the map: it sits on the far-left, tapping the widest set of *third-party* sources at once. You never send a packet to the target — you ask search engines, crt.sh, and keyservers what *they* already know, and theHarvester deduplicates it into a first list of emails and hosts. Breadth over depth: it's the "cast a wide net first" pass before Amass digs deep or Shodan tells you what's exposed.

## Choosing a source set, and saving the evidence

Point it at a domain and a source set (`-b`):

```shell-session
operator@kali:~$ theHarvester -d meridian.test -b bing,crtsh,duckduckgo
[*] Searching Crtsh, Bing, Duckduckgo...
[*] Emails found:
r.okonkwo@meridian.test
security@meridian.test
[*] Hosts found:
vpn.meridian.test:203.0.113.8
mail.meridian.test:203.0.113.25
dev-old.meridian.test:192.0.2.4
```

`-b all` runs every source; `-l` limits results; `-f report.json` saves evidence. Some sources (Shodan, Hunter, SecurityTrails) need an **API key** in the config to return anything — a run that finds "nothing" from those is often a missing key, not an empty target.

## Acting on aggregated data without confirming it

Harvested data is *aggregated third-party data*, which means it can be **stale**, and acting on it blindly is the classic mistake:

```shell-session
operator@kali:~$ theHarvester -d meridian.test -b crtsh | grep dev-old
dev-old.meridian.test:192.0.2.4
operator@kali:~$ dig +short dev-old.meridian.test
# (no answer — the record is gone)
operator@kali:~$ host 192.0.2.4
192.0.2.4 belongs to a different cloud tenant now
```

**The deliberate break:** `dev-old.meridian.test` came from a *certificate* issued years ago and cached in crt.sh — but it no longer resolves, and that IP has been recycled to a **different cloud tenant**. Treat the harvested list as ground truth and you might scan or phish an asset your client no longer owns — out of scope and potentially illegal. theHarvester tells you what *was* public, not what is *live and yours*. Every harvested host must be re-resolved and ownership-confirmed (WHOIS/ASN) before it enters the active phase, and every harvested email verified before it feeds a phishing sim (distribution lists and ex-employees are common noise). Breadth is the strength; verification is the discipline that makes it usable.

**How you'd spot it:** re-resolve everything before acting on it. A harvested name that does not resolve today is history; one that resolves into an ASN your client does not own belongs to somebody else. Both are common enough that re-resolution is a workflow step rather than a caveat in the report.

## Security Implications

**It leaves no trace on the target, so the exposure it finds must be managed at the source.** Every result comes from a third party — search engines, crt.sh, keyservers — so the target logs nothing and can detect nothing. The defensive use is again the inversion: harvest your own domain to see the emails and hosts an attacker will start from, because you cannot stop the collection, only reduce what there is to collect.

**Harvested emails are the raw material for phishing, which links this to the social-engineering branch.** A list of real addresses and a naming convention (`first.last@`) is exactly what a phishing campaign needs, which is why the addresses are sensitive engagement evidence and feed only *authorised* simulations. A distribution list or an ex-employee in the list is common noise that must be verified before use.

**Aggregated data is stale by nature, and acting on it blindly is a scope hazard.** A subdomain from a years-old certificate may no longer resolve, and its IP may have been recycled to a different tenant — so re-resolution and ownership confirmation (`whois`/ASN) are workflow steps, not caveats. theHarvester reports what *was* public, never what is *live and yours*.

## Summary

You should now be able to:

- Explain why theHarvester counts as passive even though it returns the target's emails and hosts.
- Diagnose the most likely cause when a run returns nothing from the Shodan and SecurityTrails sources.
- Explain why a harvested subdomain can be a scope hazard, and what you verify before acting on it.

---
> 🔼 Up: [[OSINT & Reconnaissance Tools]]
