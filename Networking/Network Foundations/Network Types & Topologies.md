---
title: "Network Types & Topologies"
aliases: ["LAN", "WAN", "Network Topology", "Broadcast Domain"]
tags:
  - tree/networking
  - cyber/networking/foundations
  - type/concept
  - level/crook
Domain:
  - "[[Network Foundations]]"
Color: "#42D4F4"
---

# 🕸️ Network Types & Topologies

> [!abstract] Note of [[Network Foundations]]
> A network is defined less by its cables than by its boundaries: who can reach whom without a router, who shares a broadcast, and where administrative trust changes hands. This note builds the vocabulary of scope and shape, then converts it into the two questions that matter operationally — what is my blast radius, and where does traffic become someone else's problem?

## Parent Learning Order
Network Types & Topologies -> The OSI Model -> The TCP-IP Model -> Encapsulation & Protocol Data Units -> Network Devices & Traffic Paths -> Reachability Testing & ICMP

## Start at Zero: What a Network Actually Is

A **network** is two or more devices that can exchange data using an agreed set of rules. That is the whole definition. Everything else — switches, routers, subnets, firewalls — exists to answer one repeated question: *given this destination, where do I send the data next?*

Before any of that, you need three terms.

A **node** (or **host**) is anything with a network interface that sends or receives data: a laptop, a printer, a virtual machine, a container, a phone. A **link** is the medium connecting nodes — copper, fibre, or radio. A **segment** is a set of nodes that can reach each other over links alone, with no routing decision in between.

The single most useful concept for a beginner is the **broadcast domain**: the set of devices that receive a frame addressed to "everyone on this segment." Two hosts in the same broadcast domain can discover and talk to each other directly. Two hosts in different broadcast domains cannot — they need a router, and a router is a place where policy can be applied. This is why segmentation is a security control and not merely a design preference.

> [!tip] The analogy, and where it breaks
> A broadcast domain is like a room where shouting reaches everyone. A router is the door between rooms. The analogy breaks down in two places: a switch quietly delivers most traffic point-to-point rather than shouting it, and modern virtual networks put "rooms" inside a single physical box, so physical proximity tells you nothing about logical adjacency.

## Classifying by Scope

Networks are conventionally named by geographic and administrative reach. The names are loose, but they communicate who owns the infrastructure and therefore who can change it.

| Term | Scope | Typical owner | Example |
| --- | --- | --- | --- |
| **PAN** | A person, metres | The individual | Bluetooth headset, wearable |
| **LAN** | One site or building | The organization | Office floor, home network |
| **VLAN** | A logical slice of a LAN | The organization | `Finance` separated from `Guest` |
| **CAN** | Several adjacent buildings | The organization | University campus |
| **MAN** | A metropolitan area | Carrier or municipality | City-wide fibre ring |
| **WAN** | Regions, countries | Multiple carriers | Corporate inter-site links, the Internet |
| **Overlay / VPN** | Logical, spans anything | The organization | Encrypted tunnel joining two sites |

The security consequence of this table is trust asymmetry. Devices on the same LAN historically trusted each other far more than they trusted anything outside — file shares, printer discovery, credential caching, and management protocols were all designed for a "friendly" local segment. That assumption is why a single foothold inside a LAN is disproportionately valuable, and why modern architecture pushes toward treating the local segment as hostile.

An **overlay** deserves special attention because it breaks the geography intuition entirely. A VPN or software-defined overlay makes two hosts on different continents behave as if they share a segment. Everything you conclude about trust from a physical diagram must therefore be re-checked against the logical topology.

## Topology: Physical Shape versus Logical Behaviour

**Topology** describes how nodes are interconnected. Crucially, the *physical* topology (where the cables run) and the *logical* topology (how traffic actually flows) can differ.

| Topology | Structure | Failure behaviour | Status |
| --- | --- | --- | --- |
| **Star** | Every node to a central switch | One link fails, one node drops; the switch is a single point of failure | Dominant today |
| **Bus** | All nodes share one backbone | One break kills the segment | Legacy |
| **Ring** | Each node connects to two neighbours | Break splits the ring unless dual-ring | Legacy, some carrier use |
| **Mesh** | Many nodes interconnect directly | Highly resilient, expensive | Core/backbone, wireless mesh |
| **Tree / hierarchical** | Stars uplinked into a core | Localized failure, predictable growth | Standard enterprise design |

Real enterprise networks are a **tree of stars**: access switches serving endpoints, uplinked to distribution switches, uplinked to a core, with routers and firewalls at the edge. This is drawn as three tiers because each tier has a different job — access enforces port-level policy, distribution aggregates and routes between VLANs, core moves traffic fast without policy.

```mermaid
flowchart TD
    INET["Internet / WAN"] --> FW["Edge firewall"]
    FW --> CORE["Core switch / router"]
    CORE --> D1["Distribution A"]
    CORE --> D2["Distribution B"]
    D1 --> A1["Access switch: VLAN 10 Staff"]
    D1 --> A2["Access switch: VLAN 20 Finance"]
    D2 --> A3["Access switch: VLAN 30 Guest"]
    A1 --> H1["Workstations"]
    A2 --> H2["Finance hosts"]
    A3 --> H3["Guest devices"]
```

Read the diagram as a policy map, not a cable map. Every downward edge is a place where a forwarding decision is made, and every horizontal boundary between VLANs is a place where a rule can allow or deny. If two branches meet only at the core, then the core is the only place a control can be applied between them — and if that control is absent, the two branches are effectively one flat network regardless of how the drawing looks.

## The Flat Network Problem

