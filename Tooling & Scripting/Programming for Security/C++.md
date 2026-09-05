---
title: "C++ for Security Engineering"
aliases: ["C++ Security", "C++"]
tags: [tree/tooling, cyber/tooling/programming/cpp, type/concept, difficulty/hard]
Domain: "[[Programming for Security]]"
Color: "#708090"
verified: 2026-09-05
---

# C++ for Security Engineering

> [!abstract] Note of [[Programming for Security]]
> C++ is the only language on this map with no memory-safety net, which is the reason to reach for it and the reason most tools should not. This note covers the structural defences, and then reproduces the failure they exist to prevent — a use-after-free that passes its test, prints a plausible answer, and is wrong.

C++ is the bottom of the ladder — maximum performance and byte-exact control, at the cost of memory safety. You reach for it when you truly need it: line-rate packet parsers, performance-critical engines, and exploit development where you must control every byte. It is also where you can *write* the very vulnerability classes the rest of this vault teaches you to exploit, which makes disciplined C++ a security topic in its own right.

> [!warning] The power is the hazard
> C++ lets you write buffer overflows and use-after-frees by accident. Every serious C++ security tool uses sanitizers and fuzzing — not optionally.

## Parent Learning Order
Python -> Go -> C++ -> Bash -> PowerShell

## Maximum control, and no memory-safety net

> *What does C++ give you that Go and Python cannot, and what does it take away in exchange?*
>
> Hold your answer — the section below is the response.

C++ is the **maximum-control** corner — and the one place on the map with no memory-safety net.

Reach for C++ only when the problem genuinely needs it: every cycle, every byte, no garbage-collector pauses, direct memory layout. The defining tradeoff is stark — the same low-level control that makes C++ fast is exactly what lets a mistake become a **buffer overflow or use-after-free**, the memory-corruption bugs that the Exploit-Development branch weaponises.

Four defences do the work, and each one removes a failure rather than detecting it:

| Defence | Removes | How |
|:--|:--|:--|
| **RAII** and smart pointers | leaks, double frees, use-after-free | ownership is a type, and destruction is automatic |
| `std::span` / `string_view` | buffer overflows | a view carries its own length, so there is no raw pointer arithmetic |
| **Sanitizers** in CI | the silent ones that survive the above | undefined behaviour aborts loudly instead of returning a plausible value |
| **Fuzzing** | the input you did not think of | malformed data is generated faster than it is imagined |

The first two prevent by construction; the last two catch what slips past them. A project with the first two and neither of the last two is the common case, and it is the one this note is about.

**Prerequisites:** the stack and the heap, and what it means for a pointer to be freed.

> [!tip] The analogy, and where it breaks
> Working without a safety net is the usual image. The analogy breaks in the way that matters most: a performer without a net finds out immediately; C++ lets you complete the routine, take the applause and walk off, and the fall happens months later to somebody else, at a time chosen by whoever supplies the input. The absence is not of the net but of the *notification* — which is why the discipline is not care, it is tooling that makes the fall loud on the day it happens.

## RAII, smart pointers, and bounding every access

Modern C++ replaces manual `new`/`delete` with **RAII** and smart pointers, and bounds every buffer access:

```cpp
// UNSAFE C — the classic overflow
char buf[64]; strcpy(buf, input);          // no bound → overflow if input > 64

// Modern C++ — bounds are structural
std::vector<std::byte> buf(len);           // owns its memory (RAII); frees automatically
if (offset + n > buf.size()) throw std::out_of_range{"parse"};   // check BEFORE reading
std::span<const std::byte> view{buf.data() + offset, n};         // bounded view, no raw ptr math
```

Use `std::unique_ptr`/`shared_ptr` (no manual `delete`), `std::span`/`string_view` for bounded views, and a reproducible toolchain (pinned compiler, `-Wall -Wextra`). Build with **sanitizers** in CI: `-fsanitize=address,undefined`.

## Why the worst bugs stay silent until someone exploits them

The reason C++ demands sanitizers and fuzzing is that its worst bugs are **silent** until exploited:

Here is one, complete enough to compile. The bug is the kind that survives review because the rejection path looks correct:

```cpp
Record* parse(const char* in) {
    Record* r = (Record*)malloc(sizeof(Record));
    r->len = strlen(in);
    strncpy(r->data, in, sizeof(r->data) - 1);
    r->data[sizeof(r->data) - 1] = '\0';
    if (r->len > 32) { free(r); }          // rejects oversize input
    return r;                               // ...and returns it anyway
}
```

