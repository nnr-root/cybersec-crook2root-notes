---
title: "SQLmap"
aliases: ["sqlmap"]
tags: [tree/tooling, cyber/tooling/offensive/web/sqlmap, type/tool, level/root]
Domain: "[[Web Application Testing Tools]]"
Color: "#708090"
---

# SQLmap

SQLmap automates SQL-injection detection, DBMS fingerprinting, and — with authorization — data extraction. It takes a single request, hammers one parameter with the injection techniques you'd otherwise try by hand, and infers the backend from how the app responds. It is enormously powerful and enormously dangerous: start with detection-only settings and never extract or reach the OS beyond explicit authorization.

> [!warning] Authorized, bounded testing only
> `--dump-all`, file writes, and `--os-shell` are destructive/high-impact. Use a captured request, the lowest useful `--risk`/`--level`, and a canary database — never point it at production and walk away.

## Parent Learning Order
curl -> Postman -> Burp Suite -> OWASP ZAP -> Nikto -> WPScan -> SQLmap

## Crook — The Mental Model

Where scanners sweep the whole server, SQLmap is a sniper: it takes **one request and one parameter** and probes the deepest point in the path — the boundary where the app builds a SQL query and hands it to the database.

![[tool_web_request_path.svg]]

SQLmap automates the manual SQL-injection craft (see the **SQL Injection** leaf): it sends crafted values, watches how the response changes, and from those differences deduces *whether* the parameter is injectable, *which* technique works, and *what* DBMS is behind it. You already learned to do this by hand; SQLmap does it faster and more thoroughly — which is exactly why it must be bounded.

## Operator — Make It Work

Feed it a **saved request** from Burp (auth and headers come for free), target a parameter, and keep it gentle:

```shell-session
operator@lab:~$ sqlmap -r evidence/search-request.txt -p q --level 2 --risk 1 --technique=BEUT --batch
[INFO] GET parameter 'q' appears to be dynamic
[INFO] testing 'AND boolean-based blind - WHERE or HAVING clause'
[INFO] GET parameter 'q' is 'MySQL >= 5.0 boolean-based blind' injectable
[INFO] the back-end DBMS is MySQL
```

The two dials that keep you safe: `--level` (1-5, how many places/headers to test) and `--risk` (1-3, how *aggressive/state-changing* the payloads are). `--technique=BEUST` selects Boolean, Error, Union, Stacked, Time. Start low; escalate only with reason.

## Root — Internals & The Deliberate Break

SQLmap's time-based technique infers data from *how long* a response takes — and network noise makes that a statistical minefield:

```text
Baseline samples (ms):  112, 119, 108, 131, 116
Candidate samples (ms): 5118, 5109, 5127     ← injected SLEEP(5)
Interpretation: strong differential — but still verify manually
```

**The deliberate break:** a single delayed response is *not* proof. Congestion, a slow query, a GC pause, or a queue can all mimic a `SLEEP(5)`, and — worse — `--risk 3` enables **stacked queries** that can *change state* (a `; UPDATE` or `; DROP` your payload didn't intend on a fragile app). The safe method is many samples with a conservative threshold, the lowest risk that works, and a canary DB. And the cardinal rule: a **negative** SQLmap run is *not* proof of safety — second-order injection, unusual encodings, and business-logic context all evade automated detection. SQLmap tells you "yes, here's how"; it never authoritatively tells you "no." Treat `--tamper` (WAF evasion) as a separate, explicitly-approved exercise, not a default.

## Crook → Operator → Root Checkpoint

- **Crook:** What manual technique does SQLmap automate, and why does it target one parameter rather than the whole server?
- **Operator:** How do `--risk` and `--level` plus a captured request keep a run bounded and safe?
- **Root:** Explain why a time-based result needs many samples, and why a negative SQLmap run is not proof of safety.

---
> 🔼 Up: [[Web Application Testing Tools]]
