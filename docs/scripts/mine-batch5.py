#!/usr/bin/env python3
"""Offensive Security worked examples — batch 5 (Exploit Development, final)."""
import re
import sys

RELIABILITY = '''## Worked Example: Why a Working Exploit Needs Two Bugs

An exploit that hardcodes an address is not an exploit; it is a coin flip. The
reason is visible in three runs of a program that does nothing but print where a
libc function landed.

```shell-session
analyst@lab:/tmp/rel-lab$ for i in 1 2 3; do ./leak; done
0x7f3a2c1b4e40
0x7f9c81a35e40
0x7f14b6d02e40
```

Three runs, three addresses. That is ASLR: the loader picks a new base for the
shared library each execution, so `printf` — the same function, in the same
library, in the same binary — is never twice in the same place.

Look closely at what *did* stay constant, though: every address ends in `e40`.
The randomisation happens at page granularity, so the low twelve bits are fixed
by the offset within the library. An attacker who learns any single libc address
therefore learns them all, because the distances between functions inside the
library never change.

**That is exactly what a leak buys**, and disabling ASLR shows the world the
attacker is trying to reach:

```shell-session
analyst@lab:/tmp/rel-lab$ for i in 1 2 3; do setarch "$(uname -m)" -R ./leak; done
0x7ffff7a5ee40
0x7ffff7a5ee40
0x7ffff7a5ee40
```

Identical every run, so any address computed from it is deterministic and the
exploit fires every time.

**This is the two-bug requirement**, and it is the single most important
structural fact about modern exploitation. The first bug leaks an address — a
format string reading up the stack, an uninitialised buffer returning stale heap
data, an off-by-one that lets a length field be read back. The second bug
converts that knowledge into control. Neither is sufficient alone: a leak without
a write is an information disclosure, and a write without a leak is a crash.

It also reframes what mitigations do. ASLR does not make exploitation impossible;
it makes it *conditional*, by adding a required prerequisite that the attacker
must satisfy with a second vulnerability. That is why hardening a target often
means hunting information disclosures with the same seriousness as memory
corruption — removing the leak removes the exploit even when the corruption bug
survives.

'''

KERNEL = '''## Worked Example: Reading a Kernel's Mitigation State Before Attacking It

Kernel exploitation is unforgiving — a mistake panics the machine rather than
crashing a process — so the first work is reconnaissance against the defences
rather than the bug. Four settings decide how hard the target is, and all four
are readable without privilege.

**Are kernel pointers hidden, and is KASLR on?**

```shell-session
analyst@lab:~$ cat /proc/sys/kernel/kptr_restrict
1
analyst@lab:~$ cat /proc/sys/kernel/dmesg_restrict
1
analyst@lab:~$ grep -qw nokaslr /proc/cmdline && echo "KASLR DISABLED" || echo "KASLR enabled"
KASLR enabled
```

`kptr_restrict = 1` hides kernel pointers from unprivileged readers and
`dmesg_restrict = 1` closes the kernel log, which is historically one of the
richest sources of accidentally-printed addresses.

**Verifying the restriction actually applies to you**, rather than trusting the
setting:

```shell-session
analyst@lab:~$ head -1 /proc/kallsyms
0000000000000000 T startup_64
```

The symbol name is readable; the address is zeroed. That single line is the
difference between a KASLR bypass costing nothing and costing a whole separate
information-disclosure bug.

**What the CPU enforces:**

```shell-session
analyst@lab:~$ grep -o -m1 -E 'smep|smap' /proc/cpuinfo | sort -u | tr '\\n' ' '
smap smep
```

SMEP means the kernel cannot execute pages that belong to userspace, which kills
`ret2usr` — the old and comfortable technique of pointing a corrupted kernel
function pointer at attacker code sitting in user memory. SMAP extends the same
idea to reads and writes.

**The assessment that follows from those four lines.** KASLR plus a restricted
`kallsyms` means the attacker needs a separate leak before any address is usable.
SMEP and SMAP mean that even with control of a kernel pointer, user-mapped
shellcode is unreachable, so the technique must become kernel-ROP or a data-only
attack — typically overwriting the `cred` structure of the current process to set
its UID to 0, which never executes attacker code at all and therefore never
touches the protections above.

Which is the useful conclusion: mitigations do not stop kernel exploitation, they
select the technique. The next place to look on this host is the surface those
mitigations do not cover — unprivileged user namespaces, unprivileged eBPF, and
any third-party driver exposing an `ioctl`.

'''

