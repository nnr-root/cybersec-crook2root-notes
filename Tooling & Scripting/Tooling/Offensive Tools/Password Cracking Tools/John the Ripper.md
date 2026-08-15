---
title: "John the Ripper"
aliases: ["JtR", "john"]
tags: [tree/tooling, cyber/tooling/offensive/cracking/john, type/tool, level/operator]
Domain: "[[Password Cracking Tools]]"
Color: "#708090"
---

# John the Ripper

John the Ripper (JtR) is the classic CPU-first password cracker. Its strengths are **breadth** (hundreds of hash formats), an **incremental** Markov mode, and a powerful **rules** engine that mutates a wordlist into millions of realistic candidates. Its output is evidence about *password weakness*, not authorization to use the recovered credential.

> [!warning] Authorized recovery only
> Crack only hashes captured under scope or generated in your own lab. The examples below hash values you create yourself.

## Parent Learning Order
name-that-hash -> hash-identifier -> John the Ripper -> Hashcat

## Crook — The Mental Model

Offline cracking is one loop: guess a candidate, hash it, compare to the target, repeat. What changes is *how you generate candidates* — and John's specialty is generating *smart* ones.

![[tool_cracking_modes.svg]]

On the ladder, John excels at rungs 1–2 (dictionary and **dictionary + rules**) and format breadth. Where Hashcat brings raw GPU speed, John brings a CPU, a huge format list (NetNTLM, Kerberos, ZIP, PDF, bcrypt), and a rule engine that turns `summer2024` into `Summer2024!` — which, as the diagram's "most fall HERE" rung says, is where the majority of real passwords actually break.

## Operator — Make It Work

The `jumbo` build adds the extra formats. Combine `/etc/passwd` + `/etc/shadow` with `unshadow`, then crack:

```shell-session
operator@lab:~$ john --version | head -n 1
John the Ripper 1.9.0-jumbo-1 OMP [linux-gnu 64-bit AVX2]
operator@lab:~$ unshadow passwd.lab shadow.lab > creds.lab
operator@lab:~$ john --wordlist=rockyou.txt --rules=Jumbo creds.lab
bob:Autumn2023            (bob)
operator@lab:~$ john --show creds.lab
bob:Autumn2023:1001:...
1 password hash cracked, 1 left
```

`--format=` pins the hash type (avoid mis-detection); `--wordlist=` + `--rules=` is the workhorse; `--incremental` is Markov brute-force; `--show` re-reads the `john.pot` cache (so a solved hash reprints instantly).

## Root — Internals & The Deliberate Break

The **rules engine** is what separates a novice run from a real one — and why "complexity requirements" don't help defenders:

```shell-session
# raw wordlist alone — misses the password
operator@lab:~$ john --format=raw-md5 --wordlist=rockyou.txt hashes.txt
0 password hashes cracked, 1 left
# same wordlist + rules — appends a digit and a bang, capitalises
operator@lab:~$ john --format=raw-md5 --wordlist=rockyou.txt --rules=Jumbo hashes.txt
Winter2025!       (?)
```

**The deliberate break:** `Winter2025!` is nowhere in rockyou.txt, so the first run fails — and a naive tester concludes "strong password." But the rule engine mutates `winter2025` → `Winter2025!` in one pass, and it falls. Enterprise "complexity" passwords (a word + a capital + a number + a symbol) are *exactly* what rules generate, so they crack about as fast as the base word. The lesson cuts two ways: offensively, always run `--rules` before believing a password is strong; defensively (the diagram's Truth #2), complexity rules just push users toward predictable mutations the rule engine anticipates — the real defense is a **slow hash** (bcrypt/argon2), which starves the loop regardless of the password. And the flip side still holds: a genuinely high-entropy passphrase never appears in any wordlist or rule expansion, so it survives — the finding you report is the *pattern* (`bob` used a seasonal password), never the plaintext.

## Crook → Operator → Root Checkpoint

- **Crook:** Why can offline cracking run at full speed without ever contacting the target?
- **Operator:** A wordlist alone fails but the password is `Summer2024!`. Which JtR feature recovers it?
- **Root:** Explain why "complexity requirements" barely slow a rules-based attack, and what defense actually does.

---
> 🔼 Up: [[Password Cracking Tools]]
