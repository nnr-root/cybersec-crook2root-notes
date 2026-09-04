---
title: "OSINT-Driven Pretext Development"
aliases: ["Pretexting", "Pretext Development", "OSINT Pretext"]
tags:
  - tree/offensive
  - cyber/offensive/social/pretext
  - type/concept
  - difficulty/medium
Domain: "[[Human Factors & Pretext Development]]"
Color: "#DC143C"
---

# 🎭 OSINT-Driven Pretext Development

> [!abstract] Note of [[Human Factors & Pretext Development]]
> A pretext is a claim that makes a request feel routine. This note covers where the raw material for that claim actually comes from — which is not where beginners look — how to score a pretext before anyone is exposed to it, which themes are refused outright, and how to retire the infrastructure when the exercise ends.

## Parent Learning Order
Influence, Decision-Making & Human Risk -> OSINT-Driven Pretext Development

## A Pretext Rides a Process, Not a Person

> *You have the target's public profile, their conference talk, and the name of their dog. Which of these makes the pretext work?*
>
> Hold your answer — the section below is the response.

The conference talk, and only because it reveals *when they are out of the office*. The profile and the dog contribute nothing that a request needs in order to feel routine.

A pretext succeeds when a request matches a pattern the recipient already services many times a week. What carries it is knowledge of **how work normally arrives** at that desk: which channel, in whose name, with what reference number, under what deadline. A message that fits the shape of the day gets handled. A message stuffed with personal detail about the recipient does not fit that shape at all — it is unusual, and unusual is precisely what a recipient notices.

| Source | The process cue it yields | Why that cue carries a request |
| --- | --- | --- |
| Job postings | The tooling, the team structure, who reports to whom | Names a plausible internal requester and their remit |
| Supplier and partner announcements | Who has a live commercial relationship right now | An unknown vendor is suspicious; a current one is expected |
| Support pages and published hours | The channel and the reference format for requests | Lets the request arrive in the shape the desk expects |
| Conference agendas | Who is away, and when | Explains why the usual approver cannot be reached |
| Email footers and out-of-office replies | Naming conventions, ticket prefixes, signature form | Makes the artefacts of the request look native |
| Filing and procurement records | The contract cycle and renewal dates | Gives the deadline a reason to exist |

Note what is absent from that column. Home addresses, family details, health, finances, relationships, photographs of the person: none of it makes a request more routine, and all of it raises the harm if the collection leaks.

**The deliberate break:** open-source intelligence sounds like an instruction to gather as much as possible about a person, and the resulting dossier feels like progress because it is thick.

Depth on a person is the wrong axis, and it is actively counterproductive. The operative knowledge is **shallow and about the organisation**: how a request reaches this desk, who is plausibly asking, what reference number it would carry. A pretext built from a personal dossier tends to *leak* that depth — the operator, having done the reading, mentions something no legitimate requester would know — and that mention is the tell that ends the call. Meanwhile the dossier is a real privacy liability held on the tester's disk for a finding it did not contribute to.

**How you'd spot it:** the incoming request that knows too much about *you* and too little about *the process*. Legitimate internal requesters get the ticket prefix right and the personal details vague, because they have never looked you up. A message that opens with a personal reference and then asks for something in the wrong channel, or without a reference number, has the ratio backwards.

## Minimum Viable Collection

The discipline follows from the break: record the cue and its source, not the person.

```text
Objective:        test external collaboration-invite verification
Public cue:       Meridian announced a new design partner (press release, 2026-02)
Source:           meridian.test/news/design-partner  (retrieved 2026-03-01)
Claimed role:     partner project coordinator  — synthetic identity, role only
Channel:          collaboration platform invite
Requested action: open a canary workspace, ref SE-TEST-121
Expected defense: external-user label + confirmation on a known channel
Personal data:    none collected, none used
Abort:            personal information disclosed · recipient shows distress
```

Two properties make this record defensible. It is **auditable** — every cue names where it came from and when, so a reviewer can confirm nothing was collected outside the authorised scope. And it is **disposable** — nothing in it needs protecting after the exercise, because nothing in it is about a private individual.

## Scoring a Pretext Before Anyone Sees It

A pretext is reviewed and either approved or refused before it touches a person. Score it on six axes, and treat a poor score on any single axis as sufficient to refuse.

| Axis | The question | Refuse when |
| --- | --- | --- |
| Plausibility | Does this match how work actually arrives here? | It requires the recipient to behave unusually to succeed |
| Threat relevance | Does a real adversary have a reason to do this? | The scenario tests a threat nobody faces |
| Deception required | How much untruth carries it? | It needs a lie the organisation could not defend publicly |
| Privacy impact | What personal data does it touch? | It depends on personal facts about the recipient |
| Distress potential | How does this feel to receive? | It could frighten, shame, or destabilise the recipient |
| Reversibility | What happens if it works completely? | Full success causes harm that cannot be undone |

The reversibility axis is the one most often skipped, and it is the one that keeps an exercise safe. A pretext whose total success moves real money, deletes real data, or exposes a real credential has no safe failure mode. The canary reference exists to give it one.

## Themes That Are Refused Outright

Some pretexts work well and are still refused, because the finding is not worth what the scenario does to the person receiving it. Legal and safety review rejects themes built on health, family emergency, bereavement, layoffs or job security, immigration status, protected characteristics, real compensation figures, and law-enforcement threat.

These are not squeamishness. A bereavement pretext produces genuine distress in a person who has done nothing wrong, and the resulting finding — that a distressed employee bypassed a control — was predictable without the exercise. A layoff pretext damages trust in the security team for years and suppresses the reporting behaviour the programme depends on. The cost lands on the organisation long after the report is filed.

> [!tip] The analogy, and where it breaks
> A pretext works like a stage set: it needs only the side the audience can see, and building the back of the wall is wasted effort. The analogy breaks in one important way — a stage set is agreed with the audience, and a pretext is not. That missing consent is exactly why the review above exists, and why the operator carries an abort condition that a set designer does not.

## Synthetic Identity and Its Teardown

The identity the operator uses is created for the exercise and destroyed with it: a synthetic name, an organisation-controlled domain, a number the organisation holds, a landing page on infrastructure the organisation owns. Never a real third party's identity — impersonating a real named person or a real supplier's employee creates liability for someone outside the engagement who never agreed to any of it. The role is impersonated; the individual is not.

During execution, the record worth keeping is which process cues carried trust and which controls interrupted the scenario. That is the finding. At the end, the identity, domain, number, landing page and any collected material are retired on a stated date, and the teardown is recorded — an exercise domain left live after the report is a pretext someone else can pick up.

## Summary

You should now be able to:

- Explain why a pretext rides a business process rather than a personal dossier, and identify the process cues that make a request feel routine at a specific desk.
- Recognise the ratio that gives an attacking message away — too much about the recipient, too little about the procedure — and describe why depth on a person is both ineffective and a liability.
- Score a candidate pretext on plausibility, threat relevance, deception, privacy impact, distress and reversibility, and explain why full success must have a safe failure mode.
- Name the themes refused at review and explain the organisational cost of running them anyway; describe the synthetic-identity and teardown obligations that close an exercise.

---
> 🔼 Up: [[Human Factors & Pretext Development]]
