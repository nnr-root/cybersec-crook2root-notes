---
title: "ShadowStep Tool Architecture"
aliases: ["ShadowStep Engineering"]
tags: [tree/tooling, cyber/tooling/development/shadowstep, type/concept, difficulty/hard]
Domain: "[[Writing Your Own Tools]]"
Color: "#708090"
---

# ShadowStep Tool Architecture

ShadowStep is an open-source Python **anti-forensics simulator** — it models log manipulation, data shredding, and network-identity masking so that *defenders* can validate tamper detection, immutable logging, recovery, and attribution controls. It is the architecture principles applied to a deliberately dangerous domain, where the scope gate and reproducible-evidence layers are not optional but the whole point. (A featured tool of this vault.)

> [!danger] IR training & controlled red-team simulation only
> Destructive modules run only on disposable range hosts or client-authorized artifacts. Production evidence preservation and legal holds override any cleanup request.

## Parent Learning Order
Security Tool Architecture & Design Patterns -> Building Network Scanners -> Command & Control Design Principles -> Hashsmith Tool Architecture -> ShadowStep Tool Architecture

## A scope gate every action must pass

> *What must every ShadowStep action pass through before anything runs?*
>
> Hold your answer — the section below is the response.

ShadowStep is the "well-built tool" diagram with the **scope guard promoted to a mandatory gate** every action must pass.

A typed CLI feeds a **policy/scope gate**, which produces a **dry-run plan** *before* anything runs; three capability modules (log simulation, lab-artifact shred, identity-mask simulation) are plugins behind that gate; and every action writes to a **remote immutable audit** with rollback/verification. The design philosophy: an anti-forensics tool is only defensible if it is *safe by default* and every destructive step is scoped, planned, logged elsewhere, and reversible.

## Plan, act inside scope, then verify

The interface refuses to do anything surprising — plan first, then act inside scope, then verify:

```shell-session
responder@range:~$ shadowstep plan --profile ir-lab.yaml --dry-run
SAFE PLAN  host=range-ubuntu-04 actions=3 destructive=1 rollback=available
responder@range:~$ shadowstep simulate logs --fixture /srv/range/auth.log --marker C2R-IR-44
SIMULATED  records=2 fixture_only=true audit_id=ss-44a1
responder@range:~$ shadowstep verify --audit-id ss-44a1
remote_audit=present  fixture_restored=true  marker_detected_by_siem=true
```

Architecture rules: canonicalize every path and **deny system log locations** unless a disposable-lab policy explicitly allows them; require a dry-run and a short-lived approval token for destructive modules; write the audit trail to a *remote* store the local actions can't reach.

## Proving that anti-forensics is detectable

The most important thing ShadowStep is designed to *prove* is that **anti-forensics is detectable** — and the `verify` step makes that the product:

```shell-session
responder@range:~$ shadowstep verify --audit-id ss-44a1
remote_audit=present         ← the action was recorded on an immutable REMOTE log
marker_detected_by_siem=true ← the SIEM SAW the tampering attempt
fixture_restored=true        ← and it was reversed
```

**The deliberate break:** a naive anti-forensics tool assumes deleting a log *removes the evidence*. ShadowStep's architecture demonstrates the opposite: because real logs are shipped to an **immutable remote store** the instant they're written, a local deletion leaves the remote copy intact — and worse (for the attacker), the *gap itself* is a signal a SIEM alerts on (a log source going silent is an incident). Every ShadowStep action is deliberately **paired with the detection it triggers** (log manipulation → immutable/remote logging + gap detection; shredding → recovery/backup + secure-delete telemetry; identity masking → attribution controls). That pairing is why it's a *defensive training* tool built like an offensive one: the scope gate and remote-audit layers of the architecture aren't safety theatre, they are the mechanism that turns "run anti-forensics" into "prove the blue team can catch anti-forensics." A tool this dangerous is only legitimate because its design makes every action scoped, planned, externally logged, reversible — and, above all, observable to the defenders it exists to train.

## Summary

You should now be able to:

- Explain why ShadowStep promotes the scope guard to a mandatory gate, and what the dry-run plan produces.
- Walk the plan → simulate → verify flow, and explain what each guarantees.
- Explain why deleting a log doesn't destroy the evidence, and how ShadowStep pairs each action with its detection.

---
> 🔼 Up: [[Writing Your Own Tools]]
