---
title: "VLSM & Route Summarization"
aliases: ["VLSM", "Supernetting", "Route Aggregation", "Route Summarization"]
tags:
  - tree/networking
  - cyber/networking/addressing
  - type/technique
  - difficulty/medium
Domain:
  - "[[Addressing & Subnetting]]"
Color: "#42D4F4"
---

# 🪜 VLSM & Route Summarization

> [!abstract] Note of [[Addressing & Subnetting]]
> Fixed-size subnets waste address space and produce routing tables that grow without bound. This note covers the two techniques that fix that — dividing a block into unequal pieces, and collapsing many prefixes into one — and shows how longest-prefix match makes both safe, plus how summarization silently widens security policy if it is applied to rules rather than routes.

## Parent Learning Order
IPv4 Addressing -> Subnetting & CIDR -> VLSM & Route Summarization -> IPv6 Addressing -> Address Assignment & DHCP -> NAT & Address Translation

## One Size Does Not Fit

Suppose you are given `172.16.8.0/22` and must serve four networks:

| Segment | Hosts needed |
| --- | --- |
| Staff | 500 |
| Servers | 100 |
| Management | 25 |
| Router-to-router link | 2 |

Splitting the `/22` into four equal `/24` blocks fails immediately — Staff needs 500 addresses and a `/24` provides 254. Splitting into equal `/23` blocks gives only two subnets. Any fixed-size scheme either starves the largest segment or squanders hundreds of addresses on a link that needs two.

**VLSM (Variable-Length Subnet Masking)** removes the constraint: different subnets carved from the same parent may use different prefix lengths. It is not a new protocol, only the disciplined application of subnetting recursively.

The method has one rule that must not be broken: **allocate largest first**. Taking the small blocks first fragments the space and strands the large requirement with no contiguous room.

**Prerequisites:** CIDR notation and how to compute a subnet's range.

> [!tip] The analogy, and where it breaks
> Cutting a plank of wood: take the longest piece first and the offcuts still fit the smaller jobs, but cut the small pieces out of the middle first and you can never recover a long one. That is exactly why VLSM allocates largest-first. The analogy breaks for summarization, since you cannot glue planks back together in the physical world, whereas contiguous, aligned prefixes genuinely do collapse into one advertisement — provided the alignment rule holds.

## Worked Allocation

Start with `172.16.8.0/22`, which spans `172.16.8.0` through `172.16.11.255` — 1,024 addresses.

**Step 1 — Staff, 500 hosts.** Need 512 addresses → 9 host bits → `/23`.

```text
172.16.8.0/23    usable 172.16.8.1 - 172.16.9.254    broadcast 172.16.9.255
```

Remaining space begins at `172.16.10.0`.

**Step 2 — Servers, 100 hosts.** Need 128 → 7 host bits → `/25`.

```text
172.16.10.0/25   usable 172.16.10.1 - 172.16.10.126  broadcast 172.16.10.127
```

Remaining space begins at `172.16.10.128`.

**Step 3 — Management, 25 hosts.** Need 32 → 5 host bits → `/27`.

```text
172.16.10.128/27 usable 172.16.10.129 - 172.16.10.158 broadcast 172.16.10.159
```

Remaining space begins at `172.16.10.160`.

**Step 4 — Point-to-point link, 2 hosts.** A `/30` gives exactly two usable addresses.

```text
172.16.10.160/30 usable 172.16.10.161 - 172.16.10.162 broadcast 172.16.10.163
```

`172.16.10.164` through `172.16.11.255` remains free for growth — roughly 380 addresses held in reserve, contiguous and therefore still summarizable.

```mermaid
flowchart TB
    P["172.16.8.0/22 — 1024 addresses"]
    P --> S["Staff /23 — 512"]
    P --> R["172.16.10.0/24 remainder"]
    R --> SV["Servers /25 — 128"]
    R --> R2["172.16.10.128/25 remainder"]
    R2 --> M["Management /27 — 32"]
    R2 --> R3["172.16.10.160/27 remainder"]
    R3 --> L["P2P link /30 — 4"]
    R3 --> F["Free space, contiguous, reserved for growth"]
```

Read the diagram as repeated halving. Each allocation consumes an aligned block and leaves an aligned remainder, which is what keeps the free space usable. Allocating out of order — taking the `/30` from the middle of the range first — would leave two smaller fragments where the `/23` needed to fit, and the design would fail with plenty of "free" addresses available.

Verify each block:

```bash
ipcalc 172.16.8.0/23
```

Expected excerpt:

```text
Network:   172.16.8.0/23
HostMin:   172.16.8.1
HostMax:   172.16.9.254
Broadcast: 172.16.9.255
Hosts/Net: 510
```

510 usable against a requirement of 500 confirms the choice; a `/24` would have failed and a `/22` would have wasted the rest of the parent.

## Summarization: The Opposite Operation

**Route summarization** (also called aggregation or supernetting) advertises many contiguous prefixes as one shorter prefix. Where VLSM divides, summarization collapses.

To summarize, find the longest run of leading bits common to every constituent prefix.

Given four networks:

