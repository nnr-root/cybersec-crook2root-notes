---
title: "HTTP Fundamentals"
aliases: ["HTTP", "HTTP Methods", "Status Codes", "HTTP Headers", "Cookies", "Statelessness"]
tags:
  - tree/networking
  - cyber/networking/appproto
  - type/concept
  - level/crook
Domain:
  - "[[Web & Application Protocols]]"
Color: "#42D4F4"
---

# 🌐 HTTP Fundamentals

> [!abstract] Note of [[Web & Application Protocols]]
> HTTP is a stateless request/response conversation in plain text, and almost everything confusing about the modern web — cookies, sessions, redirects, caching — is a workaround for that statelessness. This note builds the protocol from its message format upward, so a reader can read a raw exchange and know exactly what each line does.

## Parent Learning Order
HTTP Fundamentals -> HTTPS & the TLS Handshake -> Web Architecture & Proxies -> WebSockets & Real-Time Protocols -> REST & Modern API Transport -> Application Delivery & Load Balancing

## Start at Zero: A Conversation of Requests and Responses

**HTTP (HyperText Transfer Protocol)** is the application-layer protocol of the web. Its model is simple: a **client** sends a **request**, a **server** sends back a **response**, and the exchange is over. The client always speaks first, the server only ever answers, and neither remembers the other once the exchange completes.

That last property — **statelessness** — is the single most important fact about HTTP. Each request is independent and self-contained; the server, by default, has no memory that this client made a previous request. Everything that feels like memory on the web (being logged in, a shopping cart, a preference) is a deliberate mechanism built on top of a protocol that has none.

An HTTP message is text with a strict structure:

```text
<start line>
<header>: <value>
<header>: <value>
<blank line>
<optional body>
```

A request start line is a method, a path, and a version. A response start line is a version, a status code, and a reason phrase. The blank line separates headers from body and is mandatory — it is how a parser knows the headers have ended.

**Prerequisites:** TCP connections and client-server communication.

> [!tip] The analogy, and where it breaks
> Ordering at a counter where the server has complete amnesia between orders, so they hand you a numbered ticket to present next time. The analogy breaks because a physical ticket is awkward to copy, whereas a session cookie is just a short string — anyone who obtains it simply *is* you, with no further check. That is why the cookie flags restricting where and how it travels are the actual security control.

## A Request and Its Response

```bash
curl -v https://shop.example.com/cart -H 'Cookie: session=abc123'
```

The request on the wire:

```text
GET /cart HTTP/1.1
Host: shop.example.com
User-Agent: curl/8.4.0
Accept: */*
Cookie: session=abc123
```

The response:

```text
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
Content-Length: 1274
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax
Cache-Control: private, max-age=0

<!doctype html>...
```

Read every line as doing a job. `GET /cart` states the method and resource. **`Host:` is mandatory in HTTP/1.1** because one IP address serves many sites, and the Host header is how the server knows which one you want — a detail that becomes central to virtual hosting and to certain attacks. `Content-Type` tells the client how to interpret the body. `Content-Length` states the body size so the parser knows where the message ends. `Set-Cookie` is the server asking the client to remember something — the workaround for statelessness in action.

## Methods and What They Promise

The method declares the intent of the request, and two properties of methods matter for correctness and security.

| Method | Purpose | Safe? | Idempotent? |
| --- | --- | --- | --- |
| **GET** | Retrieve a resource | Yes | Yes |
| **HEAD** | Like GET, headers only | Yes | Yes |
| **POST** | Submit data, create | No | No |
| **PUT** | Replace a resource | No | Yes |
| **PATCH** | Partially modify | No | No |
| **DELETE** | Remove a resource | No | Yes |
| **OPTIONS** | Ask what is allowed | Yes | Yes |

**Safe** means the request should not change server state — a GET should never delete anything. **Idempotent** means repeating it has the same effect as doing it once — PUT to the same resource twice leaves it in one defined state, while two POSTs may create two records.

These are not pedantry. Caches, proxies, and browsers are permitted to retry idempotent requests automatically and to cache safe ones. An application that performs deletion on a GET violates the contract, and the consequence is real: a link prefetcher or a crawler following that GET will delete data without a human ever clicking. The method's promise is relied upon by infrastructure the developer never sees.

## Status Codes

The response status code is a three-digit number whose first digit is its class:

| Class | Meaning | Common examples |
| --- | --- | --- |
| **1xx** | Informational | 101 Switching Protocols (used by WebSockets) |
| **2xx** | Success | 200 OK, 201 Created, 204 No Content |
| **3xx** | Redirection | 301 Moved Permanently, 302 Found, 304 Not Modified |
| **4xx** | Client error | 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found, 429 Too Many Requests |
| **5xx** | Server error | 500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable |

The 4xx/5xx boundary is a genuine diagnostic split: **4xx means the client's request was wrong; 5xx means the server failed to handle a valid request.** A 502 or 504 specifically points at a proxy or gateway failing to reach a backend, which localizes a problem to the infrastructure between the client and the application. Reading status codes correctly is often the fastest triage in a web incident.

Two are routinely confused: **401 Unauthorized** actually means *unauthenticated* (you have not proven who you are), while **403 Forbidden** means *authenticated but not permitted* (you are known, and still not allowed). The names are historical and misleading; the distinction is real.

## Cookies: Memory Bolted On

