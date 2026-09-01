#!/usr/bin/env python3
"""
strip-task-numbers.py — remove the `## Task N — ` prefix from lesson headings.

The public documentation repo is prose, not a course runner: numbered tasks are a
website construct and belong in the private site repo. This script rewrites

    ## Task 3 — The EtherType: The Demultiplexing Key
into
    ## The EtherType: The Demultiplexing Key

Fence-aware: `##` lines inside fenced code blocks are never touched.
Read-only unless --apply is passed.

Usage:
    python3 docs/scripts/strip-task-numbers.py            # dry run, summary
    python3 docs/scripts/strip-task-numbers.py --verbose  # dry run, per-file
    python3 docs/scripts/strip-task-numbers.py --apply    # write changes
"""
import re, sys, pathlib
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[2]
SKIP = {".archive", "_to_delete", ".git", ".obsidian", "node_modules"}
TASK = re.compile(r"^(#{2,6})\s+Task\s+(\d+)\s*—\s*(.+?)\s*$")

def fence_mask(lines):
    mask = [False] * len(lines)
    infence, marker = False, None
    for i, line in enumerate(lines):
        m = re.match(r"^(`{3,}|~{3,})", line)
        if m:
            mask[i] = True
            if not infence:
                infence, marker = True, m.group(1)
            elif m.group(1)[0] == marker[0] and len(m.group(1)) >= len(marker):
                infence, marker = False, None
            continue
        mask[i] = infence
    return mask

def main():
    apply = "--apply" in sys.argv
    verbose = "--verbose" in sys.argv
    notes = sorted(p for p in ROOT.rglob("*.md") if not (SKIP & set(p.parts)))

    files_changed = 0
    heads = 0
    dupes = []
    for p in notes:
        src = p.read_text(encoding="utf-8")
        lines = src.split("\n")
        mask = fence_mask(lines)
        out, n, titles = [], 0, Counter()
        for i, line in enumerate(lines):
            if not mask[i]:
                m = TASK.match(line)
                if m:
                    title = m.group(3)
                    out.append(f"{m.group(1)} {title}")
                    titles[title.lower()] += 1
                    n += 1
                    continue
            out.append(line)
        if n:
            files_changed += 1
            heads += n
            d = [t for t, c in titles.items() if c > 1]
            if d:
                dupes.append((p.relative_to(ROOT), d))
            if verbose:
                print(f"  {n:3d}  {p.relative_to(ROOT)}")
            if apply:
                p.write_text("\n".join(out), encoding="utf-8")

    print(f"\n{'APPLIED' if apply else 'DRY RUN'}: {heads} headings in {files_changed} files")
    if dupes:
        print(f"\n!! {len(dupes)} files would end up with duplicate H2 titles:")
        for f, d in dupes:
            print(f"   {f}: {d}")
    if not apply:
        print("Re-run with --apply to write.")

if __name__ == "__main__":
    main()
