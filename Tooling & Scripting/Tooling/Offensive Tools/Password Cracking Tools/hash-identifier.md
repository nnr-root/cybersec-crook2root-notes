---
title: "hash-identifier"
aliases: ["hash-identifier", "hashid", "hash-id"]
tags: [tree/tooling, cyber/tooling/offensive/cracking/hashid, type/tool, difficulty/easy]
Domain: "[[Password Cracking Tools]]"
Color: "#708090"
---

# hash-identifier

> [!abstract] Note of [[Password Cracking Tools]]
> hash-identifier reads a hash's structural fingerprint — prefix, length, charset — and lists the algorithms it could be, with no sense of which is likeliest. This note covers why that ambiguity is the expected output rather than a fault, why provenance breaks the tie, and why the identified type is itself a hardening verdict before a single crack is attempted.

hash-identifier (and the related `hashid`) is the classic interactive hash-type guesser. You paste a hash, it prints the algorithms whose structure matches. It predates and overlaps **name-that-hash** — knowing both matters because they disagree in useful ways, and disagreement is a signal about how confident you can be in the identification.

> [!warning] Identification is safe; cracking is scoped
> Naming a hash touches nothing. Only crack hashes captured under authorization or generated yourself.

## Parent Learning Order
name-that-hash -> hash-identifier -> John the Ripper -> Hashcat

## Reading the structural fingerprint of a hash

> *A hash is a run of hex characters. What in it could possibly reveal which algorithm produced it?*
>
> Hold your answer — the section below is the response.

Every hash type leaves a structural fingerprint — a prefix, a length, a charset. A hash *identifier* is a lookup that reads those fingerprints and lists the algorithms they could be.

The diagram is what these tools automate. hash-identifier is the older, simpler engine: it matches length and charset against a fixed list. That simplicity is both its speed and its weakness — it will confidently list *many* possibilities for an ambiguous value, and you must reason about which is real from the diagram's three signals.

## Ranking candidate types, and the -m bridge

`hashid` is the fast, scriptable, modern variant; `hash-identifier` is the interactive legacy tool. Both take a hash and rank types:

```shell-session
operator@lab:~$ hashid '482c811da5d5b4bc6d497ffa98491e38'
Analyzing '482c811da5d5b4bc6d497ffa98491e38'
[+] MD2
[+] MD5
[+] MD4
[+] NTLM
operator@lab:~$ hashid -m '$1$28772684$iEwNOgGugqO9.bIz5sk8k/'
[+] MD5 Crypt      [Hashcat Mode: 500]
[+] Cisco-IOS(MD5)
```

The `-m` flag adds the Hashcat mode — the bridge to the cracker. `hash-identifier` is the same idea, interactively:

```shell-session
operator@lab:~$ hash-identifier
 HASH: 5f4dcc3b5aa765d61d8327deb882cf99
Possible Hashs:
[+] MD5
[+] Domain Cached Credentials
```

## A fixed rule table with no sense of likelihood

hash-identifier matches against a **fixed rule table**, and it has no notion of *likelihood* — it lists every structural match with equal weight.

```shell-session
operator@lab:~$ hashid '5f4dcc3b5aa765d61d8327deb882cf99'
[+] MD5
[+] Domain Cached Credentials
[+] NTLM
```

**The deliberate break:** for a bare 32-hex string, hash-identifier lists MD5, DCC, **and** NTLM with no ranking — technically correct, practically unhelpful, because it can't tell you *which*. This is exactly why **name-that-hash** was written: it adds likelihood ordering and cleaner output. The professional workflow uses both — if they *agree*, confidence is high; if hash-identifier lists an option name-that-hash ranks low, the source context (web DB → MD5, AD dump → NTLM) breaks the tie. A tool that "identifies" a hash is really *narrowing a field*, never deciding — running the wrong Hashcat `-m` on a misidentified hash burns hours for nothing.

**How you'd spot it:** ambiguity is the expected output here, not a fault. When it lists MD5, DCC and NTLM for one value, provenance breaks the tie rather than the tool — a web application database points to MD5, a domain controller dump points to NTLM. If you cannot say where the hash came from, that is the thing to go and fix first.

Note `hashid` reads from files/stdin (scriptable) while `hash-identifier` is interactive only — for automation, `hashid` or name-that-hash; for a quick manual check, either.

## Security Implications

**Identification is completely passive — it touches nothing and leaves no trace.** You are reading a string you already hold, so there is no target interaction, no telemetry, and no scope concern in the identification step itself. The scoped, logged activity is everything downstream of it.

**The identified type is a hardening verdict on its own.** A dump that hash-identifier calls raw MD5, SHA-1 or NTLM is a finding before anything is cracked: those are fast, and fast-at-rest is the weakness. A value it calls bcrypt or argon2 is a control working as intended. The type tells you the storage decision the defender made, which is often more reportable than whether any single password falls.

**Misidentification is the real cost, and it is an attacker's own-goal.** Running the wrong Hashcat mode against a misidentified hash churns for hours and cracks nothing, looking exactly like a strong password. The tool narrows a field; it never decides. Provenance — a web app database points to MD5, a domain controller dump to NTLM — is what resolves an ambiguous 32-hex value, which is why recording where each hash came from is a workflow step, not a nicety.

## Summary

You should now be able to:

- Name the structural signals a hash identifier reads to guess a type.
- Explain why the `Hashcat Mode` printed by `hashid -m` is the most useful part of the output.
- Explain why hash-identifier lists MD5/DCC/NTLM together with no ranking, and how you resolve the ambiguity in practice.

---
> 🔼 Up: [[Password Cracking Tools]]
