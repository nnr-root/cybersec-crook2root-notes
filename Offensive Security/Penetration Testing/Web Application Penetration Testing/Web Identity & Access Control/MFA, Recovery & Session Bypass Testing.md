---
title: "MFA, Recovery & Session Bypass Testing"
aliases: ["MFA Bypass Testing", "MFA Recovery Process Testing", "Account Recovery Testing"]
tags: [tree/offensive, cyber/offensive/web/identity/mfa, type/technique, difficulty/medium]
Domain: "[[Web Identity & Access Control]]"
Color: "#DC143C"
---

# 📱 MFA, Recovery & Session Bypass Testing

> [!warning] Authorized simulation only
> These tests probe the last line of account defense. Use synthetic accounts, throttle to avoid locking real users, and prove bypasses with benign markers. Test only in-scope applications.

## Parent Learning Order
Web Authentication Testing -> Broken Access Control -> JWT Security Testing -> Federated Identity & SSO -> MFA, Recovery & Session Bypass Testing

## The Second Factor and Its Escape Hatches

**Multi-Factor Authentication (MFA)** requires a second proof beyond the password — a code from an app, an SMS, a hardware key — so that a stolen password alone is not enough. It is the single most effective control against credential attacks. But MFA is only as strong as its *implementation and its bypasses*: the account-recovery flow that resets it, the session handling around it, and the ways it can be skipped. Attackers who cannot beat the password-plus-MFA front door look for the *side doors* — and there are usually several.

This note covers the three ways MFA-protected accounts fall: **bypassing MFA directly**, **abusing account recovery** (the "forgot password" flow that often has *weaker* protection than the login it resets), and **session flaws** that make MFA moot after the fact.

> [!tip] The analogy, and where it breaks
> MFA is a deadbolt added to a door that already has a lock. The analogy breaks because the *back door* (account recovery) often has only a flimsy latch — an attacker who can't pick the deadbolt just resets it through the "I lost my key" process, which frequently verifies identity far more weakly than the front door it bypasses. The strongest front door is worthless if the recovery process is weak.

**Prerequisites:** the authentication leaf (login and sessions), and MFA concepts.

## Direct MFA Bypass

MFA can be bypassed when it is bolted on rather than enforced throughout:

- **Missing enforcement on some endpoints** — MFA guards login but an API or a "remember me" path skips it.
- **Skippable step** — the flow lets you proceed to the authenticated area without completing the MFA step (a forced-browsing / state flaw).
- **Brute-forcing the code** — a 6-digit code has a million possibilities; without rate limiting, it is guessable.
- **MFA-fatigue / push-bombing** — spamming push approvals until the victim accidentally accepts (a social/technical hybrid).
- **Response manipulation** — changing a `"mfa_required": true` response to `false` in flows that trust the client.

The classic finding is **the second factor not being enforced server-side**: the app checks the password, sets a "half-authenticated" state, asks for the code — but the authenticated resources are reachable by skipping directly to them, because the server treated password-success as good enough.

## Account Recovery: The Weak Back Door

Account recovery (password reset, MFA reset) is a parallel authentication path, and it is frequently *weaker* than login:

- **Weak reset tokens** — predictable or non-expiring reset links.
- **Host-header injection** — the reset link's domain is built from an attacker-controllable `Host` header, sending the victim's reset link to the attacker (links to the HTTP Host-header trust issue).
- **Knowledge-based questions** — "mother's maiden name" is often OSINT-discoverable.
- **MFA reset without re-verification** — recovery disables MFA without strongly proving identity, defeating the whole control.
- **Account enumeration in reset** — the reset flow reveals which accounts exist (the enumeration flaw again).

Recovery is where many "MFA-protected" accounts actually fall, because the effort goes into the login while the reset flow is an afterthought.

```mermaid
flowchart TD
    A["MFA-protected account"] --> D{"Front door: password + MFA"}
    D -->|"MFA not enforced server-side"| B1["Skip to authenticated area"]
    D -->|"code brute-forceable"| B2["Guess the 6-digit code"]
    A --> R{"Back door: account recovery"}
    R -->|"weak reset token / host injection"| B3["Hijack the reset link"]
    R -->|"MFA reset without re-verification"| B4["Disable MFA via recovery"]
    B1 --> P["Prove with synthetic accounts, benign markers"]
    B3 --> P
    B4 --> P
```

