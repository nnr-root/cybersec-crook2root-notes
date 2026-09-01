#!/usr/bin/env python3
"""Offensive Security — batch 17 (conceptual notes: worked mappings).

These four notes had a reader-tasking 'Practical Exercise' that survived the
migration. Each is replaced with a completed 'Worked Mapping' — the analytical
artifact filled in, demonstrating the skill rather than assigning it. That both
removes the reader-tasking framing and provides the worked example these notes
were missing. A worked mapping is the honest form of 'example' for a framework
note; a shell command would be cargo-cult.
"""
import re
import sys

KILLCHAIN = '''## Task 4 — Worked Mapping: An Engagement Across the Chain

The kill chain earns its keep as a reporting language: it places every action of an
assessment on a shared timeline and names, for each, the control that would have
broken it. Here is a completed mapping for one authorized engagement — the artifact
a report delivers, not an exercise to attempt.

| Stage | What the assessment did / observed | Control that breaks this link | Client status |
|:--|:--|:--|:--|
| Reconnaissance | Employee emails found via OSINT; an admin panel exposed to the internet | Reduce public info; alert on scan patterns; remove the exposure | **gap** — panel was reachable |
| Weaponisation | Prepared a benign macro-bearing document (canary payload) | Block or restrict Office macros by policy | present — macros restricted |
| Delivery | Sent a simulated phish to 40 scoped users | Mail filtering; user reporting culture | partial — 6 delivered, 2 clicked |
| Exploitation | Macro would have run on click | Attack-surface reduction; least privilege | present — no admin on endpoints |
| Installation | Persistence would be attempted here | EDR; application allowlisting | present — EDR blocked the test binary |
| Command & Control | Beacon to an external redirector | Egress filtering; beacon-cadence detection | **gap** — outbound HTTPS unrestricted |
| Actions on Objectives | Scoped goal: reach a canary data store | Segmentation; least privilege; DLP | **gap** — flat internal network |

Read across the "client status" column and the finding writes itself in the language
an executive acts on: *the chain can already be broken at weaponisation, delivery and
installation, so the controls there are working; the exposures are the exposed panel
at recon, unrestricted C2 egress, and a flat internal network at the objective.* Three
named links to fix, each tied to a control the client either has or lacks.

That framing is the whole reason to map to the chain rather than list findings
severity-first. A severity list says "three highs, five mediums"; a kill-chain map
says "you stop the attacker in three places and miss them in three others, and here
is which." One is a scorecard; the other is a defensive plan, and the layered nature
of the chain is exactly what lets a defender who cannot fix everything choose the link
that costs the attacker the most.

'''

FUNDAMENTALS = '''## Task 14 — Worked Mapping: A Finding Driven to a Risk Decision

The reasoning this domain builds toward is turning a technical fact into a business
decision a stakeholder can own. Here that reasoning is carried out in full for two
findings — one that must be fixed and one that may rationally be accepted — as the
worked artifact a report contains.

| Step | High-risk finding | Low-risk finding |
|:--|:--|:--|
| Vulnerability | `/api/invoice/{id}` returns any invoice without checking ownership | The server response includes a precise version banner |
| Threat | Any authenticated low-privilege user changes `{id}` | An attacker fingerprints the version to look up known CVEs |
| Impact | Exposure of all customers' financial data → regulatory + reputational | Marginal — speeds recon slightly; no direct access |
| Likelihood | Trivial — no special access, just increment the ID | Low value — banner alone grants nothing |
| **Risk** | **High** (high impact × high likelihood) | **Low** (low impact × low leverage) |
| Decision | **Mitigate** — enforce object-level authorization server-side | **Accept** — patch on the normal cycle; note in the report |
| Retest | Request another user's invoice ID → expect `403`; own invoice still `200` | None required — informational |

The two rows exist to make one point: a risk rating is a defensible argument, not a
scanner's label. The high finding is high because impact and likelihood are both high,
and the recommendation is to enforce authorization server-side rather than hide the ID
— because hiding the identifier addresses neither the impact nor the likelihood. The
banner is low because, argued honestly to a skeptical stakeholder, it grants an
attacker nothing on its own; an organisation can rationally accept it and spend the
remediation budget on the invoice endpoint instead.

The mastery signal the note names is exactly this: being able to defend both the rating
*and* the decision — including the decision to accept — to someone who will be
accountable for it. A finding that cannot be driven to a decision a stakeholder can
own is not yet a finding; it is a bug report.

'''

