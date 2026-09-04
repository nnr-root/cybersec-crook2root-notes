---
title: "Phishing & Spear-Phishing Methodology"
aliases: ["Phishing", "Spear-Phishing", "Phishing Simulation", "Social Engineering & Phishing"]
tags:
  - tree/offensive
  - cyber/offensive/social/phishing-methodology
  - type/concept
  - difficulty/easy
Domain: "[[Phishing & Messaging Security Testing]]"
Color: "#DC143C"
---

# 🎣 Phishing & Spear-Phishing Methodology

> [!abstract] Note of [[Phishing & Messaging Security Testing]]
> A phishing exercise is an instrument, and like any instrument it measures whatever it was pointed at. Point it at people and it produces a click rate, which improves under pressure and tells you almost nothing. Point it at the control chain and it produces a map of which defences engaged, in what order, and where the chain has a hole. This note covers the difference, the mail-authentication mechanics the exercise tests, and how to build a campaign whose complete success is still harmless.

## Parent Learning Order
Phishing & Spear-Phishing Methodology -> Smishing, QR & Collaboration-Platform Testing

## What a Click Rate Does Not Tell You

> *Your simulation achieved a 2% click rate. Is that a good result?*
>
> Hold your answer — the section below is the response.

There is no way to know, because the number is not anchored to anything. A 2% click rate is a statement about one message, sent at one time, to one cohort, under one difficulty setting that the tester chose. Make the pretext clumsier and the number falls; make it match a real workflow and it rises. The exercise designer controls the metric directly, which is the defining property of a measurement that cannot be used for comparison.

Worse, the number is silent about everything that mattered. It does not say whether the message should have been delivered at all, whether anyone reported it, how quickly the analyst connected the reports, or whether the workflow the message targeted would have released money. Two campaigns with identical 2% click rates can describe opposite security postures.

**The deliberate break:** the click rate is treated as the score — the thing that goes on the slide, the thing that should trend down quarter over quarter.

It is a tuning knob, not a score. The metric that carries information is the **report rate and the time to first report**, because those measure something the tester does not control and the organisation can actually improve. A campaign where 8% clicked and 40% reported within six minutes is a healthier result than one where 2% clicked and nobody reported anything — in the second, a real campaign runs undetected until an analyst stumbles over it. Driving the click rate down by sending progressively easier messages produces a beautiful trend line and no change in defensive capability at all.

**How you'd spot it:** ask what happened to the reports. A programme with a genuine measurement practice can tell you its median time-to-report, how many reports were false alarms, and whether false alarms are treated as good outcomes. A programme optimising a click rate usually cannot answer any of the three, and often has no reporting button in the mail client at all.

## The Control Chain the Message Actually Passes

A phishing message crosses a dozen controls before it reaches a decision, and the exercise's job is to record which engaged.

```mermaid
flowchart LR
    S["Send"] --> A["SPF / DKIM / DMARC"]
    A --> R["Reputation & filtering"]
    R --> C["Content inspection"]
    C --> D["Attachment detonation"]
    D --> U["URL rewrite / safe links"]
    U --> L["External-sender label"]
    L --> H["Human decision"]
    H --> P["Report button"]
    P --> T["SOC triage"]
    T --> N["Containment"]
```

Each stage produces a verdict worth preserving. **A blocked message is evidence about a preventive control.** **A reported message is evidence about human detection.** These are different findings and neither substitutes for the other — an organisation whose gateway catches everything has no idea what its people would do on the day something novel arrives, and one relying on reporting alone is spending human attention on messages a filter should have removed.

## Why a Message Can Pass SPF and Still Spoof Your CEO

Mail authentication checks three different names, and users read a fourth.

| Mechanism | What it checks | What it does not check |
| --- | --- | --- |
| **SPF** | Is this sending IP authorised by the domain in the SMTP envelope (`MAIL FROM`)? | The `From:` header the recipient actually sees |
| **DKIM** | Does a signature verify against a key published by the signing domain (`d=`)? | That the signing domain has anything to do with the visible sender |
| **DMARC** | Does SPF's or DKIM's domain **align** with the visible `From:` header domain? | Content, intent, or whether the real sender is a person you trust |

The gap lives in the first row. An attacker registers `meridian-freight.test`, publishes a valid SPF record for their own sending host, and sends mail with `MAIL FROM: billing@meridian-freight.test`. SPF passes cleanly — the domain in the envelope did authorise that IP. The `From:` header can still read `d.varga@meridian.test` to the recipient, because SPF never looked at it. DMARC exists precisely to close this, by requiring that an authenticated domain *match* the visible one.

