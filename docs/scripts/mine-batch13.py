#!/usr/bin/env python3
"""Offensive Security worked examples — batch 13 (OPSEC + WPA2)."""
import re
import sys

OPSEC = '''## Worked Example: Off-Host Logging Defeats the Log-Tampering It Records

Anti-forensics and the defence against it are the same subject seen from two
sides, and the deciding factor is *where* the evidence lives. An operation log, a
hash recorded off-host, and a simulated tamper make the principle concrete.

**Preserve the record off-host first**, before anything can touch it:

```shell-session
operator@lab:/tmp/rt-lab$ sha256sum operation.log | tee offhost-evidence.sha256
7f3a...c21e  operation.log
```

That hash is the off-host copy's fingerprint, taken while the log is still
pristine. In a real operation the log itself is shipped to separate infrastructure
as it is written; here the hash stands in for that shipped, immutable copy.

**Tamper with the on-host log** the way an attacker covering tracks would —
timestomping an entry to move it outside the window defenders will examine:

```shell-session
operator@lab:/tmp/rt-lab$ sed -i 's/10:00:00Z/03:00:00Z/' operation.log
operator@lab:/tmp/rt-lab$ sha256sum -c offhost-evidence.sha256
operation.log: FAILED
```

`FAILED` is the detection. The on-host log no longer matches the fingerprint taken
before the tamper, so the alteration is not merely suspected — it is proven against
an independent record the attacker could not reach. This is the whole argument for
real-time off-host logging: an attacker who controls the host can rewrite anything
on it, but cannot rewrite what already left. Local logs establish nothing an
attacker with local privilege could not have forged; the copy shipped elsewhere is
the evidence.

**Teardown is driven by an inventory, and verified independently:**

```shell-session
operator@lab:/tmp/rt-lab$ while read a; do rm -f "$a"; done < inventory.txt
operator@lab:/tmp/rt-lab$ while read a; do [ -e "$a" ] && echo "STILL PRESENT: $a"; done < inventory.txt; echo "checked"
checked
```

Nothing printed before `checked`, so every tracked artifact is gone — confirmed by
re-checking the inventory rather than trusting that the `rm` loop ran. This is the
operational discipline the note argues for: track every artifact you create,
remove them from that tracked list at teardown, and verify the removal against the
list. The distinction from an attacker's anti-forensics is intent and direction —
the operator's logs and evidence are *delivered* to the client, never destroyed;
only the operational infrastructure is torn down, and the record of what was done
is the deliverable.

'''

WPA2 = '''## Worked Example: WPA2 Is Not Broken — Weak Passphrases Are

The offline half of a WPA2-PSK attack can be reproduced with no radio at all,
because once a handshake is captured the rest is pure computation: derive the key
the passphrase would produce and compare. Doing it against two passphrases —
weak, then strong — isolates the one variable that actually decides the outcome.

**The derivation** is WPA2's own key schedule: PBKDF2-HMAC-SHA1, the SSID as salt,
4096 iterations:

```python
def pmk(p):
    return hashlib.pbkdf2_hmac("sha1", p.encode(), SSID.encode(), 4096, 32)

target = pmk("Summer2024")           # the PMK a captured handshake reveals
for w in ["password", "letmein", "CorpWiFi123", "Summer2024", "Winter2025"]:
    print(w, "CRACKED" if pmk(w) == target else "")
```

**Against a weak passphrase**, a five-word list finds it:

```shell-session
analyst@lab:~$ python3 wpa2crack.py
SSID=CorpWiFi  target_PMK=bb818e7aa8d415e4dc318bd0...
  try password       -> c0f87d25fd9c8bd0...
  try letmein        -> 6fa4e4fd0342dfce...
  try CorpWiFi123    -> dd33e41b1fae09b2...
  try Summer2024     -> bb818e7aa8d415e4...  <-- CRACKED
  try Winter2025     -> 16f0df498c03ee95...
```

`Summer2024` was in the list, so its PMK matched and the passphrase fell. On a
real engagement the wordlist is millions of entries and the compute is a GPU, but
the loop is identical: derive, compare, repeat. The capture cost nothing to attack
once obtained, because the guessing happens entirely offline with no further
contact with the network.

**Against a high-entropy passphrase**, the same code and the same effort produce
nothing:

```shell-session
analyst@lab:~$ python3 wpa2crack.py --target-strong
now targeting a HIGH-ENTROPY passphrase:
  dictionary EXHAUSTED -> not cracked
```

Nothing about the algorithm changed. The iteration count, the salt, the hash, the
attacker's effort — all identical. The only variable that moved is the passphrase's
entropy, and it moved the result from "cracked in five tries" to "not in the
dictionary at all." That is the entire lesson, and it corrects a common
misstatement: WPA2-PSK is not a broken protocol, and capturing a handshake is not
the same as recovering a key. A long, random passphrase makes the offline attack
computationally hopeless while a captured handshake sits uselessly on the
attacker's disk.

It is also exactly what WPA3 changes. Its SAE handshake makes each guess require
interaction with the network rather than offline computation, so an attacker can
no longer capture once and grind forever — which removes the dependence on
passphrase entropy that this example isolates.

'''

WORK = {
    # OPSEC already applied in the prior run; WPA2 re-runs with the Summary fallback.
    "Offensive Security/Penetration Testing/Wireless & Physical Penetration Testing/WPA2 Security Testing.md": WPA2,
}

ANCHOR = re.compile(r"^## Task \d+ — (Failure Modes|Security Implications|Detection|Defen|Reporting)", re.M)
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
        m = ANCHOR.search(src) or SUMMARY.search(src)   # before Summary if no security task
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
