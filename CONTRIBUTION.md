# Contributing to Crook2Root

Thank you for helping build Crook2Root into a rigorous, open cybersecurity curriculum. Contributions are welcome from learners, security engineers, researchers, educators, red teamers, blue teamers, platform specialists, and technical writers.

Before contributing, read the [Crook2Root Authoring Standard](docs/Crook2Root%20Authoring%20Standard.md). It defines the required zero-to-mastery structure, the strict multiple-trees topology, visuals, evidence, naming, and completion criteria.

## First: This Is the Documentation Repository

Crook2Root is **two repositories**. This one is the **public documentation repo** — pure learning material. A separate **private website repo** consumes this one as its source of content and images, and adds the interactive platform on top.

That split decides what belongs in a pull request here.

| Belongs here | Belongs in the website repo |
|:--|:--|
| Explanation, from zero to mastery | Practice questions and quizzes |
| Worked examples — real commands, real output | Hands-on labs and target environments |
| Mermaid diagrams, tables, ASCII layouts | CTF challenges and flags |
| Failure modes and troubleshooting | Progress tracking and scoring |

**Please do not submit** labs, exercises, questions, quizzes, checkpoints, self-tests, flags, or cleanup instructions. A pull request adding any of these will be asked to convert them into worked examples instead.

## Ways to Contribute

- Correct a technical error or outdated platform detail.
- Improve a beginner explanation without weakening expert depth.
- Add realistic output, troubleshooting, or a clearer worked example.
- Improve Mermaid architecture, sequence, state, or decision diagrams.
- Add a Mermaid diagram, field table or annotated hex dump where a note has only prose.
- Split a clumped subject into atomic leaves under the correct parent.
- Expand an intentionally scaffolded domain.
- Fix broken links, aliases, anchors, embeds, metadata, or curriculum order.
- Improve accessibility, clarity, consistency, and English prose.

## Repository Architecture

Crook2Root uses a strict hierarchy:

```text
Cyber Security
-> Domain Index
-> Branch or Sub-Index
-> Technical Leaf
```

Every node has one parent. Indexes provide vertical navigation. Technical leaves do not link laterally to other leaves, because those edges turn the Obsidian Graph into an unreadable mesh.

Before adding a note, identify:

1. Its single parent.
2. Its domain folder and `tree/*` tag.
3. Its position among the parent's direct children.
4. Whether it is truly atomic or duplicates an existing leaf.

## The Zero-to-Mastery Requirement

Every technical leaf carries a complete lesson inside one note. The ramp is the **order of the sections**, not labelled difficulty sections:

- **The first section opens at zero** — plain-language mental model, prerequisites, vocabulary, an analogy and where the analogy breaks.
- **Middle sections build working understanding** — architecture, real commands with real output, field-by-field interpretation, troubleshooting.
- **Later sections reach mastery** — internals, edge cases, failure modes, security consequences, design tradeoffs.

Do not submit generic summaries, command dumps without interpretation, copied tool manuals, placeholder prose, or notes that assume expert prerequisites from the first paragraph.

## Section Structure

Content sections are plain `##` headings with descriptive titles:

```markdown
## The Envelope for the Local Hop
## The EtherType: The Demultiplexing Key
## The FCS: Detection, Not Correction
```

- **No numbering, and no `Task` prefix.** `## Task 1 — …` is a course-runner
  construct: it belongs in the private website repo, which uses these notes as its
  source. Here the heading's job is to say what the section teaches.
- Order is carried by the sequence of headings, not by a number.
- To point at another section, name it in **bold** — "as **The FCS** explains" —
  never "as Task 4 explains", which breaks as soon as a section moves.
- Index and hub notes carry navigation only, not lesson sections.
- One idea per section. Past roughly 700 words, split it.

## Required Learning Order

Every leaf repeats its parent's first-degree curriculum near the beginning:

```markdown
## Parent Learning Order
First Leaf -> Second Leaf -> Third Leaf
```

Only direct sibling titles separated by `->`. No wikilinks, bullets, numbering, descriptions, the parent title, or descendants. If you reorder a parent curriculum, update the order line in every direct child.

## Technical Leaf Template

The full copy-paste template lives at [`docs/templates/Room Template.md`](docs/templates/Room%20Template.md). Its shape:

```markdown
---
title: "Professional Topic Title"
aliases: ["Useful Historical Name"]
tags:
  - tree/domain
  - cyber/domain/topic
  - type/concept
  - difficulty/medium
Domain:
  - "[[Single Parent]]"
Color: "#DOMAIN_COLOR"
---

# Topic Title

> [!abstract] Note of [[Single Parent]]
> State what the reader will understand by the end.

## Parent Learning Order
First Leaf -> This Leaf -> Final Leaf

## Opening idea, stated plainly
## Architecture or mechanism
## Worked example
## Internals, edge cases & failure modes
## Security implications

## Summary

You should now be able to:

- Capability the reader has gained

---
> 🔼 Up: [[Single Parent]]
```

Section titles adapt to the subject, but every function above must remain.

## Worked Examples, Not Labs

This is the distinction reviewers check most closely.

- **A lab says:** "Build this environment, run these commands, verify your result, then clean up."
- **A worked example says:** "Here is the command, here is exactly what it prints, and here is what each field means."

Every worked example shows the exact command, its realistic output in its own fenced block, and a sentence explaining which fields matter. Somewhere in the note, at least one failure or misleading result is shown and its mechanism explained.

