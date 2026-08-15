---
title: "Responder"
aliases: ["responder"]
tags: [tree/tooling, cyber/tooling/offensive/ad/responder, type/tool, level/operator]
Domain: "[[Active Directory & Windows Attack Tools]]"
Color: "#708090"
---

# Responder

Responder is a link-local poisoner. When a Windows host fails DNS and falls back to **LLMNR**, **NBT-NS**, or **mDNS** broadcasts to find a name, Responder answers "that's me" and harvests the victim's **NetNTLM** authentication — no exploit, just abuse of a chatty, trusting name-resolution fallback. It is the classic first move on an internal network with zero credentials.

> [!warning] Authorized operations only
> Poisoning intercepts real user authentication on the segment. Run only on an authorized internal engagement, and never enable the relay servers unless relaying is explicitly in scope.

## Parent Learning Order
Impacket -> NetExec -> BloodHound -> Responder

## Crook — The Mental Model

Responder is the **capture credentials** stage — how you get your first hash with no credentials at all.

![[tool_ad_attack_chain.svg]]

The mechanism is pure trust abuse. When a user mistypes a share (`\\fileserv1`) or a host looks up a name DNS can't resolve, Windows *shouts to the whole subnet*: "who is `fileserv1`?" via LLMNR/NBT-NS broadcast. Nobody authenticates that answer — so Responder shouts back "me!", the victim connects and **authenticates**, and you capture its NetNTLMv2 challenge-response. One poisoned typo yields a crackable credential.

## Operator — Make It Work

Point it at the interface and listen; captured hashes are ready for offline cracking:

```shell-session
operator@kali:~$ sudo responder -I eth0 -w -d
[+] Listening for events...
[SMB] NTLMv2-SSP Client   : 10.0.0.44
[SMB] NTLMv2-SSP Username : CORP\jsmith
[SMB] NTLMv2-SSP Hash     : jsmith::CORP:1122...:A1B2...
operator@kali:~$ hashcat -m 5600 jsmith.hash rockyou.txt
JSMITH::CORP:...:Summer2024
```

`-m 5600` is the Hashcat mode for NetNTLMv2. Responder's logs and its `Responder-Sessions.log`/database are the evidence record. Its **Analyze mode** (`-A`) *watches* poisonable traffic without answering — a safe way to prove the exposure exists before you actively poison.

## Root — Internals & The Deliberate Break

The single most important AD-beginner distinction lives right here:

```shell-session
# You captured this from Responder:
jsmith::CORP:1122334455667788:A1B2C3...   ← NetNTLMv2 (a challenge-response)
operator@kali:~$ impacket-secretsdump -hashes :A1B2C3... corp/jsmith@10.0.0.30
[-] [Errno Connection error] authentication failed
```

**The deliberate break:** you *cannot* pass-the-hash a Responder capture. A **NetNTLMv2** hash is a one-time challenge-response — the client hashed a server-supplied *challenge* with its NT hash, so the value is useless for direct authentication (it's not the stored secret, and it's bound to that specific challenge). Your only two moves are: **crack it** offline to recover the plaintext (Hashcat `-m 5600`), or **relay it** live to another host with `ntlmrelayx` before the challenge expires. Contrast with **Impacket** pass-the-hash, which needs the *NT hash* — the stored secret you dump from SAM/NTDS. Beginners capture a NetNTLMv2 with Responder, try to pass it, fail, and conclude the tool is broken. It isn't: NetNTLMv2 = crack or relay; NT hash = pass. And the defense writes itself: **disable LLMNR/NBT-NS** (there's nothing to poison), enforce SMB signing (relay fails), and use strong passwords (cracking fails).

## Crook → Operator → Root Checkpoint

- **Crook:** What trust flaw in LLMNR/NBT-NS lets Responder capture a hash with no credentials?
- **Operator:** How do you capture a NetNTLMv2 hash and crack it, and what does Analyze mode do?
- **Root:** Explain why a Responder-captured NetNTLMv2 hash can't be passed, and the two things you can do with it instead.

---
> 🔼 Up: [[Active Directory & Windows Attack Tools]]
