# Crook2Root Authoring Standard

Crook2Root is a cybersecurity knowledge system designed to take a reader from complete beginner to independent expert. The name is the editorial promise: a reader who starts at zero and works through a track ends up owning the machine.

This document is the permanent content philosophy for every domain. Contributors and automated editors apply it without the project owner restating it in each request.

---

## 0. Two Repositories — Know Which One You Are In

Crook2Root ships as **two separate repositories with different jobs**. Confusing them is the most damaging mistake an author or agent can make.

| | **This repo — `cybersec-crook2root-notes`** | **The website repo — private, later** |
|:--|:--|:--|
| Visibility | **Public** | Private |
| Purpose | Pure learning documentation | The interactive platform |
| Contains | Explanation, diagrams, worked examples, images | Labs, practice questions, quizzes, CTFs, flags, progress |
| Reads from | — | **This repo, as its source of content and images** |
| A reader here | Reads and learns | Does and is assessed |

**Therefore, in this repository:**

- ❌ **No labs.** No "set up two hosts and try this", no exercises for the reader to perform.
- ❌ **No questions, quizzes or answer boxes.** Nothing to submit, nothing to check.
- ❌ **No flags, no scoring, no progress tracking.**
- ❌ **No cleanup instructions**, because the reader was never asked to build anything.
- ✅ **Worked examples** — real commands with their real output, presented as demonstration.
- ✅ **Complete technical explanation** from zero to mastery.
- ✅ **Diagrams and images**, which the website repo will reuse directly.

The website repo will turn this documentation into rooms with numbered tasks, questions and labs. Its job is assessment, and the task numbering is part of it. **This repo's job is teaching**, so it carries plain descriptive section headings and no `Task N` anywhere. Keep the boundary clean and both repos stay simple.

---

## 1. The Learning Contract

Every technical leaf takes a reader from *never heard of this* to *can reason about it independently* — inside a single note.

The ramp is carried by **the order of the sections**, not by labelled difficulty sections. The opening section assumes nothing. Each section builds only on the sections above it and on the rooms named in `Parent Learning Order`. By the final section the reader is looking at internals, edge cases and failure modes.

**Open at zero.**

- State what the thing is and why it exists before using any jargon.
- Define every essential term on first use.
- Give one concrete analogy — then say where the analogy stops being accurate. That boundary is where real understanding starts.
- Identify the object, protocol, process or trust boundary being studied.
- No unexplained acronyms, no cargo-cult commands, no premature edge cases.

**Build to working understanding.**

- Explain architecture, data flow, state transitions, inputs, outputs and dependencies.
- Show real commands, configuration, code, requests, responses, logs or debugger output — **with their real output**.
- Explain every important flag or field in the example.
- Show at least one failure or misleading result and how to tell it apart from success.
- Teach evidence: what proves the conclusion, and what could produce a false one.

**Finish at mastery.**

- Trace the mechanism through parsers, protocols, runtimes, kernel structures, cryptographic assumptions or control planes.
- Cover edge cases, version and platform differences, race conditions, resource limits and recovery.
- Explain how controls fail, how to debug the failure, and how design choices change risk.
- Distinguish demonstrated fact, inference and hypothesis.
- Connect offence, defence and engineering under authorized use.

A leaf succeeds when a beginner can enter without an unstated prerequisite, and someone finishing it can predict behaviour and explain it from first principles.

---

## 2. Required Leaf Anatomy

Section titles adapt to the subject, but every technical leaf needs these functions in this order:

1. YAML frontmatter — one parent, domain tag, type tag, **difficulty tag**, aliases, matching colour.
2. A clear H1 and a short abstract stating the learning outcome.
3. `## Parent Learning Order` followed by one plain-text order line.
4. An opening `## <descriptive title>` section starting at zero: mental model, prerequisites, vocabulary.
5. Further `## <descriptive title>` sections carrying the technical content, in teaching order.
6. At least one meaningful visual — Mermaid, or a table / ASCII layout / annotated hex dump where the subject is spatial (§4).
7. At least one **worked example** with real commands and real output (§5).
8. Failure modes and troubleshooting.
9. Security implications and authorized-use boundaries.
10. `## Summary` — what the reader should now be able to do.
11. A single parent link at the footer.

Recommended depth is approximately **1,500–5,000 words**. Complexity, not padding, determines the size. Shorter is acceptable only when the topic is genuinely narrow and still satisfies the full contract.

### Section headings

