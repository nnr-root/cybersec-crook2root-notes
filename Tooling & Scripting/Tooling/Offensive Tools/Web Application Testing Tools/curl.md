---
title: "curl"
aliases: ["curl"]
tags: [tree/tooling, cyber/tooling/offensive/web/curl, type/tool, difficulty/medium]
Domain: "[[Web Application Testing Tools]]"
Color: "#708090"
---

# curl

curl is the universal command-line HTTP client — the tool that lets you *hand-craft a single request* and read the raw response. Burp and ZAP are indispensable for interception, but curl is where you truly learn HTTP: every header, method, and byte of the body is explicit and under your control. It is also the backbone of scripted testing, reproducible bug reports, and CI checks.

> [!warning] Authorized targets only
> curl sends exactly what you tell it — including attack payloads. Point it only at systems you may test, and keep an assessment header on test traffic.

## Parent Learning Order
curl -> Postman -> Burp Suite -> OWASP ZAP -> Nikto -> WPScan -> SQLmap

## Four parts of a request, four parts of a response

> *A request and a response share the same four parts. Name them.*
>
> Hold your answer — the section below is the response.

Every web interaction is a **request** that produces a **response**, and each has the same four parts: a start line, headers, a blank line, and an optional body. curl builds the request; the flags map one-to-one onto the parts.

Read the diagram left to right and you have curl's core flags: `-X` sets the method, `-H` adds a header, `-d` sends a body, and `-i` shows you the response status line and headers. Understand this picture and curl stops being a wall of flags and becomes "type out the message you want to send."

## The everyday verbs, starting with -I

The everyday verbs. `-I` fetches only headers (a `HEAD` request) — the fastest way to fingerprint a server:

```shell-session
operator@lab:~$ curl -sI https://app.example.test
HTTP/2 200
server: nginx
content-type: text/html; charset=UTF-8
set-cookie: session=…; HttpOnly; Secure; SameSite=Lax
strict-transport-security: max-age=31536000
```

That single response already tells a tester a lot: HTTP/2, nginx, and — importantly — the cookie flags and HSTS that a security review checks. Send data with `-d` (implies `POST`) and add headers with `-H`:

```shell-session
operator@lab:~$ curl -i -X POST https://app.example.test/api/login \
    -H 'Content-Type: application/json' \
    -d '{"user":"alice","pass":"s3cret"}'
HTTP/2 401
www-authenticate: Bearer
{"error":"invalid credentials"}
```

Read what rejected that, because it decides where you look next. The `401` came
from the application, not from nginx and not from TLS: the request completed, the
server parsed the JSON body, looked `alice` up, and the credential check failed.
`www-authenticate: Bearer` is the server naming the scheme it wants — so the
endpoint expects a token, and username/password in the body was never going to
work. A `401` from the proxy would have carried no `www-authenticate` and usually
an HTML body; a TLS failure would never have produced an HTTP status at all.
Distinguishing those three is most of what `-i` is for.

The flags you will use constantly:

| Flag | Does |
|---|---|
| `-i` / `-I` | include response headers / headers only |
| `-X` | set method (GET, POST, PUT, DELETE…) |
| `-H` | add a request header |
| `-d` / `--data-raw` | send a body |
| `-L` | follow redirects |
| `-o` / `-O` | write body to a file |
| `-w` | print variables (`%{http_code}`, `%{time_total}`) |
| `-k` | skip TLS certificate verification (dangerous) |
| `-b` / `-c` | send / save cookies |

`-w` turns curl into a measurement tool — perfect for scripted checks:

```shell-session
operator@lab:~$ curl -s -o /dev/null -w 'code=%{http_code} time=%{time_total}s size=%{size_download}B\n' https://app.example.test
code=200 time=0.142s size=1256B
```

## What -k costs you, and why that is the lesson

curl exposes the protocol *honestly*, which is exactly why it teaches. Consider TLS verification — the difference between `-k` and its absence is a security lesson:

```shell-session
operator@lab:~$ curl -sI https://192.0.2.10
curl: (60) SSL certificate problem: unable to get local issuer certificate /
      subjectAltName does not match 192.0.2.10
operator@lab:~$ curl -skI https://192.0.2.10
HTTP/2 200
```

**The deliberate break:** the first request *fails* because the certificate's SubjectAltName doesn't match the IP — curl is doing its job, refusing to trust an unverified endpoint. Adding `-k` "fixes" it by disabling verification — and that is the trap. `-k` is fine for a lab against your own self-signed box, but reaching for it reflexively is how MITM attacks succeed. curl makes the security decision *visible*; a browser hides it behind a warning page.

Other internals worth mastering: curl does **not** follow redirects unless you pass `-L` (so a `301` shows you the redirect, not the destination — useful for testing open redirects); `-d` URL-encodes form data but `--data-raw` does not (matters for injection payloads); and `--resolve` / `-H 'Host:'` let you test **virtual-host routing** and reach a specific backend behind a load balancer. For untrusted input, remember curl is a *shell* command — never build a curl line by concatenating unescaped user data (a lesson from **Bash**).

## Summary

You should now be able to:

- Name the four parts of an HTTP request, and the curl flag that builds each.
- You need the status code and response time of an endpoint, nothing else. Write the curl command.
- Explain what `-k` disables and why reaching for it reflexively is dangerous, using the SAN-mismatch failure as your example.

---
> 🔼 Up: [[Web Application Testing Tools]]
