# Crook2Root — Visual Identity

**Status: adopted.** Style is **technical schematic**. Scope is **brand only** —
no image enters a note body, and every instructional visual stays Mermaid or a
field table.

---

## 0. Why this document exists, and a correction

On 2026-09-01 all 227 image files were removed from the repo and a CI gate was
added to keep them out. The Master Blueprint recorded the reason as *"the
AI-generated visuals read as AI-generated."*

**That reason was wrong, and this note corrects the record.** The removed files
are still in `_to_delete/assets/`, and reading them shows two different problems,
neither of which was AI art:

1. **Lifted third-party screenshots.** Tool captures taken from other people's
   training material — one still carries a `DRAFT` watermark and a stack trace
   from an unrelated commercial course. Unknown licence, unknown provenance, and
   nothing about them was ours to publish.
2. **Generic stock clipart.** A red clipboard with tick marks. A magnifying
   glass. Decoration adjacent to technical prose, which is precisely what the
   coherence principle (d = 0.97, and *negative* in technical subjects) says
   depresses comprehension.

The distinction matters because it changes what is permitted now. What was
removed was borrowed and decorative. A purpose-built identity, authored for this
platform and kept out of the teaching material, is a different proposition and is
not what the gate was built to stop.

**The two rules that survive from the original Visual Standard are unchanged:**

- A visual that could mislead is worse than no visual.
- Media that regenerates itself does not rot.

Everything below is downstream of those two.

---

## 1. The concept

**The mark is `#`.**

`$` is a user shell. `#` is root. Every practitioner this platform is for reads
that instantly and reads it correctly — no legend, no explanation, no "it is a
cross-section representing depth." It is the most economical mark available for
the second half of the name, and it is understood before anyone has read a word
of the corpus.

The first draft of this document proposed a strata cross-section instead. `#` is
better, and the reason it is better than a compromise is what the glyph is made
of:

> **Two horizontal bars, crossed by two strokes that lean rather than falling
> straight.**

That is the strata concept already compressed into an existing character. The
horizontals are layer boundaries; the leaning strokes are the descent that
deviates instead of dropping straight through. **The symbol says root. The
geometry says descent through layers, and not in a straight line.** Both halves
of the name, in four strokes, in a character every reader already knows.

A straight-sided `#` would be the wrong drawing — it would say the route from
surface to depth is obvious. The lean is load-bearing, and it is also simply how
the glyph is drawn, which is the part that makes this work rather than feel
imposed.

**What the mark is not:** a padlock, a hoodie, a skull, a shield. Those say
*security* generically, which is the one thing this platform never needs to
establish — the reader arrived knowing.

### The rejected treatment, and why

A neon-green `#` with chromatic aberration and bloom was generated and
seriously considered. The symbol was right and the treatment was refused, on
three grounds, in order of weight:

1. **Neighbourhood.** Green-on-black with RGB fringing is the most crowded
   corner of this market — it is what Hack The Box looks like, and roughly every
   CTF platform of the last decade. A corpus whose actual differentiator is 302
   notes that each name a misconception and supply a recognition cue should not
   wear a mark saying *we are also a hacking site*.
2. **Internal continuity.** Glow and fringing sitting next to flat 1.5 px
   Mermaid line work reads as two projects. Every other visual decision here was
   made to match the notes.
3. **Reduction.** Weaker than the first two, and worth stating accurately: the
   neon version *does* survive 32 px. It goes soft and muddy-teal and loses the
   crisp core and the fringe — which are exactly the things that made it
   distinctive — but it remains legibly a hash. This was checked by rendering it
   rather than asserted.

**The neon render is retained as a launch and social asset**, where volume is
the job and permanence is not. It is not the identity, and it does not appear in
`docs/brand/`.

## 2. The style

**Technical schematic.** Engineering drawing, not illustration.

