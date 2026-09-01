#!/usr/bin/env python3
"""Offensive Security worked examples — batch 10 (Web identity)."""
import re
import sys

SSO = '''## Worked Example: A Relying Party That Trusts a Claim It Never Verified

Federated identity works because the relying party trusts assertions signed by the
identity provider. Every SSO vulnerability of consequence is the relying party
trusting the *claim* while skipping the *signature check* that is supposed to earn
that trust. The specimen makes exactly that omission:

```python
assertion = json.loads(base64.b64decode(body))   # {"user": ..., "sig": ...}
user = assertion.get("user")                      # BUG: uses the claim...
return {"logged_in_as": user}                     # ...without verifying sig
```

**A legitimate assertion** logs the right user in:

```shell-session
analyst@lab:~$ echo -n '{"user":"alice","sig":"valid-idp-sig"}' | base64 | \\
>   xargs -I{} curl -s -X POST -d '{}' http://127.0.0.1:8115/sso
{"logged_in_as": "alice"}
```

Nothing looks wrong, because on the happy path a real IdP produced the assertion
and the claimed user is the true one. The bug is invisible until someone lies.

**A forged assertion** carries an obviously bogus signature and a chosen identity:

```shell-session
analyst@lab:~$ echo -n '{"user":"admin","sig":"FORGED-not-from-idp"}' | base64 | \\
>   xargs -I{} curl -s -X POST -d '{}' http://127.0.0.1:8115/sso
{"logged_in_as": "admin"}
```

`admin`, with a signature that reads `FORGED-not-from-idp`. The relying party
accepted it because it never asked whether the signature verified against the
IdP's public key — it read the `user` field and believed it. That is the entire
class: SAML response tampering, unsigned-assertion acceptance, and the XML
signature-wrapping attacks are all elaborations of "the RP trusted a claim it did
not authenticate."

The correctness condition is narrow and non-negotiable: verify the assertion's
signature against the IdP's key *before* reading any claim from it, and then check
that the issuer, audience and expiry are the ones you expect — a valid signature
on an assertion minted for a different service is still the wrong assertion. The
reason hand-rolled validation fails here so reliably is that the checks must all
pass and must happen in the right order, which is exactly what a vetted SAML or
OIDC library encodes and an afternoon's own code does not.

'''

MFA = '''## Worked Example: MFA That Is Prompted but Not Enforced

A second factor only protects a resource if the resource checks for it. A common
flaw prompts for MFA, records that the password was correct, and then guards the
protected page against the *password* state rather than the *MFA-complete* state.
The specimen has that exact gap:

```python
if path == "/login" and password_ok:
    half_auth.add(user)                    # password verified
    return '{"mfa_required": true}'
if path == "/dashboard":
    if user in half_auth:                  # BUG: checks password, not MFA
        return '{"data": "..."}'
```

**Logging in** looks correctly protected:

```shell-session
analyst@lab:~$ curl -s -X POST -d 'u=alice&p=S3cret!' http://127.0.0.1:8118/login
{"mfa_required":true}
```

The password is accepted and the app declares that MFA is required. A tester
watching the intended flow — password, then a code prompt — sees a second factor
and might conclude it is enforced.

**Skipping the second factor** is a single request that never touches the code
prompt:

```shell-session
analyst@lab:~$ curl -s http://127.0.0.1:8118/dashboard
{"data":"CANARY-DASHBOARD"}
```

The dashboard returned its data with no MFA completed. The server treated a
correct password as sufficient because the protected resource only checked the
half-authenticated state — the one the password created — and MFA, though
prompted, was never a precondition for anything. The prompt was theatre; the gate
was open.

This is why MFA testing follows the resource, not the login screen. The question
is never "does it ask for a code" but "does *every* authenticated resource refuse
to serve a session that has not completed MFA, verified server-side". The
half-authenticated state must gate the whole application until the second factor
is confirmed, and the check cannot live in the client, which the attacker
controls.

The second place to look is the recovery flow, because it is the designed bypass:
a "lost your device" path that resets MFA on a single emailed link, or a security
question, hands an attacker the same access the second factor was meant to
prevent. An MFA implementation is only as strong as the weakest way to switch it
off, and recovery is usually that way.

'''

WORK = {
    "Offensive Security/Penetration Testing/Web Application Penetration Testing/Web Identity & Access Control/Federated Identity & SSO.md": SSO,
    "Offensive Security/Penetration Testing/Web Application Penetration Testing/Web Identity & Access Control/MFA, Recovery & Session Bypass Testing.md": MFA,
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
