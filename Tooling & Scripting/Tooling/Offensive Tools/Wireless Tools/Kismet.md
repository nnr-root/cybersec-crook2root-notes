---
title: "Kismet"
aliases: ["kismet"]
tags: [tree/tooling, cyber/tooling/offensive/wireless/kismet, type/tool, difficulty/medium]
Domain: "[[Wireless Tools]]"
Color: "#708090"
---

# Kismet

Kismet is a passive wireless detector, sniffer, and wireless IDS. Unlike aircrack-ng's capture-and-attack pipeline, Kismet's job is **discovery and situational awareness**: it silently logs every AP, client, and probe request it hears across channels, builds a picture of the RF environment, and flags anomalies like rogue APs and deauth floods. It transmits nothing — pure listening.

> [!warning] Passive, but still scoped
> Kismet captures frames from every network in range, including bystanders. Handle captures as sensitive data, and operate only where you are authorized to monitor the spectrum.

## Parent Learning Order
aircrack-ng -> Kismet -> hcxtools

## The passive discovery layer you run first

Before you capture or crack anything, you have to *know what's there*. Kismet is the passive-discovery layer.

On the map, Kismet is the bottom band — you run it **first** to map the RF environment (which SSIDs, which BSSIDs, which channels, which clients), then hand targets to aircrack-ng/hcxtools. Its defining property: it **injects nothing**. It only listens, hopping channels and logging every frame, which makes it invisible on the air and equally useful as a *defensive* wireless IDS — it detects the very deauth floods and rogue APs that the offensive tools produce.

## Monitor mode, and the live web UI

Point it at a monitor-mode interface; drive it from the web UI:

```shell-session
operator@kali:~$ sudo kismet -c wlan0mon
[INFO] Detected new 802.11 Wi-Fi access point 00:00:5E:00:53:C0 "MERIDIAN-CORP" ch 6
[INFO] Detected new 802.11 Wi-Fi device 00:00:5E:00:53:0E (client)
[INFO] Probe request from 00:00:5E:00:53:0E for "HomeNet-5G"
[ALERT] BCASTDISCON: possible deauth flood on 00:00:5E:00:53:C0
```

The web UI (`http://localhost:2501`) shows live APs, associated clients, signal strength (for direction-finding/wardriving), and alerts. It logs to `.kismet` (SQLite) and pcapng for later analysis. As a WIDS, its alerts (`DEAUTHFLOOD`, rogue-AP, karma-attack) are the blue-team side of everything in this category.

## Probe requests, and what phones announce about people

The most surprising Kismet capability isn't about networks — it's about **people**, and it's entirely passive:

```shell-session
[Probe] client 00:00:5E:00:53:0E →  "MERIDIAN-CORP"
[Probe] client 00:00:5E:00:53:0E →  "HomeNet-5G"
[Probe] client 00:00:5E:00:53:0E →  "SFO_Airport_WiFi"
[Probe] client 00:00:5E:00:53:0E →  "Marriott_Guest"
```

**The deliberate break:** those are **probe requests** — a phone shouting the names of Wi-Fi networks it has connected to before, looking for them. Kismet harvests them without transmitting anything, and the *list itself* is a fingerprint: it reveals where this device (person) lives, works, and has travelled — enough to identify and track an individual across locations. Beginners think Kismet "just finds Wi-Fi"; its deeper power (and privacy hazard) is that clients leak their history for free, which is why modern phones randomize MACs and stop broadcasting saved SSIDs. This also flips Kismet into a defensive tool: the same passive visibility detects an attacker's deauth flood or an evil-twin AP the instant it appears. Kismet doesn't attack — it *sees*, and seeing is both reconnaissance and defense.

## Summary

You should now be able to:

- Why do you run Kismet *before* aircrack-ng, and why is it invisible on the air?
- What does Kismet show you about an environment, and how does it double as a wireless IDS?
- Explain how probe requests fingerprint a device/person, and why that's both an offensive and a privacy concern.

---
> 🔼 Up: [[Wireless Tools]]
