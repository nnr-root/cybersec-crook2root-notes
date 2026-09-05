---
title: "tcpdump"
aliases: ["tcpdump"]
tags: [tree/tooling, cyber/tooling/defensive/tcpdump, type/tool, difficulty/medium]
Domain: "[[Packet Analysis Tools]]"
thread-exempt:
  - "9.100.51.198: not an address — the reversed in-addr.arpa name for 198.51.100.9, the query tcpdump emits about its own filter target"
Color: "#708090"
verified: 2026-09-05
---

# tcpdump

> [!abstract] Note of [[Packet Analysis Tools]]
> tcpdump captures frames straight from the interface through a filter that runs *in the kernel*, and writes them to a `.pcap`. It is what you reach for on a headless server or mid-incident, and it pairs with [[Wireshark]] exactly: capture with tcpdump, analyse in Wireshark.

tcpdump is the command-line packet capturer. No GUI, tiny footprint, on every Unix box — it captures frames straight from the interface with a kernel-level BPF filter and writes them to a `.pcap`. It's what you reach for on a headless server or mid-incident, and it pairs perfectly with Wireshark: **capture with tcpdump, analyse in Wireshark.**

> [!warning] Captured traffic is sensitive
> Captures contain credentials and personal data. Capture only where authorized, and protect the `.pcap`.

## Parent Learning Order
Wireshark -> tcpdump

**Prerequisites:** [[Wireshark]] first — tcpdump's filters are the same BPF language as Wireshark's *capture* filters, and the division of labour only makes sense once you have seen the analysis end.

## Deciding in the kernel which packets are worth keeping

> *Wireshark and tcpdump look at the same packet. What does tcpdump decide that Wireshark never gets to?*
>
> Hold your answer — the section below is the response.

Same layered packet as Wireshark — but tcpdump lives at the **capture** end, deciding (via a kernel BPF filter) which packets are worth saving at all.

Its filters target the lower layers efficiently (`host`, `port`, `tcp[13]` flag bits) because BPF runs *in the kernel* before the packet is ever copied to userspace — so a tight filter means the machine barely notices the capture. tcpdump's job is to grab exactly the right bytes with minimal overhead; deep decoding is Wireshark's job.

## The canonical capture, written to a file

The canonical capture: numeric, filtered, written to a file for later analysis.

```shell-session
operator@server:~$ sudo tcpdump -i eth0 -nn -w cap.pcap 'host 198.51.100.9 and port 443'
tcpdump: listening on eth0, link-type EN10MB (Ethernet)
^C  1428 packets captured
operator@server:~$ tcpdump -nn -r cap.pcap 'tcp[tcpflags] & tcp-syn != 0' | head
09:14:02.11 IP 10.10.10.14.51234 > 198.51.100.9.443: Flags [S], seq 12...
```

