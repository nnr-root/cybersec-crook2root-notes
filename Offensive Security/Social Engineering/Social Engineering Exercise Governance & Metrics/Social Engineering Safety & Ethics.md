---
title: "Social Engineering Safety & Ethics"
aliases: ["SE Ethics", "Exercise Safety Case", "Social Engineering Authorisation"]
tags:
  - tree/offensive
  - cyber/offensive/social/safety
  - type/concept
  - difficulty/easy
  - level/novice
Domain: "[[Social Engineering Exercise Governance & Metrics]]"
Color: "#DC143C"
---

# ⚖️ Social Engineering Safety & Ethics

> [!abstract] Note of [[Social Engineering Exercise Governance & Metrics]]
> Every other kind of security testing is aimed at a machine. Social engineering is aimed at a person who did not agree to it, on behalf of an organisation that did. This note covers that consent asymmetry and what follows from it: the safety case, the themes refused regardless of authorisation, data minimisation by design, the stop condition, and why the ethical ceiling is also the practical one.

## Parent Learning Order
Social Engineering Safety & Ethics -> Human-Risk Metrics & Program Improvement

## Who Actually Consented

> *The client authorised a phishing exercise. Does that make every pretext acceptable?*
>
> Hold your answer — the section below is the response.

No, because the party that authorised the exercise is not the party the exercise happens to. Meridian Freight consented; the analyst on the finance desk at 16:40 on a Friday did not, and cannot, since an exercise announced to its participants measures nothing. The harm lands on someone who never agreed to it, and organisational authorisation does not transfer their consent — it was never the organisation's to give.

That asymmetry is the whole ethical structure of the discipline, and every rule below follows from it. It also fixes the direction of the burden: because participants cannot consent, the duty of care sits entirely with the people designing the exercise.

**The deliberate break:** a signed authorisation is treated as the thing that makes an exercise permissible — get the paperwork, and the scope is settled.

Authorisation establishes that the *organisation* accepts the exercise. It does not and cannot override employment law, privacy obligations, union agreements, accessibility needs, safeguarding duties, or a person's dignity, because none of those belong to the signatory either. A manager cannot authorise deception that would breach a works agreement, and a client cannot authorise the collection of a participant's real credentials. The signature is necessary and it is not sufficient — a scenario can be fully authorised, fully in scope, and still refused at review.

**How you'd spot it:** the tell is a scope document that lists systems and no people. If the authorisation names target hosts, target domains and a testing window, but says nothing about participant cohorts, prohibited themes, the stop authority or the support route, the exercise has been scoped as a technical test and the human dimension has not been considered at all. The second tell is a proposal with no named person holding stop authority — if nobody can end it, nobody has been made responsible for what it does.

## The Safety Case

Treat each exercise as a documented safety case rather than a plan. The structure is deliberately the same one used for physical work, because the question is the same: what could this hurt, and what catches it.

| Element | The question it settles |
| --- | --- |
| Participants and bystanders | Who is affected, including people not in the cohort |
| Plausible harms | Distress, reputational damage, financial loss, employment consequence |
| Existing safeguards | What already limits each harm |
| Residual risk | What remains after the safeguards, stated plainly |
| Decision owner | Who accepts that residual risk, by name |
| Stop authority | Who can end it instantly, and how they are reached |
| Support route | Where an affected participant goes, and who tells them |
| Post-exercise review | What is examined afterwards, and by whom |

Bystanders are the row most often left blank and most often the source of trouble. A vishing call to a shared line reaches whoever answers. A physical exercise is watched by staff who are not in the cohort and have no idea what they are seeing. A pretext referencing redundancies spreads through a team within the hour, entirely outside the exercise's boundary.

## Themes Refused Regardless of Authorisation

Some scenarios work well, and are refused because the harm is disproportionate to a finding that was usually predictable anyway.

| Refused theme | Why the finding is not worth it |
| --- | --- |
| Medical, or a family emergency | Produces genuine distress in someone who did nothing wrong |
| Job security, redundancy, disciplinary threat | Damages trust in the security team for years; suppresses reporting |
| Bereavement | Unpredictable severity; can reach real grief |
| Immigration status, protected characteristics | Discriminatory in effect regardless of intent |
| Real compensation figures, real financial loss | Causes actual harm rather than measuring a control |
| Law-enforcement threat | Coercive; may constitute an offence in some jurisdictions |
| Targeting personal accounts or personal devices | Outside the organisation's authority entirely |
| Real credential collection | A genuine breach, committed deliberately |

