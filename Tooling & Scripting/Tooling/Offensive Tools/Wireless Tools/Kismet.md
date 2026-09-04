---
title: "Kismet"
aliases: ["kismet"]
tags: [tree/tooling, cyber/tooling/offensive/wireless/kismet, type/tool, difficulty/medium]
Domain: "[[Wireless Tools]]"
Color: "#708090"
---

# Kismet

> [!abstract] Note of [[Wireless Tools]]
> Kismet is the passive-discovery layer you run first: it transmits nothing, logs every AP, client and probe request it hears, and doubles as a wireless IDS. This note covers why it is invisible on the air, how it becomes the blue-team counter to the rest of this category, and why the probe requests it harvests are personal data.

Kismet is a passive wireless detector, sniffer, and wireless IDS. Unlike aircrack-ng's capture-and-attack pipeline, Kismet's job is **discovery and situational awareness**: it silently logs every AP, client, and probe request it hears across channels, builds a picture of the RF environment, and flags anomalies like rogue APs and deauth floods. It transmits nothing — pure listening.

> [!warning] Passive, but still scoped
> Kismet captures frames from every network in range, including bystanders. Handle captures as sensitive data, and operate only where you are authorized to monitor the spectrum.

## Parent Learning Order
aircrack-ng -> Kismet -> hcxtools

## The passive discovery layer you run first

> *Before you capture or crack anything on a wireless engagement, what do you need first?*
>
> Hold your answer — the section below is the response.

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

**How you'd spot it:** the hazard is visible in the data itself — a device's probe list naming home, workplace and hotel networks identifies a person, so treat a Kismet capture as personal data and scope its retention accordingly. Devices emitting no probe list at all are using MAC and probe randomisation, which is the defence working as intended.

## Security Implications

**Transmitting nothing makes Kismet undetectable — and makes it the defence.** Because it only listens, there is no frame for anyone to catch, which is why it is both the reconnaissance layer and a wireless IDS: the same passive visibility that maps a target's RF estate detects an attacker's deauth flood, evil twin or karma AP the instant it appears. The [[Wireless Reconnaissance & Defense]] argument that a rogue transmitter cannot hide is Kismet's operating principle from the other side.

**Probe requests are personal data, not just network data.** A device's probe list — home, workplace, an airport, a hotel — fingerprints and tracks the person carrying it, harvested with zero transmission. A Kismet capture therefore identifies bystanders and must be handled and retained as sensitive personal data, scoped to the authorised monitoring only. Modern MAC and SSID randomisation exists precisely to blunt this, and a device emitting no probe list is that defence working.

**A capture holds every network in range, including ones out of scope.** Passive does not mean unrestricted: Kismet records frames from neighbours and passers-by, so operating it requires authorisation to monitor the spectrum, and the logs are sensitive evidence rather than free reconnaissance.

All monitoring here is within an authorised scope; capturing bystanders' traffic and probe history carries the obligations of any personal-data collection.

## Summary

You should now be able to:

- Explain why Kismet runs *before* aircrack-ng, and why it is invisible on the air.
- Describe what Kismet shows about an environment, and how it doubles as a wireless IDS.
- Explain how probe requests fingerprint a device/person, and why that's both an offensive and a privacy concern.

---
> 🔼 Up: [[Wireless Tools]]