Because HTTP is stateless, the server issues a **cookie** — a small value it asks the client to store and send back on subsequent requests. The cookie is how the server recognizes a returning client and links independent requests into a session.

```text
Set-Cookie: session=abc123; HttpOnly; Secure; SameSite=Lax; Max-Age=3600
```

The attributes are security controls, and each closes a specific hole:

- **`HttpOnly`** — the cookie is invisible to JavaScript, so a script injected into the page cannot read the session token. This blunts session theft via cross-site scripting.
- **`Secure`** — the cookie is only ever sent over HTTPS, so it never travels in cleartext where an on-path attacker could read it.
- **`SameSite`** — the cookie is withheld (or restricted) on cross-site requests, which is the primary defense against a malicious site triggering authenticated actions on yours.
- **`Max-Age` / `Expires`** — bounds the cookie's lifetime.

A session cookie without `HttpOnly` and `Secure` is a session waiting to be stolen. These flags are set by the server in one header, and their absence is a common, high-impact finding.

```mermaid
sequenceDiagram
    participant B as Browser
    participant S as Server
    B->>S: POST /login (credentials)
    S-->>B: 200 OK + Set-Cookie: session=abc123; HttpOnly; Secure
    Note over B: Stores cookie
    B->>S: GET /account + Cookie: session=abc123
    Note over S: Looks up session abc123 -> "this is Alice"
    S-->>B: 200 OK (Alice's account)
```

The diagram is the whole trick: the server has no memory, so it hands the browser a token and relies on the browser to present it each time, reconstructing "who this is" on every request from that token alone.

## Security Implications

**HTTP is cleartext, which is why HTTPS is mandatory.** Every header and body, including cookies and submitted credentials, is readable and modifiable by anyone on the path. HTTP exists in this note to be understood; in production it must be wrapped in TLS, and an unencrypted login form is a credential leak by design.

**The Host header is trusted input.** Because the server uses `Host:` to route the request and often to build absolute URLs (password-reset links, redirects), an attacker who controls it can sometimes poison caches or redirect security-sensitive links to their own domain. The header is client-supplied and must be validated against an allowlist, not reflected blindly.

**Headers carry security policy.** Beyond cookies, response headers instruct the browser's own defenses: `Strict-Transport-Security` forces HTTPS, `Content-Security-Policy` constrains what scripts may run, `X-Content-Type-Options` stops content-type guessing. These turn the browser into an ally, and their absence leaves defenses off. They cost one header each.

**Method and status semantics are a contract infrastructure relies on.** Violating safe/idempotent semantics invites automated systems to cause harm, and misusing status codes breaks caching and monitoring. Correct semantics is a correctness and security property, not style.

**Verbose responses leak.** Detailed error bodies, `Server:` version banners, and stack traces in 5xx responses hand an attacker reconnaissance. Production responses should be terse.

All probing described here must target only web systems within an authorized scope. HTTP requests are logged, and testing applications you do not own requires explicit authorization under the relevant engagement.

## Authorized Lab: Read the Raw Protocol

Use a lab web server you control and a client. The goal is fluency reading raw HTTP, not exploitation.

1. **Inspect a full exchange.** Request a page with headers shown and identify every line's role:

```bash
curl -v http://<lab server>/ 2>&1 | sed -n '1,40p'
```

Locate the request line, the mandatory `Host:` header, the blank line, and the response status and headers.

2. **Compare methods.** Send a `HEAD` and a `GET` for the same resource and confirm `HEAD` returns identical headers with no body — demonstrating the safe/idempotent pair.
3. **Trigger each status class.** Request a real page (200), a missing page (404), a protected page without credentials (401), and cause a backend error (500). Confirm the first digit classifies the outcome and that 4xx and 5xx localize the fault differently.
4. **Watch cookies establish a session.** Log in to a lab app and capture the `Set-Cookie` response, then a follow-up request carrying `Cookie:`. Confirm the server recognizes the session from the token alone.
5. **Observe the flags.** Inspect the `Set-Cookie` attributes. Remove `HttpOnly` and `Secure` on the server, and confirm via the browser tools that the cookie becomes script-readable and is sent over plain HTTP — making the flags' purpose concrete. Restore them.
6. **Test Host handling.** Send a request with an unexpected `Host:` value and observe whether the app reflects it into any generated URL. Confirm a well-configured app validates it.
7. **Cleanup.** Restore cookie flags and any server configuration changed during the lab.

Expected interpretation:

```text
Raw exchange   -> request line, mandatory Host, blank line, status, headers, body
HEAD vs GET    -> identical headers, no body; the safe/idempotent contract
Status classes -> first digit triages; 4xx client fault vs 5xx server/gateway fault
Set-Cookie     -> the stateless workaround: server remembers via a token the client returns
Missing flags  -> cookie readable by script and sent in cleartext; the flags are the control
```

## Crook → Operator → Root Checkpoint

- **Crook:** Explain HTTP's request/response model and statelessness, and how cookies create the illusion of memory; read a raw request and response and name each part.
- **Operator:** Interpret methods by their safe/idempotent properties and status codes by class, distinguishing a client fault from a server or gateway fault; explain what each cookie flag defends against.
- **Root:** Explain why the Host header is trusted client input and how it enables cache poisoning and redirect abuse; describe how response headers delegate policy to the browser, and why violating method semantics invites automated systems to cause harm.

---
> 🔼 Up: [[Web & Application Protocols]]
