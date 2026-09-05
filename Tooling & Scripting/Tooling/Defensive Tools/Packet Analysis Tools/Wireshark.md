---
title: "Wireshark"
aliases: ["wireshark", "tshark"]
tags: [tree/tooling, cyber/tooling/defensive/wireshark, type/tool, difficulty/medium]
Domain: "[[Packet Analysis Tools]]"
Color: "#708090"
verified: 2026-09-05
---

# Wireshark

> [!abstract] Note of [[Packet Analysis Tools]]
> Wireshark decodes raw frames into named fields at every layer, reassembles streams, and lets you filter to the exact conversation you care about. It answers not "is the port open?" but "what did these two hosts actually say to each other?" — and, just as importantly, tells you where its answers are inference rather than fact.

> [!warning] Captured traffic is sensitive
> A capture can contain credentials, session tokens and personal data. Capture only where authorized, store `.pcap` files as evidence, and redact before sharing.

## Parent Learning Order
Wireshark -> tcpdump

**Prerequisites:** the layered model — Ethernet, IP, TCP/UDP — and enough TCP to know what a sequence number is for.

## Peeling nested layers and naming every field

> *A packet arrives as one run of bytes. How does Wireshark know that byte 34 is a TCP port?*
>
> Hold your answer — the section below is the response.

A packet is a set of **nested layers**, each wrapping the one above it, and Wireshark's whole job is to peel them apart and name every field.

It does this with a chain of **dissectors**, each of which reads its own header and then decides who goes next:

```text
offset 12   EtherType 0x0800  --> IPv4 dissector
offset 23   protocol   6      --> TCP dissector
offset 36   dst port   443    --> dissector table lookup --> TLS dissector
                                  (or a heuristic dissector, or whatever
                                   "Decode As" was told, in that order)
```

The Ethernet dissector reads the EtherType at offset 12; `0x0800` hands the rest to IPv4. The IPv4 dissector reads the protocol byte; `6` hands the payload to TCP. The TCP dissector reads the ports — and then consults a **dissector table** keyed on port number to decide what the payload is. So byte 34 is a TCP port only because two dissectors before it agreed that it would be.

That last handoff is the weak link, and knowing it is the difference between reading a capture and being misled by one. Port 80 is registered to HTTP, so anything on port 80 is handed to the HTTP dissector whether or not it is HTTP; a beacon on port 443 that is not TLS gets handed to the TLS dissector and shown as malformed. Wireshark has two answers. **Heuristic dissectors** volunteer: each is asked "does this payload look like yours?" and the first confident one claims it, which is how it finds HTTP on port 8081 without being told. And **Decode As** is the manual override — right-click, choose the protocol, and the dissector table is remapped for that port for this session. Reach for it the moment a protocol you recognise is displaying as `Data`.

> [!tip] The analogy, and where it breaks
> Wireshark is a transcript of a conversation. The analogy breaks on who wrote the transcript. A stenographer records what was said; Wireshark records what *reached the microphone* and then annotates it with conclusions of its own — "this was a retransmission", "a segment is missing" — that are not in the audio at all. Most analysis mistakes are made by reading Wireshark's annotations as if they were the wire.

## Display filters, fields, and the statistics that answer questions fastest

The two moves that do most of the work are **display filters** and **Follow Stream**. Right-click a packet → *Follow → TCP Stream* reassembles a whole conversation into one readable transcript rather than scattered packets.

```text
Display filter examples (applied to already-captured packets):
  ip.addr == 198.51.100.9 && tcp.port == 443
  http.request.method == "POST"
  tcp.flags.syn == 1 && tcp.flags.ack == 0      (SYN without ACK: scans, or new flows)
  tls.handshake.extensions_server_name           (which hostnames, via SNI)
```

`tshark` is the same engine on the command line, and it is where filters become answers. Six connections from the finance workstation to the attacker, printed with the field that matters:

```shell-session
analyst@vm:~$ tshark -r meridian.pcap -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' \
                -T fields -e frame.time_relative -e ip.src -e ip.dst -e tcp.dstport
1.000000000     10.10.10.14     198.51.100.9    443
61.000000000    10.10.10.14     198.51.100.9    443
121.000000000   10.10.10.14     198.51.100.9    443
181.000000000   10.10.10.14     198.51.100.9    443
241.000000000   10.10.10.14     198.51.100.9    443
301.000000000   10.10.10.14     198.51.100.9    443
```

