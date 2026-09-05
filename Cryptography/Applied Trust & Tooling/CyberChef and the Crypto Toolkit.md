---
title: "CyberChef & the Crypto Toolkit"
aliases: ["CyberChef", "Crypto Toolkit", "Crypto Multi-Tool", "Hashsmith CLI"]
tags:
  - tree/crypto
  - cyber/crypto/applied
  - cyber/tooling
  - type/tool
  - difficulty/medium
Domain:
  - "[[Applied Trust & Tooling]]"
Color: "#FFE119"
verified: 2026-09-05
---

# 🧰 CyberChef & the Crypto Toolkit

> [!abstract] Note of [[Applied Trust & Tooling]]
> This branch has used a scatter of commands — `base64`, `xxd`, `openssl`, hash identifiers, crackers. This note is the practical toolkit that ties them together for the four operations you repeat constantly: **encode, decode, hash, and crack**. It covers CyberChef, the visual "recipe" tool for chained transformations, and the command-line equivalents, and works a layered-decoding challenge end to end with real tools.

## Parent Learning Order
TLS and PKI -> JWT Security -> CyberChef and the Crypto Toolkit

## Two Tools for the Same Jobs

> *You are handed a blob and have no idea how many layers of encoding are wrapped around it. Which tool finds out fastest, and why is it not a script?*
>
> Hold your answer — the section below is the response.

Applied crypto work is mostly transforming data between representations, hashing it, and identifying or cracking hashes. Two kinds of tool cover this, and knowing when to reach for each is the skill:

- **CyberChef** — an open-source, browser-based "Cyber Swiss Army Knife" (originally from GCHQ). You build a **recipe**: a chain of operations (From Base64 → From Hex → Gunzip → …) that runs left to right on the input, with the output of each feeding the next. It is ideal for *exploration* — you can see each intermediate result, drag operations around, and its "Magic" operation guesses what encoding a blob is. It runs entirely in the browser (or offline as a downloaded page), so pasted data never leaves your machine.
- **The command line** — `base64`, `xxd`, `openssl`, `hash-identifier`/`name-that-hash`, and `hashcat`/`john`. Ideal for *automation and scale*: scripting a decode over a thousand files, or handing a hash to a GPU cracker. Everything CyberChef does visually, these do in a pipe.

The rule of thumb: reach for CyberChef when you do not yet know what you are looking at and want to experiment; reach for the CLI when you know the steps and want to repeat or scale them.

## Worked Example: Peeling a Layered Blob

The everyday applied-crypto task is a blob wrapped in several encodings — common in CTFs, and in malware that stacks encodings to slow analysis. You peel one identifiable layer at a time. Here is a blob that is Base64 wrapping hex:

```shell-session
analyst@lab:~$ echo "the challenge blob: $BLOB"
the challenge blob: NDM3MjZmNmY2YjMyNTI2ZjZmNzQ3Yjc3NjU2YzZjNWY2NDZmNmU2NTdk
analyst@lab:~$ echo "$BLOB" | base64 -d
43726f6f6b32526f6f747b77656c6c5f646f6e657d
analyst@lab:~$ echo "$BLOB" | base64 -d | xxd -r -p
Crook2Root{well_done}
```

Read the method, because it is the whole skill. The blob is mixed-case with `=`-free length — a Base64 tell (the **Base64** note), so decode it. That yields a string of only `0-9a-f` — a hex tell (the **Hexadecimal & Binary** note), so reverse it with `xxd -r -p`. That yields the flag. Each step was chosen by *recognising the alphabet* of the current layer, exactly the recognition skills the encoding branch built. In CyberChef the same solve is the recipe "From Base64 → From Hex", or a single click of "Magic," which detects the chain automatically — the visual counterpart to the pipe above.

## Worked Example: Identify Before You Crack

You cannot crack a hash until you know what it is, and hash type is inferred from its shape — length and character set. The **hash-identifier** and **name-that-hash** tools automate this; the logic is simple enough to see directly:

