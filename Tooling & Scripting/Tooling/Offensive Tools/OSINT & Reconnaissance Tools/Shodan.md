---
title: "Shodan"
aliases: ["shodan"]
tags: [tree/tooling, cyber/tooling/offensive/osint/shodan, type/tool, difficulty/medium]
Domain: "[[OSINT & Reconnaissance Tools]]"
Color: "#708090"
---

# Shodan

Shodan is a search engine for internet-connected devices. It continuously scans the public IPv4 space, grabs service banners, and indexes them — so instead of scanning a target yourself, you *query someone else's scan results*. One search reveals a target's exposed services, software versions, open databases, and control panels, all without sending the target a packet.

> [!warning] Query, don't attack
> Shodan is passive reconnaissance against a public index. Confirm current ownership before treating a result as in-scope, and never act on an exposed service without authorization for that asset.

## Parent Learning Order
theHarvester -> Amass -> Shodan

## Passive recon where the scanning already happened

Shodan is the *extreme* case of passive recon: the scanning already happened.

On the map, Shodan is its own data source — it scanned the whole internet *for you*, so reading a Shodan result is reconnaissance with **zero** packets to the target. That inverts the usual model: normally you scan a host to learn its open ports; with Shodan you *search* for hosts that already have a given port/product/vulnerability open. It answers "what is exposed?" before you've decided to touch anything.

## Filters that make the index surgical

Search the web UI or the CLI. The power is in **filters**:

```shell-session
operator@kali:~$ shodan search 'org:"Acme Corp" port:3389'
203.0.113.40   3389/tcp   Remote Desktop   Windows Server 2016
198.51.100.9   3389/tcp   Remote Desktop   (NLA disabled)     ← exposed RDP, no NLA
operator@kali:~$ shodan host 203.0.113.40
Ports: 80, 443, 3389
  3389/tcp  RDP  ·  Vulnerabilities: CVE-2019-0708 (BlueKeep)
```

Filters make it surgical: `org:` / `net:` (scope to an org or netblock), `port:`, `product:`, `version:`, `country:`, `hostname:`, `vuln:` (paid), and `ssl.cert.subject.cn:` for cert-based discovery. `shodan host <ip>` is a full passive profile of one address.

## Two opposite failures of a stale snapshot

Shodan's index is a **snapshot**, and its two failure modes are opposite sides of the same coin:

```shell-session
operator@kali:~$ shodan host 198.51.100.9
  Last update: 2026-06-02        ← 10 weeks ago
  3389/tcp  RDP  (NLA disabled)
operator@kali:~$ nmap -p3389 --script rdp-ntlm-info 198.51.100.9    # ground truth, today
3389/tcp closed ms-wbt-server
operator@kali:~$ whois 198.51.100.9 | grep -i orgname
OrgName: SomeOtherCloudTenant, Inc.        ← NOT Acme Corp anymore
```

**The deliberate break:** two problems at once. First, the RDP that Shodan shows "open with NLA disabled" was scanned 10 weeks ago and is **closed now** — Shodan reports history, not live state. Second, and far more dangerous: that IP has been **reassigned to a different cloud tenant**, so it isn't your client's asset at all. Acting on a Shodan result — scanning or, worse, connecting to it — without re-confirming *current* ownership (`whois`/ASN) and *current* state (a scoped live check) risks attacking a stranger's system, which is both out of scope and potentially a crime. Shodan is a phenomenal lead generator precisely because it's pre-computed and passive; that same pre-computation is why every result needs a freshness-and-ownership check before it crosses from "intel" to "target."

## Summary

You should now be able to:

- Explain why searching Shodan reveals a target's exposed services without scanning them yourself.
- Write a Shodan query to find an org's exposed RDP, and name three useful filters.
- Explain Shodan's two snapshot hazards (stale state and IP reassignment) and what you verify before acting on a result.

---
> 🔼 Up: [[OSINT & Reconnaissance Tools]]
