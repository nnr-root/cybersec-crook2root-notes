---
title: "Impacket"
aliases: ["impacket", "secretsdump", "wmiexec"]
tags: [tree/tooling, cyber/tooling/offensive/ad/impacket, type/tool, difficulty/hard]
Domain: "[[Active Directory & Windows Attack Tools]]"
Color: "#708090"
---

# Impacket

> [!abstract] Note of [[Active Directory & Windows Attack Tools]]
> Impacket is the execution engine of the AD attack chain: a Linux box speaking the protocols directly, with no Windows host and no agent. This note covers why pass-the-hash works at all, why the three remote-execution scripts leave three completely different footprints, and what DCSync looks like from the wire the moment a workstation asks to replicate the directory.

Impacket is a Python library of low-level implementations of network protocols (SMB, MSRPC, Kerberos, LDAP, TDS) plus a bundle of example scripts that turn those classes into weapons. It matters because it speaks the protocols **directly**, without a Windows host — a Linux attack box can authenticate, execute commands, and dump secrets as if it were a domain member.

> [!warning] Authorized operations only
> Secret-dumping and remote execution are high-impact. Use against a scoped lab/engagement domain, keep bounded, and evidence everything.

## Parent Learning Order
Impacket -> NetExec -> BloodHound -> Responder -> Mimikatz

## The execution engine of the AD attack chain

> *BloodHound told you which technique to run next. What actually runs it?*
>
> Hold your answer — the section below is the response.

Impacket is the **execution** engine of the AD attack chain — the toolkit that actually performs each technique once you know which one you need.

(The diagram shows the operational flow; the learning order above is different.) Impacket's insight: Windows AD attacks are just *network protocols*, and if you re-implement those protocols you don't need a Windows box, an agent, or malware — a Python script on Kali authenticates and acts as a first-class domain participant. Each example script is one technique: `GetUserSPNs.py` (Kerberoast), `secretsdump.py` (dump hashes / DCSync), `psexec.py`/`wmiexec.py` (remote execution), `ticketer.py` (forge tickets).

**Prerequisites:** NTLM and Kerberos authentication, SMB, and what a domain hash is.

> [!tip] The analogy, and where it breaks
> A skeleton key cut from a photograph of the original — you never held the key, only its image, and the copy opens the door anyway. The analogy breaks on which image works: a photograph of the *stored* key (the NT hash) cuts a working copy, while a photograph of someone *using* the key at a specific door (a NetNTLMv2 challenge-response) cannot, because that image is bound to that one door and that one moment. Confusing the two is the classic beginner error, and the next section is about exactly which image you are holding.

## One credential syntax across every script

The scripts share a credential syntax: `domain/user:password@target`. Kerberoast, then remote execution:

```shell-session
operator@kali:~$ GetUserSPNs.py meridian.test/r.okonkwo:'Summer2024!' -request
ServicePrincipalName  Name         Hash
MSSQLSvc/app01        svc_backup   $krb5tgs$23$*svc_backup*...   ← crack with hashcat -m 13100
operator@kali:~$ wmiexec.py meridian.test/svc_backup:'CrackedPass!'@10.10.20.30
[*] SMBv3.0 dialect used
C:\> whoami
meridian\svc_backup
```

`secretsdump.py` pulls local SAM hashes, cached creds, and — against a DC with the right rights — performs a **DCSync** to extract every domain hash. Because it's a library, you can also script custom flows against SMB/LDAP/Kerberos directly.

### The three shells are not interchangeable

`psexec.py`, `smbexec.py` and `wmiexec.py` all give a command prompt on the target, and they arrive by three different mechanisms that leave three different traces. Choosing between them is an OpSec decision, not a preference:

| Script | Mechanism | Disk artifact | Service created | Typical Windows event |
|:--|:--|:--|:--|:--|
| `psexec.py` | uploads a service binary to `ADMIN$`, registers and starts a service | a `.exe` in `C:\Windows` | yes, one per run | 7045 (service install), 4697 |
| `smbexec.py` | creates a service that runs one `cmd` per command, output to a file | a temp file per command | yes, recreated per command | 7045, repeatedly |
| `wmiexec.py` | runs each command via WMI `Win32_Process.Create`, output to `ADMIN$` | none of its own | no | 4688 with a WMI parent |

