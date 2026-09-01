#!/usr/bin/env python3
"""
Crook2Root content-health audit.

Measures the vault against the Crook2Root Authoring Standard (documentation-only
model, plain descriptive section headings). Reports the baseline table used in the
Master Blueprint.

Usage:
    python3 docs/scripts/content-audit.py             # summary table
    python3 docs/scripts/content-audit.py --thin      # list sub-800w leaves
    python3 docs/scripts/content-audit.py --noexample # leaves with no worked example
    python3 docs/scripts/content-audit.py --nosummary # leaves with no Summary
    python3 docs/scripts/content-audit.py --violations# leaves containing banned constructs
    python3 docs/scripts/content-audit.py --json      # machine-readable

Run from the vault root. Read-only: touches nothing.
"""

import os
import re
import sys
import json
import collections

SKIP_DIRS = {".git", ".obsidian", "assets", "graphify-out", ".claude", "docs", ".archive"}
THIN_FLOOR = 800
STD_MIN, STD_MAX = 1500, 5000

SECTION_H2 = re.compile(r"^## (?!Summary\b|Parent Learning Order\b)(.+)$", re.M)
NUMBERED_H = re.compile(r"^#{2,6}\s+Task\s+\d+\s*[—–-]\s*", re.M)
SUMMARY_H2 = re.compile(r"^## Summary\s*$", re.M)
PLO_H2 = re.compile(r"^## Parent Learning Order", re.M)
FRONTMATTER = re.compile(r"^---.*?^---", re.S | re.M)
EMBED = re.compile(r"!\[\[([^\]|#]+)")
DIFFICULTY = re.compile(r"difficulty/(info|easy|medium|hard)")

# A worked example is a fenced block that shows a command and its output.
EXAMPLE_FENCE = re.compile(r"^```(shell-session|console|bash|shell|powershell|text|sql|http)",
                           re.M)

# A "Worked Mapping" heading followed by a real markdown table is the honest
# example form for a framework/methodology note that has no shell command.
WORKED_MAPPING = re.compile(r"^#{2,4} [^\n]*Worked Mapping[^\n]*\n(?:.*\n)*?\|.*\|", re.M)

# Constructs that must never appear in the public documentation repo.
BANNED = [
    ("lab section", re.compile(r"^#{2,4}\s+.*\b(Authorized Lab|Hands-On Lab|Runnable Lab)\b", re.M | re.I)),
    ("checkpoint", re.compile(r"^#{2,4}\s+.*\bCheckpoint\b", re.M | re.I)),
    ("level tag", re.compile(r"level/(crook|operator|root)")),
    ("three-level heading", re.compile(r"^#{2,4}\s+(Crook|Operator|Root)\s*[—–-]", re.M)),
    ("reader tasking", re.compile(r"\b(try (this|it) yourself|your turn|verify that you get|"
                                  r"now clean ?up|set up two (hosts|VMs))\b", re.I)),
    ("question box", re.compile(r"c2r-check|\[!question\]", re.I)),
]


def collect(root="."):
    rows = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if not fn.endswith(".md"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, root)
            if os.sep not in rel and rel != "Cyber Security.md":
                continue
            try:
                text = open(path, encoding="utf-8", errors="replace").read()
            except OSError:
                continue

            stem = os.path.splitext(fn)[0]
            parent = os.path.basename(dirpath)
            domain = rel.split(os.sep)[0]
            body = FRONTMATTER.sub("", text)
            sections = SECTION_H2.findall(body)
            diff = DIFFICULTY.search(text)

            rows.append({
                "rel": rel,
                "domain": domain,
                "words": len(body.split()),
                "is_index": stem == parent or stem == domain or "cyber/moc" in text,
                "sections": len(sections),
                "numbered": len(NUMBERED_H.findall(body)),
                "has_summary": bool(SUMMARY_H2.search(text)),
                "has_plo": bool(PLO_H2.search(text)),
                "has_example": bool(EXAMPLE_FENCE.search(text) or WORKED_MAPPING.search(text)),
                "difficulty": diff.group(1) if diff else None,
                "mermaid": text.count("```mermaid"),
                "embeds": EMBED.findall(text),
                "violations": [name for name, pat in BANNED if pat.search(text)],
            })
    return rows


