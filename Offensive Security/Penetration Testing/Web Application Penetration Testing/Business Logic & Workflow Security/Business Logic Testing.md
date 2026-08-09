---
title: "Business Logic Testing"
aliases: ["Business Logic Flaws", "Workflow Abuse Testing", "Entitlement Security Testing", "Multi-Tenant Isolation Testing", "Payment Workflow Security"]
tags: [tree/offensive, cyber/offensive/web/logic, type/technique, level/operator]
Domain: "[[Business Logic & Workflow Security]]"
Color: "#DC143C"
---

# 🧩 Business Logic Testing

> [!warning] Authorized simulation only
> Business-logic abuse manipulates real workflows — payments, entitlements, tenant boundaries. Prove flaws against synthetic accounts and canary values (a $0 order, a test tenant), never real money or another customer's real data. Test only in-scope applications.

## Parent Learning Order
Business Logic Testing -> Race Condition & Concurrency Testing

## Start at Zero: The Bugs No Scanner Can Find

Most vulnerabilities are *implementation* flaws — a missing check, an unescaped input. **Business-logic flaws** are different: the code works exactly as written, but the *workflow itself* can be abused in ways the designer never anticipated. There is no malformed input, no injection, no signature — just a legitimate sequence of legitimate requests that produces an illegitimate outcome. A scanner cannot find these, because a scanner has no concept of what the application is *supposed* to do; only a human who understands the intended workflow can spot its abuse.

This is why business-logic testing is the most intellectually demanding web testing: you must model the application's intent, then ask "what happens if I do this out of order, with an impossible value, or in a way the UI would never allow?"

> [!tip] The analogy, and where it breaks
> A business-logic flaw is like a self-checkout that lets you scan a cheap item's barcode while bagging an expensive one — every individual step is valid, but the *combination* cheats the system. The analogy breaks because software abuse is *scriptable and instant*: a human does this once, but an attacker automates ten thousand variations per second, turning a clever trick into a systematic exploit no cashier could match.

**Prerequisites:** HTTP requests, authentication/authorization, and the API business-logic concept.

## The Common Business-Logic Flaw Families

Three families cover most real findings, and this note absorbs the workflow-specific concerns (entitlements, multi-tenancy, payments) as instances of them:

| Family | The abuse | Example |
| --- | --- | --- |
| **Value manipulation** | Impossible or negative values | Negative quantity refunds money; $0.01 price |
| **Sequence/state abuse** | Skipping or reordering steps | Apply discount *after* validation; reach checkout without payment |
| **Boundary bypass** | Crossing an entitlement or tenant line | Access another tenant's data; use a feature you didn't pay for |

**Entitlement flaws** are boundary bypasses: a user accesses a feature or resource their subscription/role does not grant, because the check happens in the UI (which hides the button) but not the server (which still honors the request). **Multi-tenant isolation flaws** are the same at the tenant level: one customer's account reaches another's data because the tenant boundary is not enforced server-side. **Payment workflow flaws** are value + sequence abuse against money: manipulating price, quantity, currency, or the order of pay/validate steps.

The unifying root cause: **the server trusts the client to follow the intended workflow and stay within its entitlements, instead of enforcing both itself.**

## The Testing Method: Model, Then Break

Business-logic testing has no payload list. The method:

1. **Map the intended workflow** — what steps, in what order, with what constraints, produce the legitimate outcome?
2. **Identify the trust assumptions** — where does the server assume the client behaved correctly (order, value, entitlement)?
3. **Violate each assumption** — reorder steps, send impossible values, cross a boundary, and observe whether the server catches it.

```bash
# value manipulation: does the server accept a negative quantity? (your own lab shop)
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"item":"widget","qty":-5,"price":10}' "http://127.0.0.1:8106/checkout"
```

```text
{"total":-50,"status":"accepted"}
```

A negative quantity produced a **negative total** — the server would *credit* the attacker money. No injection, no malformed input; just a value the workflow never expected, accepted because the server did not validate `qty > 0`. That is a business-logic finding.

```mermaid
flowchart TD
    W["Map intended workflow"] --> A["Identify server trust assumptions"]
    A --> V1["Value: negative/zero/overflow?"]
    A --> V2["Sequence: skip/reorder steps?"]
    A --> V3["Boundary: cross entitlement/tenant?"]
    V1 --> F["Finding: legitimate requests, illegitimate outcome"]
    V2 --> F
    V3 --> F
    F --> S["No scanner finds these — human intent-modeling required"]
```

## Failure Modes and Interpretation

- **Proving with real value.** A negative-quantity refund or a cross-tenant read must be proven with synthetic accounts and canary amounts — never actually move money or read a real customer's data.
- **These resist automation.** A scanner reports "no issues" on a business-logic flaw because there is nothing malformed to detect. Concluding "clean" from an automated scan misses this entire class.
- **Requires domain understanding.** You cannot test what you do not understand — spotting that "a discount should apply once" requires knowing the business rule. Time spent understanding the app is the investment that finds these.
- **Multi-step complexity.** Sequence abuses may need a precise chain of requests; reproduce the exact sequence, and note that state may need resetting between attempts.
- **Entitlement vs. authz.** An entitlement flaw (paid feature accessed for free) and an authorization flaw (BOLA) can look similar; classify by whether the boundary is *commercial* (entitlement) or *ownership* (authz) — the fix differs.

## Security Implications — Detection & Defense

