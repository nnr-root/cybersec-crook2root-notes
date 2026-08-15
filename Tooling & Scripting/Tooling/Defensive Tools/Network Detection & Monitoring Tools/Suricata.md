---
title: "Suricata"
aliases: ["suricata"]
tags: [tree/tooling, cyber/tooling/defensive/suricata, type/tool, level/operator]
Domain: "[[Network Detection & Monitoring Tools]]"
Color: "#708090"
---

# Suricata

Suricata is the modern, multi-threaded network IDS/IPS. It runs signature rules (Snort-compatible) at high throughput, and — unlike a pure signature engine — *also* logs protocol metadata (like Zeek does) into `eve.json`. It can run passively (IDS: detect) or inline (IPS: block), which makes it the hybrid that sits between the two models in this category.

> [!warning] Inline mode can break traffic
> In IPS mode Suricata drops packets. A bad rule then blocks legitimate traffic — test rules in IDS mode first, and change deployment mode deliberately.

## Parent Learning Order
Suricata -> Snort -> Zeek

## Crook — The Mental Model

There are two ways to watch a network; Suricata is unusual in doing *both*.

![[tool_ids_models.svg]]

On the left of the diagram it is a **signature engine** — matching traffic against known-bad rules and alerting. But it also emits the right-hand side's structured **protocol logs** (`dns.json`, `http`, `tls`, `flow`). And it can flip from **IDS** (out-of-band, detect-only) to **IPS** (inline, block). Understanding which of those three hats it's wearing in a given deployment is the key to Suricata.

## Operator — Make It Work

Rules use the same grammar as Snort; output lands in `eve.json` (one JSON event per line, SIEM-ready):

```shell-session
analyst@sensor:~$ suricata -c /etc/suricata/suricata.yaml -i eth0
analyst@sensor:~$ tail -f /var/log/suricata/eve.json | jq 'select(.event_type=="alert")'
{ "alert": { "signature": "ET MALWARE Cobalt Strike Beacon", "severity": 1 },
  "src_ip": "10.0.0.44", "dest_ip": "203.0.113.9", "dest_port": 443 }
```

A rule reads left to right — *action, protocol, source → destination, then options*:

```text
alert tls any any -> any any (msg:"Self-signed cert to external"; tls.cert_self_signed; sid:100001;)
```

`suricata-update` pulls community rule sets (Emerging Threats); `eve.json` event types (`alert`, `dns`, `http`, `tls`, `flow`) feed a SIEM directly.

## Root — Internals & The Deliberate Break

The IDS-vs-IPS decision is where Suricata can go from *helpful* to *outage*:

```text
# IDS mode (af-packet, out-of-band on a tap) — a false-positive rule just ALERTS
[alert] ET rule 2019... matched  → analyst reviews, no user impact

# IPS mode (inline, NFQUEUE/af-packet inline) — the SAME false-positive rule DROPS
alert → drop   → legitimate connections to a partner API now BLOCKED for everyone
```

**The deliberate break:** a slightly over-broad rule is a minor annoyance in IDS mode (one noisy alert to tune) but a **self-inflicted denial of service** in IPS mode, because inline Suricata *acts* on every match by dropping the packet. The same rule set, two deployment modes, wildly different blast radius. The discipline: develop and tune rules in **IDS mode** against real traffic, measure the false-positive rate, and only promote to inline **IPS** rules you trust — and even then keep a bypass. The other Root reality (shared with Snort): **content signatures can't see inside TLS**, so a growing share of Suricata's value is its *metadata* logging (JA3 fingerprints, SNI, cert anomalies) rather than payload rules — which is exactly the ground Zeek was built for.

## Crook → Operator → Root Checkpoint

- **Crook:** In what three roles can Suricata operate, and how does it differ from a pure signature IDS?
- **Operator:** Read a Suricata rule's structure, and name the output that feeds a SIEM.
- **Root:** Explain why the same rule is safe in IDS mode but dangerous in IPS mode, and what that implies for rollout.

---
> 🔼 Up: [[Network Detection & Monitoring Tools]]
