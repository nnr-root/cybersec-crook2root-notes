---
title: "Guided Web & API Assessment"
aliases:
  - Guided Web App Walkthrough
  - Guided API Assessment
  - Web Application Assessment Walkthrough
  - API Assessment Walkthrough
tags:
  - tree/offensive
  - cyber/offensive/guided
  - type/walkthrough
  - level/operator
Domain: "[[Guided Assessments]]"
Color: "#DC143C"
---

# 🌐 Guided Web & API Assessment

> [!warning] Authorized simulation only
> Use a staging environment or explicitly approved production scope. Never send destructive payloads, retrieve real customer records, or bypass availability controls unless the RoE authorizes the exact action. Rate-limit automation and coordinate anything that could trigger queues, notifications, billing, or irreversible workflows.

## Parent Learning Order
Guided Network Pentest Walkthrough -> Guided Active Directory Assessment -> Guided Web & API Assessment -> Guided Wireless Assessment -> Guided Cloud Security Assessment -> Guided Social Engineering Exercise -> Guided Red Team & Purple Team Operation -> Guided Retest & Closure

## Start at Zero: One Application, Two Surfaces

A modern application is tested through two surfaces that share one security model: the **browser-facing web app** (pages, sessions, forms, workflows) and the **API** underneath (REST/GraphQL/gRPC/WebSocket endpoints the client and mobile apps call). Assessing them together is correct because *the API is where authorization actually lives* — the UI merely hides buttons, while the API is what an attacker calls directly. This walkthrough converts a URL and a set of test identities into a defensible assessment of **architecture, authorization, session handling, input boundaries, and business workflows** across both surfaces.

The recurring theme, and the single most productive test: **does the server consistently enforce the business model, regardless of what the client sends?**

> [!tip] The analogy, and where it breaks
> The web UI is like a restaurant's printed menu and the API is the kitchen's order line — a careful attacker ignores the menu and shouts orders straight at the kitchen, ordering things the menu never listed. The analogy breaks on identity: a kitchen trusts whoever is at the pass, whereas every API call carries a token, so the real test is whether the kitchen *re-checks who you are and what you own on every single order* — not whether the menu looked locked down.

**Prerequisites:** the **Broken Access Control**, **Web Authentication Testing**, **Modern API Security Testing**, and **Business Logic Testing** technique leaves; **Rules of Engagement & Scoping**.

## The Engagement Arc

```mermaid
flowchart TD
    S["Scope: hosts, APIs, roles, data, tenants"] --> ID["Get ≥2 users in different tenants + 1 admin"]
    ID --> M["Map app + build endpoint/state inventory"]
    M --> TB["Model trust boundaries"]
    TB --> AU["Test authentication & sessions"]
    AU --> AZ["Test authorization & tenant isolation"]
    AZ --> IN["Test input & parser boundaries"]
    IN --> BL["Test business workflows"]
    BL --> C["Evidence, cleanup & retest"]
```

## 1. Freeze Scope and Identities

Authorization is impossible to assess with a single account. Insist on **at least two ordinary users in different tenants plus one privileged identity**:

```text
Tenant A user : alice.test  / role=user
Tenant B user : bob.test    / role=user
Tenant A admin: admin.test  / role=administrator
Forbidden     : payment capture, email delivery, bulk export, load testing
Test marker   : C2R-20260730
```

## 2. Map Both Surfaces and Build a Role-Action Matrix

Browse every role and capture methods, paths, parameters, cookies, anti-CSRF values, object identifiers, and state transitions — *plus* JS-discovered endpoints, API specs, GraphQL schemas, WebSocket channels, and async jobs. Compare *documented* routes with *observed* routes. Then write the matrix of who-should-do-what **before** testing:

| Capability | Anonymous | Tenant user | Tenant admin |
|---|---:|---:|---:|
| View own invoice | No | Yes | Yes |
| View another tenant | No | No | No |
| Invite user | No | No | Yes |
| Export all records | No | No | Approved admin only |

## 3. Model Trust Boundaries

Identify where the browser, CDN/WAF, API gateway, application, identity provider, queues, and data stores each make security decisions. **Client-side validation is not a trust boundary**, and a signed token proves only *what the verifier actually checks* — not every claim the developer intended to constrain. Treat a WAF response as evidence of *edge* behavior, never proof the origin is safe.

