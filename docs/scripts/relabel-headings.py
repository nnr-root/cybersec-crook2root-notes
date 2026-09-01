#!/usr/bin/env python3
"""
relabel-headings.py — replace the four generic section titles with subgoal labels.

Retires "The Mental Model", "Practical Usage", "Internals & Edge Cases" and
"Failure Modes and Interpretation" across the corpus, substituting the label
written for that specific section (see heading-labels.py).

Fence-aware. Read-only unless --apply.

    python3 docs/scripts/relabel-headings.py            # dry run
    python3 docs/scripts/relabel-headings.py --apply    # write
"""
import os
import re
import sys
import importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

_s = importlib.util.spec_from_file_location("ped", os.path.join(HERE, "pedagogy-check.py"))
ped = importlib.util.module_from_spec(_s); _s.loader.exec_module(ped)
_l = importlib.util.spec_from_file_location("lab", os.path.join(HERE, "heading-labels.py"))
lab = importlib.util.module_from_spec(_l); _l.loader.exec_module(lab)

KIND = {"the mental model": "M", "mental model": "M",
        "practical usage": "P", "practical use": "P",
        "internals & edge cases": "I", "internals and edge cases": "I",
        "failure modes and interpretation": "F"}


def main():
    apply = "--apply" in sys.argv
    done = miss = files = 0
    missing = []
    os.chdir(ROOT)
    for rel in sorted(ped.note_files(".")):
        text = open(rel, encoding="utf-8").read()
        lines = text.split("\n")
        mask = ped.fence_mask(lines)
        stem = os.path.splitext(os.path.basename(rel))[0]
        out, hits = [], 0
        for i, line in enumerate(lines):
            m = re.match(r"^(#{2,4})\s+(.+?)\s*$", line) if not mask[i] else None
            k = KIND.get(m.group(2).strip().lower().rstrip(":")) if m else None
            if not k:
                out.append(line)
                continue
            new = lab.LABELS.get((stem, k))
            if not new:
                missing.append(f"{rel}  [{k}]  {m.group(2)}")
                miss += 1
                out.append(line)
                continue
            out.append(f"{m.group(1)} {new}")
            hits += 1
        if hits:
            files += 1
            done += hits
            if apply:
                open(rel, "w", encoding="utf-8").write("\n".join(out))

    print(f"{'RELABELLED' if apply else 'DRY RUN'}: {done} heading(s) in {files} file(s)")
    if missing:
        print(f"\n!! {miss} heading(s) with no label written — add them to heading-labels.py:")
        for x in missing:
            print("   ", x)
    if not apply:
        print("re-run with --apply to write.")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
