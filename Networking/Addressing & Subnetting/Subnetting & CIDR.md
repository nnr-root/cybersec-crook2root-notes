---
title: "Subnetting & CIDR"
aliases: ["Subnetting", "CIDR", "Subnet Mask", "Prefix Length", "Magic Number"]
tags:
  - tree/networking
  - cyber/networking/addressing
  - type/technique
  - difficulty/easy
Domain:
  - "[[Addressing & Subnetting]]"
thread-exempt:
  - "10.0.0.0: the whole RFC 1918 10/8 block — the 16-million-address figure depends on it being /8"
Color: "#42D4F4"
---

# ✂️ Subnetting & CIDR

> [!abstract] Note of [[Addressing & Subnetting]]
> Subnetting is binary arithmetic dressed up as a networking topic. This note teaches the mechanism rather than a lookup table, so that any prefix length can be computed from first principles in a few seconds, and then shows why the resulting boundaries are the primary containment control in a network.

## Parent Learning Order
IPv4 Addressing -> Subnetting & CIDR -> VLSM & Route Summarization -> IPv6 Addressing -> Address Assignment & DHCP -> NAT & Address Translation

## The Mask Is a Boundary Marker

> *Which holds more hosts — a `/16` or a `/24`?*
>
> Hold your answer — the section below is the response.

A **subnet mask** is 32 bits in which every network bit is 1 and every host bit is 0, and the ones are always contiguous and leading. `255.255.255.0` in binary is twenty-four 1s followed by eight 0s — which is why it is written `/24` in **CIDR (Classless Inter-Domain Routing)** notation. The number after the slash is simply the count of network bits.

```text
Address  10.10.10.14     00001010.00001010.00001010.00001110
Mask     255.255.255.0   11111111.11111111.11111111.00000000
                         └────── network ─────────┘└─ host ─┘
```

Two operations follow mechanically:

- **Network address**: keep the network bits, set every host bit to 0 → `10.10.10.0`
- **Broadcast address**: keep the network bits, set every host bit to 1 → `10.10.10.255`

Everything between those two, exclusive, is usable. Hence the formula:

```text
Total addresses = 2^(host bits)
Usable hosts    = 2^(host bits) - 2
```

The subtraction of two removes the network address (all host bits zero, which names the subnet itself) and the broadcast address (all host bits one, which addresses every host on it). Neither can be assigned to an interface.

> [!warning] The exception that trips people
> A `/31` has 2 addresses and would compute to 0 usable hosts. RFC 3021 permits `/31` on point-to-point links precisely because a link with exactly two endpoints needs no broadcast address. A `/32` is a single host route. Both are common in real configurations, so a formula applied without understanding produces nonsense on exactly the links you will meet most often in routing tables.

**Prerequisites:** IPv4 addresses in binary, and what a mask does.

> [!tip] The analogy, and where it breaks
> A phone number splits into area code and local number, and lengthening the area code carves one big region into many small ones. A subnet mask is that dividing line, except you may place it after *any* bit rather than at a fixed digit. The analogy breaks because area codes are assigned by an authority and never overlap, whereas overlapping prefixes are legal in routing and resolved by longest-prefix match — a rule with no telephone equivalent.

**The deliberate break:** `/24`, `/16`, `/8` read like sizes, and a bigger number sounds like a bigger network. It is exactly backwards.

The number counts **network bits**, so every bit you add to the prefix halves the host space. A `/24` holds 254 usable addresses; a `/16` holds 65,534. If that inversion is not automatic yet, it is the single most reliable source of subnetting mistakes — and it is why a firewall rule written for `/16` when `/24` was meant silently authorises 256 times as many hosts.

**How you'd spot it:** read a prefix as "how much is fixed", never as "how big" — `10.10.0.0/16` fixes `10.10` and leaves two octets free. The place this costs money is a rule review, where the inversion is invisible in the notation: `/8` and `/24` differ by two characters and by sixteen million addresses. So expand every prefix in a rule set into its first and last address before approving it, and check that number against the count of hosts the rule was written for. A prefix whose range is an order of magnitude larger than its stated purpose is either a mistake or an undocumented decision, and both are worth a sentence in the review.