Sixty seconds apart, to the interval. No payload was read and none needed to be — that is a beacon, and it is the same finding [[Zeek]] surfaces from `conn.log`, reached here from the packets themselves.

The built-in statistics answer the orienting questions before any filter is typed. *Protocol Hierarchy* gives the traffic mix, and an unexpected protocol at one percent is often the whole investigation. *Conversations* ranks who-talked-to-whom by bytes and duration, which is how exfiltration announces itself:

```shell-session
analyst@vm:~$ tshark -r meridian.pcap -q -z io,phs
eth              frames:21  bytes:1293
  ip             frames:21  bytes:1293
    udp          frames:2   bytes:184
      dns        frames:2   bytes:184
    tcp          frames:19  bytes:1109
      http       frames:1   bytes:137
analyst@vm:~$ tshark -r meridian.pcap -q -z conv,ip
10.10.10.14 <-> 198.51.100.9    18 frames   972 bytes   start 1.000   duration 300.03
10.10.10.14 <-> 10.10.20.10      2 frames   184 bytes   start 0.000   duration   0.01
10.10.10.14 <-> 203.0.113.20     1 frame    137 bytes   start 400.000 duration   0.00
```

Encryption removes the payload, not the metadata. The TLS ClientHello is sent in clear, so the destination hostname and a fingerprint of the client's TLS stack are both readable from an encrypted session:

```shell-session
analyst@vm:~$ tshark -r tls.pcap -Y tls
1  0.000000  10.10.10.14 -> 198.51.100.9  TLSv1  131  Client Hello (SNI=cdn.evil.example)
analyst@vm:~$ tshark -r tls.pcap -T fields -e tls.handshake.ja3_full -e tls.handshake.ja3
771,4865,0,,    1e7c622032b0cb79401b0f7be3793a1a
```

For actual plaintext you need the keys. Wireshark reads an `SSLKEYLOGFILE` — the per-session secrets a browser or any NSS/OpenSSL client will write when that environment variable is set — and decrypts the capture with them. This is a supported debugging path, not an attack, and it is worth connecting to [[Volatility]]: those same session keys live in process memory, so a memory image plus a capture can decrypt traffic that was properly encrypted on the wire.

## Capture filter versus display filter

The single most common Wireshark confusion is **capture filter vs display filter** — they look similar, behave oppositely, and are not even the same language. Each rejects the other's syntax outright:

```shell-session
analyst@vm:~$ tshark -r meridian.pcap -f 'tcp.port == 443'
tshark: Only read filters, not capture filters, can be specified when reading a capture file.
analyst@vm:~$ tshark -r meridian.pcap -Y 'tcp port 443'
tshark: "port" was unexpected in this context.
    tcp port 443
```

```text
CAPTURE filter (BPF, set BEFORE capturing):   host 198.51.100.9
  -> only matching packets are ever SAVED. Everything else is gone forever.

DISPLAY filter (set AFTER capturing):         ip.addr == 198.51.100.9
  -> hides non-matching packets from VIEW. They are still in the .pcap; clear
     the filter and they reappear.
```

**The deliberate break:** an analyst sets a *capture* filter of `host 198.51.100.9` to "focus", runs the capture, and later realises the attacker pivoted to a second address — but those packets were **never saved** and are unrecoverable. The safe habit is to capture *broad*, with little or no capture filter, and narrow afterwards with *display* filters, which are non-destructive and reversible. Capture filters exist for a real reason — on a saturated link, filtering in the kernel is the difference between a clean capture and a lossy one — so the judgement is about link rate, not preference: filter at capture time only when the volume forces you to, and then filter as loosely as the volume allows.

**How you'd spot it:** the syntax gives it away, which is exactly why the two differ. `host 198.51.100.9` is BPF and filters at capture time; `ip.addr == 198.51.100.9` is a display filter and is reversible. In a saved file, the tell is a *Conversations* list containing a single host — real traffic is never that tidy.

## The annotations that are Wireshark's opinion, not the wire