STANDARDS = '''## Task 7 — Worked Mapping: Framework Selection for One Engagement

Frameworks are chosen and blended per engagement, not recited. Here is a completed
methodology decision for a concrete scope — an external and web assessment of a UK
fintech that stores payment data and must satisfy an auditor — as it would appear in
the statement of work.

| Decision | Choice for this engagement | Why |
|:--|:--|:--|
| Lifecycle spine | **NIST SP 800-115** | A regulated, audited client — the auditor recognises NIST language over PTES's |
| Web coverage | **OWASP WSTG** — auth, session, input validation, access control, configuration | Names the exact app categories the payment surface requires; maps cleanly to findings |
| Measurement | **OSSTMM-style metrics**, selectively | Makes next year's test comparable; accept the added time cost for a recurring regulated client |
| Assurance constraint | **CREST-accredited delivery**, recorded in the SOW | The client requires it; it is a delivery constraint, not a testing method |
| Decision log | A standing note recording every phase transition and its rationale | The auditor will ask *why* each choice was made, not merely *what* was tested |

The point of the blend is that no single framework covers a real engagement. NIST gives
the auditor-legible lifecycle; WSTG gives the web-specific depth NIST lacks; OSSTMM adds
comparability the others do not measure; CREST is an assurance requirement orthogonal to
all of them. Each is named for *what it is doing in this engagement* — a spine, a coverage
checklist, a metric, a constraint — rather than listed for completeness.

The mastery signal the note identifies is the ability to justify each choice to the
auditor: NIST because you are audited, WSTG because the risk is in the web tier, OSSTMM
because the test recurs. Naming all five frameworks proves nothing; explaining why this
engagement uses these three in these roles is the competence a methodology section
demonstrates.

'''

REDTEAM = '''## Task 6 — Worked Mapping: A Campaign Plan and Its Behaviour Matrix

A red-team operation starts from two artifacts precise enough that the white team could
run it and the blue team could be scored from them alone. Here both are completed for one
scenario — a fintech worried about contractor-credential abuse — as the operation would
begin.

**The campaign plan:**

| Element | This operation |
|:--|:--|
| Objective (measurable) | Determine whether a contractor identity can reach `ENG-CANARY-REPO`, and whether the SOC detects the path within the exercise window |
| Adversary profile | Malicious contractor / supply-chain foothold |
| Initial access | Assumed breach — supplied contractor credentials |
| Safety rails | Canary payloads only; revoke plan for the test identity; excluded cohorts named; stop phrase agreed |
| Stop conditions | Authenticated stop phrase, white-team contact reachable, any real customer data touched halts the op |

**The behaviour matrix** — each emulated technique with its detection criterion:

| ATT&CK technique | Expected telemetry | Pass / detect criterion |
|:--|:--|:--|
| T1078 Valid Accounts (initial) | Contractor login from a new device/location | SOC flags anomalous contractor logon |
| T1087 Account Discovery | Directory/role enumeration by a contractor identity | Alert on enumeration volume |
| T1003 Credential Access | Attempt to read a secret store | EDR/DLP flags the access |
| T1021 Lateral Movement | Auth to a system outside contractor scope | Segmentation blocks or SOC detects |
| T1213 Collection | Access to `ENG-CANARY-REPO` | Canary-repo access fires a honeytoken alert |

The two artifacts together are the operation's contract. The plan fixes what "success"
means in advance — a specific canary reached, detection within a specific window — so the
result is a measured outcome rather than a story. The matrix turns each attacker action
into a testable question for the defenders: for every technique, what should the SOC have
seen, and did they. That is what makes a red-team engagement scoreable rather than merely
narrated, and it is why an operation planned this way produces a detection-coverage finding
the blue team can act on, exactly like the ATT&CK coverage map in the methodology branch.

'''

WORK = {
    "Offensive Security/Penetration Testing/Methodologies & Frameworks/Cyber Kill Chain.md":
        ("Task 4 — Practical Exercise: Map an Engagement to the Chain", KILLCHAIN),
    "Offensive Security/Penetration Testing/Methodologies & Frameworks/Penetration Testing Fundamentals.md":
        ("Task 14 — Practical Exercise: Turn a Finding into a Risk Story", FUNDAMENTALS),
    "Offensive Security/Penetration Testing/Methodologies & Frameworks/Penetration Testing Standards & Frameworks.md":
        ("Task 7 — Practical Exercise: Choose and Blend Frameworks for an Engagement", STANDARDS),
    "Offensive Security/Red Team Operations/Red Team Campaign Planning & Initial Access.md":
        ("Task 6 — Practical Exercise: Plan a Campaign and Its Initial Access", REDTEAM),
}

NEXT_H2 = re.compile(r"^## ", re.M)


def main():
    apply = "--apply" in sys.argv
    for rel, (old_heading, new_section) in WORK.items():
        try:
            src = open(rel, encoding="utf-8").read()
        except FileNotFoundError:
            print(f"  MISSING  {rel}")
            continue
        marker = "## " + old_heading
        i = src.find(marker)
        if i == -1:
            print(f"  ✗ heading not found: {rel}")
            continue
        # the exercise runs to the next H2 (## Summary)
        j = NEXT_H2.search(src, i + len(marker))
        end = j.start() if j else len(src)
        out = src[:i] + new_section.rstrip() + "\n\n" + src[end:]
        out = re.sub(r"\n{3,}", "\n\n", out)
        print(f"  ✓ replaced exercise -> worked mapping  {rel.split('/')[-1]}")
        if apply:
            open(rel, "w", encoding="utf-8").write(out)
    print(f"\n{'APPLIED' if apply else 'DRY RUN'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
