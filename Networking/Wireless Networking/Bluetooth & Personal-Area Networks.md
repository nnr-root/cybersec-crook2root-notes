---
title: "Bluetooth & Personal-Area Networks"
aliases: ["Bluetooth", "BLE", "Bluetooth Low Energy", "Pairing", "Zigbee", "Personal-Area Network"]
tags:
  - tree/networking
  - cyber/networking/wireless
  - type/concept
  - difficulty/medium
Domain:
  - "[[Wireless Networking]]"
thread-exempt:
  - "3B:1F:04: a BLE device address, not an Ethernet MAC — the note discusses address randomisation, which 00:00:5E would misrepresent"
  - "4C:87:5D: same, a second BLE device address"
  - "6F:2C:19: same, a third BLE device address"
Color: "#42D4F4"
---

# 🎧 Bluetooth & Personal-Area Networks

> [!abstract] Note of [[Wireless Networking]]
> Short-range wireless connects the devices around a person — headphones, wearables, keyboards, sensors — and its security is shaped by a hard constraint: many of these devices are too small and cheap for strong, updatable protection. This note explains Bluetooth and its low-energy variant, the pairing that establishes trust, and why the personal-area network is a persistent, under-monitored attack surface.

## Parent Learning Order
Wireless Fundamentals & 802.11 -> Wi-Fi Security & WPA -> Wireless Attacks & Rogue Infrastructure -> Cellular & Long-Range Wireless -> Bluetooth & Personal-Area Networks -> Wireless Reconnaissance & Defense

## The Network Around a Person

A **PAN (Personal-Area Network)** connects devices within a few metres of a person. **Bluetooth** is its dominant technology, and it comes in two quite different forms:

- **Bluetooth Classic** — higher throughput for continuous streams like audio, using more power.
- **Bluetooth Low Energy (BLE)** — designed for tiny, infrequent data from battery-constrained devices: wearables, sensors, beacons, medical devices, smart-home gadgets. BLE is why a fitness tracker runs for weeks on a tiny battery.

BLE's low-power design is the source of both its ubiquity and its security character. To sip power, it minimizes transmission and computation, which constrains how much cryptography it can afford — and the devices that use it are often cheap, single-purpose, and never updated. This produces the recurring embedded-security problem: **security is largely fixed at manufacture, on devices too constrained to improve it.**

Other PAN technologies fill specific niches — **Zigbee** and **Z-Wave** for low-power mesh home automation, **NFC** for centimetre-range tap interactions — but the security lessons generalize from Bluetooth: short range is not a security boundary, and constrained devices carry weak, static protection.

**Prerequisites:** wireless basics and the idea of key exchange.

> [!tip] The analogy, and where it breaks
> Introducing two people who will trust each other from now on — ideally by having both confirm the same number out loud. The analogy breaks for devices with no screen or keypad, like a headset: they must be introduced with no confirmation at all, trusting whoever is present. That is 'Just Works' pairing, and it is extremely common precisely because so many devices have nothing to display.

## Pairing: Establishing Trust

Before two Bluetooth devices communicate securely, they **pair** — exchanging keys to establish a trusted relationship. Pairing is where the security of the connection is decided, and its method depends on what interfaces the devices have.

| Pairing method | Requires | Security |
| --- | --- | --- |
| **Just Works** | No input/output | Weak — no authentication of the peer |
| **Passkey Entry** | A display and a keypad | Strong — a code confirms both ends |
| **Numeric Comparison** | Two displays | Strong — both users confirm a matching number |
| **Out of Band** | NFC or similar side channel | Strong — trust bootstrapped elsewhere |

The problem is visible immediately: **"Just Works" provides no authentication.** Devices with no display or keypad — a headset, a sensor, a beacon — cannot present or confirm a code, so they pair without verifying who they are pairing with. This is the personal-area equivalent of an open Wi-Fi network or 2G's one-way authentication: the client cannot verify the peer, so an attacker in range can insert themselves. And because so many BLE devices lack any interface, Just Works is extremely common.

```mermaid
flowchart TD
    P["Two devices pair"] --> Q{"Do both have display/input?"}
    Q -->|"Yes"| STRONG["Passkey / numeric comparison: peer authenticated"]
    Q -->|"No (headset, sensor)"| JW["Just Works: no authentication"]
    JW --> MITM["Attacker in range can insert during pairing"]
    STRONG --> SAFE["Man-in-the-middle rejected"]
```

## The Threats

**Interception during pairing.** If pairing is unauthenticated (Just Works) or uses a weak method, an attacker in range can perform a man-in-the-middle attack during the pairing exchange, ending up with keys to both sides. The window is the pairing moment, which is why pairing in a private location rather than a crowded one is a small but real precaution for sensitive devices.

**Tracking by address.** BLE devices advertise to be discovered, and if they use a static hardware address, they can be tracked as they move — a wearable broadcasting a constant identifier lets an observer follow the person wearing it. The fix is **address randomization**, rotating the advertised address so it cannot be correlated over time; well-designed devices use it, and cheap ones often do not.

**Implementation vulnerabilities.** Bluetooth stacks are complex and have had serious remotely exploitable flaws — vulnerabilities allowing code execution or interception simply from being in range, without pairing. Because the affected devices span everything from phones to embedded gadgets, and many never receive patches, these vulnerabilities have long tails. The constrained, unpatched-device problem means a flaw found today persists in the field for years.

