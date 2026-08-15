---
title: "Packet Analysis Tools"
tags: [tree/tooling, cyber/tooling/defensive/packet-analysis, cyber/moc]
Domain: "[[Defensive Tools]]"
Color: "#708090"
---

# Packet Analysis Tools

Capture and inspect wire evidence while preserving timestamps, interfaces, snap length, loss statistics, and cryptographic provenance.

```mermaid
flowchart LR
    N["Network tap / interface"] --> C["Capture"]
    C --> F["Display filters and protocol decode"]
    F --> E["Exported evidence"]
```

- [[Wireshark]]
- [[tcpdump]]

```shell-session
analyst@sensor:~$ sha256sum capture.pcapng
891d...  capture.pcapng
```

---
> 🔼 Up: [[Defensive Tools]]
