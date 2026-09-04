---
title: "OWASP ZAP"
aliases: ["ZAP", "Zed Attack Proxy"]
tags: [tree/tooling, cyber/tooling/offensive/web/zap, type/tool, difficulty/medium]
Domain: "[[Web Application Testing Tools]]"
Color: "#708090"
---

# OWASP ZAP

> [!abstract] Note of [[Web Application Testing Tools]]
> ZAP is Burp's open-source counterpart, and it wins in two places Burp Community does not: a capable active scanner and first-class automation for CI. This note covers the passive-versus-active distinction that decides what a scan can find, why unattended automation makes scope the critical control, and why an automated High is still a hypothesis.

OWASP ZAP (Zed Attack Proxy) is the open-source intercepting proxy and web scanner — Burp's free counterpart. It shines in two places Burp Community does not: a capable **active scanner**, and first-class **automation** (headless mode, an API, a Docker "baseline scan") that makes it the default DAST tool for CI pipelines.

> [!warning] Authorized targets only
> The active scanner sends real attack payloads. Point it only at applications you may test, and keep it inside the configured context/scope.

## Parent Learning Order
curl -> Postman -> Burp Suite -> OWASP ZAP -> Nikto -> WPScan -> SQLmap

## Passive reading versus active probing

> *ZAP sits exactly where Burp sits in the request path. What is the distinction that matters for ZAP specifically?*
>
> Hold your answer — the section below is the response.

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
operator@lab:~$ zap.sh -cmd -quickurl http://track.meridian.test -quickout /tmp/zap.html
FAIL-NEW: 1   (High: SQL Injection - /search?q=)
```

## What the passive baseline structurally cannot find

```shell-session
operator@lab:~$ zap-baseline.py -t http://track.meridian.test        # passive
WARN-NEW: 5   FAIL-NEW: 0     (headers/cookies only — no attacks sent)
operator@lab:~$ zap.sh -cmd -quickurl http://track.meridian.test -quickout out.html   # active
FAIL-NEW: 1   (High: SQL Injection - /search?q=)
```

**The deliberate break:** the passive baseline **cannot** find the SQL injection — it only reads traffic, so it flags missing headers and stops. The active scan finds the real bug but sends attack payloads. Pick passive against production (safe, shallow) and active against a staging target you're authorized to attack (intrusive, deep). Choosing the wrong mode either misses vulnerabilities or hits a system you shouldn't — the single most important ZAP decision. And, exactly as with Burp, every High the active scanner reports is a *hypothesis*: confirm SQLi by hand (or chain into **SQLmap**) before it's a finding.

**How you'd spot it:** check which mode produced the report before reading it. A result containing only header and cookie findings is a passive baseline, and its silence about injection means nothing was tested for. The reverse is more serious: injection findings against a production target mean an active scan was pointed at a live system, which is an authorisation question rather than a finding.

## Security Implications

**Automation makes scope the control that matters most.** ZAP's headless mode, API and Docker baseline are what make it the default CI DAST tool — and they mean an active scan can run unattended, on a schedule, against whatever the context config points at. A misscoped CI job fires real attack payloads at production or a third party with no human watching, so the context/scope in the automation config is the only thing standing between a nightly scan and an unauthorised attack.

**Passive versus active is a safety decision, not a thoroughness preference.** The passive baseline only reads traffic — safe against production, but structurally blind to injection. The active scan finds the real bug and sends attack payloads. Choosing wrong either misses vulnerabilities or attacks a live system, which is the single most consequential ZAP setting.

**Active payloads land in the target's logs and can trigger real actions.** An active scan submits forms, follows links and fires injection strings, so it can create records, send emails or change state on an app that does not expect a robot. Its findings, like any scanner's, are hypotheses to confirm by hand or chain into [[SQLmap]].

## Summary

You should now be able to:

- Distinguish a passive web scan from an active one.
- Wire the right ZAP mode into CI to gate on web risks without attacking the app, and state what it necessarily misses.
- Explain why an automated High finding still requires manual confirmation, and how you'd verify it safely.

---
> 🔼 Up: [[Web Application Testing Tools]]
