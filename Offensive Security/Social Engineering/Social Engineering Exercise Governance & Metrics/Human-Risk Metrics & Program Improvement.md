---
title: "Human-Risk Metrics & Program Improvement"
tags: [tree/offensive, cyber/offensive/social/metrics, difficulty/medium]
Domain: "[[Social Engineering Exercise Governance & Metrics]]"
Color: "#DC143C"
---

# Human-Risk Metrics & Program Improvement

Metrics should measure systems: delivery-control performance, report rate/time, verification-process use, SOC triage, containment, repeat themes, and remediation—not shame individuals.

```mermaid
flowchart LR
    M["Exercise metrics"] --> G["Control/process gap"]
    G --> C["Change"]
    C --> R["Retest"]
```

Segment only where privacy and sample size allow. Click rate without delivery, difficulty, cohort, and reporting context is misleading.

## Parent Learning Order
Social Engineering Safety & Ethics -> Human-Risk Metrics & Program Improvement

## A Defensible Measurement Model

> *Your click rate fell from 12% to 3% over four quarters. What improved?*
>
> Hold your answer — the section below is the response.

There is no way to tell from those two numbers, and the honest answer may be nothing. Across four quarters the scenario difficulty changed, the channel changed, the cohort changed, and the proportion of messages the gateway delivered at all changed. Each of those moves the number on its own.

Separate the exercise funnel into attempted, delivered, blocked, opened, interacted, independently verified, reported, triaged, and contained. Denominators matter: interaction among delivered messages is different from interaction among all attempted messages. Report medians and distributions for time metrics; a single average hides delayed response.

| Metric | What it reveals | Misuse to avoid |
|---|---|---|
| Preventive-control rate | Mail, identity, or endpoint blocking | Treating non-delivery as user success |
| Median report time | Human sensing speed | Ignoring late but useful reports |
| Verification adherence | Process resilience | Ranking named individuals |
| Triage and containment time | Operational readiness | Excluding after-hours exercises |

**The deliberate break:** a trend line pointing downward is read as evidence of improvement, because that is what trend lines are for.

A time series requires that the thing being measured stays the same between points, and in this programme the measurer chooses the difficulty. A quarter-on-quarter decline is consistent with better controls, and equally consistent with easier lures, a gentler cohort, a higher block rate upstream, or a workforce that has memorised last quarter's wording. Without difficulty, channel, cohort and delivery rate recorded beside each number, the chart documents the exercise designer's choices rather than the organisation's resilience — and it documents them in a form that senior stakeholders will read as progress.

**How you'd spot it:** ask to see what is stored alongside each data point. A programme that can produce scenario difficulty, channel, cohort definition and delivery rate for every campaign has a comparable series; one that stores the percentage and the date does not, and the correct response to its trend line is to stop drawing it. The second tell is a metric with no owner attached — a number nobody is accountable for acting on is a number nobody has interrogated.

Use minimum cohort sizes, role-based aggregation, fixed retention, and access controls. Track scenario difficulty, channel, exposure duration, and control changes so trends are comparable. Every metric must connect to an owner and intervention—technical control, process redesign, training, or playbook update. Retest the threat hypothesis rather than repeating an identical lure. Improvement means fewer unsafe process outcomes and faster collective response, not simply a lower click percentage.

## Worked Example: The Denominator Decides the Story

A phishing exercise produces the same raw numbers no matter who reports them; what
changes the conclusion is which denominator the "click rate" is computed against.
Running the same campaign figures two ways shows how a reassuring number and an
alarming one come from identical data.

```python
attempted, delivered, clicked, reported = 5000, 3200, 480, 210
print(f"click rate / ATTEMPTED : {100*clicked/attempted:.1f}%")
print(f"click rate / DELIVERED : {100*clicked/delivered:.1f}%")
print(f"report rate / DELIVERED: {100*reported/delivered:.1f}%")
print(f"report:click ratio     : {reported/clicked:.2f}")
```

```shell-session
$ python3 metrics.py
attempted=5000 delivered=3200 clicked=480 reported=210
click rate / ATTEMPTED : 9.6%   (looks reassuring)
click rate / DELIVERED : 15.0%   (the real human-failure rate)
report rate / DELIVERED: 6.6%   (the resilience signal)
report:click ratio     : 0.44   (>1 is the goal)
```

The first two lines are the same 480 clicks. Divided by everything *attempted*, the
click rate is a comfortable 9.6%; divided by what was actually *delivered* to an
inbox, it is 15%. The gap is the 1,800 messages the mail gateway blocked — and
folding those into the denominator credits the *technical control* to the *humans*,
making people look better than they are. The delivered denominator is the honest
one for a human-risk metric, because a person can only fail to resist a message they
received.

The report metric matters more than the click metric, and the last line says why.
A report:click ratio of 0.44 means fewer people reported the phish than fell for
it — the population has no working immune response. The goal is a ratio above 1,
where reporting outpaces clicking, because a reported phish is a defended one:
detection and response begin. A program that optimises only the click rate can drive
it down while the report rate stays flat and never learn that its users still cannot
recognise or escalate an attack.

This is the measurement discipline the note argues for. Every rate needs its
denominator stated, time metrics need medians and distributions rather than a
single average that hides the slow responders, and the metric that predicts
resilience — reporting — must be tracked alongside the metric that measures failure.
A dashboard that shows click rate alone, against an unstated denominator, is not
measuring human risk; it is producing a number that can be made to say anything.

## Summary

You should now be able to:

- Explain why "compromise rate" carries more information than "click rate".
- Prioritise a single programme change from a set of exercise numbers, and specify the retest that proves it worked.
- Explain how to trend human-risk metrics over time without gaming (e.g. easier lures inflating improvement) and how to tie them to real incident reduction.

---
> 🔼 Up: [[Social Engineering Exercise Governance & Metrics]]
