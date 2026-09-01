---
title: "ARP & Neighbor Discovery"
aliases: ["ARP", "ARP Spoofing", "Neighbor Discovery", "NDP", "Gratuitous ARP"]
tags:
  - tree/networking
  - cyber/networking/layer2
  - type/technique
  - difficulty/medium
  - level/apprentice
Domain:
  - "[[Switching & the Link Layer]]"
Color: "#42D4F4"
---

# 🧭 ARP & Neighbor Discovery

> [!abstract] Note of [[Switching & the Link Layer]]
> Before a host can send a frame to a neighbour, it must translate that neighbour's IP address into a hardware address — and the protocol that does this trusts any answer it receives. This note explains the resolution mechanism, why its trust model makes on-path attacks trivial on a local segment, and how to detect and prevent them.

## Parent Learning Order
Ethernet & Frame Structure -> MAC Addressing & Switch Operation -> ARP & Neighbor Discovery -> VLANs & Trunking -> Spanning Tree & Loop Prevention -> Link Layer Security Controls

## The Missing Translation

> *You know the destination's IP address. Why can you not build the frame yet?*
>
> Hold your answer — the section below is the response.

A host that wants to send to `10.10.10.1` knows the destination *IP* address, but a frame needs a destination *hardware* address. Something must bridge Layer 3 to Layer 2. On IPv4 that something is **ARP (Address Resolution Protocol)**.

The exchange is two messages:

1. **ARP Request** — broadcast to the whole segment: "Who has `10.10.10.1`? Tell `10.10.10.14`." — that is `WS-014` asking for its gateway. Every host receives it because it is addressed to `ff:ff:ff:ff:ff:ff`.
2. **ARP Reply** — a unicast answer from the owner: "`10.10.10.1` is at `00:00:5e:00:53:01`."

The asker caches the answer in its **ARP table** so it need not ask again for every frame.

```mermaid
sequenceDiagram
    participant A as WS-014 (10.10.10.14)
    participant Seg as Segment (broadcast)
    participant G as Gateway (10.10.10.1)
    A->>Seg: ARP Request — who has 10.10.10.1?
    Note over Seg: Every host on the link receives it
    G-->>A: ARP Reply — it is at 00:00:5e:00:53:01
    Note over A: Cache 10.10.10.1 -> 00:00:5e:00:53:01
    A->>G: Now frames can be addressed correctly
```

```bash
ip neigh show
```

Expected excerpt:

```text
10.10.10.1 dev eth0 lladdr 00:00:5e:00:53:01 REACHABLE
10.10.10.30  dev eth0 lladdr 00:00:5e:00:53:1e STALE
```

`REACHABLE` means the mapping was confirmed recently; `STALE` means it is cached but unverified and will be revalidated on next use. The table is the host's belief about who its neighbours are — and belief is exactly what an attacker manipulates.

**Prerequisites:** the difference between an IP address and a MAC address, and what a broadcast is.

> [!tip] The analogy, and where it breaks
> Shouting across an open-plan office, 'who is Alice?' and writing down whoever answers. The analogy breaks in the detail that matters most: a real office would notice if a stranger answered to Alice's name, whereas ARP has no way to check. It also accepts answers to questions nobody asked, which is why a forged reply silently reroutes a victim's traffic while everything still appears to work.

## The Flaw: ARP Believes Anyone

ARP has no authentication. Three properties make it exploitable, and they are design characteristics rather than bugs:

- A host **accepts a reply it never requested**. Most implementations cache any ARP reply they see, whether or not they asked.
- A host **accepts an updated mapping** that overwrites an existing one, so a later reply wins.
- **Gratuitous ARP** — an unsolicited announcement of a mapping — is honoured, because it legitimately exists to update neighbours after a failover or address change.

Combine these and the attack writes itself. An attacker sends the victim a forged reply claiming the *gateway's* IP is at the *attacker's* MAC, and sends the gateway a forged reply claiming the *victim's* IP is at the *attacker's* MAC. Both caches are now poisoned, and both parties send their traffic to the attacker, who forwards it on to preserve connectivity. This is **ARP spoofing**, and it produces a full on-path position — the attacker reads and can modify every frame between victim and gateway.

```mermaid
flowchart LR
    V["Victim"] -->|"traffic for gateway"| X["Attacker (poisoned as gateway)"]
    X -->|"relayed"| G["Real gateway"]
    G -->|"traffic for victim"| X
    X -->|"relayed"| V
    X -.->|"reads & may alter"| X
```

Nothing appears broken to the victim — pages load, connections work — because the attacker relays. That silence is what makes it dangerous. The only visible symptom is in the ARP table: the gateway and some other host suddenly share one MAC address.

