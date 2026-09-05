---
title: "Offensive Security — Gap Analysis & Phase 4 Roadmap"
tags:
  - tree/meta
  - type/reference
---

# Offensive Security — Gap Analysis & Phase 4 Roadmap

Phase 4 in our working sequence (OS Internals → Networking → Tooling → **here**).
In the [[Crook2Root Master Blueprint]]'s Pillar-One map this domain is Phase 5;
the two numberings refer to the same body of work.

The finding up front: **Offensive Security is not thin. It is the largest and
most structurally complete domain in the vault** — 116 content notes, median
~1,190 words, every one carrying sections, a worked example, and a summary. The
blueprint's baseline ("44 leaves with no worked example, 24 thin") is stale;
prior polishing passes closed almost all of it. The current measured state is
below. Phase 4 is therefore **not** a build-out. It is a **depth-and-currency
pass**: a small number of genuinely missing top-tier topics, a set of existing
notes that stop one technique short of the modern standard, and one systemic
quality lever that applies to all 112 notes that show shell commands.

---

## 1. Where we actually are (measured, not assumed)

Run against the current tree, not the blueprint's snapshot:

| Signal | Count | Reading |
|:--|--:|:--|
| Content notes (non-MOC) | 116 | The dominant domain |
| Notes flagged **thin** (<800w) | 0 | Depth backlog already cleared |
| Notes with **no worked example** | 4 | All four are methodology/planning notes |
| Notes showing shell commands with **no `verified:` date** | 112 | The systemic lever — see §7 |
| Long-preamble warnings | 1 | Cosmetic |

The `verified:` gap is corpus-wide, not specific to this domain (Tooling 66,
Networking 60, OS Internals 40 carry it too). But Offensive Security is where it
matters most, because its claims are the ones a reader will *execute against a
target*, and it is the domain whose credibility rests on "this actually works."

**What this means for method.** In Phase 3 the single highest-value move was to
*run the tool for real* and paste the output — the GIL benchmark, the Snort
evasion producing one alert, the Sigma pipeline actually re-mapping a field.
Phase 4 carries that standard into a domain that was written before it existed.
The gaps below are real; the verification pass is what raises the whole domain.

---

## 2. Web Exploitation — measured against OSWE

**Coverage is broad and strong.** Present with dedicated notes: SQLi, XSS, SSRF,
XXE, SSTI, insecure deserialization, file upload, LFI/RFI, OS command injection,
CSRF, CORS, prototype pollution, request smuggling, cache poisoning, JWT,
federated identity/SSO (SAML + OAuth), race conditions, NoSQL, LDAP, XPath, ORM,
CRLF, SSI, WAF bypass, business logic. This already exceeds a black-box web
syllabus (eWPT/BSCP-tier) at the topic level.

**The gaps are specific and modern:**

| Gap | Evidence | Recommendation |
|:--|:--|:--|
| **Whitebox source-code review methodology** | Zero notes match `white-box` / `source code review` as a discipline | **New note.** This is OSWE's *spine* — the exam is source-to-sink auditing, not black-box. A methodology note (taint tracking, sources/sinks, framework-specific sink catalogues, diffing, findings-to-PoC) is the single most important web addition. |
| **GraphQL security testing** | Only guided-assessment mentions; no note in the API branch | **New note** under API & Modern Protocol Testing (introspection, batching/aliasing DoS, field-level authz, injection through resolvers). |
| **Dependency confusion / supply-chain** | Absent | **New note** (or fold into a supply-chain note): package namespace confusion, npm/pip/maven resolution order, lockfile integrity. |
| **DOM clobbering** | Absent | **Deepen** Prototype Pollution & DOM Security — it is the natural neighbour, not a new note. |
| **Web LLM / prompt-injection surface** | Absent | **Defer** to the AI Security domain; cross-link from the web branch rather than author here. |

---

## 3. Active Directory & Identity — measured against CRTE / CRTO

**Coverage is genuinely strong.** Present with real depth: AD architecture &
enumeration, ACL-based privesc, Kerberos & NTLM attacks (incl. Kerberoasting,
AS-REP roasting), the full delegation family (unconstrained, constrained, RBCD),
ADCS security, NTLM relay & authentication coercion, domain persistence & trust
abuse (golden/silver tickets, cross-forest, SID history), gMSA, GPO abuse. This
is a CRTE-grade spine.

