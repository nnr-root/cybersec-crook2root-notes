#!/usr/bin/env python3
"""
Crook2Root standard gate — the CI guard.

Two tiers:

  ERRORS  (exit 1, blocks the commit / fails CI) — things that must NEVER be true
          regardless of how finished a note is:
            * banned constructs (the retired Crook/Operator/Root structure, labs,
              checkpoints, level tags, reader-tasking, question boxes)
            * an image embed pointing at a file that is not in the repo
            * unbalanced code fences
            * numbered task headings (`## Task N — …`) — the public repo uses plain
              descriptive section headings; numbering belongs in the private site repo
            * a dangling `Task N` cross-reference in prose (name the section in bold)
            * invalid YAML frontmatter, or a leaf missing Domain/Color

  WARNINGS (reported, do NOT block) — the incompleteness backlog:
            * missing ## Summary, missing difficulty tag, missing worked example,
              thin note (<800 words)
            * an embedded asset with no `visual-verified:` date in the frontmatter
              — generated imagery is audited for technical accuracy before it is
              trusted, and this is the record of that audit having happened

Run from the vault root:
    python3 docs/scripts/ci-check.py            # full check, exit 1 on any error
    python3 docs/scripts/ci-check.py --warnings # also print the backlog
    python3 docs/scripts/ci-check.py --quiet    # errors only, minimal output

Used by .githooks/pre-commit and .github/workflows/standard.yml.
"""
import os
import re
import sys

SKIP_DIRS = {".git", ".obsidian", "graphify-out", ".claude", ".archive", "_to_delete"}
GOV_FILES = {"AGENTS.md", "README.md", "CONTRIBUTION.md"}   # governance, not lessons
IMAGE_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".tiff")
THIN = 800

FM = re.compile(r"^---\n(.*?)\n---", re.S)
NUMBERED = re.compile(r"^#{2,6}\s+Task\s+\d+\s*[—–-]\s*", re.M)
TASK_REF = re.compile(r"\bTask \d+\b")
SUMMARY = re.compile(r"^## Summary\s*$", re.M)
EXAMPLE = re.compile(r"^```(shell-session|console|bash|shell|powershell|text|sql|http)", re.M)
MAPPING = re.compile(r"^#{2,4} [^\n]*Worked Mapping[^\n]*\n(?:.*\n)*?\|.*\|", re.M)
EMBED = re.compile(r"!\[\[([^\]]+)\]\]")

BANNED = [
    ("lab section", re.compile(r"^#{2,4}\s+.*\b(Authorized Lab|Hands-On Lab|Runnable Lab)\b", re.M | re.I)),
    ("checkpoint heading", re.compile(r"^#{2,4}\s+.*\bCheckpoint\b", re.M | re.I)),
    ("level/* tag", re.compile(r"level/(crook|operator|root)\b")),
    ("Crook/Operator/Root heading", re.compile(r"^#{2,4}\s+(Crook|Operator|Root)\s*[—–-]", re.M)),
    ("reader tasking", re.compile(
        r"\b(try (this|it) yourself|your turn|verify that you get|now clean ?up|set up two (hosts|VMs))\b", re.I)),
    ("question/answer box", re.compile(r"c2r-check|\[!question\]", re.I)),
]


def fence_mask(lines):
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
    return mask, infence  # infence True at EOF => unbalanced


def is_index(rel, text):
    stem = os.path.splitext(os.path.basename(rel))[0]
    parent = os.path.basename(os.path.dirname(rel))
    top = rel.split(os.sep)[0]
    return stem == parent or stem == top or "cyber/moc" in text


def note_files(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if not f.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), root)
            if rel.startswith("docs" + os.sep) or f in GOV_FILES:
                continue
            if os.sep not in rel and rel != "Cyber Security.md":
                continue
            yield rel


