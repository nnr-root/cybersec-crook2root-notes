#!/usr/bin/env python3
"""
Crook2Root — structure migration to the TryHackMe task model.

Removes the Crook / Operator / Root three-level structure from every note and
converts the vault to numbered THM-style tasks. Public repo carries NO labs and
NO questions; those move to the private website repo later.

WHAT IT DOES, per note
  1. tags      level/crook -> difficulty/easy, level/operator -> difficulty/medium,
               level/root  -> difficulty/hard, index notes -> difficulty/info
  2. labs      lab sections are CUT and archived to .archive/labs/
  3. summary   "Crook -> Operator -> Root Checkpoint" becomes "## Summary" with the
               three-level labels stripped, under "You should now be able to:"
  4. headings  Crook/Operator/Root heading vocabulary removed:
                 "Crook - The Mental Model"                -> "The Mental Model"
                 "Operator - Make It Work"                 -> "Practical Usage"
                 "Root - Internals & The Deliberate Break" -> "Internals & Edge Cases"
                 "Root - <topic>"                          -> "<topic>"
                 "Start Here - Crook"                      -> "Start Here"
  5. tasks     content H2s in LEAF notes are renumbered "## Task N - <title>"

NOT TOUCHED: frontmatter Domain/Color/title/aliases, Parent Learning Order lines,
index-note navigation sections, the footer parent link, any prose.

USAGE
    python3 docs/scripts/migrate-structure.py            # dry run, reports only
    python3 docs/scripts/migrate-structure.py --apply    # writes changes

Run from the vault root. Every note is recoverable with `git checkout -- .`
because nothing is staged or committed.
"""

import os
import re
import sys
import shutil
import collections

SKIP_DIRS = {".git", ".obsidian", "assets", "graphify-out", ".claude", "docs", ".archive"}
ARCHIVE = ".archive"

# ── section headings we cut out entirely (labs) ────────────────────────────────
LAB_H2 = re.compile(
    r"^##\s+.*\b(Authorized Lab|Hands-On Lab|Runnable Lab|Mastery lab|Practical Lab|Lab)\b.*$",
    re.I)
# ── section heading we convert into a Summary ─────────────────────────────────
CHECK_H2 = re.compile(r"^#{2,3}\s+.*\bCheckpoint\b.*$", re.I)

# ── navigation sections in index notes: never renumbered as tasks ─────────────
NAV_H2 = re.compile(
    r"^##\s+.*(Learning Path|Notes in this branch|leaves in this branch|Branches|"
    r"Master Notes|Tools in this category|Purpose categories|Curriculum|"
    r"Related Master Notes|Armory branches|Language paths|Engineering paths)",
    re.I)

PLO_H2 = re.compile(r"^##\s+Parent Learning Order\s*$", re.I)
FOOTER = re.compile(r"^>\s*🔼\s*Up:", re.M)

LEVEL_MAP = {"level/crook": "difficulty/easy",
             "level/operator": "difficulty/medium",
             "level/root": "difficulty/hard"}

# ── heading text rewrites, longest/most specific first ────────────────────────
HEAD_REWRITES = [
    (re.compile(r"^Start at Zero:\s*(.+)$", re.I), r"\1"),
    (re.compile(r"^Start at Zero\s*$", re.I), "Start Here"),
    (re.compile(r"^Crook\s*[—–-]\s*The Mental Model.*$", re.I), "The Mental Model"),
    (re.compile(r"^Operator\s*[—–-]\s*Make It Work.*$", re.I), "Practical Usage"),
    (re.compile(r"^Root\s*[—–-]\s*Internals.*Deliberate Break.*$", re.I), "Internals & Edge Cases"),
    (re.compile(r"^Start Here\s*[—–-]\s*Crook\s*$", re.I), "Start Here"),
    (re.compile(r"^Crook\s*[—–-]\s*(.+)$", re.I), r"\1"),
    (re.compile(r"^Operator\s*[—–-]\s*(.+)$", re.I), r"\1"),
    (re.compile(r"^Root\s*[—–-]\s*(.+)$", re.I), r"\1"),
]

BULLET_LABEL = re.compile(r"^(\s*[-*]\s*)\*\*(Crook|Operator|Root)\s*:?\*\*\s*:?\s*", re.I)


