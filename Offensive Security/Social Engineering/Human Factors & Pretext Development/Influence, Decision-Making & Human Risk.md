---
title: "Influence, Decision-Making & Human Risk"
tags: [tree/offensive, cyber/offensive/social/psychology]
Domain: "[[Human Factors & Pretext Development]]"
Color: "#DC143C"
---

# Influence, Decision-Making & Human Risk

Social attacks exploit context, authority, urgency, reciprocity, familiarity, scarcity, fear, workload, and process ambiguity—not user stupidity.

```mermaid
flowchart LR
    C["Context/pressure"] --> D["Decision"]
    P["Process & interface"] --> D
    D --> A["Action/reporting"]
```

Assess whether processes support verification, refusal, escalation, and reporting. Avoid shame and individual ranking. Mastery lab: redesign a high-pressure payment and password-reset process so secure behavior is the easiest behavior.

## Parent Learning Order
Influence, Decision-Making & Human Risk -> OSINT-Driven Pretext Development

## From cognitive shortcut to enterprise risk

People make rapid decisions by using cues: the apparent authority of a sender, consistency with an existing conversation, urgency, social proof, and the cost of delaying work. These shortcuts are not defects; they are necessary under workload. Risk appears when a business process lets one plausible message authorize a high-impact action. A mature assessment therefore maps **decision → authority → verification → consequence**, rather than counting who clicked.

| Pressure cue | Unsafe process condition | Resilient control |
|---|---|---|
| Executive urgency | One-person payment release | Independent approval in the payment system |
| Familiar supplier | Bank changes accepted by email | Callback to a known number and change hold |
| Help-desk empathy | Identity established with public facts | Strong recovery factors and supervisor escalation |
| Notification fatigue | Repeated prompts without context | Number matching, device context, rate limits |

## Practical analysis

For an approved workflow, interview process owners, observe normal exceptions, and identify where staff must choose between delivery speed and verification. Build a harmless scenario around that tension. Record which technical and procedural layers intervene: sender authentication, warning banners, identity checks, approval separation, user reporting, analyst triage, and transaction reversal.

```text
Decision: approve supplier bank change
Authority claimed: finance director
Independent evidence available: vendor master record + known phone number
Irreversible point: payment batch release
Required control: two-person approval outside the message channel
```

Mastery means designing systems in which refusal is socially safe, verification is fast, and urgent exceptions leave a reviewable audit trail.

## Runnable Lab (one machine, Python)

Social-engineering messages engineer a decision context out of a handful of psychological levers — urgency, authority, scarcity, fear. This lab scores a message for those levers, turning a fuzzy "feels like phishing" into a countable signal.

**Step 1 — the trigger scorer (`influence.py`).**

```python
triggers={"urgency":["now","immediately","within 30 minutes","expires"],
          "authority":["CEO","director","on behalf of"],
          "scarcity":["last chance","limited","only today"],
          "fear":["suspended","locked","legal action","fired"]}
msg="URGENT: on behalf of the CEO — your account will be suspended within 30 minutes unless you verify now"
m=msg.lower()
hits={c:[w for w in ws if w in m] for c,ws in triggers.items()}
```

**Step 2 — run it.**

```console
$ python3 influence.py
  urgency  : ['now', 'within 30 minutes']
  authority: ['on behalf of']
  fear     : ['suspended']
influence_pressure_score = 4  (high score = engineered decision context, not a real request)
control: high-pressure + sensitive action  =>  mandatory slow-path verification
```

**Step 3 — the deliberate contrast.** Re-run with a normal message ("Here's the report you asked for") and the score drops to 0. The point is not to block words — it is that **pressure + a sensitive action** is the pattern that should force a slow, out-of-band check.

**Step 4 — cleanup:** read-only text scoring — no cleanup required.

**What you should now be able to do:** name the classic influence levers, spot them in a message, and design the process control (a mandatory slow path) that neutralises them regardless of wording.

## Crook → Operator → Root Checkpoint

- **Crook:** Why do attackers manufacture urgency and invoke authority?
- **Operator:** Two messages score identically. Why is *scoring* still less reliable than a process that makes the safe action the easy action?
- **Root:** Explain why security awareness training that relies on individuals "spotting" pressure fails at scale, and what system-level control replaces it.

---
> 🔼 Up: [[Human Factors & Pretext Development]]