Never instruct the reader to build infrastructure, never ask a question, never include cleanup steps, and never write "try this yourself".

Use synthetic hosts, identities, domains, addresses and records — `192.0.2.0/24`, `example.com`. Do not include secrets or proprietary customer data.

## Visuals & Assets

- Prefer Mermaid for flows, states, sequences, architecture, and trust boundaries.
- When the subject is **spatial** — a byte or bit layout, a packet/frame/header field map, a memory or address-space map, a register layout, a disk structure, an RF channel arrangement — Mermaid cannot draw it. Use a field table, a fenced ASCII layout, or an annotated hex dump. Do not force a flowchart to stand in for a layout.
- **Do not add image files of any kind** — no SVG, PNG or GIF, and never a screenshot. Screenshots of code are not searchable or accessible; screenshots of another platform's rooms import their content and branding into a public repo.
- Explain how to read every visual.
- Do not add decorative diagrams that merely duplicate nearby prose.
- Keep Mermaid source readable and commented where the diagram is non-obvious — the website repo renders it directly.

## Naming & Style

- Write in professional English.
- Clean filenames: no numeric prefixes, no underscores, no synthetic module codes.
- Do not prefix notes with `Hub` or `Branch`.
- Use `&` instead of "and" in visible titles joining peer concepts.
- Define acronyms on first use.
- Prefer precise explanations over jargon or marketing language.
- Keep a topic atomic; split genuinely independent subjects.
- Mention related leaves in **bold**, not `[[wikilinks]]`.

## Metadata & Graph Rules

- Preserve or add exactly one `Domain:` parent.
- Use the domain's existing `Color:` value.
- Include the domain's `tree/*` tag so Graph View colouring works.
- Include exactly one difficulty tag: `difficulty/easy`, `difficulty/medium`, `difficulty/hard`, or `difficulty/info` for index and hub notes.
- Add aliases when renaming or replacing a historical note.
- Parent indexes may link to direct children; leaves may link only to their parent.
- Do not create shortcuts between domain hubs or sibling leaves.

## Contribution Workflow

1. Search existing notes and open issues before starting.
2. Choose one focused change or coherent cluster.
3. Fork the repository and create a clearly named working branch.
4. Make the smallest architectural change that fully solves the problem.
5. Run the validation checklist below.
6. Open a pull request explaining the parent, learning position, technical scope, and validation results.
7. Respond to review with evidence, and update every affected sibling order if curriculum placement changes.

Helper scripts, run from the vault root:

```bash
python3 docs/scripts/content-audit.py      # per-domain health
python3 docs/scripts/fence-check.py        # fence and heading sanity
bash    docs/scripts/post-migration-check.sh
```

## Validation Checklist

- [ ] The note starts at true beginner level and reaches expert depth.
- [ ] Sections are plain descriptive `##` headings — no `Task N` numbering.

### Teaching Standard — read for these, the gate cannot see them

The full rationale is in [`docs/Crook2Root Teaching Standard.md`](docs/Crook2Root%20Teaching%20Standard.md).

- [ ] **The Cold Open** — the note opens on an artifact (a capture, a dump, a failing command), not a definition.
- [ ] **The Break** — somewhere the note states the model a reasonable person would assume, then violates it. Stated confidently, in the reader's voice.
- [ ] **The Autopsy** — every error output is followed by a paragraph naming which component rejected it, at which stage, and what it was checking.
- [ ] **The Twin** — a reusable pattern carries two surface-different instances *and* an explicit instruction to compare them.
- [ ] **The Name** — the deep structure has a label, and it is the same label used elsewhere in the corpus.
- [ ] **The Tell** — the note says how you would notice this in the wild, not only how to exploit it.
- [ ] **One Pre-Question** — exactly one, on the load-bearing idea, answered.
- [ ] **The Fade** — scaffolding sits in skippable containers; no explanation is repeated "for safety".
- [ ] **The Honest Note** — where the topic is hard, it says so and locates the difficulty.
- [ ] `Parent Learning Order` matches the parent's direct children exactly.
- [ ] The note has one parent and no lateral leaf wikilinks.
- [ ] Domain tag and colour match the parent tree; exactly one difficulty tag is present.
- [ ] Commands and code have realistic output **and** interpretation.
- [ ] At least one meaningful visual is present, with prose explaining how to read it.
- [ ] At least one worked example is present, including one explained failure.
- [ ] **No labs, exercises, questions, quizzes, checkpoints, flags or cleanup steps appear anywhere.**
- [ ] A `## Summary` section states what the reader can now do.
- [ ] Frontmatter and Markdown fences are valid.
- [ ] Wikilinks, aliases, anchors, and image embeds resolve.
- [ ] No placeholders, secrets, customer data, or unrelated generated text remain.

## Ethical & Responsible Contributions

Crook2Root documents security mechanisms and authorized testing so systems can be understood, evaluated, and improved. Contributions must not claim authorization where none exists, target real third parties, expose private data, or present destructive behaviour without a legitimate educational and defensive context.

If a contribution describes offensive behaviour, include scope, prerequisites, operational impact, and appropriate safeguards. Clearly distinguish demonstrated behaviour from hypothetical escalation.

## Pull Request Description

A strong pull request answers:

- What did you change?
- Which parent owns the note?
- Where does it belong in the learning order?
- What new beginner and expert value does it add?
- How were commands, output, diagrams, and links verified?
- Did any filenames, aliases, parent links, or sibling order lines change?

Focused, technically justified contributions are easier to review and more valuable than large unstructured rewrites.
