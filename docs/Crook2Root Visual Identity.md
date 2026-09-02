# Crook2Root — Visual Identity

**Status: adopted.** Style is **technical schematic**. Scope is **brand only** —
no image enters a note body, and every instructional visual stays Mermaid or a
field table.

---

## 0. Why this document exists, and a correction

On 2026-09-01 all 227 image files were removed from the repo and a CI gate was
added to keep them out. The Master Blueprint recorded the reason as *"the
AI-generated visuals read as AI-generated."*

**That reason was wrong, and this note corrects the record.** The removed files were read before this was written — they sat in
`_to_delete/assets/` until that staging directory was cleared on 2026-09-02, and
remain recoverable from history at `a489d0c^`. They showed two different
problems, neither of which was AI art:

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

## 1. The mark

**The mark is a neon `#`.** The master is `docs/brand/mark.png`, and it is used as
supplied — this document describes it rather than specifying how to redraw it.

`$` is a user shell. `#` is root. Every practitioner this platform is for reads
that instantly, without a legend, before they have read a word of the corpus. It
is the most economical mark available for the second half of the name.

| | |
|:--|:--|
| Ground | `#17181A` with a soft vignette |
| Tube | `#20B57C` — the neon body |
| Core | `#CDFEE8` — the hot centre of the tube |
| Fringe | Chromatic separation, red and cyan, at the stroke edges |

### How it was chosen

A technical-schematic mark was drafted first — flat orthographic line work
matching the field tables in the corpus. It was **rejected on sight, correctly**:
it was defensible and forgettable, and it read as a UI icon rather than a brand.
A mark nobody wants to put on a landing page has failed at its actual job.

Two arguments were made against the neon treatment. One of them was wrong, and
recording which is the point of this section:

- **Wrong — "glow next to flat Mermaid line work reads as two projects."** Brand
  assets never appear inside a note. The scope is brand-only and always was, so
  the mark never sits beside a diagram and there was no continuity to break. This
  was a constraint defended after it had already been removed.
- **Partly right — the neighbourhood.** Green-on-black is the most-used palette
  in this market. That remains true, and it was overruled deliberately: the mark
  has to earn attention in marketing contexts, and a differentiated palette that
  nobody looks at twice is worth less than a familiar one that lands.
- **Weakest, and stated accurately — reduction.** The mark does soften below
  32 px. This was measured rather than asserted, and it is handled by the icon
  ladder below rather than by changing the design.

## 2. Usage

- **Dark grounds only.** The glow is part of the mark; on a light ground it has
  nothing to bloom into. Where a light or single-colour reproduction is
  unavoidable — print, embroidery, a fax of a purchase order — use
  `docs/brand/mark.svg`, the flat monochrome fallback retained for exactly this.
- **Do not recolour, rotate, outline or place on a busy photograph.**
- **Minimum size 32 px.** Below that the tube closes up.
- **Clear space** of at least one bar-width on every side. The master already
  carries generous margin; the icon crop does not.

## 3. The asset ladder

```text
docs/brand/
  mark.png       2048²   master, as supplied, untouched
  hero.png       2400×1260   README and site header
  og-card.png    1200×630    link previews
  favicon.ico    multi-res, 16 → 256
  icon-512.png … icon-16.png
  mark.svg       flat monochrome fallback — print and single-colour only
```

**The icon ladder is a crop, not a redraw.** The master centres the glyph in a
lot of empty frame, which is right for a hero and wrong for a browser tab, so the
icons are cropped square to the glyph at ×1.25 and nothing else is altered.

At **32 px and below** two things change, and only because plain downscaling
destroys legibility there: the crop tightens a further 15%, and contrast and
unsharp are applied. Every size at 48 px and above is a straight Lanczos
reduction of the master with no adjustment at all. The 16 px result was compared
across four treatments before this one was chosen.

## 4. Supporting visuals

Anything made *around* the mark — social cards, launch graphics, headers — follows
the mark: dark ground, neon tube, restrained chromatic fringe.

**Domain plates were dropped.** The original plan called for eight
technical-schematic plates, one per domain. A flat orthographic plate in eight
different accent colours does not sit with a neon mark, and reconciling them
would mean either eight neon variants (repetitive) or two visual systems
(incoherent). The mark, hero, OG card and icon ladder are a complete identity for
a repository and a site; the plates were a nice-to-have that stopped being
coherent the moment the mark changed.

The schematic specification below is retained for the **flat fallback** only —
`mark.svg`, and any print or single-colour reproduction.

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
