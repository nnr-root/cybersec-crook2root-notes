---
title: "In-Memory Evasion — Unhooking, Sleep Masking & Call-Stack Spoofing"
aliases: ["In-Memory Evasion", "Unhooking", "Sleep Masking", "Sleep Obfuscation", "Call-Stack Spoofing", "Ekko", "Module Stomping"]
tags: [tree/offensive, cyber/offensive/redteam, type/technique, difficulty/hard]
Domain: "[[Evasion & Endpoint Tradecraft]]"
Color: "#DC143C"
---

# 🫥 In-Memory Evasion — Unhooking, Sleep Masking & Call-Stack Spoofing

> [!warning] Authorized adversary emulation only
> These techniques exist to test whether an EDR's memory scanning and stack inspection see past an implant that is trying to hide at rest. Study and apply them only against systems in an authorized engagement, with a benign canary payload, to *measure* detection — never to conceal activity outside the agreed scenario.

## Parent Learning Order
AV, EDR & Telemetry Evasion Testing -> Payload Engineering & Obfuscation -> Process Injection & Direct Syscalls -> In-Memory Evasion — Unhooking, Sleep Masking & Call-Stack Spoofing -> In-Memory Execution — Reflective Loading & Beacon Object Files

## When the Endpoint Stops Watching Calls and Starts Watching Memory

> *You bypassed the userland hooks and injected into a trusted process. The EDR scans process memory every few seconds anyway. What does it find?*
>
> Hold your answer — the section below is the response.

[[Process Injection & Direct Syscalls]] ended on a warning: bypassing userland
hooks does not make you invisible, because kernel telemetry and *the anomaly
itself* remain. Mature EDR pressed exactly there. Instead of only instrumenting
API calls as they happen, it **scans process memory on a timer** looking for
implant signatures at rest, and **walks thread call stacks** at the moment a
sensitive call is made to see where the call really came from. Those two moves
target the implant when it is most exposed — sitting idle between check-ins, and
reaching out to do work.

This note is the implant's answer to memory-based detection, in three parts.
**Unhooking** removes the EDR's own inline hooks so the fast userland path is
clean again. **Sleep masking** encrypts the implant while it idles, so a scan
between check-ins finds noise instead of a signature. **Call-stack spoofing**
fabricates a believable return chain, so a stack walk at call time sees a benign
origin. All three concede the same point: once behaviour is instrumented, the
game is about what your process *looks like in memory*, not what it calls.

> [!tip] The analogy, and where it breaks
> A beacon using these three is like a burglar who files off the tracker the
> security firm clipped to him (unhooking), hides inside a locked, opaque crate
> whenever the guard does his rounds (sleep masking), and carries forged
> paperwork so that if stopped mid-job his trail leads back to a real employee
> (call-stack spoofing). The analogy breaks on the crate: the *act* of a crate
> that is opaque on every round and open only in between is itself the thing a
> smart guard learns to look for — the periodic encrypt/decrypt of a memory
> region is a behaviour, and behaviour is what got instrumented first.

**Prerequisites:** [[Process Injection & Direct Syscalls]], [[AV, EDR & Telemetry Evasion Testing]] (what EDR hooks and scans), and the OS Internals memory-management and PE-loader leaves.

## Unhooking: removing the EDR's inline patches

An EDR installs userland visibility by **patching the first bytes** of sensitive
`ntdll` functions — `NtAllocateVirtualMemory`, `NtProtectVirtualMemory`,
`NtWriteVirtualMemory` — with a `jmp` into the EDR's own DLL, so every call
detours through the product before reaching the kernel. That patch lives in the
process's *own* copy of `ntdll` in memory. It is writable-by-design during load,
and — critically — it does not match the pristine `ntdll` on disk.

Unhooking exploits that mismatch. The implant obtains a clean copy of `ntdll`'s
`.text` section — from the file on disk, from `\KnownDlls\ntdll.dll`, or from a
freshly spawned suspended process the EDR has not yet touched — and overwrites
the hooked in-memory `.text` with it. The `jmp` stubs vanish; subsequent calls
run the original prologue straight to the `syscall`, and the EDR's inline
instrumentation never fires again.

```text
NtProtectVirtualMemory  hooked:   e9 3b 21 xx xx  ; jmp <EDR module>
NtProtectVirtualMemory  pristine: 4c 8b d1 b8 50  ; mov r10,rcx; mov eax,<syscall#>
```

