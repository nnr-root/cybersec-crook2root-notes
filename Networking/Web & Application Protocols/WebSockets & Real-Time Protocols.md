---
title: "WebSockets & Real-Time Protocols"
aliases: ["WebSocket", "WSS", "Server-Sent Events", "Real-Time Web", "Protocol Upgrade"]
tags:
  - tree/networking
  - cyber/networking/appproto
  - type/concept
  - level/operator
Domain:
  - "[[Web & Application Protocols]]"
Color: "#42D4F4"
---

# 🔁 WebSockets & Real-Time Protocols

> [!abstract] Note of [[Web & Application Protocols]]
> HTTP's request/response model cannot push data to a client that did not ask, which real-time applications need. This note covers the mechanisms that solve it — from the WebSocket upgrade that abandons request/response entirely to lighter one-way options — and explains why a persistent, full-duplex channel escapes many of the request-based controls that guard ordinary web traffic.

## Parent Learning Order
HTTP Fundamentals -> HTTPS & the TLS Handshake -> Web Architecture & Proxies -> WebSockets & Real-Time Protocols -> REST & Modern API Transport -> Application Delivery & Load Balancing

## Start at Zero: The Problem With Request/Response

HTTP's model is strict: the client asks, the server answers, done. The server cannot speak first. For a chat message, a stock tick, a live notification, or a multiplayer game, the server needs to send data the moment it has it — but it has no open channel to do so.

The historical workarounds were all compromises. **Polling** has the client ask "anything new?" repeatedly, wasting requests and adding latency. **Long polling** has the server hold a request open until it has data, which ties up a connection and still incurs a full round trip per message. These bend request/response without escaping it, and they scale poorly.

The real solution is to stop using request/response and open a **persistent, bidirectional channel**.

**Prerequisites:** HTTP request/response and status codes.

> [!tip] The analogy, and where it breaks
> Upgrading from posting letters back and forth to opening a telephone line that simply stays connected, so either side may speak whenever they like. The analogy breaks where security lives: each letter passed the mailroom's inspection individually, but nothing inspects each sentence on an open phone line. That is precisely why per-request controls stop applying and validation must move inside the message handler.

## The WebSocket Upgrade

**WebSocket** establishes a full-duplex connection that begins as an ordinary HTTP request and then *upgrades* into something else entirely.

```mermaid
sequenceDiagram
    participant C as Client
    participant S as Server
    C->>S: GET /chat HTTP/1.1 + Upgrade: websocket + Sec-WebSocket-Key
    Note over S: Agrees to switch protocols
    S-->>C: 101 Switching Protocols + Sec-WebSocket-Accept
    Note over C,S: The connection is no longer HTTP — it is a WebSocket
    C->>S: frame: "hello"
    S->>C: frame: "welcome"
    S->>C: frame: "notification" (server pushes, unprompted)
    C->>S: frame: "ack"
    Note over C,S: Either side sends any time until close
```

The handshake is the clever part. The client sends a normal HTTP GET with `Upgrade: websocket` and a random `Sec-WebSocket-Key`. The server responds with **101 Switching Protocols** — the one status code that means "we are abandoning HTTP on this connection." From that point the same TCP (or TLS) connection carries WebSocket **frames**, not HTTP messages, and either side may send at any time.

Because it starts as HTTP, WebSocket traverses existing web infrastructure — the same ports (80, 443), the same proxies, the same TLS. `ws://` is the plaintext scheme; `wss://` is WebSocket over TLS and is the only acceptable form in production, for exactly the confidentiality and integrity reasons HTTPS exists.

```bash
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
  -H "Sec-WebSocket-Version: 13" http://<lab server>/chat
```

Expected excerpt:

```text
HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
```

The `101` is the moment the connection stops being HTTP.

## Lighter Options: Server-Sent Events

WebSocket is full-duplex, which is more than many applications need. When only the *server* needs to push and the client just receives — a news feed, a progress indicator, a live dashboard — **Server-Sent Events (SSE)** is simpler.

SSE is a single long-lived HTTP response that the server keeps writing to, streaming events as text. It stays within HTTP, so it works with ordinary HTTP tooling, supports automatic reconnection, and needs no protocol upgrade. Its limitation is that it is one-directional (server to client only) and text-only. The engineering rule of thumb: use SSE when only the server pushes, WebSocket when both directions need to send arbitrary data.

| Mechanism | Direction | Transport | Use when |
| --- | --- | --- | --- |
| Polling | Client asks repeatedly | HTTP requests | Rarely; simplicity over efficiency |
| Long polling | Server holds a request | HTTP request | Legacy fallback |
| **SSE** | Server → client only | One long HTTP response | Server pushes, client only listens |
| **WebSocket** | Both directions | Upgraded connection, framed | True bidirectional real-time |

