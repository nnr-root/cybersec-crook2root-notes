---
title: "IPv6 Addressing"
aliases: ["IPv6", "SLAAC", "Link-Local", "Dual Stack", "Router Advertisement"]
tags:
  - tree/networking
  - cyber/networking/addressing
  - type/concept
  - difficulty/medium
Domain:
  - "[[Addressing & Subnetting]]"
Color: "#42D4F4"
---

# 🌍 IPv6 Addressing

> [!abstract] Note of [[Addressing & Subnetting]]
> IPv6 is not "IPv4 with more digits" — it changes how addresses are assigned, how neighbours are discovered, and how many addresses one interface holds at once. This note builds the address model from its notation upward and then addresses the finding that appears in assessment after assessment: an IPv4-only review missing a fully reachable IPv6 path.

## Parent Learning Order
IPv4 Addressing -> Subnetting & CIDR -> VLSM & Route Summarization -> IPv6 Addressing -> Address Assignment & DHCP -> NAT & Address Translation

## 128 Bits and Its Notation

> *Why is `2001:db8::1::5` not a valid address?*
>
> Hold your answer — the section below is the response.

An **IPv6 address** is 128 bits, written as eight groups of four hexadecimal digits separated by colons. Each group represents 16 bits.

```text
2001:0db8:0000:0000:0000:ff00:0042:8329
```

Two compression rules make this readable, and both must be applied to write a canonical address:

1. **Drop leading zeros** in any group: `0db8` → `db8`, `0042` → `42`.
2. **Replace one run of consecutive all-zero groups with `::`** — once per address only, because a second would make the expansion ambiguous.

```text
2001:db8::ff00:42:8329
```

The prefix length works exactly as in CIDR: `2001:db8::/32` fixes the first 32 bits. The arithmetic is identical to IPv4's; only the width changed.

Subnetting is where IPv6 diverges culturally rather than mathematically. The convention is that a **/64 is the standard subnet size**, always. The lower 64 bits are the interface identifier and are not subnetted further, because address autoconfiguration depends on having 64 host bits available. A site typically receives a `/48`, giving 65,536 possible `/64` subnets — so IPv6 subnetting is about organizing a vast space, not conserving a scarce one. Attempting to save addresses with a `/120` breaks autoconfiguration and marks the design as an IPv4 habit misapplied.

**Prerequisites:** IPv4 addressing, subnet masks, and how DHCP assigns an address.

> [!tip] The analogy, and where it breaks
> Moving from a country's phone system to a global one so large that nobody needs to reuse numbers, and every phone auto-assigns itself a valid number on plugging in. The analogy breaks in two places: a phone has one number, whereas an IPv6 interface deliberately holds several addresses at once with different scopes and lifetimes; and no phone system lets any passer-by announce 'I am the exchange' the way an unauthenticated Router Advertisement can.

## Address Types, and Why an Interface Has Several

The most important structural difference: an IPv6 interface normally holds **multiple addresses simultaneously**, each with a different scope and purpose.

| Prefix | Type | Scope | Purpose |
| --- | --- | --- | --- |
| `::1/128` | Loopback | Host | Equivalent of `127.0.0.1` |
| `fe80::/10` | Link-local | One link | **Always present**; used for neighbour discovery and routing |
| `fc00::/7` | Unique local | Site | Roughly analogous to RFC 1918 private space |
| `2000::/3` | Global unicast | Internet | Publicly routable |
| `ff00::/8` | Multicast | Varies | Replaces broadcast entirely |
| `::/0` | Default route | — | All destinations |

Three consequences follow.

**There is no broadcast.** IPv6 uses multicast groups instead — `ff02::1` reaches all nodes on the link, `ff02::2` all routers. This is more efficient, because a host not subscribed to a group ignores the frame at the network card. It also means link-layer discovery attacks target multicast rather than broadcast, but they remain equally local.

**Link-local always exists.** Every IPv6-capable interface configures an `fe80::` address automatically when it comes up, with no server involved. This is why two hosts on a segment can communicate over IPv6 the instant they are connected, whether or not anyone configured IPv6 — a fact that surprises administrators who believe they "do not run IPv6."

**Addresses have lifetimes.** Privacy extensions generate temporary global addresses that rotate, so a host may hold a stable address and several deprecated temporary ones at once. Logging that records only one address per host will fail to correlate activity.

## SLAAC: Configuration Without a Server

IPv4 hosts get addresses from DHCP. IPv6 hosts can configure themselves through **SLAAC (Stateless Address Autoconfiguration)** using **Router Advertisement** messages.

```mermaid
sequenceDiagram
    participant H as Host
    participant L as Link (multicast)
    participant R as Router
    Note over H: Interface up — self-assign fe80:: address
    H->>L: Neighbor Solicitation for own address (duplicate detection)
    Note over H: No reply — address is unique and usable
    H->>L: Router Solicitation to ff02::2
    R-->>H: Router Advertisement: prefix 2001:db8:acad:10::/64, flags, lifetimes
    Note over H: Build global address from prefix + interface identifier
    H->>L: Neighbor Solicitation for the new global address
    Note over H: No reply — address usable; default route set to the advertising router
```