## 4. Test Authentication and Sessions

Review registration, recovery, MFA enrollment/reset, federation callbacks, session rotation, logout, remembered devices, and concurrent sessions. Change **one variable at a time**, and confirm that *server-side state* — not UI visibility — enforces each control.

```http
POST /api/v1/password-reset/confirm HTTP/1.1
Content-Type: application/json

{"token":"test-token","newPassword":"Approved-Test-Only-42!"}

HTTP/1.1 400 Bad Request
{"error":"token expired"}
```

## 5. Test Authorization and Tenant Isolation (the core)

Replay a known-valid request while substituting object IDs, parent IDs, tenant headers, HTTP methods, content types, and roles. Test list / read / update / delete / export / indirect actions **separately** — a `403` on `GET` does not prove `PUT` is protected.

```text
Control : Tenant A reads invoice A-7412  -> 200
Variant : Tenant B reads invoice A-7412  -> expected 403/404
Observed: 200 with test invoice metadata   <-- BROKEN OBJECT-LEVEL AUTH
Bounded : stop after the test record; do NOT enumerate adjacent identifiers
```

Also test **mass assignment** — add a server-controlled field to a synthetic update and confirm it is ignored:

```text
Invariant : client cannot set account.role
Variant   : {"displayName":"Test","role":"administrator"}
Secure    : role ignored or request rejected; audit event emitted
```

## 6. Test Input, Parser, and Workflow Boundaries

Trace input from source to sink (DB query, shell, template, file path, XML parser, deserializer, URL fetcher, log formatter). Start with harmless syntax probes and *differential responses*; escalate only enough to distinguish validation vs. parsing vs. execution.

```text
Baseline response      : 200, 842 bytes, 118 ms
Quoted-input response  : 500, 119 bytes, 121 ms
Time-control response  : 200, 842 bytes, 116 ms
Interpretation         : parser error likely; NO evidence of time-based execution
```

Then diagram the **business workflow** and attack its *logic*: skip steps, replay transitions, use stale objects, submit concurrently, and try negative values. Business impact — not payload novelty — sets severity.

```mermaid
stateDiagram-v2
    [*] --> Draft
    Draft --> Submitted
    Submitted --> Approved
    Approved --> Fulfilled
    Fulfilled --> [*]
```

If the server accepts an illegal `Draft -> Fulfilled` transition, capture **one** canary transaction and stop.

## Failure Modes and Interpretation

- **Testing with one account.** Horizontal/vertical authorization is unassessable without multiple tenants and roles — this is the most common setup failure.
- **Trusting a `403` on one verb/route.** Authorization must be tested per method, per nested resource, per API version, and per equivalent endpoint; fixes are frequently partial.
- **UI == security.** A hidden button is not a control; always call the API directly. The client only *hints* at what exists.
- **Payload theatre.** Chasing exotic payloads over business-logic and access-control flaws inflates noise and misses the high-impact findings.
- **Over-collection.** Prove access with a single canary record; enumerating adjacent IDs or exporting data turns a finding into a breach you caused.

## Security Implications — the Defender's View

- **Centralized, server-side authorization** (an ownership predicate enforced in one place for every route, verb, and version) is the durable fix for the dominant findings (BOLA/IDOR/BFLA) — hiding IDs is not.
- **Verify-what-you-check on tokens:** the identity provider and services must validate audience, scope, signature, and object ownership — the API, not the UI, is the enforcement point.
- **Defense in depth at the edge and origin:** WAFs blunt generic input attacks, but parser/deserialization sinks must be fixed at the origin (parameterized queries, safe deserializers, allow-listed templates).
- **Observability:** request IDs surviving gateway→service, measurable authorization denials, and redaction of sensitive values let defenders distinguish ordinary validation errors from attack patterns.

## Authorized Lab: Prove Broken Object-Level Authorization Locally

> [!info] Runs on one machine with Python — a tiny multi-tenant API with an IDOR flaw; you prove it with a canary, then apply the fix and confirm
> No real data or third party. Step 5 removes everything.

### Step 1 — A minimal multi-tenant invoice API (with the flaw)

