---
title: "VLANs & Trunking"
aliases: ["VLAN", "802.1Q", "Trunk Port", "VLAN Hopping", "Native VLAN"]
tags:
  - tree/networking
  - cyber/networking/layer2
  - type/concept
  - level/operator
Domain:
  - "[[Switching & the Link Layer]]"
Color: "#42D4F4"
---

# 🗂️ VLANs & Trunking

> [!abstract] Note of [[Switching & the Link Layer]]
> A VLAN turns one physical switch into several independent networks by tagging frames, and a trunk carries many VLANs down one link. This note explains the 802.1Q tag, the access/trunk distinction, and the two configuration weaknesses — the native VLAN and dynamic trunk negotiation — that let an attacker escape their assigned segment.

## Parent Learning Order
Ethernet & Frame Structure -> MAC Addressing & Switch Operation -> ARP & Neighbor Discovery -> VLANs & Trunking -> Spanning Tree & Loop Prevention -> Link Layer Security Controls

## Start at Zero: One Switch, Many Networks

Without VLANs, a switch is one broadcast domain — every port can reach every other port at Layer 2. A **VLAN (Virtual Local Area Network)** partitions that single switch into multiple logical broadcast domains. Ports assigned to VLAN 10 form one network; ports in VLAN 20 form another; and a frame cannot pass between them without a routing decision.

This is the primary segmentation tool in a wired network. Finance, guests, voice phones, and management can share physical switches while remaining logically isolated, and the isolation is enforced in switch hardware rather than by physical separation. The security value is direct: an attacker who compromises a device in the guest VLAN cannot reach the finance VLAN at Layer 2, because the two are different broadcast domains that meet only at a router where policy applies.

> [!tip] The analogy, and where it breaks
> A VLAN is like colour-coding desks in an open office so only same-colour desks may talk. It captures logical grouping over physical layout. It breaks because the "colour" travels *in the frame* as a tag that can, under weak configuration, be forged or stacked — the analogy has no equivalent of an attacker relabelling their own desk.

## The 802.1Q Tag

How does a switch know which VLAN a frame belongs to when many VLANs share one uplink? It inserts a four-byte **802.1Q tag** into the frame, between the source MAC and the EtherType.

```text
+---------+---------+------------------+----------+---------+-----+
| Dst MAC | Src MAC | 802.1Q tag (4B)  | EtherType| Payload | FCS |
+---------+---------+------------------+----------+---------+-----+
                    |  TPID  | PCP|DEI|VID (12 bits) |
                    | 0x8100 |    |   | VLAN 1-4094  |
```

- **TPID** `0x8100` marks the frame as tagged; it sits where the EtherType normally would, signalling that the real EtherType follows the tag.
- **VID (VLAN Identifier)** is 12 bits, giving 4094 usable VLANs (0 and 4095 are reserved).
- **PCP** carries a priority value for quality of service.

The tag is added and removed by switches, not by hosts. An ordinary endpoint sends and receives *untagged* frames and is unaware VLANs exist; the switch tags the frame on ingress based on the port's VLAN and strips it before delivery.

## Access Ports and Trunk Ports

Every switch port operates in one of two modes, and confusing them is the source of most VLAN incidents.

| Port type | Carries | Tagging | Connects to |
| --- | --- | --- | --- |
| **Access port** | Exactly one VLAN | Frames are untagged toward the device | An endpoint: PC, printer, phone |
| **Trunk port** | Many VLANs | Frames are tagged with their VID | Another switch, a router, a hypervisor |

An access port belongs to a single VLAN. A device plugged into it sends untagged frames, the switch assigns them to that port's VLAN, and the device never sees a tag. This is what an ordinary user connects to.

A trunk port carries multiple VLANs between infrastructure devices, tagging each frame so the far end can sort them back into the right VLANs. The uplink between two switches, or from a switch to a hypervisor hosting VMs in different VLANs, is a trunk.

```mermaid
flowchart TB
    PC1["PC — VLAN 10"] -->|"untagged"| SW1["Switch 1"]
    PC2["Phone — VLAN 20"] -->|"untagged"| SW1
    SW1 -->|"trunk: tagged 10 & 20"| SW2["Switch 2"]
    SW2 -->|"untagged VLAN 10"| PC3["PC — VLAN 10"]
    SW2 -->|"untagged VLAN 20"| PC4["Phone — VLAN 20"]
```

Read the diagram at the trunk: the single physical link between the switches carries both VLANs simultaneously, kept separate by their tags. The access links on either side are untagged, because the endpoints must not be aware of VLANs. The whole scheme depends on the switches agreeing about which ports are trunks — and that agreement is where attacks live.

## VLAN Hopping: Escaping Your Segment

An attacker confined to one VLAN wants to reach another. Two techniques exploit configuration weaknesses.

**Switch spoofing.** Some switches default to *negotiating* trunk status automatically. An attacker's device can send the negotiation signals that request a trunk, and if the switch agrees, the attacker's port becomes a trunk carrying *every* VLAN. The attacker can then tag frames for any VLAN and reach all of them. The fix is to disable dynamic trunk negotiation and configure access ports explicitly as access — a port facing an endpoint should never be willing to become a trunk.

**Double tagging.** This exploits the **native VLAN** — the one VLAN a trunk carries *untagged*. An attacker on the native VLAN sends a frame with *two* stacked tags: an outer tag for the native VLAN and an inner tag for the target VLAN. The first switch strips the outer tag (because it matches the native VLAN and native traffic is untagged on the trunk) and forwards the frame, still bearing the inner tag, across the trunk. The second switch reads the inner tag and delivers the frame into the target VLAN.