## The Reference Table You Should Be Able to Derive

| CIDR | Mask | Total | Usable | Typical use |
| --- | --- | --- | --- | --- |
| `/16` | `255.255.0.0` | 65,536 | 65,534 | Oversized; a segmentation failure in most designs |
| `/22` | `255.255.252.0` | 1,024 | 1,022 | Large campus VLAN |
| `/24` | `255.255.255.0` | 256 | 254 | Standard segment |
| `/25` | `255.255.255.128` | 128 | 126 | Split a /24 in half |
| `/26` | `255.255.255.192` | 64 | 62 | Departmental segment |
| `/27` | `255.255.255.224` | 32 | 30 | Small server group |
| `/28` | `255.255.255.240` | 16 | 14 | Appliance or DMZ block |
| `/30` | `255.255.255.252` | 4 | 2 | Classic point-to-point link |
| `/31` | `255.255.255.254` | 2 | 2 | Modern point-to-point (RFC 3021) |
| `/32` | `255.255.255.255` | 1 | 1 | Single host route |

Do not memorize this. Derive it: host bits are `32 - prefix`, total is `2^host bits`, and the mask's final non-zero octet is `256 - block size`.

## The Magic Number Method

The fastest manual technique works entirely in the octet where the mask changes from 1s to 0s — the **interesting octet**.

**Block size = 256 − (mask value in the interesting octet)**

Subnets then start at multiples of the block size within that octet.

### Worked example: split `10.10.30.0/24` into `/26` blocks

1. Prefix `/26` → mask `255.255.255.192`. The interesting octet is the fourth, value 192.
2. Block size = 256 − 192 = **64**.
3. Subnets start at multiples of 64: 0, 64, 128, 192.

| Subnet | Network | Usable range | Broadcast |
| --- | --- | --- | --- |
| 1 | `10.10.30.0/26` | `.1` – `.62` | `.63` |
| 2 | `10.10.30.64/26` | `.65` – `.126` | `.127` |
| 3 | `10.10.30.128/26` | `.129` – `.190` | `.191` |
| 4 | `10.10.30.192/26` | `.193` – `.254` | `.255` |

### Worked example: which subnet contains `10.10.203.77/20`?

1. `/20` → mask `255.255.240.0`. Interesting octet is the **third**, value 240.
2. Block size = 256 − 240 = **16**.
3. Third-octet boundaries: 0, 16, 32, … 192, **208**. Since 203 falls between 192 and 208, the network starts at 192.
4. Network `10.10.192.0`, broadcast `10.10.207.255`, usable `10.10.192.1` – `10.10.207.254`.

Note that a `/20` spans multiple third-octet values. The instinct that "the third octet identifies the network" is a classful reflex and it is wrong here — which is exactly why the arithmetic must be done rather than pattern-matched.

Verify with a tool, but only after computing it yourself:

```bash
ipcalc 10.10.203.77/20
```

Expected excerpt:

```text
Address:   10.10.203.77         00001010.00001010.1100 1011.01001101
Netmask:   255.255.240.0 = 20   11111111.11111111.1111 0000.00000000
=>
Network:   10.10.192.0/20       00001010.00001010.1100 0000.00000000
HostMin:   10.10.192.1
HostMax:   10.10.207.254
Broadcast: 10.10.207.255
Hosts/Net: 4094
```

The space in the binary column marks the prefix boundary. Everything left of it is fixed for the whole subnet; everything right of it varies per host. Reading that split is the entire skill.

