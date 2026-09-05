---
title: "Hashcat"
aliases: ["hashcat"]
tags: [tree/tooling, cyber/tooling/offensive/cracking/hashcat, type/tool, difficulty/hard]
Domain: "[[Password Cracking Tools]]"
Color: "#708090"
verified: 2026-09-05
---

# Hashcat

> [!abstract] Note of [[Password Cracking Tools]]
> Hashcat runs the offline guess-hash-compare loop on a GPU at billions of candidates per second, driven by two flags — a hash mode and an attack mode. This note covers the rules engine that makes a wordlist far bigger than it looks, the keyspace arithmetic that makes a mask beat blind brute force by seven orders of magnitude, why a unique salt multiplies the attacker's work per hash, and why "uncracked" says nothing about the password until you read the hash.

Hashcat is the GPU-accelerated cracker. Where John prizes format breadth and CPU rules, Hashcat prizes raw **throughput**: a modern GPU tests billions of candidates per second against fast hashes. It is driven by two axes — a **hash mode** (`-m`) and an **attack mode** (`-a`) — and mastering those two flags is 90% of the tool.

> [!warning] Authorized recovery only
> Crack only in-scope or self-generated hashes. GPU speed makes weak-hash cracking near-instant — bound the run and report policy weakness, not the credential.

## Parent Learning Order
name-that-hash -> hash-identifier -> John the Ripper -> Hashcat

## The same guess-and-compare loop, at GPU scale

> *John and Hashcat run the same guess-hash-compare loop. What changes?*
>
> Hold your answer — the section below is the response.

Same offline loop as John — guess, hash, compare — but Hashcat runs it on a GPU at a scale that changes what's possible.

Hashcat owns the right side of the diagram: it turns the attack-mode ladder into GPU throughput and is the **mask/hybrid king** (rung 3), making brute-force *targeted* instead of blind. It's also the clearest demonstration of the **speed wall** — the same GPU cracks a fast MD5 hash billions of times per second but crawls against a slow bcrypt, which is the entire defensive story. Two flags encode it all: `-m` (which hash) and `-a` (which attack).

**Prerequisites:** what a hash is and that it is one-way, offline versus online attacks (from [[Hydra]]), and salting from the cryptography material.

> [!tip] The analogy, and where it breaks
> Trying keys in a lock, except you have a machine that tries billions a second and the lock never wears out or calls the police — which is the whole nature of an *offline* attack. The analogy breaks on the lock itself: a good password hash is a lock deliberately built to take a long time to try each key, so the same machine that opens a cheap lock instantly still crawls against an expensive one. The attacker's speed is fixed; the defender chooses how slow each attempt is.

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

A **mask** (`?u`=upper, `?l`=lower, `?d`=digit, `?s`=symbol) enumerates only a human *pattern* rather than every possible string.

## Masks and keyspace, as arithmetic

The claim that a mask "cuts the keyspace by orders of magnitude" is measurable, and the measurement is the whole reason masks exist. `?u?l?l?l?l?l?d?d?d?d` — the shape of `Summer2024` — has a keyspace of one uppercase, five lowercase and four digits:

```text
26 × 26^5 × 10^4  =  3.09 × 10^12 candidates
```

Blind brute force of the same ten characters, allowing every printable symbol, is `95^10 ≈ 5.99 × 10^19` — about **19 million times larger**. Put the two through the speed wall and the point lands:

```text
mask (3.09e12)   @ 58 GH/s MD5    ->   53 seconds
mask (3.09e12)   @ 9.4 kH/s bcrypt -> 10.4 years
blind (5.99e19)  @ 58 GH/s MD5    ->   33 years
```

The mask turns a 33-year MD5 brute force into 53 seconds *without guessing the password* — only its shape, which human password habits make guessable. And the same mask against bcrypt is back to ten years, which is the defensive story appearing again: the work factor, not the keyspace, is what holds.

## The rules engine is where a wordlist's real size lives

