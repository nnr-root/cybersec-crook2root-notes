---
title: "TLS & PKI"
aliases: ["TLS", "SSL", "PKI", "X.509", "Certificate", "Certificate Authority", "TLS and PKI"]
tags:
  - tree/crypto
  - cyber/crypto/applied
  - type/concept
  - difficulty/medium
Domain:
  - "[[Applied Trust & Tooling]]"
Color: "#FFE119"
---

# 🔐 TLS & PKI

> [!abstract] Note of [[Applied Trust & Tooling]]
> TLS is where every primitive in this domain assembles into the padlock in the browser bar, and PKI is the trust system that answers the question key exchange left open: *who* is on the other end. This note builds a private certificate authority, issues a certificate, and watches verification fail without the CA and succeed with it — the exact check your browser runs on every HTTPS connection.

## Parent Learning Order
TLS and PKI -> JWT Security -> CyberChef and the Crypto Toolkit

## The Problem PKI Solves

> *The padlock is showing. What has your browser just proved?*
>
> Hold your answer — the section below is the response.

The **Diffie-Hellman** note ended on a gap: key exchange agrees a secret with *someone*, but not with a *verified* someone, so an unauthenticated exchange falls to a machine-in-the-middle. Encryption without identity is a padlock with no idea whose door it is on. PKI — Public Key Infrastructure — fills the gap by binding a public key to an identity in a way anyone can verify, so that when your browser agrees a key with `bank.example`, it *knows* the public key it used really belongs to the bank and not to an attacker in the path.

**The deliberate break:** the padlock is read, almost universally, as "this site is safe." It does not say that, and the worked example below shows precisely what it does say.

A padlock means the connection is encrypted to *whoever presented a certificate your machine's trust store accepts for that name*. It makes no claim that the operator is honest, that the site is not a phishing page, or that the certificate was issued to the party you meant. Note which half of that sentence is doing the work: **your machine's trust store**. Change what is in it — install one rogue root CA — and every certificate that CA signs verifies as `OK`, padlock and all. That is not a hypothetical; it is how corporate TLS interception works, and how TLS-inspecting malware works.

## Certificates and the Chain of Trust

A **certificate** is a signed statement: "this public key belongs to this identity," signed by a **Certificate Authority (CA)** using the digital-signature mechanism from the previous branch. Your browser ships with a list of trusted **root CAs**. A website's certificate is signed by a CA, which may be signed by another CA, forming a **chain** that must terminate at one of those trusted roots. Verification walks the chain: each certificate's signature is checked with the next CA's public key, up to a root the browser already trusts.

The trust is transitive and rooted. You trust `bank.example` because a CA you trust vouched for it, because your browser vendor decided that CA is trustworthy. Break any link — a compromised CA, an untrusted root — and the chain does not verify.

## Worked Example: A Private CA, End to End

The whole system fits in a handful of `openssl` commands. First, become a certificate authority and issue a certificate to a server:

```shell-session
analyst@lab:~$ openssl req -x509 -new -key ca.key -days 3650 \
    -subj "/CN=Crook2Root Lab Root CA" -out ca.crt
analyst@lab:~$ openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -days 365 -out server.crt
analyst@lab:~$ openssl x509 -in server.crt -noout -subject -issuer
subject=CN = lab.example.test
issuer=CN = Crook2Root Lab Root CA
```

The certificate says its **subject** is `lab.example.test` and its **issuer** — the CA that signed it — is the lab root. Now verify that certificate the way a browser would. First without trusting the CA:

```shell-session
analyst@lab:~$ openssl verify server.crt
CN = lab.example.test
error 20 at 0 depth lookup: unable to get local issuer certificate
```

**Rejected.** `error 20` is the exact failure behind the browser's "your connection is not private" warning: the certificate is signed by an issuer the verifier does not trust, so the chain cannot be built to a known root. Now verify again, this time trusting the lab CA:

