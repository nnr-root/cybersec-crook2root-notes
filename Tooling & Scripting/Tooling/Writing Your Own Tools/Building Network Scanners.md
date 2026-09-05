---
title: "Building Network Scanners"
aliases: ["Building Network Scanners", "Writing a Port Scanner"]
tags: [tree/tooling, cyber/tooling/development/scanners, type/concept, difficulty/medium]
Domain: "[[Writing Your Own Tools]]"
Color: "#708090"
verified: 2026-09-05
---

# Building Network Scanners

Writing your own port scanner is the classic exercise that turns "I use Nmap" into "I understand what Nmap does." A scanner is the tool architecture from the previous note applied to sockets — and the part that separates a real scanner from a `for` loop is **concurrency and rate control**.

> [!warning] Authorized targets only
> A scanner sends packets to hosts. Test only against your own lab or an authorized scope, and bound the rate.

## Parent Learning Order
Security Tool Architecture & Design Patterns -> Building Network Scanners -> Command & Control Design Principles -> Hashsmith Tool Architecture -> ShadowStep Tool Architecture

## One tiny question, answered concurrently

> *Strip a port scanner back to its core. What single question is it asking?*
>
> Hold your answer — the section below is the response.

A scanner is the architecture layers with a network-shaped engine.

The **core engine** is one tiny question — "is this port open?" — answered by attempting a connection and reading the result (open / closed / no-reply, exactly the states in the Nmap note). The **plugins** are scan techniques (connect vs. raw SYN). And the layer that makes it a *scanner* rather than a script is **concurrency + rate**: you must probe thousands of ports in parallel, safely. Get the engine right and the whole thing is small; get the concurrency wrong and it's either uselessly slow or dangerously abusive.

## A bounded async probe behind a semaphore

The engine is a bounded async connect probe; concurrency is a semaphore:

```python
import asyncio
async def probe(host, port, timeout=2.0):          # the pure engine
    try:
        _, w = await asyncio.wait_for(asyncio.open_connection(host, port), timeout)
        w.close(); return port, "open"
    except asyncio.TimeoutError: return port, "filtered"   # no reply
    except ConnectionRefusedError: return port, "closed"

async def scan(host, ports, concurrency=200):      # bounded concurrency
    sem = asyncio.Semaphore(concurrency)
    async def guarded(p):
        async with sem: return await probe(host, p)
    return await asyncio.gather(*(guarded(p) for p in ports))
```

Every probe has a **timeout** (or a filtered port hangs forever), concurrency is **capped** by a semaphore, and results are structured `(port, state)` tuples ready for JSON. Add `--rate` to throttle, and you have the skeleton of RustScan.

Run against a host with three listeners open, the engine returns typed states in milliseconds:

```shell-session
operator@lab:~$ python3 scan.py 127.0.0.1 --ports 22,80,443,8022,8080,9000,3306
127.0.0.1:8022  open
127.0.0.1:8080  open
127.0.0.1:9000  open
# 7 ports, concurrency=50, 3 ms
```

## Why the concurrency number is not a guess

The semaphore's value is not a taste preference — it falls directly out of the timeout. A scan's wall-clock time is roughly `ports × timeout ÷ concurrency`, because the only slow ports are the *filtered* ones that must wait the full timeout before giving up; open and closed ports answer in a round-trip. Scanning 200 unroutable (therefore filtered) ports at a half-second timeout makes the relationship exact:

```shell-session
200 filtered ports, timeout=0.5s, concurrency=10  -> 10.04s
200 filtered ports, timeout=0.5s, concurrency=50  -> 2.01s
200 filtered ports, timeout=0.5s, concurrency=200 -> 0.51s
```

Ten in flight means twenty sequential half-second waits; two hundred in flight means one. That is why concurrency and timeout are chosen *together*: a long timeout is affordable only with high concurrency, and high concurrency is safe only up to what the OS and the target can bear — which is the exact tension the next section is about. It is also why a scanner over the open internet uses a shorter timeout than one on a LAN: the round-trip budget is different, so the whole arithmetic shifts.

## Two concurrency mistakes that break a working scanner

Two mistakes turn a working scanner into a broken one — both in the concurrency/rate layer:

```python
# UNBOUNDED: fire all 65,535 at once
await asyncio.gather(*(probe(host, p) for p in range(1, 65536)))

# NO TIMEOUT: a filtered port never answers
await asyncio.open_connection(host, 445)   # ...hangs indefinitely, scan never finishes
```

The first is not a hypothetical. Each in-flight connection holds a file descriptor, and the OS caps how many a process may hold; fire tens of thousands at once and you hit the ceiling before the target does:

```shell-session
operator@lab:~$ python3 unbounded.py          # ulimit -n is 256 here for the demo
OSError: [Errno 24] Too many open files
```

That is a self-inflicted failure *on your own host* — and on the target side, tens of thousands of simultaneous SYNs is a flood you did not mean to send.

**The deliberate break:** unbounded concurrency exhausts the OS file-descriptor limit (`ulimit -n`) *and* floods the target — a self-inflicted DoS on both ends — while a missing timeout makes the scan hang forever on the first filtered port (silence is a valid result you must handle, not wait on). Both are the concurrency/rate layer of the architecture doing its job: a semaphore bounds in-flight sockets to something the OS and the target can bear, and a per-probe timeout turns "no reply" into a decision instead of a hang. This is *exactly* the lesson RustScan's batch-size tuning teaches from the user side — building the scanner yourself is how you learn why those knobs exist. The engine (probe one port) is ten lines; the craft is entirely in bounding and timing the parallelism.

**How you'd spot it:** two distinct symptoms, two different causes. `too many open files`, or progress stalling at a fixed number of in-flight sockets, is the descriptor limit meeting unbounded concurrency. A scan that stops advancing and never finishes is the missing timeout — silence is a legitimate result, and code that waits on it forever has confused "no answer" with "not answered yet".

## Summary

You should now be able to:

- Define a scanner's "engine", and name the architecture layer that makes it more than a `for` loop.
- Write a bounded async probe with a timeout, and explain why each is necessary.
- Explain the two failure modes of unbounded/untimed scanning, and how a semaphore and a timeout fix them.

---
> 🔼 Up: [[Writing Your Own Tools]]