```shell-session
analyst@lab:~$ python3 identify.py
  5f4dcc3b5aa765d61d8327de...  -> MD5 or NTLM (32 hex)
  5e884898da28047151d0e56f...  -> SHA-256 (64 hex)
  $2b$12$abcdefghijklmnopq...   -> bcrypt
```

Thirty-two hex characters is MD5 or NTLM; sixty-four is SHA-256; a `$2b$` prefix is bcrypt (and self-describes its cost). That identification decides everything downstream — the **Password Cracking** note showed that an MD5 falls in milliseconds while a bcrypt hash costs a second per guess, so knowing which you hold tells you whether a crack is worth attempting and which tool to point at it. The workflow is always **identify → choose strategy → crack**, and skipping the first step wastes the other two.

## openssl: The One Tool That Does Most of It

Where CyberChef is the visual multi-tool, `openssl` is the command-line one — it hashes, encodes, encrypts, and manages keys and certificates from a single binary present on essentially every system:

```shell-session
analyst@lab:~$ echo -n "password" | openssl dgst -sha256
SHA2-256(stdin)= 5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8
analyst@lab:~$ echo -n "hello" | openssl base64
aGVsbG8=
```

The same `openssl` produced the AES ciphertext in **AES & Block Ciphers**, the Ed25519 signatures in **Digital Signatures**, and the certificate authority in **TLS & PKI**. It is worth investing in `openssl` fluency precisely because it recurs across every branch — one tool for hashing, symmetric and asymmetric encryption, signatures and PKI.

**The deliberate break:** the choice between a GUI and the command line reads as taste — some people like clicking, some like typing, and either will get there in the end.

The decision is made by the problem, not the person, and the two failure modes are exact mirrors of each other. When the transformation is **unknown**, the command line makes you guess blind: every attempt is a fresh command and you never see the intermediate states that would tell you what the next layer is. When the transformation is **known**, a GUI makes you repeat manual steps that should have been a script, unreproducibly, usually by pasting the data into a browser. Exploration wants visible intermediates; procedure wants repeatability, and neither tool provides both.

**How you'd spot it:** count your repetitions. Retyping the same `openssl` or `base64` command more than twice with small variations means you are exploring and should be somewhere that shows you each step. Pasting the same recipe into a browser more than twice means you are running a known procedure that should be a script — and, more pressingly, that you have pasted the same data into a web page three times, which is the question worth asking before the tooling one.

## Choosing the Right Tool

The toolkit, mapped to the job and to where each is covered in depth:

| Job | Reach for | Depth note |
|:--|:--|:--|
| Explore an unknown blob visually | **CyberChef** ("Magic") | Tooling → **CyberChef** |
| Encode / decode in a script | `base64`, `xxd` | **Base64**, **Hexadecimal & Binary** |
| Hash, encrypt, sign, certs | `openssl` | this branch throughout |
| Identify an unknown hash | `hash-identifier`, `name-that-hash` | Tooling → **hash-identifier** |
| Crack at scale on a GPU | `hashcat`, `john` | **Password Cracking**, Tooling → **Hashcat** |

The two failure modes to avoid are the mirror of each other: grinding away on the command line when a blob needs the exploratory, see-every-step view CyberChef gives; or clicking through a GUI when the task is a thousand files that a one-line pipe would handle. Match the tool to whether you are *investigating* or *repeating*, and the applied work in this domain becomes fast.

> [!warning] Authorized use
> The cracking tools here are for hashes you are authorized to test — your own, a lab's, or an in-scope engagement's. Data pasted into the public CyberChef site leaves your machine; use the offline download for anything sensitive.

## Summary

You should now be able to:

- Choose between CyberChef (visual, exploratory, chained recipes) and the CLI toolkit (scriptable, scalable) for a given task.
- Peel a layered encoding by recognising each layer's alphabet and applying the matching decode, with `base64`/`xxd` or a CyberChef recipe.
- Identify an unknown hash by its length and character set, and explain why identification must precede cracking.
- Use `openssl` as the command-line crypto multi-tool across hashing, encryption, signatures and certificates, and pick the right tool for investigating versus repeating.

---
> 🔼 Up: [[Applied Trust & Tooling]]
