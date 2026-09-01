---
title: "RustScan"
aliases: ["Rust Port Scanner"]
tags: [tree/tooling, cyber/tooling/offensive/rustscan, type/tool, difficulty/medium]
Domain: "[[Network Discovery Tools]]"
Color: "#708090"
---

# RustScan

RustScan is a fast TCP port-discovery front end that finds open ports quickly and then **hands them to Nmap** for real service enumeration. It splits the job in two: a rapid Rust connect-scan for reachability, then Nmap for the fingerprinting Nmap does best. Its speed comes from concurrency tuning, which is also the one thing you must get right.

> [!warning] Fast defaults can be destructive
> A batch size that is comfortable on a LAN can exhaust sockets or crush an embedded target over a VPN. Tune from small, and keep the downstream Nmap stage rate-limited and in scope.

## Parent Learning Order
Nmap -> Masscan -> RustScan

## Letting the OS complete the handshake

RustScan uses the simplest probe of all: a full TCP `connect()`.

Unlike Masscan's stateless SYN or Nmap's half-open `-sS`, RustScan lets the OS complete the handshake (the "Connect -sT" row of the diagram) — so it needs **no root**, but the target application **does** see the connection. It races through ports with many concurrent sockets, collects the open set, and then invokes Nmap on just those ports. The model is "sprint to find the doors, then let Nmap describe each one."

## Everything after -- goes straight to Nmap

Everything after `--` is passed straight to Nmap, so all your Nmap knowledge transfers:

```shell-session
operator@lab:~$ rustscan -a 192.0.2.10 -p 22,80,443 -b 100 -t 1500 -- -sV --reason -oN evidence/web01.nmap
Open 192.0.2.10:22
Open 192.0.2.10:443
PORT    STATE SERVICE VERSION
22/tcp  open  ssh     OpenSSH 9.6
443/tcp open  https   nginx 1.24
```

The knobs that matter:

| Purpose | Option |
|---|---|
| Address | `-a`, `--addresses` |
| Ports | `-p`, `--range` |
| Batch size (concurrency) | `-b` |
| Per-socket timeout | `-t` (ms) |
| Skip Nmap | `--scripts none` |
| Nmap handoff | everything after `--` |

## Batch size against the file-descriptor ceiling

RustScan's speed is `-b` (batch size = simultaneous socket attempts), and that number collides directly with an OS limit: the **file-descriptor ceiling** (`ulimit -n`). Each in-flight connection is a socket = a descriptor; ask for more than the ceiling and the kernel refuses new sockets.

```shell-session
operator@lab:~$ ulimit -n
1024
operator@lab:~$ rustscan -a 192.0.2.10 -p 1-65535 -b 5000
[!] Too many open files. Try a smaller batch (-b) or raise ulimit -n.
```

**The deliberate break:** `-b 5000` against a 1024 descriptor limit **fails** — and worse, a slightly-too-high batch that *doesn't* error can silently drop probes, turning open ports into false negatives. The right method is a tuning sweep:

```shell-session
operator@range:~$ for b in 10 50 200; do /usr/bin/time -f "batch=$b elapsed=%e" rustscan -a 192.0.2.10 -p 1-1024 -b "$b" --scripts none; done
batch=10 elapsed=4.72
batch=50 elapsed=1.21
batch=200 elapsed=0.48
```

The fastest run is **not** automatically the best: validate that a known-open canary port still appears at your chosen batch. If it vanishes at `-b 200`, local or network pressure invalidated the optimisation — back off. Record `run_id`, ports, batch, timeout, and the exact downstream Nmap arguments, because the combined pipeline is otherwise impossible to reproduce.

## Summary

You should now be able to:

- Describe what RustScan does quickly, what it hands to Nmap, and why it needs no root.
- Write a RustScan command that finds open ports and runs `nmap -sV` on only those ports.
- Explain how batch size collides with `ulimit -n`, and why a too-high batch can cause false negatives rather than an error.

---
> 🔼 Up: [[Network Discovery Tools]]
