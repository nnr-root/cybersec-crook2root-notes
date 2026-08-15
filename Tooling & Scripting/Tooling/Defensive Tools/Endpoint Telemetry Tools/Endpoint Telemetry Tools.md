---
title: "Endpoint Telemetry Tools"
tags: [tree/tooling, cyber/tooling/defensive/endpoint, cyber/moc]
Domain: "[[Defensive Tools]]"
Color: "#708090"
---

# Endpoint Telemetry Tools

Host instrumentation for process, network, image-load, registry, file, and identity events.

```mermaid
flowchart LR
    K["Kernel / OS events"] --> A["Endpoint agent"]
    A --> L["Local event channel"]
    L --> C["Central collection"]
```

- [[Sysmon]]
- [[osquery]]

```powershell
PS C:\> Get-WinEvent -LogName 'Microsoft-Windows-Sysmon/Operational' -MaxEvents 1 | Select-Object Id,TimeCreated
Id TimeCreated
-- -----------
 1 7/30/2026 10:20:14 AM
```

---
> 🔼 Up: [[Defensive Tools]]
