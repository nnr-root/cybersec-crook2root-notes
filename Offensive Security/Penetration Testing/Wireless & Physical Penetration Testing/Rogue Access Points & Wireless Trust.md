---
title: "Rogue Access Points & Wireless Trust"
aliases: ["Rogue AP Testing", "Evil Twin Assessment"]
tags:
  - tree/offensive
  - cyber/offensive/wireless
  - type/methodology
  - difficulty/hard
Domain: "[[Wireless & Physical Penetration Testing]]"
Color: "#DC143C"
---

# Rogue Access Points & Wireless Trust

> [!abstract] Enterprise methodology
> Rogue-AP testing evaluates whether clients trust names instead of authenticated infrastructure, whether wired controls detect unauthorized radios, and whether identity, onboarding, and monitoring prevent a nearby attacker from becoming a network intermediary.

## Parent Learning Order
WPA2 Security Testing -> WPA3 Security Testing -> Rogue Access Points & Wireless Trust -> RFID & Physical Access Testing

## Trust paths

```mermaid
flowchart TD
    U["User/device"] --> S{"Why trust this WLAN?"}
    S -->|SSID only| R["Rogue AP opportunity"]
    S -->|Validated certificate/profile| A["Approved enterprise AP"]
    R --> P["Portal, DNS, or traffic manipulation risk"]
    A --> N["Policy-assigned network access"]
```

## Rogue categories

- **Evil twin:** attacker-controlled AP imitates an approved SSID.
- **Unauthorized internal AP:** employee/device bridges the wired network to radio.
- **Misconfigured approved AP:** legitimate infrastructure advertises unsafe security.
- **Ad hoc/hotspot:** unmanaged peer or phone tethering bypasses policy.
- **Rogue client:** device associates with prohibited external networks.

## Test design

Use a dedicated test SSID/profile, synthetic identity, approved channel, low transmit power, and RF-contained location where possible. Never imitate a production SSID or collect credentials without explicit approval.

Document the expected control chain:

```text
1. Managed device receives signed WLAN profile
2. Device validates RADIUS server certificate and expected identity
3. Network-access control assigns role/VLAN
4. Wireless IDS detects unauthorized BSSID or wired rogue AP
5. SOC triages and facilities locates device
```

## Client trust assessment

Check whether managed clients:

- Autojoin by SSID alone.
- Validate certificate chain, name, and expected identity.
- Prefer stronger security over signal strength.
- Expose probe requests for hidden/preferred networks.
- Permit user-created profiles that override managed policy.
- Retain networks after offboarding.

Representative controlled observation:

```text
Test SSID: Corp-Audit
Managed profile expected server: radius.example.internal
Presented test certificate: untrusted audit CA
Expected: connection rejected
Observed: OS prompts user to accept certificate manually
Risk: user-mediated credential disclosure path
```

## Wired-side rogue AP

An unauthorized AP connected to an office port can bypass physical and network boundaries. Validate switch-port authentication, NAC, DHCP snooping, allowed-device policy, segmentation, and whether infrastructure detects a new bridge/MAC pattern.

```mermaid
flowchart LR
    R["Unauthorized AP"] --> P["Office switch port"]
    P --> N["NAC / 802.1X"]
    N -->|Denied| Q["Quarantine"]
    N -->|Incorrectly allowed| C["Corporate segment"]
```

## Detection exercise

Coordinate a time-boxed test with the SOC and wireless team. Measure:

- Detection latency.
- Correct classification and location.
- Correlation with switch and DHCP data.
- Analyst ability to distinguish sanctioned test infrastructure.
- Containment and escalation workflow.

Do not perform automated containment against unknown radios; neighboring businesses and personal devices may be lawful.

## Remediation

Deploy signed managed WLAN profiles, certificate-based EAP, strict server-name validation, PMF, 802.1X/NAC on wired ports, wireless intrusion monitoring, inventory reconciliation, and user training that explains certificate warnings rather than teaching users to click through them.

## Trust decision analysis

Clients may select networks by saved SSID, security type, signal, previous BSSID, enterprise profile, and platform policy. Test whether an enterprise profile pins authentication-server trust or merely trusts a broad public/private CA. Observe auto-join, transition-mode, captive portal, and fallback behavior with canary devices.

## Controlled rogue-AP design

Use shielded space or approved channels/power, unique test SSID unless an exact-name simulation is authorized, no Internet forwarding by default, canary credentials only, explicit source labeling, remote monitoring, and a physical kill switch. Capture association and authentication metadata without collecting unrelated user traffic.

```text
AP identifier: C2R-ROGUE-01
Location: RF enclosure
Channel/power: 36 / minimum
Clients: two inventory-tagged canaries
Credential policy: generated, single-use
Stop condition: unexpected client association
```

## Detection validation

Compare wireless-controller rogue detection, wired switch MAC/port data, DHCP, RADIUS, DNS, endpoint WLAN events, and physical inventory. Test unknown AP, known SSID from wrong BSSID, unauthorized bridge, and canary client association. Validate response ownership and containment procedure.

## Summary

You should now be able to:

- Explain why a client connects willingly to an "evil twin" carrying the same SSID as a network it trusts.
- Design a bounded evil-twin detection exercise that proves whether corporate clients auto-associate, without capturing real user credentials.
- Explain how 802.1X server-certificate validation and PMF (Protected Management Frames) each remove a specific rogue-AP primitive, and what still fails if clients don't validate the RADIUS certificate.

---
> 🔼 Up: [[Wireless & Physical Penetration Testing]]
