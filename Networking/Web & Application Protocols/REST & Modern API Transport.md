---
title: "REST & Modern API Transport"
aliases: ["REST", "RESTful API", "gRPC", "GraphQL Transport", "API Design", "Content Negotiation"]
tags:
  - tree/networking
  - cyber/networking/appproto
  - type/concept
  - difficulty/medium
Domain:
  - "[[Web & Application Protocols]]"
Color: "#42D4F4"
---

# 🔗 REST & Modern API Transport

> [!abstract] Note of [[Web & Application Protocols]]
> APIs are how programs talk over HTTP, and the transport style shapes what a client can request, how errors surface, and where authorization must live. This note covers REST as the dominant style and the two major alternatives, focusing on the transport and networking concerns — the vulnerability catalogue for each belongs to the API-security material in the offensive and appsec domains.

## Parent Learning Order
HTTP Fundamentals -> HTTPS & the TLS Handshake -> Web Architecture & Proxies -> WebSockets & Real-Time Protocols -> REST & Modern API Transport -> Application Delivery & Load Balancing

## An API Is a Contract Between Programs

> *An API and a web page both travel over HTTP. What actually changes?*
>
> Hold your answer — the section below is the response.

A web page is for humans; an **API (Application Programming Interface)** is for programs. Instead of returning HTML to render, an API returns structured data — usually JSON — that another program parses and acts on. The transport is still HTTP, so everything from the HTTP branch applies; what differs is that the consumer is code, which changes the design pressures.

**REST (Representational State Transfer)** is the dominant style, and it is a set of conventions layered on HTTP rather than a separate protocol. Its core idea is to model everything as a **resource** identified by a URL, and to use HTTP methods as the verbs acting on those resources.

```text
GET    /api/orders          -> list orders
POST   /api/orders          -> create an order
GET    /api/orders/42       -> retrieve order 42
PUT    /api/orders/42       -> replace order 42
PATCH  /api/orders/42       -> modify order 42
DELETE /api/orders/42       -> delete order 42
```

This is why the HTTP method semantics from earlier matter concretely: in REST, GET must be safe and idempotent, DELETE must be idempotent, and the whole design relies on those promises so that caches and clients can reason about requests. A REST API that deletes on GET breaks the model at a fundamental level.

REST leans on HTTP's own machinery rather than reinventing it:

- **Status codes** carry outcome: 200 success, 201 created, 400 bad input, 401 unauthenticated, 403 unauthorized, 404 not found, 429 rate-limited.
- **Content negotiation** via the `Accept` header lets a client request a format and the server respond with `Content-Type` describing what it sent.
- **Statelessness** is preserved: each request carries everything needed to process it, typically including an authentication token, because the server remembers nothing between requests.

```bash
curl -s https://api.meridian.test/orders/42 \
  -H 'Authorization: Bearer eyJhbGci...' \
  -H 'Accept: application/json'
```

Expected excerpt:

```text
HTTP/2 200
content-type: application/json

{"id":42,"status":"shipped","total":51.25}
```

The `Authorization: Bearer` header carries the token that identifies the caller. Because the API is stateless, that token accompanies **every** request — there is no session the way a cookie-based web app has one. This is the central transport difference and it drives the security model.

```mermaid
flowchart TD
    R["API request with Bearer token"] --> AUTHN{"Token valid? (authentication)"}
    AUTHN -->|"No"| E401["401 Unauthenticated"]
    AUTHN -->|"Yes"| AUTHZ{"May THIS caller access THIS object? (authorization)"}
    AUTHZ -->|"No"| E403["403 Forbidden"]
    AUTHZ -->|"Yes"| OK["200 + data"]
    AUTHZ -.->|"skipped — the classic flaw"| LEAK["Returns another user's object"]
```

The diagram isolates the single most damaging API mistake: performing the authentication check (is the token valid?) but skipping the per-object authorization check (does this caller own this object?). The dashed path is broken object-level authorization, and it is where most real API breaches occur.

### One request, one finding

The dashed path is testable in the time it takes to edit a URL. Fetch your own order with your own token:

```bash
curl -s https://api.meridian.test/orders/42 -H 'Authorization: Bearer eyJhbGci...'
```

```text
{"id":42,"account":"r.okonkwo","status":"shipped","total":51.25}
```

Now change one character and send the identical token again:

```bash
curl -s https://api.meridian.test/orders/41 -H 'Authorization: Bearer eyJhbGci...'
```

```text
{"id":41,"account":"d.varga","status":"processing","total":1840.00}
```

That is the finding, complete. No credential was stolen, no token was forged, nothing was injected, and the request is well-formed in every respect — it is the same request that worked a moment ago with a different number in it. The API answered honestly: the token is valid, so here is order 41.

Note what makes this so much worse than it looks. The identifiers are sequential, so `/orders/1` through `/orders/41` is a loop rather than an attack, and the response body names the account it belongs to, which turns the leak into a customer list. And every network control in the chain sees a properly authenticated request to a legitimate endpoint — a WAF has nothing to match, a rate limiter sees one user's normal traffic pattern, and the access log records a successful authorised call.

The failure is a missing clause in a database query. Nothing outside the application can supply it, which is why this class of flaw appears at the top of every API risk list and why it is not, in any useful sense, a network problem — it just happens to be reachable over the network.

**Prerequisites:** HTTP methods, status codes, and TLS.

