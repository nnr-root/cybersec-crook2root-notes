---
title: "Packet Capture & Analysis"
aliases: ["Packet Capture", "BPF", "PCAP", "libpcap", "Capture Filter", "Display Filter"]
tags:
  - tree/networking
  - cyber/networking/analysis
  - type/technique
  - level/apprentice
Domain:
  - "[[Network Analysis & Troubleshooting]]"
Color: "#42D4F4"
---

# 🎣 Packet Capture & Analysis

> [!abstract] Note of [[Network Analysis & Troubleshooting]]
> Packet capture is the ground truth of networking — when tools disagree and theories conflict, the packets settle it. This note covers how capture actually works, the two kinds of filter that are constantly confused, and how to get traffic to your capture tool in a switched network where, by design, you do not see other hosts' frames.

## Parent Learning Order
Packet Capture & Analysis -> Structured Network Troubleshooting -> Traffic Analysis & Flow Inspection -> Performance & Latency Analysis -> Connectivity Diagnostics -> Protocol Debugging & Deep Inspection

## Start at Zero: Reading the Wire Directly

Every diagnostic tool so far has *interpreted* the network — reported a state, a route, a connection. **Packet capture** shows the raw traffic itself: the actual bytes on the wire, header by header. It is the authoritative evidence, because it is not an interpretation — it is what actually happened. When a developer says "the request was sent" and the server says "nothing arrived," the capture ends the argument.

Capture works by putting the network interface into **promiscuous mode**, telling it to hand the operating system every frame it receives rather than only frames addressed to it. A capture library — **libpcap** on Unix-like systems — then delivers those frames to tools like `tcpdump` and Wireshark. The result can be saved as a **PCAP file**, a portable record that any analysis tool can open later.

```bash
sudo tcpdump -i eth0 -w capture.pcap -c 100 'tcp port 443'
```

This captures 100 TCP/443 packets to a file. The `-w` writes raw packets (openable in Wireshark), `-c` bounds the count, and the final expression is a **filter** — the single most important concept in capture, examined next.

**Prerequisites:** encapsulation, and how a switch forwards frames.

> [!tip] The analogy, and where it breaks
> A tape recorder on a phone line — the definitive record when two parties disagree about what was said. The analogy breaks because a modern switched network is not a party line: by default your recorder hears only your own calls, and you must arrange a deliberate tap or mirror to hear anyone else's. Capturing 'the network' is never automatic.

## Two Filters, Constantly Confused

There are two entirely different kinds of filter, applied at different times, and mixing them up is the most common capture mistake.

A **capture filter (BPF)** decides which packets are *recorded at all*. It is applied in the kernel, before packets reach the tool, using **BPF (Berkeley Packet Filter)** syntax. Because it runs in the kernel, it is efficient and it discards non-matching traffic permanently — what a capture filter drops is gone.

A **display filter** decides which of the *already-captured* packets are *shown*. It is applied by the analysis tool after capture, and it hides rather than discards — you can change it freely to view different subsets of the same capture.

```text
Capture filter (BPF):   kernel-level, decides what is RECORDED (discarded if not matched)
Display filter:         tool-level, decides what is SHOWN (data still there, just hidden)
```

The practical rule: **use a capture filter to control volume on a busy link** (you cannot record everything on a gigabit link, and recording irrelevant traffic buries the signal), and **use display filters to explore** what you captured. The danger of an overly narrow capture filter is that you discard the very packet that would have explained the problem — the retransmission, the reset, the error — so on anything but the busiest links, capture broadly and filter the display narrowly.

BPF capture-filter syntax is worth fluency because it appears everywhere — tcpdump, Wireshark, and many security tools share it:

```bash
sudo tcpdump -i eth0 'host 10.0.5.22 and tcp port 443'      # one host's HTTPS
sudo tcpdump -i eth0 'tcp[tcpflags] & tcp-syn != 0'          # SYN packets (find scans/handshakes)
sudo tcpdump -i eth0 'icmp or arp'                           # low-level troubleshooting
sudo tcpdump -i eth0 'net 192.168.1.0/24 and not port 22'    # a subnet, excluding SSH noise
```

## The Switched-Network Problem

Here is the obstacle that surprises beginners: **on a modern switched network, your capture tool sees very little.** A switch, by design, forwards frames only to the port leading to their destination (from the switching branch). Your host's interface therefore receives only frames addressed to it, plus broadcasts and multicasts — not the conversations between other hosts. Promiscuous mode makes your interface accept everything *it receives*, but the switch is not sending you other hosts' frames in the first place.

Getting the traffic you want to your capture point requires one of several techniques:

