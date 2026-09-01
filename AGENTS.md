# Crook2Root Repository Instructions

These instructions apply to the entire repository. Read and follow the full human-facing standard in `docs/Crook2Root Authoring Standard.md` before changing documentation.

## Non-Negotiable Operating Rules

- Do not stage, commit, or push Git changes. Version control belongs to the repository owner.
- Work only with Markdown and repository image assets unless the user explicitly expands the scope.
- Write in professional English.
- Preserve existing user changes and unrelated work.
- Use `apply_patch` for manual file edits.
- Never edit anything under `.archive/` — it is retired material kept for the website repo.

## This Is a Documentation Repository

Crook2Root is **two repositories**. This one is the **public documentation repo**: pure learning material, from zero to mastery. A separate **private website repo** will consume this one as its source of content and images, and will add the interactive layer.

**Never add to this repository:**

- ❌ Labs, exercises, or "set this up and try it" instructions
- ❌ Questions, quizzes, answer boxes, self-tests or checkpoints
- ❌ Flags, scoring, points, or progress tracking
- ❌ Cleanup or teardown steps (the reader was never asked to build anything)

**Always prefer instead:**

- ✅ **Worked examples** — the real command, its real output, and what the fields mean
- ✅ Complete technical explanation with the mechanism behind every behaviour
- ✅ Mermaid diagrams, which the website repo renders directly

If a request would add assessment or hands-on tasking to this repo, say so and put the teaching version here instead.

## Zero-to-Mastery Is the Default

Every technical leaf is a complete lesson, not a summary or cheat sheet. It must:

1. **Open at zero** in the first section — plain-language mental model, prerequisites, and vocabulary suitable for a complete beginner, with an analogy and a statement of where the analogy breaks.
2. **Build through sections** — architecture, data flow, real commands with real output, field-by-field interpretation, and troubleshooting.
3. **Finish at mastery** — internals, edge cases, failure modes, security consequences, and design tradeoffs.
4. Include at least one meaningful visual, written as **Mermaid** — architecture, sequence, state, decision flows. **The vault contains no image files and none may be added.** When the subject is inherently spatial (a byte/frame/header field map, a memory or address-space map, a register/flag layout, a disk or RF-channel arrangement), Mermaid cannot express it: use a field table, a fenced ASCII layout, or an annotated hex dump instead. Never a screenshot.
5. Include at least one **worked example**: a real command and its real output, with a sentence interpreting the result and at least one failure or misleading result explained somewhere in the note. A command with no output shown is unfinished.
6. Replace generic filler with topic-specific mechanisms. Define not only what happens, but why the underlying parser, protocol, kernel, runtime, or control behaves that way.

## Section Structure

Content sections are plain `##` headings with descriptive titles — no numbering, no
`Task` prefix:

```markdown
## The Envelope for the Local Hop
## The EtherType: The Demultiplexing Key
## The FCS: Detection, Not Correction
```

- **Never write `## Task 1 — …`.** Numbered tasks are a course-runner construct and
  belong in the private website repo, which consumes these notes as its source. The
  public repo is documentation: the heading must say what the section teaches.
- The title carries the meaning. Order is expressed by the sequence of headings, not
  by a number the reader has to hold in their head.
- Cross-reference a section by naming it in **bold** — "as **The FCS** explains" —
  never "as Task 4 explains". A number reference breaks the moment a section moves.
- Index and hub notes carry navigation only, not lesson sections.
- One idea per section. Past roughly 700 words, split it.

Every leaf ends with:

```markdown
## Summary

You should now be able to:

- <capability the reader has gained>
- <capability the reader has gained>
```

## Required First-Degree Learning Order

Every leaf must contain this section near the beginning:

```markdown
## Parent Learning Order
First Leaf -> Second Leaf -> Third Leaf
```

The line lists only the leaf's parent's direct children in exact curriculum order. Do not include the parent, descriptions, nested descendants, bullets, or wikilinks. The line is plain text so sibling nodes do not acquire lateral graph edges.

## Strict Tree Topology

- Root notes link only to domain indexes.
- Domain indexes link only to their direct branches or leaves and their parent.
- Branch indexes link only to direct children and their parent.
- A leaf has exactly one parent in `Domain:` and may link only to that parent.
- Do not create lateral `[[wikilinks]]` between leaves. Mention related topics in **bold text**.
- A parent's numbered curriculum and every child's `Parent Learning Order` line must agree.

## Metadata & Naming

- Preserve YAML frontmatter, aliases, tags, `Domain`, and `Color`.
- Use one `Domain` parent per node.
- Every leaf carries exactly one difficulty tag: `difficulty/easy`, `difficulty/medium` or `difficulty/hard`. Index and hub notes use `difficulty/info`.
- Use clean professional filenames without numeric prefixes, underscores, synthetic module codes, or `Branch`/`Hub` prefixes.
- Use `&` rather than the word "and" in visible titles when joining peer concepts.
- Do not add image embeds. There is no `assets/` directory and no image file belongs in this repository.

## Completion Audit

Before reporting completion, verify:

- Frontmatter is valid and the parent exists.
- Learning order is present, plain text, first-degree only, and matches the parent curriculum.
- Sections are plain descriptive `##` headings — no `Task N` numbering anywhere.
- The note opens on an artifact, not a definition (**The Cold Open**), and states one naive model it then breaks (**The Break**).
- Every error output is followed by the mechanism that produced it (**The Autopsy**) — which component, which stage, what check.
- Never minimise the reader's task: no "you simply run", "just install", "all you have to do is". Claims about *attacker* cost ("trivially forged") are fine and often necessary.
- Full rules: `docs/Crook2Root Teaching Standard.md`. Both gates must pass: `ci-check.py` and `pedagogy-check.py`.
- Code fences and Mermaid blocks are balanced.
- Commands have realistic expected output **and** an interpretation.
- At least one worked example is present.
- **No labs, exercises, questions, quizzes, checkpoints, flags or cleanup steps exist anywhere in the note.**
- A `## Summary` section is present and states reader capabilities.
- If the subject is a byte/packet/memory/register/disk layout, an authored, visually-inspected image is present.
- No lateral leaf links, broken wikilinks, broken anchors, or missing embeds exist.
- Domain tags still match `.obsidian/graph.json` colour groups.
- Nothing is staged, committed, or pushed.

## Helper Scripts

Run from the vault root. All are read-only unless `--apply` is passed.

| Script | Purpose |
|:--|:--|
| `docs/scripts/content-audit.py` | Per-domain health: word counts, worked examples, visuals, summaries, difficulty tags |
| `docs/scripts/fence-check.py` | Finds `## ` lines inside code fences and unbalanced fences |
| `docs/scripts/post-migration-check.sh` | Full structural verification sweep |
| `docs/scripts/migrate-structure.py` | Retired one-shot migration; kept for reference |
| `docs/scripts/migrate-prose.py` | Retired one-shot migration; kept for reference |
