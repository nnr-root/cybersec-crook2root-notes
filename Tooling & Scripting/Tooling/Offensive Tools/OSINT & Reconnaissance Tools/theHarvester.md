---
title: "theHarvester"
aliases: ["theharvester"]
tags: [tree/tooling, cyber/tooling/offensive/osint/theharvester, type/tool, difficulty/medium]
Domain: "[[OSINT & Reconnaissance Tools]]"
Color: "#708090"
---

# theHarvester

theHarvester aggregates a target's public footprint — emails, subdomains, hosts, and sometimes employee names — by querying many passive sources (search engines, certificate transparency, DNS datasets, PGP key servers) through one interface. It is the fast first pass that turns a company name into a starting attack surface without touching the target.

> [!warning] Passive OSINT only
> Results come from third parties, not the target. Harvested emails feed *authorized* phishing simulations within scope — never spam.

## Parent Learning Order
theHarvester -> Amass -> Shodan

## One command fanned out across public sources

theHarvester is the **breadth** tool of passive recon — one command that fans out across many public sources and merges what they know about a domain.

Its place in the map: it sits on the far-left, tapping the widest set of *third-party* sources at once. You never send a packet to the target — you ask search engines, crt.sh, and keyservers what *they* already know, and theHarvester deduplicates it into a first list of emails and hosts. Breadth over depth: it's the "cast a wide net first" pass before Amass digs deep or Shodan tells you what's exposed.

## Choosing a source set, and saving the evidence

Point it at a domain and a source set (`-b`):

```shell-session
operator@kali:~$ theHarvester -d acme-corp.com -b bing,crtsh,duckduckgo
[*] Searching Crtsh, Bing, Duckduckgo...
[*] Emails found:
j.doe@acme-corp.com
security@acme-corp.com
[*] Hosts found:
vpn.acme-corp.com:203.0.113.8
mail.acme-corp.com:203.0.113.25
dev-old.acme-corp.com:198.51.100.4
```

`-b all` runs every source; `-l` limits results; `-f report.json` saves evidence. Some sources (Shodan, Hunter, SecurityTrails) need an **API key** in the config to return anything — a run that finds "nothing" from those is often a missing key, not an empty target.

## Acting on aggregated data without confirming it

Harvested data is *aggregated third-party data*, which means it can be **stale**, and acting on it blindly is the classic mistake:

```shell-session
operator@kali:~$ theHarvester -d acme-corp.com -b crtsh | grep dev-old
dev-old.acme-corp.com:198.51.100.4
operator@kali:~$ dig +short dev-old.acme-corp.com
# (no answer — the record is gone)
operator@kali:~$ host 198.51.100.4
198.51.100.4 belongs to a different cloud tenant now
```

**The deliberate break:** `dev-old.acme-corp.com` came from a *certificate* issued years ago and cached in crt.sh — but it no longer resolves, and that IP has been recycled to a **different cloud tenant**. Treat the harvested list as ground truth and you might scan or phish an asset your client no longer owns — out of scope and potentially illegal. theHarvester tells you what *was* public, not what is *live and yours*. Every harvested host must be re-resolved and ownership-confirmed (WHOIS/ASN) before it enters the active phase, and every harvested email verified before it feeds a phishing sim (distribution lists and ex-employees are common noise). Breadth is the strength; verification is the discipline that makes it usable.

## Summary

You should now be able to:

- Explain why theHarvester counts as passive even though it returns the target's emails and hosts.
- Diagnose the most likely cause when a run returns nothing from the Shodan and SecurityTrails sources.
- Explain why a harvested subdomain can be a scope hazard, and what you verify before acting on it.

---
> 🔼 Up: [[OSINT & Reconnaissance Tools]]
