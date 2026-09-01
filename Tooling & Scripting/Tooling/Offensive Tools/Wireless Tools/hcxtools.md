---
title: "hcxtools"
aliases: ["hcxtools", "hcxdumptool", "hcxpcapngtool"]
tags: [tree/tooling, cyber/tooling/offensive/wireless/hcxtools, type/tool, difficulty/hard]
Domain: "[[Wireless Tools]]"
Color: "#708090"
---

# hcxtools

hcxtools (with its capture companion `hcxdumptool`) is the modern WPA-capture toolkit. Its headline capability is the **PMKID attack**: against many APs you can obtain crackable material from a *single frame* during association — **no connected client and no deauth required**. hcxtools then converts captures into the `22000` hash format Hashcat consumes, making it the bridge from radio to GPU.

> [!warning] Authorized RF testing only
> Capturing PMKIDs interacts with the target AP. Use only on owned/authorized networks; the output feeds offline cracking — report passphrase weakness, not the passphrase.

## Parent Learning Order
aircrack-ng -> Kismet -> hcxtools

## Clientless capture, and the limitation it removes

hcxtools is method **B** on the map — the clientless capture that fixed the biggest limitations of the aircrack handshake approach.

The old way (aircrack) needs a *connected client* to capture a handshake, and often a *deauth* to force one — noisy, and a DoS. The PMKID attack skips all that: hcxdumptool simply asks the AP to associate, and many APs helpfully include a **PMKID** (a hash derived from the passphrase) in that very first response — no client, no deauth, no disruption. Same offline crack at the end, but a quieter, cleaner capture.

## Capture, convert, crack

Capture with hcxdumptool, convert with hcxpcapngtool, crack with Hashcat:

```shell-session
operator@kali:~$ sudo hcxdumptool -i wlan0mon -o cap.pcapng --enable_status=1
[AP] AA:BB:CC:11:22:33  CorpWiFi   PMKID captured
operator@kali:~$ hcxpcapngtool -o hash.hc22000 cap.pcapng
1 PMKID(s) written to hash.hc22000
operator@kali:~$ hashcat -m 22000 hash.hc22000 rockyou.txt
...:CorpWiFi:Summer2024!
```

The `22000` mode is the modern unifier: it cracks **both** PMKIDs *and* captured 4-way handshakes, so whatever you captured (method A or B), the offline step is identical. hcxpcapngtool also filters, deduplicates, and reports which networks yielded usable material.

## When there is no PMKID to take

PMKID is a huge convenience — but it is not universal:

```shell-session
operator@kali:~$ sudo hcxdumptool -i wlan0mon -o cap.pcapng --enable_status=1
[AP] AA:BB:CC:11:22:33  CorpWiFi     PMKID captured        ✓
[AP] DD:EE:FF:44:55:66  GuestNet     associating... no PMKID in response   ✗
```

**The deliberate break:** `CorpWiFi` leaked a PMKID on association, but `GuestNet` did **not** — because the PMKID is only present when the AP caches it (a roaming/802.11r-related feature), and plenty of APs simply don't include one. A beginner assumes PMKID always works and gives up when an AP is silent; the right move is to **fall back to method A** (capture a real 4-way handshake from a connecting client) — which is why the `-m 22000` format existing for *both* matters so much. And the wall from the whole category still stands: whether it's a PMKID or a handshake, the offline crack only beats a **weak** passphrase — `Summer2024!` falls, a 20-character random PSK does not. hcxtools made *capture* clientless and quiet; it did nothing to make a strong passphrase crackable, so the reportable finding remains passphrase strength, not the tool's cleverness.

## Summary

You should now be able to:

- How does the PMKID attack improve on the aircrack handshake method?
- Walk the hcxdumptool → hcxpcapngtool → hashcat flow, and say what `-m 22000` unifies.
- Explain why an AP might yield no PMKID, what you do then, and why a strong PSK defeats both methods.

---
> 🔼 Up: [[Wireless Tools]]
