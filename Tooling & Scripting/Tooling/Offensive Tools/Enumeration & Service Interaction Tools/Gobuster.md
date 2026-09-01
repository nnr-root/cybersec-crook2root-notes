---
title: "Gobuster"
aliases: ["Gobuster Content Discovery"]
tags: [tree/tooling, cyber/tooling/offensive/gobuster, type/tool, difficulty/medium]
Domain: "[[Enumeration & Service Interaction Tools]]"
Color: "#708090"
---

# Gobuster

Gobuster is a fast Go-based brute-forcer for web paths, virtual hosts, and DNS labels. It generates requests from a wordlist and reports how the server responded — but the response is *evidence to interpret*, not a verdict. Its speed and simple modes make it a common first content-discovery pass.

> [!warning] Authorized targets only
> Brute-forcing generates thousands of requests. Scope the target, throttle with `--delay`, and expect to appear in logs.

## Parent Learning Order
Gobuster -> ffuf -> feroxbuster -> dirsearch -> Netcat -> enum4linux

## Inferring what exists from status codes

> *A web server never lists its URLs. So how do you find out what is on it?*
>
> Hold your answer — the section below is the response.

A web server only tells you about URLs you request. Content discovery means asking for thousands of likely paths and **reading the status code** to infer what exists.

The diagram is the whole skill. Gobuster shows you a `Status:` and a `Size:` for every hit; you read them together. A `403` means *it exists but you're forbidden* (a finding); a `301` is usually a directory to recurse into; and — the trap — a `200` might be a real page **or** a soft-404 lying to you. Learn to read the code and size, and Gobuster's output becomes a map.

## Modes: paths, vhosts, subdomains

Gobuster works in *modes* — `dir` (paths), `vhost` (Host-header routing), `dns` (subdomains):

```shell-session
operator@lab:~$ gobuster dir -u https://app.example.test -w paths.txt -x html,json \
    -t 10 --delay 100ms -b 404 --exclude-length 127 -o evidence/gobuster.txt
/health   (Status: 200) [Size: 31]
/admin    (Status: 403) [Size: 226]
/api      (Status: 301) [Size: 169] [--> /api/]
```

| Mode | Finds | Key flags |
|---|---|---|
| `dir` | paths/files | `-w`, `-x` (extensions), `-b` (blacklist status), `--exclude-length`, `-r` |
| `vhost` | virtual hosts | `-w`, `--append-domain`, `--exclude-length` |
| `dns` | subdomains | `-d`, `--wildcard`, `--show-cname` |

HTTP controls that matter: `-c` (cookies for authenticated discovery), `-H` (headers), `-k` (skip TLS verify — record it), `--proxy`. For authenticated runs use a dedicated low-priv test session and confirm it's live first — a stale cookie silently turns the whole run into login-page discovery.

## Calibrating against a server that lies about 404

Gobuster decides "hit vs. miss" from the status code, which a misconfigured server weaponises. **Always calibrate first** by requesting random nonexistent paths:

```shell-session
operator@lab:~$ for p in zzz-a zzz-b; do curl -sk -o /dev/null -w "$p %{http_code} %{size_download}\n" "https://app.example.test/$p"; done
zzz-a 200 127
zzz-b 200 127
```

**The deliberate break:** two paths that *cannot* exist both return `200` with a 127-byte body — the server has no real 404, so every guess will look like a hit. Gobuster cannot infer truth from a lying status code. The fix is `--exclude-length 127` (drop the constant soft-404 size) — mapping exactly to the diagram's soft-404 warning. Without calibration, a "successful" scan of hundreds of 200s is pure noise; with it, the real routes surface.

**How you'd spot it:** calibrate before trusting anything — request two paths that cannot possibly exist and compare. Identical status *and* identical length means the server has no real 404, and every result in the run is noise until that length is filtered out. After the fact, the same finding looks like a results list where nearly every hit shares one byte count.

Defensively, a Gobuster run is a recognizable burst of `404`s (or `403`s) from one source in seconds — trivial to detect, and a reason to prefer proper 404 semantics (soft-404s break the *defender's* log analysis too).

## Summary

You should now be able to:

- Judge whether a `403` on `/server-status` from Gobuster is a finding, and explain why.
- Explain why a `dir` run must be calibrated against random paths before its results are trusted.
- Explain soft-404 detection and why response-size (not status alone) is required to trust results.

---
> 🔼 Up: [[Enumeration & Service Interaction Tools]]
