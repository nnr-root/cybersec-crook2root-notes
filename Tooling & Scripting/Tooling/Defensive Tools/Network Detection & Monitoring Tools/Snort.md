---
title: "Snort"
aliases: ["snort"]
tags: [tree/tooling, cyber/tooling/defensive/snort, type/tool, difficulty/medium]
Domain: "[[Network Detection & Monitoring Tools]]"
Color: "#708090"
verified: 2026-09-05
---

# Snort

> [!abstract] Note of [[Network Detection & Monitoring Tools]]
> Snort is the original signature-based network IDS — the tool that defined what a detection rule looks like. It inspects traffic against a rule set and alerts (or, inline, blocks) on a known-bad pattern. Its rule syntax became the industry lingua franca, which makes Snort the best place to learn *how signatures work* and where they stop working.

> [!warning] Detection needs tuning
> Out-of-the-box rule sets produce noise. An untuned Snort drowns analysts in false positives; a well-tuned one is a precise sensor. Tuning is not optional configuration, it is the deployment.

## Parent Learning Order
Suricata -> Snort -> Zeek

**Prerequisites:** TCP/IP headers, ports and flow direction, and enough HTTP to know which bytes are a header and which are a body.

## Matching traffic against known-bad patterns

> *A Snort rule describes one threat. What has to be true before it can ever fire?*
>
> Hold your answer — the section below is the response.

Snort is the archetype of the left-hand model: match traffic against a library of known-bad patterns.

Each **rule** describes one threat — "if you see *this* pattern going to *that* port, alert." It is fast and low-effort because the analysis is pre-encoded by whoever wrote the rule; the cost is that Snort can only catch what someone already wrote a rule for. That single property — powerful against the known, blind to the novel — is the whole nature of signature detection, and Snort is where you internalise it.

> [!tip] The analogy, and where it breaks
> A signature engine is a bouncer with a photograph of every banned patron. Fast, cheap, and exactly as good as the photographs. The analogy breaks on *what the bouncer is looking at*: this one cannot see faces, only the pixel values in a specific rectangle. Change the lighting — re-encode the same bytes — and the photograph no longer matches a person who is unmistakably the same person.

## Reading a rule, and the buffer the match happens in

A Snort rule is *action, protocol, src -> dst, (options)*:

```text
alert tcp any any -> $HOME_NET 445 (msg:"SMB exploit attempt";
      flow:to_server; content:"|FF|SMB"; sid:1000001; rev:1;)
```

```shell-session
analyst@sensor:~$ snort -c /etc/snort/snort.conf -r meridian.pcap -A console -q
03/14-12:00:00.000000  [**] [1:1000001:1] DNS lookup of C2 domain [**]
  {UDP} 10.10.10.14:51000 -> 10.10.20.10:53
```

`content:` is the byte pattern; `flow:` scopes direction and requires an established session; `sid:` uniquely identifies the rule and `rev:` its version; `msg:` is the alert text. `-A console` prints alerts, production logs unified2 into a SIEM, and `$HOME_NET` is the variable that makes a rule set portable — set it wrong and every rule that references it is quietly scoped to nothing.

Snort does not evaluate rules one at a time. At startup it picks one `content:` from each rule as the **fast pattern** — by default the longest, since longest means rarest — and compiles every fast pattern in the rule set into a single Aho–Corasick automaton, the same construction [[YARA]] uses for its atoms. Traffic is run through that automaton once; only rules whose fast pattern hit are then fully evaluated. This is why thousands of rules cost little more than a handful, and why a rule whose longest content is short and common is a performance defect — it hits constantly and drags the full evaluator in behind it. The `fast_pattern` keyword lets you override the engine's choice when you know which of your strings is rarest.

The second half of a `content:` match is *which bytes it is allowed to match against*. Content modifiers scope the match to a normalised buffer — `http_uri`, `http_header`, `http_client_body`, `pkt_data`, `file_data` — and picking the wrong one is a silent failure, not an error. Two rules for the same string, run against the same captured request:

