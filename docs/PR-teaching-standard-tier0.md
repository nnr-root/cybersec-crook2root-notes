## Summary

Rebuilds the corpus against an evidence-based teaching standard, and puts all 302
notes on one shared lab topology. 21 commits, 347 notes touched, both gates green.

Three things happened that were not in the original plan, and they are the parts
most worth reviewing.

## 1. Three of my own metrics were wrong, and are corrected in-repo

Each drove a recommendation. Each was a regex classifying prose, and each got the
direction right and the magnitude badly wrong — always alarming.

| Claim | Real | Why it was wrong |
|:--|:--|:--|
| 81 hedge words to purge | **1** | "Trivially forged" is attacker cost, not condescension |
| 230 notes with unexplained failures | **4** | Matched Mermaid labels, C source, `Failed : 0` from a success report |
| 280 notes with a buried cold open | **25** | Ratio penalised short notes; ignored our own Mermaid-first visual standard |

The structural counts were exact — 273 generic headings, 1,624 numbered task
headings, 766 IPv4 literals — because they matched unambiguous things.
`docs/Crook2Root Teaching Standard.md` §6a and §6b record both corrections.

## 2. Real defects found and fixed

- **Six routable public addresses** removed. Four were live third-party hosts;
  two (`185.22.11.4`, `81.143.211.90`) were C2 destinations *in notes teaching
  readers to spot C2*. Now structurally impossible — the gate rejects anything
  outside the reserved documentation ranges.
- **Two arithmetic errors.** VLSM free space was "roughly 380"; `.164`–`.255`
  across an octet boundary is **348**. And a longest-prefix example whose
  destination stopped matching its own route when the ladder moved.
- **Two orphaned visual references** left by the image purge: `CPU, Assembly & the
  ABI` described "the top bar / the grid / the right-hand panel" of a deleted
  figure, and `Suricata` said "on the left of the diagram" while containing zero
  visuals. Both repaired; Suricata's diagram authored.
- **A fabricated tool** (`Hashsmith CLI` — invented install command, version and
  output) removed in the Cryptography rebuild.

## 3. The Thread

One topology (Meridian Freight), every address from a reserved range: `.test` per
RFC 6761, TEST-NET-1/2/3 per RFC 5737, MACs from the RFC 7042 documentation block,
IPv6 from RFC 3849. **12 notes carry declared exemptions**, each with a written
reason the gate reads — a bare address is an error, so exemptions cannot become a
silent opt-out. Every exemption is load-bearing: the RFC 1918 range definitions,
the 802.1X PAE group address, real vendor OUIs used for rogue-AP detection, and
reproductions the reader builds on their own machine.

## Review guidance

Most of the diff is mechanical. Two files carry **recomputed arithmetic** rather
than substitution and are where review is most valuable:

- `Networking/Addressing & Subnetting/VLSM & Route Summarization.md` — every
  subnet boundary re-derived and verified with Python's `ipaddress`; the binary
  bit table recomputed (a string replace would have left it teaching the wrong
  bits under a heading that says "22 identical bits").
- `Networking/Routing & the Network Layer/IP Forwarding & the Routing Table.md` —
  all four longest-prefix resolutions recomputed.

## Not done

- **The Cold Open** — 25 genuine candidates, theory-heavy openings rather than
  defects. Optional quality work.
- **`verified:` dates** — 294 notes flagged. Deliberately **not** backfilled: a
  date nobody earned converts an honest gap into a false claim, on the exact axis
  where this repo beats TryHackMe and HackTheBox.
- **One Pre-Question** — 129 notes. Authoring.

## Gates

`ci-check.py` and `pedagogy-check.py` both at 0 errors, run on every commit via
`.githooks/pre-commit` (`git config core.hooksPath .githooks`).