- Content sections are plain `##` headings with descriptive titles: `## The EtherType: The Demultiplexing Key`.
- **Never `## Task N — …`.** Numbered tasks are a course-runner construct and belong in the private website repo (§0). In this repo the heading's job is to say what the section teaches; the CI gate rejects a numbered heading as an error.
- Order is expressed by the sequence of headings, not by a number the reader has to carry.
- **Cross-reference by name, in bold** — "as **The FCS** explains", never "as Task 4 explains". A numeric reference silently rots the moment a section is inserted, moved or split; a named one does not. The gate rejects a bare `Task N` in prose.
- `## Parent Learning Order` and `## Summary` are structural, not lesson sections.
- Index and hub notes carry navigation, not lessons.
- A section is a coherent unit of one idea. If a section needs more than roughly 700 words, it is probably two sections.

---

## 3. Parent Learning Order Rule

Each parent owns an ordered curriculum of its direct children. Every direct child repeats that first-degree order near the beginning:

```markdown
## Parent Learning Order
Foundations -> Architecture -> Operation -> Troubleshooting -> Mastery
```

Rules:

- Use `->` exactly as the separator.
- List direct siblings only — no grandchildren, no deeper descendants.
- No descriptions, numbers, bullets or commentary on the order line.
- No wikilinks; lateral links would collapse the tree topology.
- Use each sibling's professional visible title.
- Update every sibling if the parent curriculum changes.

---

## 4. Visual Standard

**Every visual in this repository is Mermaid.** The vault carries no image files:
no SVG, no PNG, no GIF. A note that needs a picture writes it as Mermaid source
in a fenced block, and the renderer draws it.

This is a deliberate constraint, and it has three reasons behind it. Mermaid is
plain text, so it diffs in a pull request and a reviewer can see what changed.
It inherits the reader's theme instead of fighting it. And it cannot carry
another organisation's branding or licence into a public repository, which
image files repeatedly did.

A visual must teach a relationship that prose alone would make harder to
understand. Reach for:

- `sequenceDiagram` — protocol exchanges, syscalls, authentication, request
  lifecycles, attack chains.
- `flowchart` — architecture, decision paths, trust boundaries, transformations.
- `stateDiagram-v2` — process, protocol, scheduler or resource states.
- `classDiagram` — object ownership and structural relationships.
- `timeline` — boot, incident or forensic sequences.
- `erDiagram` — schema and entity relationships.

### When the subject is spatial

Byte and bit layouts, packet and header field maps, memory and address-space
maps, register and flag layouts, disk structures and RF channel arrangements are
**spatial**, and Mermaid cannot draw them. Do not force a flowchart to stand in
for a layout — it will mislead. Use one of these instead, in order of preference:

1. **A field table.** Columns for field, size and purpose carry the same
   information as a byte map and are searchable, translatable and screen-reader
   accessible.
2. **A fenced ASCII diagram.** For a frame or header, a plain box drawing inside
   a ```text fence shows offsets and widths precisely, and copies as text.
3. **An annotated hex dump.** Show the real bytes with a second block naming
   which offset is which field. This is usually the strongest option, because it
   is simultaneously the diagram and the evidence.

`Ethernet & Frame Structure` uses all three and is the reference for this
pattern.

Every visual needs nearby prose explaining how to read it and why it matters.
Decorative diagrams, repeated generic flows, and visuals that merely restate a
list do not satisfy this standard.

> Screenshots are never acceptable. A screenshot of code is not searchable, not
> copyable, not accessible and does not scale; write a fenced code block. A
> screenshot of a third party's training platform additionally imports their
> content and branding into a public repository.

## 5. The Worked Example Standard

Worked examples replace what used to be labs. The difference is framing, and it is not cosmetic.

**A lab says:** "Build this environment, run these commands, verify your result, then clean up."
**A worked example says:** "Here is the command, here is exactly what it prints, and here is what each field means."

The reader follows along by reading. They may run the commands if they wish, but the note never depends on it, never asks them to, and never assumes they did.

Every worked example MUST:

1. **Show the exact command, request, code or configuration.**
2. **Show its realistic output**, in its own fenced block. A command with no output teaches syntax but not interpretation.
3. **Explain which fields matter and why** — the sentence after the output is the part that teaches.
4. **Include at least one failure or misleading result** somewhere in the note, with the mechanism behind it. Not "it failed because the value was wrong", but *which parser rejected it, at which stage, and what it was checking for.*

Every worked example MUST NOT:

- Instruct the reader to build infrastructure, spin up hosts, or install a target.
- Ask a question, request a submission, or contain an answer box.
- Include cleanup steps — nothing was built, so nothing needs removing.
- Say "try this yourself", "your turn", or "verify that you get".

Use synthetic hosts, identities, domains, addresses and records — `192.0.2.0/24`, `example.com`. Authorized offensive material establishes the mechanism with bounded evidence and explicit scope statements.

**Formatting.** Prefer `shell-session` fences with a visible prompt for command-plus-output pairs, and a plain fence for output shown alone:

````markdown
```shell-session
analyst@lab:~$ ip -s link show eth0
2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP
    RX: bytes  packets  errors  dropped
    114829461  248193   0       0