```shell-session
# rule 1000002: content:"curl/"; http_client_body;   -> no alert
# rule 1000003: content:"curl/";                     -> ALERT
03/14-12:06:40.000000  [**] [1:1000003:1] Non-browser user agent (raw content) [**]
  {TCP} 10.10.10.14:52000 -> 203.0.113.20:80
```

The user agent is a *header*. Scoped to the request body, the identical string never matches, and the rule reports nothing at all — no warning, no error, just a detection you believe you have and do not. Buffers are also the fix for the next section: `http_uri` matches against the URI *after* Snort's `http_inspect` preprocessor has URL-decoded and normalised it, which is what closes the most common encoding evasion.

## How literal matching gets encoded around

A signature matches *exactly what it describes* — and attackers exploit that literalness. Three requests, sent to the same host, all carrying the same instruction:

```shell-session
analyst@sensor:~$ tshark -r evade.pcap -T fields -e http.request.uri
/cgi?cmd=/bin/sh
/cgi?cmd=%2fbin%2fsh
/cgi?cmd=/bin/${x}sh
analyst@sensor:~$ snort -c snort.conf -r evade.pcap -A console -q   # content:"/bin/sh"
03/14-12:00:00.000000  [**] [1:2000001:1] literal /bin/sh [**]
  {TCP} 10.10.10.14:53000 -> 203.0.113.20:80
```

**The deliberate break:** three requests on the wire, **one alert**. A raw content rule for `/bin/sh` catches the naive payload and is defeated by URL-encoding and by a shell variable that produces the *same effect* with *different bytes* — and it is blind entirely once the traffic is inside TLS, where Snort sees only ciphertext. This is the fundamental limit of signatures: they detect **known byte patterns**, so commodity malware and un-adapted attacks get caught while a motivated attacker who varies their encoding sails past. That is not a Snort bug, it is *why* behavioural monitoring exists as a complement — you can change your bytes, but it is much harder to hide that a host is contacting the same destination every sixty seconds. Normalised buffers (`http_uri`) recover the encoded case, which is the real lesson: the rule is only as good as the buffer you matched in, and no buffer recovers the encrypted one.

**How you'd spot it:** look at what the rule is pinned to. A literal string match is defeated by any encoding producing the same effect, so the test is to replay that effect with different bytes and see whether the alert still fires — exactly the three-request experiment above, which any rule you write deserves before it ships. Across a fleet, the systemic tell is an alert volume that quietly collapses as TLS adoption rises: the traffic did not get safer, it got opaque.

## Security Implications

An IDS is a target as well as a sensor. Snort must parse hostile input by definition, and its preprocessors — the code that reassembles streams and normalises HTTP — are the deepest and most attacked part of it; historic Snort and Suricata CVEs are overwhelmingly in decoders and preprocessors rather than in the rule engine. A sensor runs with high privilege on a span port with visibility into everything, which makes compromising it the single best position on the network. Run it unprivileged after the capture socket is opened, keep it patched, and keep its management interface off the network it is watching.

The rule set is also intelligence. A `sid` and its `msg` describe precisely what you detect, so an attacker who obtains your local rules learns exactly which of their techniques are visible and which are not — and, more usefully to them, can generate traffic that trips a noisy rule deliberately to bury the real activity in alerts. That is the other half of tuning: an alert stream nobody reads is functionally the same as no sensor, and a **stealth interface** with no IP address is what keeps the sensor from being a routable target in the first place.

Finally, the sensor's blind spots are structural and worth writing down. Snort sees what its tap sees: asymmetric routing that delivers only one direction of a flow breaks stream reassembly, an over-subscribed span port drops packets silently, and any traffic that never crosses the monitored link — host to host inside a virtual switch, or anything inside a VPN — is not merely undetected but invisible. "No alerts" is a statement about the sensor, never about the network.

## Summary

You should now be able to:

- Explain why Snort is fast and low-effort, and what it fundamentally cannot catch.
- Read a Snort rule, say what `content:`, `flow:`, `sid:` and a content modifier do, and explain why the wrong buffer is a silent non-detection.
- Explain the fast-pattern automaton and why rule count is cheap, demonstrate three ways a content signature for `/bin/sh` is evaded, and name the sensor's structural blind spots.

---
> 🔼 Up: [[Network Detection & Monitoring Tools]]
