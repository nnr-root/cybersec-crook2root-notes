---
title: "Snort"
aliases: ["snort"]
tags: [tree/tooling, cyber/tooling/defensive/snort, type/tool, difficulty/medium]
Domain: "[[Network Detection & Monitoring Tools]]"
Color: "#708090"
---

# Snort

Snort is the original signature-based network IDS — the tool that defined what a detection rule looks like. It inspects packets against a rule set and alerts (or, inline, blocks) when traffic matches a known-bad pattern. Its rule syntax became the industry lingua franca (Suricata speaks it too), which makes Snort the best place to *learn how signatures work*.

> [!warning] Detection needs tuning
> Out-of-the-box rule sets produce noise. An untuned Snort drowns analysts in false positives; a well-tuned one is a precise sensor.

## Parent Learning Order
Suricata -> Snort -> Zeek

## Matching traffic against known-bad patterns

Snort is the archetype of the left-hand model: match traffic against a library of known-bad patterns.

Each Snort **rule** describes one threat — "if you see *this* pattern going to *that* port, alert." It's fast and low-effort because the analysis is pre-encoded in the rule; the cost is that Snort can only catch what someone already wrote a rule for. That single property — powerful against the known, blind to the novel — is the whole nature of signature detection, and Snort is where you internalise it.

## Reading a rule: action, protocol, direction, options

A Snort rule is *action, protocol, src → dst, (options)*:

```text
alert tcp any any -> $HOME_NET 445 (msg:"SMB exploit attempt";
      flow:to_server; content:"|FF|SMB"; sid:1000001; rev:1;)
```

```shell-session
analyst@sensor:~$ snort -c /etc/snort/snort.conf -i eth0 -A console
[**] [1:1000001:1] SMB exploit attempt [**]
{TCP} 10.0.0.44:51234 -> 10.0.0.5:445
```

`content:` is the byte pattern to match; `flow:` scopes direction; `sid:` uniquely identifies the rule; `msg:` is the alert text. `-A console` prints alerts; production logs to unified2 → a SIEM. Community and subscriber (Talos) rule sets provide thousands of maintained rules.

## How literal matching gets encoded around

A signature matches *exactly what it describes* — and attackers exploit that literalness:

```text
Rule:    content:"/bin/sh"
Catches: GET /cgi?cmd=/bin/sh          ✓
Evades:  GET /cgi?cmd=/bin/${x}sh      ✗   (shell var — same effect, different bytes)
         GET /cgi?cmd=%2fbin%2fsh      ✗   (URL-encoded)
         [any content inside TLS]      ✗   (encrypted — Snort sees ciphertext)
```

**The deliberate break:** a content rule for `/bin/sh` catches the naive payload but is trivially evaded by encoding, padding, or a shell variable that produces the *same effect* with *different bytes* — and it is blind entirely once the traffic is encrypted. This is the fundamental limit of signatures: they detect **known patterns**, so commodity malware and un-adapted attacks get caught, while a motivated attacker who varies their bytes (or wraps them in TLS) sails past. That's not a Snort bug — it's *why* behavioural monitoring (Zeek) exists as a complement: you can change your bytes, but it's much harder to hide that a host is beaconing to a rare domain every 60 seconds. Run signatures for cheap coverage of the known; never mistake "no Snort alert" for "no attack."

## Summary

You should now be able to:

- Why is Snort fast and low-effort, and what can it fundamentally not catch?
- Read a Snort rule and name what `content:`, `flow:`, and `sid:` do.
- Show three ways a content signature for `/bin/sh` is evaded, and explain why that motivates behavioural detection.

---
> 🔼 Up: [[Network Detection & Monitoring Tools]]
