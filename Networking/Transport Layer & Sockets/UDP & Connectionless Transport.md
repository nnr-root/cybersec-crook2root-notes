---
title: "UDP & Connectionless Transport"
aliases: ["UDP", "Datagram", "Amplification Attack", "Reflection Attack"]
tags:
  - tree/networking
  - cyber/networking/transport
  - type/concept
  - difficulty/medium
Domain:
  - "[[Transport Layer & Sockets]]"
Color: "#42D4F4"
---

# 📨 UDP & Connectionless Transport

> [!abstract] Note of [[Transport Layer & Sockets]]
> UDP is TCP with everything removed: no handshake, no state, no ordering, no retransmission. That minimalism makes it the right choice for a large class of applications and makes it the engine of the largest denial-of-service attacks ever recorded. This note explains both consequences from the same eight-byte header.

## Parent Learning Order
Ports & Sockets -> TCP Connections & State -> TCP Reliability & Congestion Control -> UDP & Connectionless Transport -> QUIC & Modern Transport -> Transport Layer Threats & Controls

## Eight Bytes and No Promises

> *What does UDP give you that raw IP does not?*
>
> Hold your answer — the section below is the response.

**UDP (User Datagram Protocol)** provides exactly one service beyond raw IP: **demultiplexing to a port**, plus an optional checksum. Its entire header is eight bytes.

| Field | Size | Purpose |
| --- | --- | --- |
| Source port | 2 bytes | Where a reply should go (may be zero if none expected) |
| Destination port | 2 bytes | Which program receives this datagram |
| Length | 2 bytes | Header plus payload |
| Checksum | 2 bytes | Error detection; optional in IPv4, mandatory in IPv6 |

Compare with TCP's twenty-byte minimum header and its sequence numbers, acknowledgments, flags, and windows. Everything TCP uses to build reliability is absent, and its absence *is* the design:

| Property | TCP | UDP |
| --- | --- | --- |
| Connection setup | Three-way handshake | None — send immediately |
| Delivery guarantee | Retransmission until acknowledged | None |
| Ordering | Reassembled by sequence | Arrives in any order |
| Duplicate suppression | Yes | No |
| Flow / congestion control | Yes | **None** |
| Per-connection state | Both endpoints | None |
| Header overhead | 20+ bytes | 8 bytes |

A **datagram** is self-contained: it either arrives whole or does not arrive. There is no partial delivery and no relationship between one datagram and the next.

**Prerequisites:** TCP's handshake and what it guarantees.

> [!tip] The analogy, and where it breaks
> Dropping postcards in a mailbox: no handshake, no delivery guarantee, no record kept, and nothing arrives half-written. The analogy breaks at scale and at forgery — you cannot cheaply write a stranger's address as the sender on thousands of postcards and have institutions mail heavy parcels to them. UDP's unverifiable source is exactly what makes reflection and amplification possible.

## Why Anyone Would Choose This

UDP is not a lesser TCP; it is the correct choice when TCP's guarantees are actively harmful.

**When late data is worthless.** In live voice or video, a segment that arrives 300 ms late is useless — the moment it described has passed. TCP would stall the entire stream retransmitting it, adding latency to everything behind it. UDP lets the application skip the loss and continue, which is why real-time media overwhelmingly uses UDP with application-level concealment.

**When the exchange is a single round trip.** A DNS query and its reply fit in one datagram each. A three-way handshake to exchange two small messages triples the latency and the packet count for no benefit.

**When the application knows better.** Retransmission, ordering, and pacing can be implemented above UDP with semantics tuned to the application. This is exactly what QUIC does — and it is why "UDP is unreliable" is a statement about the protocol, not about what runs on it.

**When broadcast or multicast is needed.** TCP is inherently point-to-point because a connection has exactly two endpoints. One-to-many delivery requires a connectionless transport.

Common UDP services: DNS (53), DHCP (67/68), NTP (123), SNMP (161), syslog (514), and QUIC/HTTP-3 (443).

## The Scanning Problem

TCP scanning is straightforward because the state machine answers: SYN+ACK means open, RST means closed. UDP has no such reply.

