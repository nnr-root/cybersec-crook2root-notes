---
title: "John the Ripper"
aliases: ["JtR", "john"]
tags: [tree/tooling, cyber/tooling/offensive/cracking/john, type/tool, difficulty/medium]
Domain: "[[Password Cracking Tools]]"
Color: "#708090"
verified: 2026-09-05
---

# John the Ripper

> [!abstract] Note of [[Password Cracking Tools]]
> John the Ripper brings format breadth and a rules engine rather than raw GPU speed — hundreds of hash types and mutations that turn a wordlist into the exact passwords a complexity policy produces. This note covers why rules defeat "complexity", why the recovered pattern is the finding rather than the plaintext, and why a slow hash is the only defence that survives them.

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
r.okonkwo:Autumn2023      (r.okonkwo)
operator@lab:~$ john --show creds.lab
r.okonkwo:Autumn2023:1104:...
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

**The deliberate break:** `Winter2025!` is nowhere in rockyou.txt, so the first run fails — and a naive tester concludes "strong password." But the rule engine mutates `winter2025` → `Winter2025!` in one pass, and it falls. Enterprise "complexity" passwords (a word + a capital + a number + a symbol) are *exactly* what rules generate, so they crack about as fast as the base word. The lesson cuts two ways: offensively, always run `--rules` before believing a password is strong; defensively (the diagram's Truth #2), complexity rules just push users toward predictable mutations the rule engine anticipates — the real defense is a **slow hash** (bcrypt/argon2), which starves the loop regardless of the password. And the flip side still holds: a genuinely high-entropy passphrase never appears in any wordlist or rule expansion, so it survives — the finding you report is the *pattern* (`r.okonkwo` used a seasonal password), never the plaintext.

**How you'd spot it:** a wordlist-only run that fails proves very little, so check whether `--rules` was on before writing "strong password" anywhere. In recovered output the pattern gives the game away: a dictionary word wearing a capital, a year and a symbol. If most of your cracked passwords look like that, the complexity policy is generating precisely what the rule engine expects.

## Security Implications

**Complexity requirements produce exactly what the rule engine generates.** A word plus a capital plus a year plus a symbol is precisely the `Jumbo` rule set's output, so an enterprise "complex" password cracks about as fast as its base word. The finding to report is the *pattern* — a seasonal or word-plus-decoration scheme across many users — not the individual plaintext, because the pattern is what a policy change can fix.

**The only defence that survives rules is a slow hash.** Rules make the candidate list bigger for near-free; nothing about the password itself starves the loop the way bcrypt or argon2 does. So the recommendation is never "require more complexity" — that feeds the rules — it is the work factor, exactly as with Hashcat.

**Format breadth means the captured artifact is the exposure, not just the password.** John cracks NetNTLM, Kerberos tickets, ZIP, PDF and KeePass among hundreds of formats, so an encrypted archive or a Kerberoast ticket is a crackable credential the moment it is captured. Protecting those artifacts matters as much as the password policy behind them.

**Offline cracking is silent, so detect the capture.** John never contacts the target; the detectable event is the theft that produced the hash file. Once it is captured, only the work factor stands between the attacker and the plaintext.

All cracking here targets only in-scope or self-generated hashes; the reportable output is the weakness, never the recovered credential.

## Summary

You should now be able to:

- Explain why offline cracking runs at full speed without ever contacting the target.
- Choose the JtR feature that recovers `Summer2024!` when a wordlist alone fails.
- Explain why "complexity requirements" barely slow a rules-based attack, and what defense actually does.

---
> 🔼 Up: [[Password Cracking Tools]]