```shell-session
analyst@lab:~$ openssl verify -CAfile ca.crt server.crt
server.crt: OK
```

**Accepted.** The only thing that changed was whether the CA was in the trust store. That single difference — is the signing CA trusted — is the entire basis of web trust, and it is why installing a rogue root CA on a machine is so dangerous: it makes every certificate that rogue CA signs verify as `OK`, which is precisely how corporate TLS interception and TLS-inspecting malware work.

## The Handshake: Where Everything Composes

An HTTPS connection assembles every primitive in this domain in one exchange:

1. The server presents its **certificate**. The client verifies the chain to a trusted root (**A Private CA, End to End**, above) and checks the name matches and the certificate is in date — this is the **signature** and **PKI** machinery.
2. The two sides run an **ephemeral elliptic-curve Diffie-Hellman** exchange to agree a fresh shared secret, and the server **signs** its exchange parameters with the certificate's private key — binding the key agreement to the verified identity, which is what defeats the machine-in-the-middle.
3. That shared secret keys an **authenticated symmetric cipher** (AES-GCM or ChaCha20-Poly1305) which encrypts the actual traffic.

So the padlock is: asymmetric signatures for identity, DH for key agreement with forward secrecy, and symmetric AEAD for bulk data — hashing underneath all of it. TLS is not one algorithm; it is the correct *composition* of every branch of this tree, which is why it is the domain's natural capstone.

**How you'd spot which trust check failed:** `openssl verify` numbers its errors, and each number points at a different problem with a different fix.

| Error | What it means | Where the fix is |
|:--|:--|:--|
| `error 20` — unable to get local issuer certificate | The chain cannot be built to a trusted root | Trust store, or a missing intermediate the server should be sending |
| `error 18` — self-signed certificate | The leaf signed itself; there is no chain at all | Issue from a CA, or explicitly trust it in a lab |
| `error 10` — certificate has expired | The chain is fine; the dates are not | Renewal, not trust |

Reading the number first stops the most common misdiagnosis in TLS work. A browser warning is not one condition, and "add it to the trust store" fixes exactly one of the three — for the other two it hides a real problem behind a decision you will forget you made.

## How PKI Fails in the Real World

The math rarely breaks; the trust system does, and the failures are the findings:

- **Mis-issuance** — a CA issues a certificate for a domain to the wrong party, through fraud or a compromised registration check. The offending certificate is fully valid until revoked.
- **CA compromise** — a breached CA (DigiNotar, 2011) can sign certificates for any domain, and every browser trusting it is deceived until the CA is distrusted.
- **Weak or expired certificates** — a self-signed or expired certificate fails verification exactly as in **A Private CA, End to End**; users trained to click through those warnings are the vulnerability.
- **Revocation is hard** — telling the world a certificate is no longer valid (CRL, OCSP) is unreliable, which is why certificate lifetimes have been shortened aggressively.

The defences layer on top: **HSTS** forces HTTPS so an attacker cannot strip it, **certificate pinning** ties an app to a specific certificate so a rogue CA is not enough, and **Certificate Transparency** logs every issued certificate publicly so mis-issuance is detectable. Each exists because the trust layer, not the cryptography, is where TLS is actually attacked.

## Summary

You should now be able to:

- Explain why PKI exists — binding a public key to a verified identity — and how the chain of trust roots in the browser's trusted CAs.
- Describe a certificate as a CA-signed statement, and build/verify one with `openssl`, explaining the `error 20` rejection and the `OK` acceptance.
- Explain how the TLS handshake composes signatures/PKI, ephemeral DH, and authenticated symmetric encryption, and why signing the DH parameters defeats the middle-man.
- Name the real-world PKI failure modes (mis-issuance, CA compromise, weak certs, revocation) and the defences (HSTS, pinning, Certificate Transparency).

---
> 🔼 Up: [[Applied Trust & Tooling]]
