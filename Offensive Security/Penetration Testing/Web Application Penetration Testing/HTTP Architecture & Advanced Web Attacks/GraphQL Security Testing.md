---
title: "GraphQL Security Testing"
aliases: ["GraphQL Security", "GraphQL Testing", "GraphQL Introspection", "GraphQL Injection", "GraphQL Batching"]
tags: [tree/offensive, cyber/offensive/web/graphql, type/technique, difficulty/hard]
Domain: "[[HTTP Architecture & Advanced Web Attacks]]"
Color: "#DC143C"
verified: 2026-09-05
---

# 🕸️ GraphQL Security Testing

> [!warning] Authorized testing only
> GraphQL introspection and batching tests are performed against in-scope applications with a dedicated test account. Batching-based DoS probes are run with a white-team notification and a hard cap on iterations to avoid affecting other users. All object-reference tests use canary records you created.

## Parent Learning Order
Server-Side Request Forgery -> HTTP Request Smuggling -> Web Cache Attacks -> WAF Testing & Bypass Methodology -> GraphQL Security Testing

## When the API Hands You Its Own Map

> *A REST API returns 404 for every undocumented endpoint. A GraphQL endpoint handed you a complete schema the moment you connected. What changed?*
>
> Hold your answer — the section below is the response.

REST APIs hide their surface — an attacker must enumerate endpoints, guess
parameters, and infer types. GraphQL was designed around the opposite principle:
the schema is **self-documenting**, and the built-in **introspection** mechanism
returns the full type system — every query, mutation, field, argument, type, and
description — in a single request. That design decision, valuable for developer
tooling, also hands an attacker a complete map of the application's data model
before sending a single payload.

GraphQL shifts the attack surface in three important ways compared to REST.
**Authorization enforcement** moves from "was this endpoint called correctly" to
"does this resolver check whether the caller can access this specific field or
object" — and frameworks do not enforce that check automatically. **Query
complexity** moves from "how many HTTP requests did the client send" to "how
expensive is this one request to resolve" — and a single deeply-nested or
batched query can consume far more server resources than any realistic rate
limit per request catches. **Injection** still reaches every backend sink that
resolvers touch — SQL, NoSQL, LDAP — through the same taint path as any other
API, but the path is expressed in GraphQL syntax rather than URL parameters.

> [!tip] The analogy, and where it breaks
> A REST API is like a museum with unmarked doors — you only learn what's behind
> each one by trying it. A GraphQL API is like a museum with a full map posted
> at the entrance: you know every room exists, what each one contains, and how to
> get there before you take a step. The analogy breaks on access control: the map
> tells you what rooms exist, not which ones you are allowed to enter — that
> check is only at the door of each room, and if any door is unlocked that should
> not be, the map has already told you exactly where it is.

**Prerequisites:** HTTP basics (the [[OWASP Web Testing Methodology]] note), REST
API testing concepts, and the SQL Injection / NoSQL Injection notes for injection
through resolvers.

## Introspection: reading the full schema

Introspection is a built-in GraphQL feature — not a misconfiguration — but
leaving it enabled in production exposes the entire data model. A single query
retrieves every type, field, and argument:

```graphql
# Full schema dump via introspection
{
  __schema {
    queryType { name }
    mutationType { name }
    types {
      name
      kind
      fields {
        name
        type { name kind ofType { name kind } }
        args { name type { name kind } }
      }
    }
  }
}
```

```shell-session
analyst@lab:/tmp/gql-lab$ curl -s -X POST http://app.meridian.test/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __schema { types { name fields { name } } } }"}' \
  | python3 -m json.tool | grep -A2 '"name": "Order"'
            "name": "Order",
            "fields": [
                {"name": "id"}, {"name": "owner"}, {"name": "total"},
                {"name": "internalCost"}, {"name": "supplierId"}
```

The schema reveals an `internalCost` and `supplierId` field on `Order` objects —
fields the UI never displays. Introspection-derived schema discovery is the first
step in every GraphQL engagement; it takes thirty seconds and surfaces the entire
attack surface.

