---
title: "CORS & Clickjacking"
aliases: ["CORS Misconfiguration", "Clickjacking", "Cross-Origin Resource Sharing", "UI Redressing"]
tags: [tree/offensive, cyber/offensive/web/client-side, type/technique, level/operator]
Domain: "[[Client-Side Web Security]]"
Color: "#DC143C"
---

# 🪟 CORS & Clickjacking

> [!warning] Authorized simulation only
> These attacks abuse the trust between origins. Prove them with a benign proof-of-concept page you host locally against a synthetic account, never against real users. Test only in-scope applications.

## Parent Learning Order
CORS & Clickjacking -> Cross-Site Scripting -> CSRF & SameSite Testing -> Prototype Pollution & DOM Security

## Start at Zero: Two Ways to Abuse Cross-Origin Trust

The browser's core security rule is the **Same-Origin Policy**: a page from `evil.example` cannot read data from `bank.example`. Two mechanisms deliberately relax parts of this trust boundary, and both are commonly misconfigured into vulnerabilities:

- **CORS (Cross-Origin Resource Sharing)** relaxes the *read* restriction — it lets a server say "these other origins may read my responses." Misconfigure it, and you tell the attacker's origin it may read your users' data.
- **Clickjacking** abuses the *framing* trust — it loads your real page invisibly over a decoy, so a victim's clicks land on your application without them knowing.

Both are client-side attacks that exploit the browser's cross-origin model, which is why they belong together: one leaks data *out* across origins, the other tricks clicks *in* across origins.

> [!tip] The analogy, and where it breaks
> CORS misconfiguration is like a bank posting "any courier may collect statements on a customer's behalf" — meant for one trusted courier, it now lets anyone collect. Clickjacking is like a scammer holding a clear "sign here" sheet over a real contract so you sign the contract thinking it's the sheet. The analogy breaks on invisibility: the clickjacking overlay is *perfectly transparent*, so the victim genuinely cannot see they are interacting with the real application, unlike any physical overlay.

**Prerequisites:** the Same-Origin Policy, HTTP headers, and cookies.

## CORS: When "Who May Read Me" Is Too Permissive

When a page makes a cross-origin request, the browser enforces CORS: it only lets the calling origin *read* the response if the server's `Access-Control-Allow-Origin` (ACAO) header permits it. The misconfigurations:

| Misconfiguration | Why it's dangerous |
| --- | --- |
| `ACAO: *` **with credentials** | Any origin reads authenticated responses (though browsers block `*`+credentials, reflected origin achieves it) |
| **Reflected origin** — echoing the request's `Origin` | Effectively allows *every* origin, including the attacker's |
| **Weak origin validation** — `endsWith("bank.com")` | `evilbank.com` or `bank.com.evil.com` passes |
| **`null` origin allowed** | Sandboxed iframes and some contexts send `Origin: null` |

The critical case is **reflected origin with credentials**: the server echoes whatever `Origin` the request carried into ACAO and sets `Access-Control-Allow-Credentials: true`. Now the attacker's page can make a *credentialed* request to your API and *read the response* — stealing the victim's data using their own cookies.

```bash
# test whether the server reflects an arbitrary Origin (your own lab API)
curl -s -I -H "Origin: https://evil.example" "http://127.0.0.1:8108/account" | grep -i 'access-control'
```

```text
Access-Control-Allow-Origin: https://evil.example
Access-Control-Allow-Credentials: true
```

The server echoed `evil.example` and allowed credentials — the finding. Any attacker page can now read authenticated account data. A secure server would return only its own trusted origins, never the reflected attacker origin.

## Clickjacking: Stealing Clicks Through Invisible Frames

Clickjacking (UI redressing) loads your real application in an invisible iframe positioned over an attractive decoy ("Click to win!"). The victim clicks the decoy, but the click actually lands on your application's button — transferring money, changing a setting, confirming an action — while they authenticate via their existing session:

```text
Attacker page:  [ decoy button "CLAIM PRIZE" ]
Invisible iframe (opacity 0) on top:  [ your real "Delete Account" button aligned to the decoy ]
Victim clicks decoy -> click lands on "Delete Account" in the framed real app
```

The defense is a single response header telling the browser your page may not be framed by other origins — `X-Frame-Options: DENY` or, modern, `Content-Security-Policy: frame-ancestors 'none'`. A page *without* framing protection is clickjackable, and testing it is simply: can I frame it?

```mermaid
flowchart TD
    SOP["Same-Origin Policy: origins isolated"] --> C{"CORS: who may READ my responses?"}
    C -->|"reflected origin + creds"| L["Attacker origin reads authenticated data"]
    C -->|"own origins only"| SC["Secure"]
    SOP --> F{"Framing: may other origins frame me?"}
    F -->|"no frame protection"| CJ["Clickjacking: victim clicks land on real app"]
    F -->|"frame-ancestors none"| SF["Secure"]
```

## Failure Modes and Interpretation