def check(root="."):
    errors, warnings = [], []

    # ── repo-level: media is permitted anywhere ──────────────────────────────
    # Generated imagery is produced externally and audited on arrival. The gate
    # therefore does not police WHERE assets live; it polices whether an embed
    # resolves, and whether the audit was recorded. A drawing that is wrong is
    # caught by a person reading it, which is the only thing that can catch it.
    assets = set()
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if f.lower().endswith(IMAGE_EXT):
                assets.add(os.path.basename(f))

    for rel in note_files(root):
        text = open(os.path.join(root, rel), encoding="utf-8", errors="replace").read()
        lines = text.split("\n")
        mask, unbalanced = fence_mask(lines)

        # ── ERRORS ────────────────────────────────────────────────────────────
        for name, pat in BANNED:
            if pat.search(text):
                errors.append(f"{rel}: banned construct — {name}")

        embeds = [m.group(1).split("|")[0].strip()
                  for i, m in enumerate(EMBED.finditer(text))
                  if not mask[text[:m.start()].count("\n")]]
        for target in embeds:
            if not target.lower().endswith(IMAGE_EXT):
                continue                       # a note-to-note transclusion, not media
            if os.path.basename(target) not in assets:
                errors.append(f"{rel}: embed points at a missing asset — {target}")

        if embeds and "visual-verified:" not in text:
            warnings.append(f"{rel}: {len(embeds)} embedded asset(s), no "
                            f"`visual-verified:` date — generated imagery is not "
                            f"trusted until someone has checked it")

        if unbalanced:
            errors.append(f"{rel}: unbalanced code fence")

        numbered = sum(1 for i, l in enumerate(lines) if not mask[i] and NUMBERED.match(l))
        if numbered:
            errors.append(f"{rel}: {numbered} numbered task heading(s) — the public repo "
                          f"uses plain descriptive headings; `## Task N —` numbering "
                          f"belongs in the private site repo")

        for i, l in enumerate(lines):
            if mask[i] or NUMBERED.match(l):
                continue
            if TASK_REF.search(l):
                errors.append(f"{rel}: dangling 'Task N' cross-reference (line {i + 1}) — "
                              f"name the section in **bold** instead")
                break

        m = FM.match(text)
        if not m:
            errors.append(f"{rel}: no YAML frontmatter")
            continue
        block = m.group(1)
        try:
            import yaml
            meta = yaml.safe_load(block)
            if not isinstance(meta, dict):
                raise ValueError("frontmatter is not a mapping")
        except ImportError:
            meta = None  # yaml unavailable locally — skip deep frontmatter checks
        except Exception as e:
            errors.append(f"{rel}: invalid YAML frontmatter — {str(e)[:60]}")
            continue

        idx = is_index(rel, text)
        diff = re.findall(r"difficulty/(info|easy|medium|hard)", block)
        if len(diff) > 1:
            errors.append(f"{rel}: multiple difficulty tags — {diff}")

        if meta is not None and not idx:
            if "Domain" not in meta:
                errors.append(f"{rel}: leaf missing Domain (parent) in frontmatter")
            if "Color" not in meta:
                errors.append(f"{rel}: leaf missing Color in frontmatter")

        # ── WARNINGS (backlog) ────────────────────────────────────────────────
        if idx:
            continue
        body_words = len(FM.sub("", text).split())
        if not SUMMARY.search(text):
            warnings.append(f"{rel}: no ## Summary")
        if not diff:
            warnings.append(f"{rel}: no difficulty tag")
        if not (EXAMPLE.search(text) or MAPPING.search(text)):
            warnings.append(f"{rel}: no worked example")
        if body_words < THIN:
            warnings.append(f"{rel}: thin ({body_words}w < {THIN})")

    return errors, warnings


def main():
    args = sys.argv[1:]
    quiet = "--quiet" in args
    show_warn = "--warnings" in args
    errors, warnings = check()

    if errors:
        print(f"✗ {len(errors)} ERROR(S) — standard gate failed:\n")
        for e in errors:
            print(f"  ERROR  {e}")
    elif not quiet:
        print("✓ standard gate passed — 0 errors")

    if warnings and (show_warn or not errors):
        if show_warn:
            print(f"\n{len(warnings)} backlog item(s) (do not block):")
            for w in warnings:
                print(f"  todo   {w}")
        elif not quiet:
            print(f"  ({len(warnings)} backlog warnings — run with --warnings to list)")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