`-i` interface, `-nn` no name/port resolution, `-w` write pcap, `-r` read pcap, `-c N` stop after N, `-s0` full snaplen, `-A`/`-X` show ASCII/hex payload. The filter is **BPF** (same syntax as Wireshark's *capture* filter): `host`, `net`, `port`, `and`/`or`/`not`, and flag tests.

## What a filter compiles to, and what it quietly excludes

"BPF runs in the kernel" is worth making concrete, because the compiled program explains a class of missing data. `-d` disassembles the filter instead of running it:

```shell-session
operator@server:~$ tcpdump -d 'tcp port 443'
(000) ldh      [12]                       ; EtherType
(001) jeq      #0x86dd          jt 2  jf 8   ; IPv6? ... else try IPv4
(008) jeq      #0x800           jt 9  jf 19  ; IPv4?
(009) ldb      [23]                       ; IP protocol byte
(010) jeq      #0x6             jt 11 jf 19 ; TCP?
(011) ldh      [20]                       ; flags + fragment offset
(012) jset     #0x1fff          jt 19 jf 13 ; fragment offset != 0 -> REJECT
(013) ldxb     4*([14]&0xf)               ; IHL: header length is variable
(014) ldh      [x + 14]                   ; source port, at a computed offset
(015) jeq      #0x1bb           jt 18 jf 16
(016) ldh      [x + 16]                   ; destination port
(017) jeq      #0x1bb           jt 18 jf 19
(018) ret      #262144                    ; accept, snaplen bytes
(019) ret      #0                         ; reject
```

Twenty instructions, and two of them are the lesson. Line 013 loads the IP header length from the packet and computes the port offsets from it, which is why hand-written offset filters like `tcp[13]` are relative to the TCP header rather than to the frame — IP options move everything. And line 012 rejects any packet whose fragment offset is non-zero, because only the *first* fragment of a fragmented datagram carries the TCP header, and therefore the ports the filter needs. Every later fragment is dropped by the filter.

That is not a corner case in a capture you are filtering tightly:

```shell-session
operator@server:~$ tcpdump -n -r frag.pcap | wc -l                # everything in the file
3
operator@server:~$ tcpdump -n -r frag.pcap 'tcp port 443' | wc -l # the same file, filtered
1
operator@server:~$ tcpdump -n -r frag.pcap
12:00:00.000000 IP 10.10.10.14.51234 > 198.51.100.9.443: Flags [P.], length 980
12:00:00.001000 IP 10.10.10.14 > 198.51.100.9: ip-proto-6
12:00:00.002000 IP 10.10.10.14 > 198.51.100.9: ip-proto-6
```

One 2,000-byte TCP segment, three fragments on the wire, and a port filter that saves one of them — two thirds of the payload gone, with nothing in the output to say so. Where fragmentation is plausible, add `or ip[6:2] & 0x1fff != 0` to keep the trailing fragments, or capture on `host` rather than `port`. This is also the shape of a real evasion: an attacker who fragments deliberately splits the signature across packets that a port-scoped sensor never assembles.

## Running a capture that outlives your session

A capture you start during an incident usually needs to survive longer than your patience and shorter than your disk:

```shell-session
operator@server:~$ sudo tcpdump -i eth0 -nn -s0 -Z tcpdump \
    -w /var/captures/meridian-%Y%m%d-%H%M%S.pcap -G 3600 -C 100 -W 24 \
    'host 198.51.100.9 or port 445'
```

`-G 3600` rotates on time, `-C 100` on size in millions of bytes, and `-W 24` caps the set at twenty-four files so the ring overwrites instead of filling the filesystem — a capture that fills `/var` on a production host is the classic self-inflicted outage of this tool. `-Z tcpdump` drops privileges to that user immediately after the socket is opened, which most distributions now do by default. `-s0` takes the full packet; the old default snaplen truncated payloads and is still the reason a capture sometimes cuts off at a suspiciously round number of bytes.

## How omitting -n pollutes your own capture

The `-n` flags are not cosmetic — omitting them makes tcpdump *pollute its own capture*:

```shell-session
# WITHOUT -n: tcpdump reverse-resolves every IP and every port
operator@server:~$ sudo tcpdump -i eth0 host 198.51.100.9
  ... tcpdump itself now emits DNS queries for 9.100.51.198.in-addr.arpa ...
  198.51.100.9.https > ...        ← "https" hides the real port number 443

# WITH -nn: no lookups, real numbers, no self-generated traffic
operator@server:~$ sudo tcpdump -i eth0 -nn host 198.51.100.9
  198.51.100.9.443 > ...
```

**The deliberate break:** without `-n` (IPs) and `-nn` (also ports), tcpdump does a **reverse-DNS lookup for every address it sees** — which is slow, and worse, those lookups are *new packets your capture host sends*, so on a busy link they appear in your own capture and can even feed back (an observer effect). Always capture with `-nn`. Two more Root essentials: on old versions the default **snaplen** truncated packets (use `-s0` for full payload), and `-w` writes **binary pcap** — piping it to `grep` fails, so write to a file and read it back with `-r` or open it in Wireshark. The division of labour is the whole point: tcpdump captures cheaply and precisely at the edge; Wireshark does the deep dissection afterward.

**How you'd spot it:** your own capture shows it — reverse lookups to `in-addr.arpa`, sourced from the capture host, appearing in step with the traffic you are watching. If names are printing rather than addresses, `-nn` was missing. Payloads that stop dead at 68 or 96 bytes are the other one, and that is snaplen rather than a truncated conversation.

## Security Implications

The capture file is the sensitive artifact, not the command. Anything unencrypted on the link is written to disk verbatim — credentials, cookies, tokens — so a `.pcap` in `/tmp` on a shared host is a credential store with world-readable permissions. Write captures to a restricted directory, and delete them when the investigation closes.

Capturing requires privilege, and that privilege is the exposure. Reading raw frames needs `CAP_NET_RAW`, and tcpdump parses hostile input to *print* it, which is where its own historical vulnerabilities have lived — its printers, not its capture path. Hence the split the tool ships with: open the socket, then `-Z` to an unprivileged user, and never decode an untrusted capture as root. Putting an interface into promiscuous mode is itself a visible act on some networks and changes what the host processes, so on a compromised machine a capture is not a passive observation.

The footprint runs both ways, which is the reason the offensive tree uses this tool too. An attacker with a foothold runs tcpdump for exactly the reasons you do, and it is available on nearly every Unix host by default. Defensively, the tells are specific: a process holding a raw socket, an interface flipped to promiscuous mode (`ip link` shows `PROMISC`), and a growing file in a temporary directory. [[Sysmon]]'s Linux build and `auditd` both record the process execution, and an unexpected `tcpdump -w` on a server is worth an alert on its own.

## Summary

You should now be able to:

- Explain why tcpdump is the right tool on a headless server, and what its BPF filter does at the kernel level.
- Write a tcpdump command that saves only host-X:443 traffic to a pcap for later Wireshark analysis.
- Read a compiled BPF program, explain why a port filter silently discards every fragment after the first, and write a rotating capture that cannot fill the disk.
- Explain what omitting `-nn` does to your capture, why `-w` output can't be grepped, and what a running capture looks like to a defender.

---
> 🔼 Up: [[Packet Analysis Tools]]
