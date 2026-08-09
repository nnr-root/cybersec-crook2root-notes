---
title: "Intrusion Detection & Network Monitoring"
aliases: ["IDS", "IPS", "Network Detection", "Signature Detection", "Anomaly Detection", "NDR"]
tags:
  - tree/networking
  - cyber/networking/secarch
  - type/concept
  - level/operator
Domain:
  - "[[Network Security Architecture]]"
Color: "#42D4F4"
---

# 👁️ Intrusion Detection & Network Monitoring

> [!abstract] Note of [[Network Security Architecture]]
> Firewalls decide what may pass; detection systems watch what actually did. This note covers the two ways to recognize an attack — matching known-bad patterns and spotting deviation from normal — where sensors must sit to see anything, and why pervasive encryption forced network detection to shift from reading content to reading behaviour and metadata.

## Parent Learning Order
Firewall Architecture & Policy -> Network Segmentation & Zero Trust -> VPNs & Encrypted Tunnels -> Intrusion Detection & Network Monitoring -> Egress Control & Web Proxies -> Network Access Control

## Start at Zero: Detect Versus Prevent

A firewall enforces policy at a boundary. A **detection system** watches traffic to recognize malicious activity that policy alone did not stop — because the traffic was permitted, or because the attack hid inside allowed protocols.

Two roles exist, and the difference is consequential:

- An **IDS (Intrusion Detection System)** observes and alerts. It sits out of the traffic path (or on a copy of it) and raises an alarm when it sees something suspicious. It cannot block; it can only tell you.
- An **IPS (Intrusion Prevention System)** sits inline in the traffic path and can drop malicious traffic in real time. It prevents, not just detects.

The trade-off is direct. An IPS stops attacks but, being inline, is a potential bottleneck and a single point of failure — and a false positive means it blocks legitimate traffic, causing an outage. An IDS never breaks legitimate traffic but only tells you after the fact. Many deployments run detection broadly and enable prevention selectively for high-confidence signatures, accepting alerts elsewhere.

**Prerequisites:** firewalls, packet capture, and what encryption hides.

> [!tip] The analogy, and where it breaks
> A security guard watching camera feeds: one who recognises known faces from a wanted list, and one who notices that someone is behaving oddly for this building at this hour. The analogy breaks with encryption — it is as if everyone now wears a mask, so the wanted list becomes useless and only the behaviour, timing, and movement patterns remain readable. That is why detection shifted to metadata.

## Two Detection Philosophies

How does a system decide traffic is malicious? Two fundamentally different approaches, with complementary strengths.

**Signature-based detection** matches traffic against a database of known-bad patterns — a specific byte sequence, a known exploit, a malware communication pattern. It is precise and produces few false positives *for known threats*, and its alerts are specific and actionable ("this is exploit X"). Its fatal limitation: it can only catch what someone has already written a signature for. A novel attack, or a known one altered enough to miss the pattern, sails through. Signatures are necessary and permanently one step behind.

**Anomaly-based detection** builds a model of normal behaviour and flags deviation. It can catch *novel* attacks that no signature describes — a workstation suddenly transferring gigabytes at 3 a.m., a server connecting to a country it never talks to, a login from an impossible location. Its weakness is the mirror image of signatures': it produces false positives, because "unusual" is not the same as "malicious," and legitimate rare events trigger it. It also requires a good baseline, and if the baseline is built while an attacker is already present, their activity becomes "normal."

```mermaid
flowchart TB
    T["Observed traffic"] --> SIG{"Matches a known-bad signature?"}
    T --> ANO{"Deviates from the learned baseline?"}
    SIG -->|"Yes"| A1["Alert: specific known threat (precise, only catches known)"]
    ANO -->|"Yes"| A2["Alert: anomaly (catches novel, more false positives)"]
    A1 --> C["Correlation & triage"]
    A2 --> C
```

The two are complementary, not competing: signatures catch the known with precision, anomaly detection catches the unknown with noise, and a mature program runs both and correlates their output.

## Sensor Placement: You Only See What Reaches the Sensor

The most important operational fact about network detection is that **a sensor sees only the traffic that passes it.** Detection is blind to everything else, which makes placement a first-order design decision.

- A sensor at the **perimeter** sees traffic crossing the boundary — inbound attacks, outbound exfiltration — but nothing between internal hosts.
- A sensor sees **east-west** (internal, host-to-host) traffic only if that traffic is routed past it or mirrored to it. In a flat segment, lateral movement never crosses the perimeter sensor and is invisible.

This is why sensor placement must follow the topology and the segmentation, not the org chart. An attacker moving laterally within a segment that has no internal sensor is undetected by the network entirely. Comprehensive coverage means placing sensors — or collecting flow data — at the boundaries where you need visibility, and knowing precisely which segments are covered and which are blind. Mapping your own blind spots before an attacker finds them is itself a control.

Traffic reaches a sensor by a **SPAN/mirror port** (the switch copies traffic to the sensor), a **network tap** (a passive hardware device on the link), or **flow export** (the device sends metadata rather than full packets).

## The Encryption Problem

Signature detection historically read packet contents. Pervasive TLS and QUIC broke that: **the payload is encrypted, so content-matching sensors see ciphertext.** A signature for a malicious HTTP request cannot match when the HTTP is inside TLS. This is the defining challenge for modern network detection, and there are three responses, each with a cost.

