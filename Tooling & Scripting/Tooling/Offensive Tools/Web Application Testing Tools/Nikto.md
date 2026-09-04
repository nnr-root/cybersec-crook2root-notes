---
title: "Nikto"
aliases: ["nikto"]
tags: [tree/tooling, cyber/tooling/offensive/web/nikto, type/tool, difficulty/medium]
Domain: "[[Web Application Testing Tools]]"
Color: "#708090"
---

# Nikto

> [!abstract] Note of [[Web Application Testing Tools]]
> Nikto fires a large list of known-bad requests at a web server and reports what comes back — a fast, deliberately loud first sweep whose every hit is a lead, never proof. This note covers reading its hedged wording, confirming a flag before it enters a report, and why the noisiest tool in the category is still worth running first.

Nikto is a fast, noisy web-server scanner. It checks a target against a large database of known-dangerous files, outdated server versions, default pages, and misconfigurations. It is not subtle and not a full application scanner — it's the quick first sweep that flags low-hanging *server-level* issues before you bring out Burp or ZAP.

> [!warning] Authorized + loud
> Nikto makes thousands of requests and does not hide. Run only against authorized targets, and expect it to appear in every log and trip every WAF.

## Parent Learning Order
curl -> Postman -> Burp Suite -> OWASP ZAP -> Nikto -> WPScan -> SQLmap

## Firing a list of known-bad requests at the server

> *Does Nikto understand anything about your application's logic?*
>
> Hold your answer — the section below is the response.

Nikto doesn't intercept or think about your app's logic — it fires a big list of *known-bad* requests at the **web server** and reports what comes back.

In the request path it targets the server end: "do you have `/phpinfo.php`? a `/backup/` directory? an outdated Apache banner? `/.git/`?" It's a checklist scanner — every hit is a *lead* pulled from its signature database, never proof. That makes it fast and great for a first look, but also exactly why its output needs triage, not copy-paste.

## Reading each + as a lead

```shell-session
operator@lab:~$ nikto -h http://track.meridian.test -o nikto.txt
+ Server: Apache/2.4.29 (Ubuntu)
+ /admin/: Directory indexing found.
+ /phpinfo.php: Output from the phpinfo() function was found.
+ Apache/2.4.29 appears to be outdated (current is at least 2.4.58).
+ /.git/HEAD: 200 — source-code exposure
```

Each `+` is a lead: `phpinfo.php` leaks environment detail, directory indexing exposes files, `.git/` can leak source. Useful options: `-ssl` (force HTTPS), `-Tuning` (test categories), `-o`/`-Format` (report), `-maxtime` (bound the run).

## Why every finding needs manual confirmation

```shell-session
operator@lab:~$ nikto -h http://track.meridian.test
+ OSVDB-3092: /backup/: This might be interesting...
operator@lab:~$ curl -s http://track.meridian.test/backup/ | head -n 2
<title>Index of /backup</title>
<a href="db-2026-07.sql">db-2026-07.sql</a>
```

**The deliberate break:** Nikto *flagged* `/backup/` as "might be interesting" — a guess from its database, not a verified fact. Only the manual **curl** confirms it's a real, browsable directory leaking a database dump. Report the Nikto line without confirming and you produce false positives; confirm it and a guess becomes a finding. Same with version banners — Apache `2.4.29` "appears outdated," but a distro may have **back-ported** security fixes to that version string, so the CVE claim needs verification against the actual patch level, not the banner. Nikto's speed comes from guessing; your value comes from confirming.

**How you'd spot it:** Nikto's own wording marks it. "Appears", "might be interesting" and "this might be" are hedges, and they are honest ones — anything phrased that way needs a manual request before it enters a report. A findings list lifted straight from Nikto is recognisable precisely because those hedges survive into the client-facing document.

## Security Implications

**Nikto is the loudest tool in this category, by design, and that is a deliberate trade.** Thousands of requests for known-bad paths trip every WAF and land in every access log within seconds — there is no stealthy way to run it. You accept that noise in exchange for a fast server-level triage before the quieter, manual tools come out; running it expecting stealth is a category error.

**Its findings are server-hygiene failures, and the fix is removing the artifact.** `phpinfo.php`, directory indexing, `/.git/`, default pages and leftover `/backup/` directories are all files or settings that should not be web-reachable. The remediation is deletion or configuration, not detecting the scanner — and an organisation can run Nikto against itself to find them first.

**Its hedged wording must not survive into a report.** "Appears", "might be interesting" and version-banner guesses are honest inferences from a signature database, and a back-ported patch makes a version-based CVE claim a false positive. A findings list still carrying those hedges is the signature of a scan pasted into a document without the confirmation step.

## Summary

You should now be able to:

- Explain why Nikto is a first sweep rather than a thorough application test.
- Take the next step on a `/backup/` path Nikto flagged, before it goes in the report.
- Explain why a server-version alert can be a false positive, and how back-porting complicates version-based CVE claims.

---
> 🔼 Up: [[Web Application Testing Tools]]