**Range is greater than assumed.** "It's only a few metres" is a false comfort. With a directional antenna and amplification, an attacker can reach Bluetooth devices from far beyond the nominal range. Short range raises the effort but is not a boundary, exactly as Wi-Fi's walls are not a boundary.

## Worked Example: What a Device Broadcasts Before You Connect

The personal-area attack surface is easiest to grasp by looking at what devices
emit continuously, to anyone, with no connection and no pairing.

> [!note] Representative output
> Reconstructed from a lab of this shape rather than copied from one capture. Field layouts and flag names match the named tool; addresses and identifiers are synthetic.

**Classic discovery.** A scan names the devices in range and tracks their signal
strength:

```shell-session
analyst@lab:~$ bluetoothctl
[bluetooth]# scan on
Discovery started
[NEW] Device 4C:87:5D:2A:11:E9 Wireless Earbuds
[NEW] Device 3B:1F:04:9C:77:A2 Car-Audio-8842
[CHG] Device 4C:87:5D:2A:11:E9 RSSI: -54
[CHG] Device 4C:87:5D:2A:11:E9 RSSI: -41
```

Two things are already available without any interaction: a stable address and a
name that often describes the product, the owner, or both. The falling-then-rising
`RSSI` is a crude distance signal — enough to tell that the device is approaching.

**Low-energy advertising, in detail.** `btmon` shows the raw advertising reports
that BLE devices broadcast on a fixed interval:

```shell-session
analyst@lab:~$ sudo btmon
> HCI Event: LE Meta Event (0x3e) plen 42
      LE Advertising Report (0x02)
        Address type: Random (0x01)
        Address: 6F:2C:19:D4:8A:33 (Static)
        Data length: 26
        Flags: 0x06
          LE General Discoverable Mode
          BR/EDR Not Supported
        Complete Local Name: Fitness Band 4
        Service Data (UUID 0x180f): 4b
        RSSI: -67 dBm (0xbd)
```

`Service Data (UUID 0x180f)` is the standard Battery Service, and `4b` is 75% —
a device reporting its battery level to the whole room. Harmless in itself, and a
good illustration of how much a beacon says before any trust is established.

**The line that matters for privacy** is `Address: … (Static)`. BLE supports
resolvable private addresses that rotate every fifteen minutes precisely so a
device cannot be followed between locations. A *static* random address never
rotates, so this beacon is a durable identifier — anyone with a receiver can
recognise the same wearable in a shop today and an office tomorrow. The failure
here is not broken cryptography; it is a device that never enabled the privacy
feature, which is exactly the cheap-endpoint constraint this note opened with.

## Security Implications

**The constrained-device problem defines PAN security.** Many Bluetooth and BLE devices cannot run strong cryptography, cannot be updated, and pair without authentication because they lack interfaces. Their security is set at manufacture and does not improve, and they are deployed in enormous numbers close to people and, increasingly, inside organizations (wireless peripherals, medical devices, building sensors). The realistic posture is to treat them as weakly secured, minimize what they can access, and monitor for anomalies — because hardening the devices is often impossible.

**Short range is not isolation.** The assumption that a Bluetooth device is safe because an attacker must be nearby fails against directional antennas and against the reality that "nearby" includes shared offices, public transit, and adjacent rooms. PAN devices in sensitive environments are an attack surface that physical proximity does not adequately bound.

**Wireless peripherals extend the keyboard-and-mouse trust boundary.** A wireless keyboard or mouse that pairs weakly or communicates without strong encryption can be injected into — an attacker sends keystrokes to a victim's machine, or captures them. This turns a convenience peripheral into an input channel to a workstation, which is why some high-security environments prohibit wireless peripherals entirely.

**The encryption backstop applies but is weaker here.** For data flowing over Bluetooth, the link's own encryption is the primary protection, and unlike Wi-Fi carrying general Internet traffic, there is often no additional end-to-end encryption layered on top — a Bluetooth headset's audio or a sensor's readings rely on the Bluetooth encryption alone. This makes the strength of pairing and link encryption more directly consequential than in a Wi-Fi context where TLS usually backs it up.

**Discoverability and pairing state are exposure.** A device left discoverable, or one that re-enters pairing mode readily, widens the window for attack. Keeping devices non-discoverable except when intentionally pairing, and pairing in controlled settings, are simple reductions of the exposure.

All scanning and testing described here must target only devices you own or are explicitly authorized to assess. Intercepting Bluetooth communications, attacking pairing, and injecting into peripherals belonging to others are unlawful.

## Summary

You should now be able to:

- Explain what a personal-area network is, the difference between Bluetooth Classic and BLE, and what pairing establishes.
- Enumerate your own Bluetooth devices, identify pairing methods and address randomization, and explain why "Just Works" provides no authentication.
- Explain how the constrained-device problem fixes PAN security at manufacture and why short range is not a boundary; connect weak pairing to the man-in-the-middle window and wireless-peripheral injection, and explain why the link encryption is more directly consequential here than where TLS backs it up.

---
> 🔼 Up: [[Wireless Networking]]
