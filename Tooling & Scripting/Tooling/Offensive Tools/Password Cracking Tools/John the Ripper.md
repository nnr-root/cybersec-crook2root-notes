---
title: "John the Ripper"
aliases: ["JtR", "john"]
tags: [tree/tooling, cyber/tooling/offensive/cracking/john, type/tool, difficulty/medium]
Domain: "[[Password Cracking Tools]]"
Color: "#708090"
---

# John the Ripper

John the Ripper (JtR) is the classic CPU-first password cracker. Its strengths are **breadth** (hundreds of hash formats), an **incremental** Markov mode, and a powerful **rules** engine that mutates a wordlist into millions of realistic candidates. Its output is evidence about *password weakness*, not authorization to use the recovered credential.

> [!warning] Authorized recovery only
> Crack only hashes captured under scope or generated in your own lab. The examples below hash values you create yourself.

## Parent Learning Order
name-that-hash -> hash-identifier -> John the Ripper -> Hashcat

## Generating smart candidates, not just more of them

> *Offline cracking is one loop repeated. Which part of it is John's specialty?*
>
> Hold your answer — the section below is the response.

Offline cracking is one loop: guess a candidate, hash it, compare to the target, repeat. What changes is *how you generate candidates* — and John's specialty is generating *smart* ones.

On the ladder, John excels at rungs 1–2 (dictionary and **dictionary + rules**) and format breadth. Where Hashcat brings raw GPU speed, John brings a CPU, a huge format list (NetNTLM, Kerberos, ZIP, PDF, bcrypt), and a rule engine that turns `summer2024` into `Summer2024!` — which, as the diagram's "most fall HERE" rung says, is where the majority of real passwords actually break.

## unshadow, then crack with rules

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

## Why complexity requirements do not help defenders

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

**How you'd spot it:** a wordlist-only run that fails proves very little, so check whether `--rules` was on before writing "strong password" anywhere. In recovered output the pattern gives the game away: a dictionary word wearing a capital, a year and a symbol. If most of your cracked passwords look like that, the complexity policy is generating precisely what the rule engine expects.

## Summary

You should now be able to:

- Explain why offline cracking runs at full speed without ever contacting the target.
- Choose the JtR feature that recovers `Summer2024!` when a wordlist alone fails.
- Explain why "complexity requirements" barely slow a rules-based attack, and what defense actually does.

---
> 🔼 Up: [[Password Cracking Tools]]
