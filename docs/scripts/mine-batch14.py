#!/usr/bin/env python3
"""Offensive Security worked examples — batch 14 (methodology & reporting)."""
import re
import sys

ATTACK = '''## Worked Example: Turning Findings Into a Coverage Heatmap

Mapping findings to MITRE ATT&CK is not documentation for its own sake — it turns
a list of things that worked into a measurement of what the defender's controls
caught, in a format the blue team can act on directly. Five findings, each tagged
with a technique and an outcome, make the workflow concrete.

**Findings recorded as technique procedures**, not prose:

```text
finding,tactic,technique_id,technique,detected
F-01,Initial Access,T1566.001,Spearphishing Attachment,blocked
F-02,Credential Access,T1003.001,LSASS Memory,detected
F-03,Lateral Movement,T1550.002,Pass-the-Hash,missed
F-04,Persistence,T1053.003,Cron Job,detected
F-05,Exfiltration,T1048,Exfil Over Alternative Protocol,missed
```

Each row carries the technique ID and — the column that makes this an assessment
rather than a diary — whether the client's controls caught it.

**Scoring the coverage** reduces five rows to the number that matters:

```shell-session
analyst@lab:/tmp/attack-lab$ python3 score.py
techniques emulated : 5
blocked/detected    : 3  (60% coverage)
MISSED (gaps)       : 2
--- gaps to fix ---
  T1550.002  Pass-the-Hash  (Lateral Movement)
  T1048      Exfil Over Alternative Protocol  (Exfiltration)
```

Sixty percent coverage, and — more useful than the percentage — the two specific
techniques that went unseen, named by ID and tactic. That is a remediation backlog,
not a grade: the blue team knows exactly which two detections to write.

**Emitting a Navigator layer** puts it in the tool the defenders already use:

```shell-session
analyst@lab:/tmp/attack-lab$ python3 layer.py
wrote coverage.layer.json -> 5 techniques (importable into ATT&CK Navigator)
```

The JSON colours each technique green or red on the standard ATT&CK matrix, so a
defender sees the engagement as a heatmap over the same framework their detections
are organised around. This is what makes the finding durable: not "the pentest
found some gaps" but a technique-by-technique coverage map that the blue team
imports, closes two cells on, and re-tests against next quarter — the whole purpose
of framing offensive results in ATT&CK rather than in an ad-hoc list.

'''

RETEST = '''## Worked Example: When "Fixed" Is Not Fixed

A retest exists to answer one question — was the vulnerability actually
remediated — and a naive retest answers a weaker one: does the exact proof from the
report still work. The gap between those two is where superficial fixes hide. One
app with three modes — vulnerable, superficially patched, and properly patched —
shows why variant testing is the whole job.

**The original vulnerability**, confirmed as a baseline:

```shell-session
analyst@lab:~$ python3 app.py vuln
vuln        | probe="' OR '1'='1"  -> CANARY-SECRET
vuln        | probe="' OR 'a'='a"  -> CANARY-SECRET
```

Both tautologies leak the secret — a working SQL injection.

**The superficial fix, tested naively**, looks remediated:

```shell-session
analyst@lab:~$ python3 app.py superficial | head -1
superficial | probe="' OR '1'='1"  -> blocked
```

The exact string from the report is now blocked. A retest that replays only the
original proof-of-concept stops here, marks the finding closed, and is wrong.

**The same fix, tested with a variant**, exposes it:

```shell-session
analyst@lab:~$ python3 app.py superficial | tail -1
superficial | probe="' OR 'a'='a"  -> CANARY-SECRET
```

A one-character change — `'1'='1'` to `'a'='a'` — sails straight through, because
the fix blocked a *string* rather than the *behaviour*. The vulnerability class is
fully intact; only the specific payload in the report was patched. Closing this
finding would leave the client exactly as exposed as before, with a report that
says otherwise.

**The root-cause fix** holds against both:

```shell-session
analyst@lab:~$ python3 app.py rootcause
rootcause   | probe="' OR '1'='1"  -> no results
rootcause   | probe="' OR 'a'='a"  -> no results
```

Parameterisation treats input as data that is never interpreted, so neither the
original nor any variant is a query any more. The class is closed, not the payload.

This is the discipline a retest enforces: a finding is remediated when the
*vulnerability class* is closed at its root, verified with variants the original
report never listed — not when the one proof-of-concept string stops working.
Distinguishing a superficial fix from a real one is the single most valuable thing
a retest delivers, because a falsely-closed finding is more dangerous than an open
one: the client has stopped worrying about it.

'''