**The gaps are the newer tradecraft the incumbents added after 2021:**

| Gap | Evidence | Recommendation |
|:--|:--|:--|
| **Shadow Credentials** (msDS-KeyCredentialLink / PKINIT abuse) | Absent | **Deepen** ADCS Security or Kerberos — it is a PKINIT/certificate abuse and belongs beside them. Major modern technique (Whisker/Certipy). |
| **Hybrid identity: Entra ID ↔ on-prem AD** | Azure/Entra appears only as passing mentions in guided/unrelated notes — no real note | **New note.** Azure AD Connect, PHS/PTA abuse, Seamless SSO silver ticket, Primary Refresh Token theft. This is CARTP/CRTO's fastest-growing area and the on-prem↔cloud seam is where real breaches now pivot. **Highest-value new AD note.** |
| **SCCM / MECM attacks** | Absent | **New note** — network access accounts, client push, credential harvesting. CRTO 2 added this; real environments are full of it. |
| **Diamond / Sapphire tickets** | Absent | **Deepen** Kerberos & NTLM Attacks — the modern, stealthier evolution of golden tickets. |
| **DCShadow** | Absent | **Deepen** Domain Persistence & Trust Abuse — sits directly beside DCSync, which is present. |
| **Exchange / PrivExchange coercion** | Absent | **Deepen** NTLM Relay & Authentication Coercion — dated but part of the coercion family (PetitPotam neighbour). |

---

## 4. Binary Exploitation & RE Fundamentals — measured against OSED

**Exploit Development is one of the strongest branches in the vault** — ~15
notes at 1,500–1,900w covering CPU/ABI, ELF/PE/Mach-O, stack corruption, heap &
UAF, integer/type-confusion/format-string, ROP/JOP/SROP, shellcode engineering,
exploit reliability & mitigations, userland (incl. **SEH**, **egghunter**),
kernel and browser theory. This is OSED-grade and needs no build-out.

**The gap is not exploitation — it is reverse engineering as a discipline:**

| Gap | Evidence | Recommendation |
|:--|:--|:--|
| **RE fundamentals** (static/dynamic workflow, Ghidra/IDA methodology, anti-debugging, unpacking, triage) | Live only as scattered mentions inside Exploit Dev | This is the **empty [[Reverse Engineering & Malware]] domain** (1 MOC, 0 content). Per the blueprint it is gated on Phase 1 memory work and pairs with Exploit Dev. **Scope decision for Phase 4:** treat RE fundamentals as the natural bridge domain to open *after* the Offensive depth pass, and cross-link Exploit Dev to it — do not fold a whole RE branch into Offensive Security. |
| **WinDbg exploitation workflow** | `windbg` matches zero notes; the debugging note is GDB-centric | **Deepen** Fuzzing, Debugging & Crash Triage with the Windows workflow OSED assumes (WinDbg, `!exploitable`, mona.py). |

---

## 5. Post-Exploitation — measured against OSCP / CRTO

**The healthiest focus area.** Present: credential access & secret hunting,
local privilege escalation (Linux + Windows, incl. SeImpersonate/potato family),
persistence techniques, pivoting & tunneling, data collection & cleanup,
pass-the-hash/overpass, LOLBins. Little is missing.

| Gap | Evidence | Recommendation |
|:--|:--|:--|
| **Windows token manipulation** as a framed technique | Potato/SeImpersonate present, but `token impersonation` / `incognito` framing absent | **Deepen** Local Privilege Escalation — give the token model (impersonation vs primary, `SeImpersonatePrivilege`, the potato lineage) its own section rather than a passing mention. |

---

## 6. EDR Evasion & Tradecraft — measured against CRTO

**The largest genuine topic gap in the domain.** The base is good: AV/EDR &
Telemetry Evasion (with a coverage matrix), Payload Engineering & Obfuscation,
Process Injection & Direct Syscalls, C2 Infrastructure & Redirectors, OPSEC &
anti-forensics. **AMSI**, **ETW**, and **direct syscalls** are covered. But the
modern in-memory tradecraft that defines current CRTO is largely absent:

| Gap | Evidence | Recommendation |
|:--|:--|:--|
| **Userland unhooking** (restore `ntdll` from disk/KnownDLLs) | Absent | **New note** or deepen Process Injection — it is the counterpart to the hooks the EDR note describes. |
| **Sleep obfuscation & in-memory encryption** (Ekko/Foliage) | Absent | Same new note — how a beacon hides at rest between check-ins. |
| **Call-stack spoofing & module stomping** | Absent | Same new note — defeating stack-based and image-based detection. |
| **Indirect syscalls** | Only *direct* syscalls present | **Deepen** Process Injection & Direct Syscalls — indirect syscalls are the current evolution (direct syscalls are increasingly caught). |
| **Reflective / PE loading & Beacon Object Files** | Absent in the offensive framing | **New note** on the in-memory execution model (reflective DLL, PE loading, BOFs) — how post-ex code runs without touching disk. |
| **Malleable C2 profiles** | The C2 note covers redirectors, not profile shaping | **Deepen** C2 Infrastructure & Redirectors with profile shaping (the traffic side of the [[Command & Control Design Principles]] jitter lesson). |

**Recommendation:** one new note — *In-Memory Evasion: Unhooking, Sleep Masking
& Call-Stack Spoofing* — plus one on the *reflective/BOF execution model*, plus
deepening injection (indirect syscalls) and C2 (malleable profiles). This is the
cluster that most separates the current corpus from a 2026 red-team standard.

---

## 7. The cross-cutting lever: executed verification

112 Offensive Security notes show shell commands with no `verified:` date —
meaning the output was written, not run. This is the same gap Phase 3 closed by
*actually executing* each tool. It cannot be closed identically here (much of
this domain needs a live AD lab, a Windows target, an EDR), but it can be
closed **on The Thread**: stand up the Meridian lab pieces each branch needs,
run the technique, and paste real output with a `verified:` date — exactly as
the template already specifies.

The **4 methodology notes with no observation at all** (Cyber Kill Chain,
Penetration Testing Fundamentals, Penetration Testing Standards & Frameworks,
Red Team Campaign Planning & Initial Access) are the concrete starting point:
each needs one grounded artifact — a real scoping table, a real ATT&CK-mapped
timeline, a real command log — rather than pure prose.

---

## 8. Execution roadmap — decoupled high-depth passes

Same method as Phase 3: one branch per "go ahead", reported between each,
gates green before moving on, every claim executed on The Thread where a lab
can be stood up. Ordered by exam-and-real-world value and by dependency.

1. **Active Directory & Identity** — deepen (Shadow Credentials, Diamond
   tickets, DCShadow, Exchange coercion, token framing) and author the two new
   notes (**Hybrid Entra↔AD**, **SCCM/MECM**). Highest combined CRTE/CRTO/real
   value.
2. **EDR Evasion & Tradecraft** — author *In-Memory Evasion* and the
   *reflective/BOF execution model*; deepen Process Injection (indirect
   syscalls) and C2 (malleable profiles). The biggest topic gap.
3. **Web Exploitation** — author **Whitebox Source-Code Review Methodology**
   (the OSWE spine), **GraphQL**, and **Dependency Confusion**; deepen DOM
   clobbering into Prototype Pollution & DOM Security.
4. **Binary Exploitation / RE seam** — deepen the debugging note with the
   WinDbg workflow; scope the **Reverse Engineering & Malware** domain as the
   next bridge to open, cross-linked to Exploit Development.
5. **Post-Exploitation** — deepen Local Privilege Escalation with the Windows
   token-manipulation model. Smallest gap.
6. **Verification & evidence pass** — folded into each branch as it is touched:
   add executed output and `verified:` dates, starting with the 4 methodology
   notes that carry no observation at all.

**New notes to author: ~7.** **Existing notes to deepen: ~10.** Plus the
per-branch verification pass. Estimated shape: comparable to the Networking
domain pass, front-loaded on AD and Evasion.

---

*Compiled from a measured probe of the current tree against OSCP, OSWE, OSED,
CRTE and CRTO syllabi and current red-team tradecraft. The coverage claims are
grep-verified against the corpus, not estimated.*