## Worked Example: MFA That Is Prompted but Not Enforced

A second factor only protects a resource if the resource checks for it. A common
flaw prompts for MFA, records that the password was correct, and then guards the
protected page against the *password* state rather than the *MFA-complete* state.
The specimen has that exact gap:

```python
if path == "/login" and password_ok:
    half_auth.add(user)                    # password verified
    return '{"mfa_required": true}'
if path == "/dashboard":
    if user in half_auth:                  # BUG: checks password, not MFA
        return '{"data": "..."}'
```

**Logging in** looks correctly protected:

```shell-session
analyst@lab:~$ curl -s -X POST -d 'u=alice&p=S3cret!' http://127.0.0.1:8118/login
{"mfa_required":true}
```

The password is accepted and the app declares that MFA is required. A tester
watching the intended flow — password, then a code prompt — sees a second factor
and might conclude it is enforced.

**Skipping the second factor** is a single request that never touches the code
prompt:

```shell-session
analyst@lab:~$ curl -s http://127.0.0.1:8118/dashboard
{"data":"CANARY-DASHBOARD"}
```

The dashboard returned its data with no MFA completed. The server treated a
correct password as sufficient because the protected resource only checked the
half-authenticated state — the one the password created — and MFA, though
prompted, was never a precondition for anything. The prompt was theatre; the gate
was open.

This is why MFA testing follows the resource, not the login screen. The question
is never "does it ask for a code" but "does *every* authenticated resource refuse
to serve a session that has not completed MFA, verified server-side". The
half-authenticated state must gate the whole application until the second factor
is confirmed, and the check cannot live in the client, which the attacker
controls.

The second place to look is the recovery flow, because it is the designed bypass:
a "lost your device" path that resets MFA on a single emailed link, or a security
question, hands an attacker the same access the second factor was meant to
prevent. An MFA implementation is only as strong as the weakest way to switch it
off, and recovery is usually that way.

## MFA present is not MFA enforced

- **Locking out real users.** Code brute-force and recovery-flow testing can lock accounts. Synthetic accounts, throttling, coordination.
- **MFA present ≠ MFA enforced.** The finding is often that MFA *exists* but is skippable — test whether authenticated resources are reachable without completing it, don't assume the presence of an MFA prompt means protection.
- **Recovery is the real target.** Testing only the login and declaring "MFA protects this" misses the recovery back door, which is where the account often falls. Test recovery as rigorously as login.
- **Host-header reset.** A reset link built from the `Host` header lets an attacker receive a victim's reset — test whether the reset domain is attacker-influenceable.
- **Client-trusted MFA state.** A `mfa_required: false` the client can flip is a bypass; test whether MFA state is enforced server-side.

## Security Implications — Detection & Defense

- **Enforce MFA server-side, on every authenticated path** — never let a client-side flag or a skipped step reach authenticated resources. The half-authenticated state must gate everything until MFA completes.
- **Harden recovery to match login:** strong, expiring, single-use reset tokens; a `Host`-header-independent reset domain; strong identity proof before resetting MFA; and no account enumeration.
- **Rate-limit the MFA code** and prefer phishing-resistant factors (hardware keys / passkeys) over SMS, which is vulnerable to SIM-swap and interception.
- **Number-matching / context in push MFA** defeats push-bombing by requiring the user to actively match a number, not just tap "approve."
- **Detection**: repeated MFA-code attempts, recovery-flow abuse, and MFA-reset events are high-value signals — an account whose MFA was just reset then logged in from a new device is the takeover signature.

## Summary

You should now be able to:

- Explain what MFA protects against, and why account recovery is often the weak back door around it.
- Bypass a skippable MFA step, test recovery for weak tokens and host-header injection, and prove a bypass with a synthetic account.
- Explain why MFA must be enforced server-side on every path, why recovery must be hardened to match login, and why phishing-resistant factors and number-matching defeat the strongest MFA attacks.

---
> 🔼 Up: [[Web Identity & Access Control]]
