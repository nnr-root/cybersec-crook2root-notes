---
title: "Cross-Site Scripting"
aliases: ["XSS", "Reflected XSS", "Stored XSS", "DOM XSS"]
tags: [tree/offensive, cyber/offensive/web/client-side/xss, type/technique, level/operator]
Domain: "[[Client-Side Web Security]]"
Color: "#DC143C"
---

# 💉 Cross-Site Scripting

> [!warning] Authorized simulation only
> XSS executes script in another user's browser. Prove it with a benign marker (a test DOM attribute, an `alert`-free canary), never by stealing cookies or acting as the victim. Test only in-scope applications you build or are authorized to assess.

## Parent Learning Order
CORS & Clickjacking -> Cross-Site Scripting -> CSRF & SameSite Testing -> Prototype Pollution & DOM Security

## Start at Zero: Running Your Script in Someone Else's Page

**Cross-Site Scripting (XSS)** is a flaw where an application includes attacker-controlled data in a page without properly encoding it, so the browser executes it as *script* in the context of that page's origin. The consequence is severe because the script runs with the victim's session: it can read their data, act as them, and reach anything their browser can. The root cause is always the same — **untrusted input reaching an output context (HTML, attribute, JavaScript, URL) without the encoding that context requires.**

The three types are distinguished by *where the payload lives*:

| Type | Payload path | Persistence |
| --- | --- | --- |
| **Reflected** | In the request, echoed into the response | Per-request (needs a lure) |
| **Stored** | Saved server-side, served to every viewer | Persistent (hits all users) |
| **DOM-based** | Never reaches the server; client JS is the sink | Client-side only |

> [!tip] The analogy, and where it breaks
> XSS is like slipping a forged instruction into a document that a trusted assistant reads aloud and *obeys* — the assistant (browser) can't tell your inserted line from the real ones. The analogy breaks on *context*: the same inserted text is harmless in one place (plain text) and dangerous in another (inside a script tag), so XSS is entirely about *where* your input lands and what encoding that spot needs — a subtlety no spoken instruction has.

**Prerequisites:** HTML/JavaScript basics, HTTP parameters, and the Same-Origin Policy.

## Context Is Everything

The single most important XSS concept: the *encoding a payload needs depends on where it lands*. The same input is safe in one context and executable in another:

| Output context | Safe encoding | A naive filter that fails |
| --- | --- | --- |
| HTML text | HTML-entity encode (`<`→`&lt;`) | Blocking `<script>` (many other tags execute) |
| HTML attribute | Attribute encode + quote | Allowing unquoted attributes |
| JavaScript string | JS-string escape | HTML-encoding (wrong context) |
| URL | URL encode + scheme allowlist | Allowing `javascript:` URLs |

This is why "we filter `<script>`" is not a fix — an event handler (`<img src=x onerror=...>`), a `javascript:` URL, or an attribute breakout all execute without the literal `<script>` tag. Correct defense encodes for the *specific* context, which is why testing probes each context separately.

## Testing With a Benign Canary

The ethical XSS proof does **not** steal cookies or pop `alert(document.cookie)` — it demonstrates *script execution* with a harmless marker. Setting a test DOM attribute proves the browser ran your code without any malicious action:

```bash
# reflect a benign payload and check whether it lands unencoded in an executable context (your own lab)
curl -s "http://127.0.0.1:8109/search?q=<img+src=x+onerror=window.__xss_canary=1>" | grep -o '<img src=x onerror=[^>]*>'
```

```text
<img src=x onerror=window.__xss_canary=1>
```

The payload came back **unencoded** inside the HTML — a browser rendering this would run `onerror`, setting a benign `__xss_canary` flag. That reflected, unencoded output in an executable context is the finding, proven without any harmful payload. (A real attacker would run session-stealing code; the canary proves execution is possible, which is the finding.)

## DOM XSS: The Server Never Sees It

DOM-based XSS is subtler: the payload flows entirely through client-side JavaScript, from a *source* (`location.hash`, `document.referrer`) to a dangerous *sink* (`innerHTML`, `eval`, `document.write`) — the server never processes it, so server-side filtering and even a WAF are blind to it. Testing DOM XSS means reading the client JavaScript for source-to-sink flows:

```text
source: location.hash            (attacker controls the URL fragment)
sink:   element.innerHTML = ...  (writing attacker data as HTML)
proof:  #<img src=x onerror=...> executes, server logs show nothing
```

The defense is client-side: use safe sinks (`textContent`, not `innerHTML`), and frameworks that auto-encode. This is why "the server is secure" does not mean "no XSS."

```mermaid
flowchart TD
    I["Untrusted input"] --> C{"Reaches an output context?"}
    C -->|"server echoes it"| RS["Reflected / Stored XSS"]
    C -->|"client JS sink"| D["DOM XSS (server blind)"]
    RS --> E{"Encoded for THAT context?"}
    D --> E
    E -->|"No"| X["Script executes in victim's origin"]
    E -->|"Yes"| S["Safe"]
    X --> P["Prove with a benign canary, never cookie theft"]
```

## Failure Modes and Interpretation

