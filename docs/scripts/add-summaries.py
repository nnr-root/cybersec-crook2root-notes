#!/usr/bin/env python3
"""
Add ## Summary sections to the 7 non-Cryptography leaves that lack one.

The 20 Cryptography stubs are deliberately skipped: they are rewritten from
scratch in the next phase, and their summaries are authored as part of that
rewrite. Adding stub-summaries now would be deleted work.

Each summary is inserted immediately before the note's trailing
"Related Master Notes" section (these older notes end there rather than with a
"## Summary"). Content is hand-authored per note from its task list.

    python3 docs/scripts/add-summaries.py            # dry run
    python3 docs/scripts/add-summaries.py --apply
"""
import re
import sys

SUMMARIES = {
    "Application Security/API Security.md": [
        "Test an API methodically — enumerate endpoints, map its authentication, and probe each OWASP API risk in turn rather than guessing.",
        "Recognise broken object- and function-level authorization (BOLA/BFLA) as the dominant API flaws, and explain why the check must be per-object and server-side.",
        "Explain how APIs leak through excessive data exposure and mass assignment, and how rate limiting, asset management and logging close the operational gaps.",
    ],
    "Application Security/OWASP Top 10.md": [
        "Name each of the OWASP Top 10 categories and state the mechanism behind it, not just its title.",
        "Recognise the highest-impact web risks — broken access control, cryptographic failures, injection and SSRF — in real code.",
        "State the primary control for each category and explain why it addresses the cause rather than the symptom.",
    ],
    "Application Security/Web Exploitation.md": [
        "Exploit the major web injection classes — SQLi, XSS, command, SSTI, XXE, LDAP, ORM and SSRF — against a controlled target.",
        "Explain why each injection works at the parser level: which input reaches which interpreter, and where the trust boundary was crossed.",
        "Turn a web foothold into deeper access through file inclusion, upload flaws, IDOR and authentication bypass.",
    ],
    "Application Security/Web Fundamentals.md": [
        "Read and construct an HTTP transaction, and systematically walk an unfamiliar application's structure.",
        "Discover hidden content and subdomains with calibrated fuzzing and enumeration, and feed the results into testing.",
        "Decode and attack a JWT, and explain what each of its three segments controls and how tampering is detected.",
    ],
    "Defensive Security/Advanced Defenses.md": [
        "Adopt the detection mindset — assume compromise and hunt for the behaviour rather than waiting for a signature.",
        "Build detections for privilege escalation, exploitation and shellcode, living-off-the-land, and anti-forensics.",
        "Explain how EDR, SIEM and threat hunting compose into a layered defensive stack, and where each layer sees what.",
    ],
    "Defensive Security/Defensive Groundwork.md": [
        "Configure a default-deny host firewall and explain the netfilter model beneath both iptables and ufw.",
        "Distinguish cookie-based and token-based sessions, and reason about the attack surface each exposes.",
        "Explain how multi-factor authentication factors compose, and why the recovery path is usually the weakest link.",
    ],
    "DevSecOps/Docker and Containers.md": [
        "Build and reason about container images, including multi-stage builds that ship only the final artifact.",
        "Identify and demonstrate the common container-escape paths — a mounted Docker socket, sensitive host mounts, dangerous capabilities — and explain why each breaks isolation.",
        "Name the runtime controls (least privilege, dropped capabilities, read-only mounts, Falco-style monitoring) that detect or prevent an escape.",
    ],
}

REL_NOTES = re.compile(r"^## .*Related Master Notes", re.M)
FOOTER = re.compile(r"^>\s*🔼\s*Up:", re.M)


def build(bullets):
    lines = "\n".join(f"- {b}" for b in bullets)
    return "## Summary\n\nYou should now be able to:\n\n" + lines + "\n"


def main():
    apply = "--apply" in sys.argv
    for rel, bullets in SUMMARIES.items():
        try:
            src = open(rel, encoding="utf-8").read()
        except FileNotFoundError:
            print(f"  MISSING  {rel}")
            continue
        if re.search(r"^## Summary\s*$", src, re.M):
            print(f"  · already has Summary  {rel.split('/')[-1]}")
            continue
        block = build(bullets) + "\n"
        m = REL_NOTES.search(src) or FOOTER.search(src)
        if m:
            out = src[:m.start()] + block + src[m.start():]
        else:
            out = src.rstrip() + "\n\n" + block
        out = re.sub(r"\n{3,}", "\n\n", out)
        print(f"  ✓ inserted Summary ({len(bullets)} bullets)  {rel.split('/')[-1]}")
        if apply:
            open(rel, "w", encoding="utf-8").write(out)
    print(f"\n{'APPLIED' if apply else 'DRY RUN'}")
    print("Cryptography summaries deferred to the rewrite phase (would be deleted work now).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