A wordlist looks small until Hashcat's **rules** run on it. Each rule is a mutation applied to every candidate, entirely on the GPU: append digits, capitalise, substitute leetspeak, duplicate, reverse. `password` becomes `Password`, `password1`, `p@ssw0rd`, `password2024` and dozens more from one line:

```shell-session
operator@lab:~$ hashcat -m 0 -a 0 md5.txt rockyou.txt -r rules/best64.rule
e90664c0af74160644d29e4d6147969b:Summer2024
```

`best64` is 64 rules, so it multiplies rockyou's 14.3 million words into roughly **918 million candidates** — which against MD5 completes in a fraction of a second, because the mutation happens on the card and never touches disk. This is why "it wasn't in the wordlist" is rarely the end: the rules generate the human variations of every word, which is exactly how most real passwords are built. The reportable consequence is that a password derived from a dictionary word by any predictable transformation is a dictionary word to Hashcat.

## Why a unique salt changes the economics

The **potfile** caches every hash Hashcat has already cracked, so a repeated run skips them — useful, and the reason `--potfile-disable` appears when you want an honest benchmark. But the deeper economic lever is the **salt**.

An unsalted hash file is attacked *all at once*: Hashcat hashes each candidate once and compares the result against every hash in the file simultaneously, so cracking one hash or a million costs almost the same. A **unique** salt per password breaks that — each candidate must be re-hashed with each distinct salt, so a file of 500 uniquely-salted hashes costs 500 times the work of one. Salting does not slow a single hash much; it removes the attacker's ability to attack the whole set in parallel, and it kills precomputed rainbow tables outright because the table would have to exist per salt.

## The benchmark table read as a hardening spec

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

**How you'd spot it:** read the hash prefix before drawing any conclusion from a failed run. `$2b$` or `$argon2` means the work factor is doing its job and "uncracked" says nothing about the password; a bare MD5 or NTLM that survives a real run genuinely suggests a strong one. Hashcat's own reported speed makes the same point — billions per second against thousands is the entire difference.

## Security Implications

**The work factor is the entire defence, and it is a defender's choice not an attacker's.** The attacker's GPU speed is fixed; what changes cracking from seconds to years is the hash's cost. Fast unsalted hashes (MD5, NTLM, SHA1) are indefensible at rest and must be migrated to bcrypt, scrypt or argon2 with a high cost parameter — the benchmark gap is the argument, written as numbers rather than asserted.

**Unique salts are non-negotiable for a reason beyond rainbow tables.** They remove the attacker's ability to attack the whole credential set in parallel, turning one run against a million hashes into a million times the work. A shared salt, or none, hands that parallelism back.

**"No mode cracked it" is ambiguous, and reporting it as a strong password is an error.** It means either a strong password or a strong hash, and only the hash prefix distinguishes them. A report must say which — a `$argon2` that resisted a run is a working control, a bare NTLM that resisted one is a genuinely strong secret.

**Detect the capture, because after it only the work factor remains.** Cracking is offline and silent — the defender never sees it — so the detectable event is the *theft* that feeds it: LSASS access and DCSync ([[Mimikatz]], [[Impacket]]), a WPA handshake grab, a database dump. Once the hash is out, nothing the defender does matters except the work factor already baked in when the password was stored.

All cracking here targets only in-scope or self-generated hashes; GPU speed makes weak-hash recovery near-instant, so the finding is the policy weakness, never the recovered credential.

## Summary

## Summary

You should now be able to:

- Explain what `-m` and `-a` each select, and why both are always set.
- A wordlist misses `Summer2024`. Write the mask that finds it and explain why it beats blind brute force.
- Compute a mask's keyspace and explain why it beats blind brute force by seven orders of magnitude, and why the rules engine makes a wordlist far larger than its line count.
- Explain why a unique salt multiplies the attacker's work per hash and kills parallel cracking, not just rainbow tables.
- Given the MD5-vs-bcrypt benchmark gap, justify the storage-hashing choice and salt/cost you'd mandate; explain why "uncracked" is ambiguous and why the capture step is the detectable event.

---
> 🔼 Up: [[Password Cracking Tools]]
