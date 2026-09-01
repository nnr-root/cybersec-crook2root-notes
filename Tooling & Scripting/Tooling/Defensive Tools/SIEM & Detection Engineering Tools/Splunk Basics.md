---
title: "Splunk Basics"
aliases: ["Splunk", "SPL"]
tags: [tree/tooling, cyber/tooling/defensive/splunk, type/tool, difficulty/medium]
Domain: "[[SIEM & Detection Engineering Tools]]"
Color: "#708090"
---

# Splunk Basics

Splunk is the reference SIEM: it ingests enormous volumes of logs, indexes them, and lets you search across everything with its own query language, **SPL** (Search Processing Language). Every log source in the estate — Sysmon, Zeek, firewalls, cloud audit — lands here, and a *detection* is simply a saved SPL search that alerts when it matches. Learn SPL and you can turn a haystack of logs into an answer.

> [!warning] Searches have a cost
> An unbounded search across a large index is expensive and slow. Always scope by index, sourcetype, and time.

## Parent Learning Order
Splunk Basics -> Sigma

## Where the logs go to be searched at scale

> *Logs are arriving from 4,000 hosts. What does Splunk do to them before you can search anything?*
>
> Hold your answer — the section below is the response.

Splunk is the **platform** in the detection pipeline — the place logs go to be stored and searched at scale.

Read the pipeline: sources feed Splunk, Splunk indexes them (by `source`, `sourcetype`, `host`), and you search with SPL. SPL is a **pipeline language** — data flows left to right through `|` commands, each transforming the stream: `search → stats → eval → table`. Once "everything is a searchable event and I pipe it through transforms" clicks, Splunk stops being a log viewer and becomes an analytics engine.

## Start narrow, then transform

A search *always* starts narrow (index + time) and then transforms:

```text
index=windows sourcetype=Sysmon EventCode=1 earliest=-24h
| stats count by ParentImage, Image
| where ParentImage LIKE "%winword.exe" AND Image LIKE "%powershell.exe"
```

```text
ParentImage            Image                  count
C:\...\winword.exe     C:\...\powershell.exe  3      ← Office spawning PowerShell
```

The workhorses: `stats`/`chart`/`timechart` (aggregate), `eval` (compute fields), `rex` (regex-extract), `lookup` (enrich), `dedup`, `sort`. Save a search as an **alert** with a schedule and threshold → it becomes a live detection feeding the SOC.

## Bounding a search before it scans everything

The first lesson every Splunk user learns the hard way is **bound your search**:

```text
# catastrophic — scans every index, all time
* mimikatz
# correct — one index, one sourcetype, a time window
index=windows sourcetype=Sysmon EventCode=1 process_name=mimikatz.exe earliest=-7d
```

**The deliberate break:** a bare search like `* mimikatz` (no `index=`, no time bound) tells Splunk to scan *every event ever indexed* — minutes of runtime, huge resource cost, and on a busy cluster it can degrade the whole SIEM. The discipline is: lead with `index=` and `sourcetype=`, add a time range, and only then transform. The deeper Root point ties to the next note: SPL is **powerful but Splunk-specific** — a detection you carefully craft here does *not* run on Elastic or Sentinel, so a shop that changes SIEM rewrites its whole rule library. That vendor lock-in is precisely the problem **Sigma** exists to solve: express the *logic* in a portable format and compile it to SPL (or any backend) rather than hand-writing SPL you can never take with you.

## Summary

You should now be able to:

- Explain why SPL is described as a "pipeline language", and what `|` does.
- Write a bounded search that counts Office-spawns-PowerShell events, and name three transforming commands.
- Explain why an unbounded search is dangerous, and why SPL's power is also a portability problem.

---
> 🔼 Up: [[SIEM & Detection Engineering Tools]]