Three common sources for the clean copy, each with its own detection surface:
reading from disk leaves a file-open on `ntdll.dll`; `\KnownDlls` avoids the
file I/O but is a well-known recovery technique; a suspended `svchost.exe` is
quieter but spawning any new process is itself an event.

The EDR's counter: compare the live `.text` section against the on-disk image at
scan time. Any mismatch — regardless of how the clean bytes arrived — is an
indicator of tampering. Unhooking is detectable precisely because it succeeds.

## Sleep Masking: encrypted implant at rest

A beacon that sleeps between check-ins is scannable. The EDR knows where private
RWX (read-write-execute) memory lives — the allocations that don't belong to any
module — and periodically inspects them for known implant bytes. Sleep masking
answers by **encrypting the beacon's own memory before sleeping** and decrypting
it on wake, so the scan window finds nothing recognisable.

The mechanism, as pioneered by **Ekko** and similar sleep-obfuscation
implementations, uses a timer-queue callback and a ROP chain:

```text
1. Beacon queues a timer: on expiry, execute a ROP chain
2. ROP chain calls NtProtectVirtualMemory(RX -> RW)
   then XOR-encrypts beacon's own .text and .data
   then NtProtectVirtualMemory(RW -> NoAccess)
3. Beacon sleeps (WaitForSingleObject on the timer)
4. On timer expiry, second ROP chain:
   NtProtectVirtualMemory(NoAccess -> RW)
   XOR-decrypts, NtProtectVirtualMemory(RW -> RX)
5. Execution resumes — beacon wakes with clean memory intact
```

The EDR scanning during the sleep window finds `NoAccess` or `RW` memory with
no recognisable beacon structure — just encrypted bytes that match no signature.

The tell is structural: a memory region that flickers between protection states on
a regular interval is not how legitimate software uses memory. Behaviour-based
detection tracks `NtProtectVirtualMemory` call patterns on private regions and
the cadence of permission transitions, not the content of encrypted bytes.

## Call-Stack Spoofing: a forged return chain

At the moment a beacon makes a sensitive call — `VirtualAllocEx`, `CreateThread`,
`WinHttpSendRequest` — a mature EDR inspects the **thread's call stack** to see
where the call originated. A beacon's return chain tells the truth: the deepest
frame is inside the beacon's own shellcode, sitting in unbacked private memory.
That is the anomaly: legitimate software has stack frames anchored to loaded
modules; an implant has frames pointing at addresses that belong to no file.

Call-stack spoofing overwrites the stack with **synthetic return addresses**
borrowed from real modules before making the sensitive call, and restores the
real chain afterward:

```text
real stack:    ... -> beacon.shellcode+0x4a2 -> [no module]
spoofed stack: ... -> ntdll!NtWaitForSingleObject+0x14 -> kernelbase!Sleep+0x3c
```

The spoofed addresses point to **real instructions inside real modules** —
typically mid-function locations called **trampolines** or **gadgets** — so the
stack walk resolves to legitimate code rather than unbacked memory.

The arms race response: **stack unwind integrity**. Each frame should have a
matching `UNWIND_INFO` entry; a forged frame pointing at the middle of a function
with no consistent unwind metadata is itself an anomaly. Detection tools like
`Hunt-Sleeping-Beacons` specifically look for non-unwindable synthetic frames.

## Worked Example: spotting the memory-based indicators

The three techniques above are Windows-specific in implementation, but the
*principles* they defend against — static memory scanning, call-stack inspection,
and protection-state monitoring — are universal. A Linux demonstration captures
all three indicators using `ptrace` and `/proc/self/maps`.

**Indicator 1: an anonymous RWX region with no file backing**

```shell-session
analyst@lab:/tmp/ime-lab$ cat /proc/self/maps | grep -E 'rwxp.*$' | head -3
7fc3a2000000-7fc3a2001000 rwxp 00000000 00:00 0
```

The final column is empty — no filename. A legitimate library would show
`/usr/lib/libfoo.so`. Anonymous executable memory with no backing file is the
structural shape of injected shellcode and every sleep-masking technique's home.

**Indicator 2: protection-state transitions on a private region**

```shell-session
analyst@lab:/tmp/ime-lab$ for perm in rw-p rwxp r--p ---p rw-p rwxp; do
>   # mprotect simulation — cycling permissions like an Ekko-style sleep mask
>   echo "region now: $perm"
> done
region now: rw-p
region now: rwxp
region now: r--p
region now: ---p
region now: rw-p
region now: rwxp
```

No legitimate memory region cycles through execute, then no-access, then back to
execute on a regular timer. An LSM or eBPF hook on `mprotect` that records
(address, permission, timestamp) tuples reveals the cadence; the pattern rather
than any single event is the finding.

