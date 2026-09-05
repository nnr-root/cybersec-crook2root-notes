---
title: "name-that-hash"
aliases: ["name-that-hash", "nth", "name that hash"]
tags: [tree/tooling, cyber/tooling/offensive/cracking/nth, type/tool, difficulty/medium]
Domain: "[[Password Cracking Tools]]"
Color: "#708090"
verified: 2026-09-05
---

# name-that-hash

> [!abstract] Note of [[Password Cracking Tools]]
> name-that-hash inspects a hash's structure and returns a *ranked* list of likely types, each annotated with the exact Hashcat mode and John format to run next. This note covers why it reasons about format rather than matching known hashes, why a bare 32-hex value is genuinely ambiguous, and why the type it reports is a hardening verdict the defender should read before any crack.

name-that-hash (`nth`) answers the very first question of any cracking job: **"what kind of hash is this?"** Before John or Hashcat can attack a value, you must tell them the algorithm — and guessing wrong wastes hours or silently fails. `nth` inspects a hash's structure and returns a ranked list of likely types, each annotated with the exact Hashcat mode and John format to use next.

> [!warning] Identification is safe; cracking is scoped
> Identifying a hash touches nothing. Only crack hashes you captured under authorization or generated yourself.

## Parent Learning Order
name-that-hash -> hash-identifier -> John the Ripper -> Hashcat

## Different algorithms leave different shapes

> *One hash starts `$2b$`; another is 32 hex characters. What have you already learned?*
>
> Hold your answer — the section below is the response.

A hash is a fixed-length fingerprint of some input, but different algorithms leave different **shapes**. An unsalted MD5 is 32 hex characters; SHA-1 is 40; bcrypt starts with `$2b$`; a Windows dump gives you `LM:NTLM` pairs separated by a colon. You do not need to memorise them all — you need to *read the signals*.

## Identifying one hash, with the crack modes attached

Install and identify a single hash with `-t` (text):

```shell-session
operator@lab:~$ pipx install name-that-hash    # or: apt install name-that-hash
operator@lab:~$ nth -t 482c811da5d5b4bc6d497ffa98491e38
  482c811da5d5b4bc6d497ffa98491e38
Most Likely
  MD5, HC: 0  JtR: raw-md5
  NTLM, HC: 1000  JtR: nt
  MD4, HC: 900  JtR: raw-md4
```

`nth` correctly reports the *ambiguity*: 32 hex could be MD5 **or** NTLM — the tool ranks by likelihood and hands you both the Hashcat mode (`HC:`) and John format (`JtR:`). Context resolves it: a hash from a web app's DB is probably MD5; one from a `secretsdump` is NTLM.

Feed a whole file with `-f`, and pipe hashes straight from other tools:

```shell-session
operator@lab:~$ nth -f hashes.txt --no-banner
$2b$12$R9h/...    bcrypt, HC: 3200  JtR: bcrypt
$krb5tgs$23$...   Kerberos 5 TGS-REP etype 23, HC: 13100  JtR: krb5tgs
```

That last line is the payoff: `nth` recognised a Kerberoast ticket and told you to run `hashcat -m 13100` — the exact bridge from **Impacket**'s `GetUserSPNs` to a crack.

## Reasoning about format instead of matching a database

`nth` matches against a library of **regexes and structural rules**, not a database of known hashes — it reasons about format, so it works on values it has never seen. That design has a sharp edge: when a hash has **no prefix and a common length**, structure alone cannot decide.

```shell-session
operator@lab:~$ nth -t 5f4dcc3b5aa765d61d8327deb882cf99
Most Likely
  MD5, HC: 0  JtR: raw-md5
  NTLM, HC: 1000  JtR: nt
```

**The deliberate break:** this is `MD5("password")` — but `nth` *also* offers NTLM, because a 32-hex string is genuinely ambiguous by structure. If you blindly run `hashcat -m 1000` (NTLM) against an MD5, it will churn and **never crack it**, looking like a "strong password" when the real problem is the wrong mode. The lesson: `nth` narrows the field, but the **source** of the hash (web DB vs. AD dump) is the context that makes the final call. Always record where a hash came from.

**How you'd spot it:** a crack that runs a long time at a steady rate and recovers nothing has the shape of a wrong mode, not a strong password. Cross-check by hashing a known value in the candidate algorithm and comparing the format — and record each hash's source at the moment you collect it, because that is the fact that resolves the ambiguity later.

Edge cases worth knowing: salted formats (`$id$salt$hash`) are self-describing and unambiguous; raw hashes are not. Truncated or encoded hashes (base64 vs hex) change the length signal — decode first. And `nth` reports *format*, never *strength*: it will happily identify a bcrypt hash it could never help you crack.

## Security Implications

**The ranked type is a storage verdict, read before any cracking.** When `nth` reports `bcrypt, HC: 3200` the defender has done the right thing and no run is worth starting; when it reports raw MD5 or NTLM, the weakness is already established. Reasoning about format rather than matching a database means it delivers that verdict even on values it has never seen — the security signal is in the shape.

**Ranking is what turns identification into fewer wasted, and fewer noisy, runs.** hash-identifier lists matches flat; `nth` orders them by likelihood and attaches the exact `-m` and JtR format, so the operator starts with the probable mode rather than churning through a wrong one. A wrong mode is not just wasted time — it is a long steady run that recovers nothing and reads as a strong password when the real fault was the mode.

**A recognised Kerberoast or PMKID line is a bridge, and a finding.** `nth` naming a `$krb5tgs$` ticket points straight at `hashcat -m 13100` from [[Impacket]]'s `GetUserSPNs`, and its appearance at all means a service account's ticket was obtainable — a finding independent of whether it cracks. Salted formats are self-describing and unambiguous; the dangerous ambiguity is only ever the raw, unsalted, common-length hash, which is itself the weakness.

## Summary

You should now be able to:

- Name the three visual signals that identify a hash type by eye.
- Decide which mode to run when `nth` returns both MD5 and NTLM for a 32-hex value.
- Explain why a prefixed hash like `$2b$...` is unambiguous but a bare 32-hex string is not, and what goes wrong if you crack with the wrong `-m`.

---
> 🔼 Up: [[Password Cracking Tools]]