Three domains to compare in a captured header:

```text
Return-Path: <billing@meridian-freight.test>       ← SPF checks this
DKIM-Signature: ... d=meridian-freight.test;        ← DKIM signs as this
From: "D. Varga" <d.varga@meridian.test>            ← the user reads this
```

Misalignment here proves the message was not authorised by `meridian.test`, whatever the green "SPF pass" badge says. It does not prove malice on its own — which is the reason enforcement is rolled out carefully.

**Forwarding is the standard complication.** A mailing list or a forwarding rule re-sends the message from a new IP, breaking SPF, and often rewrites headers or footers, breaking the DKIM signature. When Meridian moves to `p=reject`, legitimate supplier mail routed through a list starts bouncing. The fix is to identify the forwarding path from DMARC aggregate reports, then either have the intermediary apply a scheme that preserves the original authentication result or authorise the specific relay — never to relax `p=reject` back to `p=none`, which restores delivery by removing the protection entirely.

## Broad and Spear Are Two Different Hypotheses

They are not difficulty settings of one test. They ask different questions and produce different findings.

| | Broad campaign | Spear campaign |
| --- | --- | --- |
| Hypothesis | Do the generic controls and the reporting path work at volume? | Does business context defeat controls that generic mail does not? |
| Cohort | Large, randomised, privacy-approved | Small, role-selected, justified in the plan |
| Reveals | Filter coverage, label behaviour, report-rate baseline | Workflow-specific authority gaps |
| Fails usefully when | A whole category of message is delivered unlabelled | A role can authorise something alone |

A spear campaign is closer to a workflow test than a mail test, which is why it belongs beside the decision mapping in [[Influence, Decision-Making & Human Risk]] rather than being judged on click rate at all.

## Designing a Campaign With a Safe Total Success

```text
Hypothesis:      external file-share invitations bypass link inspection
Cohort:          randomised, privacy-approved sample
Campaign ID:     SE-TEST-131  (unique, present in every artefact)
Action ceiling:  landing-page visit — no credential fields, ever
Landing page:    organisation-controlled, states it is an exercise
Expiry:          page and domain retired 2026-03-20
Expected telemetry: gateway verdict · DNS · proxy · user report · SOC case
White cell:      security lead + SOC shift lead, notified before send
Stop contact:    named, reachable during the whole window
```

The action ceiling is the line that makes the exercise defensible. A landing page with a password field collects real credentials from real people into a tester's infrastructure — a genuine breach committed on purpose, and one whose finding ("people type passwords into forms") was known in advance. The page records that a visit occurred, tied to the campaign identifier, and nothing else.

**Deconfliction matters more than it seems.** Seed the campaign indicators with the white cell before sending. Without that, a well-run SOC treats the exercise as a live incident, and the organisation spends a night on containment for a test — which is expensive, corrosive to trust, and teaches the SOC to hesitate next time.

> [!tip] The analogy, and where it breaks
> A phishing exercise resembles a fire drill: rehearse the response when nothing is burning. The analogy breaks in a way that changes the design — nobody records which individuals left the building slowest and circulates the list, because a fire drill measures the building's evacuation process. Phishing programmes routinely do the individual version, and it produces the same effect it would in a fire drill: people who are unsure stop raising their hand.

## Reading the Result and Closing the Loop

Debrief the process owner before the participants. In the participant debrief, teach the specific verification cue that would have worked here and the exact reporting route, rather than general vigilance — advice that names a button gets used, advice to "stay alert" does not.

Then remediate the root cause the exercise exposed: a supplier workflow that accepts bank changes by email, a missing external-sender label, a reporting button absent from the mobile client. Retest afterwards with different language and different timing, because a cohort that recognises the previous campaign's wording will produce an improved number without any improvement in control.

## Summary

You should now be able to:

- Explain why a click rate is a tuning knob rather than a score, and name the two metrics that carry information about defensive capability instead.
- Explain how a message can pass SPF and still spoof a colleague, identify the three domains to compare in a captured header, and say what misalignment does and does not prove.
- Diagnose a supplier whose legitimate mail fails DMARC after `p=reject` enforcement, and restore delivery without weakening anti-spoofing.
- Distinguish the hypotheses that broad and spear campaigns test, and design a campaign — action ceiling, canary identifier, expiry, white-cell deconfliction — whose complete success is still harmless.

---
> 🔼 Up: [[Phishing & Messaging Security Testing]]