def slugify(rel):
    return re.sub(r"[^A-Za-z0-9]+", "-", rel.replace(".md", "")).strip("-").lower()


def split_frontmatter(text):
    m = re.match(r"^(---\n.*?\n---\n)(.*)$", text, re.S)
    return (m.group(1), m.group(2)) if m else ("", text)


def is_index(rel, text):
    stem = os.path.splitext(os.path.basename(rel))[0]
    parent = os.path.basename(os.path.dirname(rel))
    top = rel.split(os.sep)[0]
    return stem == parent or stem == top or "cyber/moc" in text


def fence_mask(lines):
    """True for every line inside a fenced code block.

    Markdown notes legitimately contain '## ' lines inside fences (note-taking
    templates, markdown examples). Those are content, never headings, and must
    never be renumbered or treated as a section boundary.
    """
    mask = [False] * len(lines)
    infence, marker = False, None
    for i, line in enumerate(lines):
        m = re.match(r"^(`{3,})", line)
        if m:
            mask[i] = True
            if not infence:
                infence, marker = True, m.group(1)
            elif len(m.group(1)) >= len(marker):
                infence, marker = False, None
            continue
        mask[i] = infence
    return mask


def h2_blocks(lines, mask=None):
    """Yield (start, end) index pairs for each real '## ' section, end exclusive."""
    if mask is None:
        mask = fence_mask(lines)
    idx = [i for i, l in enumerate(lines) if l.startswith("## ") and not mask[i]]
    for n, s in enumerate(idx):
        e = idx[n + 1] if n + 1 < len(idx) else len(lines)
        yield s, e


def trim_footer(lines, start, end):
    """Shrink a section's end so the trailing '---' + parent-link footer survives."""
    for i in range(start + 1, end):
        if lines[i].strip() == "---" and any(
                FOOTER.match(l) for l in lines[i:min(i + 4, end)]):
            return i
    return end


def migrate(text, rel):
    fm, body = split_frontmatter(text)
    stats = collections.Counter()
    archived = {}

    # ── 1. frontmatter tags ───────────────────────────────────────────────────
    index = is_index(rel, text)
    for old, new in LEVEL_MAP.items():
        if old in fm:
            fm = fm.replace(old, "difficulty/info" if index else new)
            stats["tags"] += 1

    lines = body.split("\n")

    # ── 2 & 3. cut labs, convert checkpoints ──────────────────────────────────
    drop = set()
    mask = fence_mask(lines)
    for s, e in h2_blocks(lines, mask):
        head = lines[s]
        if LAB_H2.match(head) and "Learning Path" not in head:
            real_e = trim_footer(lines, s, e)
            archived.setdefault("labs", []).append("\n".join(lines[s:real_e]).rstrip())
            drop.update(range(s, real_e))
            stats["labs_cut"] += 1
        elif CHECK_H2.match(head):
            real_e = trim_footer(lines, s, e)
            seg = lines[s:real_e]
            archived.setdefault("checkpoints", []).append("\n".join(seg).rstrip())
            body_lines = [l for l in seg[1:] if l.strip()]
            bullets = [BULLET_LABEL.sub(r"\1", l) for l in body_lines
                       if BULLET_LABEL.match(l)]
            if bullets:
                new_sec = ["## Summary", "", "You should now be able to:", ""] + bullets + [""]
            else:
                cleaned = [BULLET_LABEL.sub(r"\1", l) for l in seg[1:]]
                new_sec = ["## Summary"] + cleaned
            lines[s:real_e] = new_sec
            stats["summaries"] += 1
            break  # indices shifted; checkpoint is last section anyway

    if drop:
        lines = [l for i, l in enumerate(lines) if i not in drop]

    # ── 3b. checkpoints nested at H3/H4 (13 notes) ────────────────────────────
    # The H2 scan above never reaches these. Promote them to a top-level Summary
    # so every note ends the same way regardless of how it was originally nested.
    mask = fence_mask(lines)
    for i, l in enumerate(lines):
        if mask[i] or not re.match(r"^#{3,4}\s+.*\bCheckpoint\b", l, re.I):
            continue
        e = len(lines)
        for j in range(i + 1, len(lines)):
            if not mask[j] and re.match(r"^#{2,4}\s", lines[j]):
                e = j
                break
        e = trim_footer(lines, i, e)
        seg = lines[i:e]
        archived.setdefault("checkpoints", []).append("\n".join(seg).rstrip())
        bullets = [BULLET_LABEL.sub(r"\1", x) for x in seg[1:] if BULLET_LABEL.match(x)]
        if bullets:
            lines[i:e] = ["## Summary", "", "You should now be able to:", ""] + bullets + [""]
        else:
            lines[i:e] = ["## Summary"] + [BULLET_LABEL.sub(r"\1", x) for x in seg[1:]]
        stats["summaries"] += 1
        break

    # ── 4. heading vocabulary ─────────────────────────────────────────────────
    mask = fence_mask(lines)          # recomputed: line indices shifted above
    for i, l in enumerate(lines):
        if mask[i]:
            continue
        m = re.match(r"^(#{2,4})\s+(.*)$", l)
        if not m:
            continue
        hashes, txt = m.group(1), m.group(2).strip()
        for pat, rep in HEAD_REWRITES:
            if pat.match(txt):
                new = pat.sub(rep, txt).strip()
                if new and new != txt:
                    lines[i] = f"{hashes} {new}"
                    stats["headings"] += 1
                break

    # ── 5. task numbering (leaf notes only) ───────────────────────────────────
    if not index:
        n = 0
        for i, l in enumerate(lines):
            if mask[i] or not l.startswith("## "):
                continue
            txt = l[3:].strip()
            if PLO_H2.match(l) or NAV_H2.match(l) or txt.lower().startswith("summary"):
                continue
            if re.match(r"^Task\s+\d+", txt, re.I):
                n += 1
                continue
            n += 1
            lines[i] = f"## Task {n} — {txt}"
            stats["tasks"] += 1

    out = fm + "\n".join(lines)
    out = re.sub(r"\n{4,}", "\n\n\n", out)
    return out, stats, archived