```mermaid
flowchart TD
    P["UDP probe to a port"] --> R{"What comes back?"}
    R -->|"UDP reply"| O["open — a service responded"]
    R -->|"ICMP port unreachable"| C["closed — nothing listening"]
    R -->|"ICMP admin prohibited"| F["filtered — a policy device"]
    R -->|"Nothing at all"| A["open|filtered — genuinely ambiguous"]
```

The bottom branch is the difficulty. Silence can mean the port is open but the service only answers a correctly formatted request, or that a firewall dropped the probe. Both produce identical observations, so scanners report `open|filtered` — an honest statement of ambiguity.

Worse, closed-port detection depends on ICMP port-unreachable messages, which hosts commonly rate-limit. A scan across many ports therefore receives only a fraction of the "closed" replies it should, and the scanner must slow down to avoid mistaking rate limiting for openness.

```bash
sudo nmap -sU -p 53,123,161 10.10.20.10
```

Expected excerpt:

```text
PORT    STATE         SERVICE
53/udp  open          domain
123/udp open|filtered ntp
161/udp closed        snmp
```

Three different epistemic positions in one output. `open` came from an actual service reply. `closed` came from an ICMP port unreachable. `open|filtered` means no evidence either way was obtained — and reporting it as "closed" would be a fabrication. This is why UDP scans are slow and why service-specific probes, which elicit a real reply, are far more reliable than empty datagrams.

## Amplification: The Structural Vulnerability

UDP's lack of a handshake creates the most consequential security property in this note. Because there is no connection setup, **a server cannot verify that the source address in a request is genuine.** It receives a request and sends a reply to whatever source address the request claimed.

An attacker exploits this in three steps:

1. Send a small request to a public UDP service, spoofing the **victim's** address as the source.
2. The service sends its reply to the victim, who never asked.
3. Choose a service whose reply is much larger than the request.

```mermaid
sequenceDiagram
    participant A as Attacker 198.51.100.9
    participant S as ns1.meridian.test 203.0.113.53
    participant V as Victim 192.0.2.10
    A->>S: 64-byte query, source spoofed as 192.0.2.10
    Note over S: No handshake — cannot verify the source
    S->>V: 3,456-byte reply sent to 192.0.2.10
    Note over V: Receives unsolicited traffic it never asked for
    Note over A,V: Thousands of resolvers, one victim, traffic multiplied
```

Note who the reflector is in that diagram. It is not the attacker's infrastructure and it is not compromised — it is Meridian's own name server, correctly configured, answering a question it was asked. The abuse consists entirely of believing the return address.

The **amplification factor** is the ratio of reply size to request size, and the published figures are worth carrying because they explain why particular services keep appearing in incident reports:

| Service | Typical factor | Why the reply is large |
|:--|--:|:--|
| NetBIOS | 3.8× | small name records |
| SNMPv2 | 6.3× | a `GetBulk` walk returns many values |
| DNS | 28–54× | a signed or `ANY` response dwarfs the query |
| SSDP | 30.8× | device descriptions |
| chargen | 358.8× | the service exists to emit characters |
| NTP `monlist` | 556× | up to 600 recent clients, six per packet |
| memcached | 10,000–51,000× | arbitrary stored values, retrieved by key |

Do the arithmetic on the middle row, because the numbers are what make this a structural problem rather than a nuisance. A 64-byte query drawing a 3,456-byte answer is 54×. An attacker with a single gigabit of upstream — a rented server, not a botnet — directs 54 Gbps at the victim. The bottom row is worse by two orders of magnitude: memcached amplification meant an attacker needed roughly twenty *kilobits* per second to deliver a gigabit, which is why those incidents produced record-breaking figures from unremarkable origins.

Because the traffic genuinely originates from many legitimate servers, it is hard to filter by source and the true attacker is hidden — every packet the victim receives has an honest return address belonging to someone who did nothing wrong.

TCP is structurally immune to this: the handshake requires a reply to reach the claimed source before any data is sent, so a spoofed source never completes a connection.

The defenses operate at three levels:

