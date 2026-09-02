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

> were written when the standard still used `## Task N — ` headings, and they
> emit that form. Re-running one would reintroduce numbering the standard now
> forbids and the gate now rejects. Read them for their patterns; if you need to
> mine again, port the pattern to plain descriptive headings first.

| Script | What it did |
|:--|:--|

---

## Removed 2026-09-02

Twenty-nine one-shot scripts were deleted after the migrations they performed
were complete and committed: the `mine-batch*` worked-example miners, the
`migrate-*` structure and prose passes, the `add-*` section fillers, the
`strip-*` purges (images, task numbering), `patch-visual-standard.py`,
`tag-difficulty.py`, and the `heading-labels.py` / `relabel-headings.py` pair
that authored the 273 subgoal headings.

Each ran once, its output is in the notes, and its source is in git history.
Keeping them implied they were part of the toolchain, which they were not.

What remains is the toolchain proper: two gates that block a commit, two
auditors, and two verification sweeps.

