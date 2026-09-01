#!/usr/bin/env python3
"""
Mine worked examples for Offensive Security from .archive/labs/.

The recipe, applied per note:
  1. Keep every command and its real output verbatim — that material is already
     correct and already written.
  2. Drop the setup framing ("run these in order"), the mkdir/cd scaffolding
     where it is not the specimen, and the cleanup step.
  3. Drop contrived steps whose "output" was an echo of the lesson — that is
     prose pretending to be evidence; write it as prose instead.
  4. Add the interpretation sentence under each output block.
  5. Insert as a numbered task before Security Implications, then renumber.

    python3 docs/scripts/mine-offsec.py            # dry run
    python3 docs/scripts/mine-offsec.py --apply
"""

import re
import sys

STACK = '''## Worked Example: An Overflow That Never Touches the Return Address

The canonical mental image of stack corruption is a smashed return address. This
example shows the more common and quieter case first — corrupting a neighbour —
then shows what the canary does and does not catch.

**The specimen.** A local flag sits immediately next to an unbounded buffer:

```c
#include <stdio.h>
#include <string.h>
int main(void){
    volatile int authenticated = 0;   // adjacent local
    char buf[16];
    printf("password: ");
    gets(buf);                        // no bounds check at all
    if (authenticated) puts("AUTH-BYPASS");
    else puts("denied");
    return 0;
}
```

Built with the canary disabled, 28 bytes of input reach past the 16-byte buffer
and land on the flag:

```shell-session
analyst@lab:/tmp/stack-lab$ gcc -fno-stack-protector -O0 -w auth.c -o auth_nocanary
analyst@lab:/tmp/stack-lab$ python3 -c "import sys; sys.stdout.buffer.write(b'A'*24 + b'\\x01\\x00\\x00\\x00')" | ./auth_nocanary
password: AUTH-BYPASS
```

Read what did *not* happen. The return address was never touched, `RIP` was never
redirected, and no control flow was hijacked. Twenty-four bytes of padding
carried the write past `buf` and four more bytes set `authenticated` to a
non-zero value. The program then took its own `if` branch, correctly, on
corrupted data. This is stack corruption achieving its goal purely through data.

**Now the same source with the canary enabled**, overflowing far enough to reach
the return address:

```shell-session
analyst@lab:/tmp/stack-lab$ gcc -fstack-protector-all -O0 -w auth.c -o auth_canary
analyst@lab:/tmp/stack-lab$ python3 -c "import sys; sys.stdout.buffer.write(b'A'*100)" | ./auth_canary; echo "exit=$?"
password: *** stack smashing detected ***: terminated
exit=134
```

Exit code 134 is SIGABRT — the process killed itself on purpose. That is the
control working exactly as designed, and it is worth recognising in a crash
triage: a `stack smashing detected` abort is not a bug in the program, it is the
program refusing to return to an attacker-supplied address.

**The two results together are the lesson.** The canary sits *between* the local
variables and the return address. It therefore protects the return address and
nothing below it — the first overflow flew underneath it and was never a
candidate for detection. A canary is a control-flow-integrity measure, not a
bounds check, and defending the first case needs bounds-checked APIs or a
language that will not compile `gets` at all.

'''

CPU = '''## Worked Example: Seeing the ABI in the Machine Code

The calling convention is not an abstraction layer over the CPU — it is written
literally into the instruction bytes, and every code-reuse technique later in
this branch depends on that being true.

**The specimen**, compiled without PIE so the addresses stay readable:

```c
#include <stdio.h>
int add(int a, int b){ return a + b; }
int main(void){ printf("%d\\n", add(2, 3)); return 0; }
```

**Where the arguments go.** Disassembling `main` shows the two integers being
placed before the call:

```shell-session
analyst@lab:/tmp/cpu-lab$ objdump -d --disassemble=main -M intel demo | grep -E 'mov|call' | head -3
  4011  be 03 00 00 00        mov    esi,0x3
  4011  bf 02 00 00 00        mov    edi,0x2
  4011  e8 d5 ff ff ff        call   401126 <add>
```

The second argument goes into `ESI` and the first into `EDI` — the System V
AMD64 convention, in that order, before `call` transfers control. Note the
compiler emitted them in reverse source order; the convention constrains *which
register*, not the sequence of the writes. This is why a ROP chain must control
`RDI` and `RSI` to pass arguments to a function it did not write.

**Where the return address goes.** `call` pushes it, so at the entry to `add` it
sits at the top of the stack:

```shell-session
analyst@lab:/tmp/cpu-lab$ gdb -q -batch -ex 'break add' -ex 'run' \\
    -ex 'info registers rsp rip' -ex 'x/1xg $rsp' ./demo
rsp            0x7fffffffe3c8      0x7fffffffe3c8
rip            0x401126            0x401126 <add+4>
0x7fffffffe3c8: 0x0000000000401160
```

`RSP` points at `0x7fffffffe3c8`, and the eight bytes stored there are
`0x401160` — an address inside `main`, immediately after the `call`. When `add`
executes `ret`, the CPU pops that value into `RIP` and resumes there.

That single stack slot is the premise of everything that follows. `ret` does not
verify what it pops; it is an unconditional jump to whatever eight bytes happen
to be at the top of the stack. An attacker who can write to that slot is not
"corrupting memory" in the abstract — they are choosing the next instruction the
CPU executes.

'''

WORK = {
    "Offensive Security/Exploit Development/Memory Corruption Exploitation/Stack Corruption.md": STACK,
    "Offensive Security/Exploit Development/Exploit Foundations & Architecture/CPU, Assembly & the ABI.md": CPU,
}

ANCHOR = re.compile(r"^## Task \d+ — (Failure Modes|Security Implications)", re.M)
ANY_TASK = re.compile(r"^## Task \d+ — (.*)$", re.M)


def apply_to(text, section):
    m = ANCHOR.search(text)
    if not m:
        return text, "no anchor task found"
    out = text[:m.start()] + section + text[m.start():]
    out = out.replace("## Worked Example:", "## Task 0 — Worked Example:", 1)
    n = [0]

    def renum(mm):
        n[0] += 1
        return f"## Task {n[0]} — {mm.group(1)}"

    out = ANY_TASK.sub(renum, out)
    return out, f"inserted, {n[0]} tasks renumbered"


def main():
    apply = "--apply" in sys.argv
    for rel, section in WORK.items():
        try:
            src = open(rel, encoding="utf-8").read()
        except FileNotFoundError:
            print(f"  MISSING  {rel}")
            continue
        out, how = apply_to(src, section)
        ok = out != src
        print(f"  {'✓' if ok else '✗'} [{how}] {rel}")
        if ok and apply:
            open(rel, "w", encoding="utf-8").write(out)
    print(f"\n{'APPLIED' if apply else 'DRY RUN'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
