---
title: "Finding & Report Writing"
aliases:
  - Technical Finding Writing
  - Executive Reporting & Attack Narratives
  - Report Writing
  - Attack Narratives
tags:
  - tree/offensive
  - cyber/offensive/reporting
  - type/concept
  - difficulty/medium
Domain: "[[Reporting & Purple Teaming]]"
Color: "#DC143C"
---

# ✍️ Finding & Report Writing

> [!warning] The report is the deliverable
> Everything you did on the engagement is worthless if the report doesn't drive a fix. Write for two audiences at once — engineers who must reproduce and fix, and executives who must decide and fund — using only *verified* language for what you actually demonstrated.

## Parent Learning Order
Evidence & Risk Prioritization -> Finding & Report Writing -> Purple Team Exercise Design -> Retesting, Closure & Lessons Learned

## Two Readers, One Truth

A penetration test produces exactly one durable artifact: the report. It has to serve two very different readers from the *same* set of verified facts. The **technical finding** is written for an engineer who must reproduce the issue and fix its root cause. The **executive summary and attack narrative** are written for a decision-maker who must understand business exposure and allocate budget. This note covers both crafts, because the skill is *translation* — turning the evidence and priorities from the previous leaf into a technical ticket an engineer can act on *and* a narrative a CISO can decide on, without exaggeration and without drowning either reader in the wrong detail.

The unifying discipline across both: **separate confirmed fact from inference, and never claim beyond demonstrated reach** — use "demonstrated," "observed," "inferred," and "not tested" precisely.

