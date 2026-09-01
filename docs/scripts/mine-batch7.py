#!/usr/bin/env python3
"""Offensive Security worked examples — batch 7 (Network Pentesting)."""
import re
import sys

L23 = '''## Worked Example: Poisoning a Neighbour Table With One Forged Reply

A layer-2 on-path position does not require breaking anything. It requires the
switch and the victim to believe a claim that ARP was never designed to verify.
This walks a single forged reply on a real switched segment, built from Linux
bridges and namespaces.

**The baseline.** The victim has resolved the gateway to its genuine MAC:

```shell-session
root@lab:~$ ip netns exec victim ping -c1 10.20.0.1 >/dev/null
root@lab:~$ ip netns exec victim ip neigh show 10.20.0.1
10.20.0.1 dev in-victim lladdr 4a:1b:2c:3d:4e:5f REACHABLE
```

`REACHABLE`, and pointing at the gateway's real hardware address. This is the
entry the attack overwrites.

**The attack** is one gratuitous ARP reply announcing "10.20.0.1 is at my MAC",
sent from the attacker namespace:

```shell-session
root@lab:~$ ip netns exec attacker python3 forge_arp.py 8a:9b:ac:bd:ce:df
forged ARP sent: 10.20.0.1 -> attacker MAC 8a:9b:ac:bd:ce:df
```

The reply is unsolicited — the victim never asked. ARP has no state machine that
requires a reply to match a request, and no authentication on the reply's
contents, so an announcement arriving out of nowhere is accepted as readily as
one that answers a question.

**The finding:**

```shell-session
root@lab:~$ ip netns exec victim ip neigh show 10.20.0.1
10.20.0.1 dev in-victim lladdr 8a:9b:ac:bd:ce:df STALE
```

The gateway's address in the victim's table is now the attacker's MAC. Every
packet the victim sends to its default gateway will be framed to the attacker
instead — the on-path position, established with one packet and zero
interception so far.

Two points of discipline matter here. First, the finding is the *poisoned table*,
not captured traffic: proving the attacker now sits in the path is the deliverable,
and actually capturing a victim's data is a separate, higher-consent step. Second,
this is exactly what Dynamic ARP Inspection defeats — on a switch with DAI, the
forged reply in the attack step is dropped because it does not match a DHCP
snooping binding, and this final command would still show `4a:1b:2c:3d:4e:5f`.
Running the attack against a DAI-enabled switch and seeing the entry *not* change
is how you evidence that the control works.

'''

INTERNAL = '''## Worked Example: Testing Whether Segmentation Is Real or Decorative

A network diagram claims two segments are separated. Internal pentesting does not
trust the diagram — it puts a foothold in one segment and tries to reach the
other, before and after the control exists. Two namespaces joined by a forwarding
router stand in for the two segments.

**Before any control**, a foothold in segment A reaches a service in segment B:

```shell-session
root@lab:~$ ip netns exec seg-a curl -s -o /dev/null -w "seg-a -> seg-b:80 = HTTP %{http_code}\\n" http://10.2.0.10:80/
seg-a -> seg-b:80 = HTTP 200
```

`HTTP 200`. The segments are routable to each other with nothing in between, so
the separation on the diagram is decorative — a foothold anywhere is a foothold
everywhere. On a flat network this one line is the whole finding.

**After a real boundary** is placed on the router:

```shell-session
root@lab:~$ ip netns exec router iptables -A FORWARD -s 10.1.0.0/24 -d 10.2.0.0/24 -j DROP
root@lab:~$ ip netns exec seg-a curl -s --max-time 3 http://10.2.0.10:80/ || echo "seg-a -> seg-b = BLOCKED"
seg-a -> seg-b = BLOCKED
```

The boundary holds. The value of testing it empirically — rather than reading the
firewall config and assuming — is that a rule can exist and still not apply: wrong
interface, wrong direction, shadowed by an earlier `ACCEPT`, or bypassed by a
route the config author forgot. The before/after pair is the evidence that
containment is real, and it is the single most useful artefact an internal test
produces about a segmentation claim.

**The caveat that makes findings good.** The block above stops packets from A to
B, and stops nothing about *identity*. If a credential harvested in segment A also
authenticates in segment B, and any management path reaches across — a jump host,
a shared admin console, a domain controller both segments trust — then the attacker
moves without ever sending a packet the firewall would see. That is why a strong
internal finding is never "the segments are flat" but a named path: *this*
boundary, crossed with *this* reused credential, over *this* service. The report's
value is the path, because the path is what the defender fixes.

'''

WORK = {
    "Offensive Security/Penetration Testing/Network Penetration Testing/Layer 2 & 3 Network Attacks.md": L23,
    "Offensive Security/Penetration Testing/Network Penetration Testing/Internal Network Pentesting.md": INTERNAL,
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
