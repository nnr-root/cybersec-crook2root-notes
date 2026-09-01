---
title: "Wireshark"
aliases: ["wireshark"]
tags: [tree/tooling, cyber/tooling/defensive/wireshark, type/tool, difficulty/medium]
Domain: "[[Packet Analysis Tools]]"
Color: "#708090"
---

# Wireshark

Wireshark is the deep-analysis packet dissector — the GUI that takes raw frames and decodes every layer into human-readable fields, reassembles TCP streams, and lets you filter to the exact conversation you care about. It is how you *understand* traffic: not "is the port open?" but "what did these two hosts actually say to each other?"

> [!warning] Captured traffic is sensitive
> A capture can contain credentials, tokens, and personal data. Capture only where authorized, store `.pcap` files as sensitive evidence, and redact before sharing.

## Parent Learning Order
Wireshark -> tcpdump

## Peeling nested layers and naming every field

A packet is a set of **nested layers**, each wrapping the one above it. Wireshark's whole job is to peel them apart and name every field.

Read the diagram: Ethernet wraps IP wraps TCP wraps the payload. Wireshark decodes all of them at once and lets a **display filter** target any field at any layer — `ip.addr`, `tcp.flags.syn`, `http.request`. Once you see traffic as addressable fields rather than a byte blur, analysis becomes "filter to the layer/field that answers my question."

## Display filters and Follow Stream

The two moves that do 80% of the work: **display filters** and **Follow Stream**.

```text
Display filter examples (apply to already-captured packets):
  ip.addr == 198.51.100.9 && tcp.port == 443
  http.request.method == "POST"
  tcp.flags.syn == 1 && tcp.flags.ack == 0     (SYN scans)
  tls.handshake.extensions_server_name          (which hostnames via SNI)
```

Right-click a packet → **Follow → TCP Stream** reassembles the whole conversation into one readable transcript (the request and response, not scattered packets). *Statistics → Conversations* ranks who-talked-to-whom by bytes — the fastest way to spot exfiltration or a beacon. *Statistics → Protocol Hierarchy* shows the traffic mix at a glance.

## Capture filter versus display filter

The single most common Wireshark confusion is **capture filter vs. display filter** — they look similar and behave oppositely:

```text
CAPTURE filter (BPF, set BEFORE capturing):   host 198.51.100.9
  → only matching packets are ever SAVED. Everything else is gone forever.

DISPLAY filter (set AFTER capturing):         ip.addr == 198.51.100.9
  → hides non-matching packets from VIEW. They're still in the .pcap; clear the
    filter and they reappear.
```

**The deliberate break:** an analyst sets a *capture* filter of `host 198.51.100.9` to "focus," runs the capture, and later realises the attacker pivoted to `10.10.10.9` — but those packets were **never saved** and are unrecoverable. The safe habit is: capture *broad* (little or no capture filter), then narrow with *display* filters, which are non-destructive and reversible. The two even use **different syntax** (BPF `host 198.51.100.9` for capture; Wireshark `ip.addr == 198.51.100.9` for display), which is the tell that they're different mechanisms. One more Root reality: Wireshark shows TLS as opaque ciphertext unless you supply the session keys (via `SSLKEYLOGFILE`) — you can see *that* two hosts did TLS and to which SNI, but not the plaintext, without the keys.

## Summary

You should now be able to:

- Why does Wireshark show a packet as nested layers, and what does a display filter target?
- You need to read one HTTP conversation out of thousands of packets. What two features get you there?
- Explain the difference between a capture filter and a display filter, and why capturing broad then filtering the view is the safe habit.

---
> 🔼 Up: [[Packet Analysis Tools]]