- **Ingress filtering** at the source network prevents spoofed packets from ever leaving — the root fix, though it depends on other networks' hygiene.
- **Service hardening**: restrict or disable high-amplification commands, require the reply to be no larger than the request where the protocol allows, and do not expose these services publicly without need.
- **Rate limiting** per source address at the service, so a single spoofed victim cannot be targeted repeatedly through you.

The recurring theme is that operators of UDP services must protect *third parties*, not just themselves. An open, amplifying UDP service is a weapon pointed at strangers.

**The deliberate break:** a public UDP service looks like something that can be attacked — the exposure question is whether *your* server is reachable, patched and hardened.

The more consequential exposure runs the other way. With no handshake, the service cannot verify who asked, so it replies to whatever source address the request claimed. A hardened, fully patched, perfectly behaving UDP service is therefore still **a weapon aimed at a third party**: an attacker spoofs a victim's address, your server answers dutifully, and the victim absorbs a reply many times larger than the request that triggered it. The risk you carry is not only being a target but being an unwitting participant, and no amount of patching the service changes that — the property belongs to the transport.

**How you'd spot it:** look at the direction of the bytes. A UDP service whose outbound volume materially exceeds its inbound volume is being used as an amplifier, and that ratio is visible in flow data long before anyone complains — it looks like this, and the giveaway is not any single row but the column:

```text
SrcIP           DstIP           Proto SrcPt DstPt  Packets  Bytes
198.51.100.9    203.0.113.53    UDP   40001 53     14022    897408
203.0.113.53    192.0.2.10      UDP   53    40001  14022    48460032
```

Equal packet counts, fifty-four times the bytes, and — the part that no single-flow view would show — the two rows have *different peers*. Requests arrive from one address and replies leave to another, which is not a thing a real client-server exchange ever does. Ordinary DNS flow rows are symmetric in address and roughly symmetric in size; these are neither, and either anomaly alone would be enough. Then check the specific features that make the ratio large — recursion on a resolver, `monlist` on NTP, public community strings on SNMP, an exposed memcached — and fix the origin as well as the reflector: source-address validation at your own edge (BCP 38) stops your network emitting the spoofed requests that make everyone else's servers into weapons.

## Security Implications

**Statelessness cuts both ways for defenders.** There is no connection state to inspect, so a firewall cannot rely on "this is a reply to a request we made" the way it can with TCP. Stateful devices approximate it by tracking recent outbound datagrams and permitting matching returns for a short window — a heuristic, not a guarantee, and one an attacker can sometimes time around.

**UDP is attractive for tunnelling and exfiltration.** Because DNS and NTP must generally be permitted outbound, encoding data into them passes controls that examine only the five-tuple. Detection is behavioural — volume, entropy, timing regularity, unusual record or message sizes — rather than port-based.

**Spoofing is trivial and attribution is weak.** A UDP datagram's source address is unverified and there is no handshake to expose the lie. Logs attributing activity to a UDP source address should be treated as a claim, not a fact, unless the exchange included a challenge the sender had to answer.

**Absence of congestion control means UDP does not back off.** A UDP flood or a poorly written UDP application will happily saturate a link while TCP flows sharing it politely reduce their rate — so UDP traffic can starve TCP traffic. Application-level pacing is the responsibility of whoever writes the UDP application, and many do not.

All scanning and traffic generation described here must be confined to systems within an authorized scope. Amplification techniques in particular direct traffic at third parties and must never be exercised outside a fully isolated lab.

## Summary

You should now be able to:

- List what UDP omits compared to TCP and give two applications where those omissions are advantages rather than deficiencies.
- Interpret UDP scan results correctly, explain why `open|filtered` is honest rather than a tool failure, and why closed-port detection depends on ICMP and rate limiting distorts it.
- Explain precisely why the absence of a handshake enables reflection and amplification while TCP is structurally immune; justify ingress filtering, service hardening, and rate limiting as complementary defenses, and explain why UDP's lack of congestion control lets it starve well-behaved TCP flows.

---
> 🔼 Up: [[Transport Layer & Sockets]]
