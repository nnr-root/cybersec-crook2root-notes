---
title: "WebSocket Security Testing"
aliases: ["WebSocket Testing", "Cross-Site WebSocket Hijacking"]
tags: [tree/offensive, cyber/offensive/api/websocket, type/technique, difficulty/medium]
Domain: "[[API & Modern Protocol Testing]]"
Color: "#DC143C"
---

# 🔁 WebSocket Security Testing

> [!warning] Authorized simulation only
> WebSocket testing sends messages over a persistent channel and can affect real-time application state. Test only in-scope endpoints with authorized credentials, and prove flaws with benign messages.

## Parent Learning Order
Modern API Security Testing -> Legacy XML Web Services Testing -> API Security Fundamentals -> WebSocket Security Testing

## The Channel That Escapes Request-Based Controls

> *Your WAF inspects every HTTP request. How much of a WebSocket conversation does it see?*
>
> Hold your answer — the section below is the response.

A **WebSocket** is a persistent, bidirectional connection between browser and server — unlike HTTP's request/response, either side may send at any time (the mechanism is covered in the Networking **WebSockets & Real-Time Protocols** leaf). This changes testing fundamentally: the security controls that guard ordinary web traffic operate on *discrete HTTP requests*, but a WebSocket is *one long connection* carrying many messages that never appear as separate requests. A WAF that inspects the opening handshake sees nothing of the thousands of messages that follow.

So the central WebSocket testing lesson is that **per-request security does not apply per-message**. Authorization, input validation, and rate limiting must move *into* the message handler, and a common finding is that they didn't.

> [!tip] The analogy, and where it breaks
> A WebSocket is like a phone line left open after security checked your ID at the door — the guard verified you once, and now everything you say down the line is unmonitored. The analogy breaks because the "guard" (WAF/authorization) that inspected the handshake genuinely cannot hear the ongoing conversation, so every sentence must be independently validated by the person on the other end, not the door guard.

**Prerequisites:** the Networking **WebSockets & Real-Time Protocols** leaf (the mechanism), and the API authorization concepts.

## The Three WebSocket Testing Concerns

| Concern | Test | Why it matters |
| --- | --- | --- |
| **Handshake authorization** | Does the upgrade validate `Origin` and require a proper token? | Cross-Site WebSocket Hijacking |
| **Per-message authorization** | Is each message authorized, or only the connection? | Privilege escalation mid-session |
| **Per-message validation** | Is each message's input validated? | Injection via frames a WAF never saw |

**Cross-Site WebSocket Hijacking (CSWSH)** is the signature WebSocket flaw. The handshake is an HTTP request, and browsers attach cookies to it automatically — but the SameSite/CORS protections that guard ordinary cross-origin requests do not fully apply to WebSocket. If the server authenticates the connection purely from the cookie and does not validate the `Origin` header, a malicious page can open an authenticated WebSocket to your server *in the victim's context*, reading and sending data as the victim.

## Per-Message Authorization: The Stale-Permission Trap

A subtler concern: authorization checked *once* at connection time goes stale. A permission valid when the WebSocket opened may be revoked hours later while the connection persists. And a connection opened as a low-privilege user may send messages requesting high-privilege actions that the handler never re-checks:

```bash
# does a message request a privileged action the connection wasn't authorized for? (your own lab)
# sending an admin-action message over a user-authenticated socket
printf '{"action":"admin_delete","id":5}\n' | timeout 2 websocat ws://127.0.0.1:8101/ 2>/dev/null || echo "(websocat not installed; the lab below uses a raw client)"
```

```text
{"result":"deleted","by":"user"}
```

The socket was opened by a regular user, yet an `admin_delete` message succeeded — the handler validated the *connection* but not each *message's* authorization. That is the mid-session privilege flaw, and it exists because per-request checks don't fire per-message.

## Testing the Handshake for CSWSH

The CSWSH test: does the handshake accept a connection from an arbitrary `Origin`? If a WebSocket upgrade with `Origin: https://evil.example` and the victim's cookie succeeds, a malicious page can hijack the channel.

```mermaid
flowchart TD
    H["WebSocket handshake (HTTP upgrade)"] --> O{"Origin validated? Token required?"}
    O -->|"No — cookie only"| C["CSWSH: malicious page opens socket as victim"]
    O -->|"Yes"| M["Connection authorized"]
    M --> P{"Each MESSAGE authorized + validated?"}
    P -->|"No"| E["Mid-session privilege escalation / injection"]
    P -->|"Yes"| S["Secure: security moved into the handler"]
    C --> F["Finding: handshake trusts ambient cookie, no Origin check"]
```

## The WAF blind spot both sides miss

- **WAF blind spot assumed safe.** A payload blocked as an HTTP request but accepted as a WebSocket message *looks* safe to the WAF — testers and defenders both miss it. Always test payloads over the socket, not just over HTTP.
- **CSWSH needs the cookie context.** Proving CSWSH requires demonstrating the cross-origin handshake succeeds with the victim's ambient credentials — an `Origin` check defeats it, so confirm whether the check exists.
- **Stale authorization is time-dependent.** The privilege-revocation flaw only manifests on long-lived connections; a short test may miss it. Consider connection lifetime.
- **Message flooding = DoS.** Rate-limit testing over a socket can genuinely overwhelm a server (each connection is cheap for the client, expensive for the server). Throttle.
- **Framing quirks.** WebSocket messages can be fragmented and use text or binary frames; a validation bypass may hide in an unusual framing — test the variants.

## Security Implications — Detection & Defense

- **Security must move into the message handler.** Per-message authorization and validation are the core controls, because the per-request controls upstream (WAF, request-level authz) do not see individual frames.
- **Validate `Origin` on the handshake and use a token the malicious page cannot obtain** — not the ambient cookie alone. This is the definitive CSWSH defense.
- **Re-validate authorization periodically or on privileged actions** over long-lived connections, so a revoked permission actually takes effect and a low-privilege socket cannot request high-privilege actions.
- **Bound the resource:** cap concurrent connections and messages per connection, since a persistent socket is cheap to open and expensive to serve — the same finite-state concern as the transport layer.
- **Monitoring must inspect messages, not just connections** — a connection that opens normally and then sends anomalous privileged actions is the CSWSH/escalation signature, invisible if you only log the handshake.

## Summary

You should now be able to:

- Explain why a WebSocket escapes request-based controls, and what Cross-Site WebSocket Hijacking is.
- Test per-message authorization by sending a privileged action over a low-privilege socket, and test the handshake for `Origin` validation.
- Explain why security must move into the message handler, why `Origin` validation plus a non-ambient token defeats CSWSH, and why long-lived connections require periodic authorization re-validation.

---
> 🔼 Up: [[API & Modern Protocol Testing]]
