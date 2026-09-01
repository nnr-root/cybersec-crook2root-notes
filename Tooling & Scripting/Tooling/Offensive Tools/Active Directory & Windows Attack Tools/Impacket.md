---
title: "Impacket"
aliases: ["impacket", "secretsdump", "wmiexec"]
tags: [tree/tooling, cyber/tooling/offensive/ad/impacket, type/tool, difficulty/hard]
Domain: "[[Active Directory & Windows Attack Tools]]"
Color: "#708090"
---

# Impacket

Impacket is a Python library of low-level implementations of network protocols (SMB, MSRPC, Kerberos, LDAP, TDS) plus a bundle of example scripts that turn those classes into weapons. It matters because it speaks the protocols **directly**, without a Windows host — a Linux attack box can authenticate, execute commands, and dump secrets as if it were a domain member.

> [!warning] Authorized operations only
> Secret-dumping and remote execution are high-impact. Use against a scoped lab/engagement domain, keep bounded, and evidence everything.

## Parent Learning Order
Impacket -> NetExec -> BloodHound -> Responder

## The execution engine of the AD attack chain

Impacket is the **execution** engine of the AD attack chain — the toolkit that actually performs each technique once you know which one you need.

(The diagram shows the operational flow; the learning order above is different.) Impacket's insight: Windows AD attacks are just *network protocols*, and if you re-implement those protocols you don't need a Windows box, an agent, or malware — a Python script on Kali authenticates and acts as a first-class domain participant. Each example script is one technique: `GetUserSPNs.py` (Kerberoast), `secretsdump.py` (dump hashes / DCSync), `psexec.py`/`wmiexec.py` (remote execution), `ticketer.py` (forge tickets).

## One credential syntax across every script

The scripts share a credential syntax: `domain/user:password@target`. Kerberoast, then remote execution:

```shell-session
operator@kali:~$ GetUserSPNs.py corp.local/jdoe:Summer2024 -request
ServicePrincipalName  Name        Hash
MSSQLSvc/db01         svc_sql     $krb5tgs$23$*svc_sql*...   ← crack with hashcat -m 13100
operator@kali:~$ wmiexec.py corp.local/svc_sql:CrackedPass@10.10.20.30
[*] SMBv3.0 dialect used
C:\> whoami
corp\svc_sql
```

`secretsdump.py` pulls local SAM hashes, cached creds, and — against a DC with the right rights — performs a **DCSync** to extract every domain hash. Because it's a library, you can also script custom flows against SMB/LDAP/Kerberos directly.

## Pass-the-hash, and what it reveals about NTLM

The most important Impacket concept is **pass-the-hash** — and it reveals how NTLM authentication actually works:

```shell-session
# You have the NT hash but NEVER cracked the password
operator@kali:~$ secretsdump.py -hashes :aad3b...:31d6cfe0d16ae931b73c59d7e0c089c0 corp.local/admin@10.10.20.10
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
corp.local\krbtgt:502:aad3b...:1a59b...
```

**The deliberate break:** that command authenticated as `admin` and DCSync'd the domain **without a password** — just the NT hash, passed with `-hashes :NTHASH`. It works because NTLM authentication never uses the plaintext password; it uses the *hash* directly as the secret. So a hash dumped from one machine is a login credential everywhere that account is a local admin — you don't need to crack anything. This is why an NTLM hash must be treated as equivalent to a cleartext password, and why credential reuse (the same local-admin hash on every workstation) turns one compromised box into the whole fleet. The contrast to know (see **Responder**): a *NetNTLMv2* challenge-response hash is **not** pass-the-hash-able — only the stored **NT hash** is. Confusing the two is the classic AD-beginner error.

## Summary

You should now be able to:

- Why can a Linux box run AD attacks with no Windows host and no malware?
- You Kerberoast a service account and crack it. Which Impacket script gives you a shell on a target, and what's the credential syntax?
- Explain pass-the-hash with `-hashes`, why it needs no password, and why an NT hash ≠ a NetNTLMv2 hash.

---
> 🔼 Up: [[Active Directory & Windows Attack Tools]]
