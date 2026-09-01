---
title: "OSINT-Driven Pretext Development"
tags: [tree/offensive, cyber/offensive/social/pretext, difficulty/medium]
Domain: "[[Human Factors & Pretext Development]]"
Color: "#DC143C"
---

# OSINT-Driven Pretext Development

Pretexts use plausible business context while minimizing personal data and avoiding sensitive personal themes.

```mermaid
flowchart LR
    I["Approved OSINT"] --> R["Role/process model"]
    R --> P["Pretext"]
    P --> L["Legal/safety review"]
    L --> T["Canary exercise"]
```

Define objective, target cohort, communication channel, claimed identity, expected verification process, prohibited themes, data handling, and exit. Mastery lab: create three pretexts from public corporate information and reject one for privacy or harm risk.

## Parent Learning Order
Influence, Decision-Making & Human Risk -> OSINT-Driven Pretext Development

## Controlled pretext engineering

Start from a business process, not a person. Public job descriptions, supplier portals, conference agendas, press releases, technology vacancies, support hours, and organizational naming patterns can reveal how work normally arrives. Minimize collection: record the process cue and source URL, not a dossier of unrelated personal facts.

```text
Objective: test external collaboration-invite verification
Public cue: organization announced a new design partner
Claimed role: partner project coordinator
Requested action: open a harmless canary workspace
Expected defense: external-user label + known-channel confirmation
Abort: personal information disclosed or recipient shows distress
```

Score a pretext for plausibility, relevance to the threat model, required deception, privacy impact, potential distress, and reversibility. Legal and safety reviewers should reject themes involving health, family emergencies, layoffs, immigration, protected characteristics, or real compensation. Use synthetic identities and organization-controlled infrastructure. During execution, record which process cues carried trust and which controls interrupted the scenario. Retire the identity, domain, number, and landing page at exercise end.

## Summary

You should now be able to:

- What makes a pretext believable, and where does that raw material come from?
- Given a target's public photo, what three pretext-useful facts might its metadata leak, and how do you use them without crossing scope?
- Explain how metadata minimisation and profile hygiene reduce an organisation's pretext attack surface — and why they can never eliminate it.

---
> 🔼 Up: [[Human Factors & Pretext Development]]