```bash
ip neigh show | sort -k5
```

Expected excerpt during an attack:

```text
10.10.10.1  dev eth0 lladdr 00:00:5e:00:53:de REACHABLE
10.10.10.30  dev eth0 lladdr 00:00:5e:00:53:de REACHABLE
```

Two different IP addresses resolving to the identical MAC (`00:00:5e:00:53:de`) is the signature. A legitimate configuration essentially never does this, so it is a high-confidence indicator.

## IPv6: Neighbor Discovery Inherits the Problem

IPv6 does not use ARP. It uses **NDP (Neighbor Discovery Protocol)**, carried inside ICMPv6, with **Neighbor Solicitation** and **Neighbor Advertisement** messages that play the roles of request and reply. NDP is more capable — it also handles router discovery and address autoconfiguration — but it inherited ARP's core weakness: the messages are unauthenticated by default, so **Neighbor Advertisement spoofing** is the direct analogue of ARP spoofing.

```bash
ip -6 neigh show
```

Expected excerpt:

```text
fe80::1 dev eth0 lladdr 00:00:5e:00:53:01 router REACHABLE
2001:db8:acad:10::30 dev eth0 lladdr 00:00:5e:00:53:1e STALE
```

The same detection logic applies: two IPv6 addresses resolving to one MAC is suspicious. IPv6 additionally exposes router advertisement spoofing, a related but distinct attack covered where addressing is discussed. The lesson is that "we use IPv6" does not escape the trust problem — it renames it.

## Detection and Prevention

**Detection** watches for the signatures above and for behavioural anomalies:

- Multiple IP addresses mapping to one MAC in the neighbour table.
- A flood of gratuitous ARP or unsolicited neighbour advertisements.
- The gateway's MAC changing unexpectedly.

A passive monitor can maintain a baseline of IP-to-MAC bindings and alarm on changes:

```bash
sudo arpwatch -i eth0
```

Expected excerpt (from its log):

```text
changed ethernet address for 10.10.10.1
   from 00:00:5e:00:53:01 to 00:00:5e:00:53:de
```

A "changed ethernet address" event for the gateway is the alert that matters most; gateways do not normally change hardware address.

**Prevention** is a link-layer control, because the attack is link-layer:

- **Dynamic ARP Inspection (DAI)** on switches validates every ARP reply against a trusted binding table — typically the one built by DHCP snooping — and drops replies that do not match. An attacker's forged mapping fails validation and never reaches the victim.
- **Static ARP entries** for critical mappings (a server's gateway) cannot be overwritten by a forged reply, but do not scale beyond a few high-value bindings.
- For IPv6, the equivalent switch feature inspects neighbour advertisements against the same trusted bindings.

DAI is the scalable answer, and it depends on the snooping binding table — which is why the link-layer controls in this branch reinforce each other rather than standing alone.

## Security Implications

ARP and NDP spoofing are the foundation of most local on-path attacks. Once an attacker sits between a victim and its gateway, everything downstream becomes possible: reading plaintext credentials, stripping transport security by tampering with the handshake, injecting content, redirecting name lookups, and harvesting authentication material. The position is the prize; the specific payload varies.

The scope of the attack is exactly one broadcast domain — it cannot cross a router, because ARP and NDP are link-local. This is why segmentation limits the blast radius: an attacker on the guest VLAN cannot poison the finance VLAN's gateway. It is also why a flat network is so dangerous, since a single foothold can position itself between any two hosts in the entire estate.

Transport-layer security is the backstop that survives an on-path attacker. Even with a perfect on-path position, an attacker cannot read a properly validated TLS session — they can only see metadata and attempt a downgrade that certificate validation and HSTS defeat. This is precisely why "the local network is hostile" is the correct assumption and why end-to-end encryption is not optional.

All poisoning and interception described here must be performed only on an isolated lab you own. ARP spoofing intercepts other parties' traffic and is unlawful on networks you are not authorized to test.

## Summary

You should now be able to:

- Explain why ARP exists, describe the request/reply exchange, and state what an ARP table stores.
- Read a neighbour table, recognize the two-IPs-one-MAC signature of poisoning, and use a monitor to detect a gateway MAC change; explain why connectivity keeps working during the attack.
- Explain why ARP's acceptance of unsolicited and overwriting replies makes on-path attacks trivial; describe how Dynamic ARP Inspection uses the snooping binding table to validate replies, why the attack is confined to one broadcast domain, and why transport-layer security is the backstop that survives an on-path adversary.

---
> 🔼 Up: [[Switching & the Link Layer]]
