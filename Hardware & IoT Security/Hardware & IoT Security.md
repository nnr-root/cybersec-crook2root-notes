---
title: Hardware & IoT Security
aliases:
  - Hardware & IoT Security Hub
tags:
  - tree/hardware
  - cyber/moc
Domain:
  - "[[Cyber Security]]"
Color: "#9A6324"
---

# 🔌 Hardware & IoT Security

> [!abstract] The Domain
> Attacking physical devices — firmware extraction, embedded-system exploitation, hardware debug interfaces, and radio protocol analysis. Part of the domain map at [[Cyber Security]].

## Learning Path

```mermaid
flowchart LR
    A["🔌 Hardware & IoT Security"]
    A --> B["💾 Firmware Analysis & Extraction"]
    A --> C["🔧 Hardware Interfaces & Side-Channel"]
    A --> D["📡 Radio & Wireless Protocols"]
    style A fill:#111,stroke:#9A6324,color:#9A6324
```

1. [[Firmware Analysis & Extraction]] — extracting and reversing firmware blobs; hardcoded credentials; vulnerable update mechanisms
2. [[Hardware Interfaces & Side-Channel]] — JTAG/UART/SPI debugging interfaces; fault injection; power and EM side-channel
3. [[Radio & Wireless Protocols]] — SDR-based analysis; Zigbee, Z-Wave, 433 MHz; replay and injection attacks

---
> 🌐 Back to the domain map: [[Cyber Security]]
