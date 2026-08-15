---
title: "Building Network Scanners"
aliases: ["Building Network Scanners", "Writing a Port Scanner"]
tags: [tree/tooling, cyber/tooling/development/scanners, type/concept, level/operator]
Domain: "[[Writing Your Own Tools]]"
Color: "#708090"
---

# Building Network Scanners

Writing your own port scanner is the classic exercise that turns "I use Nmap" into "I understand what Nmap does." A scanner is the tool architecture from the previous note applied to sockets — and the part that separates a real scanner from a `for` loop is **concurrency and rate control**.

> [!warning] Authorized targets only
> A scanner sends packets to hosts. Test only against your own lab or an authorized scope, and bound the rate.

## Parent Learning Order
Security Tool Architecture & Design Patterns -> Building Network Scanners -> Command & Control Design Principles -> Hashsmith Tool Architecture -> ShadowStep Tool Architecture

## Crook — The Mental Model

A scanner is the architecture layers with a network-shaped engine.

![[tool_build_architecture.svg]]

The **core engine** is one tiny question — "is this port open?" — answered by attempting a connection and reading the result (open / closed / no-reply, exactly the states in the Nmap note). The **plugins** are scan techniques (connect vs. raw SYN). And the layer that makes it a *scanner* rather than a script is **concurrency + rate**: you must probe thousands of ports in parallel, safely. Get the engine right and the whole thing is small; get the concurrency wrong and it's either uselessly slow or dangerously abusive.

## Operator — Make It Work

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

## Root — Internals & The Deliberate Break

Two mistakes turn a working scanner into a broken one — both in the concurrency/rate layer:

```python
# UNBOUNDED: fire all 65,535 at once
await asyncio.gather(*(probe(host, p) for p in range(1, 65536)))
# → OSError: [Errno 24] Too many open files   (each socket = an fd; you blew ulimit -n)
#   and on the target side: a SYN flood you didn't mean to send.

# NO TIMEOUT: a filtered port never answers
await asyncio.open_connection(host, 445)   # ...hangs indefinitely, scan never finishes
```

**The deliberate break:** unbounded concurrency exhausts the OS file-descriptor limit (`ulimit -n`) *and* floods the target — a self-inflicted DoS on both ends — while a missing timeout makes the scan hang forever on the first filtered port (silence is a valid result you must handle, not wait on). Both are the concurrency/rate layer of the architecture doing its job: a semaphore bounds in-flight sockets to something the OS and the target can bear, and a per-probe timeout turns "no reply" into a decision instead of a hang. This is *exactly* the lesson RustScan's batch-size tuning teaches from the user side — building the scanner yourself is how you learn why those knobs exist. The engine (probe one port) is ten lines; the craft is entirely in bounding and timing the parallelism.

## Crook → Operator → Root Checkpoint

- **Crook:** What is a scanner's "engine," and which architecture layer makes it more than a `for` loop?
- **Operator:** Write a bounded async probe with a timeout, and explain why each is necessary.
- **Root:** Explain the two failure modes of unbounded/untimed scanning, and how a semaphore and a timeout fix them.

---
> 🔼 Up: [[Writing Your Own Tools]]
