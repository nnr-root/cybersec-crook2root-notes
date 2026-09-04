---
title: "Splunk Basics"
aliases: ["Splunk", "SPL"]
tags: [tree/tooling, cyber/tooling/defensive/splunk, type/tool, difficulty/medium]
Domain: "[[SIEM & Detection Engineering Tools]]"
Color: "#708090"
---

# Splunk Basics

> [!abstract] Note of [[SIEM & Detection Engineering Tools]]
> Splunk is the reference SIEM: it ingests the estate's logs, indexes them by time, and searches them with **SPL**, a pipeline language. A detection here is nothing more exotic than a saved search with a schedule and a threshold.

Splunk is the reference SIEM: it ingests enormous volumes of logs, indexes them, and lets you search across everything with its own query language, **SPL** (Search Processing Language). Every log source in the estate — Sysmon, Zeek, firewalls, cloud audit — lands here, and a *detection* is simply a saved SPL search that alerts when it matches. Learn SPL and you can turn a haystack of logs into an answer.

> [!warning] Searches have a cost
> An unbounded search across a large index is expensive and slow. Always scope by index, sourcetype, and time.

## Parent Learning Order
Splunk Basics -> Sigma

**Prerequisites:** [[Sysmon]] — most of the searches worth writing are over its events, and its field names are the ones every example assumes.

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

> [!tip] The analogy, and where it breaks
> SPL is a Unix pipeline over logs: `search` is `grep`, `stats` is `sort | uniq -c`, `|` is `|`. The analogy holds further than most and breaks in one place that matters — `grep` reads a file you named, while `search` decides *for itself* how much of a multi-terabyte index to read, based on what you put before the first pipe. In a shell you choose the input. In SPL you only hint at it, and a bad hint costs the cluster rather than your terminal.

## Where the time bound gets its power

The instruction to "always bound your search" sounds like etiquette until you know what Splunk does with the bound. Data is not stored in one file; it is stored in **buckets**, each covering a contiguous span of time and carrying its own index of which terms appear inside it. A bucket ages through hot (open, being written), warm, cold and finally frozen, migrating to slower storage as it goes.

Two consequences follow, and they explain nearly every performance question a beginner has. First, a time range lets Splunk discard whole buckets before opening any of them — a seven-day window on a two-year index skips more than 99% of the data on metadata alone, which is why the time picker is not a display preference but the primary filter. Second, the terms in a bucket's index are what make a search *dense* or *sparse*: a search for a rare string finds few candidate events and returns quickly, while one for a common term must read and discard enormous numbers of them.

The other structural fact is *when* a field comes into existence. `index`, `source`, `sourcetype`, `host` and `_time` are **index-time** fields — written at ingestion, present in the bucket metadata, usable to skip data. Everything else is typically **search-time**: extracted by regex as each event is read. That is why `index=windows sourcetype=Sysmon` before the first pipe is a genuinely different kind of filter from `process_name=mimikatz.exe` after it. The first decides what to read; the second is applied to everything already read. Put the cheap filters first and the expensive ones last, always.

This is also the answer to "why is `| tstats` so much faster." `tstats` runs against accelerated data models and index-time metadata rather than raw events, so an aggregation that takes minutes as a `stats` over raw data can return in seconds — at the cost of only being able to ask about fields the acceleration covers. A distributed deployment adds the last piece: search heads dispatch to indexers, each indexer searches its own buckets in parallel, and results are merged. Transforming commands that can be computed per-indexer (`stats`, `timechart`) are far cheaper than ones that must gather everything centrally first.

## Bounding a search before it scans everything

The first lesson every Splunk user learns the hard way is **bound your search**:

```text
# catastrophic — scans every index, all time
* mimikatz
# correct — one index, one sourcetype, a time window
index=windows sourcetype=Sysmon EventCode=1 process_name=mimikatz.exe earliest=-7d
```

**The deliberate break:** a bare search like `* mimikatz` (no `index=`, no time bound) tells Splunk to scan *every event ever indexed* — minutes of runtime, huge resource cost, and on a busy cluster it can degrade the whole SIEM. The discipline is: lead with `index=` and `sourcetype=`, add a time range, and only then transform. The deeper Root point ties to the next note: SPL is **powerful but Splunk-specific** — a detection you carefully craft here does *not* run on Elastic or Sentinel, so a shop that changes SIEM rewrites its whole rule library. That vendor lock-in is precisely the problem **Sigma** exists to solve: express the *logic* in a portable format and compile it to SPL (or any backend) rather than hand-writing SPL you can never take with you.

**How you'd spot it:** the Job Inspector states it plainly — a scan count in the hundreds of millions against an event count in the dozens means the search read everything and threw nearly all of it away. In the search bar the tell is simpler: no `index=` before the first pipe, and the time picker left on All time.

## Security Implications

A SIEM is the most centralised sensitive data store in the organisation. It holds command lines, URLs, file paths, user names and often credentials that were logged by accident, drawn from every system at once — which makes it both a compliance obligation and a target of the first order. An attacker who reaches the SIEM gets a map of the estate, a list of what is monitored, and the ability to see the defenders' own investigation. Role-based access, index-level restrictions for sensitive sources, and separate credentials from the domain being monitored are the baseline.

The log pipeline is itself an attack surface. Log **deletion** on a host is loud and largely futile once events are forwarded, so the more effective moves are upstream: stopping or reconfiguring the forwarder, filling the disk that buffers events, or generating enough noise that the real events age out of a volume-limited index. The counter is to alert on the *absence* of data — a host that stopped forwarding, an index whose ingest rate dropped — because the gap in the timeline is the signal, and nothing else will report it.

Splunk's own extensibility is the sharp edge worth naming. Apps and add-ons run code on the search heads, scheduled searches can trigger alert actions that execute scripts, and SPL commands like `sendemail` or a custom command can reach outward. Treat app installation as a code deployment, review scheduled searches the way you review cron, and remember that a saved search running as a privileged user is a scheduled task with the SIEM's full visibility behind it.

## Summary

You should now be able to:

- Explain why SPL is described as a "pipeline language", and what `|` does.
- Write a bounded search that counts Office-spawns-PowerShell events, and name three transforming commands.
- Explain buckets, index-time versus search-time fields, and why the time range and `index=` are a different kind of filter from everything after the first pipe.
- Explain why an unbounded search is dangerous, why SPL's power is also a portability problem, and why alerting on missing data matters as much as alerting on events.

---
> 🔼 Up: [[SIEM & Detection Engineering Tools]]
