---
title: "Stream Ciphers"
aliases: ["Stream Cipher", "RC4", "ChaCha20", "Keystream", "Nonce Reuse"]
tags:
  - tree/crypto
  - cyber/crypto/symmetric
  - type/concept
  - difficulty/medium
Domain:
  - "[[Symmetric Encryption]]"
Color: "#FFE119"
---

# 🌊 Stream Ciphers

> [!abstract] Note of [[Symmetric Encryption]]
> A stream cipher generates a long, key-derived **keystream** and XORs it against the plaintext — an attempt to approximate the one-time pad with a short key. It is fast and needs no padding, but it stands or falls on one rule: never reuse a keystream. This note shows a stream cipher working, then breaks two messages encrypted under the same nonce to recover plaintext with no key at all.

## Parent Learning Order
AES and Block Ciphers -> Block Cipher Modes -> Stream Ciphers

## Encryption One Byte at a Time

A block cipher transforms fixed blocks. A **stream cipher** takes a different route: from the key and a **nonce** (number used once) it generates a pseudorandom **keystream** as long as the message, and XORs that keystream against the plaintext. Because XOR is self-inverse (the **XOR** note), decryption is the identical operation with the identical keystream.

This is a direct descendant of the one-time pad. The pad is provably unbreakable because its key is truly random, message-length, and never reused. A stream cipher cannot supply a truly random message-length key, so it *derives* a long keystream from a short key — trading the pad's perfect secrecy for practicality. Everything good and everything dangerous about stream ciphers follows from that trade: the keystream is only as unique as the key-and-nonce pair that generated it.

## Worked Example: A Stream Cipher Working

**ChaCha20** is the modern, widely deployed stream cipher (it secures much of TLS alongside AES-GCM). Encrypting and decrypting show the keystream XOR in action:

```shell-session
analyst@lab:~$ python3 -c "
from Crypto.Cipher import ChaCha20
key=b'k'*32; nonce=b'n'*8
c=ChaCha20.new(key=key,nonce=nonce).encrypt(b'attack at dawn')
print('cipher:', c.hex())
print('back  :', ChaCha20.new(key=key,nonce=nonce).decrypt(c).decode())"
cipher: fd7ba3047ae1441616a66032b0b6
back  : attack at dawn
```

Note the ciphertext is exactly 14 bytes — the same length as the plaintext, with no padding, because a stream cipher encrypts each byte independently against the keystream. That length-preserving property is why stream ciphers are used where padding is awkward: real-time protocols, disk sectors, and network streams.

## The Cardinal Sin: Nonce Reuse

The keystream depends only on the key and the nonce. Encrypt two different messages with the *same* key and nonce, and both are XORed against the *same* keystream — which an attacker can cancel out entirely:

```shell-session
analyst@lab:~$ python3 nonce-reuse.py
c1 XOR c2 == m1 XOR m2 (keystream cancels)
if attacker knows m1, they recover m2: attack the fortress at seven
```

The mathematics is unforgiving. `c1 = m1 ⊕ KS` and `c2 = m2 ⊕ KS`, so `c1 ⊕ c2 = m1 ⊕ m2` — the keystream vanishes, leaving the XOR of the two plaintexts, with no key involved. From there the attacker uses the same crib-dragging and frequency analysis as the repeating-key XOR break in the **XOR** note; and if any part of one message is known or guessable, the corresponding part of the other falls out directly, as the recovered "attack the fortress at seven" shows. This is not a weakness of ChaCha20 — the cipher is fine — it is the keystream-reuse flaw, and it has sunk real systems: WEP's Wi-Fi encryption and Microsoft's PPTP both died largely to nonce/IV reuse.

## RC4's Death and the Modern Choice

**RC4** was the dominant stream cipher for two decades — small, fast, in SSL and WEP everywhere. It is now forbidden. Its keystream has statistical biases: certain output bytes are very slightly more likely to take certain values, and across millions of TLS connections encrypting the same cookie, those biases accumulate until the cookie is recoverable. RC4 was not broken by a single dramatic flaw but by the slow exploitation of a keystream that was not quite random enough.

The lesson set the modern direction. Today's stream cipher is **ChaCha20**, almost always paired with the **Poly1305** authenticator as **ChaCha20-Poly1305** — an AEAD construction, the stream-cipher counterpart to AES-GCM. The pairing is not optional decoration: like all keystream encryption, ChaCha20 alone is malleable (flipping a ciphertext bit flips exactly that plaintext bit, since it is a direct XOR), so authentication is required to detect tampering.

## Security: It All Reduces to Nonce Discipline

A stream cipher's security in practice is almost entirely about never reusing a keystream:

- **Never reuse a (key, nonce) pair.** Use a counter, a random nonce large enough that collisions are negligible, or rekey. This is the whole ballgame.
- **Always authenticate.** A bare stream cipher gives an attacker bit-precise, undetectable edits — worse than CBC's block-granular malleability. Use ChaCha20-Poly1305 or AES-GCM.
- **Prefer AEAD over composing your own.** "Encrypt then MAC" done by hand is a minefield; an AEAD mode makes the safe construction the default one.

The through-line from the one-time pad holds all the way here: the pad is unbreakable because the keystream is never reused, and every stream-cipher disaster is a violation of exactly that rule.

## Summary

You should now be able to:

- Explain a stream cipher as keystream ⊕ plaintext, and its lineage from the one-time pad and its trade-off (short key, derived keystream).
- Encrypt and decrypt with ChaCha20 and explain why the ciphertext is length-preserving.
- Break two messages encrypted under a reused nonce by cancelling the keystream (`c1 ⊕ c2 = m1 ⊕ m2`) and recovering plaintext from a crib.
- Explain why RC4 was deprecated, why ChaCha20 is paired with Poly1305, and why nonce discipline and authentication are the whole of practical stream-cipher security.

---
> 🔼 Up: [[Symmetric Encryption]]
