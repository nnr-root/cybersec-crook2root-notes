---
title: "Vishing & Executive Impersonation Testing"
tags: [tree/offensive, cyber/offensive/social/vishing]
Domain: "[[Voice, Help Desk & Identity Verification]]"
Color: "#DC143C"
---

# Vishing & Executive Impersonation Testing

Voice exercises test callback verification, authority pressure, payment/data processes, caller-ID trust, escalation, recording, and reporting.

```mermaid
flowchart LR
    P["Pretext"] --> C["Call"]
    C --> V["Independent verification"]
    V --> O["Outcome & report"]
```

Use trained operators, approved scripts, canary transactions, prohibited topics, and immediate abort. Do not imitate distress or collect real secrets. Mastery lab: test one executive payment request and one vendor-change request, measuring process rather than individual blame.

## Parent Learning Order
Help Desk Identity Verification -> MFA Recovery Process Testing -> Vishing & Executive Impersonation Testing

## Voice-specific threat model

Caller ID, voice familiarity, job-title authority, conversational confidence, and knowledge of current events can create false trust. Synthetic voice technology increases plausibility but does not change the control requirement: sensitive actions must be verified through an independent, policy-approved channel.

Prepare a call card containing the exact claim, permitted responses, forbidden requests, escalation phrase, maximum duration, and abort conditions. The operator must never ask for a password, MFA code, real payment, private employee data, or remote-control installation.

```text
Claim: urgent supplier bank-detail correction
Canary: ticket FIN-TEST-204
Secure path: terminate call → dial known directory number → verify ticket owner
Pass: request refused or independently validated
Fail: workflow advances based only on inbound voice authority
```

Measure callback use, verification questions, supervisor escalation, ticket quality, fraud-team notification, and time to report. Debrief the process owner before participants, preserve aggregate results, and test remediation with a different script so memorized wording does not masquerade as resilience.

## Runnable Lab (one machine, Python)

Caller ID, a familiar voice, and job-title authority create false trust — synthetic voice only makes it more plausible. None of it changes the rule: a sensitive action must be verified through an independent, directory-known channel. This lab encodes that control and shows it holding under an "executive" payment demand.

**Step 1 — the callback-verification gate (`verify.py`).**

```python
def decide(req):
    sensitive = req["action"] in {"password_reset","mfa_reset","bank_change","payment"}
    ob = req.get("out_of_band_callback") and req.get("directory_number")
    return "ALLOW" if (not sensitive or ob) else "BLOCK (requires independent callback verification)"
```

**Step 2 — run it against four inbound requests.**

```console
$ python3 verify.py
help desk caller   password_reset -> BLOCK (requires independent callback verification)
help desk caller   password_reset -> ALLOW
'exec' inbound     payment        -> BLOCK (requires independent callback verification)
user               mfa_reset      -> ALLOW
```

**Step 3 — the deliberate contrast.** The same `password_reset` is both BLOCK and ALLOW — the *only* difference is whether the agent hung up and called back a directory number. Inbound authority (even a perfect voice clone) never satisfies the gate; the callback does.

**Step 4 — cleanup:** decision simulation only — no cleanup required.

**What you should now be able to do:** state why caller ID and voice are not identity, and design the out-of-band callback rule that makes a sensitive action safe regardless of who is on the line.

## Crook → Operator → Root Checkpoint

- **Crook:** Why can't a convincing voice on the phone authorise a bank-detail change?
- **Operator:** Build the call card for an authorized vishing test of a finance team — claim, canary, secure path, abort condition.
- **Root:** Voice-cloning defeats "I recognise their voice." Explain why the callback control is unaffected, and what telemetry proves the process was followed.

---
> 🔼 Up: [[Voice, Help Desk & Identity Verification]]