ROE = '''## Worked Example: Evidence That Survives a Challenge

An engagement's findings are only as defensible as the evidence behind them, and
defensibility comes from a chain of custody that can prove a piece of evidence is
unaltered. Hashing an artifact on collection and verifying it later turns "trust
us" into "here is the proof."

**Register the evidence with its hash at collection time:**

```shell-session
analyst@lab:/tmp/engagement$ sha256sum evidence/F-07-request.txt | awk '{print $1}'
9c1f...4ab2
analyst@lab:/tmp/engagement$ cat evidence-register.csv
id,collector,utc,source,method,sha256,classification,custodians,disposition
F-07,analyst,2026-08-09T14:22:07Z,api.example.test,manual-request,9c1f...4ab2,restricted,lead+reviewer,delete+30d
```

The register binds the artifact to who collected it, when, from where, by what
method, and — the anchor — its hash at the moment of collection. Everything else in
the row is context; the hash is what makes the record provable.

**An untampered working copy verifies against the register:**

```shell-session
analyst@lab:/tmp/engagement$ echo "9c1f...4ab2  evidence/F-07-working.txt" | sha256sum -c -
evidence/F-07-working.txt: OK
```

`OK` means the working copy is byte-for-byte the evidence that was registered — so
analysis, redaction and reporting can proceed from it while the original stays
sealed.

**Any alteration is detectable:**

```shell-session
analyst@lab:/tmp/engagement$ echo "TAMPERED" >> evidence/F-07-working.txt
analyst@lab:/tmp/engagement$ echo "9c1f...4ab2  evidence/F-07-working.txt" | sha256sum -c -
evidence/F-07-working.txt: FAILED
```

`FAILED` is the property that makes the chain worth maintaining. A single appended
line breaks the hash, so any modification — accidental or malicious, by the tester
or by anyone who later handles the file — is caught against the collection-time
anchor. This is what lets a finding withstand a client disputing it: the evidence
is provably the same as when it was gathered.

The final link is disposition. The register's `delete+30d` field is a commitment,
and honouring it — destroying restricted evidence on schedule, logged before
deletion — is as much a part of the engagement's integrity as gathering it. Scope
defines what you were authorised to touch; chain of custody proves what you found
was real and that you handled it responsibly from collection to destruction.

'''

WORK = {
    "Offensive Security/Penetration Testing/Methodologies & Frameworks/Threat Modeling & MITRE ATT&CK.md": ATTACK,
    "Offensive Security/Penetration Testing/Reporting & Purple Teaming/Retesting, Closure & Lessons Learned.md": RETEST,
    "Offensive Security/Penetration Testing/Methodologies & Frameworks/Rules of Engagement & Scoping.md": ROE,
}

ANCHOR = re.compile(r"^## Task \d+ — (Failure Modes|Security Implications|Detection|Defen|Reporting|Lessons)", re.M)
SUMMARY = re.compile(r"^## Summary\s*$", re.M)
ANY_TASK = re.compile(r"^## Task \d+ — (.*)$", re.M)


def main():
    apply = "--apply" in sys.argv
    for rel, sec in WORK.items():
        try:
            src = open(rel, encoding="utf-8").read()
        except FileNotFoundError:
            print(f"  MISSING  {rel}")
            continue
        m = ANCHOR.search(src) or SUMMARY.search(src)
        if not m:
            print(f"  ✗ NO ANCHOR  {rel}")
            continue
        out = src[:m.start()] + sec + src[m.start():]
        out = out.replace("## Worked Example:", "## Task 0 — Worked Example:", 1)
        n = [0]

        def renum(mm):
            n[0] += 1
            return f"## Task {n[0]} — {mm.group(1)}"

        out = ANY_TASK.sub(renum, out)
        print(f"  ✓ {n[0]} tasks  {rel.split('/')[-1]}")
        if apply:
            open(rel, "w", encoding="utf-8").write(out)
    print(f"\n{'APPLIED' if apply else 'DRY RUN'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
