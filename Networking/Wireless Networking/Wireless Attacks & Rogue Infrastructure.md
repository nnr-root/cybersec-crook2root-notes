---
title: "Wireless Attacks & Rogue Infrastructure"
aliases: ["Evil Twin", "Rogue Access Point", "Deauthentication Attack", "Karma Attack", "Captive Portal Attack"]
tags:
  - tree/networking
  - cyber/networking/wireless
  - type/technique
  - level/operator
Domain:
  - "[[Wireless Networking]]"
Color: "#42D4F4"
---

# 😈 Wireless Attacks & Rogue Infrastructure

> [!abstract] Note of [[Wireless Networking]]
> The most effective wireless attacks do not break encryption — they impersonate the network so the victim connects to the attacker willingly. This note covers the rogue-AP family, from the evil twin to karma attacks, and explains why a client's own eagerness to reconnect to familiar networks is the vulnerability being exploited.

## Parent Learning Order
Wireless Fundamentals & 802.11 -> Wi-Fi Security & WPA -> Wireless Attacks & Rogue Infrastructure -> Cellular & Long-Range Wireless -> Bluetooth & Personal-Area Networks -> Wireless Reconnaissance & Defense

## Start at Zero: Don't Break In, Be the Door

Cracking a strong WPA3 passphrase is hard. Convincing a victim to connect to *your* access point is easy, and yields the same on-path position without touching the encryption. This is the strategic insight of wireless attacks: **impersonate the infrastructure rather than defeat the cryptography.**

The reason it works is a client behaviour that seems helpful and is exploitable. Devices remember networks they have joined and **automatically reconnect** to any network broadcasting a matching SSID. Your laptop, seeing "CoffeeShop_WiFi," connects without asking, because it joined a network by that name before. But an SSID is just a name — nothing stops an attacker from naming *their* access point "CoffeeShop_WiFi." The client cannot tell the difference by name alone, and connects to the attacker.

**Prerequisites:** association, Wi-Fi encryption modes, and management frames.

> [!tip] The analogy, and where it breaks
> Someone putting up a convincing sign reading 'Staff Entrance' over their own doorway. Nobody breaks a lock; people walk in willingly because the sign matches what they expect. The analogy breaks because your device reads the sign *automatically and silently* — it reconnects to a remembered name without asking you, so the victim never even makes a decision to be fooled.

## The Rogue Access Point Family

A **rogue access point** is any AP an attacker controls that a victim connects to believing it legitimate. Several variants exploit different angles.

**The evil twin** clones a legitimate network — same SSID, often a stronger signal — so clients in range prefer it or reconnect to it. Once a victim associates, the attacker is the client's gateway, occupying an on-path position for all the victim's traffic.

```mermaid
flowchart TB
    V["Victim device"] -->|"remembers 'CoffeeShop_WiFi'"| CHOICE{"Two APs with that name"}
    CHOICE -->|"legitimate"| REAL["Real AP"]
    CHOICE -->|"attacker, stronger signal"| EVIL["Evil twin AP"]
    EVIL --> ATT["Attacker sees all victim traffic"]
    ATT --> INET["Forwards to Internet (victim notices nothing)"]
```

**The deauthentication attack** is the evil twin's accomplice. Because management frames are unauthenticated (the fundamentals-leaf weakness), an attacker forges deauth frames that kick a victim off the legitimate AP. The victim's device, now disconnected, automatically hunts for a network by that name — and the evil twin, broadcasting the same SSID with a strong signal, wins the reconnection. Deauth turns a passive lure into an active push.

**The karma attack** exploits probe requests directly. Recall that clients broadcast probe requests asking "is network X here?" for networks they remember. A karma-style rogue AP listens for these probes and simply *answers yes to all of them* — "yes, I am the network you are looking for" — for whatever name the client asks. A device probing for a familiar home or office network is answered by the attacker and connects, no cloning of a specific known network required. Modern devices probe less aggressively to mitigate this, but the technique illustrates that the client's memory of networks is the exposure.

**The captive portal attack** adds a credential-harvesting layer. After a victim connects to the rogue AP, the attacker presents a fake login or "sign-in to continue" page — mimicking a hotel, airport, or corporate portal — to capture credentials the victim types. The connection was the foothold; the portal is the harvest.

## Why Encryption Does Not Always Save the Victim

A natural objection: if the real network uses WPA-Enterprise or WPA3, can the attacker really impersonate it? This is where the details matter.

For an **open network** (coffee shops, many public Wi-Fi), there is no mutual authentication at all — the client has no way to verify the AP, so an evil twin is trivial and complete. Open networks are the softest target.

For a **WPA-Personal** network, the attacker who knows the shared passphrase (often posted on a wall, or previously cracked) can stand up a perfect evil twin, because the passphrase is all the "authentication" there is.

