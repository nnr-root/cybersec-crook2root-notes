---
title: "SQLmap"
aliases: ["sqlmap"]
tags: [tree/tooling, cyber/tooling/offensive/web/sqlmap, type/tool, difficulty/hard]
Domain: "[[Web Application Testing Tools]]"
Color: "#708090"
verified: 2026-09-05
---

# SQLmap

> [!abstract] Note of [[Web Application Testing Tools]]
> SQLmap is a sniper: one request, one parameter, probed to the point where the app hands a query to the database. This note covers the two safety dials that keep a run bounded, why time-based inference is a statistical problem rather than a yes/no answer, and why a negative run is never proof of safety while an aggressive one can change state.

SQLmap automates SQL-injection detection, DBMS fingerprinting, and — with authorization — data extraction. It takes a single request, hammers one parameter with the injection techniques you'd otherwise try by hand, and infers the backend from how the app responds. It is enormously powerful and enormously dangerous: start with detection-only settings and never extract or reach the OS beyond explicit authorization.

> [!warning] Authorized, bounded testing only
> `--dump-all`, file writes, and `--os-shell` are destructive/high-impact. Use a captured request, the lowest useful `--risk`/`--level`, and a canary database — never point it at production and walk away.

## Parent Learning Order
curl -> Postman -> Burp Suite -> OWASP ZAP -> Nikto -> WPScan -> SQLmap

## One request, one parameter, probed deeply

> *Scanners sweep the whole server. What does SQLmap point at instead?*
>
> Hold your answer — the section below is the response.

Where scanners sweep the whole server, SQLmap is a sniper: it takes **one request and one parameter** and probes the deepest point in the path — the boundary where the app builds a SQL query and hands it to the database.

SQLmap automates the manual SQL-injection craft (see the **SQL Injection** leaf): it sends crafted values, watches how the response changes, and from those differences deduces *whether* the parameter is injectable, *which* technique works, and *what* DBMS is behind it. You already learned to do this by hand; SQLmap does it faster and more thoroughly — which is exactly why it must be bounded.

## Feeding it a saved request, and the two safety dials

Feed it a **saved request** from Burp (auth and headers come for free), target a parameter, and keep it gentle:

```shell-session
operator@lab:~$ sqlmap -r evidence/search-request.txt -p q --level 2 --risk 1 --technique=BEUT --batch
[INFO] GET parameter 'q' appears to be dynamic
[INFO] testing 'AND boolean-based blind - WHERE or HAVING clause'
[INFO] GET parameter 'q' is 'MySQL >= 5.0 boolean-based blind' injectable
[INFO] the back-end DBMS is MySQL
```

The two dials that keep you safe: `--level` (1-5, how many places/headers to test) and `--risk` (1-3, how *aggressive/state-changing* the payloads are). `--technique=BEUST` selects Boolean, Error, Union, Stacked, Time. Start low; escalate only with reason.

## Why time-based inference is a statistical minefield

SQLmap's time-based technique infers data from *how long* a response takes — and network noise makes that a statistical minefield:

```text
Baseline samples (ms):  112, 119, 108, 131, 116
Candidate samples (ms): 5118, 5109, 5127     ← injected SLEEP(5)
Interpretation: strong differential — but still verify manually
```

**The deliberate break:** a single delayed response is *not* proof. Congestion, a slow query, a GC pause, or a queue can all mimic a `SLEEP(5)`, and — worse — `--risk 3` enables **stacked queries** that can *change state* (a `; UPDATE` or `; DROP` your payload didn't intend on a fragile app). The safe method is many samples with a conservative threshold, the lowest risk that works, and a canary DB. And the cardinal rule: a **negative** SQLmap run is *not* proof of safety — second-order injection, unusual encodings, and business-logic context all evade automated detection. SQLmap tells you "yes, here's how"; it never authoritatively tells you "no." Treat `--tamper` (WAF evasion) as a separate, explicitly-approved exercise, not a default.

**How you'd spot it:** one slow response is noise. What you need is clean separation across repeated samples — the true condition consistently slow, the false condition consistently fast, over many trials; if the timings overlap at all, the oracle is not reliable yet. Check `--risk` before running, too: risk 3 against an application you cannot restore is a state-change hazard, not a detection setting.

## Security Implications

**Every payload reaches the database, and the aggressive ones change it.** `--dump` exfiltrates real data, `--os-shell` is remote code execution, and `--risk 3` enables stacked queries that can run a `; UPDATE` or `; DROP` the tester never intended. This is why a captured request, the lowest useful `--risk`/`--level`, and a canary database are not caution but method — pointing it at production and walking away is how an assessment becomes an outage.

**It is noisy in a place the app owner can see.** Thousands of malformed queries fill the database error log and the application log, and the classic injection strings trip any WAF. SQLmap is a detection-heavy tool, so the finding is often discovered by the defender mid-run.

**The source-level fix ends the whole class, WAF or not.** Parameterized queries and prepared statements make user input data rather than SQL, so no payload SQLmap sends can escape the parameter. `--tamper` WAF evasion is a separate, explicitly-approved exercise precisely because a WAF is a filter, not the fix.

**A negative run is not proof of safety.** Second-order injection, unusual encodings and business-logic context all evade automated detection — SQLmap tells you "yes, here's how", never authoritatively "no".

All use here is authorised and bounded; extraction and OS access are high-impact and require explicit sign-off beyond detection.

## Summary

You should now be able to:

- Name the manual technique SQLmap automates, and explain why it targets one parameter rather than the whole server.
- Keep a run bounded and safe with `--risk`, `--level` and a captured request.
- Explain why a time-based result needs many samples, and why a negative SQLmap run is not proof of safety.

---
> 🔼 Up: [[Web Application Testing Tools]]
