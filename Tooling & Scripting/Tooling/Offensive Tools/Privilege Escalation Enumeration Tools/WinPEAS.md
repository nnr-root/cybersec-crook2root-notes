---
title: "WinPEAS"
aliases: ["winpeas", "winPEAS"]
tags: [tree/tooling, cyber/tooling/offensive/privesc/winpeas, type/tool, difficulty/hard]
Domain: "[[Privilege Escalation Enumeration Tools]]"
Color: "#708090"
---

# WinPEAS

WinPEAS is the Windows counterpart of LinPEAS — the PEASS-ng script that sweeps a Windows host for local privilege-escalation vectors and colour-ranks them. Windows privesc is a different landscape from Linux: instead of SUID bits and sudo, the paths run through **service misconfigurations**, **token privileges**, the **registry**, and **stored credentials**. WinPEAS knows where they all hide.

> [!warning] Authorized post-exploitation only
> Run only on in-scope hosts. WinPEAS touches services, registry, and credential stores extensively and is highly visible to EDR.

## Parent Learning Order
LinPEAS -> WinPEAS

## The vector families that lead to SYSTEM

Escalating on Windows means finding a **service, task, or privilege that will execute your code as SYSTEM** — or a credential that unlocks a higher account. The vector families are distinct from Linux, but the principle is identical: one misconfiguration that trusts a low-priv user too much.

The **right** column of the diagram is WinPEAS's checklist. The two that pay off most often: **`SeImpersonatePrivilege`** on a service account (the "Potato" family escalates it to SYSTEM), and **unquoted service paths** (Windows may execute an attacker-planted `C:\Program.exe`). WinPEAS finds them; you recognise which to pursue.

## The .exe and the .bat fallback

WinPEAS ships as a native `.exe` (fast, full checks) and a `.bat` (fallback where the exe is blocked). Run and capture:

```console
PS C:\Users\low\Downloads> .\winPEASx64.exe log=winpeas.txt
╔══════════╣ Current Token privileges
   SeImpersonatePrivilege        Enabled     ← Potato-family to SYSTEM
╔══════════╣ Checking Service Unquoted Paths
   'Vuln Service' => C:\Program Files\Vuln App\svc.exe  (writable dir, unquoted)
╔══════════╣ AlwaysInstallElevated
   HKLM & HKCU = 1   ← any .msi installs as SYSTEM
╔══════════╣ Looking for saved credentials (cmdkey)
   Target: Domain:interactive=CORP\admin  (stored)
```

Four independent SYSTEM paths in one sweep. Each maps to a concrete exploit — `SeImpersonate` → PrintSpoofer/GodPotato; `AlwaysInstallElevated` → a malicious `.msi` via `msfvenom`:

```console
PS C:\> .\PrintSpoofer64.exe -i -c cmd
[+] Found privilege: SeImpersonatePrivilege
[+] Impersonated user: NT AUTHORITY\SYSTEM
C:\Windows\system32> whoami
nt authority\system
```

## Why the colour ranking is triage, not a verdict

As with LinPEAS, the colour ranking is a triage aid, not a verdict:

```console
PS C:\> .\winPEASx64.exe quiet servicesinfo | findstr /i "unquoted writable"
   [!] 'Vuln Service' unquoted AND service dir writable  → plant EXE
PS C:\hardened> .\winPEASx64.exe quiet servicesinfo | find /c "[!]"
0
```

**The deliberate break / contrast:** the vulnerable host flags an unquoted path *whose directory is writable* — the combination that is exploitable; the hardened host shows `0`. The nuance WinPEAS teaches: an unquoted path alone is **not** enough — you also need write access somewhere along the path to plant the binary. A tester who reports every "unquoted service path" without checking the directory ACL produces false positives. WinPEAS surfaces the candidate; you confirm the writable directory before claiming the finding.

Operational internals: prefer the `.exe` (the `.bat` misses many checks); `log=` writes an evidence file; AMSI/EDR frequently flags WinPEAS on write, so operators use obfuscated builds or the `.bat` in constrained environments (in an authorized test, coordinate expected alerts with the blue team rather than evading silently). And remember the Windows privesc reality: many findings (stored creds, DPAPI, GPP passwords) yield *credentials* rather than direct SYSTEM — those feed **NetExec**/**Impacket** for lateral movement, closing the loop with the AD tooling.

## Summary

You should now be able to:

- Explain how Windows privesc vectors — services, tokens, registry — differ from Linux's SUID and sudo.
- Identify the tool family that escalates `SeImpersonatePrivilege`, and the account it escalates to.
- Explain why an "unquoted service path" is only exploitable with a second condition, and what a careless tester gets wrong.

---
> 🔼 Up: [[Privilege Escalation Enumeration Tools]]
