---
title: "Hexadecimal & Binary"
aliases: ["Hexadecimal", "Hex", "Binary", "Hex and Binary"]
tags:
  - tree/crypto
  - cyber/crypto/encoding
  - type/technique
  - difficulty/easy
Domain:
  - "[[Encoding & Obfuscation]]"
Color: "#FFE119"
---

# 🔢 Hexadecimal & Binary

> [!abstract] Note of [[Encoding & Obfuscation]]
> Under every abstraction, data is bits. Hexadecimal is the human-readable shorthand for those bits — two hex digits per byte — and it is the notation security work is conducted in: hash digests, memory dumps, packet captures, file signatures and shellcode are all read as hex. This note builds the fluency to move between text, bytes and hex at sight, and to read a raw dump byte by byte.

## Parent Learning Order
Hexadecimal & Binary -> Base64 and the Base Family -> XOR and Classical Ciphers

## Everything Is Bits, Hex Is How We Read Them

A computer stores everything as bits. Eight bits make a **byte**, which holds a value from 0 to 255. Writing a byte as eight ones and zeros is accurate but unreadable, and writing it as a decimal number (0–255) hides the bit structure. **Hexadecimal** — base 16 — is the compromise everyone settled on, because it maps to bits with no arithmetic: each hex digit is exactly four bits, so **two hex digits are exactly one byte**.

| Form | The letter `H` |
|:--|:--|
| Binary | `01001000` |
| Decimal | `72` |
| Hex | `48` |
| ASCII | `H` |

The mappings worth committing to memory, because you will read them constantly: `0x41` = `A`, `0x61` = `a`, `0x20` = space, `0x0A` = newline (`\n`), `0x00` = the null byte. The relationship between upper and lower case is a single bit — `A` is `0x41`, `a` is `0x61`, a difference of `0x20` — which is why case-flipping tricks work at the bit level.

Python shows all four views of one byte at once:

```shell-session
analyst@lab:~$ python3 -c "b=0x48; print(f'{b} = {b:#x} = {b:08b} = {chr(b)!r}')"
72 = 0x48 = 01001000 = 'H'
```

You will also meet three written forms of the same hex byte and should not be thrown by them: `41` (raw hex, as in a dump), `0x41` (a literal, in code), and `\x41` (an escape, in C and Python strings). All three are the byte whose value is 65, the letter `A`.

## Reading a Hex Dump

The tool for looking at raw bytes is `xxd` (or `hexdump`). It prints three columns: the offset, the bytes in hex, and the same bytes rendered as ASCII with non-printable bytes shown as `.`.

```shell-session
analyst@lab:~$ printf 'HMT\x00\x41\x42' > sample.bin
analyst@lab:~$ xxd sample.bin
00000000: 484d 5400 4142                           HMT.AB
```

Read it left to right against **Everything Is Bits, Hex Is How We Read Them**. `48 4d 54` is `H M T`. Then `00` — the null byte, which the ASCII column cannot print so it shows as `.`. Then `41 42` is `A B`. The left column `00000000` is the byte offset into the file, in hex; it matters the moment a file is larger than one line, because it is how you say "the interesting bytes start at offset `0x1F`."

The conversion runs both ways, which is how you craft or extract raw bytes from a shell:

```shell-session
analyst@lab:~$ echo -n "HMT" | xxd -p
484d54
analyst@lab:~$ echo "484d54" | xxd -r -p
HMT
```

`-p` gives plain hex with no offsets or ASCII column; `-r` reverses a dump back into bytes. That pair — text to hex, hex to text — is the everyday workflow for pasting a payload into a report and getting it back out intact.

## Magic Bytes: Identifying a File by Its First Bytes

A file's type is not its extension — it is the bytes at the start, the **magic number**. Renaming `malware.exe` to `photo.jpg` changes nothing about what the file is, and the first few bytes give it away:

```shell-session
analyst@lab:~$ printf 'PK\x03\x04' > mystery.file
analyst@lab:~$ xxd -l4 mystery.file
00000000: 504b 0304                                PK..
analyst@lab:~$ head -c4 /bin/ls | xxd
00000000: 7f45 4c46                                .ELF
```

`50 4b` is `PK` — the initials of Phil Katz, who wrote the ZIP format — so any file beginning `50 4b 03 04` is a ZIP archive (and therefore also a `.docx`, `.jar` or `.apk`, all of which are ZIP underneath). `7f 45 4c 46` is `\x7f` followed by `ELF`, the signature of a Linux executable. Recognising these on sight is a core triage skill: it tells you what a suspicious file really is before you open it, and `file` uses exactly this table of signatures to name a type regardless of extension.

## Endianness: The Byte-Order Trap

A single byte has no ordering question. A multi-byte value does: when the four bytes of `0x41424344` are written to memory or a file, which byte comes first? Two conventions disagree, and the disagreement has cost more debugging hours than almost anything else in low-level work.

```shell-session
analyst@lab:~$ python3 -c "import struct; v=0x41424344; print('BE', struct.pack('>I',v).hex()); print('LE', struct.pack('<I',v).hex())"
BE 41424344
LE 44434241
```

**Big-endian** stores the most significant byte first — the order humans write numbers in — so `0x41424344` becomes `41 42 43 44`. **Little-endian**, which x86 and ARM use, stores the least significant byte first, so the same value becomes `44 43 42 41`, apparently backwards. A hash printed as `0x41424344` sitting in a little-endian memory dump appears as `44 43 42 41`, and reading it left to right without accounting for endianness gives the wrong value. Network protocols standardised on big-endian ("network byte order") precisely so machines of different conventions could agree on the wire.

## Where This Shows Up in Security

Hex is the working notation for most of security, and fluency in it is assumed rather than taught in the material that follows:

- **Hash digests** are printed as hex — a SHA-256 is 32 bytes shown as 64 hex characters. Comparing two digests is comparing two hex strings.
- **Packet captures** show every field as hex; reading a protocol header (see the sibling **Networking** material) means reading its bytes.
- **Shellcode and exploit payloads** are written and injected as hex or `\x` escapes, and endianness decides whether an address lands correctly.
- **File carving and forensics** rely on magic bytes to recover files from raw disk images with no filesystem to name them.

None of these is a separate skill. They are all the same act — reading bytes as hex — which is why this is the first note in the branch.

## Summary

You should now be able to:

- Convert between text, decimal, binary and hexadecimal for a byte at sight, and recognise the common ASCII mappings (`0x41`=`A`, `0x20`=space, `0x0A`=newline, `0x00`=null).
- Read an `xxd` hex dump column by column, and round-trip data between text and hex with `xxd -p` / `xxd -r -p`.
- Identify a file by its magic bytes regardless of its extension, and explain why the extension is not the type.
- Explain big- versus little-endian byte order and why misreading it corrupts addresses and multi-byte values.

---
> 🔼 Up: [[Encoding & Obfuscation]]
