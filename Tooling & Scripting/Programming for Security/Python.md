---
title: "Python for Security Engineering"
aliases: ["Python Security", "Python"]
tags: [tree/tooling, cyber/tooling/programming/python, type/concept, difficulty/medium]
Domain: "[[Programming for Security]]"
Color: "#708090"
---

# Python for Security Engineering

Python is the default language of security tooling: fast to write, batteries-included, and backed by an ecosystem (`requests`, `scapy`, `impacket`, `pwntools`, `cryptography`) that covers most of what an operator or defender needs. When you need a tool *now*, Python is almost always the answer — the trick is knowing where its performance ceiling is and how to work with it.

> [!abstract] Note of [[Programming for Security]]
> Python is the default language of security tooling, and the one place it genuinely loses is the place people most often ask it to work. This note covers what the ecosystem buys you, why the interpreter refuses to parallelise CPU work no matter how many threads you start, and how to tell in one measurement which regime you are in.

> [!warning] Authorized use
> The libraries below send real traffic and handle real credentials. Use only in scope.

## Parent Learning Order
Python -> Go -> C++ -> Bash -> PowerShell

## The rapid-development corner of the map

> *You have a pure-Python hashing loop that takes eight seconds. You rewrite it to run across eight threads. How long does it take now?*
>
> Hold your answer — the section below is the response.

Python is the **rapid-development** corner of the language map, and the reason is not the language — it is that somebody has already written the hard part:

| The job | The library | What you are not writing |
|:--|:--|:--|
| HTTP, sessions, auth flows | `requests` / `httpx` | redirects, cookie jars, TLS verification |
| Crafting and reading packets | `scapy` | header layouts, checksums, raw sockets |
| SMB, Kerberos, NTLM, DCERPC | `impacket` | three decades of Windows protocol detail |
| Exploit development plumbing | `pwntools` | ROP assembly, cyclic patterns, process I/O |
| Hashing, signing, key handling | `cryptography` | primitives you must not implement yourself |

The last row is the one to take literally. Every other row is a matter of time saved; that one is a matter of not shipping a subtly broken cipher.

Reach for it when the task is prototyping, parsing, automation, or anything with a library that already exists — which is most security work. You trade raw speed and easy deployment for development velocity, and that's usually the right trade: a working Python tool today beats a fast Rust tool next month. The one thing to understand up front is *why* Python is slow at CPU-bound work, so you pick the right concurrency model instead of fighting the language.

> [!tip] The analogy, and where it breaks
> A single-lane counter with one clerk: however many customers queue up, only one is being served at a time, and hiring more clerks for that one counter changes nothing. The analogy breaks in the direction that matters — the clerk *does* step away and serve someone else whenever a customer has to go and fetch a document, which is why a program that spends its time waiting on sockets gets real concurrency from threads while one that spends its time computing gets none at all.

## A bounded async probe in a reproducible environment

A bounded async probe (I/O-bound → `asyncio` shines), in a reproducible environment:

```python
import asyncio
async def probe(host, port, timeout=2.0):
    try:
        _, w = await asyncio.wait_for(asyncio.open_connection(host, port), timeout)
        w.close(); return port, "open"
    except (asyncio.TimeoutError, ConnectionRefusedError, OSError):
        return port, "closed/filtered"

async def scan(host, ports, limit=200):
    sem = asyncio.Semaphore(limit)
    async def g(p):
        async with sem: return await probe(host, p)
    return await asyncio.gather(*(g(p) for p in ports))
```

Use a **virtualenv** (`python -m venv`), pin deps, add type hints + `mypy`, and write `pytest` tests on pure functions. The library reach is the point: `requests`/`httpx` for web, `scapy` for packets, `impacket` for AD, `cryptography` for crypto — don't reimplement what these do.

The `Semaphore` is the part worth not skipping. Without it, `asyncio.gather` over sixty-five thousand ports opens sixty-five thousand sockets at once, which exhausts file descriptors on your side and reads as a flood on the target's — the same unbounded-concurrency failure the Go note reaches from the other direction. Concurrency being cheap is not the same as concurrency being free.

**Prerequisites:** basic Python syntax, and what blocking on a socket means.

## The GIL, and the concurrency model it forces on you

The single most misunderstood thing in Python is the **GIL** (Global Interpreter Lock) — and it decides your concurrency model:

```python
# I/O-bound (network scan) — threads/async WORK, because the GIL releases during I/O waits
async def scan(...): ...                 # 200 ports "in parallel" — great

# CPU-bound (hashing millions of candidates) — threads DON'T help
from threading import Thread              # 8 threads → still ~1 core of work
#   the GIL lets only ONE thread run Python bytecode at a time
from multiprocessing import Pool          # THIS parallelises CPU work (separate processes)
```