- **CORS `*` is not always exploitable.** Browsers block `ACAO: *` combined with credentials, so a `*` on a *public, non-credentialed* endpoint may be harmless. The dangerous case is reflected origin *with* credentials — classify precisely.
- **Proving CORS needs the credentialed read.** The finding is that an attacker origin can *read authenticated data* — demonstrate the reflected header and the credentialed read, not just the header.
- **Clickjacking needs a sensitive action.** Framing a read-only page is low impact; the finding is framing a page with a *state-changing* one-click action. Assess what a redirected click achieves.
- **Framebusting JS is weak.** Old JavaScript "framebusting" is bypassable; only the response headers (`frame-ancestors`/`X-Frame-Options`) reliably prevent framing.
- **SameSite cookies interact.** `SameSite=Lax/Strict` cookies may not be sent in a framed cross-origin context, reducing clickjacking impact — assess the cookie configuration too.

## Security Implications — Detection & Defense

- **CORS: allowlist specific trusted origins**, never reflect the request origin, never combine permissive ACAO with credentials, and validate origins by exact match (not `endsWith`). This is a server configuration fix.
- **Clickjacking: set `Content-Security-Policy: frame-ancestors 'none'`** (or a specific allowlist) on every sensitive page — the single header that defeats it. `X-Frame-Options` is the older equivalent.
- **Both are configuration flaws**, not code flaws — which means they are cheap to fix (headers) and cheap to *miss*, since nothing crashes without them. A security-header audit catches both.
- **Detection is limited** because both exploit legitimate browser behavior; the defense is prevention via headers, and a header-scanning tool (run against yourself) is the practical control.
- **Sensitive actions deserve extra friction** — a confirmation step or re-authentication for high-impact actions blunts clickjacking even if a page is framed, since a single stolen click cannot complete the action.

## Authorized Lab: Detect Both Misconfigurations

> [!info] Runs on one Linux machine — builds an API with reflected-origin CORS and a page with no frame protection
> Loopback-bound, synthetic data. Step 5 removes it.

### Step 1 — Build an app with both flaws

```bash
cat > /tmp/cors.py << 'EOF'
import http.server
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        origin = self.headers.get("Origin","")
        self.send_response(200)
        # FLAW 1: reflect the request Origin + allow credentials
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Credentials","true")
        # FLAW 2: no X-Frame-Options / frame-ancestors -> framable
        self.send_header("Content-Type","text/html"); self.end_headers()
        self.wfile.write(b'{"account":"alice","balance":"CANARY-1000"}' if self.path=="/account" else b'<button>Delete Account</button>')
    def log_message(self,*a): pass
http.server.HTTPServer(("127.0.0.1",8108),H).serve_forever()
EOF
python3 /tmp/cors.py &>/dev/null &
sleep 1; echo "app up (reflected CORS + no frame protection)"
```

```text
app up (reflected CORS + no frame protection)
```

### Step 2 — CORS: does it reflect an attacker origin with credentials?

```bash
curl -s -I -H "Origin: https://evil.example" http://127.0.0.1:8108/account | grep -i 'access-control'
```

```text
Access-Control-Allow-Origin: https://evil.example
Access-Control-Allow-Credentials: true
```

The server echoed `evil.example` and allowed credentials — an attacker page can now read the victim's authenticated `/account` response. Finding one confirmed.

### Step 3 — Clickjacking: is framing prevented?

```bash
curl -s -I http://127.0.0.1:8108/ | grep -iE 'x-frame-options|frame-ancestors' || echo "NO frame protection header present -> page is framable (clickjackable)"
```

```text
NO frame protection header present -> page is framable (clickjackable)
```

No `X-Frame-Options` or `frame-ancestors` — the page can be loaded in an invisible iframe over a decoy. Finding two confirmed, by the *absence* of the header.

### Step 4 — State the fixes

```bash
echo "CORS fix: allowlist exact trusted origins; never reflect Origin; never permissive-ACAO + credentials."
echo "Clickjacking fix: Content-Security-Policy: frame-ancestors 'none' on every sensitive page."
echo "Both are one-line header configurations — cheap to fix, cheap to forget."
```

```text
CORS fix: allowlist exact trusted origins; never reflect Origin; never permissive-ACAO + credentials.
Clickjacking fix: Content-Security-Policy: frame-ancestors 'none' on every sensitive page.
Both are one-line header configurations — cheap to fix, cheap to forget.
```

### Step 5 — Cleanup

```bash
kill %1 2>/dev/null; rm -f /tmp/cors.py; wait 2>/dev/null
curl -s -o /dev/null -w "app gone: %{http_code}\n" --max-time 2 http://127.0.0.1:8108/ 2>&1 | grep -o 'gone.*' || echo "app gone: connection refused"
```

```text
app gone: connection refused
```

**What you should now be able to do:** test CORS for reflected-origin-with-credentials, detect missing frame protection as a clickjacking exposure, distinguish exploitable CORS from harmless `*`, and name the one-header fix for each.

## Crook → Operator → Root Checkpoint

- **Crook:** Explain the Same-Origin Policy and how CORS relaxes reads while clickjacking abuses framing.
- **Operator:** Test CORS for reflected-origin-with-credentials and a page for missing frame protection, and classify whether each is genuinely exploitable.
- **Root:** Explain why reflected origin + credentials is the dangerous CORS case, why only response headers (not framebusting JS) reliably prevent clickjacking, and why both are cheap-to-fix, cheap-to-miss configuration flaws.

---
> 🔼 Up: [[Client-Side Web Security]]
