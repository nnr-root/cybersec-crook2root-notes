---
title: "feroxbuster"
aliases: ["feroxbuster"]
tags: [tree/tooling, cyber/tooling/offensive/enumeration/feroxbuster, type/tool, level/operator]
Domain: "[[Enumeration & Service Interaction Tools]]"
Color: "#708090"
---

# feroxbuster

feroxbuster is a fast, Rust-based content-discovery tool whose signature feature is **automatic recursion**: when it finds a directory, it immediately starts brute-forcing inside it, walking the tree without you re-running scans by hand. Where Gobuster is a flat sweep, feroxbuster maps depth — ideal for nested application paths.

> [!warning] Authorized targets only
> Recursive brute-forcing multiplies requests fast. Scope the target, cap the rate, and bound recursion depth to avoid hammering the app.

## Parent Learning Order
Gobuster -> ffuf -> feroxbuster -> dirsearch -> Netcat -> enum4linux

## Crook — The Mental Model

feroxbuster reads the same signals as every content-discovery tool — the HTTP status code and response size — but adds one idea: **when a directory turns up, dig into it automatically.**

![[tool_content_discovery_status.svg]]

A `301` redirect to `/admin/` isn't an endpoint, it's a *door*; feroxbuster walks through it and keeps brute-forcing `/admin/*` without you lifting a finger. That recursion is powerful and dangerous in equal measure — it also multiplies your request count and your exposure to the soft-404 trap at every level.

## Operator — Make It Work

```shell-session
operator@lab:~$ feroxbuster -u http://app.example.test -w raft-medium.txt
 200  GET  http://app.example.test/index.html
 301  GET  http://app.example.test/admin => /admin/
 200  GET  http://app.example.test/admin/login.php
 301  GET  http://app.example.test/admin/uploads => /admin/uploads/
 200  GET  http://app.example.test/admin/uploads/readme.txt
```

Notice it found `/admin`, then **auto-recursed** to `/admin/login.php` and `/admin/uploads/` — a flat scanner stops at `/admin`. The control flags:

| Flag | Does |
|---|---|
| `-x php,txt` | append extensions |
| `-d 2` | cap recursion depth |
| `-C 404,403` | drop status codes |
| `--filter-size 1520` | drop a constant soft-404 body |
| `-t` / `--rate-limit` | threads / throttle |

## Root — Internals & The Deliberate Break

```shell-session
operator@lab:~$ feroxbuster -u http://app.example.test -w list.txt
 200  GET  /app/config/  => /app/config/db.php.bak
 200  GET  /randomxyz123    (size 1520)   <-- everything returns 200?
operator@lab:~$ feroxbuster -u http://app.example.test -w list.txt --filter-size 1520
 200  GET  /app/config/db.php.bak
```

**The deliberate break:** the server returns `200` with a fixed 1520-byte "not found" page for *every* path — and because feroxbuster **recurses on 200s**, a soft-404 doesn't just add noise, it makes the tool recurse into non-existent directories, exploding the run. Filtering the constant size (`--filter-size`) both recovers the real file (`db.php.bak`) and stops the runaway recursion. The lesson from Gobuster/ffuf is amplified here: with recursion, calibrating against soft-404s isn't optional, it's what keeps the scan finite.

Cap depth with `-d` on large sites (unbounded recursion brute-forces every discovered directory forever), and emit a report rather than scraping the console so status, size, and redirect target survive for the finding.

## Crook → Operator → Root Checkpoint

- **Crook:** What does feroxbuster's automatic recursion do that a flat brute-forcer doesn't?
- **Operator:** Every path returns `200`. What's happening, and how do you recover the real files?
- **Root:** Explain why a soft-404 is *worse* for a recursive scanner than a flat one, and how filtering fixes both problems.

---
> 🔼 Up: [[Enumeration & Service Interaction Tools]]
