---
title: "API Security"
aliases: ["API Security", "API Pentesting", "OWASP API Security Top 10", "BOLA", "BFLA", "Mass Assignment"]
tags:
  - tree/appsec
  - cyber/web/api
  - type/concept
  - difficulty/medium
Domain:
  - "[[Standards & API]]"
Color: "#911EB4"
---

# 🔌 API Security

> [!abstract] Note of [[Standards & API]]
> Modern applications *are* APIs — a back end exposing JSON to web, mobile and third-party clients at once. With no interface constraining what a client may send, whole vulnerability classes that a browser would have prevented become routine. This note covers the fundamentals, a repeatable testing method, and the OWASP API Security Top 10. It is the API counterpart to [[OWASP Top 10]].

> [!warning] Authorized vulnerability-assessment context
> All testing below assumes in-scope, authorized endpoints, typically delivered as a Postman collection or an OpenAPI spec. The framing is defensive: find the flaw, prove it safely, remediate.

## Parent Learning Order
OWASP Top 10 -> API Security

## API Fundamentals

> *Your framework authenticates every route for you. Which authorization decision does it still leave entirely in your hands?*
>
> Hold your answer — the section below is the response.

Whether *this* caller may touch *that* object. A framework can confirm a token is valid and route the request; it cannot know that order `1041` belongs to user `4` and not to the user asking, because that relationship is specific to your data model. Authentication generalises and object-level authorization does not, which is why it has to be written into every endpoint by hand — and why forgetting it once is the most common serious API flaw there is.

The dominant style is **REST** (Representational State Transfer) — an architectural convention over HTTP, not a strict protocol. A **RESTful API** exposes **resources** (a user, product, order) at **endpoints** in a predictable, hierarchical, versioned structure: `/v1/users`, `/v1/users/42`, `/v1/users/42/orders`.

**HTTP methods map to CRUD** — and the mapping itself is a test surface (does `DELETE` actually check authorization?):

| Method | CRUD | Note for testing |
| --- | --- | --- |
| `GET` | Read (never mutate) | A `GET` that changes state is a design smell |
| `POST` | Create | Main body-injection surface |
| `PUT` | Full replace | Omitted fields may null-out — data loss / logic bugs |
| `PATCH` | Partial update | Extra fields the client should not control — see **Mass Assignment** below |
| `DELETE` | Delete | Often the least-authorized-checked verb |

**Status codes that matter:** `200/201/204` success; `400` bad input (probe validation); **`401`** = *who are you?* (missing/invalid auth); **`403`** = *I know you, but no* (the key BOLA/authorization signal); `404` not found; `405` method not allowed; `429` rate-limited; `500` server error (may reveal injection or a logic flaw). The `401` vs `403` distinction is the single most useful tell in authorization testing — a `403` that flips to `200` when you change an ID is a finding.

## Authentication Mechanisms

| Mechanism | How it works | Weakness to test |
| --- | --- | --- |
| **API Keys** (`X-API-Key: …`) | A static key identifies the client | Long-lived, shared across environments, committed to git — full access if leaked, until rotated |
| **Bearer Tokens** (`Authorization: Bearer …`) | Login returns a short-lived, revocable token | Theft in transit/storage; check expiry & revocation |
| **JWT** | Self-contained `header.payload.signature` | Payload is **encoded, not encrypted** — decode it; then test every flaw in **Web Fundamentals (JWT Security)** |

Decode any JWT you capture and read `user_id`, `role`, `exp` — those claims drive every authorization decision the API makes, and are exactly what BOLA/BFLA testing manipulates.

## API Pentesting Methodology

1. **Map** the surface — import the Postman/Insomnia collection, parse OpenAPI/Swagger docs, and proxy the mobile/web client through **Burp Suite** to catch **undocumented** endpoints.
2. **Authenticate** with two low-privilege accounts (A and B) plus, if available, an admin — you need multiple identities to prove authorization flaws.
3. **Test authorization on every endpoint** — swap A's token onto B's objects/functions. The flaws below are mostly authorization failures the framework does *not* fix for you.
4. **Inspect responses** for over-exposed fields; **probe** request bodies for extra writable fields; **burst** requests to check rate limits.

> The single most important truth: most API frameworks handle authentication and routing, but **object-level and function-level authorization must be coded into every endpoint by hand** — miss one and you have a critical bug.

## Broken Object Level Authorisation (BOLA)

**API1 — the #1 API risk**, because it's ubiquitous and yields mass data exposure. The API authenticates the user but doesn't verify they're allowed to access the *specific object* requested. (This is **IDOR** in API form.)

Authenticated as user 4, you request your data — then change the ID:

```http
GET /v1/users/4/orders HTTP/1.1
Host: api.meridian.test
Authorization: Bearer <token for user 4>

→ 200 OK    (yours)
```

```http
GET /v1/users/1/orders HTTP/1.1
Host: api.meridian.test
Authorization: Bearer <token for user 4>

→ 200 OK    (user 1's orders, returned to user 4)
```

The token never changed. Only the number in the path did, and the server answered anyway — it verified who was asking and never asked whether they were allowed. A secure endpoint compares the identity inside the token against the owner of the object named in the URL, and refuses when they differ:

```http
GET /v1/users/1/orders HTTP/1.1
Host: api.meridian.test
Authorization: Bearer <token for user 4>

→ 403 Forbidden
```

Note that the correct answer is `403` and not `404`. A `404` would hide whether the object exists, which sounds safer and mostly is not: it conceals the finding from your own logs as effectively as from the attacker, and enumeration still works by timing. `403` is the honest answer and the one worth alerting on.

BOLA appears in path params, query strings (`?owner_id=13`), body fields (`{"user_id":13}`), and headers (`X-User-ID: 13`). **Scaling is trivial** — sequential integer IDs let a `1..10000` loop exfiltrate every user in seconds. UUIDs add obscurity, not security (they leak via other endpoints and logs).

> **Fix:** enforce ownership on **every** endpoint (not a single global middleware — the user↔resource relationship differs per route), keyed to the authenticated identity from the token. Use unpredictable references and deny by default.

## Broken User Authentication (BUA)

**API2.** Flaws in verifying identity. The most common is **no rate limiting on login/auth endpoints**, enabling brute-force and **credential stuffing** (replaying breach-sourced credential pairs against a password-reusing user base). APIs skip CAPTCHA/lockout more often than web apps because they're built for programmatic access.

Plus the JWT failures — **weak HS256 secrets** (`hashcat -m 16500` / `jwt_tool` → forge tokens), **`alg:none`**, and **missing `exp` validation** (a stolen token valid forever). Full set: **Web Fundamentals (JWT Security)**.

> **Fix:** rate-limit + lockout on all auth endpoints, **MFA**, strong signing secrets, reject `none`, validate `exp`/`aud`, and keep token lifetimes short.

## Excessive Data Exposure

**API3.** The back-end returns **entire database objects** and trusts the front-end to hide sensitive fields. But the raw JSON already left the server — anyone using **Burp Suite** or browser dev-tools sees everything.

The UI renders `username`/`email`/avatar; the raw response also carries `password_hash`, `api_key`, `internal_notes`, `last_login_ip`, `is_admin`. Front-end filtering provides **zero** security.

Combined with **BOLA** this escalates from a moderate access-control issue to a **full data breach** — and it also *reveals the field names* an attacker then injects, which is **Mass Assignment** below.

> **Fix:** server-side **response filtering / serialization schemas** per role — never `return user` (the whole ORM object); return an explicit DTO with only the fields that role should see.

## Lack of Resources & Rate Limiting

**API4.** Missing rate limits affect *every* endpoint, not just login: brute-force **4-digit OTPs** (only 10,000 combinations), scrape data at scale, abuse costly actions (SMS/email sends, report generation), or cause **DoS** with heavy queries.

Test it: send a burst of identical requests and watch for `429 Too Many Requests`. Well-built APIs return `X-RateLimit-Limit`, `X-RateLimit-Remaining`, and `X-RateLimit-Reset` headers; their absence usually means no limiting is in place.

> **Fix:** global rate limiting with **stricter caps on sensitive endpoints** (login, OTP, password reset), request-size/complexity limits, pagination caps, timeouts, and the standard rate-limit response headers.

## Broken Function Level Authorisation

**API5.** Like BOLA but for **actions/functions** rather than objects — a regular user reaching **administrative functionality** because the endpoint checks authentication but not **role**.
```
GET    /v1/users/me         → normal endpoint (fine)
GET    /v1/admin/users      → 200 OK for a non-admin?     ← broken function-level auth
DELETE /v1/users/99          → can a normal user delete another user?
POST   /v1/users/1/promote   → self-promote to admin?
```

Discovery: take an admin-only request captured from an admin session and replay it with a **low-privilege** token; a `200` instead of `403` is the finding. Also fuzz predictable admin paths (`/admin`, `/internal`, `/v1/manage`).

> **Fix:** deny-by-default authorization; verify **role/permission** on every administrative and state-changing route (centralised, not per-controller); never rely on the client hiding admin buttons or the endpoint being "unlinked."

## Mass Assignment

**API6.** The API binds client request data **directly** to internal object fields without an allow-list. The server object has `role`, `is_admin`, `credit_balance`, `email_verified` — normally server-controlled — and the API accepts them if the client injects them:
```http
PATCH /v1/users/me
{"email":"new@meridian.test", "role":"admin"}      ← privilege escalation, no auth flaw needed
```

You learn injectable field names from the API's own **over-exposed responses** or from OpenAPI `readOnly` hints (which reveal a field exists — the question is whether the server actually enforces the constraint). Prevalent in auto-binding ORMs (Laravel, CodeIgniter, Rails).

> **Fix:** explicit **input allow-list** of client-writable fields per endpoint (DTOs / `fillable` / strong params); silently drop anything else; `role`/`is_admin`/`permissions`/`balance` must never be client-writable.

## Security Misconfiguration

**API7.** Default configs, verbose errors/stack traces (leaking framework, version, file paths), missing security headers, **permissive CORS** (`Access-Control-Allow-Origin: *` *with* credentials lets any site read authenticated responses), unnecessary HTTP methods enabled, and unpatched servers.