The security-critical property is visible in the diagram: **the host accepts a prefix and a default gateway from whichever device answers.** Router Advertisements are unauthenticated by default. Any host on the segment that emits them becomes a router for every listener — the IPv6 equivalent of a rogue lease server, and generally easier to exploit because no request has to be won by racing. The mitigation is **RA Guard** on access switches, which drops advertisements arriving on ports that should never carry them.

DHCPv6 also exists and can operate alongside SLAAC. The `M` (managed) and `O` (other) flags in the advertisement tell hosts whether to use it, but operating system behaviour varies — some prefer SLAAC, some run both. Assuming one mechanism is authoritative is a recurring source of addresses that appear from nowhere.

## Reading the Configuration

```bash
ip -6 addr show dev eth0
ip -6 route
ip -6 neigh
```

Expected excerpt:

```text
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500
    inet6 2001:db8:acad:1:a1b2:c3d4:e5f6:7890/64 scope global temporary dynamic
       valid_lft 6821sec preferred_lft 3221sec
    inet6 2001:db8:acad:1:20c:29ff:fe4a:9b31/64 scope global dynamic mngtmpaddr
       valid_lft 2591821sec preferred_lft 604621sec
    inet6 fe80::20c:29ff:fe4a:9b31/64 scope link
       valid_lft forever preferred_lft forever

default via fe80::1 dev eth0 proto ra metric 100 expires 1621sec
2001:db8:acad:10::/64 dev eth0 proto ra metric 100 expires 2591821sec

fe80::1 dev eth0 lladdr 00:00:5e:00:53:01 router REACHABLE
```

Every line carries a finding:

- **Three addresses on one interface.** A rotating `temporary` address for outbound connections, a stable one, and the permanent link-local. Correlating logs across all three is necessary to attribute activity to a host.
- **`20c:29ff:fe4a:9b31`** — the `ff:fe` in the middle marks a EUI-64 identifier derived from the hardware address. This leaks the network card's identity and makes a host trackable across networks, which is exactly why privacy extensions were introduced. Seeing this pattern on a modern client suggests privacy extensions are disabled.
- **`default via fe80::1 ... proto ra`** — the default gateway is a *link-local* address learned from a Router Advertisement. `proto ra` names the source of the route, and `expires` shows it must be refreshed. If a rogue advertisement wins, this line is where it appears.
- **`router REACHABLE`** — the neighbour entry confirms the device identified itself as a router.

Test reachability, noting that link-local addresses require a zone index because the same address can exist on multiple interfaces:

```bash
ping6 -c 2 fe80::1%eth0
ping6 -c 2 2001:db8:acad:10::10
```

Expected excerpt:

```text
64 bytes from fe80::1%eth0: icmp_seq=1 ttl=64 time=0.48 ms
64 bytes from 2001:db8:acad:10::10: icmp_seq=1 ttl=64 time=1.21 ms
```

The `%eth0` suffix is mandatory for link-local and omitting it produces `Invalid argument` — a small detail that consumes a surprising amount of troubleshooting time.

## Security Implications

IPv6's security problems are overwhelmingly problems of *unmanaged* IPv6 rather than flaws in the protocol.

**The dual-stack blind spot.** Modern operating systems enable IPv6 by default and prefer it over IPv4 when both are available. A network where "IPv6 is not deployed" frequently still has link-local connectivity on every segment, and sometimes global connectivity via an unnoticed advertisement or tunnel. If firewall policy, monitoring, and access control were written for IPv4 only, a fully functional and completely unfiltered path exists in parallel. This is one of the most reliably productive findings in an authorized internal assessment, and the fix is parity — equivalent rules, logging, and inspection for both families — not disablement.

**Rogue Router Advertisements.** Because advertisements are unauthenticated, an attacker on the segment can become the default gateway for every listening host, or trigger renumbering. It is the IPv6 analogue of rogue lease and address-resolution attacks and, like them, is confined to the local link. RA Guard and restricting which ports may source advertisements are the controls.

**Neighbor Discovery.** IPv6 replaced address resolution with Neighbor Discovery, which inherits the same lack of authentication and therefore the same spoofing exposure. The corresponding switch feature is ND inspection.

**Scanning does not work the same way.** A `/64` contains more addresses than could ever be swept, so exhaustive host discovery is impossible. Enumeration shifts to multicast responses on the local link, DNS records, log analysis, and management systems. Defensively, this means "we are hard to scan" is not a control — an attacker with local access uses `ff02::1` and finds everything instantly.

**Disabling IPv6 is rarely the right answer.** Several platform and management components assume its presence, and disabling it partially can create the worst of both worlds: components still emit IPv6 traffic while policy and monitoring assume it is absent. Manage it deliberately instead.

All discovery and probing described here must stay within an authorized scope. Multicast enumeration is quiet but not invisible, and it reaches every host on the segment.

## Summary

You should now be able to:

- Compress and expand an IPv6 address correctly, explain why `::` may appear only once, and name the link-local, unique-local, global, and multicast ranges.
- Read `ip -6 addr`, `ip -6 route`, and `ip -6 neigh` to identify temporary versus stable addresses, EUI-64 derivation, and a gateway learned from an advertisement; use a zone index correctly when addressing link-local.
- Explain why `/64` is the fixed subnet size and what breaks otherwise; describe how unauthenticated Router Advertisements enable a rogue gateway and which switch control prevents it; and justify policy parity over disablement when addressing a dual-stack blind spot.

---
> 🔼 Up: [[Addressing & Subnetting]]
