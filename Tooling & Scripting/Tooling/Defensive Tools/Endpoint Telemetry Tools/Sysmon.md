---
title: "Sysmon"
aliases: ["sysmon", "System Monitor"]
tags: [tree/tooling, cyber/tooling/defensive/sysmon, type/tool, difficulty/medium]
Domain: "[[Endpoint Telemetry Tools]]"
Color: "#708090"
---

# Sysmon

> [!abstract] Note of [[Endpoint Telemetry Tools]]
> Sysmon is CCTV for a Windows host — a continuous, ordered event stream of process creation, network connections, image loads and injection that underpins most Windows detection. This note covers why the config is the whole tool, and why the events it records are precisely the footprints the offensive tree leaves behind.

Sysmon (System Monitor) is the free Sysinternals driver that turns a Windows host into a rich security **event stream**. Default Windows logging is thin; Sysmon adds high-fidelity events — process creation with full command line and hashes, network connections, image loads, remote-thread injection, DNS queries — that are the raw material of nearly every Windows detection rule. It records; a SIEM/EDR detects on top of it.

> [!warning] Telemetry, not prevention
> Sysmon *observes* — it doesn't block. And it only records what its configuration tells it to; the config is the tool.

## Parent Learning Order
Sysmon -> osquery

## The event stream: CCTV for the operating system

> *A process started at 02:14 and exited at 02:15. Tomorrow you need to know it happened. What kind of visibility does that require?*
>
> Hold your answer — the section below is the response.

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

**How you'd spot it:** count events per host per hour. Near zero means the config excludes everything that matters; hundreds of thousands means it excludes nothing and the storage bill is about to say so. Then check which IDs actually arrive — a deployment producing only Event ID 1 is not giving you the network, image-load or injection visibility the rest of this note assumes.

## Security Implications

**Sysmon is where the offensive tree becomes visible, if the config is right.** The Event IDs map directly onto tools from Offensive Tools: **ID 10** (process access to `lsass.exe`) catches [[Mimikatz]] regardless of how it was delivered; **ID 8** (CreateRemoteThread) catches Meterpreter migration; **ID 1 + ID 3** together catch a [[LOLBAS]] binary that both runs and reaches the network (`certutil` downloading an executable); **ID 1**'s parent-child pairs catch `winword.exe → powershell.exe`. The detections those notes describe are queries over this stream — which is why "deploy Sysmon" means "deploy and maintain a config that records IDs 1/3/7/8/10/22."

**A gap in the stream is itself a signal.** An attacker who knows Sysmon is present avoids the watched IDs or tries to unload the driver, so detection engineers alarm on **Sysmon stopping** — an event source going silent is as suspicious as a bad event. The config is readable, so an attacker on the host can learn what is watched; the durable answer is defence in depth, not a secret config.

**It observes, it does not block.** Sysmon tells you the injection happened; preventing it is the EDR's job layered on this data. Treating telemetry as a control is the mistake — it is the evidence a control acts on.

## Summary

You should now be able to:

- Describe what Sysmon adds over default Windows logging, and why Event ID 1 is central.
- Map three Event IDs to the attacker behaviour each catches.
- Explain why "the config is the tool," and how an attacker or a stopped driver creates a blind spot.

---
> 🔼 Up: [[Endpoint Telemetry Tools]]
