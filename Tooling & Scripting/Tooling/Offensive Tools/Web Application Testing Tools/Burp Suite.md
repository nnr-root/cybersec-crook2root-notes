---
title: "Burp Suite"
aliases: ["Burp"]
tags: [tree/tooling, cyber/tooling/offensive/web/burp, type/tool, level/root]
Domain: "[[Web Application Testing Tools]]"
Color: "#708090"
---

# Burp Suite

Burp Suite is the intercepting-proxy platform at the centre of web application testing. It sits between your browser and the target, capturing every request so you can pause it, edit it, replay it, and automate it. Community Edition gives the full manual workflow; Professional adds the automated Scanner. If you learn one web tool deeply, it is this one.

> [!warning] Authorized application testing
> Set target scope *before* browsing. Never let Scanner, Intruder, or extensions reach third-party domains or production actions excluded by the Rules of Engagement.

## Parent Learning Order
curl -> Postman -> Burp Suite -> OWASP ZAP -> Nikto -> WPScan -> SQLmap

## Crook — The Mental Model

Every web tool operates at a *point* in the request path. Burp's point is the most powerful one: **the middle**.

![[tool_web_request_path.svg]]

Positioned as the proxy between client and server, Burp sees the *real* traffic your browser generates — then lets you grab any request and change it before it reaches the server. That is the whole superpower: the browser enforces client-side rules (hidden fields, JS validation, disabled buttons); Burp lets you ignore all of them and send exactly the bytes you want. The application's *server-side* behaviour is what you're really testing, and the proxy is how you reach it.

## Operator — Make It Work

**Set up:** proxy listener on `127.0.0.1:8080`, point the browser at it, import Burp's CA into a dedicated test profile, and define scope so you only touch the target:

```text
Proxy listener: 127.0.0.1:8080     Target scope: https://app.example.test/*
Out-of-scope:   analytics.example.net, payment-provider.example
```

**The core loop** is Proxy → Repeater. Capture a request, send it to Repeater, then hand-edit and replay while comparing responses:

```http
GET /api/v1/profile HTTP/1.1
Host: app.example.test
Cookie: session=REDACTED

HTTP/1.1 200 OK
{"id":"test-user-01","role":"user"}
```

Change `test-user-01` to another ID and compare status/length/body — that's an access-control test in three clicks. The tools you'll reach for:

| Tool | Use |
|---|---|
| **Proxy / HTTP history** | capture, intercept, annotate |
| **Repeater** | hand-edit & replay *one* request |
| **Intruder** | automated payloads across positions |
| **Decoder / Comparer** | transform data, diff responses |
| **Collaborator** | detect blind out-of-band (SSRF, blind XXE) |
| **Scanner** (Pro) | automated passive/active checks |

## Root — Internals & The Deliberate Break

Intruder's four attack types are a common trap, and picking wrong turns a quick test into a self-DoS:

```text
Sniper:        1 position, 1 list       — N requests
Battering Ram: same payload, all pos    — N requests
Pitchfork:     parallel lists, paired   — N requests
Cluster Bomb:  every combination        — N × M requests
2 positions × 500 payloads (Cluster Bomb) = 250,000 requests ≈ 14h at 5/s
```

**The deliberate break:** a Cluster Bomb across two 500-item lists is a quarter-million requests — hours of traffic that will get you rate-limited or noticed, when Pitchfork (500 paired requests) was what you actually wanted. Always compute the request count before launching. The deeper discipline point: a **Scanner-generated issue is a hypothesis, not a finding** — Burp guesses, and every automated "SQL injection" or "XSS" must be manually reproduced in Repeater and tied to real impact before it enters a report. The whole tool rewards the workflow *map with the proxy → confirm by hand in Repeater → only then automate*, exactly the flow in the diagram above.

One more internal that bites everyone: HTTPS interception fails until Burp's CA is trusted, and **certificate pinning** or HTTP/3 (QUIC) can bypass the proxy entirely — if traffic vanishes from HTTP history, suspect QUIC or a service worker before assuming the app is quiet.

## Crook → Operator → Root Checkpoint

- **Crook:** Why does sitting "in the middle" let Burp defeat client-side validation?
- **Operator:** How do Repeater and Intruder differ, and when do you reach for each?
- **Root:** Explain why a Cluster Bomb can become a self-DoS, and why a Scanner issue is only a hypothesis until reproduced.

---
> 🔼 Up: [[Web Application Testing Tools]]