A **flat network** is one large broadcast domain with no internal segmentation. It is easy to run and catastrophic to defend, because every host is one link-layer hop from every other host. In a flat network, an attacker with any foothold can enumerate neighbours, impersonate the gateway, answer name-resolution requests, and reach management interfaces that were never meant to be exposed to endpoints.

Segmentation fixes this by making lateral movement cross a controlled boundary. The practical design questions are:

- Which systems must talk to each other, and on which ports? Everything else is denied.
- Where do management interfaces live, and can an ordinary endpoint reach them?
- Is a guest or IoT device in its own domain with no path to corporate resources?
- Does the segmentation survive an attacker who already has valid credentials?

That last question is the one that separates real segmentation from decorative segmentation. A VLAN with a permissive inter-VLAN rule set is a drawing, not a control.

## Mapping a Network You Are Authorized to Examine

Start with what your own host already knows. These commands read local state and do not touch other systems.

```bash
ip addr show                 # interfaces, addresses, prefix lengths
ip route                     # local subnets and the default gateway
ip neigh                     # neighbours already resolved on this segment
```

Expected excerpt:

```text
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 state UP
    inet 192.168.10.24/24 brd 192.168.10.255 scope global eth0

default via 192.168.10.1 dev eth0 proto dhcp metric 100
192.168.10.0/24 dev eth0 proto kernel scope link src 192.168.10.24

192.168.10.1 dev eth0 lladdr 00:1a:2b:3c:4d:5e REACHABLE
```

Three facts fall out of that output, and each one answers a scope question:

- `192.168.10.24/24` means this host's own segment holds 254 usable addresses. That is the set of hosts reachable without any routing decision.
- `default via 192.168.10.1` identifies the gateway — the only exit from this broadcast domain, and therefore the natural place for policy.
- The neighbour entry proves the gateway answered at the link layer, which is a stronger statement than "an address is configured."

To enumerate live hosts within a block you are explicitly authorized to test, use a host-discovery sweep:

```bash
nmap -sn 192.168.10.0/24
```

Expected excerpt:

```text
Nmap scan report for 192.168.10.1
Host is up (0.00089s latency).
Nmap scan report for 192.168.10.24
Host is up (0.000058s latency).
Nmap done: 256 IP addresses (2 hosts up) scanned in 2.41 seconds
```

### The misleading result you must expect

"2 hosts up" does not mean two hosts exist. Host discovery infers liveness from replies, and replies can be suppressed. A host firewall that drops ICMP and unsolicited probes will appear dead. Conversely, a security appliance that answers on behalf of absent addresses can make an empty range look fully populated.

The troubleshooting workflow is to change the evidence type rather than repeat the same probe:

```bash
nmap -sn -PR 192.168.10.0/24        # ARP-based discovery, local segment only
```

ARP discovery is far harder to suppress on a local segment because a host that ignores ARP cannot receive traffic at all. If ARP finds hosts that ICMP missed, the correct conclusion is "ICMP is filtered," not "the network changed."

## Security Implications

Scope and shape determine three things that matter to both attackers and defenders.

**Blast radius.** The size of a broadcast domain sets how many systems a single compromised host can reach without crossing a control. An oversized flat range multiplies the consequences of one weak endpoint.

**Observability.** Traffic that never crosses a routed boundary may never pass a sensor. If all inspection sits at the edge firewall, intra-segment lateral movement is invisible. Sensor placement must follow the topology, not the org chart.

**Trust inheritance.** Overlays, VPNs, and virtual switches can silently join segments that the physical diagram shows as separate. Any assessment of exposure must be validated against live routing and neighbour state rather than documentation.

All enumeration described here is limited to systems within an authorized scope. Host discovery generates traffic that is logged, and sweeping ranges outside an agreed boundary is both detectable and out of bounds.

## Authorized Lab: Prove a Boundary Exists

Use two virtual machines on an isolated hypervisor network you control.

1. Place both VMs on the same virtual switch. Record `ip addr` and `ip route` on each.
2. From VM-A, run `nmap -sn -PR <segment>/24` and confirm VM-B appears.
3. Move VM-B to a second virtual switch with its own subnet and a router between the two.
4. Repeat the ARP-based sweep from VM-A. VM-B must now be absent, because ARP does not cross a routed boundary.
5. Repeat with `nmap -sn <VM-B subnet>/24`. VM-B should reappear, because ICMP does route.
6. Add a deny rule on the router for traffic between the two subnets and repeat step 5.
7. Remove the rule and restore both VMs to their original switch.

Expected interpretation:

```text
Same segment, ARP sweep      -> host found   (no routing decision required)
Routed segments, ARP sweep   -> host absent  (proves a broadcast-domain boundary)
Routed segments, ICMP sweep  -> host found   (proves routing works)
Routed + deny rule, ICMP     -> host absent  (proves the control, not the topology)
```

Steps 4 and 6 produce the same observable result — "host not found" — for completely different reasons. Distinguishing them is the entire skill.

## Crook → Operator → Root Checkpoint

- **Crook:** Define node, link, segment, and broadcast domain; name the common topologies and explain why star-of-stars dominates.
- **Operator:** Read `ip addr`, `ip route`, and `ip neigh` to state your own segment, gateway, and reachable scope; run an authorized sweep and explain why ARP and ICMP discovery can disagree.
- **Root:** Given a topology diagram, identify every enforcement point and every place where an overlay could bypass one; design a segmentation scheme that still constrains an attacker holding valid credentials, and specify where sensors must sit to observe intra-segment movement.

---
> 🔼 Up: [[Network Foundations]]