```

`errors 0` is what a healthy link looks like. A rising count here — while everything
still "works" because TCP retransmits — is the early warning of a failing cable.
````

---

## 6. Strict Multiple-Trees Architecture

The graph is intentionally hierarchical:

```text
Cyber Security
-> Domain
-> Branch or Sub-Index
-> Technical Leaf
```

- A node has one parent.
- Root and indexes create vertical edges.
- **Leaves do not link laterally to other leaves.** Cross-topic references use **bold text**, not wikilinks.
- `Domain:` creates the child-to-parent graph edge.
- Domain `tree/*` tags drive Graph View colours.
- A concept needing substantial independent treatment becomes an atomic leaf under the correct parent, not a large lateral section.

---

## 7. Naming, Metadata & Difficulty

Use professional names that resemble an enterprise wiki: no numeric folder prefixes, no underscores, no synthetic module codes, no `Hub` or `Branch` prefixes. Use `&` instead of "and" in visible titles joining peer concepts. Keep filenames stable unless a rename materially improves the architecture, and preserve aliases so historical names keep resolving.

**Difficulty tags** replace the old level tags and map to the scale the website will render:

| Tag | Meaning |
|:--|:--|
| `difficulty/info` | Index, hub and navigation notes. No lesson content. |
| `difficulty/easy` | Assumes no prior knowledge of the subject. Entry points into a branch. |
| `difficulty/medium` | Assumes the branch's earlier rooms. The working majority. |
| `difficulty/hard` | Internals, edge cases, exploitation depth. Assumes the whole branch. |

```yaml
---
title: "Windows Memory Internals & Exploit Mitigations"
aliases: ["Windows Memory", "VAD", "Windows Mitigations"]
tags:
  - tree/os
  - cyber/foundations/windows
  - type/concept
  - difficulty/hard
Domain:
  - "[[Windows]]"
Color: "#FFA500"
---
```

---

## 8. Editorial Quality

- Write in professional English.
- Prefer precise plain language over inflated jargon; define acronyms on first use.
- Separate stable principles from version-specific behaviour.
- Mark simulations, illustrative output, assumptions and inferences honestly.
- No generic filler, and no paragraph mechanically repeated across notes.
- Replace training-provider branding with technology-focused instruction.
- Preserve existing image embeds and user-authored material unless the task explicitly supersedes it.

---

## 9. Definition of Done

A leaf is complete only when:

- A beginner can enter without an unstated prerequisite.
- Someone finishing it can reproduce, troubleshoot and reason about internals, edge cases and security.
- Sections are plain descriptive `##` headings — no `Task N` numbering, and no `Task N` cross-references in prose.
- The first-degree learning order matches the parent.
- The parent link, `Domain:`, `Color:`, difficulty tag, aliases, tags, code fences, visuals and embeds are all valid.
- No sibling or lateral leaf wikilinks were introduced.
- Every important command shows realistic output **and** an interpretation.
- At least one worked example is present, and **no labs, questions, quizzes or flags** appear anywhere.
- If the subject is a byte, packet, memory, register or disk layout, an **authored, visually-inspected image** is present — not merely a Mermaid flowchart (§4).
- A `## Summary` section states what the reader should now be able to do.
- No generic placeholders remain.

---

## 10. Migration Note (2026-08-31)

This standard replaced an earlier three-level model in which every note was divided into labelled *Crook*, *Operator* and *Root* sections and was required to carry a runnable lab.

That structure was removed vault-wide: 306 notes were converted to flat sections, 205 lab sections were cut, 281 checkpoints became `## Summary` sections, and `level/*` tags became `difficulty/*`. A later pass stripped the interim `## Task N — ` numbering from 1,624 headings across 303 notes, leaving the descriptive titles. The extracted labs and checkpoints are preserved under `.archive/` as source material for the private website repo — they are not part of the published documentation and Obsidian ignores that folder.

The **name** Crook2Root is unchanged. It always described the journey, not the note template.