**When introspection is disabled,** use **field suggestion** — GraphQL returns
"Did you mean X?" for near-misses — and tools like `clairvoyance` to enumerate
the schema by fuzzing field names against the correction hints.

## Field-level authorization: the REST assumption that breaks

REST APIs gate authorization at the endpoint: `GET /orders/{id}` either succeeds
or fails for the caller. GraphQL adds a dimension: **each field in the response
has its own resolver**, and the framework does not automatically verify that the
caller is allowed to see each field. A developer who protects the `Order` query
may forget to protect the `internalCost` field on every resolver that returns
an `Order`.

```graphql
# Legitimate customer query — UI only shows these fields
query {
  order(id: "canary-order-a") {
    id
    total
  }
}

# Same query extended with fields the UI never requests
query {
  order(id: "canary-order-a") {
    id
    total
    internalCost      # should be staff-only
    supplierId        # should be staff-only
  }
}
```

If the server returns `internalCost` and `supplierId` for a customer token, the
resolver is not checking the field against the caller's role — only the top-level
query authorization ran. This is the GraphQL equivalent of a REST endpoint that
checks authentication but not authorization: the request is allowed, but the
*data* returned exceeds what the caller should see.

**Object-level authorization (IDOR through GraphQL)** is the same problem at
the object level: the `order()` query may return the correct fields for the
caller's role but still return objects owned by other users if the resolver
does not filter by `owner == caller`:

```graphql
# caller is customer A; canary-order-b belongs to customer B
query {
  order(id: "canary-order-b") {
    id
    owner
    total
  }
}
# If the server returns the order rather than an authorization error, IDOR is present
```

## Batching and aliasing: multiplying one request's cost

HTTP-level rate limiting counts requests. A single GraphQL request can contain
**many queries** via two mechanisms the spec provides: **batching** (an array of
query objects in the request body) and **aliasing** (multiple queries with
different names in one operation). Both let an attacker issue hundreds of
equivalent queries inside one HTTP request, bypassing per-request rate limits
entirely.

**Batched request (array body):**

```shell-session
analyst@lab:/tmp/gql-lab$ curl -s -X POST http://app.meridian.test/graphql \
  -H "Content-Type: application/json" \
  -d '[
    {"query":"{ order(id:\"canary-1\") { total } }"},
    {"query":"{ order(id:\"canary-2\") { total } }"},
    {"query":"{ order(id:\"canary-3\") { total } }"}
  ]'
[{"data":{"order":{"total":10.0}}},
 {"data":{"order":{"total":20.0}}},
 {"data":{"order":{"total":30.0}}}]
```

Three queries, one HTTP request. Scale to fifty or a hundred to confirm whether
the server imposes a per-request query cap.

**Aliased brute-force** (one operation, many aliases):

```graphql
# Credential testing without triggering per-request rate limits
mutation {
  attempt1: login(user: "admin", pass: "Password1") { token }
  attempt2: login(user: "admin", pass: "Password2") { token }
  attempt3: login(user: "admin", pass: "Password3") { token }
}
```

Each alias calls `login` independently; a server that rate-limits by
`(IP, request)` rather than `(IP, login-call-count)` allows all three. Report
whether the server enforces a per-operation count, not just a per-request limit.

## Injection through resolvers

GraphQL resolvers are just code: a resolver for `order(id: String)` may build a
SQL query, a MongoDB filter, or an LDAP search using the argument value. The same
injection classes apply — **SQL injection, NoSQL injection, LDAP injection** —
but the payload is delivered through a GraphQL argument rather than a URL
parameter or JSON body field:

```graphql
# SQL injection through a GraphQL argument
{
  order(id: "1 UNION SELECT username,password,3,4 FROM users-- -") {
    id
    total
  }
}
```

```shell-session
analyst@lab:/tmp/gql-lab$ curl -s -X POST http://app.meridian.test/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ order(id: \"1 UNION SELECT username,password,3,4 FROM users-- -\") { id total } }"}'
{"data":{"order":{"id":"admin","total":"$2b$12$hunter2hash..."}}}
```