**The deliberate break:** a beginner speeds up a CPU-heavy task (say, a pure-Python hasher) by spawning threads — and gets **no speedup**, because the GIL permits only one thread to execute Python bytecode at once. Threads only help when the work is **I/O-bound** (a scanner spends its time *waiting* on sockets, and the GIL is released during those waits, so `asyncio`/threads give real concurrency). For **CPU-bound** work you need `multiprocessing` (separate interpreters, separate GILs) — or you drop the hot loop into Go/C++ (the next rungs of the ladder). Knowing which regime you're in is the whole game: match `asyncio`/threads to I/O-bound tools (most of them) and `multiprocessing` to CPU-bound ones, and Python's "slowness" mostly stops mattering. When even that isn't enough, that's your signal to graduate to Go.

**How you'd spot it:** measure rather than reason. Run the same work with one worker and with eight and compare wall-clock: flat means you are CPU-bound and the GIL is serialising you, near-linear means the work was I/O-bound all along. Seen from the other side, it is one core pinned at 100% while the rest idle.

### The measurement, on a real box

Four hundred thousand SHA-256 iterations, split across a growing number of workers, first as threads and then as processes. CPython 3.11 on a two-core machine:

```text
cpus: 2
threads k=1  0.27s
threads k=4  0.31s
threads k=8  0.31s
procs   k=1  0.30s
procs   k=4  0.16s
procs   k=8  0.16s
```

The thread rows answer the opening question: eight threads is not faster, and is very slightly *slower* than one. That extra 0.04s is real — it is the cost of eight threads contending for a lock only one of them can hold. Adding workers to a GIL-bound task buys scheduling overhead and nothing else.

The process rows are the correction, and they stop where the machine does. Four processes halve the time; eight processes do not improve on four, because there are two cores and the work was already saturating both. That is the second half of the lesson and the half people skip: `multiprocessing` is bounded by cores, not by the number you pass it, so a worker count above the core count is as inert as the threads were.

Note also `procs k=1` at 0.30s against `threads k=1` at 0.27s. Spawning a process costs something, so on small workloads the parallel version can lose outright. The regime question is worth asking before the concurrency question — a task too small to saturate one core does not need either.

## Security Implications

**Installing a dependency executes code.** `pip install` runs the package's build steps, so a compromised or typosquatted package on the index is arbitrary code execution on the machine that installed it, at install time, before a line of your program runs. Pinning versions and hashes and installing into a virtualenv rather than system-wide is the baseline, and vetting a new dependency before adding it is worth more than any runtime control.

**`pickle` is remote code execution by design, not by accident.** Deserialising a pickle constructs objects by calling whatever the stream says to call, so any pickle from an untrusted source is a command to run. It is the natural-looking choice for caching results or passing state between processes, and it is the wrong one at any boundary an attacker can reach. JSON where the data is data; a signed format where it must be richer.

**`subprocess` with `shell=True` reintroduces the Bash problem.** Passing a command as one string hands it to a shell, so any interpolated value becomes shell syntax — the same word-splitting-into-injection path the Bash note covers, imported into a language that did not have it. Pass an argument list instead and no shell is involved at all.

**A Python tool ships its source, which cuts both ways.** An operator can read exactly what a tool does before running it against a client's estate, which is a genuine advantage over a binary. The same property means anything embedded in it — a key, a token, a client name — is readable by whoever obtains the script, and "compiled" `.pyc` files are trivially decompiled rather than protective.

**Timing matters in the wrong places.** Comparing secrets with `==` leaks length and prefix through timing; `hmac.compare_digest` exists for that reason. It is a small habit and the kind of detail a fast-to-write language makes easy to skip.

All automation described here must target systems within an authorized scope. The libraries above send real traffic and handle real credentials, and a script that works is a script that works against production.

## Summary

You should now be able to:

- Explain why Python is the default for security tooling and what it trades away; name the library that already solves each common security task and say which one you must never replace by hand.
- Write a bounded async probe, explain what the semaphore prevents, and run the one measurement that tells you whether a workload is CPU-bound or I/O-bound.
- Explain the GIL and why threads speed up a scanner but not a pure-Python hasher; explain why `multiprocessing` stops improving at the core count rather than the worker count, and why installing a dependency, unpickling a message, and calling `subprocess` with `shell=True` are each code execution wearing ordinary clothes.

---
> 🔼 Up: [[Programming for Security]]