def main():
    apply = "--apply" in sys.argv
    root = os.getcwd()
    total = collections.Counter()
    touched = []
    arch_files = []

    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in sorted(fn):
            if not f.endswith(".md"):
                continue
            path = os.path.join(dp, f)
            rel = os.path.relpath(path, root)
            if os.sep not in rel and rel != "Cyber Security.md":
                continue
            src = open(path, encoding="utf-8").read()
            out, stats, archived = migrate(src, rel)
            if out == src:
                continue
            touched.append((rel, stats))
            total.update(stats)
            if apply:
                open(path, "w", encoding="utf-8").write(out)
                for kind, blocks in archived.items():
                    d = os.path.join(root, ARCHIVE, kind)
                    os.makedirs(d, exist_ok=True)
                    ap = os.path.join(d, slugify(rel) + ".md")
                    with open(ap, "w", encoding="utf-8") as fh:
                        fh.write(f"# Archived {kind} from: {rel}\n\n"
                                 f"> Cut from the public docs repo during the "
                                 f"TryHackMe-structure migration.\n"
                                 f"> Source material for the private website repo.\n\n")
                        fh.write("\n\n".join(blocks) + "\n")
                    arch_files.append(os.path.relpath(ap, root))

    mode = "APPLIED" if apply else "DRY RUN — nothing written"
    print(f"=== Crook2Root structure migration — {mode} ===\n")
    print(f"Notes changed          {len(touched)}")
    print(f"  level/* -> difficulty/*   {total['tags']}")
    print(f"  lab sections cut          {total['labs_cut']}")
    print(f"  checkpoints -> Summary    {total['summaries']}")
    print(f"  headings de-vocabularised {total['headings']}")
    print(f"  H2s numbered as Task N    {total['tasks']}")
    if apply:
        print(f"  archive files written     {len(arch_files)}  (in {ARCHIVE}/)")
    print()
    for rel, s in touched[:12]:
        bits = ", ".join(f"{k}={v}" for k, v in sorted(s.items()))
        print(f"  {rel}\n      {bits}")
    if len(touched) > 12:
        print(f"  ... and {len(touched) - 12} more")
    if not apply:
        print("\nRe-run with --apply to write. Recover any time with: git checkout -- .")
    return 0


if __name__ == "__main__":
    sys.exit(main())
