---
title: "Network Detection & Monitoring Tools"
tags: [tree/tooling, cyber/tooling/defensive/network-monitoring, cyber/moc]
Domain: "[[Defensive Tools]]"
Color: "#708090"
---

# Network Detection & Monitoring Tools

Signature detection and protocol-rich network telemetry for investigation and monitoring.

```mermaid
flowchart LR
    T["Tap / SPAN"] --> S["Suricata signatures"]
    T --> N["Snort signatures"]
    T --> Z["Zeek protocol analysis"]
    S --> A["Alerts"]
    Z --> L["Structured logs"]
    A --> C["Correlation"]
    L --> C
```

- [[Suricata]]
- [[Snort]]
- [[Zeek]]

```shell-session
analyst@sensor:~$ printf '%s\n' 'capture_loss=0.00%' 'sensor_time_sync=ok'
capture_loss=0.00%
sensor_time_sync=ok
```

---
> 🔼 Up: [[Defensive Tools]]
