#!/usr/bin/env python3
"""Find '## ' lines that live INSIDE fenced code blocks — these must never be
mistaken for section headings. Run from vault root."""
import os, re

SKIP = {".git", ".obsidian", "assets", "graphify-out", ".claude", "docs", ".archive"}
hits = []
unbalanced = []

for dp, dn, fn in os.walk("."):
    dn[:] = [d for d in dn if d not in SKIP]
    for f in fn:
        if not f.endswith(".md"):
            continue
        p = os.path.join(dp, f)
        rel = os.path.relpath(p, ".")
        if os.sep not in rel and rel != "Cyber Security.md":
            continue
        infence = False
        marker = None
        for i, line in enumerate(open(p, encoding="utf-8"), 1):
            m = re.match(r"^(`{3,})", line)
            if m:
                if not infence:
                    infence, marker = True, m.group(1)
                elif len(m.group(1)) >= len(marker):
                    infence, marker = False, None
                continue
            if infence and line.startswith("## "):
                hits.append((rel, i, line.rstrip()[:70]))
        if infence:
            unbalanced.append(rel)

print(f"'## ' lines inside code fences: {len(hits)}")
for r, i, l in hits[:20]:
    print(f"   {r}:{i}  {l}")
print(f"\nFiles with an unclosed fence: {len(unbalanced)}")
for r in unbalanced[:20]:
    print(f"   {r}")