```bash
mkdir -p /tmp/webapi-lab && cat > /tmp/webapi-lab/app.py <<'PY'
from http.server import BaseHTTPRequestHandler, HTTPServer
INVOICES={"A-7412":("tenant-A","CANARY-INV-A"),"B-2201":("tenant-B","CANARY-INV-B")}
TOKENS={"tokA":"tenant-A","tokB":"tenant-B"}
FIX=False  # flip to True in step 4
class H(BaseHTTPRequestHandler):
    def log_message(self,*a): pass
    def do_GET(self):
        tok=self.headers.get("Authorization","").replace("Bearer ","")
        tenant=TOKENS.get(tok)
        iid=self.path.rsplit("/",1)[-1]
        rec=INVOICES.get(iid)
        if not tenant or not rec: self.send_response(401); self.end_headers(); return
        if FIX and rec[0]!=tenant:   # object-level authz check
            self.send_response(403); self.end_headers(); self.wfile.write(b"forbidden"); return
        self.send_response(200); self.end_headers(); self.wfile.write(rec[1].encode())
HTTPServer(("127.0.0.1",8099),H).serve_forever()
PY
python3 /tmp/webapi-lab/app.py &>/tmp/webapi-lab/srv.log & sleep 1
echo "multi-tenant API up on 127.0.0.1:8099 (FIX=False)"
```

```text
multi-tenant API up on 127.0.0.1:8099 (FIX=False)
```

### Step 2 — Control request: Tenant A reads its own invoice

```bash
curl -s -H "Authorization: Bearer tokA" http://127.0.0.1:8099/api/invoice/A-7412; echo "  <- expected (own record)"
```

```text
CANARY-INV-A  <- expected (own record)
```

### Step 3 — The IDOR proof: Tenant B reads Tenant A's invoice

```bash
curl -s -o /dev/null -w "HTTP %{http_code}\n" -H "Authorization: Bearer tokB" http://127.0.0.1:8099/api/invoice/A-7412
curl -s -H "Authorization: Bearer tokB" http://127.0.0.1:8099/api/invoice/A-7412; echo "  <- BROKEN: cross-tenant read"
```

```text
HTTP 200
CANARY-INV-A  <- BROKEN: cross-tenant read
```

### Step 4 — Apply the fix (server-side ownership check) and re-test

```bash
sed -i.bak 's/FIX=False/FIX=True/' /tmp/webapi-lab/app.py
pkill -f webapi-lab/app.py; python3 /tmp/webapi-lab/app.py &>/tmp/webapi-lab/srv.log & sleep 1
curl -s -o /dev/null -w "Tenant B -> A: HTTP %{http_code}\n" -H "Authorization: Bearer tokB" http://127.0.0.1:8099/api/invoice/A-7412
curl -s -o /dev/null -w "Tenant A -> A: HTTP %{http_code} (own still works)\n" -H "Authorization: Bearer tokA" http://127.0.0.1:8099/api/invoice/A-7412
```

```text
Tenant B -> A: HTTP 403
Tenant A -> A: HTTP 200 (own still works)
```

The server-side ownership predicate blocks the cross-tenant read **and** preserves legitimate access — the closure standard a retest must confirm.

### Step 5 — Cleanup

```bash
pkill -f webapi-lab/app.py 2>/dev/null; rm -rf /tmp/webapi-lab
ls -d /tmp/webapi-lab 2>&1 | tail -1
```

```text
ls: cannot access '/tmp/webapi-lab': No such file or directory
```

**What you should now be able to do:** scope an app/API test with the identities it requires, map both surfaces into a role-action matrix, test authentication/authorization/input/workflow with one-variable-at-a-time discipline, prove broken object-level authorization with a canary, and verify a centralized server-side fix without breaking legitimate use.

## Crook → Operator → Root Checkpoint

- **Crook:** Explain why the API (not the UI) is where authorization lives, and why you need multiple tenants/roles to test it.
- **Operator:** Build a role-action matrix, prove a BOLA/IDOR flaw with a single canary record, and test authentication, input sinks, and business-workflow logic safely.
- **Root:** Explain why centralized server-side authorization (not ID hiding) is the durable fix, why `403` on one verb never generalizes, and how token verification, origin-side parser fixes, and observability defend both surfaces.

---
> 🔼 Up: [[Guided Assessments]]