For **WPA-Enterprise**, the picture improves *if configured correctly*: the client can validate the RADIUS server's certificate, which an attacker cannot forge. But if clients are misconfigured to not validate the server certificate — a distressingly common default — the attacker stands up a rogue Enterprise AP, the client authenticates to it without checking the certificate, and the attacker captures the credentials or relays the authentication. **The defense exists but depends on client-side certificate validation being enforced**, which is the recurring Enterprise Wi-Fi failure.

The general principle: the evil twin succeeds wherever the client cannot, or does not, cryptographically verify the AP's identity. Strong, correctly configured mutual authentication is what defeats it; anything less leaves the door open.

## Security Implications

**The client's automatic behaviour is the root vulnerability.** Auto-reconnect and probing for remembered networks are conveniences that let an attacker impersonate a network the victim trusts. The user does nothing wrong and often nothing visible — the device connects silently. This is why user education alone is a weak defense and why technical controls (certificate validation, disabling auto-join for open networks) matter more.

**On-path is the prize, exactly as in every earlier branch.** A successful rogue AP gives the attacker the same on-path position as ARP spoofing, a rogue gateway, or a BGP hijack — and the same conclusion applies: **transport-layer encryption is the backstop.** A victim connected through an evil twin who then uses properly validated HTTPS gives the attacker only metadata and TLS-stripping attempts that HSTS and certificate validation defeat. The evil twin owns the path; it does not automatically own the content. This is the domain's recurring thesis appearing once more, and it is why VPNs are recommended on untrusted Wi-Fi — they re-establish a verified encrypted tunnel over the hostile link.

**Detection is possible and asymmetric.** A rogue AP broadcasting a legitimate SSID is detectable: two APs claiming the same network with different hardware addresses, unexpected signal characteristics, or deauth floods are all signatures. Wireless intrusion detection systems watch for exactly these, and defenders have the advantage that a rogue AP must transmit to function, revealing itself. The reconnaissance-and-defense leaf develops this.

**Enterprise misconfiguration undoes Enterprise security.** The single most important control against Enterprise evil twins — client certificate validation of the RADIUS server — is frequently disabled or unenforced, converting a strong architecture into a vulnerable one. Auditing client configuration for enforced server-certificate validation is high-value and frequently neglected.

Every technique in this note must be performed only against networks and devices you own or are explicitly authorized to test. Standing up a rogue AP that lures other people's devices, forging deauthentication frames on networks you do not own, and harvesting credentials are unlawful outside a controlled, authorized lab.

## Authorized Lab: Lure a Device You Own

Use an isolated lab with an AP you control as the "legitimate" network, a second radio as the attacker, and a test client that is yours. No production or third-party devices may be in scope.

1. **Set up the legitimate network** and connect your test client so it remembers the SSID.
2. **Stand up an evil twin** on the attacker radio with the same SSID and a stronger signal. Observe whether the client prefers or reconnects to it.
3. **Add a deauthentication push.** Forge deauth frames against your own client on the legitimate AP and confirm it disconnects and then reconnects — to the evil twin if it presents the stronger matching SSID.
4. **Confirm the on-path position.** With the client on the evil twin, confirm the attacker sees the client's traffic, then confirm that properly validated HTTPS from the client yields only encrypted content to the attacker — the backstop holding.
5. **Demonstrate the captive portal.** Present a fake portal to the connected client and confirm it can capture typed input (use only synthetic test credentials).
6. **Test Enterprise certificate validation.** With a WPA-Enterprise lab AP, first misconfigure the client to skip server-certificate validation and confirm it authenticates to a rogue Enterprise AP; then enforce validation and confirm the rogue AP is now rejected — demonstrating the decisive control.
7. **Cleanup.** Tear down the rogue AP, restore the client's configuration, and remove any remembered rogue networks.

Expected interpretation:

```text
Evil twin        -> client prefers/reconnects to the matching SSID by name alone
Deauth push      -> forces the reconnection actively, not just passively
On-path          -> attacker sees traffic; validated HTTPS still yields only ciphertext
Captive portal   -> harvests typed input after the connection
Enterprise, no cert check -> rogue AP captures the authentication
Enterprise, cert enforced -> rogue AP rejected; the control that actually works
```

## Crook → Operator → Root Checkpoint

- **Crook:** Explain why impersonating a network beats cracking its encryption, and how auto-reconnect lets an evil twin work.
- **Operator:** Describe the evil twin, deauthentication, karma, and captive-portal techniques and how they chain; explain why open networks are the softest target.
- **Root:** Explain why the evil twin succeeds wherever the client cannot verify the AP, and why enforced RADIUS server-certificate validation is the decisive Enterprise control; connect the on-path outcome to the encryption backstop and the recommendation to use a VPN on untrusted Wi-Fi.

---
> 🔼 Up: [[Wireless Networking]]