Test CORS by sending `Origin: https://evil.com` and checking whether it's reflected back in `Access-Control-Allow-Origin` alongside `Access-Control-Allow-Credentials: true`.

> **Fix:** hardened repeatable baseline, generic error responses, **strict CORS** (explicit origin allow-list, never `*` with credentials), disable unused methods, ship security headers, and patch on a cadence. Mirrors **web A05**.

## Injection

**API8.** Untrusted input reaches an interpreter — **SQL, NoSQL, command, LDAP**. APIs are prime targets because they take structured JSON straight into queries, and **NoSQL** injection via typed JSON is API-specific:
```javascript
// ❌ NoSQL (MongoDB) auth bypass via a typed JSON body
{"username": {"$ne": null}, "password": {"$ne": null}}   // "not equal to null" matches any user
{"username": "admin", "password": {"$gt": ""}}            // "greater than empty" → logs in as admin
```

> **Fix:** parameterised queries, strict input **typing and validation** (reject objects where a string is expected — the root of NoSQL operator injection), ORM-safe methods, and least-privilege DB accounts. Full family: **SQLi**, **command injection**.

## Improper Assets Management

**API9.** APIs sprawl across versions and environments: old versions (`/v1` left running beside the patched `/v3`), undocumented **shadow** endpoints, beta/debug routes, and staging hosts exposed to the internet. Deprecated versions frequently lack the newer security fixes, so attackers *downgrade* to the weak one.

Discovery: enumerate versions (`/v1`, `/v2`, `/v3`, `/beta`, `/internal`), diff their behaviour, and check for non-production hosts (`api-dev.`, `staging-api.`) found via subdomain enumeration.

> **Fix:** maintain an authoritative **inventory** of every API, version, and host; formally retire (not just "hide") old versions; keep non-production environments off the public internet; and keep documentation current so shadow endpoints don't accumulate.

## Insufficient Logging & Monitoring

**API10.** API attacks are automated and high-volume — without logging of authentication failures, authorization denials (`401`/`403`), and anomalies, they run unseen. This is the API face of **web A09**.

> **Fix:** log security events with context (identity, endpoint, source, outcome — but never the secrets themselves), forward to a tamper-resistant SIEM, and alert on `401`/`403` spikes, sequential-ID enumeration, and rate-limit breaches. Ties to **host logging**.

**The deliberate break:** the API's attack surface reads as the endpoints in its current documentation — that is what exists, so that is what gets tested.

The surface is **every version ever deployed and never decommissioned**. `v1` is usually still answering beside `v2`, a staging host usually shares the production data store, and the deprecated endpoint reliably retains the flaw that was fixed in its replacement — because nobody backports a fix to a version they have stopped thinking about. Securing the documented API leaves the undocumented one running, and the undocumented one is where the authorisation logic is a release behind.

**How you'd spot it:** enumerate by version and environment rather than by documentation: request `/v1` where the docs describe `/v2`, and look for staging or internal hostnames answering with production data. Then check logging as a separate question — an API without per-caller logging cannot detect the sequential walk through object identifiers that its single most common vulnerability consists of, so the absence of that telemetry is itself the finding.

## Security Implications

**Eight of these ten are the same flaw wearing different clothes.** BOLA, broken function-level authorization, mass assignment, excessive data exposure — each is the server accepting a client's word about something the client should not get a say in: which object, which function, which fields, which audience. Reading them as one question rather than ten checklist items is what turns a tester into an assessor, because the eleventh variant will not be on the list.

**The absence of a user interface removes a control nobody designed.** A web form is not a security boundary, but it is an accident of one: it constrains what a naive attacker sends. An API has no such accident. Every constraint a browser used to supply — field set, value range, request rate, ordering — has to be re-created deliberately server-side, and the flaws in this note are largely the catalogue of the ones that were not.

**Authorization does not centralise the way authentication does.** It is tempting to solve these once in middleware, and authentication genuinely works that way. Object-level authorization does not, because the relationship between a caller and a resource differs per route: ownership for an order, membership for a team, delegation for an admin acting on behalf of a user. A single global check is either too permissive to help or too strict to ship, which is why the work is per-endpoint and why coverage — not cleverness — is what makes it correct.

**An API with no per-caller logging cannot see its own worst case.** The signature of BOLA exploitation is one authenticated identity walking sequential object identifiers, which is invisible in aggregate traffic and obvious in per-caller traffic. An organisation that logs request volume but not who requested what has instrumented everything except the thing most likely to happen to it.

## Summary

You should now be able to:

- Test an API methodically — enumerate endpoints, map its authentication, and probe each OWASP API risk in turn rather than guessing.
- Recognise broken object- and function-level authorization (BOLA/BFLA) as the dominant API flaws, and explain why the check must be per-object and server-side.
- Explain how APIs leak through excessive data exposure and mass assignment, and how rate limiting, asset management and logging close the operational gaps.
- Explain why authorization cannot be centralised the way authentication can, and why per-caller logging is what makes the most common API attack visible at all.

---
> 🔼 Up: [[Standards & API]]
