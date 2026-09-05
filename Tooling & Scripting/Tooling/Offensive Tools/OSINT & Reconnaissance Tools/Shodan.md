---
title: "Shodan"
aliases: ["shodan"]
tags: [tree/tooling, cyber/tooling/offensive/osint/shodan, type/tool, difficulty/medium]
Domain: "[[OSINT & Reconnaissance Tools]]"
Color: "#708090"
verified: 2026-09-05
---

# Shodan

> [!abstract] Note of [[OSINT & Reconnaissance Tools]]
> Shodan is reconnaissance with zero packets to the target: it scanned the internet for you, so you query someone else's results instead of scanning yourself. This note covers the filters that make the index surgical, its two snapshot hazards — stale state and IP reassignment — and why the same pre-computation that makes it powerful makes every result a lead that needs a freshness-and-ownership check.

Shodan is a search engine for internet-connected devices. It continuously scans the public IPv4 space, grabs service banners, and indexes them — so instead of scanning a target yourself, you *query someone else's scan results*. One search reveals a target's exposed services, software versions, open databases, and control panels, all without sending the target a packet.

> [!warning] Query, don't attack
> Shodan is passive reconnaissance against a public index. Confirm current ownership before treating a result as in-scope, and never act on an exposed service without authorization for that asset.

## Parent Learning Order
theHarvester -> Amass -> Shodan

## Passive recon where the scanning already happened

> *How many packets do you send the target when you research it on Shodan?*
>
> Hold your answer — the section below is the response.

Shodan is the *extreme* case of passive recon: the scanning already happened.

On the map, Shodan is its own data source — it scanned the whole internet *for you*, so reading a Shodan result is reconnaissance with **zero** packets to the target. That inverts the usual model: normally you scan a host to learn its open ports; with Shodan you *search* for hosts that already have a given port/product/vulnerability open. It answers "what is exposed?" before you've decided to touch anything.

## Filters that make the index surgical

Search the web UI or the CLI. The power is in **filters**:

```shell-session
operator@kali:~$ shodan search 'org:"Meridian Freight" port:3389'
203.0.113.40   3389/tcp   Remote Desktop   Windows Server 2016
192.0.2.9   3389/tcp   Remote Desktop   (NLA disabled)     ← exposed RDP, no NLA
operator@kali:~$ shodan host 203.0.113.40
Ports: 80, 443, 3389
  3389/tcp  RDP  ·  Vulnerabilities: CVE-2019-0708 (BlueKeep)
```

Filters make it surgical: `org:` / `net:` (scope to an org or netblock), `port:`, `product:`, `version:`, `country:`, `hostname:`, `vuln:` (paid), and `ssl.cert.subject.cn:` for cert-based discovery. `shodan host <ip>` is a full passive profile of one address.

## Two opposite failures of a stale snapshot

Shodan's index is a **snapshot**, and its two failure modes are opposite sides of the same coin:

```shell-session
operator@kali:~$ shodan host 192.0.2.9
  Last update: 2026-06-02        ← 10 weeks ago
  3389/tcp  RDP  (NLA disabled)
operator@kali:~$ nmap -p3389 --script rdp-ntlm-info 192.0.2.9    # ground truth, today
3389/tcp closed ms-wbt-server
operator@kali:~$ whois 192.0.2.9 | grep -i orgname
OrgName: SomeOtherCloudTenant, Inc.        ← NOT Meridian Freight anymore
```

**The deliberate break:** two problems at once. First, the RDP that Shodan shows "open with NLA disabled" was scanned 10 weeks ago and is **closed now** — Shodan reports history, not live state. Second, and far more dangerous: that IP has been **reassigned to a different cloud tenant**, so it isn't your client's asset at all. Acting on a Shodan result — scanning or, worse, connecting to it — without re-confirming *current* ownership (`whois`/ASN) and *current* state (a scoped live check) risks attacking a stranger's system, which is both out of scope and potentially a crime. Shodan is a phenomenal lead generator precisely because it's pre-computed and passive; that same pre-computation is why every result needs a freshness-and-ownership check before it crosses from "intel" to "target."

**How you'd spot it:** every result carries a timestamp; read it before anything else, and treat anything older than the asset's likely lifetime as a lead rather than a fact. Then confirm ownership separately with `whois` and the ASN, because a cloud address that has changed tenant still carries the previous tenant's banner in the index.

## Security Implications

**Zero packets to the target means zero telemetry for the target — for either side.** Researching an organisation on Shodan leaves nothing in its logs, so a defender cannot detect the reconnaissance at all. The security response is the inversion: an organisation can query Shodan for its *own* netblocks, and Shodan Monitor will alert when a new exposed service appears in the index — knowing your exposure before an attacker searches for it is the only available defence against a source the target cannot see.

**The snapshot hazards are an attribution and legal risk, not just an accuracy one.** A result is history: the RDP shown open may be closed now, and — the dangerous case — the IP may have been reassigned to a different cloud tenant. Acting on a stale result without re-confirming current ownership (`whois`/ASN) and current state risks scanning or connecting to a stranger's system, which is out of scope and potentially a crime. The timestamp is the first field to read on every result.

**`vuln:` results are claims from a banner, not proof.** Shodan infers `CVE-2019-0708` from a version string, which a patched-but-unbanner-changed host contradicts. The finding is a lead to validate in scope, never a confirmed vulnerability to report.

## Summary

You should now be able to:

- Explain why searching Shodan reveals a target's exposed services without scanning them yourself.
- Write a Shodan query to find an org's exposed RDP, and name three useful filters.
- Explain Shodan's two snapshot hazards (stale state and IP reassignment) and what you verify before acting on a result.

---
> 🔼 Up: [[OSINT & Reconnaissance Tools]]
