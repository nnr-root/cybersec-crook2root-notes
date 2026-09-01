---
title: "AES & Block Ciphers"
aliases: ["AES", "Block Cipher", "Rijndael", "AES and Block Ciphers"]
tags:
  - tree/crypto
  - cyber/crypto/symmetric
  - type/concept
  - difficulty/medium
Domain:
  - "[[Symmetric Encryption]]"
Color: "#FFE119"
---

# 🔒 AES & Block Ciphers

> [!abstract] Note of [[Symmetric Encryption]]
> A block cipher is a keyed, reversible permutation on a fixed-size block of bits — the primitive almost all symmetric encryption is built from, and AES is the one the world standardised on. This note explains what a block cipher actually does, how AES is structured, and the crucial limitation that a block cipher alone can only encrypt exactly one block, which is what forces the *modes* in the next note.

## Parent Learning Order
AES and Block Ciphers -> Block Cipher Modes -> Stream Ciphers

## What a Block Cipher Actually Is

A block cipher is a function that takes a fixed-size block of bits and a key, and produces a block of the same size — reversibly. For a given key it is a **permutation**: every possible input block maps to exactly one output block and back, with no collisions. Change the key and you get a completely different permutation. There are astronomically many possible permutations of a 128-bit block, and the key selects which one is in effect.

Two design goals, named by Claude Shannon, make that permutation secure:

- **Confusion** — each bit of the output depends on the key in a complicated way, so seeing outputs tells you nothing usable about the key.
- **Diffusion** — flipping one input bit changes about half the output bits (the *avalanche effect*), so ciphertext reveals no structure of the plaintext.

A cipher that achieves both looks, to anyone without the key, like a random mapping — and that is exactly what "secure" means for a block cipher.

**The deliberate break:** the natural expectation is that encrypting *n* bytes produces *n* bytes — encryption scrambles data, it does not invent it. Watch the worked example below: a **27-byte** message comes back as **32 bytes** of ciphertext, inside a file that is larger still.

That is not overhead to shrug at, it is the whole nature of a block cipher. AES transforms exactly 16 bytes at a time and can do nothing with a partial block, so 27 bytes is padded up to the next multiple of 16 — and on top of that openssl prepends a `Salted__` header plus 8 bytes of salt. Every question in this branch that follows — padding, modes, IVs, nonces — exists because a real message is never a neat multiple of 16.

## AES: The Standard

**AES** (Advanced Encryption Standard, originally Rijndael) operates on **128-bit (16-byte) blocks** with a key of 128, 192 or 256 bits. It is a *substitution-permutation network*: each round substitutes bytes through a fixed lookup table (the S-box, providing confusion), then shifts and mixes them across the block (providing diffusion), then XORs in a round key derived from the main key. More rounds mean more mixing, and the key size sets the count:

```shell-session
analyst@lab:~$ python3 -c "print('AES-128: 10 rounds   AES-192: 12 rounds   AES-256: 14 rounds')"
AES-128: 10 rounds   AES-192: 12 rounds   AES-256: 14 rounds
```

AES-256 is not "twice as strong" as AES-128 in any linear sense — both are far beyond brute force — but its larger key gives a wider margin against future advances, which is why it is the common default for data at rest. After more than two decades of intense analysis, AES has no practical break; every real-world AES failure is a failure of how it was *used*, not of the cipher.

## Worked Example: Encrypt and Decrypt

`openssl` exposes AES directly. Encrypting a message and looking at the raw output shows what a real ciphertext is:

```shell-session
analyst@lab:~$ echo -n "transfer 1000 to account 42" > msg.txt
analyst@lab:~$ openssl enc -aes-256-cbc -pbkdf2 -in msg.txt -out msg.enc -pass pass:hunter2
analyst@lab:~$ xxd msg.enc | head -2
00000000: 5361 6c74 6564 5f5f 8b19 9760 c09c b62a  Salted__...`...*
00000010: 89b3 e2aa 5208 9921 f506 08dd 8b52 5c51  ....R..!.....R\Q
analyst@lab:~$ openssl enc -d -aes-256-cbc -pbkdf2 -in msg.enc -pass pass:hunter2
transfer 1000 to account 42
```

Three things in that output matter. The ciphertext begins `Salted__` followed by eight random bytes — openssl's salt header, which lets the same password produce different ciphertext each time. `-pbkdf2` tells openssl to stretch the password into a key with a proper key-derivation function rather than a fast hash (the reason for that is the whole **Salting and KDFs** note). And the ciphertext is 32 bytes for a 27-byte message: it was padded up to a whole number of 16-byte blocks, because a block cipher cannot encrypt a partial block — which is the limitation **One Block Is Not Enough** turns into the next note.

## One Block Is Not Enough

AES encrypts exactly 128 bits. Real messages are longer, shorter, or not a multiple of 16 bytes. Two problems follow, and neither is solved by the cipher itself:

- **Messages longer than one block** must be split, and the cipher needs a rule for how the blocks relate — encrypt each independently, or chain them. That rule is the **mode of operation**, and the choice between modes is a security decision with dramatic consequences, as the next note shows.
- **Messages that are not a whole number of blocks** must be **padded** to fill the final block (PKCS#7 padding appends bytes whose value equals the number of pad bytes). How padding errors are reported can itself leak plaintext — the *padding oracle* attack — which is one reason authenticated modes are preferred.

So "encrypt with AES" is never a complete instruction. "Encrypt with AES in which mode, with what IV, and is it authenticated?" is the real question, and the block cipher is only the first of those answers.

## Security: The Cipher Is Not the Weak Point

AES itself is not where systems break. The failures are around it:

- **Key management** — a hardcoded key, a key in source control, or a password used directly as a key defeats AES completely without touching the algorithm.
- **Mode misuse** — ECB mode (next note) leaks plaintext structure through the strongest cipher.
- **Missing authentication** — encryption without an integrity check lets an attacker tamper with ciphertext undetected; modern practice uses authenticated modes (AES-GCM) for exactly this reason.
- **Side channels** — a naive software AES can leak key bits through cache-timing, which is why production code uses the CPU's hardware AES instructions (AES-NI), both faster and constant-time.

The takeaway for both attacker and defender: do not attack or defend the AES math. Attack and defend the key, the mode, the authentication and the implementation, because that is where every real AES compromise lives.

## Summary

You should now be able to:

- Explain a block cipher as a keyed, reversible permutation on a fixed block, and define confusion, diffusion and the avalanche effect.
- Describe AES's block size, key sizes and round counts, and its substitution-permutation structure.
- Encrypt and decrypt with `openssl`, and explain the salt header, why `-pbkdf2` is used, and why a 27-byte message produces 32 bytes of ciphertext.
- Explain why a block cipher alone is incomplete — the need for a mode of operation and padding — and why every real AES failure is a usage failure, not a cipher break.

---
> 🔼 Up: [[Symmetric Encryption]]
