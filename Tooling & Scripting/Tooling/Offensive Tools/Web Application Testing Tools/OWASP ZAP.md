---
title: "OWASP ZAP"
aliases: ["ZAP", "Zed Attack Proxy"]
tags: [tree/tooling, cyber/tooling/offensive/web/zap, type/tool, difficulty/medium]
Domain: "[[Web Application Testing Tools]]"
Color: "#708090"
---

# OWASP ZAP

OWASP ZAP (Zed Attack Proxy) is the open-source intercepting proxy and web scanner — Burp's free counterpart. It shines in two places Burp Community does not: a capable **active scanner**, and first-class **automation** (headless mode, an API, a Docker "baseline scan") that makes it the default DAST tool for CI pipelines.

> [!warning] Authorized targets only
> The active scanner sends real attack payloads. Point it only at applications you may test, and keep it inside the configured context/scope.

## Parent Learning Order
curl -> Postman -> Burp Suite -> OWASP ZAP -> Nikto -> WPScan -> SQLmap

## Passive reading versus active probing

ZAP occupies the same spot as Burp — the intercepting proxy in the middle of the request path.

The mental leap for ZAP specifically is **passive vs. active**. Passive scanning only *watches* the traffic you generate (flagging missing headers, insecure cookies) and sends nothing extra — safe against any target. Active scanning *injects* attack payloads to find injection/XSS — powerful but intrusive. Knowing which mode you're in is the difference between a safe CI check and attacking a system you shouldn't.

## The CLI, and the CI-friendly baseline scan

Interactively you proxy the browser, spider the app, and active-scan within a context. But ZAP's real edge is the CLI. The Docker **baseline scan** is passive-only and CI-friendly (non-zero exit on findings):

```shell-session
operator@ci:~$ docker run -t owasp/zap2docker-stable zap-baseline.py -t https://staging.example.test
WARN-NEW: Cookie No HttpOnly Flag [10010] x3
WARN-NEW: Missing Anti-clickjacking Header [10020] x2
FAIL-NEW: 0   WARN-NEW: 5
```

A full (active) scan finds deeper bugs but attacks the app:

```shell-session
operator@lab:~$ zap.sh -cmd -quickurl http://app.example.test -quickout /tmp/zap.html
FAIL-NEW: 1   (High: SQL Injection - /search?q=)
```

## What the passive baseline structurally cannot find

```shell-session
operator@lab:~$ zap-baseline.py -t http://app.example.test        # passive
WARN-NEW: 5   FAIL-NEW: 0     (headers/cookies only — no attacks sent)
operator@lab:~$ zap.sh -cmd -quickurl http://app.example.test -quickout out.html   # active
FAIL-NEW: 1   (High: SQL Injection - /search?q=)
```

**The deliberate break:** the passive baseline **cannot** find the SQL injection — it only reads traffic, so it flags missing headers and stops. The active scan finds the real bug but sends attack payloads. Pick passive against production (safe, shallow) and active against a staging target you're authorized to attack (intrusive, deep). Choosing the wrong mode either misses vulnerabilities or hits a system you shouldn't — the single most important ZAP decision. And, exactly as with Burp, every High the active scanner reports is a *hypothesis*: confirm SQLi by hand (or chain into **SQLmap**) before it's a finding.

## Summary

You should now be able to:

- Distinguish a passive web scan from an active one.
- Wire the right ZAP mode into CI to gate on web risks without attacking the app, and state what it necessarily misses.
- Explain why an automated High finding still requires manual confirmation, and how you'd verify it safely.

---
> 🔼 Up: [[Web Application Testing Tools]]
