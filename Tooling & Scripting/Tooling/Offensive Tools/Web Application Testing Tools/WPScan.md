---
title: "WPScan"
aliases: ["wpscan"]
tags: [tree/tooling, cyber/tooling/offensive/web/wpscan, type/tool, difficulty/medium]
Domain: "[[Web Application Testing Tools]]"
Color: "#708090"
---

# WPScan

WPScan is a WordPress-specific security scanner. WordPress powers a huge share of the web, and its risk is rarely the core — it's the sprawl of **plugins and themes**, each a third-party codebase with its own CVEs. WPScan enumerates the version, installed plugins/themes, and users, then cross-references a vulnerability database to say exactly what is exploitable.

> [!warning] Authorized targets only
> Enumeration and password attacks hit a real site. Scope it, and respect the API token's rate limits — user brute-forcing can lock accounts.

## Parent Learning Order
curl -> Postman -> Burp Suite -> OWASP ZAP -> Nikto -> WPScan -> SQLmap

## A specialist that knows how WordPress leaks

> *Nikto and WPScan both aim at the server. What does WPScan know that Nikto does not?*
>
> Hold your answer — the section below is the response.

Like Nikto, WPScan aims at the **server** — but it's a specialist. It knows exactly how WordPress exposes its version, plugins, themes, and users, and it fingerprints each, then looks up known vulnerabilities.

The insight WPScan encodes: a WordPress site is only as secure as its *weakest plugin*. The core is well-maintained; the twelve plugins someone installed years ago are not. WPScan's job is to inventory that third-party sprawl and match it against a CVE feed.

## Enumerating plugins and users, and what the token unlocks

```shell-session
operator@lab:~$ wpscan --url https://blog.example.test --enumerate vp,u --api-token $TOK
[+] WordPress version 5.8.1 identified (Insecure, released 2021-09-09)
[+] contact-form-7 5.4.1 - outdated
 |   [!] Contact Form 7 - Unrestricted File Upload (CVE-2020-35489)
[+] Users: admin, editor_jane
```

`--enumerate vp` = *vulnerable plugins*, `u` = users. The **API token unlocks the CVE mapping** — without it you get versions but not the vulnerability data. WPScan can also brute-force enumerated users via `xmlrpc.php` (`--passwords rockyou.txt`) — bound it and respect lockouts.

## Confirming an inferred version before claiming a CVE

```shell-session
operator@lab:~$ wpscan --url https://blog.example.test --enumerate vp --api-token $TOK | grep CVE
 |   Contact Form 7 - Unrestricted File Upload (CVE-2020-35489)
operator@lab:~$ curl -s https://blog.example.test/wp-content/plugins/contact-form-7/readme.txt | grep -i 'Stable tag'
Stable tag: 5.4.1
# --- after the site updates the plugin ---
operator@lab:~$ wpscan --url https://blog.example.test --enumerate vp --api-token $TOK | grep -c CVE
0
```

**The deliberate break:** WPScan *inferred* the plugin version from fingerprints — the `readme.txt` **curl** confirms `5.4.1` is really installed before you assert CVE-2020-35489 applies (fingerprints can lie; a partial install or a hidden version means guessing). After the update, the CVE count drops to `0` — an objective before/after remediation metric. The professional flow is the same everywhere in this category: the scanner *narrows*, a manual check *confirms*, and the fix is measured by re-running the scanner.

**How you'd spot it:** the output says which it is — a version derived from a fingerprint is an inference, and WPScan marks its confidence next to it. Confirm against `readme.txt` or the plugin's own assets before asserting that a CVE applies. A report mapping every detected plugin straight onto CVEs with no confirmation step is the signature of skipping this.

## Summary

You should now be able to:

- Explain why plugins and themes, rather than the WordPress core, are usually the real risk.
- Check what must be confirmed before asserting that a plugin CVE WPScan reported is exploitable.
- Explain why the API token is required for CVE mapping, and how the CVE count gives an objective remediation metric.

---
> 🔼 Up: [[Web Application Testing Tools]]
