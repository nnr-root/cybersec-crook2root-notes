---
title: "Digital Signatures"
aliases: ["Signature", "Digital Signature", "ECDSA", "Ed25519", "PSS", "Digital Signatures"]
tags:
  - tree/crypto
  - cyber/crypto/asymmetric
  - type/technique
  - difficulty/medium
Domain:
  - "[[Asymmetric Encryption]]"
Color: "#FFE119"
---

# ✍️ Digital Signatures

> [!abstract] Note of [[Asymmetric Encryption]]
> A digital signature inverts the public-key roles: the owner signs with the *private* key, and anyone verifies with the *public* key. That single swap delivers authenticity, integrity and non-repudiation at once — proof that a specific holder produced a message and that it has not changed since. This note signs and verifies a document, then watches verification fail the instant one character is altered.

## Parent Learning Order
RSA -> Diffie Hellman and ECC -> Digital Signatures

## Inverting the Keys

> *Public key locks, private key unlocks. What do you get if you run it the other way round?*
>
> Hold your answer — the section below is the response.

Encryption uses the public key to lock and the private key to unlock. A signature does the reverse: the private key **signs**, and the public key **verifies**. Because only the owner holds the private key, a valid signature proves three things at once:

- **Authenticity** — it came from the holder of that private key.
- **Integrity** — the message has not changed since it was signed (a change invalidates the signature).
- **Non-repudiation** — the signer cannot later deny signing, because no one else could have produced the signature.

This is the mechanism behind trust on the internet: a TLS certificate is a signed statement, a software update is signed by its vendor, a signed commit proves authorship. The whole point is that verification needs only the *public* key, so anyone can check a signature without being able to forge one.

## Worked Example: Sign and Verify

Signing a document with a private key and verifying with the public key is a handful of `openssl` commands. Here with Ed25519, the modern elliptic-curve signature scheme:

```shell-session
analyst@lab:~$ openssl genpkey -algorithm ed25519 -out sk.pem
analyst@lab:~$ openssl pkey -in sk.pem -pubout -out pk.pem
analyst@lab:~$ echo -n "pay Bob 100" > doc.txt
analyst@lab:~$ openssl pkeyutl -sign -inkey sk.pem -rawin -in doc.txt -out doc.sig
analyst@lab:~$ openssl pkeyutl -verify -pubin -inkey pk.pem -rawin -in doc.txt -sigfile doc.sig
Signature Verified Successfully
```

The private key `sk.pem` produced the signature `doc.sig` over the document; the public key `pk.pem` — which can be handed to anyone — confirmed it. A verifier who has only the public key and the document can check the signature but could never have created it, which is exactly the asymmetry that makes the signature meaningful.

## Worked Example: Tampering Breaks the Signature

The integrity guarantee is not a claim to trust — it is enforced by the math. Change one character of the document and verify the *original* signature against it:

```shell-session
analyst@lab:~$ echo -n "pay Bob 900" > tampered.txt
analyst@lab:~$ openssl pkeyutl -verify -pubin -inkey pk.pem -rawin -in tampered.txt -sigfile doc.sig
Signature Verification Failure
```

`100` became `900`, and verification failed outright. The signature was computed over the exact bytes of the original document, and any change — one character, one bit — makes the verification arithmetic reject it. There is no "close enough": either the signature matches the message and the public key, or it does not. This is why a signed software update cannot be silently modified in transit, and why an attacker who alters a signed message must also forge a new signature, which requires the private key they do not have.

## Hash-then-Sign

Signature schemes do not sign the whole document — they sign its **hash**. The signer computes `SHA-256(message)` and signs that 32-byte digest; the verifier hashes the message themselves and checks the signature against their computed digest. This is done for a practical reason (signing a 32-byte hash is fast regardless of a gigabyte document) and it ties signatures directly to the **Hashing** branch: a signature is only as strong as the hash under it.

That link is why hash collisions are so dangerous. If an attacker can find two messages with the same hash (a collision), a signature over one is *also* a valid signature over the other — the signer signed a benign contract, and the attacker attaches the signature to a malicious one with the same digest. This is precisely how forged certificates were created against MD5, and why signatures must use a collision-resistant hash (SHA-256, not MD5 or SHA-1). The signature scheme and the hash are a unit; weaken either and the whole guarantee falls.

## Where Signatures Live, and Keeping the Key

Signatures are the trust primitive underneath much of security infrastructure:

- **TLS certificates** — a certificate authority signs a statement binding a public key to a domain (**TLS and PKI**).
- **Code signing** — operating systems verify a vendor's signature before running an installer or driver.
- **JWT (`RS256`/`ES256`)** — a signed token whose claims a server trusts because it verifies the signature (**JWT Security**).
- **Signed commits and releases** — Git and package registries prove authorship and integrity.

The schemes in use are **RSA-PSS** (RSA signatures with proper padding — never the textbook form), **ECDSA**, and **Ed25519** (fast, and designed to resist the implementation mistakes that have broken ECDSA). ECDSA carries one infamous trap that ties back to the stream-cipher branch: it requires a unique random nonce per signature, and **reusing that nonce leaks the private key** — the flaw that infamously broke the Sony PlayStation 3's code signing. Ed25519 removes the trap by generating the nonce deterministically.

The security of every signature reduces to the secrecy of the private key. A leaked signing key lets an attacker forge anything the key was trusted to sign — updates, certificates, tokens — which is why signing keys live in hardware security modules and are the most tightly guarded secrets an organisation holds.

## Summary

You should now be able to:

- Explain how signing inverts the public-key roles (private signs, public verifies) and why that delivers authenticity, integrity and non-repudiation.
- Sign a document and verify it with `openssl`, and demonstrate that any tampering makes verification fail.
- Explain hash-then-sign and why a signature is only as strong as its hash, linking collision resistance to signature forgery.
- Name where signatures are used (TLS, code signing, JWT, Git), the standard schemes (RSA-PSS, ECDSA, Ed25519), the ECDSA nonce-reuse trap, and why private-key secrecy is everything.

---
> 🔼 Up: [[Asymmetric Encryption]]
