---
title: "Sysmon"
aliases: ["sysmon", "System Monitor"]
tags: [tree/tooling, cyber/tooling/defensive/sysmon, type/tool, difficulty/medium]
Domain: "[[Endpoint Telemetry Tools]]"
Color: "#708090"
---

# Sysmon

Sysmon (System Monitor) is the free Sysinternals driver that turns a Windows host into a rich security **event stream**. Default Windows logging is thin; Sysmon adds high-fidelity events — process creation with full command line and hashes, network connections, image loads, remote-thread injection, DNS queries — that are the raw material of nearly every Windows detection rule. It records; a SIEM/EDR detects on top of it.

> [!warning] Telemetry, not prevention
> Sysmon *observes* — it doesn't block. And it only records what its configuration tells it to; the config is the tool.

## Parent Learning Order
Sysmon -> osquery

## The event stream: CCTV for the operating system

There are two shapes of endpoint visibility. Sysmon is the **event stream** — a continuous, ordered recording of what happened.

Think of it as CCTV for the OS: every process launch, network connection, and injection becomes a timestamped **Event ID** you can replay to reconstruct exactly what an attacker did and when. Event ID 1 (ProcessCreate, with parent and command line) alone underpins a huge fraction of detections, because "what spawned what, with what arguments" is the story of most attacks.

## Installing it with a config that records something

Sysmon is nothing without a **config** — install it with a curated one (SwiftOnSecurity or Olaf Hartong's are the standards):

```console
C:\> sysmon64 -accepteula -i sysmonconfig.xml
Sysmon installed.  Config schema version: 4.90
```

Events land in `Applications and Services Logs → Microsoft → Windows → Sysmon → Operational`, ready to forward to a SIEM. The high-value IDs:

| ID | Event | Catches |
|---|---|---|
| 1 | ProcessCreate | LOLBins, suspicious parent→child (`winword.exe`→`powershell.exe`) |
| 3 | NetworkConnect | C2 callbacks, tool downloads |
| 7 | ImageLoad | DLL side-loading, unsigned modules |
| 8 | CreateRemoteThread | process injection |
| 11 | FileCreate | dropped payloads |
| 22 | DNSQuery | DGA/exfil, beacon domains |

A detection is then just a query: *ProcessCreate where ParentImage ends in `winword.exe` and Image ends in `powershell.exe`*.

## The config is both the power and the blind spot

Sysmon's power and its blind spot are the same thing — the **config**:

```xml
<!-- No config (or default install): almost nothing useful is logged -->
<Sysmon><EventFiltering></EventFiltering></Sysmon>
<!-- The community config logs the RIGHT things and excludes known-good noise -->
<ProcessCreate onmatch="exclude"> ...trusted signed updaters... </ProcessCreate>
```

**The deliberate break:** install Sysmon with no config and it records essentially nothing actionable; install it logging *everything* and it floods the SIEM (and the endpoint) into uselessness. The entire value of Sysmon lives in a tuned configuration that captures attacker-relevant events (ID 1/3/7/8/22) while *excluding* the mountain of benign activity — which is why "deploy Sysmon" really means "deploy and maintain a good Sysmon config." Two more Root truths: attackers who know Sysmon is present avoid the watched Event IDs (living off un-logged techniques) or try to unload the driver — so detection engineers monitor for **Sysmon itself stopping** (a gap in the stream is a signal). And Sysmon is telemetry, not prevention: it tells you the injection happened; blocking it is the EDR's job on top of this data.

## Summary

You should now be able to:

- What does Sysmon add over default Windows logging, and why is Event ID 1 so central?
- Map three Event IDs to the attacker behaviour each catches.
- Explain why "the config is the tool," and how an attacker or a stopped driver creates a blind spot.

---
> 🔼 Up: [[Endpoint Telemetry Tools]]
