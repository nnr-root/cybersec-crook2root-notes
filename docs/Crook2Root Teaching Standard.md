# Crook2Root Teaching Standard

Companion to the **Authoring Standard**. That document governs *structure* — one
parent, Mermaid-only visuals, no labs, no numbered tasks. This one governs
*teaching*: the moves that decide whether a correct note is actually learned.

It exists because a September 2026 audit of all 302 leaves found the prose was
strong and the sequencing was not. Paragraphs ran a tight 38-word median, 60% of
analogies stated their own breaking point, 75% of notes showed a command failing
— and 0.3% explained why it failed, 1.3% named a misconception, 1.6% compared two
examples, and the first piece of evidence arrived 41% of the way into the note.

## 0. The principle

Chi, Feltovich & Glaser had physicists and undergraduates sort problems. Novices
sorted by **surface features** — the apparatus, the objects named. Experts sorted
by the **governing principle**. That gap is what this project is named after:

> **Crook** sees surface features: a tool, a port, a payload that worked once.
> **Root** sees deep structure: the class of parser confusion that payload belongs to.

Every note exists to move the reader across that line. A note that teaches a tool
teaches a surface feature. A note that names the *class of mistake* the tool
exploits, and then shows the same shape somewhere unrelated, moves someone toward
root.

## 1. What "not boring" means here

Engagement comes from the **structure of the explanation**, never from ornament.
This is not a style preference. The *seductive details effect* — interesting but
irrelevant material — measurably degrades both retention and transfer, and the
damage is worse in technical subjects than in any other. Meanwhile the largest
single effect in the multimedia literature (d = 0.97) is *coherence*: cutting
exactly that material.

So the war story that does not bear on the mechanism costs us. The reliable engine
is the information gap: curiosity is the feeling of a missing piece you know is
missing. Give the reader the naive model, then break it. That is a reordering, not
an addition, and it is free.

Humour is allowed in three places: a section opening before the technical content
starts, a quarantined aside nothing depends on, and self-deprecation about the
author's own past confusion. It is banned in troubleshooting and remediation,
where the reader is already stressed.

## 2. The ten patterns

| Pattern | The move | Gate |
|:--|:--|:--|
| **The Cold Open** | Open on the artifact — a capture, a dump, a diagram, a field table — not the definition. Abstraction lands *after* the reader has seen the thing it abstracts. | warning at >400w |
| **The Break** | State the model a reasonable person would arrive at, then violate it. Phrase it in the reader's voice and state it confidently: "you'd assume", never "some people think". Marked with the house form **`**The deliberate break:**`** — see §2a. | review |
| **The Autopsy** | Every error output gets a paragraph naming **which component rejected it**, **at which stage**, and **what it was checking for**. "It failed because the value was wrong" does not satisfy this. The corpus was already close to this; see §6a. | warning |
| **The Twin** | Two surface-different, structurally identical examples, with the comparison spelled out in prose. Juxtaposition alone does not work — only 16% of readers compare unprompted. | review |
| **The Name** | Give the deep structure a label and reuse it everywhere it recurs. "Parser differential." Named patterns are chunks, and chunking is what expertise physically is. | glossary |
| **The Tell** | Name the recognition cue — how you notice you are looking at this, not how to exploit it. Where options are confusable, use a diagnostic table. | review |
| **Subgoal Headings** | Headings name the move, not the topic. The four generic labels are banned outright. | error |
| **One Pre-Question** | Exactly one per note, on the load-bearing idea, always answered within a few sentences. Never leave one hanging. | warning |
| **The Fade** | Annotation density drops across a branch. Scaffolding goes in visually distinct, skippable containers. Never repeat an explanation "for safety". | review |
| **The Honest Note** | When something is hard, say so before the hard part, in the reader's voice. Never "don't worry, this is easy". | error (hedges) |

### 2a. The Break has a house form already — use it

The Tooling branch independently evolved a marker for this pattern and uses it in
**63 notes**: a paragraph opening `**The deliberate break:**`. It works, readers
of that branch already meet it every few pages, and it is exactly the two-beat
gap this standard asks for.

It appears in **zero** notes outside Tooling. Adopt it corpus-wide rather than
inventing a second form — a pattern with two names is two patterns.

### The Thread

One lab topology, defined once and referenced by every note: a handful of named
hosts, one deliberately weak web app, one binary, one capture file. Attention that
would go into re-orienting goes into the mechanism instead.

This is all-or-nothing. A half-adopted running example is worse than none, because
readers learn to distrust references to a lab only half the notes use.

## 3. Why the pre-question is budgeted at one

Prequestioned material learns at g = 0.66. Non-prequestioned material *in the same
lesson* learns at g = 0.01. A pre-question is a targeting instrument, not a warm-up:
whatever you ask about gets learned, at the expense of everything else on the page.
Ask three and you have told the reader most of the note is optional.

## 4. Two findings that contradict the obvious