```mermaid
flowchart TB
    A["10.10.30.0/24 — 254 usable"]
    A --> B["10.10.30.0/26 — .1-.62"]
    A --> C["10.10.30.64/26 — .65-.126"]
    A --> D["10.10.30.128/26 — .129-.190"]
    A --> E["10.10.30.192/26 — .193-.254"]
    B --> F["Each /26 is its own broadcast domain"]
    C --> F
    D --> F
    E --> F
    F --> G["Traffic between them requires a routing decision — the enforcement point"]
```

The diagram's final node is the point of the whole topic. Splitting a range does not merely organize addresses; it creates boundaries that traffic must cross through a device where policy can be applied.

## Operational Use

Compute the block, then act on exactly that block:

```bash
nmap -sn 10.10.192.0/20
```

Expected excerpt:

```text
Nmap scan report for 10.10.192.1
Host is up (0.00095s latency).
Nmap scan report for 10.10.194.20
Host is up (0.0012s latency).
Nmap done: 4096 IP addresses (2 hosts up) scanned in 41.02 seconds
```

The value of prefix fluency here is concrete: one correctly computed sweep replaces guesswork, and the scan covers exactly the authorized scope — no more, no less. Scanning `10.10.203.0/24` because "the third octet is 203" would have missed most of the actual subnet and, worse, could have touched addresses outside the agreed boundary.

### Common errors and how they present

**Off-by-one on the boundary.** Assigning `10.10.30.64` to a host inside the second `/26` fails, because that address is the network identifier. The symptom is an interface that configures but cannot communicate.

**Overlapping subnets.** Defining both `10.10.0.0/16` and `10.10.5.0/24` on different interfaces creates an ambiguity resolved by longest-prefix match — traffic to `10.10.5.x` uses the `/24`, everything else the `/16`. This is legal and sometimes intentional, but when unintentional it produces traffic that vanishes down the wrong interface.

**Mask mismatch between neighbours.** Two hosts on one wire with different masks may each consider the other local or remote inconsistently, producing connectivity that works in one direction only. Always verify the mask on both ends, not just the addresses.

## Security Implications

Subnet size is the single most consequential containment decision in a network, and it is made long before any incident.

Every host inside a subnet shares a broadcast domain and is therefore exposed to the entire family of link-layer attacks from any other host in it — address resolution poisoning, rogue lease servers, name-resolution spoofing, discovery-protocol abuse. None of these cross a routed boundary. Consequently, the number of hosts in a subnet is a direct measure of how far one compromised endpoint reaches before it must pass a control.

A `/16` for a user population that needs 400 addresses is not merely wasteful; it places tens of thousands of potential neighbours in a single uncontrolled space. Right-sizing to a `/23` and routing between segments converts lateral movement from a link-layer certainty into a routed event that a firewall can deny and a sensor can observe.

Prefix precision also matters for the controls themselves. A firewall rule written for `10.0.0.0/8` when the intent was `10.10.5.0/24` silently authorizes 16 million addresses. Rule sets should be reviewed by expanding every prefix into its actual range, because the difference between intent and effect is invisible in the notation.

Finally, subnet boundaries shape evidence. Traffic that stays inside a segment may never pass a sensor, so intra-subnet activity is unobserved unless monitoring is deliberately placed there. Where you draw the lines determines what you can later prove.

All scanning must target only ranges inside an authorized scope. Because a mis-computed prefix can silently extend a sweep beyond an agreed boundary, verifying the computed range before running any active tool is part of staying in scope, not merely good practice.

## Summary

You should now be able to:

- Explain what a mask does in binary, compute network, broadcast, and usable range for any `/24` through `/30`, and state why two addresses are subtracted.
- Use the magic-number method to place any address in its subnet without a table; verify with `ipcalc`, scan exactly the computed block, and diagnose off-by-one, overlap, and mask-mismatch errors from their symptoms.
- Explain why `/31` and `/32` break the usable-host formula and why that is correct; argue subnet sizing as a containment control by relating broadcast-domain size to lateral movement; and audit a rule set by expanding prefixes to reveal the gap between intended and authorized scope.

---
> 🔼 Up: [[Addressing & Subnetting]]
