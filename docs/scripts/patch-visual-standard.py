#!/usr/bin/env python3
"""
Switch the governance docs to a Mermaid-only visual standard.

All image assets were removed from the vault on 2026-08-31. The Authoring
Standard, AGENTS.md, CONTRIBUTION.md, the README and the Room Template all
still required or referenced authored images, so each is patched here.

    python3 docs/scripts/patch-visual-standard.py            # dry run
    python3 docs/scripts/patch-visual-standard.py --apply
"""

import sys

STANDARD_S4_OLD_START = "## 4. Visual Standard"
STANDARD_S4_NEW = """## 4. Visual Standard

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

"""

PATCHES = {
    "docs/Crook2Root Authoring Standard.md": [
        ("6. At least one meaningful visual — Mermaid, **or an authored image** where the subject is spatial (§4).",
         "6. At least one meaningful visual — Mermaid, or a table / ASCII layout / annotated hex dump where the subject is spatial (§4)."),
    ],
    "AGENTS.md": [
        ("- ✅ Diagrams and authored images, which the website repo reuses directly",
         "- ✅ Mermaid diagrams, which the website repo renders directly"),
        ("4. Include at least one meaningful visual — prefer Mermaid for architecture, sequence, state or decision flows. When the subject is inherently spatial (a byte/frame/header field map, a hex-dump-to-field mapping, a memory or address-space map, a register/flag layout, a disk or RF-channel arrangement), Mermaid is **insufficient**: author a self-contained SVG (dark bg `#0f1420`), store it in `assets/` with a domain prefix, embed with `![[name.svg]]`, and **render and visually inspect it before committing**.",
         "4. Include at least one meaningful visual, written as **Mermaid** — architecture, sequence, state, decision flows. **The vault contains no image files and none may be added.** When the subject is inherently spatial (a byte/frame/header field map, a memory or address-space map, a register/flag layout, a disk or RF-channel arrangement), Mermaid cannot express it: use a field table, a fenced ASCII layout, or an annotated hex dump instead. Never a screenshot."),
        ("- Preserve `![[asset.ext]]` embeds and keep assets in `assets/`.",
         "- Do not add image embeds. There is no `assets/` directory and no image file belongs in this repository."),
    ],
    "CONTRIBUTION.md": [
        ("| Diagrams, authored SVGs, images | CTF challenges and flags |",
         "| Mermaid diagrams, tables, ASCII layouts | CTF challenges and flags |"),
        ("- Author an SVG for a subject that is spatial and currently has only prose.",
         "- Add a Mermaid diagram, field table or annotated hex dump where a note has only prose."),
        ("- When the subject is **spatial** — a byte or bit layout, a packet/frame/header field map, a memory or address-space map, a register layout, a disk structure, an RF channel arrangement — Mermaid is insufficient. Author a self-contained SVG (dark background `#0f1420`), store it in `assets/` with a domain prefix, and **render and visually inspect it before committing**.",
         "- When the subject is **spatial** — a byte or bit layout, a packet/frame/header field map, a memory or address-space map, a register layout, a disk structure, an RF channel arrangement — Mermaid cannot draw it. Use a field table, a fenced ASCII layout, or an annotated hex dump. Do not force a flowchart to stand in for a layout."),
        ("- Store assets under `assets/` and embed with `![[asset.ext]]`.",
         "- **Do not add image files of any kind** — no SVG, PNG or GIF, and never a screenshot. Screenshots of code are not searchable or accessible; screenshots of another platform's rooms import their content and branding into a public repo."),
        ("- Keep filenames stable and descriptive — the website repo consumes these images directly.",
         "- Keep Mermaid source readable and commented where the diagram is non-obvious — the website repo renders it directly."),
    ],
    "README.md": [
        ("| Diagrams and authored SVGs | CTF challenges and flags |",
         "| Mermaid diagrams, tables, ASCII layouts | CTF challenges and flags |"),
        ("| 🖼️ **Assets** | 226 diagrams & images (self-authored SVGs + localized graphics) |",
         "| 🖼️ **Visuals** | Mermaid only — diffable, theme-aware, zero binary assets |"),
    ],
    "docs/templates/Room Template.md": [
        ("""![[dom_topic_layout.svg]]

Explain how to read the visual and why it matters. A visual with no reading
instructions does not satisfy the standard.""",
         """```mermaid
flowchart LR
    A["Input"] --> B{"The component<br/>that decides"}
    B -->|condition| C["Outcome A"]
    B -->|otherwise| D["Outcome B"]
```

Explain how to read the visual and why it matters. A visual with no reading
instructions does not satisfy the standard.

<!-- Mermaid only. This repo contains no image files. For a spatial subject —
     a byte layout, a memory map, a register — use a field table, a fenced
     ASCII diagram, or an annotated hex dump instead. Never a screenshot. -->"""),
    ],
}


def patch_section(text):
    """Replace Authoring Standard §4 wholesale."""
    start = text.find(STANDARD_S4_OLD_START)
    if start == -1:
        return text, False
    end = text.find("\n## 5.", start)
    if end == -1:
        return text, False
    return text[:start] + STANDARD_S4_NEW + text[end + 1:], True


def main():
    apply = "--apply" in sys.argv
    for rel, subs in PATCHES.items():
        try:
            src = open(rel, encoding="utf-8").read()
        except FileNotFoundError:
            print(f"  MISSING  {rel}")
            continue
        out = src
        hits = 0
        for old, new in subs:
            if old in out:
                out = out.replace(old, new, 1)
                hits += 1
            else:
                print(f"    ! pattern not found in {rel}: {old[:60]}…")
        if rel.endswith("Authoring Standard.md"):
            out, ok = patch_section(out)
            if ok:
                hits += 1
            else:
                print("    ! could not locate §4 block")
        print(f"  {'✓' if out != src else '·'} {hits} edit(s)  {rel}")
        if apply and out != src:
            open(rel, "w", encoding="utf-8").write(out)
    print(f"\n{'APPLIED' if apply else 'DRY RUN'}")
    if not apply:
        print("Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
