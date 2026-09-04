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

## Why the audit store has to be somewhere the tool cannot reach

The single design decision the whole tool rests on is *where the audit trail lives*. If ShadowStep writes its own log to the same host it operates on, then a tool whose job is to simulate tampering can tamper with its own record — the audit is only as trustworthy as the least-trusted action the tool can take, which is total. The architecture breaks the loop by writing evidence to a **remote, append-only store the local actions have no path to**: the operating host holds a write-only credential, the store rejects deletes and overwrites, and verification reads from the store rather than from anything on the host.

This is the same principle that makes the defence it teaches actually work. A real attacker deleting `/var/log/auth.log` is defeated not by file permissions — they have root — but by the fact that the events were shipped off-box the instant they were written. ShadowStep is built to demonstrate exactly that asymmetry: the local copy is deletable and the remote copy is not, so the *gap* between them is the evidence. A tool that kept its audit locally could prove nothing, because its own destructive modules could erase the proof; putting the store out of reach is what turns "trust me, it was scoped" into "here is the external record."

The **dry-run plan** enforces the second half of trustworthiness. Every destructive module must first emit a plan — which host, which actions, how many are destructive, whether rollback is available — and a human approves that plan before anything runs. The plan is not advisory output; it is a gate, and the destructive path is unreachable without a short-lived approval token minted against it. Safe-by-default means the tool's resting state does nothing irreversible, and every step toward irreversibility is a separate, logged, externally-witnessed decision.

## Proving that anti-forensics is detectable

The most important thing ShadowStep is designed to *prove* is that **anti-forensics is detectable** — and the `verify` step makes that the product:

```shell-session
responder@range:~$ shadowstep verify --audit-id ss-44a1
remote_audit=present         ← the action was recorded on an immutable REMOTE log
marker_detected_by_siem=true ← the SIEM SAW the tampering attempt
fixture_restored=true        ← and it was reversed
```

**The deliberate break:** a naive anti-forensics tool assumes deleting a log *removes the evidence*. ShadowStep's architecture demonstrates the opposite: because real logs are shipped to an **immutable remote store** the instant they're written, a local deletion leaves the remote copy intact — and worse (for the attacker), the *gap itself* is a signal a SIEM alerts on (a log source going silent is an incident). Every ShadowStep action is deliberately **paired with the detection it triggers** (log manipulation → immutable/remote logging + gap detection; shredding → recovery/backup + secure-delete telemetry; identity masking → attribution controls). That pairing is why it's a *defensive training* tool built like an offensive one: the scope gate and remote-audit layers of the architecture aren't safety theatre, they are the mechanism that turns "run anti-forensics" into "prove the blue team can catch anti-forensics." A tool this dangerous is only legitimate because its design makes every action scoped, planned, externally logged, reversible — and, above all, observable to the defenders it exists to train.

**How you'd spot it:** absence is the signal. A log source that goes quiet is an alert in any competently run SIEM, so the gap a deletion leaves is louder than the entries it removed. The same logic serves a defender directly — reconcile local logs against the remote store, and a local file shorter than its shipped copy names both the host and the window.

## Summary

You should now be able to:

- Explain why ShadowStep promotes the scope guard to a mandatory gate, and what the dry-run plan produces.
- Walk the plan → simulate → verify flow, and explain what each guarantees.
- Explain why deleting a log doesn't destroy the evidence, and how ShadowStep pairs each action with its detection.

---
> 🔼 Up: [[Writing Your Own Tools]]
