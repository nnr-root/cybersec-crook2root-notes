---
title: "Hashcat"
aliases: ["hashcat"]
tags: [tree/tooling, cyber/tooling/offensive/cracking/hashcat, type/tool, difficulty/hard]
Domain: "[[Password Cracking Tools]]"
Color: "#708090"
---

# Hashcat

Hashcat is the GPU-accelerated cracker. Where John prizes format breadth and CPU rules, Hashcat prizes raw **throughput**: a modern GPU tests billions of candidates per second against fast hashes. It is driven by two axes — a **hash mode** (`-m`) and an **attack mode** (`-a`) — and mastering those two flags is 90% of the tool.

> [!warning] Authorized recovery only
> Crack only in-scope or self-generated hashes. GPU speed makes weak-hash cracking near-instant — bound the run and report policy weakness, not the credential.

## Parent Learning Order
name-that-hash -> hash-identifier -> John the Ripper -> Hashcat

## The same guess-and-compare loop, at GPU scale

Same offline loop as John — guess, hash, compare — but Hashcat runs it on a GPU at a scale that changes what's possible.

Hashcat owns the right side of the diagram: it turns the attack-mode ladder into GPU throughput and is the **mask/hybrid king** (rung 3), making brute-force *targeted* instead of blind. It's also the clearest demonstration of the **speed wall** — the same GPU cracks a fast MD5 hash billions of times per second but crawls against a slow bcrypt, which is the entire defensive story. Two flags encode it all: `-m` (which hash) and `-a` (which attack).

## Benchmark, then dictionary and mask attacks

Benchmark to see why fast hashes are indefensible, then crack with dictionary and mask:

```shell-session
operator@lab:~$ hashcat -b -m 0 | tail -1
Speed.#1.........: 58123.4 MH/s (raw MD5)
operator@lab:~$ hashcat -m 0 -a 0 md5.txt rockyou.txt        # -a 0 = dictionary
482c811da5d5b4bc6d497ffa98491e38:password123
operator@lab:~$ hashcat -m 0 -a 3 hashes.txt '?u?l?l?l?l?l?d?d?d?d'   # -a 3 = mask
e90664c0af74160644d29e4d6147969b:Summer2024
```

| `-m` | Hash | | `-a` | Attack |
|---|---|---|---|---|
| 0 | MD5 | | 0 | dictionary (+ `-r rules`) |
| 1000 | NTLM | | 1 | combinator |
| 1800 | sha512crypt | | 3 | mask / brute |
| 3200 | bcrypt | | 6/7 | hybrid |
| 22000 | WPA-PBKDF2/PMKID | | | |

A **mask** (`?u`=upper, `?l`=lower, `?d`=digit, `?s`=symbol) enumerates only a human *pattern* — `?u?l?l?l?l?l?d?d?d?d` is exactly `Summer2024`, cutting the keyspace by orders of magnitude versus blind brute force.

## The benchmark table read as a hardening spec

The benchmark table *is* a hardening spec — the speed wall from the diagram, measured:

```shell-session
# fast hash — falls instantly
operator@lab:~$ hashcat -m 0 -a 0 md5.txt rockyou.txt --potfile-disable
482c811da5d5b4bc6d497ffa98491e38:password123    (0.4 s)
# SAME password, slow hash, SAME GPU
operator@lab:~$ hashcat -m 3200 -a 0 bcrypt.txt rockyou.txt --status
Speed.#1.........: 9421 H/s (bcrypt $2b$, cost 12)
Progress.........: 47104/14344385 (0.33%)
```

**The deliberate break:** `password123` as raw MD5 falls in under a second at ~58 **billion** guesses/sec; the *identical password* as bcrypt cost-12 runs at ~9 **thousand** guesses/sec — about **six million times slower** — on the same hardware. Same password, same GPU: the only variable is the hash's **work factor**, and that variable is the entire defense. This is why "no hashcat mode cracked it" can mean either "strong password" *or* "strong hash" — never confuse the two. The reportable numbers: fast unsalted hashes (MD5/NTLM/SHA1) are indefensible at rest and must be migrated to bcrypt/scrypt/argon2 with high cost and unique salts, and the blue team must also detect the *capture* step (LSASS access, DCSync, WPA handshake grabs) that feeds the cracker — because once the hash is out, only its work factor stands between the attacker and the plaintext.

## Summary

You should now be able to:

- What do `-m` and `-a` each select, and why do you always set both?
- A wordlist misses `Summer2024`. Write the mask that finds it and explain why it beats blind brute force.
- Given the MD5-vs-bcrypt benchmark gap, justify the storage-hashing choice and salt/cost you'd mandate.

---
> 🔼 Up: [[Password Cracking Tools]]
