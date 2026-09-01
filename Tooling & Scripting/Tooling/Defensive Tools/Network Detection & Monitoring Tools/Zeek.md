---
title: "Zeek"
aliases: ["zeek", "Bro"]
tags: [tree/tooling, cyber/tooling/defensive/zeek, type/tool, difficulty/hard]
Domain: "[[Network Detection & Monitoring Tools]]"
Color: "#708090"
---

# Zeek

Zeek (formerly Bro) is a network-traffic **recorder**, not a signature engine. It watches traffic, understands the protocols, and writes rich, structured logs — one per protocol (`conn.log`, `dns.log`, `http.log`, `ssl.log`, `files.log`). It doesn't tell you "this is bad"; it gives you a queryable transcript of *everything that happened*, which is the raw material of threat hunting and network forensics.

> [!warning] Captures are sensitive
> Zeek logs record who talked to whom and (for cleartext) what about. Treat the logs as sensitive data and run only where authorized.

## Parent Learning Order
Suricata -> Snort -> Zeek

## Recording behaviour instead of matching signatures

> *You deploy Zeek and it raises no alerts at all. Is it broken?*
>
> Hold your answer — the section below is the response.

Zeek is the entire right-hand model of the diagram — behaviour, not signatures.

Where Snort/Suricata ask "did a *known* threat just happen?", Zeek asks nothing — it simply *records*. Every connection becomes a row in `conn.log`; every DNS lookup a row in `dns.log`; every TLS handshake (JA3, SNI, cert) a row in `ssl.log`. The detection happens *later*, when you or a SIEM hunt over those logs for what's abnormal. Its superpower is seeing patterns no signature could encode — and doing so even on **encrypted** traffic, because it reasons about *metadata*, not payload.

## Pointing it at an interface and reading the logs

Point Zeek at an interface (or a pcap); it produces the logs:

```shell-session
analyst@sensor:~$ zeek -i eth0
analyst@sensor:~$ head -1 conn.log; cat conn.log | zeek-cut id.orig_h id.resp_h duration | head
10.10.10.44  203.0.113.9   0.512
10.10.10.44  203.0.113.9   0.498     ← same pair, regular ~0.5s connections
10.10.10.44  203.0.113.9   0.505
```

`zeek-cut` extracts columns from the tab-separated logs. The high-value logs: `conn.log` (every flow + duration + bytes), `dns.log` (queries — catch DGA/exfil), `ssl.log` (JA3 + SNI + cert), `http.log`, `files.log` (extracted files + hashes). Zeek's scripting language lets you write custom detections that trigger on protocol events.

## Why 'no alerts' means it is working

New Zeek users open the tool expecting alerts — and find none:

```shell-session
analyst@sensor:~$ zeek -i eth0
analyst@sensor:~$ ls
conn.log  dns.log  http.log  ssl.log  files.log   ← logs, but where are the ALERTS?
# there are none. You HUNT. C2 beaconing shows up as regularity, not a signature:
analyst@sensor:~$ cat conn.log | zeek-cut id.resp_h ts | sort | \
    awk '{d=$2-p[$1]; if(d>55&&d<65) c[$1]++; p[$1]=$2} END{for(h in c) if(c[h]>10) print h,c[h]}'
203.0.113.9  47      ← 47 connections at a steady ~60s interval = a beacon
```

**The deliberate break:** Zeek produces **no alerts**, and a beginner concludes it's "not working." It's working perfectly — Zeek's model is *record now, detect later*. A Cobalt Strike beacon calling home every 60 seconds matches no Snort signature (the payload is encrypted, the domain rotates), but in `conn.log` it's glaringly obvious: the same destination at a metronomic interval. That's the class of threat behavioural monitoring exists to catch and signatures never will. The tradeoff the diagram states plainly: Zeek shifts the work from the *rule author* (signatures) to the *analyst* (hunting) — more effort, but it's the only side of the house that sees the novel and the encrypted. In practice you run Zeek *and* Suricata: signatures for the known, Zeek logs for everything else, both feeding the SIEM.

## Summary

You should now be able to:

- Explain how Zeek differs from Snort and Suricata, and why it still works on encrypted traffic.
- Name four Zeek logs and what each is used to hunt for.
- Explain why Zeek emits no alerts by design, and show how a C2 beacon surfaces in `conn.log` when no signature would catch it.

---
> 🔼 Up: [[Network Detection & Monitoring Tools]]
