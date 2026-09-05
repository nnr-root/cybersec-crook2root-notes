---
title: "Zeek"
aliases: ["zeek", "Bro"]
tags: [tree/tooling, cyber/tooling/defensive/zeek, type/tool, difficulty/hard]
Domain: "[[Network Detection & Monitoring Tools]]"
Color: "#708090"
verified: 2026-09-05
---

# Zeek

> [!abstract] Note of [[Network Detection & Monitoring Tools]]
> Zeek is a network-traffic **recorder**, not a signature engine. It understands protocols and writes a structured transcript of everything that happened — the raw material of threat hunting and network forensics, and the only lens in this category that still works when the payload is encrypted.

Zeek (formerly Bro) is a network-traffic **recorder**, not a signature engine. It watches traffic, understands the protocols, and writes rich, structured logs — one per protocol (`conn.log`, `dns.log`, `http.log`, `ssl.log`, `files.log`). It doesn't tell you "this is bad"; it gives you a queryable transcript of *everything that happened*, which is the raw material of threat hunting and network forensics.

> [!warning] Captures are sensitive
> Zeek logs record who talked to whom and (for cleartext) what about. Treat the logs as sensitive data and run only where authorized.

## Parent Learning Order
Suricata -> Snort -> Zeek

**Prerequisites:** [[Snort]] and [[Suricata]] first — Zeek is defined by contrast with them. You should also be comfortable with `awk`, `sort` and `uniq`, because hunting is mostly that.

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
10.10.10.14  198.51.100.9  0.512
10.10.10.14  198.51.100.9  0.498     ← same pair, regular ~0.5s connections
10.10.10.14  198.51.100.9  0.505
```

`zeek-cut` extracts columns from the tab-separated logs. The high-value logs: `conn.log` (every flow + duration + bytes), `dns.log` (queries — catch DGA/exfil), `ssl.log` (JA3 + SNI + cert), `http.log`, `files.log` (extracted files + hashes). Zeek's scripting language lets you write custom detections that trigger on protocol events.

> [!tip] The analogy, and where it breaks
> Snort is a smoke alarm; Zeek is the building's CCTV. The alarm tells you *now* and tells you nothing else; the cameras tell you nothing now and answer any question you think to ask later. The analogy breaks on who does the work. Nobody has to watch a smoke alarm, and CCTV that nobody reviews is a storage bill. Zeek moves the effort from the rule author to the analyst, and a deployment without analyst time is not a quieter Snort, it is an expensive log pipeline.

## The event engine, and the uid that ties the logs together

Zeek is two layers, and the split is why it is extensible where a signature engine is not. The C++ **event engine** parses protocols and raises semantic events — `connection_established`, `dns_request`, `http_reply`, `ssl_client_hello` — with no opinion about what any of them mean. Above it, the **policy layer** is Zeek's own scripting language, where handlers subscribe to those events and decide what to record. `conn.log` is not a built-in feature; it is the output of the `base/protocols/conn` scripts that ship with Zeek. Writing a custom detection therefore means writing an event handler in a language that already knows what a DNS response is, rather than describing bytes.

The practical consequence is the field beginners overlook: every log line carries a **`uid`**, one identifier per connection, shared across every log the connection touched. That is the pivot. A suspicious name in `dns.log` gives you a `uid`; the same `uid` in `conn.log` gives duration and byte counts; in `ssl.log` the certificate and fingerprint; in `files.log` the SHA-256 of what was transferred. Hunting in Zeek is almost always "find one interesting row, then follow its `uid` sideways."

`ssl.log` deserves particular attention, because it is where Zeek earns its keep against encrypted traffic. It records the SNI, the certificate, and the **JA3** fingerprint: an MD5 over the client's offered TLS version, ciphers, extensions, curves and point formats, in the client's own order. That ordering is a property of the TLS *implementation*, so it survives a domain rotation and a change of IP:

```text
JA3 string: 771,4865,0,,
JA3 hash  : 1e7c622032b0cb79401b0f7be3793a1a
```

Nothing there required decrypting anything. A client whose fingerprint matches no browser in the fleet, talking to a destination nobody else visits, is a hunt that a payload signature could not have expressed.

One log to watch before you trust any of the others: `capture_loss.log`, which reports the percentage of traffic Zeek believes it missed, inferred from gaps in TCP sequence numbers. A sensor dropping ten percent of packets produces logs that look completely normal and quietly answer your hunting queries wrong. Check it first, every time.

## Why 'no alerts' means it is working

New Zeek users open the tool expecting alerts — and find none:

```shell-session
analyst@sensor:~$ zeek -i eth0
analyst@sensor:~$ ls
conn.log  dns.log  http.log  ssl.log  files.log   ← logs, but where are the ALERTS?
# there are none. You HUNT. C2 beaconing shows up as regularity, not a signature:
analyst@sensor:~$ cat conn.log | zeek-cut id.resp_h ts | sort | \
    awk '{d=$2-p[$1]; if(d>55&&d<65) c[$1]++; p[$1]=$2} END{for(h in c) if(c[h]>10) print h,c[h]}'