Some of the most useful things Wireshark tells you are not in the packets at all. `[TCP Retransmission]`, `[TCP Out-Of-Order]`, `[TCP Previous segment not captured]`, `[TCP ZeroWindow]` are **expert info**: conclusions the TCP dissector reaches by comparing sequence numbers across the frames *it was given*. No flag on the wire says "retransmission." Wireshark infers it, and it is careful enough to say so:

```shell-session
analyst@vm:~$ tshark -r rtx.pcap -T fields -e frame.number -e tcp.seq -e _ws.expert.message
1  1
2  1   This frame is a (suspected) retransmission
```

That word `suspected` is the whole lesson. The same inference machinery misfires when the *capture* is incomplete rather than the network. Here is one TCP stream of four segments, written to two files — the complete capture, and the same traffic with one packet removed to simulate a sensor that dropped it:

```shell-session
analyst@vm:~$ tshark -r full.pcap -T fields -e frame.number -e tcp.seq -e _ws.expert.message
1  1
2  101
3  201
4  301
analyst@vm:~$ tshark -r gap.pcap -T fields -e frame.number -e tcp.seq -e _ws.expert.message
1  1
2  201   Previous segment(s) not captured (common at capture start)
3  301
```

**The deliberate break:** the network behaved identically in both runs. Every segment was sent, in order, once. The second file reports a problem that did not happen, because the *sensor* missed a packet and Wireshark can only reason about what it received. An analyst who reads that line as "the network dropped a segment" will spend the afternoon investigating a link that is fine. Retransmission storms and out-of-order floods in a capture are far more often a symptom of an over-subscribed span port, a busy capture host, or a snaplen truncation than of the network under investigation — and Wireshark's own wording, *not captured*, is telling you which side of the microphone the problem is on.

**How you'd spot it:** check the capture before you diagnose the network. `capinfos` reports the file's drop count where the format records one; `tshark`'s own run reports dropped packets on a live capture; and a capture full of retransmissions with no corresponding application slowness is the classic profile of a lossy sensor rather than a lossy link. Capturing at both ends of the path settles it in one step: a segment present at the sender and absent at the receiver was lost by the network, and a segment absent from both captures but acknowledged by the receiver was lost by your capture.

## Security Implications

A `.pcap` is credential material. Anything unencrypted is in it verbatim — HTTP basic auth, session cookies, SNMP community strings, legacy protocol passwords — and anything encrypted is still a full record of who contacted whom, when and how much. Treat capture files as the most sensitive artifact an incident produces: encrypt at rest, restrict access, and never paste one into a ticket or a chat channel that a wider audience can read. Where a capture must be shared, `tracewrangler` and similar tools sanitise addresses and payloads; deleting the file when the investigation closes is a control, not an omission.

Wireshark itself is a large attack surface, and this is not theoretical — its dissector code parses thousands of protocols from untrusted input and has a long history of memory-safety advisories. Opening a hostile `.pcap` is running an attacker's input through that code, which is why the project separates privileges: `dumpcap` is the small program that touches the interface, and the dissection engine is meant to run as an ordinary user. The tool says so itself:

```shell-session
analyst@vm:~$ sudo tshark -r suspicious.pcap
Running as user "root" and group "root". This could be dangerous.
```

Capture with `dumpcap` or `tcpdump`, analyse unprivileged, and analyse hostile captures in a VM. The GUI on a jump host with domain credentials is the wrong place to open evidence from a compromised network.

The capture point defines the truth you get, and every deployment leaks in a specific direction. A span port drops silently under load; a network tap does not, which is why taps are used for evidence. A switch shows one host only its own traffic, so capturing from a workstation sees a fraction of the segment. Encrypted tunnels — VPN, SSH, DNS over HTTPS — collapse whole conversations into one opaque flow. None of these are Wireshark limitations, but all of them become Wireshark conclusions if you forget where the microphone was.

## Summary

You should now be able to:

- Explain the dissector chain that makes byte 34 a TCP port, and use heuristic dissectors and *Decode As* when the port lies.
- Read one conversation out of thousands of packets with display filters, `tshark -T fields`, Follow Stream and the statistics views, and pull SNI and JA3 out of an encrypted session.
- Explain the difference between a capture filter and a display filter, and when capturing narrow is nonetheless correct.
- Explain why expert-info flags are inference, demonstrate a capture gap manufacturing a problem that did not happen, and say how to tell a lossy sensor from a lossy link.

---
> 🔼 Up: [[Packet Analysis Tools]]
