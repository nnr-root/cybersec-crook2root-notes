---
title: "JWT Security"
aliases: ["JWT", "JSON Web Token", "alg:none", "JWT Attacks", "JWT Security"]
tags:
  - tree/crypto
  - cyber/crypto/applied
  - type/technique
  - difficulty/medium
Domain:
  - "[[Applied Trust & Tooling]]"
Color: "#FFE119"
---

# 🎫 JWT Security

> [!abstract] Note of [[Applied Trust & Tooling]]
> A JSON Web Token is a signed, self-contained claim — "this user is alice, role admin" — that a server trusts because it verifies the signature rather than looking anything up. That design makes JWTs efficient and makes their failures severe: the token is readable by anyone, and the classic attacks trick the server into skipping or confusing the very verification the whole scheme depends on. This note dissects a token and forges an admin one with the `alg:none` attack.

## Parent Learning Order
TLS and PKI -> JWT Security -> CyberChef and the Crypto Toolkit

## What a JWT Is

A JWT is three Base64url-encoded parts joined by dots: **header.payload.signature**. The header names the algorithm; the payload carries the claims (who the user is, their role, an expiry); the signature is computed over the first two parts with a key. A server that issues a JWT can later trust it *without server-side session storage*, because it re-verifies the signature — the token carries its own proof. That statelessness is the appeal, and the source of every pitfall.

## Worked Example: Anatomy of a Token

Building one by hand shows exactly what a JWT is and is not:

```shell-session
analyst@lab:~$ python3 make-jwt.py
a JWT is 3 base64url parts:
eyJhbGciOiAiSFMyNTYiLCAidHlwIjogIkpXVCJ9.eyJ1c2VyIjogImFsaWNlIiwgInJvbGUiOiAidXNlciJ9.F_zRAmf7uISOSJbx2Dj6Sx44XC888JHbaBLH0r_3mZ4
decode header : {'alg': 'HS256', 'typ': 'JWT'}
decode payload: {'user': 'alice', 'role': 'user'}  <- readable by ANYONE; not secret
```

The single most important fact about a JWT is in that last line: the payload is **encoded, not encrypted**. Anyone holding the token can Base64url-decode the payload and read every claim — the user, the role, any data put there. A JWT provides *integrity* (the signature proves the claims were not altered) but **no confidentiality**. Putting a secret, a password, or sensitive personal data in a JWT payload is exposing it to anyone who intercepts the token, which is a common and serious mistake.

## Worked Example: The `alg:none` Forgery

The header names the algorithm, and the JWT specification includes a `none` algorithm meaning "unsigned." A server that honours the header's choice can be told to expect no signature at all — so an attacker edits the payload, sets `alg` to `none`, drops the signature, and walks in:

```shell-session
analyst@lab:~$ python3 forge-none.py
forged token (no signature): eyJhbGciOiAibm9uZSIsICJ0eXAiOiAiSldUIn0.eyJ1c2VyIjogImFsaWNlIiwgInJvbGUiOiAiYWRtaW4ifQ.
a server that honours alg:none accepts this as admin
```

The payload was changed from `role: user` to `role: admin`, the algorithm to `none`, and the signature removed entirely (note the trailing dot with nothing after it). A vulnerable server reads `alg: none`, concludes no verification is needed, and accepts the forged claims — instant privilege escalation with no key and no cracking. The flaw is that the *attacker's token* was allowed to *choose* how it would be verified. The fix is that the server, not the token, must decide the algorithm.

## Algorithm Confusion: RS256 to HS256

A subtler version attacks tokens signed with an asymmetric algorithm. With **RS256**, the server signs with its RSA *private* key and verifies with its *public* key — and the public key is, by definition, public. The attack: take the token, change the header from `RS256` (asymmetric) to `HS256` (symmetric HMAC), and sign it using the server's **public key as the HMAC secret**. A server that reads the algorithm from the token and calls a generic "verify with our key" routine will now HMAC-verify using its public key — which the attacker also has — and accept the forgery.

The root cause is the same as `alg:none`: the server let the token dictate the verification method, so a value meant to be verified *with* a public key was instead verified *as if* the public key were a shared secret. Both attacks vanish under one rule.

## Using JWTs Safely

The pitfalls all reduce to a few disciplines:

- **Pin the algorithm server-side.** The server must decide which algorithm(s) it accepts and reject everything else — never trust the token's `alg` header. This closes both `alg:none` and RS256→HS256.
- **Actually verify the signature.** It sounds obvious, but "decode and trust the payload" without verifying is a real and recurring bug.
- **Never put secrets in the payload** — it is public. Put an identifier; keep the sensitive data server-side.
- **Set and check expiry (`exp`).** A stateless token cannot be revoked by deleting it server-side, so short lifetimes limit a stolen token's usefulness; long-lived JWTs are hard to invalidate.
- **Protect the signing key** — an HS256 secret weak enough to brute-force, or a leaked RS256 private key, forges any token. Strong keys, and prefer asymmetric signing so the verifying services never hold a secret that could sign.

There is also a design debate worth knowing: because JWTs cannot be easily revoked, many argue they are the wrong tool for ordinary web sessions (where a server-side session with an opaque cookie can be revoked instantly) and are better suited to short-lived, cross-service authorization. The security failures above are why "just use JWTs for auth" is not automatically the right call.

## Summary

You should now be able to:

- Describe a JWT's three parts and explain that the payload is encoded, not encrypted — integrity without confidentiality.
- Decode a token's claims, and explain why putting secrets in the payload exposes them.
- Forge a token with the `alg:none` attack and explain the RS256→HS256 confusion attack, identifying the shared root cause (the token dictating its own verification).
- State the disciplines for safe JWT use: pin the algorithm server-side, verify the signature, no secrets in the payload, enforce expiry, and protect the signing key.

---
> 🔼 Up: [[Applied Trust & Tooling]]
