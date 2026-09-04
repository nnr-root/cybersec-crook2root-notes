---
title: "Masscan"
aliases: ["Mass IP Port Scanner"]
tags: [tree/tooling, cyber/tooling/offensive/masscan, type/tool, difficulty/hard]
Domain: "[[Network Discovery Tools]]"
Color: "#708090"
---

# Masscan

> [!abstract] Note of [[Network Discovery Tools]]
> Masscan probes the whole IPv4 space in minutes by decoupling sending from receiving and keeping no per-connection state — which is its power and its danger, because rate is decoupled from safety. This note covers how a stateless scanner re-associates replies, why an aggressive rate produces false negatives that look like closed ports, and the outbound flood a sweep is from the defender's side.

Masscan is an asynchronous, stateless, Internet-scale SYN scanner. It can probe the entire IPv4 space in minutes because it decouples sending from receiving and keeps *no per-connection state*. That speed is also its danger: it discovers reachability but proves nothing about services, and it can flatten a fragile network long before it strains the scanning host.

> [!warning] Rate is a weapon
> Calculate packet rate from the weakest device on the path, start low, and get a second operator to check scope and exclusions before any high-rate run.

## Parent Learning Order
Nmap -> Masscan -> RustScan

## The first move of a SYN scan, and nothing else

> *Masscan sends the same opening packet as an Nmap SYN scan. What does it not do afterwards?*
>
> Hold your answer — the section below is the response.

Masscan sends the same first move as Nmap's SYN scan — but only the first move.

It fires a `SYN` at every target/port and listens for the `SYN-ACK` (open) or `RST` (closed) from the diagram. What it does **not** do is the rest: no version detection, no handshake completion, no follow-up. It is a firehose of the top row of that table, which is why the mental model is "discover fast, then validate slow." A Masscan hit is a *lead*, never a conclusion.

## Scope in a config file, reviewed before it runs

Masscan needs raw-packet privilege. Put scope in a config file, review it with `--echo`, then run:

```shell-session
operator@lab:~$ sudo masscan --conf approved.conf --echo
rate = 100.00
ports = 22,80,443
range = 203.0.113.0/28
exclude = 203.0.113.7/32
operator@lab:~$ sudo masscan --conf approved.conf
Discovered open port 443/tcp on 203.0.113.10
Discovered open port 22/tcp on 203.0.113.12
```

The options that matter most:

| Purpose | Options |
|---|---|
| Targets | CIDRs, `-iL`, `--exclude`, `--excludefile` |
| Ports | `-p80,443`, ranges, `U:53` for UDP |
| Rate | `--rate`, `--max-rate`, `--wait` |
| Network | `--adapter-ip`, `--adapter-mac`, `--router-mac` |
| Output | `-oB` (binary), `-oJ`, `-oX`, `--readscan` |
| Resume | `--resume paused.conf` |

Then feed the deduplicated `(IP, port)` set into a slower validation stage (Nmap `-sV`):

```shell-session
operator@lab:~$ sudo masscan --conf approved.conf -oB evidence/discovery.scan
operator@lab:~$ masscan --readscan evidence/discovery.scan -oJ evidence/discovery.json
```

## Statelessness, and what it encodes into the packet

Statelessness is the whole design. Nmap remembers every probe it sent; Masscan cannot, so it encodes what it needs to recognise a reply **into the packet itself** — the target IP/port are reconstructed from the response, and a `--seed` randomises the address ordering so a `/8` sweep doesn't hammer one subnet at a time. That is how it re-associates answers with no connection table, and why it scales to the whole internet on one host.

The danger is that rate is decoupled from safety:

```text
100,000 packets/s × 84 bytes × 8 ≈ 67 Mbit/s outbound
Reply bandwidth is tiny — but firewall STATE tables and IDS event volume are not.
```

**The deliberate break:** run at an aggressive `--rate` and results can *drop* — not because ports closed, but because a NAT/firewall state table filled, a router's ARP cache thrashed, or the sensor's ingestion dropped packets. Silence from Masscan is the diagram's `filtered` ambiguity multiplied by loss: a missed port may mean "closed" or "I flooded the path." The fix is to lower the rate, re-sample a small slice, and compare a known-open **canary** service — if the canary disappears at high rate, your optimisation invalidated the whole scan.

**How you'd spot it:** plant a canary — a port you already know is open — and carry it in every sweep. Present at a low rate and absent at a high one means the missing results are your loss, not the target's state. Two runs at the same rate returning materially different port sets say the same thing.

## Security Implications

**A sweep is a measurable outbound flood, and that is the first thing a defender sees.** At 100,000 packets/s the reply bandwidth is tiny but the *event* volume is not: firewall state tables, IDS ingestion, and flow collectors all see a single source touching a vast address-and-port space in seconds. A stateless scanner cannot be quiet by design — its whole premise is volume — so the only real control is rate, and rate is exactly what the operator is tempted to raise.

**The danger runs toward the target, not the scanner.** A rate comfortable for the scanning host can fill a NAT/firewall state table, thrash a router's ARP cache, or exhaust a fragile embedded device on the path — a denial of service delivered by reconnaissance. Calculating rate from the *weakest device on the path* rather than the fastest is the safety discipline, and the canary check is what proves the rate did not silently break the scan.

**A Masscan hit is a lead, never a finding.** It proves a SYN-ACK came back, nothing more — no service, no version, no proof the port is what its number implies. Feeding the deduplicated set into a slower `-sV` stage is not optional polish; reporting a raw Masscan result as a service is reporting an inference as a fact.

All sweeping here targets only approved ranges at a reviewed rate; the outbound volume is attributable and the collateral risk to path devices is real.

## Summary

You should now be able to:

- Explain why Masscan sweeps at rates Nmap cannot, and why a hit is only a lead.
- Choose a safe `--rate`, and describe the discover-then-validate pipeline.
- Explain how a stateless scanner re-associates replies with no connection table, and how excessive rate produces false negatives.

---
> 🔼 Up: [[Network Discovery Tools]]