The common structure: each produces a result that was foreseeable without running it. That a frightened person bypasses a control is known. What the exercise was supposed to discover — whether the *process* holds under ordinary pressure — is measurable with a routine document-sharing pretext that harms nobody.

```text
Risk:        recipient believes their employment is threatened
Likelihood:  medium        Severity: high
Bystanders:  the recipient's team, who will hear about it within the hour
Decision:    reject scenario
Replacement: routine document-sharing invitation, harmless canary SE-TEST-171
Rationale:   tests the same verification control at a fraction of the harm
```

> [!tip] The analogy, and where it breaks
> Exercise ethics work like a clinical trial protocol: an independent review before anyone is exposed, a stated stop condition, and a named person who can halt it. The analogy breaks at the one place that should make testers more careful rather than less — a trial participant gives informed consent and an exercise participant cannot, since telling them destroys the measurement. Everything the consent step would have provided has to be supplied by the review instead.

## Data Minimisation by Design

The exercise generates a record of who failed a test. That record is the most sensitive artefact the programme produces, and the design goal is for it not to exist in identifiable form at all.

- **Synthetic credentials only.** No landing page has a password field. A real secret volunteered by a participant is discarded and reported, never recorded as evidence.
- **Opaque participant identifiers.** Analysis needs to distinguish participants, not to name them.
- **Aggregate reporting.** Findings name controls and workflows, never individuals.
- **Narrow retention with a stated deletion date**, and the deletion actually performed.
- **Encryption and role-limited access** to whatever raw material exists in the interim.

The practical test of the design: if the raw dataset leaked tomorrow, what would it do to the people in it? A well-designed exercise answers "very little", because the identifiable layer was never collected.

## The Stop Condition and Safeguarding

Operators need to know in advance what ends an exercise instantly, because the moment it happens is not the moment to be deciding. The exercise stops when a participant shows real distress; when anything real is about to move — money, credentials, access; when scope becomes ambiguous; when a genuine incident collides with the test; and when the stop authority says so, without needing a reason.

One category overrides everything, including the reporting structure of the engagement. If a participant discloses abuse, self-harm, fraud, a medical emergency or any other real crisis in the course of an exercise, the exercise is over and the organisation's established safeguarding process takes precedence immediately. That disclosure is not exercise data, is not written into the report, and is not the testers' to hold.

```text
Abort criteria — SE-TEST-171 (vishing)
  distress in the recipient's voice, at the operator's judgement
  request for a real credential, payment instrument or remote access
  any real transaction approaching an irreversible step
  disclosure of a personal crisis of any kind
  scope ambiguity the operator cannot resolve inside the call
  instruction from the stop authority
On abort: end the call courteously, notify the white cell within 5 minutes,
          debrief the recipient the same day, do not retry that recipient
```

## Debrief, and Non-Punitive Use

Debrief quickly — the same day where possible — and explain the control that was being tested, how the data will be used, and where support is available. A participant who learns weeks later that a stressful message was a test experiences it as having been watched, and the programme loses them.

The non-punitive commitment has to be written down and honoured, because the moment exercise results feed into performance management, the programme's own telemetry collapses. People stop reporting the messages they are unsure about, and those uncertain reports are the earliest signal the organisation has.

Ethical mastery is producing reliable security evidence with the least deception and the least harm — not making a scenario maximally convincing. The two goals are often assumed to be in tension; in practice the restrained scenario usually tests the process more cleanly, because it is not measuring how a person behaves while frightened.

## Summary

You should now be able to:

- Explain the consent asymmetry at the centre of social engineering testing, and why organisational authorisation is necessary but never sufficient.
- Assemble a safety case — participants and bystanders, harms, safeguards, residual risk, decision owner, stop authority, support route, review — and identify the elements most often left blank.
- Name the themes refused regardless of authorisation and the shared reason they are refused, and redesign a rejected scenario to test the same control at lower harm.
- State the abort criteria for a voice exercise, describe what happens when a participant discloses a real crisis, and explain why non-punitive use and data minimisation protect the programme's own measurements.

---
> 🔼 Up: [[Social Engineering Exercise Governance & Metrics]]
