---
title: "tcpdump"
aliases: ["tcpdump"]
tags: [tree/tooling, cyber/tooling/defensive/tcpdump, type/tool, difficulty/medium]
Domain: "[[Packet Analysis Tools]]"
Color: "#708090"
---

# tcpdump

tcpdump is the command-line packet capturer. No GUI, tiny footprint, on every Unix box — it captures frames straight from the interface with a kernel-level BPF filter and writes them to a `.pcap`. It's what you reach for on a headless server or mid-incident, and it pairs perfectly with Wireshark: **capture with tcpdump, analyse in Wireshark.**

> [!warning] Captured traffic is sensitive
> Captures contain credentials and personal data. Capture only where authorized, and protect the `.pcap`.

## Parent Learning Order
Wireshark -> tcpdump

## Deciding in the kernel which packets are worth keeping

Same layered packet as Wireshark — but tcpdump lives at the **capture** end, deciding (via a kernel BPF filter) which packets are worth saving at all.

Its filters target the lower layers efficiently (`host`, `port`, `tcp[13]` flag bits) because BPF runs *in the kernel* before the packet is ever copied to userspace — so a tight filter means the machine barely notices the capture. tcpdump's job is to grab exactly the right bytes with minimal overhead; deep decoding is Wireshark's job.

## The canonical capture, written to a file

The canonical capture: numeric, filtered, written to a file for later analysis.

```shell-session
operator@server:~$ sudo tcpdump -i eth0 -nn -w cap.pcap 'host 10.0.0.5 and port 443'
tcpdump: listening on eth0, link-type EN10MB (Ethernet)
^C  1428 packets captured
operator@server:~$ tcpdump -nn -r cap.pcap 'tcp[tcpflags] & tcp-syn != 0' | head
09:14:02.11 IP 10.0.0.44.51234 > 10.0.0.5.443: Flags [S], seq 12...
```

`-i` interface, `-nn` no name/port resolution, `-w` write pcap, `-r` read pcap, `-c N` stop after N, `-s0` full snaplen, `-A`/`-X` show ASCII/hex payload. The filter is **BPF** (same syntax as Wireshark's *capture* filter): `host`, `net`, `port`, `and`/`or`/`not`, and flag tests.

## How omitting -n pollutes your own capture

The `-n` flags are not cosmetic — omitting them makes tcpdump *pollute its own capture*:

```shell-session
# WITHOUT -n: tcpdump reverse-resolves every IP and every port
operator@server:~$ sudo tcpdump -i eth0 host 10.0.0.5
  ... tcpdump itself now emits DNS queries for 5.0.0.10.in-addr.arpa ...
  10.0.0.5.https > ...        ← "https" hides the real port number 443

# WITH -nn: no lookups, real numbers, no self-generated traffic
operator@server:~$ sudo tcpdump -i eth0 -nn host 10.0.0.5
  10.0.0.5.443 > ...
```

**The deliberate break:** without `-n` (IPs) and `-nn` (also ports), tcpdump does a **reverse-DNS lookup for every address it sees** — which is slow, and worse, those lookups are *new packets your capture host sends*, so on a busy link they appear in your own capture and can even feed back (an observer effect). Always capture with `-nn`. Two more Root essentials: on old versions the default **snaplen** truncated packets (use `-s0` for full payload), and `-w` writes **binary pcap** — piping it to `grep` fails, so write to a file and read it back with `-r` or open it in Wireshark. The division of labour is the whole point: tcpdump captures cheaply and precisely at the edge; Wireshark does the deep dissection afterward.

## Summary

You should now be able to:

- Why is tcpdump the right tool on a headless server, and what does its BPF filter do at the kernel level?
- Write a tcpdump command that saves only host-X:443 traffic to a pcap for later Wireshark analysis.
- Explain what omitting `-nn` does to your capture, and why `-w` output can't be grepped.

---
> 🔼 Up: [[Packet Analysis Tools]]