BROWSER = '''## Worked Example: The Primitive Every Browser Exploit Is Built From

Browser exploitation reduces to one capability: being able to read the same bytes
as two different types. JavaScript offers a legitimate, safe version of that, and
looking at it makes the illegitimate version legible.

```javascript
const buf = new ArrayBuffer(8);
const f64 = new Float64Array(buf);   // view those 8 bytes as a double
const u32 = new Uint32Array(buf);    // view the SAME 8 bytes as two integers

f64[0] = 3.14159;
console.log("float   :", f64[0]);
console.log("raw bits:", "0x" + u32[1].toString(16) + u32[0].toString(16));

u32[0] = 0x41414141; u32[1] = 0x00007fff;   // choose the bits directly
console.log("float from chosen bits:", f64[0]);
```

```shell-session
analyst@lab:/tmp/br-lab$ node prim.js
float   : 3.14159
raw bits: 0x400921f9f01b866e
float from chosen bits: 6.94906e-310
```

The same eight bytes were read as a number and as raw integers, and then written
as integers and read back as a number. Nothing here is a vulnerability — typed
arrays are designed to do exactly this, over a buffer that holds only data.

**A type-confusion bug gives an attacker the same capability over an object
reference**, and that changes everything:

- Read an object's pointer bits as a number — that is **addrof**, and it leaks
  where an object lives.
- Write chosen bits and have the engine treat them as an object pointer — that is
  **fakeobj**, and it forges an object at an address of your choosing.

Together, `addrof` and `fakeobj` compose into arbitrary read and write inside the
renderer, which is why exploit writeups treat reaching them as the milestone
rather than the finish.

**And the renderer is not the finish.** A modern drive-by chain needs a distinct
bug at each stage, and the defence at each stage is what forces the next one:

| Stage | What it achieves | The control that forces another bug |
|:--|:--|:--|
| Engine bug (type confusion / UAF) | the primitive above | shape-integrity checks in the JIT |
| addrof + fakeobj | arbitrary read/write in the renderer | JIT hardening, pointer authentication |
| Renderer RCE | code execution — still sandboxed | site isolation, multi-process sandbox |
| Sandbox escape | out of the renderer | broker hardening, least-privilege renderer |
| OS control | root or SYSTEM | kernel mitigations |

The reason a browser bug is rarely a browser *compromise* is that each row is a
separate vulnerability. That is also why full chains are expensive and why
defenders get real value from breaking any single row rather than all of them.

'''

WORK = {
    "Offensive Security/Exploit Development/Exploit Construction & Control Flow/Exploit Reliability & Mitigation Engineering.md": RELIABILITY,
    "Offensive Security/Exploit Development/Platform Exploitation/Kernel Exploitation Theory.md": KERNEL,
    "Offensive Security/Exploit Development/Platform Exploitation/Browser Exploitation Theory.md": BROWSER,
}

ANCHOR = re.compile(r"^## Task \d+ — (Failure Modes|Security Implications|Detection)", re.M)
ANY_TASK = re.compile(r"^## Task \d+ — (.*)$", re.M)


def main():
    apply = "--apply" in sys.argv
    for rel, sec in WORK.items():
        try:
            src = open(rel, encoding="utf-8").read()
        except FileNotFoundError:
            print(f"  MISSING  {rel}")
            continue
        m = ANCHOR.search(src)
        if not m:
            print(f"  ✗ NO ANCHOR  {rel}")
            continue
        out = src[:m.start()] + sec + src[m.start():]
        out = out.replace("## Worked Example:", "## Task 0 — Worked Example:", 1)
        n = [0]

        def renum(mm):
            n[0] += 1
            return f"## Task {n[0]} — {mm.group(1)}"

        out = ANY_TASK.sub(renum, out)
        print(f"  ✓ {n[0]} tasks  {rel.split('/')[-1]}")
        if apply:
            open(rel, "w", encoding="utf-8").write(out)
    print(f"\n{'APPLIED' if apply else 'DRY RUN'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
