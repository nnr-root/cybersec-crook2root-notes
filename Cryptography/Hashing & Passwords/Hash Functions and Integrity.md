---
title: "Hash Functions & Integrity"
aliases: ["Hash", "Hashing", "SHA-256", "MD5", "Hash Functions and Integrity"]
tags:
  - tree/crypto
  - cyber/crypto/hashing
  - type/concept
  - difficulty/easy
Domain:
  - "[[Hashing & Passwords]]"
Color: "#FFE119"
---

# #️⃣ Hash Functions & Integrity

> [!abstract] Note of [[Hashing & Passwords]]
> A cryptographic hash function turns any input into a fixed-size fingerprint that is deterministic, one-way, and violently sensitive to change. It is the tool for *integrity* — proving data was not altered — and the foundation for password storage and digital signatures. This note builds the mental model, shows the avalanche effect directly, and draws the line between hashing, encoding and encryption.

## Parent Learning Order
Hash Functions and Integrity -> Salting and KDFs -> Password Cracking

## What a Hash Function Is

A cryptographic hash function takes an input of any size and produces a fixed-size output — the **digest** or **hash** — with three defining behaviours:

- **Deterministic** — the same input always gives the same digest.
- **Fixed-size output** — SHA-256 always produces 256 bits (32 bytes / 64 hex characters) whether the input is one byte or a gigabyte.
- **One-way** — given a digest, there is no feasible way to recover the input; the function is easy to compute forwards and infeasible to reverse.

The critical distinction from the encoding branch: **hashing is not reversible and has no key**. Base64 can be decoded by anyone; a hash cannot be "decoded" at all, because the function throws information away. This is not a weakness — it is the entire point. A fingerprint that could be reversed to the original would not be a fingerprint.

**The deliberate break:** a fingerprint sounds proportional. Change a little of the input, change a little of the digest — that is how a checksum of a document feels like it should behave, and it is how most people first picture a hash.

It is wrong, and the demonstration below is unambiguous: flip a single bit of input and roughly **half of the output bits change**, with no relationship between the two digests that anyone can compute. That property has a name and a consequence. The name is the avalanche effect. The consequence is that you can never look at two hashes and say "these inputs were similar" — which is exactly why a hash can prove a file is unchanged, and exactly why it cannot tell you *how* it changed.

## Determinism and the Avalanche Effect

Two properties are visible in a single pair of commands. The same input always hashes the same, and a one-character change produces a completely unrelated digest:

```shell-session
analyst@lab:~$ printf 'The quick brown fox' | sha256sum
5cac4f980fedc3d3f1f99b4be3472c9b30d56523e632d151237ec9309048bda9  -
analyst@lab:~$ printf 'The quick brown fux' | sha256sum
b13b70f1c7c1bab3fa5fba7e1093c37ac5c42e46c8d76c3b80355db7e6d7cdb2  -
```

Changing one letter — `fox` to `fux` — changed essentially every bit of the digest. This is the **avalanche effect**: a good hash spreads any input change across the whole output, so digests give no hint of how similar their inputs were. It is what makes a hash usable for integrity — you cannot make a small, undetectable edit — and it is why you cannot "work towards" a target digest by getting gradually closer.

Digest size depends on the algorithm, and it is why algorithm choice matters:

```shell-session
analyst@lab:~$ echo -n "password" | sha256sum
5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8  -
analyst@lab:~$ echo -n "password" | md5sum
5f4dcc3b5aa765d61d8327deb882cf99  -
```

MD5's 128-bit digest is half the length of SHA-256's — and, as the **collision resistance** discussion below explains, far too weak to trust.

## The Three Properties That Make a Hash "Cryptographic"

Any hash is deterministic and fixed-size. A *cryptographic* hash additionally resists three attacks, and the vocabulary matters because breaks are described in these terms:

- **Preimage resistance** — given a digest `H`, you cannot find any input that hashes to `H`. (This is the "one-way" property; it is what protects a stored password hash.)
- **Second-preimage resistance** — given a specific input, you cannot find a *different* input with the same digest. (This protects a signed document from substitution.)
- **Collision resistance** — you cannot find *any two* different inputs with the same digest. (The hardest to achieve, and the first to fall.)

Collision resistance is where the deprecated algorithms died. **MD5** and **SHA-1** are both broken for collisions: attackers can construct two different files with the same digest, which was used to forge certificates and is why neither may be used for signatures or integrity today. Their preimage resistance is weaker but less catastrophically broken — which is why you still occasionally see MD5 used as a non-security checksum, though **SHA-256** should be the default for anything that matters.

## Integrity in Practice

The everyday use of hashing is proving that data arrived unchanged. A download page publishes the SHA-256 of a file; you hash your copy and compare:

```shell-session
analyst@lab:~$ sha256sum ubuntu.iso
946c8...e3f21  ubuntu.iso
```

If your digest matches the published one, the file is bit-for-bit what the publisher released — a corrupted download or a tampered mirror would produce a different digest by the avalanche effect. The same mechanism underlies Git commit IDs (a hash of the commit contents), file-integrity monitoring (a change to a system binary changes its hash), and deduplication (identical files share a digest). For any of these to be *secure* against a deliberate attacker rather than just accidental corruption, the algorithm must be collision-resistant — which is exactly why the integrity world moved off MD5 and SHA-1.

## Where Hashing Stops

A hash is not encryption and, on its own, is not password storage. Two limits set up the rest of the branch:

- **A bare hash is not confidential for low-entropy inputs.** Hashing is one-way, but if the input is guessable — like a password — an attacker simply hashes guesses until one matches, which the **Password Cracking** note demonstrates. One-wayness protects a random 256-bit key; it barely slows an attacker against `password123`.
- **A hash proves integrity only if it is itself trustworthy.** An attacker who can change the file can change the published digest too, unless the digest is protected — by a signature, or by a keyed hash (**HMAC**), which mixes a secret key into the hash so only the key-holder can produce a valid tag.

Those two limits are the doorways to the next two notes: salting and KDFs fix password storage, and the cracking note shows precisely why a raw hash is not enough.

## Summary

You should now be able to:

- Define a cryptographic hash as deterministic, fixed-size and one-way, and explain why it is neither reversible nor keyed.
- Demonstrate the avalanche effect and explain why it makes hashes suitable for integrity.
- Name and distinguish preimage, second-preimage and collision resistance, and explain why MD5 and SHA-1 are deprecated.
- Use a published SHA-256 to verify a file's integrity, and explain the two limits (guessable inputs, unprotected digests) that motivate salting, KDFs and HMAC.

---
> 🔼 Up: [[Hashing & Passwords]]
