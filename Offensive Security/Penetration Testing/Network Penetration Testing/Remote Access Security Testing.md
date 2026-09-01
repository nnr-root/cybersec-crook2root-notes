---
title: "Remote Access Security Testing"
aliases: ["Remote Access Testing", "VPN Testing", "RDP Security Testing"]
tags: [tree/offensive, cyber/offensive/network-pentest, type/technique, difficulty/medium]
Domain: "[[Network Penetration Testing]]"
Color: "#DC143C"
---

# 🚪 Remote Access Security Testing

> [!warning] Authorized simulation only
> Remote-access portals are authentication endpoints — testing them risks account lockout and can disrupt legitimate remote workers. Throttle authentication attempts, coordinate lockout thresholds with the client, and test only in-scope portals.

## Parent Learning Order
External Network Pentesting -> Service Enumeration -> Layer 2 & 3 Network Attacks -> Remote Access Security Testing -> Internal Network Pentesting

## The Doors Meant to Let People In

Every organization needs to let remote employees in, so it deliberately exposes **remote-access services** — VPN gateways, RDP, SSH, Citrix, and remote-management portals. These are unique on the perimeter: unlike an accidentally-exposed database, they are *supposed* to be internet-facing, which means they must be extraordinarily well-authenticated, because a single credential that works here is a direct route from the internet into the internal network.

That makes remote access the highest-value external target: it bypasses the whole "find a vulnerability" game. If you can authenticate to the VPN, you are *inside* — no exploit needed. So remote-access testing is overwhelmingly about **authentication strength**: is there MFA, are credentials guessable, is the gateway itself patched?

> [!tip] The analogy, and where it breaks
> A VPN portal is the building's staff entrance — a real door, meant to open for the right people, guarded by a badge reader. The analogy breaks because the staff entrance is physically local, whereas a VPN portal is reachable by *the entire internet* simultaneously, so an attacker can try millions of badges from anywhere with no risk of being physically seen. The defense must therefore be cryptographic, not positional.

**Prerequisites:** the recon and enumeration leaves (to find the portals), and MFA/authentication concepts from the Networking security-architecture branch.

## What Remote-Access Testing Covers

Three attack surfaces, in order of impact:

| Surface | Test | Why it matters |
| --- | --- | --- |
| **Authentication** | MFA present? Credentials guessable? | A working credential = instant internal access |
| **The gateway software** | Known CVE on the appliance? | VPN/gateway CVEs are among the most-exploited flaws |
| **Configuration** | Default creds, weak ciphers, info disclosure | Low-effort footholds and downgrade paths |

The **authentication** surface dominates because of the payoff. The attacker's toolkit here is exactly the identities from OSINT: harvested email addresses become usernames, breach-corpus passwords become guesses, and a portal without MFA is vulnerable to **credential stuffing** (trying breached username/password pairs) and **password spraying** (trying one common password across many users, staying under lockout thresholds).

## Password Spraying: The Signature Technique

Spraying is the emblematic remote-access attack because it defeats lockout policy by design. Instead of many passwords against one account (which locks it), it tries **one password against many accounts**, then waits, then tries the next password:

```text
Attempt 1: Spring2026!  vs  [alice, bob, carol, dave, ...]   then wait
Attempt 2: Password123  vs  [alice, bob, carol, dave, ...]   then wait
```

Each account sees only one failed attempt per round, staying under the lockout threshold, while the attacker covers the whole user list with common passwords. Against a portal without MFA, one hit is a foothold. This is why MFA — not password policy — is the control that actually stops it: a correct password alone is no longer enough.

## The Gateway Itself as a Target

Remote-access appliances (VPN concentrators, gateways) are software, and their CVEs are catastrophic because a flaw in the *gateway* yields access without any credential at all. These have repeatedly been among the most-exploited vulnerabilities in real breaches, precisely because the payoff is direct internal access. Testing includes fingerprinting the appliance and version (enumeration) and checking it against known CVEs (vulnerability intelligence) — a high-priority external finding when the gateway is unpatched.

```mermaid
flowchart TD
    P["Find remote-access portals (recon)"] --> G{"Gateway software patched?"}
    G -->|"No: known CVE"| X["Exploit gateway -> internal access, no creds"]
    G -->|"Yes"| A{"MFA enforced?"}
    A -->|"No"| S["Spray / stuff credentials from OSINT + breaches"]
    A -->|"Yes"| H["Hardened: report verified, note MFA-fatigue risk"]
    S -->|"one hit"| I["Authenticated -> inside the network"]
    X --> I
    I --> N["Pivot -> Internal Network Pentesting"]
```

## When password spraying becomes denial of service

- **Account lockout = denial of service.** Aggressive spraying can lock out real employees, disrupting the business and burning the engagement's goodwill. Stay well under thresholds and coordinate.
- **Detection is near-certain for volume.** Spraying and stuffing produce a distinctive burst of failed logins across many accounts — modern identity providers alarm on exactly this. Slow, distributed spraying evades thresholds but not a patient analyst.
- **MFA is not absolute.** MFA-fatigue (push-bombing) and real-time phishing proxies can defeat weaker MFA; a portal *with* MFA is much stronger but not immune. Report MFA presence *and* its type.
- **The gateway CVE trumps everything.** If the appliance is unpatched with a known-exploited CVE, that is the finding — authentication strength is moot when the gateway itself is the way in.
- **Legitimate-looking access.** A successful credential attack produces a *valid* login, indistinguishable from a real user without behavioral analysis — which is why detection must look at context (impossible travel, new device), not just success/failure.

## Security Implications — Detection & Defense

- **MFA on every remote-access portal is the single highest-value control** — it neutralizes credential stuffing and spraying, the two commonest remote-access attacks, by making a stolen password insufficient.
- **Patch gateways fast.** Remote-access appliance CVEs are exploited within days of disclosure; the exposure window (from the continuous-validation leaf) is the metric that matters most here.
- **Detection is behavioral:** password-spray patterns (one password, many accounts, low per-account rate), impossible-travel logins, and new-device authentications are the signals. Identity-provider protection and conditional access enforce these automatically.
- **Reduce the exposed portal count.** Every internet-facing remote-access service is a target; consolidating to one well-hardened, MFA-enforced gateway shrinks the surface.
- **This is the perimeter breach that skips the exploit** — which is why remote-access hardening is disproportionately important: it closes the easiest path from internet to internal.

## Summary

You should now be able to:

- Explain why remote-access portals are uniquely dangerous (a credential = internal access, no exploit needed) and what MFA protects against.
- Distinguish brute-force (locks accounts) from spraying (one password, many users), demonstrate a spray that authenticates without lockout, and report MFA presence and type.
- Explain why gateway CVEs trump authentication strength, why detection must be behavioral (spray pattern, impossible travel) rather than success/failure, and why remote-access hardening closes the easiest internet-to-internal path.

---
> 🔼 Up: [[Network Penetration Testing]]
