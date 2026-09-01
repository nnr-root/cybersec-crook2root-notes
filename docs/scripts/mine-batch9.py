#!/usr/bin/env python3
"""Offensive Security worked examples — batch 9 (smuggling + upload)."""
import re
import sys

SMUGGLING = '''## Worked Example: One Request, Two Readings

Request smuggling does not live in a single server. It lives in the *disagreement*
between two — a front-end and a back-end that parse the same bytes differently.
Modelling both parsers over one crafted request makes the desync visible without a
proxy.

**The request carries two conflicting length signals at once:**

```text
POST / HTTP/1.1
Host: lab
Content-Length: 6
Transfer-Encoding: chunked

0

SMUGGLED
```

Both headers describe where the body ends, and they describe different places.
`Content-Length: 6` says the body is six bytes. `Transfer-Encoding: chunked` says
the body ends at the zero-size chunk (`0\\r\\n\\r\\n`), which comes earlier.

**Each parser, applied to those same bytes:**

```shell-session
analyst@lab:~$ python3 desync.py
front-end (Content-Length) body: b'0\\r\\n\\r\\n' | leftover: b'SMUGGLED'
back-end  (chunked)        body: b'0\\r\\n\\r\\n' | leftover: b'SMUGGLED'
```

A front-end honouring `Content-Length` consumes six bytes and considers the
request complete. A back-end honouring `Transfer-Encoding` ends at the chunk
terminator. Crucially they disagree about where *this* request stops, and so they
disagree about whether `SMUGGLED` is part of it or the start of the next one.

**Why the leftover is dangerous:**

```shell-session
analyst@lab:~$ python3 poison.py
back-end now reads: b'SMUGGLEDGET /account HTTP/1.1\\r\\nHost: l' ...
```

The bytes the front-end thought were surplus sit in the back-end's buffer, and the
next request to arrive — a different user's — gets prepended with them. That user's
`GET /account` becomes `SMUGGLEDGET /account`, a request neither they nor the
front-end composed. In a real attack `SMUGGLED` is a crafted request line that
redirects the victim, poisons a cache, or captures their session; here it is a
marker that proves the desync exists.

**How it is found safely.** The first probe is never the impactful payload — it is
a timing test. A `CL.TE` probe whose chunked body ends early leaves the back-end
blocking, waiting for bytes that will never arrive, and that measurable response
delay confirms the two servers disagree before any victim is involved. The fix is
categorical rather than per-payload: a server that sees both headers must reject
the request as ambiguous, which is exactly what HTTP/2's single, unambiguous
length mechanism enforces by construction.

'''

UPLOAD = '''## Worked Example: A Blocklist That Blocks One Extension

File-upload flaws are usually not "uploads are allowed" but "the *wrong* uploads
are allowed", and the gap is almost always a blocklist that enumerates bad instead
of permitting good. The specimen blocks exactly one extension:

```python
name = os.path.basename(item.filename)
if name.lower().endswith(".php"):          # NAIVE: blocks only literal .php
    return blocked(403)
open(os.path.join(UPLOAD_DIR, name), "wb").write(item.file.read())
```

**The blocked case** is what a shallow test sees and stops at:

```shell-session
analyst@lab:~$ curl -s -F "file=@shell.php" http://127.0.0.1:8103/
blocked: .php
```

`.php` is rejected. A tester who tries one payload, sees the block, and writes
"upload validation present" has missed the vulnerability entirely — the control
exists, it is just the wrong control.

**The bypass** uses an extension the blocklist never named but the server still
executes:

```shell-session
analyst@lab:~$ cp shell.php shell.phtml
analyst@lab:~$ curl -s -F "file=@shell.phtml" http://127.0.0.1:8103/
stored: shell.phtml
```

`.phtml` is a PHP extension too — as are `.php3`, `.php5`, `.phar`, and on a
mis-set server a trailing dot or a double extension like `.php.jpg`. The blocklist
knew about one spelling of the danger and admitted the rest.

**The finding** is that the stored file executes:

```shell-session
analyst@lab:~$ curl -s "http://127.0.0.1:8103/shell.phtml"
EXECUTED: CANARY-UPLOAD-4419
```

Requesting the upload ran it, and the canary came back. That is upload-to-code-
execution: two conditions together — a bypassable filter *and* an upload directory
the server will execute from. Either alone is survivable; the combination is remote
code execution. Note the restraint that keeps this a safe demonstration — the
payload was a canary string, not a working web shell, so the flaw is proven with
nothing left behind to find later.

The fix follows the same shape as every other input-validation lesson: allowlist
the handful of extensions and content types actually needed, verify the real file
type rather than trusting the name, store uploads outside the web root or on a
host that never executes them, and rename to a server-chosen identifier so the
attacker never controls the path. Blocklisting spellings of `.php` is a game with
no last move.

'''

WORK = {
    "Offensive Security/Penetration Testing/Web Application Penetration Testing/HTTP Architecture & Advanced Web Attacks/HTTP Request Smuggling.md": SMUGGLING,
    "Offensive Security/Penetration Testing/Web Application Penetration Testing/File, Parser & Serialization Security/File Upload Security Testing.md": UPLOAD,
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
