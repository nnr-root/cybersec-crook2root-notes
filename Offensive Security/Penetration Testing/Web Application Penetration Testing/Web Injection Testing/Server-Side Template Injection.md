---
aliases: [SSTI]
title: "Server-Side Template Injection"
tags: [tree/offensive, cyber/offensive/web/injection/ssti, type/technique, difficulty/hard]
Domain: "[[Web Injection Testing]]"
Color: "#DC143C"
---

# Server-Side Template Injection

> [!warning] Authorized validation only
> Use arithmetic and inert canary rendering in an approved fixture. Do not traverse object graphs toward process execution, access secrets, write files, or invoke operating-system functions.

## Parent Learning Order
SQL Injection -> NoSQL Injection -> ORM Injection -> Operating System Command Injection -> Server-Side Template Injection -> LDAP Injection -> XPath Injection -> CRLF Injection -> SSI Injection

## Core Vulnerability & Parser Mechanics (Zero)

> *Your input is rendered by a template engine. At what moment does it stop being data?*
>
> Hold your answer — the section below is the response.

Server-side template injection (SSTI) occurs when untrusted text is treated as **template source** rather than as a data value rendered by a trusted template. A template engine is a language implementation: it tokenizes delimiters and text, parses expressions or directives into an AST, compiles or interprets nodes, resolves variables against a context, applies filters or methods, and writes output. If user input reaches the source-compilation phase, the user controls expression nodes. If it reaches only a context variable, delimiter characters remain ordinary data.

The difference can be shown with two designs. Safe code loads a fixed template such as `Hello {{ display_name }}` and supplies `{display_name: userInput}`. The engine parses only developer-controlled source; autoescaping can encode the resulting value for HTML. Vulnerable code builds `Hello ` + userInput and passes the combined string to `renderTemplateString`. The untrusted bytes are now present when the lexer recognizes `{{`, `${`, `<%=`, or engine-specific directive syntax.

Engine identification matters because syntax and capability differ. Jinja2 uses Python-like expressions and filters; Twig is a PHP ecosystem engine; FreeMarker and Velocity are common in Java; Thymeleaf processes attribute and expression dialects; EJS embeds JavaScript; Go templates expose functions explicitly registered by the application. A mathematical probe that renders `49` establishes expression evaluation but does not by itself establish access to dangerous objects. The next analytical question is the **capability surface**: which variables, functions, classes, loaders, or adapters are exposed, and what sandbox or policy mediates them?

Sandboxing is a reference-monitor problem. It must mediate property lookup, method calls, indexing, filters, imports, reflection, and object conversion. Blocklisting class names is fragile because equivalent object paths or framework helpers may reach the same capability. Sandboxes have historically failed through unsafe globals, reflection, method resolution, deserialization, or differences between compile-time and runtime checks. Defensive validation should inventory exposed capabilities in a lab through benign types and canary values, not attempt code execution.

SSTI is separate from client-side template injection. The key evidence is that evaluation occurs on the server before the HTTP response is sent, often with access to server-side context. It also differs from ordinary XSS: `{{7*7}}` rendered as `49` proves a server expression parser, while the same text reflected literally does not. Autoescaping addresses output encoding and does not prevent source injection.

Normalization may create parser differential. The WAF can inspect percent-encoded delimiters while the framework decodes them before template compilation. Unicode normalization may turn compatibility characters into delimiter-like ASCII in an unusual pipeline. Multiple rendering passes are particularly risky: content safely escaped during one pass can become source in a later pass. The report should trace every render stage and record whether input is source, context data, or already-rendered output.

## Visual Attack Flow

```mermaid
sequenceDiagram
    autonumber
    participant T as Authorized Tester
    participant L as Load Balancer
    participant W as WAF
    participant A as Web Controller
    participant C as Template Compiler
    participant X as Expression Evaluator
    participant V as Canary Context
    participant S as SOC & APM
    T->>L: Baseline displayName=C2R-USER
    L->>W: Decoded request and ID
    W->>A: Allowed value
    A->>C: Compile concatenated template source
    C->>C: Tokenize text and expression delimiters
    C->>X: AST containing attacker expression
    X->>V: Resolve permitted arithmetic/context values
    V-->>X: Bounded canary result
    X-->>A: Rendered page
    A-->>T: Literal text or evaluated 49
    C-->>S: Template name, source hash & parse event
    A-->>S: Route, request ID & rendering exception
    Note over T,S: Evaluation proves source control; it does not authorize capability escalation
```

For a safe implementation, the compiler receives a constant source hash on every request and only the context value changes. A request-dependent template source hash is a powerful architectural detection signal.

## Weaponization & Practical Execution (Mastery)

### Engine-neutral arithmetic fingerprint

Baseline:

```http
POST /lab/greeting/preview HTTP/1.1
Host: portal.example.test
Content-Type: application/x-www-form-urlencoded
X-Assessment-ID: C2R-SSTI-010

displayName=C2R-USER
```

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<p>Hello C2R-USER</p>
```

Jinja2/Twig-style arithmetic probe:

```http
POST /lab/greeting/preview HTTP/1.1
Host: portal.example.test
Content-Type: application/x-www-form-urlencoded
X-Assessment-ID: C2R-SSTI-010

displayName=%7B%7B7%2A7%7D%7D
```

Vulnerable response:

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
X-Template-Engine: lab-jinja

<p>Hello 49</p>
```

Secure response:

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

<p>Hello &#123;&#123;7*7&#125;&#125;</p>
```

If an engine is unknown, compare inert arithmetic forms one at a time: `{{7*7}}`, `${7*7}`, and `<%= 7*7 %>`. Do not spray broad payload lists. Error messages may safely reveal a family in the lab:

```text
jinja2.exceptions.TemplateSyntaxError: unexpected '}'
template_source_hash=9fca... request_id=req-tpl-448
```

### Context-versus-source control

A useful negative test places the same marker into a fixed template variable and verifies literal rendering. Application instrumentation should show:

```text
SAFE:   template=greeting.html source_hash=constant context.display_name="{{7*7}}"
UNSAFE: template=<dynamic> source_hash=request-dependent ast_nodes=[Text, Mul]
```

This evidence demonstrates root cause more clearly than a large payload corpus. URL-encoded `%7B%7B`, double-encoded `%257B%257B`, duplicate form fields, JSON bodies, and Unicode compatibility forms can be tested to map decoding. The desired fix behaves safely regardless of representation because it never compiles the value.

### Bounded differential validator

```python
import requests

URL = "https://portal.example.test/lab/greeting/preview"
HEADERS = {"X-Assessment-ID": "C2R-SSTI-010"}

tests = [
    ("literal", "C2R-USER"),
    ("jinja_like", "{{7*7}}"),
    ("dollar_like", "${7*7}"),
    ("ejs_like", "<%= 7*7 %>"),
]

for name, value in tests:
    r = requests.post(URL, data={"displayName": value}, headers=HEADERS, timeout=3)
    print(name, r.status_code, "evaluated-49=", ">49<" in r.text,
          "literal=", value in r.text)
```

```text
literal    200 evaluated-49=False literal=True
jinja_like 200 evaluated-49=True  literal=False
dollar_like 200 evaluated-49=False literal=True
ejs_like   200 evaluated-49=False literal=True
conclusion: Jinja/Twig-family expression evaluation; stopped at arithmetic
```

Remediation uses immutable template files or trusted source stored outside user control, data-only context, minimal registered functions, autoescaping for the destination, and sandboxing as defense in depth. Remove dynamic rendering helpers from request paths. If user-authored presentation is a product requirement, use a deliberately limited non-Turing-complete grammar with explicit AST validation and isolated rendering.

## Red Team OpSec & Impact

An authorized tester assessed an email-preview feature that accepted a display name. Ordinary HTML was encoded, suggesting output escaping, but `{{7*7}}` became `49`. The tester tried a malformed closing delimiter to obtain a controlled template exception, confirmed a Jinja-family parser in restricted logs, and stopped without object traversal. Code review showed that developers concatenated user fields into a template string before rendering because the preview supported dynamic localization.

The WAF did not block the arithmetic expression because braces were common in legitimate JSON and frontend templates. Application telemetry was more informative: the template source hash varied per request, compilation occurred on an endpoint expected to render a fixed template, and parse exceptions clustered around the same principal. A SIEM analytic should correlate encoded template delimiters, arithmetic/operator density, template parse exceptions, dynamic source hashes, and unusual rendering latency. HTTP 500 with `TemplateSyntaxError` is high signal; HTTP 200 with deterministic transformation from `{{7*7}}` to `49` is visible only through synthetic monitoring or response-aware assessment telemetry.

The SOC also monitors for application workers spawning child processes or making unexpected outbound connections, which would indicate a capability breach beyond arithmetic validation. Those postconditions should never be required to prove the root cause. Relevant fields include route, template engine, template name, source hash, AST node classes where available, context schema, request ID, WAF score, status code, response bytes, render duration, and worker process telemetry.

The engineering team moved localization and user values into a fixed template context, removed the dynamic render-string helper, restricted registered functions, and added unit tests asserting that delimiters render literally. Purple-team replay tested percent encoding, double encoding, duplicate fields, alternate content types, and a second rendering pass. All produced literal output, a constant source hash, and no compiler exception.

## Summary

You should now be able to:

- Explain why `{{7*7}}` becomes `49` here but would stay literal if `name` were a context variable.
- Take the next *non-destructive* step after `49` comes back to identify the engine — Jinja2, Twig or Freemarker — and explain why the engine matters.
- Sandboxed engines still get broken. Explain the general shape of a sandbox escape (attribute/method traversal to a callable) and why denylists of attribute names fail.

---
> 🔼 Up: [[Web Injection Testing]]
