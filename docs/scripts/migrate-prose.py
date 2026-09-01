#!/usr/bin/env python3
"""
Crook2Root — pass 2: remove Crook/Operator/Root vocabulary from PROSE.

Pass 1 (migrate-structure.py) removed the vocabulary from headings, frontmatter
and section structure. This pass removes what is left inside body text, mapping
the old three levels onto the project's new difficulty scale.

  "> [!tip] Crook → Root"      ->  "> [!tip] Beginner → Expert"
  "**Crook** reboots ..."      ->  "**A beginner** reboots ..."
  "**Root** finds ..."         ->  "**An expert** finds ..."
  "- **Crook:** ..."           ->  "- **Easy:** ..."
  "- **Operator:** ..."        ->  "- **Medium:** ..."
  "- **Root:** ..."            ->  "- **Hard:** ..."
  stray level/* tags           ->  difficulty/*

The project NAME "Crook2Root" is deliberately preserved everywhere — the brand
stays, only the note structure and its vocabulary go.

USAGE
    python3 docs/scripts/migrate-prose.py            # dry run
    python3 docs/scripts/migrate-prose.py --apply
"""

import os
import re
import sys
import collections

SKIP_DIRS = {".git", ".obsidian", "assets", "graphify-out", ".claude", ".archive"}
SKIP_FILES = {"AGENTS.md", "README.md", "CONTRIBUTION.md"}   # rewritten by hand

# Order matters: the brand token is protected first, restored last.
BRAND = "\x00BRAND\x00"

RULES = [
    # callout titles
    (re.compile(r"\[!tip\]\s*Crook\s*(?:→|->)\s*Root", re.I), "[!tip] Beginner → Expert"),
    (re.compile(r"\[!warning\]\s*Crook\s*(?:→|->)\s*Root", re.I), "[!warning] Beginner → Expert"),
    (re.compile(r"\[!(\w+)\]\s*Crook\s*(?:→|->)\s*Operator\s*(?:→|->)\s*Root", re.I),
     r"[!\1] Beginner → Expert"),

    # labelled list items — map onto the difficulty scale
    (re.compile(r"^(\s*[-*]\s*)\*\*Crook:\*\*", re.M), r"\1**Easy:**"),
    (re.compile(r"^(\s*[-*]\s*)\*\*Operator:\*\*", re.M), r"\1**Medium:**"),
    (re.compile(r"^(\s*[-*]\s*)\*\*Root:\*\*", re.M), r"\1**Hard:**"),

    # inline bold contrasts
    (re.compile(r"\*\*Crook\*\*"), "**A beginner**"),
    (re.compile(r"\*\*Root\*\*(?=\s+(?:finds|pipes|checks|reads|knows|asks|traces|"
                r"understands|reasons|predicts|explains|designs|verifies))"), "**An expert**"),
    (re.compile(r"\*\*Root\*\*"), "**An expert**"),
    (re.compile(r"\*\*Operator\*\*"), "**A practitioner**"),

    # prose phrases
    (re.compile(r"\bhow a Crook compounds into a Root\b", re.I),
     "how a beginner compounds into an expert"),
    (re.compile(r"\bthe Crook's first step\b", re.I), "the beginner's first step"),
    (re.compile(r"\bCrook\s*(?:→|->)\s*Operator\s*(?:→|->)\s*Root\b"), "Beginner → Expert"),
    (re.compile(r"\bCrook\s*(?:→|->)\s*Root\b"), "Beginner → Expert"),

    # leftover tags
    (re.compile(r"level/crook"), "difficulty/easy"),
    (re.compile(r"level/operator"), "difficulty/medium"),
    (re.compile(r"level/root"), "difficulty/hard"),
]


def convert(text):
    # protect the brand name so no rule can damage it
    text = re.sub(r"[Cc]rook2[Rr]oot", BRAND, text)
    n = 0
    for pat, rep in RULES:
        text, k = pat.subn(rep, text)
        n += k
    return text.replace(BRAND, "Crook2Root"), n


def main():
    apply = "--apply" in sys.argv
    total = collections.Counter()
    touched = []

    for dp, dn, fn in os.walk("."):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in sorted(fn):
            if not f.endswith(".md") or f in SKIP_FILES:
                continue
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, ".")
            src = open(p, encoding="utf-8").read()
            out, n = convert(src)
            if out == src:
                continue
            touched.append((rel, n))
            total["files"] += 1
            total["edits"] += n
            if apply:
                open(p, "w", encoding="utf-8").write(out)

    mode = "APPLIED" if apply else "DRY RUN — nothing written"
    print(f"=== Crook2Root prose vocabulary pass — {mode} ===\n")
    print(f"Files changed {total['files']}   substitutions {total['edits']}\n")
    for rel, n in touched[:25]:
        print(f"   {n:>3}  {rel}")
    if len(touched) > 25:
        print(f"   ... and {len(touched)-25} more")
    print("\nNOTE: AGENTS.md, README.md and CONTRIBUTION.md are skipped on purpose —")
    print("they define the model and are rewritten by hand.")
    if not apply:
        print("Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
