---
title: "Hashing & Passwords"
aliases: ["Hashing", "Passwords", "Password Storage"]
tags:
  - tree/crypto
  - cyber/crypto/hashing
  - type/concept
  - difficulty/info
Domain:
  - "[[Cryptography]]"
Color: "#FFE119"
---

# #️⃣ Hashing & Passwords

> [!abstract] Branch of [[Cryptography]]
> A hash is a one-way fixed-size fingerprint — the tool for proving integrity and for storing passwords without keeping them. This branch builds the hash function, shows why a raw hash is the *wrong* way to store a password, and then attacks stored hashes to prove the point. The recurring lesson: the algorithm is rarely the weak part; how it is used decides everything.

Hashing sits apart from the encryption branches: it is deliberately irreversible and keyless. That one-way property is exactly what makes it right for integrity and password verification — you check a match without ever recovering the input — and exactly why it must be combined with salting and a slow KDF to be safe for low-entropy inputs like passwords.

```mermaid
flowchart LR
    I["any input"] -->|"hash (one-way)"| D["fixed digest"]
    D -.->|"cannot reverse"| I
    style D fill:#3a2f0a,stroke:#ffe119,color:#fff8d6
```

## The leaves in this branch

Read them in order — each sets up the next:

1. **Hash Functions & Integrity** — what a cryptographic hash is, the avalanche effect, the three resistance properties, and integrity verification.
2. **Salting & KDFs** — why a raw password hash is broken, and how salts and slow, memory-hard key-derivation functions fix it.
3. **Password Cracking** — the attacker's side: cracking an unsalted hash instantly, and watching a KDF and salt defeat the same attack.

## 📄 Notes in this branch
- [[Hash Functions and Integrity]]
- [[Salting and KDFs]]
- [[Password Cracking]]

---
> 🔼 Up: [[Cryptography]]