The injection surface is every resolver that builds a backend query from an
argument. The test workflow is the same as for REST APIs: baseline the query,
introduce an injection payload, compare the response structure. A canary row in
the test database (`test_canary_gql`) confines impact and proves the injection.

**SSRF through GraphQL** is a separate vector: a resolver that fetches an
external URL (for a preview, a webhook, an import) may be reachable via a
mutation and can be used to probe internal services:

```graphql
mutation {
  importFromUrl(url: "http://10.10.20.10/") { status }
}
```

## Treating GraphQL's openness as a framework problem, not a misconfiguration

- **Introspection in production.** Disabling introspection does not make fields
  inaccessible — it removes the map, not the doors. Disable it in production to
  reduce recon speed; do not rely on it as a control.
- **Authorization at the resolver, not the gateway.** An API gateway that
  validates the JWT and routes the request to GraphQL does not authorize
  individual fields — that check must be in each resolver. Missing it on one
  resolver leaves the field open to any authenticated caller.
- **Query depth and complexity limits.** An unrestricted nested query
  (`{ orders { items { order { items { order ... } } } } }`) can cause
  exponential resolver work. Test for depth and complexity limits; report their
  absence even if no DoS was reached.
- **Introspection → privilege escalation.** Introspection revealing internal-only
  mutations (e.g., `setUserRole`, `approveInvoice`) that lack authorization
  checks turns the schema map into a direct attack path.
- **Type coercion as injection bypass.** A resolver that expects an integer ID
  and receives a string may pass the string directly to a backend query if type
  enforcement is loose — test with unexpected types, not just injection payloads.

**The deliberate break:** a GraphQL API with introspection disabled feels secured
against discovery.

Introspection is recon, not access. Disabling it slows an attacker who doesn't
know the schema by hours; it does nothing against an attacker who does, or
against a client-side JavaScript bundle that already encodes every query in plain
text. The authorization gap — resolvers that return fields or objects the caller
should not see — exists regardless of whether introspection is on, because the
check is not in the introspection layer. Disabling introspection removes a
convenience; fixing authorization removes the vulnerability.

**How you'd spot incomplete authorization:** send a query as a lower-privileged
account that requests fields or mutations only a higher-privileged account should
access. If the response contains data rather than an authorization error, the
resolver lacks the check. That test does not require introspection — it requires
only knowing that the field or mutation exists, which the application's own
client-side code already reveals.

## Security Implications — the Defender's View

- **Disable introspection in production** (enable in dev/staging only) and use
  field suggestions to detect probing — but treat it as recon reduction, not
  authorization.
- **Field-level authorization in every resolver:** frameworks like GraphQL Shield
  (Node), Strawberry permissions (Python), and graphql-java authorization
  directives add per-field policy enforcement; require it consistently.
- **Query depth and complexity limits:** set a maximum query depth (three to five
  is usually sufficient for product needs) and a complexity budget per request,
  enforced server-side.
- **Disable batching in production** unless the product requires it; if it must
  be enabled, enforce a per-request operation cap (ten is a common default).
- **Rate-limit by operation count, not request count:** rate limiting at the HTTP
  layer counts requests; the graphql-rate-limit library and similar tools count
  resolver invocations per window, which is the correct unit.
- **Log the full query, not just the operation name:** the query body is the
  payload in GraphQL; operation name alone is insufficient for audit.

## Summary

You should now be able to:

- Explain what GraphQL introspection reveals and run a schema dump, then identify candidate fields and mutations not exposed in the UI.
- Test for field-level and object-level authorization gaps by querying fields the caller's role should not see and objects the caller does not own, using canary records.
- Demonstrate batching and aliasing as mechanisms that bypass per-request rate limits, and test resolver inputs for SQL, NoSQL, and LDAP injection using GraphQL argument payloads.

---
> 🔼 Up: [[HTTP Architecture & Advanced Web Attacks]]
