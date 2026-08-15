---
title: "Nikto"
aliases: ["nikto"]
tags: [tree/tooling, cyber/tooling/offensive/web/nikto, type/tool, level/apprentice]
Domain: "[[Web Application Testing Tools]]"
Color: "#708090"
---

# Nikto

Nikto is a fast, noisy web-server scanner. It checks a target against a large database of known-dangerous files, outdated server versions, default pages, and misconfigurations. It is not subtle and not a full application scanner — it's the quick first sweep that flags low-hanging *server-level* issues before you bring out Burp or ZAP.

> [!warning] Authorized + loud
> Nikto makes thousands of requests and does not hide. Run only against authorized targets, and expect it to appear in every log and trip every WAF.

## Parent Learning Order
curl -> Postman -> Burp Suite -> OWASP ZAP -> Nikto -> WPScan -> SQLmap

## Crook — The Mental Model

Nikto doesn't intercept or think about your app's logic — it fires a big list of *known-bad* requests at the **web server** and reports what comes back.

![[tool_web_request_path.svg]]

In the request path it targets the server end: "do you have `/phpinfo.php`? a `/backup/` directory? an outdated Apache banner? `/.git/`?" It's a checklist scanner — every hit is a *lead* pulled from its signature database, never proof. That makes it fast and great for a first look, but also exactly why its output needs triage, not copy-paste.

## Operator — Make It Work

```shell-session
operator@lab:~$ nikto -h http://app.example.test -o nikto.txt
+ Server: Apache/2.4.29 (Ubuntu)
+ /admin/: Directory indexing found.
+ /phpinfo.php: Output from the phpinfo() function was found.
+ Apache/2.4.29 appears to be outdated (current is at least 2.4.58).
+ /.git/HEAD: 200 — source-code exposure
```

Each `+` is a lead: `phpinfo.php` leaks environment detail, directory indexing exposes files, `.git/` can leak source. Useful options: `-ssl` (force HTTPS), `-Tuning` (test categories), `-o`/`-Format` (report), `-maxtime` (bound the run).

## Root — Internals & The Deliberate Break

```shell-session
operator@lab:~$ nikto -h http://vuln.example.test
+ OSVDB-3092: /backup/: This might be interesting...
operator@lab:~$ curl -s http://vuln.example.test/backup/ | head -n 2
<title>Index of /backup</title>
<a href="db-2026-07.sql">db-2026-07.sql</a>
```

**The deliberate break:** Nikto *flagged* `/backup/` as "might be interesting" — a guess from its database, not a verified fact. Only the manual **curl** confirms it's a real, browsable directory leaking a database dump. Report the Nikto line without confirming and you produce false positives; confirm it and a guess becomes a finding. Same with version banners — Apache `2.4.29` "appears outdated," but a distro may have **back-ported** security fixes to that version string, so the CVE claim needs verification against the actual patch level, not the banner. Nikto's speed comes from guessing; your value comes from confirming.

## Crook → Operator → Root Checkpoint

- **Crook:** Why is Nikto a "first sweep" rather than a thorough application test?
- **Operator:** Nikto flags `/backup/` as interesting. What's your next step before it goes in the report?
- **Root:** Explain why a server-version alert can be a false positive, and how back-porting complicates version-based CVE claims.

---
> 🔼 Up: [[Web Application Testing Tools]]
