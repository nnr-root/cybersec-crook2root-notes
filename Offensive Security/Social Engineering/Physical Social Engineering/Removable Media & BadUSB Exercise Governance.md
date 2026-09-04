---
title: "Removable Media & BadUSB Exercise Governance"
aliases: ["BadUSB", "USB Drop", "Removable Media Testing", "HID Injection"]
tags:
  - tree/offensive
  - cyber/offensive/social/removable-media
  - type/concept
  - difficulty/medium
Domain: "[[Physical Social Engineering]]"
Color: "#DC143C"
---

# 🔌 Removable Media & BadUSB Exercise Governance

> [!abstract] Note of [[Physical Social Engineering]]
> USB is not a storage interface. It is a bus on which a device announces what kind of device it is, and the host believes the announcement. This note covers why blocking mass storage proves nothing about the port, what a composite device does to that model, and how to run a drop exercise whose most successful possible outcome is still a marker typed into a text file.

## Parent Learning Order
Tailgating, Facility & Visitor Process Testing -> Removable Media & BadUSB Exercise Governance

## The Port Trusts Whatever the Device Says It Is

> *Autorun is disabled across the fleet and USB mass storage is blocked by policy. Is the port safe?*
>
> Hold your answer — the section below is the response.

No, and the two controls named are aimed at a different threat than the one that matters. When a device is plugged in, it **enumerates**: it tells the host which USB class it belongs to, and the host loads a driver on that basis. A device that declares itself a keyboard gets the keyboard driver. Nothing in that exchange verifies the declaration against the physical object, because there is nothing to verify it against — the plastic shell says nothing to the operating system.

A keyboard needs no autorun, because it is not media to be opened. It needs no storage permission, because it stores nothing. It types, at machine speed, into whatever window has focus, with the privileges of the logged-in user.

| USB class | What it can do once enumerated | Blocked by a mass-storage policy? |
| --- | --- | --- |
| Mass storage | Present files | Yes |
| **HID (keyboard/mouse)** | Inject keystrokes at the user's privilege | **No** |
| Network adapter | Become a preferred route; answer DHCP and DNS | **No** |
| Serial / CDC | Open a device channel to a host process | **No** |
| Composite | Declare several of the above at once | Partially, and that partial block is the trap |

**The deliberate break:** "USB security" is understood as controlling what files may be copied on and off a machine.

The file question is a data-loss question, and it is genuinely important — but it is not the intrusion question. The intrusion question is which **device classes** the host will accept from an untrusted physical object, and a policy written entirely about storage answers it for one class out of five. This is why the finding "we block USB drives" is not evidence of a controlled port. A device enumerating as a keyboard walks past that policy without engaging it at all, and a device enumerating as a USB Ethernet adapter can install itself as a route with a higher priority than the corporate network, redirecting name resolution before anyone touches a file.

**How you'd spot it:** in endpoint telemetry, at the enumeration event and the lineage that follows it. A keyboard attaching at 02:14 on a workstation nobody was sitting at, followed within two seconds by a process launched from an interactive shell, is the signature — the timing is what gives it away, because the interval between "keyboard connected" and "keystrokes issued" is inhumanly short. On Windows, correlate device-installation events with process creation and parent lineage; the absence of any human-scale gap is the tell.

## Composite Devices, and Why Partial Blocking Misleads

A composite device declares more than one class in a single enumeration — commonly storage *and* HID. The consequence is specific: a device-control policy that blocks the storage function frequently permits the device, because the storage interface was refused and the policy's condition was satisfied. The keyboard interface attaches regardless.

This is worth testing directly rather than reasoning about, since the behaviour depends on the product and its configuration. The question the test answers is whether device control evaluates the **device** or each **interface**, and whether a refused interface causes the whole device to be rejected.

> [!tip] The analogy, and where it breaks
> Enumeration works like a visitor writing their own job title on a sign-in sheet — the building responds to what was written, not to who arrived. The analogy breaks in the organisation's favour in one place: a receptionist can look up at the visitor, whereas the USB host has no channel through which to look. Which is why the control has to be a policy about what titles are accepted at all, rather than a judgement about the individual holding the pen.

## Governing the Exercise

A drop exercise puts physical objects into a workplace, so every one of them is inventoried before it leaves the tester's hands and accounted for afterwards.

```text
Asset:          C2R-USB-017            (serial recorded, one of 6 in SE-TEST-153)
Class:          signed read-only storage canary
Placement:      approved training room, Meridian depot building
Behaviour:      opens a static instruction page; no auto-execution, no payload
Callback:       records asset serial + timestamp only — no user, no hostname
Expiry:         18:00 UTC, page retired
Recovery owner: Physical Security, p.nowak
Unrecovered:    treated as an incident and reported same day
```

Two rules carry most of the safety. **The canary records the asset and the time, and nothing else** — a device that reports usernames and hostnames has begun collecting personal data about who fell for a test, which is the finding nobody should want and the data nobody should hold. **An unrecovered device is an incident**, not a loose end: a tester's USB stick left in a car park after the window closes is an untracked object in a workplace, and the exercise has produced a hazard rather than a finding.

Never deploy destructive keystrokes, uncontrolled payloads, or anything whose behaviour depends on timing the tester cannot observe. The exercise's total success must remain harmless — the same action ceiling that governs a phishing landing page.

## HID Simulation Within the Ceiling

The HID class still needs testing, since it is the class the storage policy misses. It is tested on an isolated endpoint in a controlled range rather than on a member of staff's workstation, and the injected action is inert: typing a unique marker into a local text editor, then stopping.

```text
Endpoint:  isolated test host, 10.10.30.7 (SCAN-07 range)
Injected:  opens a text editor, types SE-TEST-153-HID-OK, saves locally
Forbidden: launching a shell · altering security controls · network egress ·
           anything whose effect depends on unobserved timing
Evidence:  device-install event, process lineage, keystroke-interval timing
```

That marker is sufficient. It demonstrates that a keyboard-class device attached and issued keystrokes at the user's privilege, which is the entire claim under test. A shell adds no information to the finding and a great deal of risk to the exercise.

## Reading the Result Across Three Layers

The exercise produces three separate findings, and conflating them loses most of the value:

1. **Did device control block the class?** Test each class independently, including the composite case.
2. **Did telemetry see it?** Insertion recorded, process lineage attributable, alert raised — an unblocked device that is fully visible is a very different posture from one that is invisible.
3. **Did people report unknown media without plugging it in?** This is the human finding, and the desired behaviour is handing the object to security, not testing it in a spare machine to see what it is.

An organisation can score well on one and badly on the others, and the remediation differs each time.

## Summary

You should now be able to:

- Explain USB enumeration and why a device's declared class is trusted, and therefore why a BadUSB device functions with autorun disabled and mass storage blocked.
- Name the classes a storage-focused policy leaves unaddressed, and explain why a composite device can defeat a policy that evaluates devices rather than interfaces.
- Specify what a tagged canary device may record and what it must never record, and explain why an unrecovered device is handled as an incident.
- Describe the endpoint telemetry that detects keystroke injection — device-install event, process lineage, keystroke-interval timing — and separate the device-control, telemetry and human-reporting findings that one exercise produces.

---
> 🔼 Up: [[Physical Social Engineering]]
