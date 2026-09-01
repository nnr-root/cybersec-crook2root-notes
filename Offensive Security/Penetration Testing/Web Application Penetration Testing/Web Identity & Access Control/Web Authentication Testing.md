---
title: "Web Authentication Testing"
aliases: ["Authentication Attacks", "Identity and Session Testing", "Session Management Testing"]
tags: [tree/offensive, cyber/offensive/web/auth, type/technique, difficulty/medium]
Domain: "[[Web Identity & Access Control]]"
Color: "#DC143C"
---

# 🔐 Web Authentication Testing

> [!warning] Authorized simulation only
> Authentication testing probes login, session, and account flows. Throttle to avoid locking out real users, test with synthetic accounts, and prove flaws with benign markers. Test only in-scope applications.

## Parent Learning Order
Web Authentication Testing -> Broken Access Control -> JWT Security Testing -> Federated Identity & SSO -> MFA, Recovery & Session Bypass Testing

## Proving Who You Are, and Staying Proven

**Authentication** is how an application establishes who you are; **session management** is how it *remembers* that across the many stateless HTTP requests that follow. Both are attack surfaces, and this note covers the foundation the rest of the identity cluster builds on: how login and sessions work, and the flaws in each. Because a broken authentication flaw often means *complete account takeover*, this is among the highest-impact web testing.

The two phases:

- **Login** — verifying a credential (usually a password). Flaws: weak credentials, credential stuffing, username enumeration, brute-force without lockout.
- **Session** — the token (usually a cookie) proving you already logged in. Flaws: predictable tokens, tokens that don't expire, tokens not invalidated on logout, tokens leaked or fixated.

> [!tip] The analogy, and where it breaks
> Authentication is the ID check at a club door; the session token is the wristband you get so you don't re-show ID all night. The analogy breaks on wristband forgery: a club wristband is hard to copy, but a predictable or non-expiring session token is trivially guessed, stolen, or reused — and unlike a wristband, one leaked token can be used from anywhere in the world simultaneously.

**Prerequisites:** HTTP, cookies, and the statelessness concept.

**The deliberate break:** testing authentication means testing the login form. That is where the password goes, so that is where the security is.

The login form is usually the **strongest** part of an authentication system, because it is the part everyone remembers to harden — rate limiting, MFA, lockout, monitoring. Authentication is the whole set of paths that can end with the application believing you are someone: registration, password reset, email change, "remember me", account recovery, and any SSO or social login bolted on beside them. Those paths are built later, tested less, and frequently skip the controls the login has.

The consequence is a rule worth carrying: **if recovery is weaker than the front door, an attacker does not attack the front door.** A reset flow that accepts a guessable token, or a help desk that will change an email address on a plausible phone call, is the authentication system — MFA on the login page notwithstanding.

**How you'd spot it:** enumerate every path that ends in an authenticated session, then check each one for the controls the login has. An MFA prompt that appears at login and *not* after a password reset is the finding, and it will not show up in any scan.

## Login Attacks

The login form is constantly attacked, and testing checks the defenses:

- **Username enumeration** — does the app reveal whether a username exists? Different responses for "wrong password" vs. "no such user" (in the message, status code, or *timing*) let an attacker build a valid-username list. The fix is identical responses regardless.
- **Brute-force / credential stuffing** — without rate limiting and lockout, an attacker tries many passwords (brute-force) or breached username/password pairs (stuffing). Testing checks whether limits exist and are effective.
- **Weak credential policy** — does the app permit `password123`? Weak policies make guessing trivial.
- **Password spraying** — one common password across many users (the remote-access leaf's technique), defeating per-account lockout.

```bash
# username enumeration: do the responses differ for valid vs invalid users? (your own lab)
echo "valid user, wrong pass -> $(curl -s -X POST -d 'u=alice&p=wrong' http://127.0.0.1:8116/login)"
echo "invalid user           -> $(curl -s -X POST -d 'u=nobody&p=wrong' http://127.0.0.1:8116/login)"
```

```text
valid user, wrong pass -> Incorrect password
invalid user           -> No such user
```

The two messages differ — "Incorrect password" reveals `alice` exists, "No such user" reveals `nobody` doesn't. That difference is username enumeration, letting an attacker confirm valid accounts before spraying. Identical responses ("Invalid credentials") for both is the fix.

## Session Attacks

Once logged in, the session token is the prize:

- **Predictable tokens** — a sequential or weakly-random session ID can be guessed, letting an attacker ride a valid session. Tokens must be long and cryptographically random.
- **Session fixation** — the app accepts a session ID *set before login* and keeps it after; an attacker fixes a known ID on the victim, waits for them to log in, then uses it. The fix: regenerate the session ID on login.
- **Missing expiry / invalidation** — a token that never expires, or survives logout, extends the attack window. Logout must invalidate server-side.
- **Insecure cookie flags** — missing `HttpOnly` (script can steal it), `Secure` (sent over HTTP), `SameSite` (CSRF) — the cookie hardening from the HTTP fundamentals leaf.

```mermaid
flowchart TD
    L["Login attempt"] --> E{"Reveals valid usernames?"}
    E -->|"different responses"| U["Username enumeration"]
    L --> B{"Rate-limited + lockout?"}
    B -->|"no"| BF["Brute-force / stuffing"]
    L -->|"success"| S["Session token issued"]
    S --> P{"Token: random? regenerated? expires? flagged?"}
    P -->|"predictable"| G["Guess/ride session"]
    P -->|"not regenerated"| F["Session fixation"]
    P -->|"no expiry / bad flags"| T["Theft / extended window"]
```

## Brute force as an outage you caused

- **Locking out real users.** Brute-force and spray testing can lock legitimate accounts (DoS). Use synthetic accounts, throttle, and coordinate.
- **Timing-based enumeration.** Even identical messages can leak via *timing* (a valid user's password is hashed, an invalid one short-circuits). Test response timing, not just content.
- **Session token in the URL.** A token in a URL leaks via referrer, history, and logs — check where the token lives, not just its randomness.
- **Logout that only clears the cookie.** Client-side logout that doesn't invalidate the token server-side means a captured token still works. Test whether the token is dead after logout.
- **Proving with real accounts.** Session hijacking must be demonstrated between two synthetic sessions, never against a real user's session.

## Security Implications — Detection & Defense

- **Identical responses and timing** for valid/invalid usernames defeat enumeration — the app must not reveal which accounts exist.
- **Rate limiting, lockout, and MFA** defeat brute-force, stuffing, and spraying — MFA in particular (the next leaves) makes a correct password insufficient.
- **Cryptographically random session tokens, regenerated on login, expiring on timeout, and invalidated on logout** — the session hygiene that closes fixation, prediction, and reuse.
- **Secure cookie flags** (`HttpOnly`, `Secure`, `SameSite`) limit token theft and CSRF — a one-header hardening.
- **Detection is behavioral:** failed-login bursts (brute-force), one-password-many-users (spraying), impossible-travel logins, and concurrent sessions from distant locations are the signals — the identity-provider protections that make credential attacks detectable even when individually valid.

## Summary

You should now be able to:

- Explain the two phases (login and session), and why a session token is the prize after login.
- Test username enumeration by content and timing, test session tokens for predictability and fixation, and prove hijacking between synthetic sessions.
- Explain why identical responses/timing, random regenerated expiring tokens, and MFA are the layered defenses, and how credential attacks surface as behavioral anomalies to a defender.

---
> 🔼 Up: [[Web Identity & Access Control]]
