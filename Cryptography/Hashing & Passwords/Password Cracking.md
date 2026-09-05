---
title: "Password Cracking"
aliases: ["Cracking", "Hashcat", "John the Ripper", "Dictionary Attack", "Password Cracking"]
tags:
  - tree/crypto
  - cyber/crypto/hashing
  - type/technique
  - difficulty/medium
Domain:
  - "[[Hashing & Passwords]]"
Color: "#FFE119"
verified: 2026-09-05
---

# 🔨 Password Cracking

> [!abstract] Note of [[Hashing & Passwords]]
> Cracking is the attacker's side of the previous note: given a stolen hash, recover the password that produced it. It is guessing at scale, and its feasibility is decided entirely by the defender's choices — hash speed and salting. This note cracks an unsalted hash in a fraction of a millisecond, runs the identical attack against bcrypt to show the defence working, and lays out the attack modes a real assessment uses.

## Parent Learning Order
Hash Functions and Integrity -> Salting and KDFs -> Password Cracking

## The Attacker Already Has the Hash

> *Your login form locks an account after five failed attempts. How much does that slow an attacker cracking your users' passwords?*
>
> Hold your answer — the section below is the response.

Cracking begins after a breach: the attacker has a database of hashes and wants the passwords. Because hashes are one-way, they cannot be reversed — so the attacker instead **guesses**: hash a candidate, compare to the target, repeat. This is **offline** cracking, and it has no rate limit, no lockout, and no logging, because it happens entirely on the attacker's own hardware against a stolen file. It is the opposite of **online** guessing (typing passwords at a live login), which is slow and noisy and easily blocked.

Offline cracking is why password *storage* is the whole game. The login form's rate limiting is irrelevant once the hash is stolen; only the cost of each guess and the uniqueness of each salt stand between the attacker and the plaintext.

## Worked Example: Cracking an Unsalted Fast Hash

Against a plain SHA-256, a dictionary attack is effectively instant. The mechanic is three lines — hash each word in a list, compare to the target:

```shell-session
analyst@lab:~$ python3 -c "
import hashlib, time
target=hashlib.sha256(b'sunshine').hexdigest()
wordlist=['123456','password','qwerty','sunshine','football','dragon']
t=time.time()
for w in wordlist:
    if hashlib.sha256(w.encode()).hexdigest()==target:
        print(f'CRACKED: {w!r} in {(time.time()-t)*1000:.2f} ms'); break"
CRACKED: 'sunshine' in 0.01 ms
```

Six candidates, cracked in a hundredth of a millisecond. A real attack uses a wordlist of hundreds of millions of leaked passwords (`rockyou.txt` and its successors) and a GPU doing billions of hashes per second — so any password that appears in a breach corpus, or is a small variation of one, falls almost immediately. This is the reality behind "SHA-256 is not for passwords": the algorithm is perfect, and completely inadequate for this job, because its speed is the attacker's throughput.

## Worked Example: The Same Attack Against bcrypt

Run the identical dictionary against a bcrypt hash of the same password and the defence appears:

```shell-session
analyst@lab:~$ python3 -c "
import bcrypt, time
target=bcrypt.hashpw(b'sunshine', bcrypt.gensalt(rounds=12))
wordlist=['123456','password','qwerty','sunshine','football','dragon']
t=time.time()
for w in wordlist:
    if bcrypt.checkpw(w.encode(), target):
        print(f'CRACKED: {w!r} in {time.time()-t:.2f} s'); break"
CRACKED: 'sunshine' in 1.11 s
```

The same six-word list now takes over a second instead of a hundredth of a millisecond — because each `checkpw` runs the deliberately expensive bcrypt function. Scale that up: a wordlist that a fast hash chews through in seconds would take a KDF-protected database years, and that is with the password *in the wordlist*. bcrypt did not make `sunshine` a good password — it is still crackable here because it is a common word — but it changed the economics from "every weak password falls instantly" to "only the weakest passwords are worth the attacker's time." Salting adds the other half: because each hash has a unique salt, the attacker cannot crack the whole database at once, only one account at a time.

## The Attack Modes

Real cracking (with `hashcat` on a GPU, or `john`) uses escalating strategies, cheapest first:

- **Dictionary** — try a wordlist of known and leaked passwords. Fastest, catches most real-world passwords.
- **Rule-based** — apply transformations to each word (`password` → `P@ssw0rd!`, `Password2024`) to catch the predictable ways humans "strengthen" a base word. This is where most "complex" passwords fall.
- **Mask / brute force** — try every combination matching a pattern (e.g. eight lowercase letters, or a known corporate format). Feasible only for short or structured passwords.
- **Hybrid** — combine a dictionary with brute-forced suffixes (`sunshine` + four digits), catching the word-plus-number pattern that dominates real passwords.

The workflow is: identify the hash type (the **hash-identifier** and **name-that-hash** tools), pick the wordlist and rules, and let the GPU run — cheapest strategy first, because a dictionary hit in seconds saves a brute-force that would take years.

**The deliberate break:** how hard a password is to crack reads as a property of the password. Strong password, hard to crack; weak password, easy.

The dominant variable is the **storage decision**, made long before the breach and by someone other than the user. `password123` stored under Argon2id at a sensible cost survives longer than a genuinely decent password stored as raw MD5, because the guess rate differs by six orders of magnitude and the wordlist position differs by a few thousand. The user's choice matters and the developer's choice matters far more — which is why "users must choose stronger passwords" is the weakest lever available and the one most often pulled.

**How you'd spot it:** before drawing any conclusion about password quality from a cracking run, look at what you were cracking. Recovering most of a database in an hour is a statement about the hash function, not about the users — the same people behind bcrypt would look disciplined and the same run would return almost nothing. Read the prefix, report the storage finding first, and let the password observations follow it rather than lead.

## What Actually Stops Cracking

Everything in this note is decided by choices made *before* the breach:

- **A slow, memory-hard KDF** (Argon2/bcrypt) collapses the guess rate from billions per second to a handful, which is the difference between minutes and millennia for a strong password.
- **A unique salt per password** forces the attacker to crack each hash separately rather than the whole database at once, and kills precomputed tables.
- **Password strength and length** decide whether a password is even *in* the search space — a long random passphrase is not in any wordlist and too large to brute-force, so no amount of GPU helps.
- **Not reusing passwords** limits the blast radius: a password cracked from one weak site is tried against every other (credential stuffing), so reuse turns one breach into many.

The attacker's speed is real and growing; the defence is entirely in the storage choices of the previous note and the strength of the password itself. Cracking is not magic — it is arithmetic, and the defender sets the exponent.

> [!warning] Authorized use
> Crack only hashes you are authorized to test — your own, a lab's, or an engagement's in scope. Cracking stolen credentials is a criminal offence regardless of how it is done.

## Summary

You should now be able to:

- Explain offline versus online guessing and why offline cracking makes password *storage* the decisive control.
- Crack an unsalted fast hash with a dictionary attack and explain why real wordlists plus GPUs make weak passwords fall instantly.
- Run the same attack against bcrypt and explain how a KDF and salt change the attacker's economics.
- Describe the escalating attack modes (dictionary, rules, mask, hybrid) and name the four defences that actually determine whether a password can be cracked.

---
> 🔼 Up: [[Hashing & Passwords]]
