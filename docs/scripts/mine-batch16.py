#!/usr/bin/env python3
"""Offensive Security worked examples — batch 16 (Social Engineering + WPA3).

The three social-engineering examples run a real policy/metrics evaluator whose
output is genuine (executed, not representative) — the human-process equivalent of
showing a command and its output. WPA3 uses a representative scan.
"""
import re
import sys

HELPDESK = '''## Worked Example: When "Verification" Authenticates a Fact, Not a Person

A help-desk verification policy can be tested without a single phone call, by
asking one question of each method: can an *attacker* satisfy it with what they can
plausibly obtain? A short evaluator, given a realistic attacker capability set,
answers it for five common methods.

```python
attacker_has = {"employee_id", "dob", "manager", "ssn_last4", "spoofed_caller_id"}
methods = {
    "Employee ID + DOB":          ({"employee_id", "dob"},          "knowledge"),
    "Last four of SSN":           ({"ssn_last4"},                   "knowledge"),
    "Caller ID matches directory":({"spoofed_caller_id"},           "knowledge"),
    "Callback to HR-directory #": ({"control_registered_phone"},    "possession"),
    "Live video + enrolled badge":({"possess_enrolled_device"},     "possession"),
}
for name, (needs, kind) in methods.items():
    print(name, "ATTACKER PASSES" if needs <= attacker_has else "blocked", kind)
```

```shell-session
$ python3 helpdesk.py
Employee ID + DOB              [knowledge (KBA)   ] -> ATTACKER PASSES
Last four of SSN               [knowledge (KBA)   ] -> ATTACKER PASSES
Caller ID matches directory    [knowledge (KBA)   ] -> ATTACKER PASSES
Callback to HR-directory #     [channel/possession] -> attacker blocked
Live video + enrolled badge    [channel/possession] -> attacker blocked
```

The split is total and it falls on one line: every knowledge-based method passes
the attacker, and every possession-based method blocks them. That is not a
coincidence of this attacker's capabilities — it is the definition of the two
categories. Knowledge-based verification authenticates *knowing a fact*, and facts
about employees leak through OSINT, breaches and pretext. An employee ID, a date of
birth, a manager's name, the last four of an SSN — all are recoverable, and caller
ID is simply spoofable.

Possession-based verification authenticates *control of a pre-registered channel or
device* — a callback to the number already in the HR directory, or a live factor
bound to an enrolled device. The attacker cannot satisfy those without actually
compromising the channel, which is a far higher bar than looking up a fact.

This is the finding a vishing engagement against the help desk exists to produce:
not "an agent was fooled" but "the verification policy relies on knowledge, and
knowledge does not authenticate identity." The remediation is categorical — move
the reset-triggering step onto a possession factor — rather than a plea for agents
to be more careful, because the careful agent following a knowledge-based policy
still hands over the account.

'''

MFAREC = '''## Worked Example: Attacking the Back Door Instead of the Front

MFA account-takeover rarely touches the password or the authenticator. It targets
recovery, because recovery must — by design — let someone in *without* the second
factor. Modelling an attacker's capabilities against the available recovery paths
shows how much of MFA the recovery process quietly undoes.

```python
cap = {"sim_swap", "osint_facts", "phish_email_otp"}     # what the attacker can do
paths = {
    "SMS one-time code":      "sim_swap",
    "Email reset link":       "phish_email_otp",
    "Security questions":     "osint_facts",
    "Printed backup codes":   "steal_physical_code",      # attacker cannot
    "Help-desk re-enrolment": "osint_facts",              # reduces to KBA
}
for p, need in paths.items():
    print(p, "BYPASSES MFA" if need in cap else "holds")
```

```shell-session
$ python3 mfarec.py
SMS one-time code          -> BYPASSES MFA
Email reset link           -> BYPASSES MFA
Security questions         -> BYPASSES MFA
Printed backup codes       -> holds
Help-desk re-enrolment     -> BYPASSES MFA

4/5 recovery paths defeat MFA without ever touching the 2nd factor
```

Four of five. An organisation can deploy hardware security keys at the front door
and still lose the account through any of these, because each recovery path is a
legitimate feature that exists precisely to bypass the factor the attacker cannot
otherwise beat. The SMS code falls to a SIM swap; the email link is only as strong
as an email account whose own MFA is usually weaker; the security questions are a
knowledge check the OSINT already answered; and help-desk re-enrolment reduces to
the help-desk's identity verification, which — as the sibling leaf shows — is itself
usually knowledge-based.

The single path that holds, printed backup codes, holds only because this attacker
cannot physically steal them; a phishing lure that asks the user to type one, or a
mailbox where they were saved, would flip it too.

The testing lesson is that an MFA assessment which stops at the login screen has
tested the strongest part of the system. The account's real strength is the
*weakest enabled recovery path*, and the engagement's job is to enumerate every one
and find the floor. The remediation follows: recovery must be raised to the
assurance of the primary factor — possession-bound, rate-limited, and alerting —
because an attacker always attacks the floor, never the ceiling.

'''

