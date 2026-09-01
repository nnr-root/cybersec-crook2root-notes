---
title: "Block Cipher Modes"
aliases: ["ECB", "CBC", "CTR", "GCM", "Cipher Modes", "Modes of Operation"]
tags:
  - tree/crypto
  - cyber/crypto/symmetric
  - type/concept
  - difficulty/medium
Domain:
  - "[[Symmetric Encryption]]"
Color: "#FFE119"
---

# 🧱 Block Cipher Modes

> [!abstract] Note of [[Symmetric Encryption]]
> A block cipher encrypts one block; a *mode of operation* is the rule for encrypting a whole message with it, and the choice of mode is one of the highest-consequence decisions in applied cryptography. This note shows — from ciphertext, not from a picture — why ECB leaks plaintext structure through unbroken AES, how CBC hides it, why CBC is malleable, and why modern systems use CTR and the authenticated GCM.

## Parent Learning Order
AES and Block Ciphers -> Block Cipher Modes -> Stream Ciphers

## Why a Mode Is Needed At All

> *AES encrypts exactly 16 bytes at a time. Your message is 160 bytes. Why not run AES ten times and concatenate the results?*
>
> Hold your answer — the section below is the response.

AES turns one 16-byte block into one 16-byte block. A message of several blocks needs a rule relating them, and the obvious rule — encrypt each block independently with the same key — is a trap. The reason is the block cipher's own determinism: with a fixed key, identical input blocks always produce identical output blocks. That determinism is correct and necessary at the block level, but applied naively across a message it turns into a plaintext leak.

## ECB: Where the Pattern Leaks

**Electronic Codebook (ECB)** mode encrypts each block independently. The failure is visible the moment a plaintext contains two identical blocks:

```shell-session
analyst@lab:~$ python3 ecb-vs-cbc.py
plaintext = same 16-byte block, twice
ECB block1: 1438c8f442ce85508d6b1f6826988551
ECB block2: 1438c8f442ce85508d6b1f6826988551  <- IDENTICAL: the repetition leaked
CBC block1: 1438c8f442ce85508d6b1f6826988551
CBC block2: 3b6a96f512b493efd1b55b9c59171566  <- different: chaining hid it
```

The two plaintext blocks were identical, and under ECB their ciphertext blocks are byte-for-byte identical too. AES was not broken — it did exactly what a deterministic permutation must — but the *equality of the plaintext blocks survived into the ciphertext*. Any structure in the plaintext that repeats on 16-byte boundaries is therefore visible in the ciphertext.

This is the real content of the famous "ECB penguin" image: an encrypted bitmap under ECB still shows the penguin, because the image's large areas of one colour are repeating blocks that encrypt to repeating ciphertext. You do not need the picture to see the flaw — the two identical hex lines above *are* the flaw. ECB reveals equality, and equality is structure, and structure is plaintext.

## CBC: Chaining Hides the Pattern

**Cipher Block Chaining (CBC)** breaks the determinism by XORing each plaintext block with the *previous ciphertext block* before encrypting. Identical plaintext blocks now enter AES with different values, so — as the CBC lines above show — they encrypt to different ciphertext. The very first block has no predecessor, so it is XORed with an **Initialization Vector (IV)**: a random, non-secret value that must be different for every message, which is what makes encrypting the same message twice produce different ciphertext.

The IV's requirement is subtle and load-bearing: it need not be secret, but it must be **unpredictable** for CBC. A predictable IV enables the BEAST-style chosen-plaintext attack. "Random IV, fresh per message, sent alongside the ciphertext" is the correct discipline.

## Worked Example: CBC Is Malleable

Hiding patterns is not the same as preventing tampering. CBC has a precise, exploitable malleability — flipping a bit in one ciphertext block flips the *same* bit in the next decrypted block, at the cost of destroying the block you flipped:

```shell-session
analyst@lab:~$ python3 cbc-flip.py
one flipped ciphertext bit in block 1 ->
  decrypted block1: b'\x08\x94Z9\xaf\xde\x8b?\xed\xa4\xc5\xd2\xdaD\x1e\x99'
  decrypted block2: b'BLOCK,TWO-16BYTE'  <- exactly one bit changed here
```

One flipped ciphertext bit turned block 1 into garbage but changed exactly one character of block 2 — the `-` became `,`, a single-bit difference. An attacker who knows the plaintext structure can therefore make *targeted, predictable* edits to later blocks (change an `amount=10` to `amount=90`) by sacrificing an earlier block they do not care about. CBC gives confidentiality and nothing else: it does not detect that the ciphertext was altered. This is why encryption without a separate integrity check is considered broken, and why the final mode fixes exactly this.

## CTR and GCM: The Modern Answers

**Counter (CTR)** mode encrypts a counter value for each block and XORs the result into the plaintext — turning the block cipher into a keystream generator, i.e. a stream cipher (the next note). CTR needs no padding, can be parallelised, and allows random access, but like all keystream schemes it is catastrophic if the counter/nonce is ever reused with the same key.

**Galois/Counter Mode (GCM)** is CTR plus authentication. It produces the ciphertext *and* an authentication tag that any tampering invalidates, so the recipient detects a modified or forged message before trusting it. GCM is the default for TLS and modern protocols precisely because it closes the malleability gap **CBC Is Malleable** opened: it is **AEAD** — Authenticated Encryption with Associated Data — the standard shape of "do encryption correctly" today.

The mode hierarchy, as guidance: never ECB; CBC only with a proper IV *and* a separate authentication step; prefer an AEAD mode (GCM, or ChaCha20-Poly1305) which makes authentication non-optional.

## Summary

You should now be able to:

- Explain why a mode is needed and why the block cipher's determinism makes naive ECB leak plaintext structure.
- Demonstrate, from ciphertext alone, that identical plaintext blocks give identical ECB ciphertext but differ under CBC, and explain what the ECB penguin really shows.
- Explain CBC's IV requirement (unpredictable, fresh, non-secret) and its bit-flipping malleability, and why confidentiality without integrity is insufficient.
- Describe CTR as a keystream mode and GCM as authenticated encryption (AEAD), and give the practical mode-selection order.

---
> 🔼 Up: [[Symmetric Encryption]]
