#!/usr/bin/env python3
"""Offensive Security worked examples — batch 8 (External pentest + SSRF)."""
import re
import sys

EXTERNAL = '''## Worked Example: Separating the Routine From the Finding

An external test's hardest skill is not discovery — nmap does that — but judgment:
of everything exposed to the internet, which items are supposed to be there and
which are the report. A perimeter with a legitimate web service and one
accidentally-exposed admin panel makes the distinction concrete.

**Discovery and enumeration** in one pass:

```shell-session
attacker@ext:~$ sudo nmap -sS -sV -p 443,8080,3389 10.9.0.2 | grep -E '^[0-9]'
443/tcp  open   https      SimpleHTTPServer 0.6 (Python 3.11.2)
3389/tcp closed ms-wbt-server
8080/tcp open   http-proxy SimpleHTTPServer 0.6 (Python 3.11.2)
```

Read all three lines, because two of them are good news. `3389 closed` means RDP
is not exposed — a thing to confirm and move past, not ignore. `443 open` is a web
service on a web perimeter, which is expected. `8080 open` is the one that does
not belong: a second HTTP service on a non-standard port, which on a real
perimeter is very often a management console, a staging app, or a forgotten tool.

**Analysis** is the step that turns three open ports into one finding:

```shell-session
attacker@ext:~$ for p in 443 8080; do
>   printf ":%s -> " $p; curl -s "http://10.9.0.2:$p/" | grep -oiE '<title>[^<]*' | head -1 || echo "directory listing"
> done
:443 -> directory listing
:8080 -> directory listing
```

Fingerprinting both distinguishes the routine service from the exposed one by
what each actually is, rather than by port number alone — a discipline that
matters because attackers hide admin surfaces on port 443 precisely to survive a
lazy triage.

**The proof** is one benign request from the external vantage point:

```shell-session
attacker@ext:~$ curl -s -o /dev/null -w "admin panel from 'internet': HTTP %{http_code}\\n" http://10.9.0.2:8080/
admin panel from 'internet': HTTP 200
```

`200` from outside is the finding stated in the smallest possible form: a
management interface is reachable from the internet. No exploitation is needed or
appropriate — reachability *is* the vulnerability, and the remediation writes
itself. Note the restraint: the proof stops at demonstrating access, and does not
probe the panel's functions, because the scope of an external test is the exposure,
not what could be done after it.

'''

SSRF = '''## Worked Example: Reading an Internal Service Through a Public One

Server-side request forgery turns a server's own reachability into the attacker's.
The vulnerable feature is ordinary — an app that fetches a user-supplied URL — and
the exploit is simply pointing it inward.

**The specimen** fetches whatever URL it is handed, with no allowlist:

```python
url = request.args.get("url")
data = urllib.request.urlopen(url, timeout=2).read()   # VULNERABLE: any URL
return b"fetched: " + data
```

**Legitimate use** looks exactly as intended:

```shell-session
analyst@lab:~$ curl -s "http://127.0.0.1:8111/?url=http://example.com/" | head -c 40
fetched: <!doctype html>
```

The feature works, which is why it ships. Nothing about the happy path hints at
the problem — the app is doing precisely what it was built to do.

**The exploit** aims the same feature at a service the attacker cannot reach
directly:

```shell-session
analyst@lab:~$ curl -s "http://127.0.0.1:8111/?url=http://127.0.0.1:9001/"
fetched: INTERNAL-CANARY: secret admin panel
```

The internal service on `9001` binds to localhost and is unreachable from
outside. The attacker still read it — because the *server* reached it, and handed
the response back. That is the whole of SSRF: the request originates from the
server's network position, not the attacker's, so every trust the network places
in "traffic from this server" is now available to whoever controls the URL. On a
cloud host the highest-value target of this exact request is the instance
metadata endpoint, which hands out credentials to anything that can ask.

**Why blocklists fail**, in one line:

```shell-session
analyst@lab:~$ curl -s "http://127.0.0.1:8111/?url=http://2130706433:9001/" | head -c 30
fetched: INTERNAL-CANARY: secre
```

`2130706433` is `127.0.0.1` written as a single decimal integer, and it reaches
the same service. A filter that blocks the string `127.0.0.1` never sees it, and
the equivalents are numerous: decimal, octal, hex, IPv6-mapped, a DNS name that
resolves to a private address, a redirect from an allowed host to a blocked one.
Enumerating bad forms is a losing game, which is why the robust fix is an
*allowlist* of permitted destinations plus blocking the metadata IP outright —
deciding what the feature may reach, rather than trying to name everything it may
not.

'''

WORK = {
    "Offensive Security/Penetration Testing/Network Penetration Testing/External Network Pentesting.md": EXTERNAL,
    "Offensive Security/Penetration Testing/Web Application Penetration Testing/HTTP Architecture & Advanced Web Attacks/Server-Side Request Forgery.md": SSRF,
}

ANCHOR = re.compile(r"^## Task \d+ — (Failure Modes|Security Implications|Detection|Defen|Reporting)", re.M)
ANY_TASK = re.compile(r"^## Task \d+ — (.*)$", re.M)


def main():
    apply = "--apply" in sys.argv
    for rel, sec in WORK.items():
        try:
            src = open(rel, encoding="utf-8").read()
        except FileNotFoundError:
            print(f"  MISSING  {rel}")
            continue
        m = ANCHOR.search(src)
        if not m:
            print(f"  ✗ NO ANCHOR  {rel}")
            continue
        out = src[:m.start()] + sec + src[m.start():]
        out = out.replace("## Worked Example:", "## Task 0 — Worked Example:", 1)
        n = [0]

        def renum(mm):
            n[0] += 1
            return f"## Task {n[0]} — {mm.group(1)}"

        out = ANY_TASK.sub(renum, out)
        print(f"  ✓ {n[0]} tasks  {rel.split('/')[-1]}")
        if apply:
            open(rel, "w", encoding="utf-8").write(out)
    print(f"\n{'APPLIED' if apply else 'DRY RUN'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
