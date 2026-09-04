---
title: "Responder"
aliases: ["responder"]
tags: [tree/tooling, cyber/tooling/offensive/ad/responder, type/tool, difficulty/medium]
Domain: "[[Active Directory & Windows Attack Tools]]"
Color: "#708090"
---

# Responder

> [!abstract] Note of [[Active Directory & Windows Attack Tools]]
> Responder gets a crackable credential on an internal network with no starting access, by answering name-resolution broadcasts nobody authenticates. This note covers the trust flaw it abuses, why the captured hash cannot be passed, and why the tool cannot operate without leaving the segment able to see it.

Responder is a link-local poisoner. When a Windows host fails DNS and falls back to **LLMNR**, **NBT-NS**, or **mDNS** broadcasts to find a name, Responder answers "that's me" and harvests the victim's **NetNTLM** authentication — no exploit, just abuse of a chatty, trusting name-resolution fallback. It is the classic first move on an internal network with zero credentials.

> [!warning] Authorized operations only
> Poisoning intercepts real user authentication on the segment. Run only on an authorized internal engagement, and never enable the relay servers unless relaying is explicitly in scope.

## Parent Learning Order
Impacket -> NetExec -> BloodHound -> Responder

## Getting a hash with no credentials at all

> *A user mistypes a share name. How does that hand you a hash?*
>
> Hold your answer — the section below is the response.

Responder is the **capture credentials** stage — how you get your first hash with no credentials at all.

The mechanism is pure trust abuse. When a user mistypes a share (`\\fileserv1`) or a host looks up a name DNS can't resolve, Windows *shouts to the whole subnet*: "who is `fileserv1`?" via LLMNR/NBT-NS broadcast. Nobody authenticates that answer — so Responder shouts back "me!", the victim connects and **authenticates**, and you capture its NetNTLMv2 challenge-response. One poisoned typo yields a crackable credential.

## Listening, then cracking offline

Point it at the interface and listen; captured hashes are ready for offline cracking:

```shell-session
operator@kali:~$ sudo responder -I eth0 -w -d
[+] Listening for events...
[SMB] NTLMv2-SSP Client   : 10.10.10.14
[SMB] NTLMv2-SSP Username : MERIDIAN\r.okonkwo
[SMB] NTLMv2-SSP Hash     : r.okonkwo::MERIDIAN:1122...:A1B2...
operator@kali:~$ hashcat -m 5600 okonkwo.hash rockyou.txt
R.OKONKWO::MERIDIAN:...:Summer2024!
```

**Prerequisites:** LLMNR/NBT-NS and why they fall back to broadcast, NetNTLMv2 versus the NT hash, and SMB signing.

`-m 5600` is the Hashcat mode for NetNTLMv2. Responder's logs and its `Responder-Sessions.log`/database are the evidence record. Its **Analyze mode** (`-A`) *watches* poisonable traffic without answering — a safe way to prove the exposure exists before you actively poison.

## Why a Responder capture cannot be passed

The single most important AD-beginner distinction lives right here:

```shell-session
# You captured this from Responder:
r.okonkwo::MERIDIAN:1122334455667788:A1B2C3...   ← NetNTLMv2 (a challenge-response)
operator@kali:~$ impacket-secretsdump -hashes :A1B2C3... meridian.test/r.okonkwo@10.10.20.30
[-] [Errno Connection error] authentication failed
```

**The deliberate break:** you *cannot* pass-the-hash a Responder capture. A **NetNTLMv2** hash is a one-time challenge-response — the client hashed a server-supplied *challenge* with its NT hash, so the value is useless for direct authentication (it's not the stored secret, and it's bound to that specific challenge). Your only two moves are: **crack it** offline to recover the plaintext (Hashcat `-m 5600`), or **relay it** live to another host with `ntlmrelayx` before the challenge expires. Contrast with **Impacket** pass-the-hash, which needs the *NT hash* — the stored secret you dump from SAM/NTDS. Beginners capture a NetNTLMv2 with Responder, try to pass it, fail, and conclude the tool is broken. It isn't: NetNTLMv2 = crack or relay; NT hash = pass. And the defense writes itself: **disable LLMNR/NBT-NS** (there's nothing to poison), enforce SMB signing (relay fails), and use strong passwords (cracking fails).

**How you'd spot it:** read the shape of what you captured. A NetNTLMv2 value is long and colon-separated, carrying the account, the domain and the challenge; an NT hash is a bare 32 hex characters. If your value has colons and a username in it, `-hashes` will not accept it, and the only two moves left are Hashcat `-m 5600` or `ntlmrelayx`.

## Security Implications

**The tool must transmit to work, so the segment can always see it.** Responder wins the race by *answering* poisonable broadcasts, which means it puts frames on the wire — a defender running Responder's own **Analyze mode** (`-A`), or any monitor watching for LLMNR/NBT-NS *responses* from a host that is not a name server, sees the poisoner directly. It cannot lurk silently; answering is the whole mechanism.

**The failed lookup is the root cause, and it is the durable fix.** Every capture begins with a name DNS could not resolve. Disabling LLMNR and NBT-NS by group policy removes the broadcast there is nothing to answer, which defeats the attack at its source rather than watching for it — the same conclusion the Local Name Resolution note reaches from the networking side.

**SMB signing decides whether capture becomes compromise.** A captured NetNTLMv2 can be *relayed* live with `ntlmrelayx` to any host that does not require SMB signing, turning an intercepted authentication into a session on a second machine without cracking anything. Enforcing SMB signing makes the relay fail, which is why it is the control that matters as much as disabling the broadcasts.

**A weak password is what makes the capture pay off.** The captured value is only useful if it cracks or relays; a long random password resists the offline `-m 5600` crack the way any strong secret resists Hashcat, leaving relay as the attacker's only path and SMB signing as its answer.

All poisoning here intercepts real users' authentication and belongs only on an authorized internal engagement; the relay servers stay off unless relaying is explicitly in scope.

## Summary

You should now be able to:

- Identify the trust flaw in LLMNR and NBT-NS that lets Responder capture a hash with no credentials, and explain what Analyze mode does.
- Capture a NetNTLMv2 hash and crack it, and explain why a Responder capture can't be passed — only cracked or relayed.
- Explain why disabling LLMNR/NBT-NS, enforcing SMB signing, and strong passwords each defeat a different stage, and why the poisoner cannot operate without the segment being able to detect it.

---
> 🔼 Up: [[Active Directory & Windows Attack Tools]]
