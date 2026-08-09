---
title: "Social Engineering Safety & Ethics"
tags: [tree/offensive, cyber/offensive/social/safety]
Domain: "[[Social Engineering Exercise Governance & Metrics]]"
Color: "#DC143C"
---

# Social Engineering Safety & Ethics

Define informed organizational authorization, minimal deception, protected groups, prohibited personal themes, no real credential collection, privacy, secure data, stop authority, support, debrief, and non-punitive use.

```mermaid
flowchart LR
    P["Proposal"] --> L["Legal/HR/privacy review"]
    L --> S["Safety controls"]
    S --> E["Exercise"]
    E --> D["Debrief/support"]
```

Prohibit medical/family distress, threats, harassment, discrimination, real financial loss, uncontrolled public embarrassment, and targeting unrelated personal accounts. Mastery lab: risk-assess five scenarios and redesign or reject unsafe ones.

## Parent Learning Order
Social Engineering Safety & Ethics -> Human-Risk Metrics & Program Improvement

## Safety case

Treat every exercise as a documented safety case. Identify participants and bystanders, plausible harms, existing safeguards, residual risk, decision owner, stop authority, support route, and post-exercise review. Authorization by a manager does not override employment law, privacy obligations, union agreements, accessibility needs, or human dignity.

Use data minimization by design: synthetic credentials, opaque participant IDs, aggregate reporting, narrow retention, encryption, and role-limited access. Operators must know how to respond if a participant reveals abuse, self-harm, fraud, medical information, or another real emergency; the exercise stops and the established safeguarding process takes precedence.

```text
Risk: recipient believes employment is threatened
Likelihood: medium    Severity: high
Decision: reject scenario
Replacement: routine document-sharing invitation with harmless canary
```

Debrief quickly and non-punitively. Explain the control being tested, how data will be used, and where support is available. Delete raw identifiers on schedule. Ethical mastery is the ability to produce reliable security evidence with the least deception and harm—not the ability to make a scenario maximally convincing.

## Runnable Lab (one machine, Python)

Ethics in social engineering is not a vibe — it is a **go/no-go gate** every exercise must pass before it runs. This lab encodes that gate and shows it blocking an exercise that is missing a required control.

**Step 1 — the safety gate (`safety.py`).**

```python
gates={"legal_signoff":True,"hr_privacy_review":True,"white_team_named":True,
       "prohibited_themes_listed":True,"abort_criteria":False,"individual_blame_prohibited":True}
missing=[g for g,ok in gates.items() if not ok]
print("GO" if not missing else "NO-GO — missing: "+", ".join(missing))
```

**Step 2 — run it.**

```console
$ python3 safety.py
Safety gate check before any social-engineering exercise:
  [x] legal_signoff
  [x] hr_privacy_review
  [x] white_team_named
  [x] prohibited_themes_listed
  [ ] abort_criteria
  [x] individual_blame_prohibited
GO/NO-GO: NO-GO — missing: abort_criteria
```

**Step 3 — the deliberate failure (the point).** Five of six gates pass, yet the exercise is **NO-GO** — a missing abort criterion is disqualifying on its own. Safety is conjunctive: every gate must hold, not most.

**Step 4 — cleanup:** checklist evaluation only — no cleanup required.

**What you should now be able to do:** list the non-negotiable gates before any social-engineering exercise and explain why "mostly approved" is not approved.

## Crook → Operator → Root Checkpoint

- **Crook:** Why must legal, HR, and privacy sign off *before* a phishing simulation, not after?
- **Operator:** Write the abort criteria for a vishing exercise — what conditions force an immediate stop?
- **Root:** Explain why measuring individuals (naming who clicked) damages a security program, and what to measure instead.

---
> 🔼 Up: [[Social Engineering Exercise Governance & Metrics]]
