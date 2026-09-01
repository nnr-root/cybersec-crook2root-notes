---
title: "aircrack-ng"
aliases: ["aircrack-ng suite", "airodump-ng"]
tags: [tree/tooling, cyber/tooling/offensive/wireless/aircrack, type/tool, difficulty/medium]
Domain: "[[Wireless Tools]]"
Color: "#708090"
---

# aircrack-ng

aircrack-ng is the classic 802.11 assessment suite. It is not one program but a **pipeline**: put the card in monitor mode (`airmon-ng`), survey the air and capture frames (`airodump-ng`), optionally nudge a client to reconnect (`aireplay-ng`), and crack the captured WPA2 handshake against a wordlist (`aircrack-ng`). The crypto is never broken over the air — the handshake is captured and attacked **offline**.

> [!warning] Authorized RF testing only
> Deauthentication actively knocks clients off the network — a deauth against a production WLAN is a denial of service. Use only on an owned/authorized AP.

## Parent Learning Order
aircrack-ng -> Kismet -> hcxtools

## You cannot break WPA2, so you capture the handshake

> *You cannot break WPA2 encryption over the air. What do you take instead?*
>
> Hold your answer — the section below is the response.

You cannot break WPA2 encryption over the air. What you *can* do is capture the **4-way handshake** — the brief exchange when a client joins, which contains a value derived from the passphrase — and then attack that value offline.

aircrack-ng is method **A** on the map: capture the handshake (deauthing a client to force a reconnect if you're impatient), then crack offline. The whole security of WPA2-PSK reduces to one question the handshake lets you ask offline: *is the passphrase in my wordlist?*

## The pipeline from monitor mode to offline crack

The pipeline, start to finish:

```shell-session
operator@kali:~$ sudo airmon-ng start wlan0                 # → wlan0mon (monitor mode)
operator@kali:~$ sudo airodump-ng wlan0mon                  # survey: find the target BSSID + channel
 BSSID              CH  ENC   ESSID
 00:00:5E:00:53:C0   6  WPA2  MERIDIAN-CORP
operator@kali:~$ sudo airodump-ng -c 6 --bssid 00:00:5E:00:53:C0 -w cap wlan0mon
 ... [ WPA handshake: 00:00:5E:00:53:C0 ]   ← captured!
operator@kali:~$ sudo aireplay-ng --deauth 3 -a 00:00:5E:00:53:C0 wlan0mon   # (force a reconnect)
operator@kali:~$ aircrack-ng -w rockyou.txt cap-01.cap
 KEY FOUND! [ Summer2024! ]
```

`airmon-ng` → monitor mode; `airodump-ng` → survey + capture; `aireplay-ng --deauth` → force a handshake; `aircrack-ng -w` → offline crack. Modern workflow often exports the capture and cracks with `hashcat -m 22000` on a GPU instead.

## Why identical captures crack in seconds, or never

Capturing the handshake is the easy part; whether it ever cracks is entirely the passphrase:

```shell-session
# weak PSK
operator@kali:~$ aircrack-ng -w rockyou.txt corp-cap-01.cap
KEY FOUND! [ Summer2024! ]     (23 s)

# strong PSK — SAME captured handshake
operator@kali:~$ aircrack-ng -w rockyou.txt guest-cap-01.cap
Passphrase not in dictionary          (exhausted 14 million candidates)
```

**The deliberate break:** both handshakes were captured identically and in seconds — but the corporate WLAN's `Summer2024!` falls to rockyou instantly while the guest network's 20-character random PSK never appears in any wordlist. "I captured the handshake" is **not** "I cracked the network" — beginners celebrate the `WPA handshake` line and forget that the offline crack still has to *find* the passphrase, and a strong one is computationally out of reach. The finding a report should carry is therefore **passphrase policy**, not "WPA2 is broken." Two operational cautions the map flags: the `--deauth` that forces a fast handshake is a real **DoS** against those clients (owned/authorized APs only), and you can also just *wait* passively for a natural join to avoid disrupting anyone.

**How you'd spot it:** the `WPA handshake:` line means capture succeeded and says nothing whatever about the passphrase. The number that matters comes afterwards — keyspace against your rate. A long random passphrase exhausts the wordlist and reports nothing, and the honest finding is "handshake captured, passphrase not recovered within the engagement window", never a pass.

## Summary

You should now be able to:

- Explain why WPA2 cracking is an *offline* attack, and what the 4-way handshake provides.
- Walk the airmon → airodump → aireplay → aircrack pipeline, and say what each step does.
- Explain why capturing a handshake isn't cracking a network, and what really determines whether it falls.

---
> 🔼 Up: [[Wireless Tools]]