**Inspect by decrypting.** Terminate TLS at a proxy, inspect the plaintext, re-encrypt. This restores content visibility but concentrates all plaintext at one point, breaks certificate pinning, and is the deliberate reduction of TLS's guarantee discussed in the web branch. It scales poorly and raises privacy and trust concerns.

**Detect by metadata and behaviour.** Even encrypted traffic reveals its shape: who connects to whom, when, how much, how often, with what timing, to what destination, with what certificate characteristics and TLS fingerprint. Beaconing to a command-and-control server has a distinctive rhythm even when its content is opaque; exfiltration has a distinctive volume and direction. This is why flow data, from the management-protocols material, became central — it is the visibility encryption does not remove. **Network Detection and Response (NDR)** is largely built on this: behavioural analysis of metadata rather than content inspection.

**Move detection to the endpoints.** Where the traffic terminates, it is plaintext. Endpoint detection sees what network sensors cannot, which is why detection strategy has shifted partly off the network and onto the hosts.

The honest state: content-based network detection is in decline as encryption becomes universal, and the future of network detection is behavioural and metadata-driven, complemented by endpoint visibility.

## Security Implications

**Detection assumes prevention will fail.** The entire premise is that some attacks get past the firewall, so you watch for them. This aligns with assume-breach: detection is how you find the attacker who is already inside, and its value is measured in how fast you detect and how much you can then contain.

**Alerts without triage are noise.** A detection system generating thousands of unreviewed alerts provides no security — it provides a false sense of it. The scarce resource is human attention, so tuning to reduce false positives, correlating related alerts into incidents, and prioritizing by confidence and impact are what turn detection into response. A quieter, well-tuned system beats a louder, ignored one.

**Attackers target the blind spots and the sensors.** Knowing that detection sees only what reaches it, attackers operate in unmonitored segments, use encryption to defeat content inspection, and move slowly to stay under anomaly thresholds. They also attack the detection infrastructure itself — flooding it with alerts to bury a real one, or disabling logging. The monitoring plane, per the earlier argument, must be protected accordingly.

**Evasion mirrors the lower-layer ambiguities.** Just as fragment reassembly and HTTP parsing differences enable evasion, an IDS that reassembles or normalizes traffic differently from the destination host can be fed traffic it reads as benign and the target reads as malicious. Sensors must normalize traffic the way the endpoint will, or the gap becomes an evasion.

**Time and correlation underpin everything.** Detection output is only useful if events across sensors can be ordered and correlated, which requires the synchronized time from the services branch and a central collection point. An alert without reliable time and context is hard to act on.

All monitoring described here must be deployed on networks within an authorized scope. Capturing traffic exposes its contents and metadata, and monitoring networks you do not own is unauthorized.

## Authorized Lab: See, Miss, and Tune

Use a lab with a sensor (an IDS such as a signature engine on a mirror port), a target, and an attacker, plus internal segments.

1. **Signature detection.** Run a known attack pattern against the target and confirm the IDS alerts with a specific signature. Note how precise and actionable the alert is.
2. **Signature evasion.** Alter the attack enough to miss the signature (encoding, fragmentation, or a slight variation) and confirm it now passes undetected — demonstrating the known-only limitation.
3. **Anomaly detection.** Establish a baseline of normal traffic, then generate anomalous behaviour (a large off-hours transfer, a connection to an unusual destination) and confirm the anomaly detector flags it while producing some false positives on legitimate rare events.
4. **Prove the placement blind spot.** Place the sensor at the perimeter, then conduct lateral movement between two internal hosts on a segment the sensor does not see, and confirm it is invisible. Add an internal sensor or mirror and confirm the movement now appears.
5. **Encryption challenge.** Send a malicious payload in cleartext (detected by signature) and then inside TLS (not detected by content), demonstrating why content inspection fails on encrypted traffic. Then detect the same encrypted session by its metadata — destination, volume, timing — showing the behavioural approach.
6. **IPS mode and its risk.** Switch a high-confidence signature to inline blocking and confirm the attack is dropped; then craft a false positive and confirm legitimate traffic is blocked — demonstrating the inline trade-off.
7. **Cleanup.** Restore the sensor to detection mode and remove test traffic and rules.

Expected interpretation:

```text
Signature       -> precise alert for a known attack; nothing for a novel one
Evasion         -> a slightly altered attack misses the signature entirely
Anomaly         -> catches the novel behaviour, at the cost of false positives
Placement       -> lateral movement invisible without an internal sensor
Encryption      -> content detection fails on TLS; metadata detection still works
IPS inline      -> blocks the attack, but a false positive blocks legitimate traffic
```

## Crook → Operator → Root Checkpoint

- **Crook:** Explain the difference between an IDS and an IPS and between signature and anomaly detection, including what each detection method catches and misses.
- **Operator:** Explain why a sensor sees only traffic that reaches it and how placement determines coverage; demonstrate signature evasion and the false-positive cost of anomaly detection and inline blocking.
- **Root:** Explain why pervasive encryption pushed network detection from content to metadata and behaviour, and what each response (decryption, NDR, endpoint) costs; describe how attackers exploit blind spots, evasion via parsing differences, and alert flooding, and why triage and correlation are what make detection actionable.

---
> 🔼 Up: [[Network Security Architecture]]