```text
192.168.4.0/24   11000000.10101000.000001 00.00000000
192.168.5.0/24   11000000.10101000.000001 01.00000000
192.168.6.0/24   11000000.10101000.000001 10.00000000
192.168.7.0/24   11000000.10101000.000001 11.00000000
                 └──── 22 identical bits ──┘
```

The first 22 bits match, so the summary is `192.168.4.0/22` — one advertisement replacing four.

Two conditions must hold, and violating either causes real outages. The blocks must be **contiguous**, and the summary must be **aligned** on a boundary that is a multiple of its own size. `192.168.4.0/22` is valid because 4 is a multiple of 4. Summarizing `192.168.5.0/24` through `192.168.8.0/24` as a `/22` would be wrong: the range is not aligned, and the resulting advertisement would cover `192.168.4.0` — an address block you may not own — while excluding `192.168.8.0`.

That failure mode has a name in operations: advertising address space you do not control. On an internal network it causes traffic blackholing; on the public Internet it is the mechanism behind route hijacking, whether accidental or deliberate.

```bash
ip route
```

Expected excerpt after summarization:

```text
192.168.4.0/22 via 10.255.0.2 dev eth1 proto ospf metric 20
```

versus before:

```text
192.168.4.0/24 via 10.255.0.2 dev eth1 proto ospf metric 20
192.168.5.0/24 via 10.255.0.2 dev eth1 proto ospf metric 20
192.168.6.0/24 via 10.255.0.2 dev eth1 proto ospf metric 20
192.168.7.0/24 via 10.255.0.2 dev eth1 proto ospf metric 20
```

The benefit is not only table size. Fewer entries mean faster lookups, less memory on constrained hardware, and — most importantly — **fault isolation**: if one of the four subnets flaps, the summary does not change, so the instability is not propagated to the rest of the network.

The cost is precision. The summarizing router now claims reachability for all 1,024 addresses even if one constituent `/24` is down. Traffic for the failed subnet is attracted and then discarded. Summarization trades granular failure signalling for stability, which is usually the right trade but must be a conscious one.

## Longest-Prefix Match Makes It Safe

Both techniques rely on one forwarding rule: when several routes match a destination, the router selects the one with the **longest prefix**, regardless of metric or source. Metric is only a tiebreaker between routes of equal prefix length.

Consider a table containing:

```text
0.0.0.0/0          via 10.255.0.1
192.168.0.0/16     via 10.255.0.2
192.168.4.0/22     via 10.255.0.3
192.168.5.0/24     via 10.255.0.4
192.168.5.77/32    via 10.255.0.5
```

Trace destinations:

```bash
ip route get 192.168.5.77
ip route get 192.168.5.20
ip route get 192.168.6.20
ip route get 192.168.30.1
```

Expected excerpt:

```text
192.168.5.77 via 10.255.0.5 dev eth1     # /32 — most specific wins
192.168.5.20 via 10.255.0.4 dev eth1     # /24
192.168.6.20 via 10.255.0.3 dev eth1     # /22
192.168.30.1 via 10.255.0.2 dev eth1     # /16
```

This is the property that lets a specific exception coexist with a broad summary. It is also the property that makes an accidental specific route so dangerous: a single injected `/32` overrides every broader route for that destination, and it will not appear anomalous in a table dominated by aggregates.

## Security Implications

The routing behaviour above transfers directly into two security problems.

**Specific routes override broad intent.** Because longest match always wins, an attacker or a misconfiguration that inserts a more specific prefix silently captures traffic for that destination. Nothing breaks, users notice nothing, and the traffic simply travels through somewhere it should not. Detection requires monitoring for unexpected specific prefixes and for changes in path, not merely for reachability — everything still "works" during such an event. On the public Internet the same mechanism is BGP hijacking, mitigated by origin validation such as RPKI; internally the equivalent control is authenticating routing protocol updates and filtering which prefixes a neighbour may announce.

**Summarization applied to policy is a silent privilege grant.** Aggregating *routes* is good engineering. Aggregating *firewall rules* the same way is not. A reviewer who replaces four `/24` permit rules with one `/22` for tidiness has authorized 1,024 addresses instead of 1,016 — and if the four subnets were non-contiguous, far more. Address ranges in rules must be expanded to their literal extent during review, because the notation hides the difference between what was intended and what was granted.

**Reserved space is not unused space.** The contiguous remainder left by good VLSM design is often absent from rules, monitoring, and asset inventories. When it is later allocated, hosts appear in a range no control anticipated. Reserved blocks should be explicitly denied and monitored until they are formally assigned.

Any route or rule inspection described here should be performed on infrastructure within an authorized scope; routing tables reveal internal topology and are themselves sensitive.

## Summary

You should now be able to:

- Explain why equal-size subnets waste space, and state the largest-first rule for VLSM allocation.
- Perform a full VLSM allocation for mixed requirements, compute a valid summary from a set of contiguous prefixes, and verify both with `ipcalc` and `ip route get`.
- Explain why an unaligned summary advertises space you may not own and what that causes internally and on the Internet; describe how longest-prefix match allows a single injected specific route to redirect traffic invisibly, and why summarizing firewall rules is a silent authorization change rather than a cosmetic one.

---
> 🔼 Up: [[Addressing & Subnetting]]
