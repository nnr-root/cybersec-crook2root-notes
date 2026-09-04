---
title: "NetExec"
aliases: ["nxc", "CrackMapExec", "crackmapexec"]
tags: [tree/tooling, cyber/tooling/offensive/ad/netexec, type/tool, difficulty/medium]
Domain: "[[Active Directory & Windows Attack Tools]]"
Color: "#708090"
---

# NetExec

> [!abstract] Note of [[Active Directory & Windows Attack Tools]]
> NetExec answers one question fast — where is this credential valid, and where does it grant admin — and the same speed makes it the easiest way to lock out a domain. This note covers the sweep, the meaning of `Pwned!`, why spraying has a direction, and the authentication noise the sweep leaves behind.

NetExec (`nxc`, the maintained successor to CrackMapExec) is the swiss-army knife for authenticated Active Directory operations. One command sweeps a subnet, tests a credential across every host over SMB/WinRM/LDAP/MSSQL/RDP, and reports where it works and where it grants admin — the fastest way to answer "what does this credential unlock?"

> [!warning] Authorized operations only
> Spraying and mass-authentication can trigger account lockouts — a careless spray is a self-inflicted denial of service. Respect lockout thresholds and scope.

## Parent Learning Order
Impacket -> NetExec -> BloodHound -> Responder -> Mimikatz

## One credential, checked everywhere at once

> *You hold one valid credential. Which question matters more than "is it valid?"*
>
> Hold your answer — the section below is the response.

NetExec is the **validate & spread** stage — take one credential and find out, fast, everywhere it's good.

The insight it operationalises: in AD, the value of a credential isn't "is it valid?" but "*where* is it valid, and where is it **admin**?" A single local-admin password reused across 200 workstations turns one leaked hash into the whole fleet. NetExec sweeps that question in seconds — one credential against a whole subnet, over the protocol of your choice.

## Pointing it at a range, and reading (Pwned!)

Point it at a range with a credential (password *or* hash — it does pass-the-hash natively):

```shell-session
operator@kali:~$ nxc smb 10.10.10.0/24 -u r.okonkwo -p 'Summer2024!'
SMB  10.10.20.10  DC01    [+] meridian.test\r.okonkwo:Summer2024!
SMB  10.10.10.30  WS-030  [+] meridian.test\r.okonkwo:Summer2024! (Pwned!)   ← local admin here
operator@kali:~$ nxc smb 10.10.10.30 -u r.okonkwo -p 'Summer2024!' --sam
WS-030  [+] Dumping SAM hashes
WS-030  Administrator:500:aad3b435b51404eeaad3b435b51404ee:1a59b...
```

**Prerequisites:** SMB and WinRM, pass-the-hash, and the domain lockout policy.

The `(Pwned!)` marker is the payoff — it means **local admin**, not merely valid. From there, protocol-specific power: `--sam`/`--lsa` (dump creds), `-x '<cmd>'` (run a command), `-M <module>` (spider shares, enumerate, coerce), `--pass-pol` (read the lockout policy *before* you spray).

## Spraying has a direction, and backwards locks the domain

Password spraying has a **direction**, and getting it backwards locks out the domain:

```shell-session
# WRONG — many passwords against ONE user → lockout after 5 tries
operator@kali:~$ nxc smb DC01 -u admin_bob -p passwords.txt
SMB  DC01  [-] meridian.test\admin_bob: STATUS_ACCOUNT_LOCKED_OUT   ← you just locked the admin

# RIGHT — ONE password against MANY users → stays under the threshold
operator@kali:~$ nxc smb DC01 -u users.txt -p 'Spring2026!' --continue-on-success
SMB  DC01  [+] meridian.test\r.okonkwo:Spring2026!
SMB  DC01  [+] meridian.test\k.adeyemi:Spring2026!
```

**The deliberate break:** the first command is *brute-forcing* — many guesses at one account — and trips the lockout threshold almost immediately, alerting the SOC and denying service. The second is *spraying* — one plausible password (often seasonal, from `--pass-pol`) tried once against every user — which stays under the per-account lockout counter because each account sees only a single failure. Same tool, opposite blast radius. Always read the lockout policy first, cap attempts per account with margin, and pace between rounds. NetExec makes both trivial to run, which is exactly why the discipline is on you.

**How you'd spot it:** the difference lives in the failure counter, not in the tool. Read `--pass-pol` first: attempts per account approaching the lockout threshold means you are brute-forcing whatever you called it. From the defender's chair the shapes are opposite — one failure across many accounts in a short window is a spray; many failures against one account is a brute-force.

## Security Implications

**A sweep is a burst of network logons, and that is the detection.** Every host NetExec touches records the authentication — a success is **4624 type 3**, a failure **4625** — with the operator's account and source IP. One account authenticating to a whole subnet in seconds has no benign equivalent, so the finding is the fan-out: many distinct destinations from one source in a short window, exactly as with BloodHound's session sweep.

**A spray is louder to a defender than to the sprayed accounts, by design.** Each account sees a single 4625, which is why it slips under the lockout counter — but the domain controller sees dozens of them clustered in time from one source, all with the same failure reason. A detection keyed on 4625 volume *per source* rather than per account catches the spray the lockout policy was never going to.

**Reading the lockout policy first is safety, not stealth.** `--pass-pol` returns the threshold and window before any attempt; ignoring it and spraying blind is how an engagement becomes a self-inflicted denial of service that also alerts the SOC. The tool makes both the safe and the reckless version one flag apart.

All operations here require an authorized, scoped domain. Mass authentication affects account availability for real users, and a careless spray is an incident regardless of intent.

## Summary

You should now be able to:

- Explain why "where is this credential admin?" is the question NetExec exists to answer, and interpret the `(Pwned!)` marker.
- Dump SAM hashes from a host where you have local admin, and read the lockout policy before spraying.
- Explain why spraying one password across many users stays under the threshold while many passwords against one user does not — and why the defender sees the spray as a per-source burst even though each account sees one failure.

---
> 🔼 Up: [[Active Directory & Windows Attack Tools]]
