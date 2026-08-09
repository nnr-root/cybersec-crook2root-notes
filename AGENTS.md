# Crook2Root Repository Instructions

These instructions apply to the entire repository. Read and follow the full human-facing standard in `docs/Crook2Root Authoring Standard.md` before changing documentation.

## Non-Negotiable Operating Rules

- Do not stage, commit, or push Git changes. Version control belongs to the repository owner.
- Work only with Markdown and repository image assets unless the user explicitly expands the scope.
- Write in professional English.
- Preserve existing user changes and unrelated work.
- Use `apply_patch` for manual file edits.

## Crook2Root Is the Default

Every technical leaf is a zero-to-mastery lesson, not a summary or cheat sheet. It must:

1. Begin at **Crook** level with a plain-language mental model, prerequisites, and vocabulary suitable for a complete beginner.
2. Progress to **Operator** level with architecture, commands, code, realistic output, troubleshooting, and evidence interpretation.
3. Finish at **Root** level with internals, edge cases, failure modes, security consequences, debugging, and design tradeoffs.
4. Include at least one meaningful visual—prefer Mermaid for architecture, sequence, state, or decision flows. When the subject is inherently spatial (a byte/frame/header field map, a hex-dump-to-field mapping, a memory or address-space map, a register/flag layout, a disk or RF-channel arrangement), Mermaid is **insufficient**: author a self-contained SVG (dark bg `#0f1420`), store it in `assets/` with a domain prefix, embed with `![[name.svg]]`, and **render and visually inspect it before committing**.
5. Include a **runnable, step-by-step authorized lab** in which every step shows a real command **and its real output**, contains at least one deliberate failure, and ends with verified cleanup where state changes—then a **Crook → Operator → Root** checkpoint. A bulleted list of things the reader "could try", or commands with no output shown, is **not a lab** and is grounds for rejecting the note. Prefer labs that run on one machine the reader already has (build extra hosts with namespaces/containers/loopback rather than assuming spare VMs or hardware). See `docs/Crook2Root Authoring Standard.md` §6.
6. Replace generic filler with topic-specific mechanisms. Define not only what happens, but why the underlying parser, protocol, kernel, runtime, or control behaves that way.

## Required First-Degree Learning Order

Every leaf must contain this section near the beginning:

```markdown
## Parent Learning Order
First Leaf -> Second Leaf -> Third Leaf
```

The line lists only the leaf's parent’s direct children in the exact curriculum order. Do not include the parent, descriptions, nested descendants, bullets, or wikilinks. The line is plain text so sibling nodes do not acquire lateral graph edges.

## Strict Tree Topology

- Root notes link only to domain indexes.
- Domain indexes link only to their direct branches or leaves and their parent.
- Branch indexes link only to direct children and their parent.
- A leaf has exactly one parent in `Domain:` and may link only to that parent.
- Do not create lateral `[[wikilinks]]` between leaves. Mention related topics in **bold text**.
- A parent’s numbered curriculum and every child’s `Parent Learning Order` line must agree.

## Metadata & Naming

- Preserve YAML frontmatter, aliases, tags, `Domain`, and `Color`.
- Use one `Domain` parent per node.
- Use clean professional filenames without numeric prefixes, underscores, synthetic module codes, or `Branch`/`Hub` prefixes.
- Use `&` rather than the word “and” in visible titles when joining peer concepts.
- Preserve `![[asset.ext]]` embeds and keep assets in `assets/`.

## Completion Audit

Before reporting completion, verify:

- Frontmatter is valid and the parent exists.
- Learning order is present, plain text, first-degree only, and matches the parent curriculum.
- Code fences and Mermaid blocks are balanced.
- Commands have realistic expected output.
- The lab is a runnable step-by-step sequence: every step shows a real command **and its output**, it contains a deliberate failure, it runs on one machine the reader plausibly has, and it ends with verified cleanup. A "could try" bullet list fails the audit.
- If the subject is a byte/packet/memory/register/disk layout, an authored, visually-inspected image (not just Mermaid) is present.
- No lateral leaf links, broken wikilinks, broken anchors, or missing embeds exist.
- Domain tags still match `.obsidian/graph.json` color groups.
- Nothing is staged, committed, or pushed.