| Property | Specification |
|:--|:--|
| Ground | `#0F1419` flat, with an 8 px grid at `#1A2129` (barely visible) |
| Line work | Uniform **1.5 px** strokes, `#C8D3DD`. No variable weight |
| Accent | Exactly **one** per asset, from the domain palette below |
| Fills | Flat or none. No gradients, no bevels, no drop shadows, no glow |
| Projection | Orthographic. Front-facing or true cross-section. Never perspective |
| Annotation | Leader lines with small-caps labels, set in the layout — **never drawn by the model** |
| Texture | None. No scanlines, no noise, no film grain, no lens effects |

The style is chosen for three reasons. It sits continuously with the field
tables, hex dumps and Mermaid already in the corpus. It is reproducible — two
assets made three months apart will match, which is the thing atmospheric styles
cannot promise. And it is close to unmistakable for generic AI output, because
almost nothing else in this space looks like a drawing office.

### Palette

Taken from the frontmatter `Color:` values already in use across the corpus, so
the brand and the vault agree without anyone maintaining a mapping.

| Domain | Hex | Notes |
|:--|:--|:--|
| Offensive Security | `#DC143C` | 152 notes — the dominant accent |
| Tooling & Scripting | `#708090` | 86 |
| Networking | `#42D4F4` | 70 |
| OS Internals | `#FFA500` | 45 |
| Cryptography | `#FFE119` | 21 |
| Application Security | `#911EB4` | 6 |
| Defensive Security | `#4363D8` | 3 |
| DevSecOps | `#3CB44B` | 2 |

Platform-level assets use `#DC143C` on `#0F1419`. Domain assets use their own.

---

## 3. What gets made

Twelve assets. All live in `docs/brand/`. None is referenced from a note.

```text
docs/brand/
  mark.svg              the hash, monochrome line work, on grid
  mark-accent.svg       the hash in the strata stack, crimson descent strokes
  hero.png              2400×1260 — README and site header
  og-card.png           1200×630 — link previews
  favicon.svg           16px-legible reduction of the mark
  domain-offensive.png   1600×900
  domain-tooling.png     …
  domain-networking.png  …
  domain-os.png          …
  domain-crypto.png      …
  domain-appsec.png      …
  domain-defensive.png   …
```

**Text is never generated.** Image models garble lettering, and a wordmark with a
malformed glyph is worse than no wordmark. Every label, the name, and all
annotation are set afterwards in SVG or CSS over the generated plate.

---

## 4. Prompt library