Built normally and given an oversize record:

```shell-session
$ g++ -O2 -o uaf uaf.cpp && ./uaf
parsed OK, len=1564009740
$ echo $?
0
```

Exit status zero. A test asserting that the program does not crash passes. Look at the length: `1564009740`, from a string of forty-six characters. The read after the free did not fail, it returned whatever the allocator had since put in that memory, and the program printed it as a fact.

Rebuild the same source with sanitizers:

```shell-session
$ g++ -O1 -g -fsanitize=address,undefined -o uaf_asan uaf.cpp && ./uaf_asan
==1686==ERROR: AddressSanitizer: heap-use-after-free on address 0x504000000010
READ of size 4 at 0x504000000010 thread T0
    #0 0x5568aacfe5a2 in main /tmp/uaf.cpp:18
0x504000000010 is located 0 bytes inside of 36-byte region [0x504000000010,0x504000000034)
freed by thread T0 here:
    #0 in free
    #1 0x5568aacfe4e1 in parse(char const*) /tmp/uaf.cpp:12
$ echo $?
1
```

Same source, same input, opposite verdict. The sanitizer names the read at line 18 and the free at line 12 and stops the process.

**The deliberate break:** the plain build prints "parsed OK" — the use-after-free reads freed heap memory but happens not to crash *this time*, so testing passes and the bug ships. That is the entire danger of C++: memory errors are **undefined behaviour** that may work by luck until an attacker supplies the input that turns them into a crash or code execution (the exact primitive the Heap-Exploitation note attacks). **AddressSanitizer** makes the invisible bug loud and pinpoints it (`parser.cpp:88`), and **fuzzing** (libFuzzer/AFL) feeds malformed input until it finds the crash you didn't. This is the discipline that separates a security tool from a liability: in a language with no safety net, the net is your tooling — RAII to prevent leaks/UAF by construction, `std::span`/bounds checks to prevent overflows, sanitizers to catch what slips through, and fuzzing to find it before the adversary does. Use C++ only when the performance/control is truly required, and never without that harness.

**How you'd spot it:** a passing test suite is not evidence here, because the bug is silent by construction. Build with `-fsanitize=address,undefined` and the input that printed "parsed OK" aborts instead, naming the allocation and the free. A crash that reproduces on one compiler, one optimisation level, or one machine and nowhere else is the shape of undefined behaviour rather than a logic error.

## Security Implications

**Undefined behaviour is not a crash, and treating it as one is the mistake.** The build above returned zero and printed a number. A crash would have been the fortunate outcome, because a crash is a bug report; a plausible wrong value is a result somebody uses. Any reasoning of the form "we would have noticed" assumes a notification the language does not provide.

**Your test suite is measuring the wrong thing without sanitizers.** Coverage says which lines ran, not whether they were correct while running. `-fsanitize=address,undefined` in CI converts a silent memory error into a failing test, and it is the single highest-value change available to a C++ project that does not have it.

**Fuzzing finds the input you did not think of, which is the only kind that matters.** libFuzzer or AFL driving the parser under a sanitizer explores malformed input far faster than a person writes cases, and every crash it produces is a real defect with a reproducer attached. A parser that handles untrusted input and has never been fuzzed has not been tested in the sense that matters.

**The memory bugs in this note are the exploit primitives in another branch.** A use-after-free is not merely a correctness problem — controlling what lands in the freed region is how it becomes code execution, which is exactly what the heap-exploitation material does deliberately. Writing C++ for security work means writing the thing your own discipline is elsewhere aimed at.

**Choosing C++ is a decision that needs a reason.** Every cycle, every byte, no collector pauses, exact ABI layout — those are real requirements and they are rarer than they feel. Where the requirement is absent, the same tool in Go or Python cannot have this class of bug at all, and that is the strongest argument the language map makes.

All testing described here belongs on systems within an authorized scope; a memory-corruption reproducer is an exploit primitive, and running one outside a lab you own is out of bounds.

## Summary

You should now be able to:

- Judge when C++ is the right choice, and name the safety it gives up.
- Rewrite an unsafe `strcpy` parse into bounds-checked modern C++.
- Explain why a use-after-free can pass tests, and how sanitizers + fuzzing catch it before it ships.

---
> 🔼 Up: [[Programming for Security]]
