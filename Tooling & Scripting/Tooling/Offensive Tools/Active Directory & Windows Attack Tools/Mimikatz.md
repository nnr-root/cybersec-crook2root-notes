---
title: "Mimikatz"
aliases: ["mimikatz", "sekurlsa", "golden ticket", "pass-the-ticket"]
tags: [tree/tooling, cyber/tooling/offensive/ad/mimikatz, type/tool, difficulty/hard]
Domain: "[[Active Directory & Windows Attack Tools]]"
Color: "#708090"
---

# Mimikatz

> [!abstract] Note of [[Active Directory & Windows Attack Tools]]
> Mimikatz reads the credentials Windows keeps in memory so users do not retype them all day, and forges the Kerberos tickets that make compromise permanent. This note covers what LSASS actually holds, why a modern patched host gives hashes rather than plaintext, why a golden ticket survives every password reset in the domain, and the process-access event that catches all of it.

> [!warning] Authorized operations only
> Reading LSASS extracts other users' live credentials, and ticket forgery is domain-wide persistence. Run only against a scoped lab or engagement domain, evidence every action, and treat extracted material as the sensitive credential data it is.

## Parent Learning Order
Impacket -> NetExec -> BloodHound -> Responder -> Mimikatz

## The credentials the OS is holding for you

> *You have SYSTEM on a workstation. The user logged in at 9am and has not typed their password since. Where is it right now?*
>
> Hold your answer — the section below is the response.

Mimikatz is the **credential extraction** engine — the tool that turns local administrative control of a host into the secrets of everyone who has used it.

Its target is **LSASS** (the Local Security Authority Subsystem Service), the process that authenticates users and then *caches* their credential material so that single sign-on works — so a user who authenticated once this morning is not prompted again for every share, mailbox and intranet page. That cache is the whole point of LSASS and the whole exposure: the material sits in the memory of one process, and anything that can read that process's memory can read the material. Reading another process's memory requires **SeDebugPrivilege**, which SYSTEM holds, which is why Mimikatz begins by asserting it.

**Prerequisites:** LSASS and SeDebugPrivilege (from [[Windows Security and Access Control]]), NTLM and Kerberos authentication, and the NT hash versus NetNTLMv2 distinction from [[Responder]] and [[Impacket]].

> [!tip] The analogy, and where it breaks
> A hotel that keeps a copy of every guest's key at the front desk so they never have to check in twice. The analogy breaks on who the desk trusts: a real hotel checks *your* identity before handing over *your* key, whereas LSASS hands its entire drawer to anyone the operating system already calls an administrator — and, until a few years ago, kept a plaintext copy of each key in that drawer "in case a service needed it."

## sekurlsa, and the plaintext that usually is not there

The defining command reads logon sessions straight out of LSASS memory. It must run as SYSTEM, so the session starts by elevating and asserting debug rights:

```powershell
mimikatz # privilege::debug
Privilege '20' OK
mimikatz # token::elevate
mimikatz # sekurlsa::logonpasswords
```

```text
Authentication Id : 0 ; 515784
User Name         : r.okonkwo
Domain            : MERIDIAN
        msv :
         [00000003] Primary
         * NTLM     : 2b576acbe6bcfda7294d6bd18041b8fe
         * SHA1     : b4f0c...
        wdigest :
         * Password : (null)
        kerberos :
         * Password : (null)
```

Read the `(null)` fields, because they are the point. `wdigest` and `kerberos` plaintext are empty on a modern, patched host — not because the tool failed, but because Microsoft's **KB2871997** (2014) and the default `UseLogonCredential=0` stopped WDigest caching cleartext on Windows 8.1 / Server 2012 R2 and later. What remains is the **NTLM hash**, and that is not a consolation prize: it is a pass-the-hash credential everywhere `r.okonkwo` is a local admin, and it never expires until she changes her password.

Where plaintext *does* still appear, it is a finding in itself: it means WDigest was re-enabled (a common "compatibility" misconfiguration), the host is old and unpatched, or the caller staged a downgrade. The absence of plaintext is the modern default; its presence is a defensive gap worth reporting on its own.

**The deliberate break:** Mimikatz has a reputation as "the tool that dumps everyone's plaintext password," and an operator who runs `logonpasswords` on a current build expecting cleartext concludes it is broken. It is not — the plaintext was removed from LSASS by design a decade ago. The tool now yields **hashes and Kerberos tickets**, and both are directly usable: the hash via pass-the-hash, the ticket via pass-the-ticket. Chasing plaintext misses that the hash already *is* the credential. The genuinely different obstacle is **Credential Guard**, which moves these secrets behind a virtualization boundary (LSAIso) that `sekurlsa` cannot read at all — so on a Credential-Guard host the answer is not "hashes instead of plaintext" but "nothing", and the operator's next move is capturing new authentications rather than reading old ones.

