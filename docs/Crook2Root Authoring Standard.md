# Crook2Root Authoring Standard

Crook2Root is a cybersecurity knowledge system designed to take a reader from complete beginner to independent expert. The name is an editorial promise: every technical leaf must be understandable at **Crook**, usable at **Operator**, and defensible at **Root**.

This document is the permanent content philosophy for every domain. Contributors and automated editors should apply it without requiring the project owner to repeat it in each request.

## 1. The Three-Level Learning Contract

### Crook — Build the Mental Model

Assume the learner has never seen the subject.

- Explain what the thing is and why it exists.
- Define prerequisites and every essential term before using it heavily.
- Use a concrete analogy, then state where the analogy stops being accurate.
- Show the smallest safe example and its expected result.
- Identify the object, protocol, process, or trust boundary being studied.
- Avoid unexplained acronyms, cargo-cult commands, and premature edge cases.

A Crook section succeeds when a new learner can describe the mechanism in plain language and reproduce the baseline example.

### Operator — Make It Work & Diagnose It

Move from recognition to reliable operation.

- Explain architecture, data flow, state transitions, inputs, outputs, and dependencies.
- Show realistic commands, configuration, code, requests, responses, logs, or debugger output.
- Explain every important flag or field used in the example.
- Include normal output, at least one failure mode, and a troubleshooting workflow.
- Teach evidence collection: what proves the conclusion and what could produce a false conclusion?
- Use a bounded hands-on lab with prerequisites, procedure, expected output, interpretation, and cleanup.

An Operator section succeeds when the learner can investigate an unfamiliar system without copying a memorized recipe blindly.

### Root — Explain the Internals & Tradeoffs

Reach implementation-level understanding.

- Trace the mechanism through parsers, protocols, runtimes, kernel structures, cryptographic assumptions, or control planes as appropriate.
- Cover edge cases, version or platform differences, race conditions, resource limits, failure recovery, and security boundaries.
- Explain how controls fail, how to debug the failure, and how design choices change risk.
- Distinguish demonstrated facts, inferences, and hypotheses.
- Connect offense, defense, engineering, and forensic evidence under authorized use.
- End with a **Crook → Operator → Root** checkpoint that tests explanation, operation, and independent reasoning.

A Root section succeeds when the learner can predict behavior, design a defensible experiment, and explain the result from first principles.

## 2. Required Leaf Anatomy

Section names may adapt to the subject, but every technical leaf needs the following functions:

1. YAML frontmatter with one parent, domain tag, level/type tags, aliases, and matching color.
2. A clear H1 and a short abstract stating the learning outcome.
3. `## Parent Learning Order` followed by one plain-text order line.
4. Beginner mental model and prerequisites.
5. Architecture or mechanics explanation.
6. At least one meaningful visual — Mermaid **or an authored image** where the subject is inherently spatial (see §4).
7. Practical commands, code, or protocol examples with realistic output.
8. Failure modes and troubleshooting.
9. Security implications and authorized-use boundaries.
10. A **runnable, step-by-step lab** — every step shows its real command *and* its real output (see §6). A list of things the reader "could try" is not a lab and does not satisfy this item.
11. A Crook → Operator → Root checkpoint.
12. A single parent link at the footer.

Recommended technical-leaf depth is approximately 1,500–5,000 words. Complexity—not padding—determines the final size. Shorter is acceptable only when the topic is genuinely narrow and still satisfies the complete learning contract.

## 3. Parent Learning Order Rule

Each parent owns an ordered curriculum of its direct children. Every direct child repeats that same first-degree order near the beginning:

```markdown
## Parent Learning Order
Foundations -> Architecture -> Operation -> Troubleshooting -> Mastery
```

Rules:

- Use `->` exactly as the separator.
- List direct siblings only.
- Do not include grandchildren or deeper descendants.
- Do not add descriptions, numbers, bullets, or commentary to the order line.
- Do not use wikilinks on the order line; lateral links would collapse the strict tree topology.
- Use the professional visible title of each sibling.
- Update every sibling if the parent curriculum changes.

## 4. Visual Standard

A visual must teach a relationship that prose alone would make harder to understand.

Use Mermaid for:

- `sequenceDiagram` — protocol exchanges, syscalls, authentication, remote execution, and request lifecycles.
- `flowchart` — architecture, decision paths, trust boundaries, and transformations.
- `stateDiagram-v2` — process, protocol, scheduler, or resource states.
- `classDiagram` — object ownership and structural relationships.
- `timeline` — boot, incident, or forensic sequences.

**Mermaid is not sufficient for every subject.** When the concept is inherently *spatial* — a byte or bit layout, a packet/frame/header field map, a hex-dump-to-field mapping, a memory or address-space map, a register or flag layout, a disk/partition structure, or an RF channel arrangement — Mermaid cannot express it, and the note **must include an authored image**. Author these as self-contained SVGs (theme-agnostic dark background `#0f1420`, light text), store them in `assets/` with a domain prefix (e.g. `net_`, `os_`), and embed with `![[name.svg]]`. **Any authored image must be rendered and visually inspected before it is committed** — SVG label collisions and overflow are common and are not caught by text tooling. Every visual needs nearby prose explaining how to read it and why it matters.