def report(rows):
    by_domain = collections.defaultdict(list)
    for r in rows:
        by_domain[r["domain"]].append(r)

    hdr = (f"{'DOMAIN':<32}{'notes':>6}{'leaf':>6}{'med_w':>7}{'thin':>6}"
           f"{'std':>5}{'sect':>6}{'exmp':>6}{'summ':>6}{'diff':>6}{'viz':>5}")
    print(hdr)
    print("-" * len(hdr))

    totals = collections.Counter()
    for domain in sorted(by_domain, key=lambda d: -len(by_domain[d])):
        notes = by_domain[domain]
        leaves = [r for r in notes if not r["is_index"]]
        words = sorted(r["words"] for r in leaves) or [0]
        median = words[len(words) // 2]

        vals = {
            "notes": len(notes), "leaves": len(leaves),
            "thin": sum(1 for r in leaves if r["words"] < THIN_FLOOR),
            "std": sum(1 for r in leaves if STD_MIN <= r["words"] <= STD_MAX),
            "sect": sum(1 for r in leaves if r["sections"] > 0),
            "exmp": sum(1 for r in leaves if r["has_example"]),
            "summ": sum(1 for r in leaves if r["has_summary"]),
            "diff": sum(1 for r in leaves if r["difficulty"]),
            "viz": sum(1 for r in leaves if r["mermaid"] or r["embeds"]),
        }
        print(f"{domain:<32}{vals['notes']:>6}{vals['leaves']:>6}{median:>7}"
              f"{vals['thin']:>6}{vals['std']:>5}{vals['sect']:>6}{vals['exmp']:>6}"
              f"{vals['summ']:>6}{vals['diff']:>6}{vals['viz']:>5}")
        totals.update(vals)

    print("-" * len(hdr))
    print(f"{'TOTAL':<32}{totals['notes']:>6}{totals['leaves']:>6}{'':>7}"
          f"{totals['thin']:>6}{totals['std']:>5}{totals['sect']:>6}"
          f"{totals['exmp']:>6}{totals['summ']:>6}{totals['diff']:>6}{totals['viz']:>5}")

    leaves = [r for r in rows if not r["is_index"]]
    n = len(leaves)
    print()
    print(f"Leaves with no worked example:  {sum(1 for r in leaves if not r['has_example']):>4} / {n}")
    print(f"Leaves with no Summary:         {sum(1 for r in leaves if not r['has_summary']):>4} / {n}")
    print(f"Leaves with no body sections:   {sum(1 for r in leaves if r['sections'] == 0):>4} / {n}")
    print(f"Leaves with numbered headings:  {sum(1 for r in leaves if r['numbered']):>4} / {n}")
    print(f"Leaves with no difficulty tag:  {sum(1 for r in leaves if not r['difficulty']):>4} / {n}")
    print(f"Leaves with zero visual:        {sum(1 for r in leaves if not (r['mermaid'] or r['embeds'])):>4} / {n}")

    print("\nDifficulty distribution:")
    for k, v in collections.Counter(
            r["difficulty"] for r in rows if r["difficulty"]).most_common():
        print(f"   difficulty/{k:<8} {v}")

    viol = [r for r in rows if r["violations"]]
    print(f"\nSTANDARD VIOLATIONS (banned constructs): {len(viol)} note(s)")
    for r in viol[:15]:
        print(f"   {r['rel']}  ->  {', '.join(r['violations'])}")

    if os.path.isdir("assets"):
        have = set(os.listdir("assets"))
        broken = [(r["rel"], e) for r in rows for e in r["embeds"] if e not in have]
        if broken:
            print(f"\nUnresolved embeds: {len(broken)}")
            for rel, emb in broken[:10]:
                print(f"   {rel} -> {emb}")

    return 1 if viol else 0


def main():
    rows = collect()
    args = sys.argv[1:]
    leaves = [r for r in rows if not r["is_index"]]

    if "--json" in args:
        json.dump(rows, sys.stdout, indent=2)
        return 0
    if "--thin" in args:
        for r in sorted((x for x in leaves if x["words"] < THIN_FLOOR),
                        key=lambda x: x["words"]):
            print(f"{r['words']:>6}  {r['rel']}")
        return 0
    if "--noexample" in args:
        for r in sorted((x for x in leaves if not x["has_example"]), key=lambda x: x["rel"]):
            print(f"{r['words']:>6}  {r['rel']}")
        return 0
    if "--nosummary" in args:
        for r in sorted((x for x in leaves if not x["has_summary"]), key=lambda x: x["rel"]):
            print(f"{r['words']:>6}  {r['rel']}")
        return 0
    if "--violations" in args:
        for r in rows:
            if r["violations"]:
                print(f"{r['rel']}  ->  {', '.join(r['violations'])}")
        return 0

    return report(rows)


if __name__ == "__main__":
    sys.exit(main())