> [!tip] The analogy, and where it breaks
> A vending machine with clearly labelled slots, versus a waiter to whom you describe exactly what you want. The analogy breaks on the flaw that matters: a vending machine checks that your coin is valid but never checks whether the item is *yours*. An API that validates the token and then returns record 42 without asking whether this caller owns record 42 is making exactly that mistake.

## The Alternatives and Why They Exist

REST is not the only style, and each alternative arose to fix a specific REST limitation.

**GraphQL** addresses over- and under-fetching. In REST, an endpoint returns a fixed shape, so a client often gets more than it needs (over-fetching) or must make several requests to assemble what it needs (under-fetching). GraphQL exposes a single endpoint where the client sends a **query describing exactly the fields it wants**, and the server returns precisely that. The transport consequence is distinctive: it is typically one URL, usually POST, so REST-style controls that key on method and path — per-endpoint rate limits, path-based WAF rules, method restrictions — largely do not apply. Security must understand the query, not the URL.

**gRPC** optimizes service-to-service communication. It uses HTTP/2 as transport and a compact binary serialization (Protocol Buffers) instead of JSON, with a defined schema. It is fast and strongly typed, ideal between backend microservices, but the binary framing means ordinary HTTP tooling cannot read it without the schema, and it depends on HTTP/2 features that not all intermediaries handle.

| Style | Transport | Shape | Best for |
| --- | --- | --- | --- |
| **REST** | HTTP, any version | JSON, resource per URL | Public APIs, broad compatibility |
| **GraphQL** | HTTP, one endpoint, usually POST | Client-specified query | Rich clients avoiding over/under-fetch |
| **gRPC** | HTTP/2, binary | Schema-defined messages | Internal service-to-service |

The networking takeaway is that **the transport style determines where and how controls apply.** A rate limit that works per-REST-endpoint does not translate to GraphQL's single endpoint; an inspection tool that reads JSON cannot read gRPC without the schema. Choosing a style is partly choosing a security posture.

## Versioning and Evolution

APIs have consumers who cannot be updated in lockstep, so they must evolve without breaking existing clients. Versioning appears in the path (`/v2/orders`), a header, or a media type. The networking-relevant point is that **multiple versions run simultaneously**, and an old version left running is an old attack surface — deprecated API versions with weaker validation or authentication are a recurring finding. Retiring versions is a security activity, not just maintenance.

**The deliberate break:** a valid token reads as authorisation. The request authenticated cleanly, the signature checks out, therefore the call is allowed.

Authentication answers **who is calling**; authorisation answers **whether this caller may touch this object**, and they are separate questions asked at different moments. The most common and most damaging API flaw in practice is asking the first faithfully on every request and never asking the second per object — accepting a valid token and returning record 42 without ever confirming that this caller owns record 42. The transport delivered a credential; it made no claim about entitlement, and no network control can supply that check on the application's behalf.

**How you'd spot it:** change the identifier and keep the token. Request an object belonging to another account using your own entirely valid credentials — if it comes back, object-level authorisation is absent, and that is the finding in one request. In code the tell is just as plain: a handler that validates the token at the top, then fetches by ID with no ownership predicate anywhere in the query.

## Security Implications

**Authorization must be enforced per request, on the server, for every object.** Because APIs are stateless and each request carries a token, the server must verify on **every** request both that the token is valid (authentication) and that this caller may access *this specific resource* (authorization). The most common and damaging API flaw is checking authentication but not object-level authorization — accepting a valid token and then returning object 42 without confirming the caller owns object 42. The transport delivers the token; the application must still ask "may *this* caller see *this* thing," every time. No network control substitutes for that check.

**The token is a bearer credential and must be protected in transit and at rest.** A `Bearer` token grants access to whoever holds it — there is no further proof of identity. Intercept it and you are the user. This makes TLS non-negotiable for APIs and makes token leakage (in logs, in URLs, in referrer headers) directly equivalent to account compromise. Tokens belong in the `Authorization` header, never in the URL where they land in logs and history.

**Rate limiting is essential and style-dependent.** Because APIs are consumed by programs, they are trivially hammered — for credential stuffing, scraping, or denial of service. Rate limiting per client and per operation is a core control, and it must be designed for the transport style: per-endpoint for REST, per-query-cost for GraphQL (where one crafted query can demand enormous work), per-method for gRPC.

**Error responses leak, and verbose APIs leak more.** APIs returning detailed errors, internal identifiers, or full object graphs hand attackers a map. Responses should return only what the caller needs and errors should be informative to a legitimate developer without revealing internal structure.

**Schema and discovery are double-edged.** GraphQL introspection and gRPC schemas make APIs self-documenting, which helps legitimate developers and attackers equally. Disabling introspection in production and controlling schema exposure limits the reconnaissance an attacker gets for free.

All API testing described here must target only systems within an authorized scope. Enumerating objects, testing authorization, and rate-limit probing are intrusive and require explicit authorization.

## Summary

You should now be able to:

- Explain what an API is and how REST models resources with URLs and HTTP methods; state why REST relies on the safe/idempotent method contract.
- Make authenticated REST requests and read status-code outcomes; explain why the token accompanies every request and why REST-style controls do not translate directly to GraphQL's single endpoint.
- Explain why per-request, per-object authorization is the API's essential control and why no network layer substitutes for it; describe how transport style dictates where rate limiting and inspection apply, and why deprecated versions and verbose errors are transport-level attack surface.

---
> 🔼 Up: [[Web & Application Protocols]]
