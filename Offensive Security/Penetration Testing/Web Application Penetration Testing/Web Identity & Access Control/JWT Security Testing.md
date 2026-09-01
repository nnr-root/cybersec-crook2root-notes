---
title: "JWT Security Testing"
aliases: ["JWT Testing", "JSON Web Token Security"]
tags: [tree/offensive, cyber/offensive/web/identity/jwt, type/technique, difficulty/medium]
Domain: "[[Web Identity & Access Control]]"
Color: "#DC143C"
---

# 🎟️ JWT Security Testing

> [!warning] Authorized simulation only
> JWT flaws can forge any identity. Prove them with synthetic tokens and benign claims, never by impersonating a real user. Test only in-scope applications.

## Parent Learning Order
Web Authentication Testing -> Broken Access Control -> JWT Security Testing -> Federated Identity & SSO -> MFA, Recovery & Session Bypass Testing

## A Token You Can Read, and Must Not Be Able to Forge

A **JSON Web Token (JWT)** is a compact, self-contained token that carries claims about a user (their ID, role, expiry) in a format the server can verify without a database lookup — which is why it is ubiquitous in modern APIs and SSO. A JWT has three parts, separated by dots: `header.payload.signature`. The header and payload are **base64-encoded JSON — not encrypted**, so anyone can read them. The signature is what makes the token trustworthy: the server signs the header+payload with a key, and verifies that signature on every request. If the signature verifies, the claims are trusted.

The entire security rests on the signature being **correctly verified**. Almost every JWT vulnerability is a way to make the server accept a token whose claims the attacker chose — by defeating, skipping, or weakening signature verification.

> [!tip] The analogy, and where it breaks
> A JWT is like a tamper-evident sealed envelope: anyone can read the letter through the window (payload is not encrypted), but the wax seal (signature) proves it came from the sender unaltered. The analogy breaks because a lazy recipient can be tricked into ignoring the seal entirely — accepting an envelope sealed with *no wax* or with the attacker's *own seal* — which no physical recipient would do, yet JWT libraries have done exactly this.

**Prerequisites:** base64 encoding, digital signatures (symmetric HMAC vs. asymmetric RSA), and the authentication leaf.

## The Classic JWT Attacks

All exploit signature verification failures:

| Attack | The failure |
| --- | --- |
| **`alg: none`** | Server accepts a token declaring no signature algorithm — no signature needed |
| **Algorithm confusion** | Server uses an RSA *public* key as an HMAC *secret* — attacker signs with the public key |
| **Weak HMAC secret** | The signing secret is guessable/crackable — attacker signs their own tokens |
| **No signature verification** | Server decodes but never verifies — any signature (or none) accepted |
| **Claim tampering + weak check** | Change `role: user` → `role: admin` and re-sign with a cracked/known key |

The infamous **`alg: none`** attack: the JWT header specifies the algorithm, and some libraries honored `alg: none` — meaning "unsigned." An attacker changes the payload (e.g. `admin: true`), sets `alg: none`, removes the signature, and a vulnerable server accepts it because it "verified" a token that declared it needed no verification.

**Algorithm confusion** is subtler: an app expects RSA (asymmetric — verify with a *public* key, sign with a *private* key). If the attacker changes `alg` to HMAC (symmetric — same key signs and verifies) and signs with the *public* RSA key (which is, by definition, public), a naive library uses that public key as the HMAC secret and the signature verifies. The attacker signed a token using a key everyone knows.

## Reading and Tampering a JWT

Because the payload is just base64 JSON, decoding it is trivial — and that's the point of testing: can you change a claim and get it accepted?

```bash
# decode a JWT payload (no key needed — it's not encrypted)
echo "eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjoiYWxpY2UiLCJyb2xlIjoidXNlciJ9.abc" | \
  cut -d. -f2 | base64 -d 2>/dev/null
```

```text
{"user":"alice","role":"user"}
```

The payload reads `role: user` — visible to anyone. The test is whether changing it to `role: admin` (and defeating the signature) produces a token the server accepts. If the server checks the signature properly with a strong secret, you cannot; if it accepts `alg: none`, uses a weak secret, or is confused about the algorithm, you can forge `admin`.

```mermaid
flowchart TD
    T["JWT: header.payload.signature"] --> R["Read payload (base64, not encrypted)"]
    R --> M["Tamper a claim: role=user -> admin"]
    M --> S{"How does server verify?"}
    S -->|"accepts alg:none"| N["Strip signature -> accepted"]
    S -->|"RSA verify with pub as HMAC secret"| C["Sign with public key -> accepted"]
    S -->|"weak HMAC secret"| W["Crack secret -> re-sign -> accepted"]
    S -->|"strong verify"| SAFE["Rejected"]
    N --> P["Forged admin token (prove with synthetic identity)"]
```

## When alg:none is already patched

- **Impersonating real users.** Forging a token for a real admin is over the line; prove with a synthetic identity and a benign claim.
- **`alg: none` may be patched.** Modern libraries reject it, so a failed attempt may mean a hardened library. Try algorithm confusion and secret-cracking before concluding safe.
- **Secret-cracking feasibility.** A weak HMAC secret is crackable offline (like a password); a strong random secret is not. Report the *unsafe verification* even if you can't crack the specific secret — a weak secret is the flaw.
- **Reading ≠ breaking.** Decoding a JWT proves nothing about its security — it's *supposed* to be readable. The finding is *forging* an accepted token, not reading one.
- **Sensitive data in the payload.** Because the payload is not encrypted, secrets placed in it are exposed — a JWT should never carry sensitive data in its claims.

## Security Implications — Detection & Defense

- **Verify the signature with a strong key, and pin the algorithm.** The definitive fixes: reject `alg: none`, do not accept an algorithm different from what the app expects (defeating confusion), and use a long random HMAC secret or proper RSA keys.
- **Never trust an unverified token** — decode *and verify* before honoring any claim; a library that decodes without verifying is the vulnerability.
- **Keep secrets strong and rotated** — a weak or leaked signing secret lets an attacker mint valid tokens indefinitely; rotation limits the window.
- **Do not put sensitive data in the payload** (it's readable), and set short expiry so a stolen token's window is small.
- **Detection**: tokens with `alg: none`, unexpected algorithms, or claims inconsistent with issuance are the signals — but the durable defense is correct verification, since a properly-forged token that the server accepts looks legitimate.

## Summary

You should now be able to:

- Explain the three JWT parts, why the payload is readable, and why the signature is what makes the token trustworthy.
- Decode and tamper a JWT payload, forge an `alg:none` token to escalate role, and recognize the algorithm-confusion and weak-secret attacks.
- Explain why pinning the algorithm and verifying with a strong key are the fixes, why algorithm confusion turns a public key into a signing secret, and why sensitive data must never go in a JWT payload.

---
> 🔼 Up: [[Web Identity & Access Control]]
