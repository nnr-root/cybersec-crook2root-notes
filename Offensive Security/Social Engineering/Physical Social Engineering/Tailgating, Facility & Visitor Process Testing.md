---
title: "Tailgating, Facility & Visitor Process Testing"
tags: [tree/offensive, cyber/offensive/social/facility, difficulty/easy]
Domain: "[[Physical Social Engineering]]"
Color: "#DC143C"
---

# Tailgating, Facility & Visitor Process Testing

Test reception, visitor sponsorship, badges, escorts, turnstiles, delivery/vendor workflows, secure-zone challenge culture, lost badges, and incident reporting.

```mermaid
flowchart LR
    V["Visitor"] --> R["Reception/verification"]
    R --> E["Escort/access"]
    E --> Z["Zone controls"]
```

Life safety overrides the exercise. Exclude emergency exits, medical/childcare areas, occupied sensitive spaces, and forced entry. Use visible authorization and white-team monitoring. Mastery lab: exercise one visitor and one delivery scenario with a canary destination and immediate debrief.

## Parent Learning Order
Tailgating, Facility & Visitor Process Testing -> Removable Media & BadUSB Exercise Governance

## Zone-based assessment

Map public, reception, employee, restricted, and critical zones. For each transition, identify the responsible control: receptionist validation, sponsor confirmation, badge issuance, anti-passback, turnstile, escort, guard challenge, camera coverage, or locked cabinet. A badge is an identifier, not proof that its holder belongs in every zone.

```text
Scenario: scheduled courier with synthetic package
Entry: loading reception
Canary destination: marked test shelf before restricted door
Pass: order verified, temporary badge issued, escort maintained
Stop: emergency activity, confrontation, uncontrolled access
```

Operators carry an authorization letter and immediate reveal mechanism. They do not defeat locks, block doors, photograph sensitive material, enter occupied private areas, or pressure staff after a challenge. Record control events and timings rather than employee names. Validate lost-badge revocation, visitor expiration, contractor sponsorship, delivery custody, and after-hours procedures. Debrief challenged staff positively; the desired culture makes polite verification normal and gives employees a fast escalation route.

## Summary

You should now be able to:

- What is tailgating, and which single control does it defeat?
- Design a bounded, safe test of a reception desk's visitor-verification process that measures the *process*, not one receptionist.
- Explain defence-in-depth for physical zones (mantrap, anti-passback, escort enforcement) and where each layer fails.

---
> 🔼 Up: [[Physical Social Engineering]]