- **Enforce every rule server-side.** The definitive fix: the server must validate values (positive, in-range), enforce sequence and one-time-ness, and check entitlements/tenant boundaries on *every* request — never trusting that the client followed the workflow or stayed in its lane.
- **The UI is not a control.** Hiding a button or greying out a feature is presentation, not security; the server must reject the request regardless of what the UI showed.
- **Multi-tenancy needs a tenant check on every query** — every data access must be scoped to the authenticated tenant, ideally enforced structurally (row-level security) not just in application code.
- **Detection is behavioral and rule-based:** impossible values (negative amounts), impossible sequences, and cross-tenant access patterns are the signals — anomaly detection tuned to the business rules, since there is no malicious *payload* to signature.
- **Threat-model the workflow** during design — asking "how could each step be abused?" is cheaper than finding it in a pentest, and it is the only way to catch logic flaws before they ship.

## Authorized Lab: Break a Workflow You Build

> [!info] Runs on one Linux machine — builds a shop with value and entitlement flaws locally
> Loopback-bound, synthetic accounts and canary money. Step 5 removes it.

### Step 1 — Build a checkout that trusts client-supplied values and a UI-only entitlement

```bash
cat > /tmp/shop.py << 'EOF'
import http.server, json
users={"free-token":"free","paid-token":"paid"}
class H(http.server.BaseHTTPRequestHandler):
    def _role(self): return users.get(self.headers.get("Authorization","").replace("Bearer ",""))
    def do_POST(self):
        n=int(self.headers.get("Content-Length",0)); d=json.loads(self.rfile.read(n) or b'{}')
        if self.path=="/checkout":
            # BUG: no validation that qty>0
            total=d.get("qty",1)*d.get("price",0)
            self.send_response(200); self.end_headers()
            self.wfile.write(json.dumps({"total":total,"status":"accepted"}).encode())
        elif self.path=="/premium-report":
            # BUG: checks auth but not ENTITLEMENT (free users get premium)
            role=self._role()
            if not role: self.send_response(401); self.end_headers(); return
            self.send_response(200); self.end_headers()
            self.wfile.write(json.dumps({"premium_data":"CANARY-PREMIUM","served_to":role}).encode())
        else:
            self.send_response(404); self.end_headers()
    def log_message(self,*a): pass
http.server.HTTPServer(("127.0.0.1",8106),H).serve_forever()
EOF
python3 /tmp/shop.py &>/dev/null &
sleep 1; echo "shop up (free-token, paid-token)"
```

```text
shop up (free-token, paid-token)
```

### Step 2 — Value manipulation: negative quantity credits money

```bash
echo "normal   -> $(curl -s -X POST -d '{"qty":2,"price":10}' http://127.0.0.1:8106/checkout)"
echo "negative -> $(curl -s -X POST -d '{"qty":-5,"price":10}' http://127.0.0.1:8106/checkout)"
```

```text
normal   -> {"total": 20, "status": "accepted"}
negative -> {"total": -50, "status": "accepted"}
```

A negative quantity yields a **negative total** (the system would refund the attacker) — a value-manipulation logic flaw. Every step was a valid request; the outcome is theft.

### Step 3 — Entitlement bypass: a free user gets premium

```bash
echo "free user -> $(curl -s -H 'Authorization: Bearer free-token' -X POST http://127.0.0.1:8106/premium-report)"
```

```text
free user -> {"premium_data": "CANARY-PREMIUM", "served_to": "free"}
```

A `free` user retrieved premium data (`served_to:free`). The server authenticated them but never checked their *entitlement* — the UI presumably hid the premium button, but the endpoint honored the request anyway. That is an entitlement flaw.

### Step 4 — Confirm it's a logic flaw, not an injection

```bash
echo "No malformed input, no payload — every request above is valid JSON to a valid endpoint."
echo "The flaw is the WORKFLOW: server trusts client values and UI-only entitlement checks."
echo "A scanner sees nothing wrong; only workflow modeling finds these."
```

```text
No malformed input, no payload — every request above is valid JSON to a valid endpoint.
The flaw is the WORKFLOW: server trusts client values and UI-only entitlement checks.
A scanner sees nothing wrong; only workflow modeling finds these.
```

### Step 5 — Cleanup

```bash
kill %1 2>/dev/null; rm -f /tmp/shop.py; wait 2>/dev/null
curl -s -o /dev/null -w "shop gone: %{http_code}\n" --max-time 2 http://127.0.0.1:8106/checkout 2>&1 | grep -o 'gone.*' || echo "shop gone: connection refused"
```

```text
shop gone: connection refused
```

**What you should now be able to do:** recognize business-logic flaws as valid-requests-illegitimate-outcome, model a workflow's trust assumptions and violate them (value/sequence/boundary), prove value manipulation and entitlement bypass with canary values, and explain why scanners cannot find these.

## Crook → Operator → Root Checkpoint

- **Crook:** Explain why business-logic flaws have no malicious payload and why a scanner cannot find them.
- **Operator:** Model a workflow, test value manipulation (negative amounts), entitlement bypass, and tenant-boundary crossing with synthetic accounts, and classify each family.
- **Root:** Explain why every value/sequence/entitlement/tenant rule must be enforced server-side (the UI is not a control), why multi-tenancy needs a per-query tenant scope, and why threat-modeling the workflow at design time is the only pre-ship defense.

---
> 🔼 Up: [[Business Logic & Workflow Security]]
