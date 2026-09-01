---
title: "Hashsmith Tool Architecture"
aliases: ["Hashsmith Engineering"]
tags: [tree/tooling, cyber/tooling/development/hashsmith, type/concept, difficulty/hard]
Domain: "[[Writing Your Own Tools]]"
Color: "#708090"
---

# Hashsmith Tool Architecture

Hashsmith is an open-source terminal utility for encoding/decoding, hashing, format identification, integrity verification, and *authorized* password-strength auditing. It's the architecture principles made concrete: its design carefully separates reversible **encodings** from one-way **hashes**, and makes every resource limit explicit. (A featured tool of this vault.)

> [!warning] Authorized auditing only
> Audit mode requires an explicit authorization acknowledgement, caps workers and runtime, ships no leaked-password lists, and reports *tested policy* — it never claims a hash was "decrypted."

## Parent Learning Order
Security Tool Architecture & Design Patterns -> Building Network Scanners -> Command & Control Design Principles -> Hashsmith Tool Architecture -> ShadowStep Tool Architecture

## The well-built-tool diagram applied to hashing

Hashsmith is the "well-built tool" diagram applied to a hashing/integrity/audit pipeline.

The CLI edge parses explicit subcommands into immutable **operation objects**; a pure core (codecs, digest engines, verifiers) does the work with no printing or `exit()`; new algorithms plug in without touching the engine; and everything emits structured JSON evidence. The one conceptual line the whole design defends: an **encoding is reversible, a hash is not**, and a hash is an *integrity* primitive — conflating "hash" with "encrypt/decrypt" is the error the tool's structure refuses to make.

## Explicit subcommands, machine-readable output

Explicit subcommands (no mode-guessing), machine-readable output:

```shell-session
analyst@lab:~$ hashsmith encode --codec base64 --text 'Crook2Root'
Q3Jvb2syUm9vdA==
analyst@lab:~$ hashsmith hash --algorithm sha256 --file evidence.bin --format json
{"operation":"hash","algorithm":"sha256","path":"evidence.bin","digest":"7fe32b...","status":"ok"}
analyst@lab:~$ hashsmith verify --manifest SHA256SUMS
evidence.bin: OK
analyst@lab:~$ hashsmith audit --input canary-hashes.txt --policy enterprise-v3.toml --authorized --workers 4 --max-runtime 60s
{"tested":12,"policy_failures":2,"recovered_canaries":1,"secrets_logged":false}
```

Core rules: **streaming digests** (a multi-GB file never enters memory), **constant-time** compares for authenticity decisions, mutually-exclusive input sources, diagnostics on stderr (never stdout), and stable exit codes (`0` ok · `1` mismatch · `2` bad invocation).

## Designing a tool that refuses to over-claim

Hash **identification** is where a naive tool over-claims — Hashsmith is designed to refuse to:

```json
// a 32-char hex value — the tool reports candidates + confidence, never certainty
{"value_length":32,"alphabet":"hex",
 "candidates":[{"name":"md5","confidence":"low"},{"name":"ntlm","confidence":"low"}],
 "warning":"format alone is insufficient"}
```

**The deliberate break:** a 32-character hex string *could* be MD5, NTLM, an app identifier, or random bytes — length and alphabet produce **candidates, not certainty** (exactly the name-that-hash/hash-identifier lesson, built into the tool's output contract). A lesser tool prints "MD5" confidently and sends the user down a wrong `hashcat -m`; Hashsmith emits confidence and reasons. This ties straight back to the architecture note: because the core is a set of pure `Operation` objects that *return typed results* (never print or exit), the identifier can express uncertainty as data, the audit engine can be bounded and tested with canary hashes, and adding a new codec or digest is a plugin — not an engine rewrite that risks the constant-time or streaming guarantees. The design *is* the safety: separating reversible from one-way, returning results instead of side effects, and capping every resource is what makes a cryptographic utility trustworthy rather than merely functional.

## Summary

You should now be able to:

- Explain why Hashsmith structurally separates encodings from hashes, and why that matters.
- Name three subcommands and the core rules (streaming, constant-time, exit codes) they follow.
- Explain why the identifier reports confidence not certainty, and how the pure-`Operation` design makes that (and bounded auditing) possible.

---
> 🔼 Up: [[Writing Your Own Tools]]
