# Full-corpus retrofit — batch execution plan

Live counts. `pedagogy-check.py --warnings` is the authority; the numbers below
were taken at commit `545300c`.

## What the retrofit actually is

Three passes, applied together per note so each note is touched once:

1. **The Thread** — move host/network references onto Meridian, subject to the
   §5b exemptions in the Lab Topology.
2. **The Autopsy** — after every error output, a paragraph naming which component
   rejected it, at which stage, and what it was checking for.
3. **The Cold Open** — where the note buries its first evidence, restructure the
   opening onto an artifact.

## Measured backlog

| Pass | Notes | Notes not already compliant |
|:--|--:|--:|
| The Thread | 71 | 205 addresses |
| The Autopsy | 46 | gate-flagged; true figure is higher (see below) |
| **Union of the two** | **107** | the real per-note work queue |
| The Cold Open | 280 | authoring, tracked separately |
| One Pre-Question | 129 | folds into the Cold Open pass |

**179 of 302 notes name no host at all** — most of Cryptography, most of OS
Internals, the conceptual OffSec notes. They need nothing from The Thread.

> The Autopsy figure is a floor, not a score. The gate looks for a causal marker
> in the two paragraphs after an error block, so it passes notes that name a cause
> loosely. Expect roughly 3–4× that number on manual review.

## Batch order

Networking first — it holds the most Thread work, it is where the topology has to
prove itself, and every other branch references its vocabulary. Tooling last of
the large branches: its 62 thin leaves need depth more than they need retrofit,
and that is a separate job.

| # | Batch | Notes | Passes | Commit |
|--:|:--|--:|:--|:--|
| 1 | Networking / Switching & the Link Layer | 3 | Thread, Autopsy | `feat(thread): networking — link layer` |
| 2 | Networking / Addressing & Subnetting | 5 | Thread (§5c arithmetic), Autopsy | `feat(thread): networking — addressing` |
| 3 | Networking / Routing & the Network Layer | 5 | Thread, Autopsy | `feat(thread): networking — routing` |
| 4 | Networking / Transport Layer & Sockets | 6 | Thread, Autopsy | `feat(thread): networking — transport` |
| 5 | Networking / Core Network Services | 3 | Thread, Autopsy | `feat(thread): networking — core services` |
| 6 | Networking / Network Foundations | 6 | Thread, Autopsy | `feat(thread): networking — foundations` |
| 7 | Networking / Analysis, Security Arch, Web, Wireless | 10 | Thread, Autopsy | `feat(thread): networking — remainder` |
| 8 | OS Internals / Linux | 7 | Thread, Autopsy | `feat(thread): os internals — linux` |
| 9 | OS Internals / Windows + macOS | 8 | Thread, Autopsy | `feat(thread): os internals — windows, macos` |
| 10 | Cryptography (2 notes) + AppSec + DefSec | 4 | Thread, Autopsy | `feat(thread): crypto, appsec, defsec` |
| 11 | OffSec / Penetration Testing — recon & enumeration | ~8 | Thread, Autopsy | `feat(thread): offsec — recon` |
| 12 | OffSec / Penetration Testing — exploitation & AD | ~9 | Thread, Autopsy | `feat(thread): offsec — exploitation` |
| 13 | OffSec / Penetration Testing — post-exploitation & reporting | ~8 | Thread, Autopsy | `feat(thread): offsec — post-exploitation` |
| 14 | OffSec / Red Team, Social Eng, Exploit Dev | 5 | Thread, Autopsy | `feat(thread): offsec — red team` |
| 15 | Tooling / Offensive Tools | ~12 | Thread, Autopsy | `feat(thread): tooling — offensive` |
| 16 | Tooling / Defensive Tools + Programming | ~8 | Thread, Autopsy | `feat(thread): tooling — defensive` |

Sixteen batches, 3–12 notes each. One commit per batch, so any batch can be
reviewed or reverted alone.

## Per-batch procedure

1. `python3 docs/scripts/pedagogy-check.py --warnings | grep '<branch>'` — the queue.
2. For each note: check every address against Lab Topology §5b **before** rewriting.
   A protected value rewritten is a worse defect than a scenery value left alone.
3. Rewrite scenery addresses onto Meridian. Where a hex dump encodes an address,
   recompute the bytes — do not substitute strings.
4. Add the Autopsy paragraph after each error output.
5. Re-run both gates. Both must be at 0 errors.
6. Commit the batch alone.

## Verification per batch

- `ci-check.py` and `pedagogy-check.py` both at 0 errors.
- Off-Thread count for the branch is 0, or every remaining address is annotated
  as exempt.
- `git diff --stat` touches only that batch's notes.

## Known hazards

**Hex dumps encode addresses.** `Ethernet & Frame Structure` contains
`0a63 0001` — that is 10.99.0.1 written as bytes. A find-and-replace on the
dotted form silently desynchronises the dump from the prose. Every note with a
hex dump needs the bytes recomputed by hand.

**The arithmetic notes are not substitutions.** `VLSM & Route Summarization` (34
addresses) and `Subnetting & CIDR` (27) teach relationships between prefixes.
They move onto `10.10.40.0/22` per §5c only by re-deriving each worked example.
Budget these two as a batch of their own if batch 2 runs long.

**Load-bearing MACs.** Any note teaching the locally-administered bit, OUI
structure or broadcast addressing has MACs that cannot move to `00:00:5E:…`.
The Ethernet veth demonstration is the worked precedent in §5b.

**The Cold Open is not in these batches.** 280 notes open with a median 358 words
before their first evidence. That is authoring, one note at a time, and folding it
into the Thread batches would make each batch unreviewable. It runs as its own
pass after the Thread retrofit lands.