Decorative diagrams, repeated generic flows, and visuals that merely restate a list do not satisfy the standard. A note whose only visuals are Mermaid flowcharts, when its subject is a byte or memory layout, is **incomplete**.

## 5. Practical Evidence Standard

Commands without output teach syntax but not interpretation. Every important workflow should show:

- The exact command, request, code, or configuration.
- A realistic expected result.
- Which fields matter and why.
- One likely error or misleading outcome.
- A safe troubleshooting step.
- Scope and cleanup when the exercise changes state.

Use synthetic hosts, identities, domains, addresses, records, and markers. Authorized offensive material should establish the mechanism with bounded evidence and explicit stop conditions.

## 6. The Lab Standard — Labs Must Actually Run

The lab is the leaf's proof that the reader can *do* the thing, not just read about it. It is the most frequently degraded section, so its requirements are explicit and non-negotiable.

**A lab is a sequence of executed steps, each showing a real command and its real output.** The reader should be able to paste the commands and see the results described.

Every lab MUST:

1. **State its setup cost honestly, and minimise it.** Prefer a lab that runs on **one machine the reader already has**. Network topics use Linux network namespaces, veth pairs, or loopback to build a real second host inside one kernel — never demand "two VMs" or hardware the reader may lack when a namespace or container will do. Platform notes (Windows, macOS) may require that platform, but must still run on a single ordinary instance of it with built-in tooling.
2. **Show real output under every command**, in its own fenced block, with a sentence interpreting it. A step with a command and no output is unfinished.
3. **Include at least one deliberate failure or break** — a wrong mask, a dropped packet, a missing `-ErrorAction Stop`, a spoofed field — so the reader sees the mechanism fail, not only succeed. The most important lessons live in the break.
4. **End with verifiable cleanup** whenever it changes state: a command that removes what was created **and** output confirming removal (e.g. a "does not exist" error). Read-only labs state "no cleanup required — every command read state only."
5. **Close with a one-line "What you should now be able to do."**

**Prohibited lab anti-patterns** (each is grounds for rejecting the note):

- A bulleted list of suggestions — "try scanning…", "you could inspect…", "if you have a second VM…" — with no commands or output. This is a to-do list, not a lab.
- Commands with no output shown.
- A cleanup that deletes without confirming, or a state-changing lab with no cleanup.
- A lab that cannot be run at all without infrastructure the note never helps the reader build.

A lab that merely tells the reader what they *could* try teaches nothing and fails the Crook2Root promise. If the reader cannot follow the lab to a verified result on a machine they have, the note is incomplete.

## 7. Strict Multiple-Trees Architecture

The graph is intentionally hierarchical:

```text
Cyber Security
-> Domain
-> Branch or Sub-Index
-> Technical Leaf
```

- A node has one parent.
- Root and indexes create vertical edges.
- Leaves do not link laterally to other leaves.
- Cross-topic references use **bold text**, not wikilinks.
- `Domain:` creates the child-to-parent graph edge.
- Domain `tree/*` tags drive Graph View colors.
- A concept needing substantial independent treatment becomes an atomic leaf under the correct parent rather than a large lateral section.

## 8. Naming & Metadata

Use professional names that resemble an enterprise wiki:

- No numeric folder prefixes.
- No underscores.
- No synthetic module codes such as `LNX.1`.
- No `Hub` or `Branch` prefix.
- Use `&` instead of “and” in visible titles that join peer concepts.
- Keep filenames stable unless a rename materially improves the architecture.
- Preserve useful aliases so historical names continue resolving.

Example:

```yaml
---
title: "Windows Memory Internals & Exploit Mitigations"
aliases: ["Windows Memory", "VAD", "Windows Mitigations"]
tags:
  - tree/os
  - cyber/foundations/windows
  - type/concept
  - level/root
Domain:
  - "[[Windows]]"
Color: "#FFA500"
---
```

## 9. Editorial Quality

- Write in professional English.
- Prefer precise plain language over inflated jargon.
- Define acronyms on first use.
- Separate stable principles from version-specific behavior.
- Mark simulations, illustrative output, assumptions, and inferences honestly.
- Do not use generic filler or mechanically repeat paragraphs across notes.
- Replace platform branding from training providers with technology-focused instruction.
- Preserve existing image embeds and user-authored material unless the task explicitly supersedes it.

## 10. Definition of Done

A leaf is complete only when:

- A beginner can enter without an unstated prerequisite.
- An operator can reproduce and troubleshoot the workflow.
- An expert can reason about internals, edge cases, security, and evidence.
- The first-degree learning order matches the parent.
- The parent link, Domain property, color, aliases, tags, code fences, visuals, and embeds are valid.
- No sibling or lateral leaf wikilinks were introduced.
- Commands include realistic output and interpretation.
- The lab is a **runnable step-by-step sequence** in which every step shows a real command and its real output, includes a deliberate failure, and ends with verified cleanup (§6). A "things you could try" list fails this test.
- The lab runs on **one machine the reader plausibly has**, building any additional hosts locally (namespaces, containers, loopback) rather than assuming unavailable infrastructure.
- If the subject is a byte, packet, memory, register, or disk layout, an **authored, visually-inspected image** is present, not merely a Mermaid flowchart (§4).
- No generic placeholders remain.