198.51.100.9  47     ← 47 connections at a steady ~60s interval = a beacon
```

**The deliberate break:** Zeek produces **no alerts**, and a beginner concludes it's "not working." It's working perfectly — Zeek's model is *record now, detect later*. A Cobalt Strike beacon calling home every 60 seconds matches no Snort signature (the payload is encrypted, the domain rotates), but in `conn.log` it's glaringly obvious: the same destination at a metronomic interval. That's the class of threat behavioural monitoring exists to catch and signatures never will. The tradeoff the diagram states plainly: Zeek shifts the work from the *rule author* (signatures) to the *analyst* (hunting) — more effort, but it's the only side of the house that sees the novel and the encrypted. In practice you run Zeek *and* Suricata: signatures for the known, Zeek logs for everything else, both feeding the SIEM.

**How you'd spot it:** the absence of alerts is normal; the absence of *logs* is not, so confirm `conn.log` is growing. Then look for the thing rather than wait for it: group connections by destination and examine the interval between them — a low standard deviation around a repeating interval is a beacon, whatever the payload encryption.

## Security Implications

Zeek logs are a surveillance record of the organisation, and their sensitivity is easy to underestimate because they contain no payload. `conn.log` alone establishes who talked to whom, for how long and how much — enough to reconstruct working relationships, working hours and, from an employee's DNS queries, a great deal that is nobody's business. `http.log` on any remaining cleartext holds URLs with tokens in them, and `files.log` can be configured to extract and store the transferred files themselves. Retention, access control and a stated purpose are not paperwork here; in many jurisdictions they are the difference between monitoring and unlawful interception.

The sensor's own exposure mirrors [[Suricata]]'s. Zeek's protocol analysers parse hostile input by design and have carried memory-safety bugs; a sensor on a span port sees everything, which makes it the most valuable host on the segment. Give the capture interface no address, keep management on a separate path, and run workers unprivileged.

The attacker's counter-play is not evasion of a rule — there is no rule — but denial of the *record*. Traffic that never crosses the monitored link is invisible: host-to-host inside a virtual switch, anything inside a VPN or an SSH tunnel, and increasingly DNS over HTTPS, which converts the single most productive log in the corpus into an indistinguishable HTTPS flow. Flooding a sensor to force drops has the same effect and is cheaper. The defensive answer is architectural rather than clever: monitor the choke points traffic must cross, force internal DNS through resolvers you log, and alert on `capture_loss` rather than assuming silence means peace.

## Summary

You should now be able to:

- Explain how Zeek differs from Snort and Suricata, and why it still works on encrypted traffic.
- Name four Zeek logs and what each is used to hunt for.
- Explain Zeek's two-layer architecture, and use a `uid` to pivot one connection across `dns.log`, `conn.log`, `ssl.log` and `files.log`.
- Explain why Zeek emits no alerts by design, show how a C2 beacon surfaces in `conn.log` when no signature would catch it, and say what `capture_loss.log` is protecting you from.

---
> 🔼 Up: [[Network Detection & Monitoring Tools]]
