---
title: "Wireless Tools"
tags: [tree/tooling, cyber/tooling/offensive/wireless, cyber/moc]
Domain: "[[Offensive Tools]]"
Color: "#708090"
---

# Wireless Tools

> [!warning] Authorized RF testing only
> Radio is a shared medium — capturing and injecting frames affects every device in range, and spectrum use is regulated. Test only networks you own or are authorized to assess, and prefer an isolated lab AP.

Wireless assessment operates one layer below IP: on 802.11 frames, channels, and the RF medium itself. This category holds the instruments that discover networks and clients, capture the material needed to attack WPA2/WPA3, and convert it for offline cracking. The attack almost never breaks the crypto — it captures a handshake or PMKID and moves the fight **offline** (see **WPA2 Security Testing** and **Hashcat**).

```mermaid
flowchart LR
    M["Monitor-mode interface"] --> D["Discover APs/clients (kismet, airodump)"]
    D --> C["Capture handshake / PMKID (aircrack-ng, hcxdumptool)"]
    C --> V["Convert (hcxtools) -> Hashcat -m 22000"]
    V --> R["Offline crack -> passphrase-policy finding"]
```

## Tools in this category

- [[aircrack-ng]]
- [[Kismet]]
- [[hcxtools]]

```text
Monitor mode -> discover -> capture handshake/PMKID -> convert -> crack offline -> report weak PSK
```

---
> 🔼 Up: [[Offensive Tools]]