## Security Implications

**WebSocket escapes request-based controls.** The controls guarding ordinary web traffic — WAF rules, per-request authorization checks, request logging — operate on discrete HTTP requests. A WebSocket is one long connection carrying many messages that never appear as separate HTTP requests, so a WAF that inspects the opening handshake may see nothing of the thousands of messages that follow. Security must move *into* the WebSocket message handler: every message must be validated and authorized as it arrives, because the per-request checks upstream no longer apply. Treating the initial handshake as the only checkpoint is a common and serious gap.

**Cross-Site WebSocket Hijacking exploits the handshake's origin trust.** The WebSocket handshake is an HTTP request, and browsers attach cookies to it automatically — but the **SameSite** and CORS protections that guard ordinary cross-origin requests do not apply to WebSocket the same way. If a server authenticates a WebSocket purely from the cookie and does not validate the **`Origin`** header, a malicious page can open an authenticated WebSocket to your server in the victim's context and read or send data as the victim. The defenses are explicit `Origin` validation on the handshake and authenticating the WebSocket with a token the malicious page cannot obtain, not merely the ambient cookie.

**Persistent connections are a resource commitment.** Each WebSocket holds a connection open indefinitely, consuming server memory and a connection slot for its entire lifetime. A server must bound the number of concurrent connections, enforce idle timeouts, and rate-limit messages per connection — otherwise opening many connections, or flooding messages down one, exhausts the server. This is the same finite-state concern seen at the transport layer, now at the application layer and easier to trigger because each connection is cheap for the client and expensive for the server.

**Authorization can go stale on a long connection.** A permission valid when a WebSocket opened may be revoked hours later while the connection persists. Unlike short requests that re-check authorization each time, a long-lived channel must re-validate authorization periodically or on privilege-relevant actions, or it becomes a way to retain access after it should have been withdrawn.

**Input validation still applies, per message.** Everything true of HTTP request bodies — injection, deserialization risks, malformed input — is true of WebSocket frames. The framing is different; the untrusted-input principle is identical, and each frame is a fresh piece of untrusted data.

All testing described here must target only systems within an authorized scope. WebSocket hijacking and flooding are intrusive and belong in an authorized lab.

## Authorized Lab: Upgrade, Push, and Probe

Use a lab application exposing a WebSocket endpoint and an SSE endpoint, plus a client.

1. **Watch the upgrade.** Perform the handshake with the `curl` command above and confirm the `101 Switching Protocols` response. Capture the exchange and observe that after the 101, the traffic is framed WebSocket, not HTTP:

```bash
sudo tcpdump -i eth0 -nn -A -c 12 'tcp port <ws port>'
```

2. **Observe server push.** Connect a WebSocket client and confirm the server can send a message the client never requested — the property HTTP lacks.
3. **Contrast with SSE.** Connect to the SSE endpoint and confirm it streams server events over one long HTTP response, with no upgrade, and that the client cannot send back over it.
4. **Show the control gap.** Place a request-inspecting proxy or WAF in front of the app. Send a malicious payload as an ordinary HTTP request and confirm it is caught; send the same payload as a WebSocket message and confirm it passes uninspected to the handler — demonstrating why per-message validation is required.
5. **Test origin validation.** Open a WebSocket to the app from a page served by a different origin, carrying the victim's cookie. If the server does not validate `Origin`, confirm the connection succeeds as the victim (the hijacking condition). Add `Origin` validation and a per-session token and confirm the cross-origin attempt now fails.
6. **Test resource limits.** Open many WebSocket connections and confirm the server's behaviour; then apply a connection cap and idle timeout and confirm excess connections are rejected or reaped.
7. **Cleanup.** Restore the app's baseline configuration and close all test connections.

Expected interpretation:

```text
101 Switching  -> the connection stops being HTTP; framed WebSocket follows
Server push    -> the server sends unprompted; the capability HTTP lacks
WAF gap        -> per-request inspection misses per-message payloads
No Origin check-> cross-site WebSocket hijacking succeeds as the victim
Origin + token -> handshake validated; hijacking fails
Connection cap -> persistent connections are a bounded resource
```

## Crook → Operator → Root Checkpoint

- **Crook:** Explain why HTTP cannot push to a client, what the WebSocket upgrade accomplishes, and when Server-Sent Events is the simpler right choice.
- **Operator:** Perform and read a WebSocket handshake, recognize the `101` transition, and explain why `wss://` is mandatory; contrast SSE and WebSocket by direction and transport.
- **Root:** Explain why per-request controls miss WebSocket messages and where security must move; describe Cross-Site WebSocket Hijacking and its `Origin`/token defenses, and why long-lived connections require bounded resources and periodic authorization re-validation.

---
> 🔼 Up: [[Web & Application Protocols]]