**How you'd spot it:** the read is the detection, and it is protocol-independent. Opening a handle to `lsass.exe` with memory-read access from any process that is not a known LSASS reader is **Sysmon Event ID 10** (ProcessAccess) with a `GrantedAccess` mask such as `0x1010` or `0x1410`. It fires regardless of how Mimikatz was delivered — on-disk binary, reflective load, or a `comsvcs.dll` minidump — because they all have to read the same memory. **RunAsPPL** (LSA protection) blocks the ordinary read outright; Mimikatz counters with a kernel driver (`!+`), which is itself a loud driver-load event, so the bypass trades one detection for a noisier one.

## Golden tickets: why one dump becomes forever

The most consequential module is not credential reading but ticket forging. Kerberos issues a **TGT** (ticket-granting ticket) that the KDC signs with the secret of the `krbtgt` account, and thereafter trusts any TGT it can validate with that key. Nothing in the protocol re-checks whether the account named in the ticket still exists, is disabled, or is really in the groups the ticket claims — the signature is the trust.

So an attacker who has the `krbtgt` hash (via [[Impacket]] DCSync or `lsadump::dcsync` here) can forge a TGT for anyone, in any group, valid by default for ten years:

```text
mimikatz # kerberos::golden /user:anybody /domain:meridian.test
    /sid:S-1-5-21-1004336348-1177238915-682003330
    /krbtgt:1a59bd44fe5bec39e0a1c7d4f2b83a90 /id:500 /ptt
Golden ticket for 'anybody @ meridian.test' successfully submitted for current session
```

That `/ptt` injected the forged ticket into the current session (**pass-the-ticket**), which now authenticates as a Domain Admin the directory has never heard of. This is why a single successful `krbtgt` extraction is treated as **total, persistent domain compromise**: resetting user passwords does nothing, disabling accounts does nothing, and the only remediation is rotating the `krbtgt` password *twice* (the account keeps its previous key for one generation), which invalidates every ticket in the domain at once.

**How you'd spot it:** a golden ticket skips the `AS-REQ` — the attacker never asked the KDC for a TGT, they built one — so a service ticket request (event **4769**) with no preceding authentication (event **4768**) for that account is the classic signature. Absurd ticket lifetimes and weak or mismatched encryption types are secondary tells, and a mismatch between the account name in a ticket and the domain's actual membership is the ground truth.

## Security Implications

**Local admin on one host is the credentials of everyone who used it.** This is the concrete reason lateral movement is so productive and why credential reuse is catastrophic: an admin who logs into a helpdesk workstation leaves their hash in that host's LSASS, and one dump there is the admin's credential everywhere. It is the mechanism behind the entire "assume the workstation is hostile" posture.

**The defenses are layered and each raises the bar rather than closing the door.** **RunAsPPL** stops the casual read; **Credential Guard** removes the secrets from readable memory entirely; **disabling WDigest** removes the plaintext; **not logging privileged accounts into low-trust hosts** removes the material in the first place. Credential Guard is the strongest and the least universally deployed, and its absence on a domain-admin-reachable host is a high-value finding.

**Detection here is unusually strong because the physics are fixed.** Whatever the delivery, the credential read must open a handle to LSASS and the ticket forgery must produce Kerberos anomalies the KDC records. Sysmon 10 on LSASS access and 4769-without-4768 on golden tickets are durable against obfuscation in a way signature-matching the Mimikatz binary is not — the binary is trivially renamed and reflectively loaded, the LSASS handle is not avoidable.

**Ticket forgery is a persistence problem, not an access problem, and must be scoped as one.** Finding a golden-ticket capability in an assessment means the finding is "the domain's trust root is exposed," and the remediation (double `krbtgt` rotation) is disruptive enough that it belongs in the report as an incident-response action rather than a routine fix.

All use here requires an authorized, scoped domain. Extracted hashes and tickets are live credentials for real identities, and a forged ticket persists in the environment until the trust key is rotated — clean-up is part of the engagement, not an afterthought.

## Summary

You should now be able to:

- Explain what LSASS caches and why, why reading it needs SeDebugPrivilege, and why `sekurlsa::logonpasswords` yields NTLM hashes and Kerberos tickets rather than plaintext on a modern host.
- Explain why the hash and the ticket are usable credentials without any plaintext, and how Credential Guard changes the outcome from "hashes" to "nothing".
- Explain a golden ticket as a TGT forged with the `krbtgt` hash, why it makes compromise permanent until a double rotation, and why LSASS-handle (Sysmon 10) and 4769-without-4768 are the detections that survive obfuscation.

---
> 🔼 Up: [[Active Directory & Windows Attack Tools]]
