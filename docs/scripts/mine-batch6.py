#!/usr/bin/env python3
"""Offensive Security worked examples — batch 6 (Red Team: evasion)."""
import re
import sys

INJECTION = '''## Worked Example: Making Another Process Do the Work

Process injection is valuable to an attacker for one reason: the action then
carries a trusted process's identity, not the attacker's. A benign demonstration
with `ptrace` shows the mechanism without any malware.

**The target does nothing on its own** — it idles in `pause()` and never writes
anything:

```c
#include <unistd.h>
int main(void){ for(;;) pause(); return 0; }
```

```shell-session
analyst@lab:/tmp/inj-lab$ ./target > out.txt 2>&1 & echo "PID $!"
PID 20481
analyst@lab:/tmp/inj-lab$ cat out.txt
```

`out.txt` is empty, and will stay empty for as long as the process runs itself.

**The injection** attaches to the running process and makes *its* thread call
`write`:

```shell-session
analyst@lab:/tmp/inj-lab$ gdb -q -p 20481 -batch \\
    -ex 'call (int)write(1, "INJECTED\\n", 9)' -ex detach
analyst@lab:/tmp/inj-lab$ cat out.txt
INJECTED
```

The string appeared on `target`'s own stdout. `target` has no `write` in its
source and never called one — the byte came out of its file descriptor because
its thread was made to execute the call. That is the whole idea: to any monitor
watching outputs, the write came from `target`, a process with its own history,
parentage and reputation, not from `gdb` or the attacker.

`ptrace(PTRACE_ATTACH)` is the Linux primitive here, and it is exactly the signal
a Linux EDR watches for — as `CreateRemoteThread`, `QueueUserAPC` and
`WriteProcessMemory` are on Windows. The technique is not quiet; its value is the
borrowed identity, paid for with a very noisy syscall.

**Direct syscalls** are the response to that noise, and the reason they work is a
layering fact:

```shell-session
analyst@lab:/tmp/inj-lab$ strace -f -e trace=write bash -c 'echo hi >/dev/null'
write(1, "hi\\n", 3)                     = 3
```

A normal `write` travels through libc (on Windows, through `ntdll`), and that
library layer is precisely where a userland EDR installs its hooks. An attacker
who instead emits the raw `syscall` instruction with the write number in `rax`
reaches the kernel without ever calling the hooked function, so a userland hook
on `write` never fires. The catch, and the reason this is an arms race rather than
a win, is that the kernel still sees the syscall — kernel callbacks and, on
Windows, ETW Threat Intelligence observe the transition the userland hook missed.

'''

PAYLOAD = '''## Worked Example: Obfuscation Defeats Signatures, Not Behaviour

The central limit of payload obfuscation is easy to state and easy to
demonstrate: you can change what a payload *looks like* freely, but not what it
*does*, and detection eventually keys on the latter.

**A payload and its signature.** The canary string is the thing a static scanner
matches:

```shell-session
analyst@lab:/tmp/pe-lab$ grep -q 'PAYLOAD-EXECUTED' payload.sh && echo "static sig: DETECTED"
static sig: DETECTED
```

**Layer 1 — base64.** The string is gone from the file:

```shell-session
analyst@lab:/tmp/pe-lab$ printf 'echo %s | base64 -d | bash\\n' "$(base64 -w0 payload.sh)" > stage_b64.sh
analyst@lab:/tmp/pe-lab$ grep -q 'PAYLOAD-EXECUTED' stage_b64.sh && echo DETECTED || echo "MISS (encoded)"
MISS (encoded)
```

**Layer 2 — XOR with a decrypt stub.** Gone again, and this time not even
present as a decodable substring:

```shell-session
analyst@lab:/tmp/pe-lab$ grep -q 'PAYLOAD-EXECUTED' stage_xor.sh && echo DETECTED || echo "MISS (encrypted)"
MISS (encrypted)
```

Both layers defeat the signature completely. If detection stopped at "does the
sample contain the bad string", the attacker would have won at layer 1.

**But the behaviour is invariant**, because both variants must still do the
thing, and a rule keyed on the doing catches both:

```shell-session
analyst@lab:/tmp/pe-lab$ bash stage_b64.sh
PAYLOAD-EXECUTED
analyst@lab:/tmp/pe-lab$ for f in stage_b64.sh stage_xor.sh; do
>   grep -qE '(base64 -d|fromhex).*(bash|exec|open)' "$f" && echo "$f: decode-then-execute -> detected"
> done
stage_b64.sh: decode-then-execute -> detected
stage_xor.sh: decode-then-execute -> detected
```

Each layer added a decode step, and the decode-then-execute shape is itself the
signature — one that no amount of further encoding removes, because removing it
would remove the payload's ability to run. This is why detection engineering
migrated from content signatures to behavioural ones, and why an obfuscation-only
evasion strategy has a ceiling. The stub that unpacks the payload is the tell, and
every additional layer makes the file look less like data and more like a
decoder, which is itself anomalous.

The honest lesson for both sides: obfuscation buys time against static analysis
and nothing against a behavioural rule that watches what the payload does when it
runs.

'''

WORK = {
    "Offensive Security/Red Team Operations/Evasion & Endpoint Tradecraft/Process Injection & Direct Syscalls.md": INJECTION,
    "Offensive Security/Red Team Operations/Evasion & Endpoint Tradecraft/Payload Engineering & Obfuscation.md": PAYLOAD,
}

ANCHOR = re.compile(r"^## Task \d+ — (Failure Modes|Security Implications|Detection|Defen)", re.M)
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
