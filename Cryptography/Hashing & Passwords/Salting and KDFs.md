---
title: "Salting & KDFs"
aliases: ["Salt", "Salting", "KDF", "bcrypt", "scrypt", "Argon2", "Salting and KDFs"]
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

# 🧂 Salting & KDFs

> [!abstract] Note of [[Hashing & Passwords]]
> Storing a raw hash of a password is a vulnerability, not a protection. Two independent fixes are needed: a **salt** so identical passwords do not share a hash, and a **key-derivation function** so each guess is deliberately, ruinously slow. This note shows why a fast hash loses — a bcrypt hash is measured here at roughly 372,000 times slower per guess than SHA-256, by design — and how Argon2, scrypt and bcrypt turn that slowness into a defence.

## Parent Learning Order
Hash Functions and Integrity -> Salting and KDFs -> Password Cracking

## Why a Raw Password Hash Is Broken

> *You store SHA-256 of each password rather than the password itself. Two users independently choose `password123`. What does your database show?*
>
> Hold your answer — the section below is the response.

The intuition "hash the password so we never store it in plaintext" is right in spirit and dangerous in practice, for two separate reasons.

First, a plain hash is **fast**, and fast is the attacker's friend when the input is guessable. Second, a plain hash is **unsalted**, so identical passwords produce identical hashes:

```shell-session
analyst@lab:~$ python3 -c "
import hashlib
for u in ['alice','bob']:
    print(u, 'uses password123 ->', hashlib.sha256(b'password123').hexdigest()[:32])"
alice uses password123 -> ef92b778bafe771e89245b89ecbc08a4
bob uses password123 -> ef92b778bafe771e89245b89ecbc08a4
```

Alice and Bob chose the same password and their stored hashes are byte-for-byte identical. This leaks that they share a password, and — worse — it means an attacker can precompute the hashes of millions of common passwords *once* into a **rainbow table** and then look up every stolen hash instantly. One table breaks every unsalted database in the world simultaneously.

## Salt: Make Every Hash Unique

A **salt** is a random value, unique per password, stored alongside the hash and mixed into it before hashing. It is not secret — it lives in the database next to the hash — but it makes identical passwords produce different hashes:

```shell-session
analyst@lab:~$ python3 -c "
import hashlib, os
for u in ['alice','bob']:
    salt=os.urandom(8)
    print(u, 'salt', salt.hex(), '->', hashlib.sha256(salt+b'password123').hexdigest()[:24])"
alice salt c24c89905431849b -> 3b201ff957046b0d293478bd
bob   salt 17a65e2aac745130 -> 265f9bb88073dc32e1e864a1
```

Same password, different salts, different hashes. This kills the rainbow table outright: a precomputed table would have to be rebuilt for every distinct salt, which defeats the whole point of precomputation. The attacker is forced back to attacking each password individually — which is where the second fix makes that individual attack painful. A salt must be **random and unique per password**; a single shared salt for the whole database only forces one table rebuild, and no salt at all is the broken case above.

## Worked Example: Why a Fast Hash Loses

Salting stops precomputation but not guessing. Against a stolen, salted SHA-256 hash the attacker still hashes guesses — and a general-purpose hash is designed to be *fast*, which is exactly wrong for a password. The gap is enormous and measurable:

```shell-session
analyst@lab:~$ python3 cost.py
50000 SHA-256 hashes: 0.037s  ->  1,364,525 hashes/sec
1 bcrypt(cost=12)  : 0.273s  ->  4 hashes/sec
bcrypt is ~372,494x slower PER HASH by design
```

On this single unoptimised CPU, SHA-256 manages over 1.3 million guesses a second — and a real attacker with a GPU does *billions*. bcrypt at cost 12 manages four. That six-orders-of-magnitude gap is not an accident or an inefficiency: it is the KDF's purpose. A hash function is built to be fast; a key-derivation function is deliberately built to be slow, so that the attacker's guessing rate collapses while a single legitimate login — which does the work once — is unaffected.

## KDFs: Turning Slowness Into Defence

A **key-derivation function** (also called a password-hashing function) is a hash designed to be expensive, with a tunable cost so it can be made slower as hardware gets faster. The three worth knowing, in order of preference:

- **Argon2** — the current standard (winner of the Password Hashing Competition). It is tunable in *time*, *memory* and *parallelism*, and its memory-hardness is the key modern property: it forces each guess to use a large block of RAM, which is what neutralises GPU and ASIC attackers, since those get their speed from massive parallelism with little memory per core.
- **scrypt** — the earlier memory-hard function, still solid; also forces high memory use per guess.
- **bcrypt** — older and not memory-hard, but battle-tested and still acceptable; its `cost` factor sets the number of iterations. A bcrypt hash records its cost inline (`$2b$12$...` means cost 12), so it is self-describing.

The common thread is a *tunable cost* baked into the stored hash, so the whole database can be upgraded to a higher cost over time without knowing anyone's password. Plain SHA-256, SHA-1 or MD5 — however many times iterated by hand — are not substitutes, because they are not memory-hard and their raw speed is the problem.

**The deliberate break:** salt reads as the thing that makes a stored password safe — add a salt and the hash is protected.

Salt does exactly one job: it makes every hash unique, so precomputed tables are useless and each hash must be attacked on its own. It does nothing about **speed**, and speed is where the attack lives. A salted SHA-256 still falls at billions of guesses per second — the salt only means the attacker works through the database one row at a time instead of all rows at once, which is a real improvement and not remotely sufficient. Uniqueness and cost are separate properties provided by different mechanisms, and collapsing them into "we salt our passwords" is how a database ends up looking defended and cracking in an afternoon.

**How you'd spot it:** check the stored value for both properties, because they leave different traces. A self-describing string naming a function and its cost parameters — `$argon2id$v=19$m=65536,t=3,p=4$…` — carries uniqueness and deliberate slowness together. A hex digest with a salt column beside it carries uniqueness and no cost whatsoever, and it is by far the more common shape in a real database.

## Doing Password Storage Correctly

The complete recipe, and the reasoning behind each part:

1. **Never store the password**, and never store a plain hash of it.
2. **Use a purpose-built KDF** — Argon2id by default, scrypt or bcrypt if constrained — never a bare cryptographic hash.
3. **Salt is automatic** in these functions — they generate and embed a unique salt per hash, so you store the single self-describing string they return.
4. **Tune the cost** so a single hash takes a noticeable fraction of a second on your hardware — slow enough to cripple bulk guessing, fast enough that one login is imperceptible.
5. **Consider a pepper** — a secret value, held outside the database (in code or an HSM), mixed in as well — so a database-only breach still lacks a component needed to crack.

Get this right and a stolen database is a slow, per-password grind against strong hashes; get it wrong and it is the instant catastrophe the next note demonstrates.

## Summary

You should now be able to:

- Explain the two independent flaws of a raw password hash — it is unsalted (rainbow-able) and fast (guessable) — and demonstrate the unsalted-collision problem.
- Add a per-password salt and explain why it defeats precomputed rainbow tables without needing to be secret.
- Explain, from measured hash rates, why a KDF's deliberate slowness and memory-hardness defeat bulk guessing where a fast hash cannot.
- Choose and configure Argon2/scrypt/bcrypt correctly, and describe the full modern password-storage recipe including cost tuning and an optional pepper.

---
> 🔼 Up: [[Hashing & Passwords]]