```mermaid
sequenceDiagram
    participant A as Attacker (native VLAN 1)
    participant S1 as Switch 1
    participant S2 as Switch 2
    participant T as Target VLAN 20
    A->>S1: Frame tagged [outer VLAN 1][inner VLAN 20]
    Note over S1: Native VLAN is untagged on trunk -> strip outer tag
    S1->>S2: Frame still tagged [VLAN 20]
    S2->>T: Deliver into VLAN 20
    Note over A,T: One-way injection; no reply path
```

Double tagging is one-directional — the attacker can inject frames into the target VLAN but receives no replies, because the return path has no matching double-tag trick. That still enables meaningful attacks: injecting into a management VLAN, or triggering a reflected response to a third party. The defence is to make the native VLAN an unused, dedicated VLAN that carries no real traffic and to which no access port is assigned, so an attacker is never on it, and to tag the native VLAN explicitly where the hardware allows.

## Security Implications

**A VLAN is only as strong as the configuration around it.** The isolation is real, but it rests on assumptions: that access ports cannot become trunks, that the native VLAN is not an attacker-reachable production VLAN, and that inter-VLAN routing applies policy. Violate any one and the segmentation leaks. VLAN separation should therefore be verified by testing hop attempts, not assumed from a design document.

**VLANs are a segmentation control, not a security boundary for high-value assets.** The consensus in security architecture is that VLANs are appropriate for separating broad traffic classes, but the most sensitive segments — cardholder data, industrial control, management planes — warrant physical separation or firewalled routing rather than reliance on tag integrity alone. A single misconfiguration collapses a VLAN boundary; a routed firewall boundary fails more safely.

**Inter-VLAN routing is where policy actually lives.** VLANs stop Layer 2 adjacency, but the moment a router or Layer 3 switch connects them, whatever that device permits is permitted. A permissive inter-VLAN rule set makes segmented VLANs behave like one flat network for routed traffic. The VLAN design and the routing policy must be reviewed together.

**The voice VLAN is a common weak point.** IP phones are often placed in a dedicated voice VLAN, and the switch port serving a phone carries both the voice VLAN (tagged) and a data VLAN (untagged) for a PC daisy-chained behind the phone. This dual-VLAN access port is a legitimate configuration that also widens the attacker's reachable VLAN set from a single physical port.

All hopping and trunk-negotiation testing described here must occur only on an isolated lab you own. Successfully hopping a VLAN on a production network crosses a segmentation boundary that other systems depend on.

## Authorized Lab: Configure, Then Hop, a VLAN

Use two lab switches (hardware or virtualized) and three VMs. Record baseline port configurations first.

1. Configure Switch 1 with two access VLANs: place Host-A in VLAN 10 and Host-B in VLAN 20. Confirm A and B cannot reach each other at Layer 2.
2. Configure the link between the two switches as a trunk carrying both VLANs, with a defined native VLAN. Place Host-C in VLAN 10 on Switch 2 and confirm A and C can now reach each other while B remains isolated.
3. Verify the tagging by capturing on the trunk link:

```bash
sudo tcpdump -i eth0 -nn -e -c 4 vlan
```

Expected excerpt:

```text
00:0c:29:4a:9b:31 > ff:ff:ff:ff:ff:ff, ethertype 802.1Q (0x8100), vlan 10, ...
00:0c:29:7b:2c:14 > ff:ff:ff:ff:ff:ff, ethertype 802.1Q (0x8100), vlan 20, ...
```

The `vlan 10` and `vlan 20` markers confirm both VLANs share the trunk, kept separate by their tags.

4. Demonstrate switch spoofing: leave dynamic trunk negotiation enabled on Host-A's access port, have Host-A request a trunk, and observe the port becoming a trunk that exposes both VLANs. Then disable negotiation, hard-set the port to access, and confirm the request now fails.
5. Demonstrate double tagging: set the native VLAN to a production VLAN (the misconfiguration), have Host-A on the native VLAN send a double-tagged frame targeting VLAN 20, and confirm it arrives at Host-B. Then change the native VLAN to a dedicated unused VLAN and confirm the injection no longer reaches VLAN 20.
6. Restore all ports to their baseline configuration and confirm the original isolation: A and C reachable, B isolated, no port willing to trunk.

Expected interpretation:

```text
Access ports        -> A (VLAN 10) and B (VLAN 20) isolated at Layer 2
Trunk capture       -> both VLANs share one link, separated only by tags
Negotiation enabled -> attacker's port becomes a trunk; all VLANs exposed
Native = production  -> double-tagged frame injects into VLAN 20
Native = unused      -> injection fails; the attacker is never on the native VLAN
```

## Crook → Operator → Root Checkpoint

- **Crook:** Explain what a VLAN accomplishes, the difference between an access port and a trunk port, and why an endpoint never sees a tag.
- **Operator:** Read the 802.1Q tag in a capture, configure access and trunk ports, and verify that two VLANs are isolated by testing reachability rather than trusting the design.
- **Root:** Explain switch spoofing and double tagging in terms of the native VLAN and dynamic trunk negotiation; justify why VLANs are a segmentation control rather than a boundary for the highest-value assets, and why VLAN design and inter-VLAN routing policy must be reviewed together.

---
> 🔼 Up: [[Switching & the Link Layer]]
