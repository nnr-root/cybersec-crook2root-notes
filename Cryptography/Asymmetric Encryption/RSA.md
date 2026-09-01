---
title: "RSA"
aliases: ["RSA", "RSA Encryption", "RSA Weak Keys"]
tags:
  - tree/crypto
  - cyber/crypto/asymmetric
  - type/technique
  - difficulty/medium
Domain:
  - "[[Asymmetric Encryption]]"
Color: "#FFE119"
---

# 🔑 RSA

> [!abstract] Note of [[Asymmetric Encryption]]
> RSA is the classic public-key algorithm: a public key anyone can use to encrypt, and a private key only the owner can use to decrypt, with security resting on the difficulty of factoring a large number back into its two primes. This note works RSA end to end on small numbers so the machinery is visible, then factors two "real" keys instantly because they shared a prime — the audit-and-CTF failure that recurs constantly.

## Parent Learning Order
RSA -> Diffie Hellman and ECC -> Digital Signatures

## The Trapdoor Idea

Symmetric encryption has one key that both sides must already share. RSA breaks that requirement with a **trapdoor**: a pair of keys where one direction is easy and the reverse is infeasible without a secret. The public key `(n, e)` is published to the world; the private key `d` is kept secret. Anyone can encrypt to you with your public key; only you can decrypt with your private key.

The trapdoor is factoring. The modulus `n` is the product of two large secret primes `p` and `q`. Multiplying `p × q` to get `n` is instant; recovering `p` and `q` from `n` alone — factoring — is infeasible for a large enough `n`. Everything RSA offers rests on that asymmetry of effort: easy to multiply, ruinous to factor.

**The deliberate break:** everyone learns RSA as "encrypt with the public key, decrypt with the private key," so the reasonable conclusion is that RSA is what encrypts your data on the internet.

It almost never is. RSA is orders of magnitude slower than AES, and it can only encrypt a message shorter than its modulus: a 2048-bit key is 256 bytes wide, and once modern OAEP padding takes its share you are left with **190 bytes** (OAEP-SHA-256) — not enough for a paragraph, let alone a file. So in practice RSA never encrypts your data at all: it encrypts a *symmetric key*, or it signs a *hash*, and AES does the actual work. Holding that correction now is what makes **TLS and PKI** legible later, because the handshake you will read there is exactly this division of labour.

## Worked Example: RSA End to End

RSA is five steps, and on small primes every one is visible. This is real RSA arithmetic, just with tiny numbers so the values fit on a line:

```shell-session
analyst@lab:~$ python3 -c "
p,q=61,53; n=p*q; phi=(p-1)*(q-1); e=17
d=pow(e,-1,phi)              # private exponent = modular inverse of e
m=42
c=pow(m,e,n); dec=pow(c,d,n)
print(f'p={p} q={q} n={n} phi={phi} e={e} d={d}')
print(f'encrypt {m}: c = {m}^{e} mod {n} = {c}')
print(f'decrypt {c}: m = {c}^{d} mod {n} = {dec}')"
p=61 q=53 n=3233 phi=3120 e=17 d=2753
encrypt 42: c = 42^17 mod 3233 = 2557
decrypt 2557: m = 2557^2753 mod 3233 = 42
```

Trace it: pick primes `p, q`; compute `n = p·q = 3233` (public) and `φ(n) = (p−1)(q−1) = 3120` (secret); choose a public exponent `e = 17`; compute the private exponent `d = 2753` as the modular inverse of `e` — the one step that needs `φ(n)`, and therefore needs `p` and `q`. Encryption is `c = mᵉ mod n`; decryption is `m = cᵈ mod n`. The message `42` encrypts to `2557` and decrypts back to `42`. An attacker with only `(n, e)` cannot find `d` without `φ(n)`, and cannot find `φ(n)` without factoring `n` — which is the whole security argument, in three numbers.

## Textbook RSA Is Not Safe RSA

The version above — "textbook RSA" — must never be used directly, because it is deterministic and malleable. The same message always encrypts to the same ciphertext, so an attacker can recognise repeated messages and even build a dictionary of `encrypt(guess)` for small message spaces. And with a small exponent like `e = 3`, a short message `m` where `m³ < n` can be recovered by taking an ordinary cube root, no factoring needed.