**Do not interleave topics.** Interleaving works for visual category learning
(g = 0.67 for paintings) but has *no significant effect* for expository text and is
*negative* for verbal material (g = −0.39). Block your topics — which is what
`Parent Learning Order` already does. The one exception is high-value: interleave
where the reader must tell confusable things apart. ECB vs CBC vs CTR vs GCM
belong juxtaposed in one section, not given separate homes.

**Do not make it harder for a beginner.** Desirable difficulties become
*undesirable* exactly when the learner lacks the background to succeed. The
distinction that matters: desirable difficulties are difficulties of **retrieval**,
never of **comprehension**. Obscure prose and missing steps are extraneous load
wearing a flattering label.

> Make the *material* as easy to comprehend as possible. Make the reader's
> *engagement* with it as effortful as they can currently succeed at.

## 5. On hedges — the rule targets the construction, not the word

Banned: minimising the reader's task. "You simply run", "just install", "all you
have to do is", "it should be clear that". To someone who is stuck, these say the
problem is them.

**Not banned:** "trivially forged", "trivially bypassed", "a connection is simply
matching state held at both ends". These characterise *attacker cost* or
*mechanism minimality* — precise security claims, and deleting them weakens the
prose. The original blanket ban flagged 85 instances; only one was a real
violation. The gate was retargeted rather than the corpus mangled.

## 6a. A correction: the corpus already had The Autopsy

The audit originally reported that 75% of notes show a command failing and
**0.3% explain why**, and called closing that gap the single highest-leverage
fix. **That figure was wrong**, and the error was in the measuring instrument.

The first detector matched any line containing "error", "denied", "failed" or
"invalid" *anywhere in any fenced block*. That swept in Mermaid node labels
(`DENY["Access denied"]`), C and PHP source (`else puts("denied")`), command
flags (`F=Invalid credentials`), shell options (`set -e  # exit on error`),
comments, and — memorably — a success report reading `Failed : 0`. On the other
side, it required narrow trigger words to recognise an explanation, so it scored
a paragraph reading "a single appended line breaks the hash" as no explanation
at all.

Rebuilt for precision — output-only fences, prompt and comment lines excluded, a
narrow set of shapes that are unambiguously a tool refusing something, and
recognition that a note may set the mechanism up *before* the block as easily as
after — the real backlog was **four notes**, not 230. Three have been written;
the rest of the corpus already did this.

The lesson is not that the pattern is unimportant. It is that a
badly-calibrated check produces a confidently wrong number, and a number is what
a plan gets built on. Treat any figure this gate reports as a claim about the
gate until it has been read against the source.

## 6b. A second correction: the Cold Open backlog was 280, and is 25

The audit reported the first command arriving 41% into the median note and put
**280 notes** in the Cold Open backlog. A 20-note sample, read rather than
counted, showed the metric was wrong in two ways.

**It penalised short notes.** BloodHound reaches a command 109 words after its
first heading and scored 41%, because the note is only 535 words long. Nine of
the twenty sampled were in this class — Volatility, Gobuster, feroxbuster, Bash,
enum4linux and others, all reaching evidence inside ~200 words. A ratio measures
note length as much as it measures burial.

**It ignored the visual standard.** "Distance to the first shell command" is the
wrong question to ask of a corpus whose own standard makes Mermaid the primary
visual. A note opening on a sequence diagram or a register table *has* given the
reader something concrete.

Re-measured as **words of lesson prose before the first command, diagram or
table**, excluding the abstract and Parent Learning Order:

| | ratio metric | corrected |
|:--|--:|--:|
| Median prose before an anchor | — | **173 words** |
| Notes over 400 words | — | **25** |
| Notes flagged | **280** | **25** |

Those 25 are theory-heavy openings, not defects. The pass is optional quality
work, not a blocker.

## 6. What the gate cannot check

**The Break, The Twin, The Tell and The Fade are not mechanisable.** A regex that
"detected" a naive-model beat would only teach us to type the trigger phrase.
These live on the review checklist in `CONTRIBUTION.md` and are checked by reading.

The pedagogy gate is now deliberately *strict* on what counts as an error output
and generous on what counts as an explanation — the opposite of its first
version, and for the reason in §6a. It will miss a genuinely unexplained failure
written in unusual phrasing. That is the intended trade: a check that cries wolf
230 times gets ignored, and a check that flags four notes gets read.

## 7. Staleness

Notes containing shell commands carry a `verified:` date in frontmatter, set when
someone last actually ran them. The gate warns when the field is missing and again
past twelve months.

**Dates are never backfilled.** A `verified:` date that nobody earned is worse than
no date, because it converts an honest gap into a false claim. The 294 notes
currently missing the field stay flagged until their commands are re-run.

This is the one advantage neither TryHackMe nor HackTheBox can match: their content
review is a release gate with no maintenance stage, and learners discover rot by
hitting it. A diffable corpus with a verification clock is a structural answer.

---
> Governance: **Authoring Standard** (structure) · **Teaching Standard** (this) · `AGENTS.md` (agent rules) · `CONTRIBUTION.md` (review checklist)
