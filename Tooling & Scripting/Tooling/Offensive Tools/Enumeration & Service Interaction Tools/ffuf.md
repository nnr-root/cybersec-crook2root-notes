---
title: "ffuf"
aliases: ["Fuzz Faster U Fool"]
tags: [tree/tooling, cyber/tooling/offensive/ffuf, type/tool, difficulty/hard]
Domain: "[[Enumeration & Service Interaction Tools]]"
Color: "#708090"
---

# ffuf

ffuf ("Fuzz Faster U Fool") is a high-performance HTTP fuzzer. Its trick is a single keyword — `FUZZ` — that you place *anywhere* in a request (path, parameter, header, body, Host) and ffuf substitutes each wordlist entry, filtering responses by measurable properties. It is the most flexible tool in this category: the same engine does directory discovery, parameter mining, vhost enumeration, and auth fuzzing.

> [!warning] Authorized targets only
> Multi-position fuzzing can explode into millions of requests. Calculate the count first, rate-limit, and bound the runtime.

## Parent Learning Order
Gobuster -> ffuf -> feroxbuster -> dirsearch -> Netcat -> enum4linux

## Put FUZZ here, and define what counts as interesting

> *ffuf tries every word in your list against the target. What decides which responses you ever see?*
>
> Hold your answer — the section below is the response.

Everything ffuf does is "put `FUZZ` here, try every word, keep the interesting responses." *Interesting* is defined by matchers (`-m*`, keep) and filters (`-f*`, drop) on the response's status/size/words/lines — which is just the content-discovery status map applied programmatically.

Read the diagram and ffuf's filters make sense: `-fc 404` drops misses, `-fs 127` drops the soft-404 constant, `-mc 200,403` keeps the codes that mean "something's here." The keyword-and-filter model is why ffuf generalises beyond paths to *any* fuzzable position.

## Moving the keyword to fuzz any position

Directory discovery, with the soft-404 filtered by size:

```shell-session
operator@lab:~$ ffuf -w paths.txt -u https://app.example.test/FUZZ -mc all -fc 404 -fs 127 -t 10 -rate 20
admin    [Status: 403, Size: 226, Words: 18, Lines: 7]
api      [Status: 301, Size: 169, Words: 5, Lines: 8]
health   [Status: 200, Size: 31, Words: 2, Lines: 1]
```

Move the keyword to fuzz *parameters* or *vhosts* — same tool, different position:

```shell-session
operator@lab:~$ ffuf -w params.txt -u 'https://app.example.test/report?FUZZ=canary' -fs 842
operator@lab:~$ ffuf -w hosts.txt  -u https://192.0.2.10/ -H 'Host: FUZZ.example.test' -fs 127
```

`-ac` (auto-calibration) sends baseline probes and derives the filters for you — but inspect its choices, don't trust them blindly. Output evidence with `-of json -o`.

## Clusterbomb, and the combinatorics that bite you

Multiple wordlists + a mode = a combinatorial engine, and this is where operators self-inflict pain:

```text
wordlist A = 5,000   wordlist B = 2,000
-mode clusterbomb  →  5,000 × 2,000 = 10,000,000 requests
at 20 req/s  →  ~5.8 days
```

**The deliberate break:** `clusterbomb` (every combination) against two medium wordlists is ten million requests — days of traffic that will get you blocked or noticed. `pitchfork` (pair line 1 with line 1) is thousands. Picking the wrong mode isn't a syntax error; it's a self-DoS. Always compute `A × B` before launching, and prefer `pitchfork` unless you truly need every pairing.

The other classic failure is filters: an over-broad `-fs` silently drops the *real* result (zero hits), while missing calibration returns millions of soft-404 "hits." When results look wrong, compare a single request with **curl** before changing five flags at once, and keep a response sample for every retained cluster rather than treating each matched line as a finding.

## Summary

You should now be able to:

- Explain what the `FUZZ` keyword does, and why it makes ffuf more than a directory brute-forcer.
- Combine `-fs`, `-fc`, `-mc` and `-ac` to cut false positives.
- Explain why `clusterbomb` with two wordlists can become a self-DoS, and how mode choice controls it.

---
> 🔼 Up: [[Enumeration & Service Interaction Tools]]