> [!tip] The analogy, and where it breaks
> Writing a report is like a building surveyor producing two documents from one inspection: a detailed repair spec for the contractor (which beam, what fix, how to verify) and a one-page risk letter for the owner (the house is sound except the roof, fix it before winter, here's the cost). The analogy breaks on adversarial framing: a surveyor describes passive decay, whereas you must describe an *active attacker's path* — so the executive document is a chronological *story* of how a threat reaches the crown jewels, not just a list of defects.

**Prerequisites:** **Evidence & Risk Prioritization** (the report presents that evidence and ranking); **Penetration Testing Fundamentals** (the risk vocabulary).

**The deliberate break:** the report documents what you did. Write up the exploit, attach the proof, rank it by severity, and the engagement is delivered.

The client is not buying a record of your work — they are buying **decisions they can act on**, and the exploit is the least useful part of that. What makes a finding actionable is the *root cause* (why it exists, so it is not merely patched here and left everywhere else), the *business impact* (what an attacker gains, in terms the person funding the fix understands), and the *specific remediation*. A finding with a payload and none of those three is a scanner export with a narrative.

There are also two readers with different needs, and writing for one fails the other: the engineer needs reproduction detail, the executive needs the risk decision. Neither is served by a document that splits the difference.

**How you'd spot a weak finding:** it describes what you sent and what came back, and never says why the application allowed it. If the fix cannot be inferred from the finding, the analysis is still missing.

## The Technical Finding: Anatomy

A defensible finding connects **condition → evidence → impact → root cause → fix → retest**. Include: precise title, affected assets and versions, prerequisite identity, the violated security invariant, reproducible steps, observed *and expected* results, minimum proof, business impact, likelihood factors, root cause, compensating controls, remediation (naming the control layer), detection opportunity, cleanup, and retest criteria.

```text
Title    : Cross-tenant invoice access (broken object-level authorization)
Invariant: a tenant may read only objects it owns
Observed : Tenant A test user received Tenant B canary invoice metadata (HTTP 200)
Expected : HTTP 403/404
Root cause: object lookup omits tenant predicate in the export worker
Fix      : centralized tenant-bound repository query + authorization tests
Closure  : predicate covers synchronous AND queued export paths
```

**Lead with the condition and consequence, not the tool or payload.** Give enough sanitized request/response detail for an engineer to reproduce. Recommendations must name the *control layer and verification* — "sanitize input" or "apply least privilege" is not actionable. Record environmental constraints and *failed* variants so severity isn't exaggerated.

## The Executive Report: Translate, Don't Dump

Executives need: the tested objective, material exposure, the *pattern* of control weakness, the affected business capability, the plausible consequence, and prioritized decisions. **Do not turn every technical finding into an executive theme** — group issues into root causes (fragmented identity governance, inconsistent authorization, weak segmentation, incomplete telemetry).

```mermaid
flowchart LR
    E["Entry condition"] --> B["Control boundary crossed"]
    B --> O["Business objective reached"]
    O --> C["Consequence"]
    C --> D["Decision & owner"]
```

The **attack narrative** is chronological and evidence-backed: initial condition → decisions → controls that worked → controls that failed → achieved privilege → bounded proof → detection response → cleanup. **Include the paths that were *prevented*** so the client sees where their investment paid off. Close with a 30/60/90-day roadmap tied to accountable owners. One good narrative shows how *several medium findings combine* into material impact — the whole point that a severity tally misses.

## The difference between a report and a scanner export

- **Payload-only findings.** A report that shows the exploit but not the root cause, business impact, or actionable fix is a scanner export, not an assessment.
- **Exaggerated impact.** Claiming reach you didn't demonstrate destroys credibility and can misdirect remediation. Use verified language and state what was *not* tested.
- **Averaging / counting.** "3 highs, 12 mediums" is not a posture; executives need the *attack path and consequence*, not arithmetic on severities.
- **One-theme-per-finding at the exec level.** Flooding leadership with 40 items instead of 5 root causes buries the decisions that matter.
- **Generic remediation.** "Apply least privilege" without naming the control layer and verification is not something an engineer can implement or a retest can confirm.

## Security Implications — the Defender's View

- **Root-cause framing drives systemic fixes:** grouping findings into patterns (e.g. "authorization is enforced inconsistently across services") gets the *class* fixed, not just individual instances — the highest-leverage outcome of a report.
- **Actionable technical findings feed straight into engineering workflows:** a finding written as a reproducible ticket with a named control layer becomes a tracked fix and a regression test, not a debate.
- **Recognizing prevented paths** rewards effective controls and helps the defender keep funding what works — a report that only lists failures gives a distorted picture.
- **A 30/60/90 roadmap with owners** converts a document into an accountable program, which is what actually reduces risk over time.

## Practical Exercise: Rewrite a Scanner Finding into Both Forms

> [!info] No shell needed — writing is the skill. Produce both deliverables from one raw finding.

Take a raw, low-value finding (as a scanner would emit it) and produce the two report forms:

1. **Raw input:** `"SQL Injection detected on /search?q= (High)."`
2. **Write the technical finding** with full anatomy: affected asset+version, the exact reproducing request, observed vs expected, a *canary* proof (not real data), root cause (string-concatenated query), a control-layer fix (parameterized queries + a regression test), detection opportunity, and retest criteria.
3. **Write two sentences of executive narrative:** the business consequence (e.g. "an unauthenticated user could read the customer database") grouped under the root-cause theme "inconsistent input handling in legacy search services," with the decision ("prioritize the search-service refactor in the next 30 days").
4. **Audit your own language:** highlight every claim and label it demonstrated / observed / inferred / not-tested. Remove or hedge anything you can't back with evidence.

Deliverable: one engineer-actionable ticket + one executive paragraph from the same finding. The mastery signal is that the engineer could fix it and the executive could decide on it — without either needing the other's document.

## Summary

You should now be able to:

- Explain why the report is the deliverable and why it must serve engineers and executives from the same verified facts.
- Write a technical finding with full anatomy (condition→evidence→impact→root cause→fix→retest) and an executive attack narrative, using precise verified language.
- Explain why root-cause grouping (not per-finding themes or severity tallies) drives systemic fixes, why prevented paths belong in the report, and how a 30/60/90 owner-mapped roadmap turns a document into an accountable program.

---
> 🔼 Up: [[Reporting & Purple Teaming]]