- **SPAN / mirror port** — configure the switch to copy traffic from one or more ports (or a whole VLAN) to the port where your capture host sits. This is the standard method and requires switch access.
- **Network tap** — a passive hardware device inserted into a link that copies all traffic to a monitor port, invisibly and without loss. Taps are the gold standard for reliability because they cannot drop traffic under load the way a busy SPAN port can.
- **Capture on an endpoint** — run the capture on one of the hosts in the conversation, where you naturally see its own traffic.
- **Capture at a chokepoint** — a router, firewall, or gateway sees all traffic crossing it, making it a natural capture location for anything that transits it.

```mermaid
flowchart TB
    subgraph "What a switch normally does"
        A["Host A"] --> SW["Switch"]
        SW -->|"A-to-B only to B's port"| B["Host B"]
        SW -.->|"nothing"| M["Your capture host"]
    end
    subgraph "How to capture it"
        SW2["Switch"] -->|"SPAN: copy A-B traffic"| M2["Capture host"]
        TAP["Inline tap"] -->|"copies all"| M3["Capture host"]
    end
```

This connects capture to sensor placement from the security-architecture branch: both are about getting the traffic you need to a point where you can observe it, and both are blind to traffic that never reaches that point.

## Security Implications

**Capture is the arbiter of truth, including for security.** When intrusion detection, application logs, and firewall logs disagree, the packet capture resolves what actually crossed the wire. It is the evidence of record for incident response, showing exactly what an attacker sent and received — subject, of course, to having captured at the right point.

**Capture exposes everything unencrypted, which is why encryption matters.** A capture reveals the full contents of any cleartext traffic — credentials, data, everything. This is the offensive value of a capture position and the defensive argument for encryption: the same capture that shows a plaintext password shows only ciphertext for a TLS session. Every "capture reveals cleartext" observation in this domain is an argument for encrypting the payload.

**Capturing requires privilege and is itself sensitive.** Promiscuous capture needs elevated privilege because it exposes other parties' traffic, and a capability to capture on a network is a capability to surveil it. Capture points, PCAP files, and mirror configurations are sensitive assets — a stored PCAP of production traffic may contain credentials and personal data and must be handled accordingly.

**Volume management is a real skill.** On a fast link, naive capture overwhelms storage and buries the relevant packets. Capture filters, ring buffers (rotating files), and snap length (capturing only headers when payloads are not needed) are the techniques that make capture practical at scale. A capture that fills the disk or that you cannot search is not evidence.

**The capture point defines what you can conclude.** A capture taken at the wrong location misses the traffic in question and can lead to false conclusions — "nothing was sent" may mean "nothing reached my capture point," which is a different statement. Stating where a capture was taken is part of stating what it proves, exactly as with sensor placement.

All capture described here must be performed only on networks and systems you own or are explicitly authorized to monitor. Capturing traffic exposes its contents, and doing so on networks you do not control is unlawful interception.

## Authorized Lab: Capture, Filter, and Mirror

Use a lab with a switch you can configure, two hosts generating traffic, and a capture host.

1. **Prove the switched-network blind spot.** From the capture host, put the interface in promiscuous mode and capture while two *other* hosts exchange traffic. Confirm you see almost none of it — the switch is not sending it to you.
2. **Configure a mirror.** Set up a SPAN/mirror port copying the two hosts' traffic to the capture host's port, and confirm you now see their full conversation.
3. **Capture filter versus display filter.** Capture broadly to a file, then apply different display filters to view subsets, confirming the data remains and only the view changes. Then capture with a narrow BPF filter and confirm that non-matching traffic is permanently absent from the file.
4. **Demonstrate the narrow-filter danger.** Capture with a filter so tight it excludes TCP resets, reproduce a connection failure, and confirm the capture cannot explain it because the relevant packet was filtered out — then re-capture broadly and find the reset.
5. **Practice BPF fluency.** Write capture filters for a single host's HTTPS, for SYN packets only, and for a subnet excluding SSH, confirming each records the intended traffic.
6. **Manage volume.** Capture with a ring buffer and a snap length, and confirm you can capture continuously without exhausting storage.
7. **Cleanup.** Remove the mirror configuration and delete lab capture files containing any sensitive data.

Expected interpretation:

```text
Promiscuous only  -> still see little; the switch does not forward others' frames
Mirror configured -> the full conversation now reaches the capture host
Capture vs display-> capture filter discards; display filter merely hides
Too-narrow filter -> the packet that explains the failure was discarded
BPF fluency       -> precise control of what is recorded on a busy link
```

## Crook → Operator → Root Checkpoint

- **Crook:** Explain what packet capture shows that other tools do not, what promiscuous mode does, and why a PCAP file is portable evidence.
- **Operator:** Distinguish a capture filter from a display filter and know when to use each; write BPF filters, and explain why a switched network requires a mirror, tap, or chokepoint to capture other hosts' traffic.
- **Root:** Explain why capture is the arbiter of truth and simultaneously a sensitive surveillance capability; argue why the capture point defines what you can conclude, and why every "capture reveals cleartext" fact is an argument for encrypting the payload.

---
> 🔼 Up: [[Network Analysis & Troubleshooting]]
