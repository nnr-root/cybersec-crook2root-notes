# Crook2Root tooling

Read-only scripts (nothing writes without `--apply`) that measure and enforce the
[Crook2Root Authoring Standard](../Crook2Root%20Authoring%20Standard.md). Run every
command from the vault root.

## The standard gate — `ci-check.py`

The single source of truth for "is this note allowed". Two tiers:

- **Errors (exit 1, blocks a commit / fails CI)** — things that must never be true
  regardless of how finished a note is: a banned Crook/Operator/Root construct
  (labs, checkpoints, `level/*` tags, three-level headings, reader-tasking,
  question boxes), an image file committed outside `_to_delete/`, an image embed
  `![[...]]`, an unbalanced code fence, a `## Task N —` heading or dangling `Task N`
  cross-reference, invalid frontmatter,
  or a leaf missing its `Domain`/`Color`.
- **Warnings (reported, never block)** — the incompleteness backlog: missing
  `## Summary`, missing difficulty tag, missing worked example, thin note (<800w).

```bash
python3 docs/scripts/ci-check.py             # gate; exit 1 on any error
python3 docs/scripts/ci-check.py --warnings  # also list the backlog
```

### Activate it locally (pre-commit hook)

```bash
git config core.hooksPath .githooks
```

After this, a commit that introduces a violation is blocked. `git commit --no-verify`
overrides it if you are certain. The same check runs in CI via
`.github/workflows/standard.yml` on every push and pull request.

## Health & diagnostics

| Script | What it does |
|:--|:--|
| `content-audit.py` | Per-domain health table. Flags: `--thin --noexample --nosummary --violations --json`. Recognises a "Worked Mapping" table as an example. |
| `fence-check.py` | Finds `##` lines inside code fences and unbalanced fences. |
| `pedagogy-check.py` | The Teaching Standard gate. Errors on hedges that minimise the reader's task and on generic heading labels; warns on a buried cold open, an unexplained error output, a note that asks no question, an unbounded analogy, and a missing or stale `verified:` date. `--warnings --json --fix-hedges`. |
| `verify-standard.sh` | Full structural sweep (governance docs, templates, fences, git state). |

## One-shot content operations (kept for reference)

These were run once during the 2026 restructure and the Offensive Security
worked-example build. They are retained so the changes are reproducible and the
patterns are reusable, not because they need re-running.

> ⚠️ **Do not re-run the mining and example scripts.** `mine-offsec.py`,
> `mine-batch2.py` … `mine-batch17.py`, `add-examples.py` and `strip-images.py`
> were written when the standard still used `## Task N — ` headings, and they
> emit that form. Re-running one would reintroduce numbering the standard now
> forbids and the gate now rejects. Read them for their patterns; if you need to
> mine again, port the pattern to plain descriptive headings first.

| Script | What it did |
|:--|:--|
| `migrate-structure.py` | Removed the Crook/Operator/Root structure; converted to flat sections. |
| `migrate-prose.py` | Removed the three-level vocabulary from body prose. |
| `strip-images.py` | Removed all image embeds; rescued code screenshots into fenced blocks. |
| `patch-visual-standard.py` | Rewrote the governance docs to the Mermaid-only visual standard. |
| `strip-task-numbers.py` | Removed the `## Task N — ` prefix from 1,624 headings across 303 notes, keeping the descriptive titles. Fence-aware; `--apply` to write. |
| `relabel-headings.py` + `heading-labels.py` | Replaced the four worn-out generic section titles (273 headings across 145 notes) with a subgoal label written from each section's own content. The label table is kept as the record of what changed. |
| `tag-difficulty.py`, `add-summaries.py`, `add-examples.py` | Filled difficulty tags, summaries, and Networking worked examples. |
| `mine-offsec.py`, `mine-batch2.py` … `mine-batch17.py` | Built the Offensive Security worked examples from `.archive/labs/`. |