Real RSA fixes this with **padding**: **OAEP** (Optimal Asymmetric Encryption Padding) for encryption randomises and structures the message before the RSA operation, so the same plaintext gives different ciphertexts and the small-exponent and malleability attacks disappear. `e = 65537` is the near-universal public exponent — large enough to avoid the small-`e` traps, and structured (a power of two plus one) so encryption stays fast. "RSA with OAEP and e=65537" is the safe recipe; bare `mᵉ mod n` is a teaching tool, not a cipher.

## Worked Example: How RSA Keys Fall

RSA's math is sound; RSA *keys* fail when the primes are generated badly. The most striking case: if two different keys are generated on systems with poor randomness, they can accidentally **share a prime** — and one line of arithmetic then factors both:

```shell-session
analyst@lab:~$ python3 -c "
from Crypto.Util.number import getPrime
from math import gcd
p=getPrime(256)                         # the shared (leaked) prime
q1=getPrime(256); q2=getPrime(256)
n1=p*q1; n2=p*q2                         # two independent-looking 512-bit moduli
print('gcd(n1,n2) > 1 ?', gcd(n1,n2) > 1, '-> factors BOTH keys instantly')
print('recovered q1 correct ?', n1//gcd(n1,n2) == q1)"
gcd(n1,n2) > 1 ? True -> factors BOTH keys instantly
recovered q1 correct ? True
```

Neither `n1` nor `n2` can be factored alone — that is the assumption RSA relies on. But because they share the prime `p`, the greatest common divisor `gcd(n1, n2)` *is* `p`, computed in microseconds by Euclid's algorithm, and once you have `p` both moduli divide out to reveal `q1` and `q2`. This is not hypothetical: scans of the internet's public RSA keys have found large numbers of real keys sharing primes because of weak entropy on embedded devices at boot. The other classic failures follow the same pattern — the algorithm is fine, the parameters betray it: **Fermat factorisation** when `p` and `q` are too close together, and **Wiener's attack** when `d` is too small.

**How you'd spot RSA in the wild:** keys announce themselves and ciphertext has an exact size.

- **PEM headers name the contents literally.** `-----BEGIN PUBLIC KEY-----` is a public key in generic form, `-----BEGIN RSA PRIVATE KEY-----` is a bare PKCS#1 private key, and `-----BEGIN ENCRYPTED PRIVATE KEY-----` means the private key is itself passphrase-protected. Finding the second of those in a repository is a critical finding on sight.
- **RSA ciphertext is exactly the modulus size** — 256 bytes for a 2048-bit key, 512 for 4096, every time, regardless of how short the plaintext was. A 256-byte opaque blob in a protocol is very often an RSA-wrapped symmetric key.
- `openssl rsa -in key.pem -noout -text` prints the modulus size and the parameters, which is how you confirm rather than guess.

The fixed-size property is the useful one operationally: it is what lets you recognise key wrapping in a capture without decrypting anything.

## RSA in Practice

Using RSA safely is a checklist about parameters, not about the algorithm:

- **Key size ≥ 2048 bits** (3072 for long-term); 1024-bit RSA is considered breakable by well-resourced attackers.
- **Always pad** — OAEP for encryption, PSS for signatures. Never encrypt raw messages.
- **Good randomness** for prime generation — the shared-prime disaster above is entirely an entropy failure.
- **Don't encrypt bulk data with RSA.** RSA is slow and size-limited (a 2048-bit key encrypts at most ~245 bytes with OAEP). In practice RSA encrypts a random *symmetric* key, and AES encrypts the actual data — **hybrid encryption**, the pattern every real protocol uses.

Longer term, RSA faces the quantum threat: Shor's algorithm would factor `n` efficiently on a large quantum computer, breaking RSA outright, which is why post-quantum key exchange is being standardised now. Today, though, correctly-parameterised RSA is secure, and every RSA break you will meet in a lab or an audit is a parameter failure of the kind this note factored by hand.

## Summary

You should now be able to:

- Explain RSA's trapdoor — public encrypt / private decrypt — and why its security rests on the difficulty of factoring `n` into `p` and `q`.
- Walk the five RSA steps (choose primes, compute `n` and `φ`, pick `e`, derive `d`, encrypt/decrypt) and explain which step needs the secret primes.
- Explain why textbook RSA is unsafe and what OAEP padding and `e=65537` fix.
- Factor two RSA keys that share a prime with `gcd`, name the other parameter-failure attacks, and state the practical recipe (≥2048-bit, padded, good entropy, hybrid encryption).

---
> 🔼 Up: [[Asymmetric Encryption]]
