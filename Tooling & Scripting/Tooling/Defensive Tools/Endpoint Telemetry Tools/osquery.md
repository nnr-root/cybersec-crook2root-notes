---
title: "osquery"
aliases: ["osquery", "osqueryi"]
tags: [tree/tooling, cyber/tooling/defensive/osquery, type/tool, difficulty/medium]
Domain: "[[Endpoint Telemetry Tools]]"
Color: "#708090"
---

# osquery

> [!abstract] Note of [[Endpoint Telemetry Tools]]
> osquery models an operating system as SQL tables, turning "check every endpoint for X" into one query across a whole fleet. This note covers why it answers *what is true right now* rather than what happened, why that snapshot model has a gap a fast attacker slips through, and why it complements rather than replaces a Sysmon-style event stream.

osquery exposes an operating system as a **SQL database**. Running processes, listening ports, users, startup items, installed software, kernel modules — each becomes a table you can `SELECT` from with ordinary SQL, on Windows, Linux, and macOS alike. It turns "go check every endpoint for X" into a single query, which makes it the backbone of fleet-wide hunting, inventory, and incident response.

> [!warning] Read-only visibility
> osquery queries state; it doesn't change it. Run scheduled queries with care — an expensive query across a large fleet has a cost.

## Parent Learning Order
Sysmon -> osquery

## The flashlight: what is true right now

> *You want to ask 3,000 endpoints one question and have the answer now. Stream, or snapshot?*
>
> Hold your answer — the section below is the response.

The other shape of endpoint visibility: osquery answers **what is true right now**.

Where Sysmon *streams* events over time, osquery is a **flashlight** — you point a question at an endpoint (or all of them) and get the current state back as query results. "Which hosts have a process running from a path that no longer exists on disk?" is one SQL statement, and because the OS is modelled as tables, everything you know about databases transfers directly to endpoint analysis.

## Interactive queries first, scheduled ones after

`osqueryi` is the interactive shell; the same queries run scheduled via `osqueryd`:

```shell-session
analyst@host:~$ osqueryi
osquery> SELECT name, path, pid FROM processes WHERE on_disk = 0;
+-----------+------------------------+------+
| name      | path                   | pid  |
+-----------+------------------------+------+
| xmr-miner | /tmp/.x (deleted)      | 4471 |   ← process running from a deleted binary
+-----------+------------------------+------+
osquery> SELECT address, port, pid FROM listening_ports WHERE port = 4444;
```

High-value tables: `processes`, `listening_ports`, `users`, `logged_in_users`, `startup_items`/`autoexec`, `crontab`, `kernel_modules`, `installed_applications`, `file` (with hashes). A **manager** (FleetDM, Kolide) fans one query out to thousands of hosts — a live IR sweep in seconds.

## A snapshot cannot see what already exited

osquery's model is a **snapshot**, and that is its critical limitation:

```shell-session
# 10:00 scheduled query runs — clean
osquery> SELECT name FROM processes WHERE name LIKE '%mimikatz%';   -- 0 rows
# 10:03 attacker runs mimikatz.exe, dumps creds, deletes it
# 10:15 next scheduled query runs — clean again
osquery> SELECT name FROM processes WHERE name LIKE '%mimikatz%';   -- 0 rows
```

**The deliberate break:** osquery only sees what exists *at the moment it runs*. A malicious process that started and exited **between** two scheduled queries is completely invisible — the point-in-time model has gaps that a fast attacker slips through. This is exactly why osquery and **Sysmon** are complements, not substitutes: Sysmon's continuous *event stream* would have recorded the `ProcessCreate` for `mimikatz.exe` even though it lived for three minutes, while osquery is unbeatable for "what is the current state across my whole fleet?" (persistence, inventory, live IR). Use osquery for state and hunting sweeps; use Sysmon (or an EDR) for the ordered history — the diagram's "you want both." (osquery *does* have an evented-tables mode that narrows this gap, but the core shell is snapshot-based.)

**How you'd spot it:** the gap shows whenever an event stream disagrees with a snapshot: a `ProcessCreate` in Sysmon with no matching row in any osquery result lived entirely between two scheduled runs. With osquery alone, the tell is the schedule itself — an interval in minutes against tooling that finishes in seconds.

## Security Implications

**The snapshot gap is a coverage limitation an attacker exploits deliberately.** A process that starts and exits between two scheduled runs is invisible to osquery — [[Mimikatz]] living for three minutes leaves no row — which is exactly why osquery and [[Sysmon]] are complements: the event stream records the `ProcessCreate` the snapshot missed, and the snapshot answers the fleet-wide state question the stream cannot. A defence built on osquery alone has holes sized to its scheduling interval; evented tables narrow the gap but do not close it.

**Its own risk is cost, not compromise.** osquery is read-only, so it changes nothing — but an expensive query fanned across thousands of hosts by a manager (FleetDM, Kolide) is a self-inflicted load spike, so query cost and scheduling are the operational discipline. The results are also sensitive: a fleet-wide inventory of processes, ports and software is a map an attacker would love, so the osquery infrastructure and its data warrant protection.

**It turns hunting into a query the whole fleet answers at once.** "Which hosts run a process from a deleted binary" or "which have port 4444 listening" is one SQL statement across the estate — the live-IR strength that makes it worth the snapshot tradeoff, provided the event stream covers what it cannot see.

## Summary

You should now be able to:

- Explain why modelling an endpoint as SQL tables is powerful, and what question osquery answers.
- Write the query that finds processes running from a deleted binary, and name three other useful tables.
- Explain the snapshot blind spot with the mimikatz example, and why osquery and Sysmon are complements.

---
> 🔼 Up: [[Endpoint Telemetry Tools]]
