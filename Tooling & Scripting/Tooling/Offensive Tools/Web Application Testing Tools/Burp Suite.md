---
title: "Burp Suite"
aliases: ["Burp"]
tags: [tree/tooling, cyber/tooling/offensive/web/burp, type/tool, difficulty/hard]
Domain: "[[Web Application Testing Tools]]"
Color: "#708090"
---

# Burp Suite

> [!abstract] Note of [[Web Application Testing Tools]]
> Burp sits in the middle of the request path, which is the most powerful position there is — it sees the real bytes the browser sends and lets you change them before the server does. This note covers how that interception actually works (a TLS man-in-the-middle you consented to), why certificate pinning and QUIC defeat it, how Collaborator catches vulnerabilities that produce no response, and the trail Intruder, Scanner and Collaborator leave on the target.

Burp Suite is the intercepting-proxy platform at the centre of web application testing. It sits between your browser and the target, capturing every request so you can pause it, edit it, replay it, and automate it. Community Edition gives the full manual workflow; Professional adds the automated Scanner. If you learn one web tool deeply, it is this one.

> [!warning] Authorized application testing
> Set target scope *before* browsing. Never let Scanner, Intruder, or extensions reach third-party domains or production actions excluded by the Rules of Engagement.

## Parent Learning Order
curl -> Postman -> Burp Suite -> OWASP ZAP -> Nikto -> WPScan -> SQLmap

## The most powerful position: the middle

> *Every web tool sits at some point in the request path. Which point is the most powerful, and why?*
>
> Hold your answer — the section below is the response.

Every web tool operates at a *point* in the request path. Burp's point is the most powerful one: **the middle**.

Positioned as the proxy between client and server, Burp sees the *real* traffic your browser generates — then lets you grab any request and change it before it reaches the server. That is the whole superpower: the browser enforces client-side rules (hidden fields, JS validation, disabled buttons); Burp lets you ignore all of them and send exactly the bytes you want. The application's *server-side* behaviour is what you're really testing, and the proxy is how you reach it.

**The deliberate break:** a form that validates its inputs — rejecting a negative quantity, refusing a malformed email, greying out the submit button — looks like a field that has been secured.

That validation ran in the browser, which is to say it ran *before the request existed*. Burp sits after it. Every client-side check is advisory: it improves the experience for cooperative users and constrains nobody else, because the attacker is not using your form. Hidden fields, disabled buttons, maxlength attributes and JavaScript validators are all in the same category — they shape what the UI can produce, not what the server will accept. The only check that counts is the one running on the far side of the request.

**How you'd spot it:** test it directly rather than reasoning about it. Submit a value the form accepts, catch the request in Proxy, change the field to something the form would have refused, and forward it — if the server takes it, the validation was decorative. In a codebase the tell is a check that exists in the client with no counterpart in the handler; in traffic it is a request carrying a value the interface has no way to generate.

**Prerequisites:** HTTP requests and TLS from the web branch, and the client-versus-server-side distinction.

> [!tip] The analogy, and where it breaks
> A translator standing between two people who reads every message before passing it on, and can quietly rewrite it. The analogy breaks on trust: the two parties chose the translator and the server has no idea one is there — which is exactly the man-in-the-middle position, and exactly why an application that *pins* its expected correspondent (certificate pinning) refuses to talk through the translator at all.

## How the interception works, and what defeats it

Burp reads HTTPS by being a **TLS man-in-the-middle you deliberately set up**. When the browser connects to the target through Burp, Burp terminates the TLS on its side, generates a certificate for the target's hostname *on the fly*, and signs it with **Burp's own CA** — which is why the CA must be imported into the browser first. The browser trusts Burp's CA, so it accepts the forged certificate; Burp then opens its own TLS connection onward to the real server. Two encrypted legs, Burp in cleartext between them:

```text
browser ==TLS (Burp's forged cert, signed by Burp's CA)==> BURP ==TLS (real cert)==> server
                                                            ^ cleartext here: read, edit, replay
```

That mechanism is exactly why two things break it. **Certificate pinning**: an app that ships expecting a *specific* server certificate (not merely a valid chain) rejects Burp's forged one, and the traffic fails rather than intercepts — common in mobile apps and some thick clients. **HTTP/3 over QUIC**: it does not use the proxy the same way, so a QUIC-capable browser can route around Burp entirely. Both present identically to a beginner: traffic simply *vanishes* from HTTP history. When it does, suspect pinning, QUIC, or a service worker before concluding the app is quiet.

## Proxy, scope, and the core loop

**Set up:** proxy listener on `127.0.0.1:8080`, point the browser at it, import Burp's CA into a dedicated test profile, and define scope so you only touch the target:

```text
Proxy listener: 127.0.0.1:8080     Target scope: https://track.meridian.test/*
Out-of-scope:   analytics.thirdparty.test, payments.thirdparty.test
```

**The core loop** is Proxy → Repeater. Capture a request, send it to Repeater, then hand-edit and replay while comparing responses:

```http
GET /api/v1/profile HTTP/1.1
Host: track.meridian.test
Cookie: session=REDACTED

HTTP/1.1 200 OK
{"id":"r.okonkwo","role":"user"}
```

Change `r.okonkwo` to another user's ID and compare status/length/body — that's a broken-object-level-authorization test in three clicks, the same finding the [[REST & Modern API Transport]] note reaches from the API side. The tools you'll reach for:

| Tool | Use |
|---|---|
| **Proxy / HTTP history** | capture, intercept, annotate |
| **Repeater** | hand-edit & replay *one* request |
| **Intruder** | automated payloads across positions |
| **Decoder / Comparer** | transform data, diff responses |
| **Collaborator** | detect blind out-of-band (SSRF, blind XXE) |
| **Scanner** (Pro) | automated passive/active checks |

## Intruder's four attack types, and picking wrong

Intruder's four attack types are a common trap, and picking wrong turns a quick test into a self-DoS:

```text
Sniper:        1 position, 1 list       — N requests
Battering Ram: same payload, all pos    — N requests
Pitchfork:     parallel lists, paired   — N requests
Cluster Bomb:  every combination        — N × M requests
2 positions × 500 payloads (Cluster Bomb) = 250,000 requests ≈ 14h at 5/s
```

## Collaborator: catching what sends no response

Some vulnerabilities produce nothing you can see in the response — a blind SSRF that makes the server fetch a URL, a blind XXE, an injection that runs but returns no output. **Collaborator** solves this by giving you a unique external domain that Burp controls and watches. You place that domain in a payload; if the target's *server* connects to it, the vulnerability is proven by the callback, not by the response:

```text
Payload:   http://xyz123.oastify.com/   (a unique Collaborator subdomain)
Result:    Collaborator received a DNS lookup, then an HTTP request,
           from 203.0.113.20  ← the SERVER reached out — blind SSRF confirmed
```

The callback *is* the evidence: a server that had no reason to contact an unknown domain did, at the moment you injected the payload. It is how blind, out-of-band bugs become demonstrable — the same out-of-band principle Nuclei's interactsh templates use, in a manual tool.

## Security Implications

**Every payload you send lands in the application's own logs, and often a WAF.** Repeater and Intruder requests are real requests — injection strings, tampered IDs, traversal sequences — that appear in access logs and trip WAF rules exactly as an attacker's would. The manual workflow is quiet by volume but not invisible by content; a defender reading web logs sees the test.

**Intruder is a request flood with a distinctive shape.** A Cluster Bomb of two 500-payload lists is 250,000 requests to one endpoint with systematically varying parameters — a pattern no user produces and a WAF rate-limits on sight. The attack-type choice is an OpSec and a self-DoS decision, not just a speed one.

**Collaborator callbacks are the proof and the footprint at once.** The out-of-band interaction that confirms a blind bug is an outbound connection from the target's server to an external `oastify.com` domain — which egress filtering can block (turning a real finding into a false negative) and which a defender watching outbound DNS sees immediately. The evidence and the tell are the same packet.

**Scope is the control that prevents collateral damage.** Scanner, Intruder and extensions will follow links and fire payloads at whatever they reach, so an unset scope means active testing hitting third-party analytics, a payment provider, or production actions the RoE excluded. Setting scope before browsing is not tidiness — it is what keeps automated components from attacking systems you were never authorised to touch.

**A Scanner issue is a hypothesis until reproduced.** Professional's automated Scanner is active — it submits payloads and can trigger real state changes — and its findings, like any scanner's, are leads to confirm by hand, not report as-is.

All testing here is authorised and scoped; the intercepting proxy sees credentials and session tokens in cleartext, so its saved state is sensitive engagement evidence.

## Summary

You should now be able to:

- Explain how sitting in the middle lets Burp defeat client-side validation.
- Distinguish Repeater from Intruder, and choose between them.
- Explain how Burp's TLS man-in-the-middle works, why importing its CA is required, and why certificate pinning and QUIC defeat it.
- Use Collaborator to confirm a blind, out-of-band vulnerability, and explain why the callback is the evidence.
- Explain why a Cluster Bomb can become a self-DoS, why scope is what stops active tools hitting third parties, and why a Scanner issue is only a hypothesis until reproduced.

---
> 🔼 Up: [[Web Application Testing Tools]]