Written for **Nano Banana Pro** (Gemini's image model as of 2026). Paste
verbatim; the constraints matter more than the subject line and are what keeps
twelve assets looking like one set.

### 4.1 The shared style block

Append this to every prompt.

```text
STYLE: technical schematic illustration, engineering drawing, orthographic
projection, flat dark background #0F1419 with a faint 8px square grid in
#1A2129. Uniform thin line work at consistent 1.5px weight in #C8D3DD.
Absolutely flat — no gradients, no bevels, no drop shadows, no glow, no
ambient occlusion, no 3D rendering, no photorealism, no texture, no noise.
Precise, measured, drafting-table quality. Generous negative space.
Centered composition.

DO NOT INCLUDE: any text, letters, numbers, words, labels, watermarks,
signatures, logos. No people, no faces, no hands. No hoodies, no masks, no
skulls, no padlocks, no binary rain, no circuit-board motifs, no neon, no
scanlines, no lens flare, no glowing edges.
```

### 4.2 The mark — not generated

```text
The mark is authored as SVG, not generated — a form this geometric is
drawn more precisely by code than by any model, and it stays diffable and
exact at every size. See docs/brand/mark.svg. This section is kept only
to record that the decision was deliberate.
```

### 4.3 The hero

```text
A wide technical cross-section of layered strata receding into depth, drawn
as an exploded engineering diagram. Multiple descent paths thread downward
through the layers at different lateral positions, each stepping around the
boundaries rather than piercing them straight. Faint dimension lines and
leader lines extend from several strata boundaries into empty margin space,
ending without labels. One path is crimson #DC143C; all others are #C8D3DD.
Wide 2:1 landscape composition with the strata occupying the lower two
thirds and open space above.

[+ shared style block]
```

### 4.4 Domain plates

One template, eight runs. Swap the two bracketed values.

```text
A technical schematic plate representing [SUBJECT], drawn as an orthographic
engineering diagram: clean geometric forms, thin uniform line work, faint
dimension and leader lines extending into empty margin space and ending
without labels. Single accent colour [HEX] used sparingly on one focal
element; everything else in #C8D3DD line work. 16:9 landscape, subject
centered, generous margins.

[+ shared style block]
```

| Domain | `[SUBJECT]` | `[HEX]` |
|:--|:--|:--|
| Offensive Security | a lattice of connected nodes with one traced path crossing several boundary lines | `#DC143C` |
| Tooling & Scripting | an exploded view of nested modular components on a rail | `#708090` |
| Networking | concentric routing rings connected by radial links, drawn as a plan view | `#42D4F4` |
| OS Internals | nested concentric rectangular boundaries, innermost solid, drawn as a plan view | `#FFA500` |
| Cryptography | interlocking geometric key-forms and a lattice of paired points | `#FFE119` |
| Application Security | stacked request-response layers as horizontal bands with one vertical connector | `#911EB4` |
| Defensive Security | overlapping sensor arcs covering a field, with one uncovered wedge | `#4363D8` |
| DevSecOps | a closed cyclic loop of connected stages with inspection gates on each segment | `#3CB44B` |

The uncovered wedge in the Defensive plate is deliberate — it is the blind-spot
argument from the monitoring notes, drawn.

### 4.5 Working notes

- **Generate at the largest size the model offers**, then downscale. Schematic
  line work survives downscaling and does not survive upscaling.
- **Iterate on the shared block, not the subject.** If a plate comes back with a
  glow or a gradient, strengthen the negative list rather than rewriting the
  subject.
- **Reject anything with lettering**, however plausible it looks. That is the
  single most reliable tell of a generated asset.
- Keep the raw generations. `docs/brand/` holds finals only, but the accepted
  prompt for each asset belongs in this file so a replacement is reproducible.

---

## 5. Motion, and why it is not Veo

The original pillar wanted terminal GIFs for command sequences, and the instinct
was right: a reader watching `nmap` resolve states learns something a static
block does not show.

**Generated video is the wrong tool for it.** Veo would be inventing terminal
output — plausible text, invented timings, fabricated results — which is the
misleading-visual rule breaking in the most direct way available. A viewer cannot
tell an invented `nmap` run from a real one, and the corpus's entire claim is
that its commands were actually executed.

**The right tool is a recording.** `asciinema` captures a real session as a
timed text file; `svg-term` or `agg` renders that to an animated SVG or GIF.

| Property | Recorded | Generated |
|:--|:--|:--|
| Output shown | Real, executed | Invented |
| Diffs in git | Yes — it is text | No — binary |
| Survives a rename | Yes | Yes |
| Re-recordable when output changes | Yes, one command | Requires regeneration and re-review |
| Can be wrong | Only if the command was | Always possible |

This satisfies both surviving rules, and it pairs with the `verified:` field:
a recording *is* a verification, timestamped and watchable.

**Not in scope yet.** Motion stays out until the brand set is finished and the
gate has a rule for `.cast` files. When it starts, it starts with the handful of
sequences where watching genuinely beats reading — a scan resolving states, a
handshake completing, a `free -h` before and after cache pressure — and not with
302 recordings nobody asked for.

---

## 6. The line that does not move

No image appears inside a content note. Not a header, not a diagram, not a
decoration. Instructional visuals are Mermaid or field tables, because those are
exact, diffable, theme-aware and impossible to garble.

The gate enforces it: `ci-check.py` permits image files under `docs/brand/` and
errors on one anywhere else, and the `![[...]]` embed rule is unchanged.