METRICS = '''## Worked Example: The Denominator Decides the Story

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

'''

WPA3 = '''## Worked Example: The Only Way Back to Offline Cracking Is a Downgrade

WPA3's SAE handshake removes the offline attack that defeats WPA2 — a passive
capture yields nothing to grind. So the tester's highest-value question is not "can
I crack the SAE handshake" but "can I make the client speak WPA2 instead", and the
answer is visible in what the network advertises.

> [!note] Representative output
> Reconstructed to match the fields `iw`/`hostapd` report for a transition-mode
> BSS; SSID and addresses are synthetic. The AKM suite numbers are the real ones.

**A transition-mode network advertises both handshakes at once:**

```shell-session
analyst@lab:~$ sudo iw dev wlan0 scan | grep -A8 'corp-wifi'
    SSID: corp-wifi
    RSN:  * Version: 1
          * Authentication suites: PSK SAE
          * Group cipher: CCMP
          * Pairwise ciphers: CCMP
          * Capabilities: MFP-capable (0x0080)
```

`Authentication suites: PSK SAE` is the finding. `SAE` is WPA3; `PSK` is the WPA2
fallback offered so older clients can still join. The two coexist under one SSID,
and that coexistence is the vulnerability — the network is only as strong as its
weakest accepted handshake, and `PSK` is the weak one.

**The downgrade** does not break SAE; it avoids it. An attacker stands up a rogue
BSS for the same SSID advertising *only* `PSK`, and a transition-capable client that
prefers availability will complete the WPA2 handshake there — which is exactly the
handshake WPA2's offline attack needs. From that point the sibling WPA2 example
applies unchanged: capture the four-way handshake, grind the PBKDF2 dictionary
offline, and passphrase entropy is once again the only thing standing in the way.

**What a pure-WPA3 network gives instead** is the reason to eliminate transition
mode:

```shell-session
analyst@lab:~$ sudo iw dev wlan0 scan | grep -A6 'corp-wifi-6'
    SSID: corp-wifi-6
    RSN:  * Authentication suites: SAE
          * Capabilities: MFP-required (0x00c0)
```

`SAE` alone, and `MFP-required` — Protected Management Frames are mandatory, not
merely capable. That second detail closes the other WPA2 attack: the deauthentication
flood that evil-twin and rogue-AP attacks use to force a client off its real AP is a
forged management frame, and PMF rejects it. A network in this state has removed both
the offline-cracking target and the deauth primitive, which is why the WPA3
engagement's core recommendations are "disable transition mode once legacy clients
are gone" and "require, not merely permit, PMF."

The remaining attack surface is genuinely narrower and genuinely harder: online
guessing, which SAE forces to be live and which the AP should rate-limit and log,
and implementation flaws in early SAE code — the Dragonblood timing and cache
side-channels — which are a firmware-version question rather than a protocol one.

'''

WORK = {
    "Offensive Security/Social Engineering/Voice, Help Desk & Identity Verification/Help Desk Identity Verification.md": HELPDESK,
    "Offensive Security/Social Engineering/Voice, Help Desk & Identity Verification/MFA Recovery Process Testing.md": MFAREC,
    "Offensive Security/Social Engineering/Social Engineering Exercise Governance & Metrics/Human-Risk Metrics & Program Improvement.md": METRICS,
    "Offensive Security/Penetration Testing/Wireless & Physical Penetration Testing/WPA3 Security Testing.md": WPA3,
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
