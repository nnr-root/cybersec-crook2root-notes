---
title: Cryptography
aliases:
  - Cryptography Hub
tags:
  - tree/crypto
  - cyber/moc
Domain:
  - "[[Cyber Security]]"
Color: "#FFE119"
---

# 🔐 Cryptography

> [!abstract] The Domain
> How data is represented, kept secret, proven unchanged, and proven authentic — and how each of those is attacked. This domain runs from raw bytes to the TLS handshake in five branches, with a recurring lesson: the algorithms are rarely the weak point; how they are used is where systems break.

```mermaid
flowchart TD
    C["🔐 Cryptography"]
    C --> E["🔤 Encoding & Obfuscation<br/><i>representation, no secrecy</i>"]
    C --> S["🔒 Symmetric Encryption<br/><i>one shared key</i>"]
    C --> H["#️⃣ Hashing & Passwords<br/><i>one-way fingerprints</i>"]
    C --> A["🔑 Asymmetric Encryption<br/><i>public/private keypairs</i>"]
    C --> P["🔏 Applied Trust & Tooling<br/><i>TLS, JWT, tooling</i>"]
    style C fill:#3a2f0a,stroke:#ffe119,color:#fff8d6
```

## 🚦 Start Here — the branch order

The branches build on each other; read them in order if you are new:

1. **[[Encoding & Obfuscation]]** — bits, hex, Base64 and XOR. The notation everything else is written in, and the crucial first lesson that encoding is not encryption.
2. **[[Symmetric Encryption]]** — AES, block cipher modes and stream ciphers: fast encryption with one shared key, and the usage mistakes (ECB, nonce reuse) that break it.
3. **[[Hashing & Passwords]]** — one-way hashes, salting, key-derivation functions, and cracking. Integrity, and how to store a password without keeping it.
4. **[[Asymmetric Encryption]]** — RSA, Diffie-Hellman and digital signatures: agreeing secrets and proving identity between parties who never met.
5. **[[Applied Trust & Tooling]]** — TLS/PKI and JWT, where every primitive above composes into the systems the internet actually runs on.

---
> 🌐 Back to the domain map: [[Cyber Security]]