- **Proving with real harm.** Popping `alert(document.cookie)` or exfiltrating a session is over-proving; a benign DOM-attribute canary demonstrates execution without acting as the victim.
- **Context confusion.** A payload that fails in HTML text may execute in an attribute or JS context — test each context, don't conclude "safe" from one.
- **Filter bypass neighborhood.** Blocking `<script>` leaves event handlers, `javascript:` URLs, SVG, and dozens of vectors — test the neighborhood, and treat a blocklist as likely-bypassable.
- **DOM XSS invisibility.** Server-side testing and WAFs miss DOM XSS entirely; you must read the client JavaScript for source-to-sink flows.
- **CSP as mitigation, not fix.** A strong Content-Security-Policy can *block* XSS execution even when the injection exists — but CSP is defense-in-depth, and a bypassable CSP (unsafe-inline, script gadgets) is not remediation. The encoding is the fix.

## Security Implications — Detection & Defense

- **Context-aware output encoding is the fix.** Encode every piece of untrusted data for the exact context it lands in — modern frameworks (React, Angular) do this automatically, which is why framework-native output is largely XSS-safe unless you opt out (`dangerouslySetInnerHTML`).
- **Content-Security-Policy** is powerful defense-in-depth: a nonce/hash-based policy blocks inline and injected scripts, containing XSS even when an injection slips through. Deploy it, but do not rely on it as the sole control.
- **Safe DOM sinks** (`textContent` over `innerHTML`) and avoiding `eval`/`document.write` close DOM XSS at the client.
- **Cookie flags** (`HttpOnly`) mean an XSS cannot read the session cookie — not a fix for XSS, but a mitigation that limits one common impact.
- **Detection** is hard because payloads are diverse; the durable defense is prevention (encoding + CSP), and a defender testing their own inputs across contexts is the practical audit.

## Authorized Lab: Prove Reflected XSS With a Benign Canary

> [!info] Runs on one Linux machine — builds a search page that reflects input unencoded, tested in a real browser-parse simulation
> Loopback-bound. The proof is a benign canary flag, no cookie access. Step 5 removes it.

### Step 1 — Build a page that reflects input into HTML unencoded

```bash
cat > /tmp/xss.py << 'EOF'
import http.server, urllib.parse
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).get("q",[""])[0]
        self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers()
        # VULNERABLE: reflects q directly into HTML with no encoding
        self.wfile.write(f"<html><body>Results for: {q}</body></html>".encode())
    def log_message(self,*a): pass
http.server.HTTPServer(("127.0.0.1",8109),H).serve_forever()
EOF
python3 /tmp/xss.py &>/dev/null &
sleep 1; echo "search app up on 127.0.0.1:8109"
```

```text
search app up on 127.0.0.1:8109
```

### Step 2 — Benign input is reflected as-is (baseline)

```bash
curl -s "http://127.0.0.1:8109/?q=hello"
```

```text
<html><body>Results for: hello</body></html>
```

Normal text reflects harmlessly.

### Step 3 — Injected payload lands unencoded (the finding)

```bash
curl -s "http://127.0.0.1:8109/?q=$(python3 -c "import urllib.parse;print(urllib.parse.quote('<img src=x onerror=window.__xss=1>'))")" | grep -o '<img[^>]*>'
```

```text
<img src=x onerror=window.__xss=1>
```

The `<img onerror=...>` payload appears **unencoded** in the HTML — a browser parsing this runs `onerror`, setting the benign `__xss` canary. Reflected XSS confirmed, and note the payload has no `<script>` tag (an event handler), which is why blocking `<script>` would not have stopped it.

### Step 4 — Simulate the browser's parse to confirm execution context

```bash
# a headless check: does the payload sit in a context the HTML parser treats as an executable element?
curl -s "http://127.0.0.1:8109/?q=$(python3 -c "import urllib.parse;print(urllib.parse.quote('<img src=x onerror=1>'))")" | python3 -c "
import sys,html.parser
class P(html.parser.HTMLParser):
    hit=False
    def handle_starttag(s,t,a):
        if t=='img' and any(k=='onerror' for k,_ in a): s.hit=True
p=P(); p.feed(sys.stdin.read())
print('EXECUTABLE context: browser would fire onerror' if p.hit else 'inert')
"
```

```text
EXECUTABLE context: browser would fire onerror
```

Parsing the response as a browser would confirms the payload is a live `<img>` element with an `onerror` handler — proof the injection reaches an executable context, without ever running harmful code.

### Step 5 — Cleanup

```bash
kill %1 2>/dev/null; rm -f /tmp/xss.py; wait 2>/dev/null
curl -s -o /dev/null -w "app gone: %{http_code}\n" --max-time 2 http://127.0.0.1:8109/ 2>&1 | grep -o 'gone.*' || echo "app gone: connection refused"
```

```text
app gone: connection refused
```

**What you should now be able to do:** distinguish reflected/stored/DOM XSS, explain why encoding depends on the output context, prove reflected XSS with a benign canary and confirm the executable context, and articulate why blocking `<script>` is not a fix.

## Crook → Operator → Root Checkpoint

- **Crook:** Explain what XSS is, the three types, and why script running in the victim's origin is so severe.
- **Operator:** Prove reflected XSS with a benign canary, confirm the executable context, and explain why context-specific encoding — not `<script>` blocking — is required.
- **Root:** Explain why DOM XSS is invisible to the server and WAF, how context-aware encoding and framework auto-escaping fix XSS, and why CSP is powerful defense-in-depth but not the primary fix.

---
> 🔼 Up: [[Client-Side Web Security]]
