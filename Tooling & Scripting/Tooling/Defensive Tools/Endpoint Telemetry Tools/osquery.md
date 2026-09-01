---
title: "osquery"
aliases: ["osquery", "osqueryi"]
tags: [tree/tooling, cyber/tooling/defensive/osquery, type/tool, difficulty/medium]
Domain: "[[Endpoint Telemetry Tools]]"
Color: "#708090"
---

# osquery

osquery exposes an operating system as a **SQL database**. Running processes, listening ports, users, startup items, installed software, kernel modules — each becomes a table you can `SELECT` from with ordinary SQL, on Windows, Linux, and macOS alike. It turns "go check every endpoint for X" into a single query, which makes it the backbone of fleet-wide hunting, inventory, and incident response.

> [!warning] Read-only visibility
> osquery queries state; it doesn't change it. Run scheduled queries with care — an expensive query across a large fleet has a cost.

## Parent Learning Order
Sysmon -> osquery

## The flashlight: what is true right now

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

## Summary

You should now be able to:

- Explain why modelling an endpoint as SQL tables is powerful, and what question osquery answers.
- Write the query that finds processes running from a deleted binary, and name three other useful tables.
- Explain the snapshot blind spot with the mimikatz example, and why osquery and Sysmon are complements.

---
> 🔼 Up: [[Endpoint Telemetry Tools]]