Read the table by what a defender sees. `psexec.py` is the loudest — a service install (**7045**) is a high-fidelity, low-volume event that mature environments alert on directly, and it drops a binary to disk for an EDR to catch. `wmiexec.py` creates no service and writes no binary of its own, so it is the quietest of the three, but every command it runs is a process whose parent is `WmiPrvSE.exe`, and a `cmd.exe` or `whoami.exe` under that parent on a workstation is itself a signature. There is no traceless option here; there is a choice of which trace you would rather leave.

The `-hashes` flag works on all three, which connects this to the next section: none of them needs a password.

## Pass-the-hash, and what it reveals about NTLM

The most important Impacket concept is **pass-the-hash** — and it reveals how NTLM authentication actually works:

```shell-session
# You have the NT hash but NEVER cracked the password
operator@kali:~$ secretsdump.py -hashes :aad3b...:31d6cfe0d16ae931b73c59d7e0c089c0 corp.local/admin@10.10.20.10
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
corp.local\krbtgt:502:aad3b...:1a59b...
```

**The deliberate break:** that command authenticated as `admin` and DCSync'd the domain **without a password** — just the NT hash, passed with `-hashes :NTHASH`. It works because NTLM authentication never uses the plaintext password; it uses the *hash* directly as the secret. So a hash dumped from one machine is a login credential everywhere that account is a local admin — you don't need to crack anything. This is why an NTLM hash must be treated as equivalent to a cleartext password, and why credential reuse (the same local-admin hash on every workstation) turns one compromised box into the whole fleet. The contrast to know (see **Responder**): a *NetNTLMv2* challenge-response hash is **not** pass-the-hash-able — only the stored **NT hash** is. Confusing the two is the classic AD-beginner error.

**How you'd spot it:** in an environment, look for the same local administrator hash appearing on more than one host; that reuse is what turns one compromise into all of them. Defensively the authentication is indistinguishable from a legitimate one at the protocol level, so the tell is behavioural — an account authenticating to hosts it has never touched, or `DRSUAPI` replication requested by something that is not a domain controller.

## DCSync, from the wire

DCSync is the technique worth seeing in detail, because it is pure protocol abuse — no code runs on the DC at all. `secretsdump.py` asks the domain controller to *replicate* account secrets to it, using the same `DRSUAPI` `DRSGetNCChanges` call a real DC uses to sync with its partners. The DC checks whether the caller holds the replication rights (`DS-Replication-Get-Changes` and `-All`) and, if so, hands over the hashes:

```shell-session
operator@kali:~$ secretsdump.py -just-dc-ntlm \
    -hashes :cc36cf7a8514893efccd332446158b1a meridian.test/admin_bob@10.10.20.10
[*] Dumping Domain Credentials (domain\uid:rid:lmhash:nthash)
[*] Using the DRSUAPI method to get NTDS.DIT secrets
meridian.test\krbtgt:502:aad3b435b51404eeaad3b435b51404ee:1a59bd44fe5bec39...
meridian.test\r.okonkwo:1104:aad3b435...:2b576acbe6bcfda7...
meridian.test\svc_backup:1108:aad3b435...:5835048ce94ad0564e29a924a03510ef...
```

Two things make this the crown-jewel technique. It reads **every** secret including `krbtgt`, whose hash is the key to forging golden tickets — so one successful DCSync is effectively permanent domain compromise. And it requires no foothold on the DC and touches no file on it; the replication is a legitimate operation the caller was, on paper, authorised to perform.

That is also exactly why it is detectable without any endpoint agent. `DRSGetNCChanges` should only ever originate from a domain controller's own IP. The detection is a network fact rather than a log-parsing exercise: replication traffic from any address that is not a DC is DCSync, and there is no benign version of it. Restricting the replication rights to the DCs' own accounts, and alerting on `4662` operations referencing the replication GUIDs from non-DC sources, is the standard control.

## Summary

You should now be able to:

- Explain how a Linux host runs AD attacks with no Windows host and no malware, and give the shared credential syntax.
- Choose between `psexec.py`, `smbexec.py` and `wmiexec.py` by the footprint each leaves — service install, disk artifact, WMI parent — rather than by habit.
- Explain pass-the-hash with `-hashes`, why it needs no password, and why an NT hash ≠ a NetNTLMv2 hash; describe DCSync as `DRSUAPI` replication abuse, why reading `krbtgt` makes it permanent, and why replication traffic from a non-DC address is the detection.

---
> 🔼 Up: [[Active Directory & Windows Attack Tools]]