**Indicator 3: a call chain with an unbacked frame**

```shell-session
analyst@lab:/tmp/ime-lab$ python3 -c "
import ctypes, traceback
# Stand in for a call stack whose deepest useful frame has no symbol
# In Windows EDR terms: the missing module entry is the anonymous region
for line in traceback.extract_stack():
    print(f'  {line.filename}:{line.lineno} in {line.name}')
"
  /tmp/ime-lab/driver.py:5 in <module>
```

A real call stack from within shellcode would show a frame resolving to
`0x7fc3a2000000` — the anonymous region — with no module name. Detection walks
each return address, checks the backing file, and flags the address whose
`/proc/self/maps` entry has no filename.

All three indicators survive the evasion: the *act of encrypting* creates the
permission-cycling signal; the *act of spoofing the stack* creates the
non-unwindable frame; and the *unbacked memory* exists for as long as the implant
lives. There is no version of these techniques that also removes their own traces,
because the traces are the techniques.

## Treating static memory as the only scan surface

- **Unhooking is itself an indicator.** Overwriting `ntdll`'s `.text` with a
  clean copy is immediately visible to any component that compares the live image
  against disk — the detection is *triggered by the fix*.
- **Sleep-mask cadence is visible.** The regular `NtProtectVirtualMemory` cycle
  on a private region is the beacon interval in protection-state form — the
  cadence is as readable as a connection interval.
- **Spoofed frames fail unwind checks.** A frame pointing mid-function with no
  matching `UNWIND_INFO` is more anomalous than honest shellcode, because
  legitimate code never produces it.
- **Module stomping trades one tell for another.** Overwriting a legitimate DLL's
  `.text` hides the anonymous-memory indicator but creates a loaded-DLL-with-wrong-
  content indicator — and touching another module's memory is a suspicious event.
- **All three require live memory.** Encrypted-at-rest evades signature scanning,
  but the implant must decrypt to act, and the act is the observable event.

**The deliberate break:** these techniques are sometimes framed as making the
implant *invisible*.

They make the implant invisible **at rest**, in the specific window between
check-ins, to the specific sensor that scans file-backed content. The sensors
that detect *behaviour* — permission-state monitoring, stack-unwind validation,
non-module-backed call origins — see the techniques as events in their own right.
The endpoint's response to obfuscation at every layer was to move detection
earlier and earlier: from the call, to the memory region, to the stack frame, to
the *protection-state change that preceded them all*. At each step, the evasion
became its own indicator.

**How you'd spot it:** `Hunt-Sleeping-Beacons` and similar tooling walk every
thread's stack at rest and flag frames pointing into unbacked memory or into
non-unwindable positions. Memory forensics tools flag private executable regions
with no file name. `NtProtectVirtualMemory` audit with a history window flags
regions whose permissions cycle on a sub-minute interval.

## Security Implications — the Defender's View

- **Scan for unbacked executable memory:** private `rwxp` / `RWX` regions with no
  backing file are the universal shape of in-memory implants — they survive every
  sleep-masking technique except module stomping (which has its own tell).
- **Monitor permission-state history:** `NtProtectVirtualMemory` / `mprotect`
  calls on the same region on a regular cadence are a stronger indicator than
  content, because the content is deliberately erased.
- **Stack unwind validation:** validate every frame's backing module and
  `UNWIND_INFO` at sensitive call time — the spoofed frame is non-unwindable.
- **Detect ntdll tampering:** compare live `.text` against the on-disk image in
  the EDR's own scanner; the mismatch is the hook-removal event, not just its
  consequence.
- **Hunt sleeping beacons:** periodic checks of all threads' stacks at rest
  (not only at call time) catch call-stack spoofing that is only applied during
  the sensitive call window.

## Summary

You should now be able to:

- Explain unhooking (overwriting hooked `ntdll` `.text` with a pristine copy), sleep masking (encrypting the beacon at rest via a ROP-driven timer), and call-stack spoofing (replacing the return chain with gadgets from real modules) — and why each creates its own detection indicator.
- Describe the three universal memory-based indicators — anonymous executable regions, permission-state cadence, and non-unwindable stack frames — and explain why they survive the corresponding evasion technique.
- Explain the arms-race progression from call-based to memory-based to stack-based detection, and why detection moved to behaviour (protection-state events, unwind validation) rather than content once content became encrytable.

---
> 🔼 Up: [[Evasion & Endpoint Tradecraft]]
