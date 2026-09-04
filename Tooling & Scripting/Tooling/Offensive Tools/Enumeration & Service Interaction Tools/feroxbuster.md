---
title: "feroxbuster"
aliases: ["feroxbuster"]
tags: [tree/tooling, cyber/tooling/offensive/enumeration/feroxbuster, type/tool, difficulty/medium]
Domain: "[[Enumeration & Service Interaction Tools]]"
Color: "#708090"
---

# feroxbuster

feroxbuster is a fast, Rust-based content-discovery tool whose signature feature is **automatic recursion**: when it finds a directory, it immediately starts brute-forcing inside it, walking the tree without you re-running scans by hand. Where Gobuster is a flat sweep, feroxbuster maps depth — ideal for nested application paths.

> [!warning] Authorized targets only
> Recursive brute-forcing multiplies requests fast. Scope the target, cap the rate, and bound recursion depth to avoid hammering the app.

## Parent Learning Order
Gobuster -> ffuf -> feroxbuster -> dirsearch -> Netcat -> enum4linux

## Recursion as the one added idea

> *A scan turns up `/admin/`. What does a flat brute-forcer do next?*
>
> Hold your answer — the section below is the response.

feroxbuster reads the same signals as every content-discovery tool — the HTTP status code and response size — but adds one idea: **when a directory turns up, dig into it automatically.**

A `301` redirect to `/admin/` isn't an endpoint, it's a *door*; feroxbuster walks through it and keeps brute-forcing `/admin/*` without you lifting a finger. That recursion is powerful and dangerous in equal measure — it also multiplies your request count and your exposure to the soft-404 trap at every level.

## Watching it dig into what it finds

```shell-session
operator@lab:~$ feroxbuster -u http://track.meridian.test -w raft-medium.txt
 200  GET  http://track.meridian.test/index.html
 301  GET  http://track.meridian.test/admin => /admin/
 200  GET  http://track.meridian.test/admin/login.php
 301  GET  http://track.meridian.test/admin/uploads => /admin/uploads/
 200  GET  http://track.meridian.test/admin/uploads/readme.txt
```

Notice it found `/admin`, then **auto-recursed** to `/admin/login.php` and `/admin/uploads/` — a flat scanner stops at `/admin`. The control flags:

| Flag | Does |
|---|---|
| `-x php,txt` | append extensions |
| `-d 2` | cap recursion depth |
| `-C 404,403` | drop status codes |
| `--filter-size 1520` | drop a constant soft-404 body |
| `-t` / `--rate-limit` | threads / throttle |
| `--extract-links` | scrape found responses for new paths to queue |

One feature genuinely separates it from the other three fuzzers: with `--extract-links` it does not only brute-force, it **reads the responses it gets back** and pulls hrefs, script `src`s and other paths out of them, feeding those into the same recursive queue. A pure brute-forcer finds only what its wordlist contains; feroxbuster also finds what the application itself links to, which is often the paths that are not in any wordlist.

## How a soft-404 makes recursion explode

```shell-session
operator@lab:~$ feroxbuster -u http://track.meridian.test -w list.txt
 200  GET  /app/config/  => /app/config/db.php.bak
 200  GET  /randomxyz123    (size 1520)   <-- everything returns 200?
operator@lab:~$ feroxbuster -u http://track.meridian.test -w list.txt --filter-size 1520
 200  GET  /app/config/db.php.bak
```

**The deliberate break:** the server returns `200` with a fixed 1520-byte "not found" page for *every* path — and because feroxbuster **recurses on 200s**, a soft-404 doesn't just add noise, it makes the tool recurse into non-existent directories, exploding the run. Filtering the constant size (`--filter-size`) both recovers the real file (`db.php.bak`) and stops the runaway recursion. The lesson from Gobuster/ffuf is amplified here: with recursion, calibrating against soft-404s isn't optional, it's what keeps the scan finite.

**How you'd spot it:** recursion makes this loud rather than subtle. Watch queue depth and request rate: a run that keeps discovering fresh directories several levels down, every one returning the same byte count, is recursing into paths that do not exist. Stop it and read the size column before restarting with a filter.

Cap depth with `-d` on large sites (unbounded recursion brute-forces every discovered directory forever), and emit a report rather than scraping the console so status, size, and redirect target survive for the finding.

## Security Implications

**Recursion is the signature, not just the feature.** A flat scanner requests a fixed list; feroxbuster's requests get *progressively deeper* from one source, exploring paths in an order no human browsing session ever produces — `/admin`, then everything under it, then everything under what that found. That depth-first tree walk is a distinctive detection, and the default `User-Agent: feroxbuster/2.x` confirms it.

**The soft-404 is an amplified availability risk here.** Because the tool recurses on `200`s, a server that answers every path with `200` makes it recurse into directories that do not exist, at every level — a runaway that multiplies load on the target as well as noise in the output. Calibrating the soft-404 size is what keeps the run finite, so on a recursive scanner it is a safety control, not only an accuracy one.

**Depth is a scope decision.** Uncapped recursion on a large site is thousands of requests the engagement did not budget for; `-d` and `--rate-limit` bound both the load and the exposure. A recursive run against production without them is how a content-discovery pass becomes a denial of service.

All discovery here targets only authorised scope.

## Summary

You should now be able to:

- Explain what feroxbuster's automatic recursion does that a flat brute-forcer does not.
- Diagnose a run in which every path returns `200`, and recover the real files.
- Explain why a soft-404 is *worse* for a recursive scanner than a flat one, and how filtering fixes both problems.

---
> 🔼 Up: [[Enumeration & Service Interaction Tools]]
