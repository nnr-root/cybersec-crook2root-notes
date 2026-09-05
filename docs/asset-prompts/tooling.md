---
title: "Asset Prompts — Tooling & Scripting"
tags:
  - tree/meta
  - type/reference
---

# Asset Prompts — Tooling & Scripting

One prompt per content note across Phase 3, ready to paste into **Nano Banana
Pro**. Sixty-six prompts: five language notes, twelve defensive-tool notes,
forty-four offensive-tool notes, and five tool-engineering notes. MOC and
category-index notes carry no diagram and are not listed.

## How to use this file

1. Paste the prompt body, then **append the shared style block** from §4.1 of
   [[Crook2Root Visual Identity]] verbatim. The style block is what makes the
   set look like one set; the body only says what to draw.
2. Generate, then **audit by measurement, not by eye** (rule 12). Every prompt
   ends with a **Check** line naming the one measurement that decides whether
   the asset is usable.
3. Run `docs/scripts/flatten.py` on the accepted still before committing
   (rule 9). For the notes marked **motion**, derive the GIF from the audited
   still with `docs/scripts/sweep.py` — never generate animation directly.
4. **The accent.** Tooling's domain colour is `#708090`, a muted slate — a
   weaker accent than Networking's cyan and, on the near-black ground, at risk
   of vanishing into the pale-grey line work. So each prompt names the accent
   in words as a **bright steel blue** (rule 1: never a hex value), which the
   model draws with real separation; remap it to `#708090` after generation.
   The audit adds one step for this domain: confirm the accented element is
   still separable from the line work after the remap, and if it is not,
   lighten toward the slate's bright tint rather than leaving an accent nobody
   can see.

## Why these look the way they do

Every diagram below is built from **rows** — a bar divided into fields, several
bars stacked, a line of strokes on one rule. That is rule 10: asked for a
divided bar the model returns an accurate pitch, and asked for a true
two-dimensional lattice it returns the wrong column count. Nothing here asks for
a lattice. Where two things must line up they are **one stroke** (rule 7); where
several panels are transformations of one another the prompt says so as a
transformation (rule 8) rather than describing each panel from scratch.

The through-line of the whole domain is that a tool's *mechanism* and its
*failure* are the same picture seen twice — a signature that matches one byte
sequence and misses its re-encoding, a walk that trusts a linked list a rootkit
unlinked, a filter that keeps the one fragment carrying the header. Each diagram
tries to be that single picture.

---

# Programming for Security

## Bash — `word-splitting-split.png`

*The claim: an unquoted expansion is torn into words by the shell; the quotes
are the only thing holding one argument together.*

```text
Two horizontal bars of equal total length stacked with a clear gap between
them. The upper bar is one continuous unbroken cell with a few faint evenly
spaced internal marks. The lower bar spans the same length but is divided into
several separate shorter cells with clear gaps between them, and each gap falls
exactly where the upper bar carries one of its faint marks. The lower divided
bar is bright steel blue; the upper continuous bar and everything else is pale
cool grey.
```

**Check:** the upper bar has zero real gaps; the lower bar's gaps sit on the
upper bar's faint marks. Count them and confirm alignment at 2x.

## Python — `gil-threads-vs-procs.png`

*The claim: threads share one interpreter lane and serialise through it;
processes run on their own lanes in true parallel.*

```text
On the left, several parallel horizontal lines of equal length converge so that
they all pass through a single narrow vertical slot and continue beyond it as
one merged line. On the right, the same number of parallel horizontal lines
each pass through their own separate vertical slot, one slot per line, and
remain parallel and separate beyond. The single shared slot on the left is
bright steel blue; every line and the right-hand slots are pale cool grey.
```

**Check:** the left group funnels through exactly one slot; the right group has
one slot per line. Count slots on each side.

## PowerShell — `execution-policy-porous.png`

*The deliberate break: Execution Policy is not a security boundary — the
documented bypasses run around its ends while it reports Restricted.*

```text
A single vertical barrier stands in the middle of the frame, not reaching the
top edge and not reaching the bottom edge. Several horizontal arrows approach it
from the left at different heights. One arrow meets the barrier head-on and
stops at it. The others pass above the barrier's top end or below its bottom end
and continue unbroken to the right edge. The arrows that get around the barrier
are bright steel blue; the barrier and the one stopped arrow are pale cool grey.
```

**Check:** exactly one arrow stops at the barrier; every other arrow clears one
of its two ends and reaches the right edge.

## C++ — `use-after-free-dangling.png`

*The deliberate break: the freed slot is reused, so a still-live pointer now
reads someone else's object — the pointer never moved, the ground under it did.*

```text
Two identical horizontal rows of equal cells stacked with a gap, and a single
arrow descending from above onto the same cell position in both rows. In the
upper row that target cell is filled with one hatch pattern. In the lower row
the identical target cell is filled with a clearly different hatch pattern while
every other cell in the row is unchanged from the upper row. The arrow and the
lower row's changed cell are bright steel blue; everything else is pale cool
grey.
```

**Check:** the arrow lands on the same column in both rows; only that one cell's
fill differs between the rows.

## Go — `goroutine-socket-exhaustion.png`

*The deliberate break: launching a goroutine per connection with no bound
exhausts file descriptors; a fixed worker pool holds the line.*

```text
On the left, a large number of short vertical strokes rise from a common
baseline and several of them push above a single horizontal ceiling line drawn
across the upper frame. On the right, the same number of strokes rise from the
baseline but are grouped so that only a small fixed number reach up to the
ceiling at once while the remaining strokes wait below a lower holding line and
none breach the ceiling. The strokes that breach the ceiling on the left are
bright steel blue; all other strokes and both lines are pale cool grey.
```

**Check:** the left group has strokes above the ceiling line; the right group
has none above it. Count breaches on each side.

---

# Defensive Tools

## Endpoint Telemetry Tools

### Sysmon — `lsass-read-event.png`

*The claim: a process opening a read handle into a protected process is the
single action Sysmon records as the tell, whatever delivered it.*

```text
A horizontal row of equal cells. From one cell near the left, a single long
arrow reaches across several neighbouring cells to touch the rightmost cell,
which is drawn taller and wider than the others. A small caret sits on the arrow
at the point where it meets the tall end cell. The reaching arrow and the caret
are bright steel blue; the cells are pale cool grey.
```

**Check:** exactly one arrow spans the row to the single oversized end cell, and
the caret sits at their meeting point.

### osquery — `snapshot-gap.png`

*The deliberate break: a scheduled snapshot samples at intervals, so a
short-lived process that lives and dies between two samples leaves no row.*

```text
A single long horizontal line with short vertical tick marks at regular even
intervals along its whole length. Between one adjacent pair of ticks sits a
short raised bracket, like a low doorway, that begins after the left tick and
ends before the right tick, touching neither. The raised bracket between the
ticks is bright steel blue; the line and ticks are pale cool grey.
```

**Check:** the bracket lies wholly between two ticks and touches neither. Measure
both gaps at 2x.

## Malware & Content Analysis Tools

### Volatility — `pslist-vs-psscan.png`

*The deliberate break: pslist walks the linked list a rootkit can unlink from;
psscan scans raw memory and finds the object the walk skipped.*

```text
Two horizontal rows stacked with a gap. The upper row is a series of equal cells
joined end to end by short connector strokes, except one cell whose connectors
on both sides are missing so it sits detached and slightly raised above the
line. The lower row shows every cell at the same horizontal positions as solid
blocks with no connectors between them, including a block directly beneath the
detached cell. The lower block beneath the detached cell is bright steel blue;
everything else is pale cool grey.
```

**Check:** the upper row has exactly one cell with broken connectors; the lower
row has a block at that same column, and it is the accented one.

### YARA — `packed-entropy-wall.png`

*The deliberate break: a packed section is high-entropy and hides its strings;
the same content unpacked shows them as discrete marks.*

```text
Two horizontal bars of equal size stacked with a gap. The upper bar contains a
few distinct, well-spaced short marks against an otherwise empty field. The
lower bar is filled edge to edge with an even, dense, uniform fine texture and
contains no distinct marks at all. The dense lower bar is bright steel blue; the
upper bar and its marks are pale cool grey.
```

**Check:** the upper bar has a small countable number of discrete marks; the
lower bar has none. Confirm the lower fill is uniform end to end.

### CyberChef — `peel-outermost-first.png`

*The deliberate break: layered obfuscation must be undone outside-in — each step
strips one wrapper and reveals a smaller inner payload.*

```text
A horizontal sequence of four bars decreasing in length from left to right. Each
bar starts at the same left edge as the one before it, so each successive bar is
the previous bar with a segment removed from its right end. The bars are stacked
with small vertical offsets so all four are visible at once, longest at the
back-left, shortest at the front-right. The shortest final bar on the right is
bright steel blue; the three longer bars are pale cool grey.
```

**Check:** each bar is shorter than the one before by a consistent step and all
share a left edge; the rightmost, shortest bar is accented.

## Network Detection & Monitoring Tools

### Snort — `signature-literal-miss.png`

*The deliberate break: a literal signature matches one byte sequence and misses
the re-encodings that carry the same effect.*

```text
Three horizontal bars stacked, each containing one short distinct notch cut into
its top edge at a different horizontal position. A separate small template shape
sits above the stack, aligned exactly over the notch of the top bar only, its
underside matching that notch's shape. The top bar's matched notch is bright
steel blue; the other two notches and the template are pale cool grey.
```

**Check:** the template aligns with exactly one bar's notch (the top one); the
other two notches sit at unmatched positions.

### Suricata — `handshake-gate.png`

*The deliberate break: an app-layer rule needs the parsed protocol, which needs
the handshake; a mid-stream flow has no buffer and the rule silently can't fire.*

```text
Two horizontal flow lines stacked with a gap. The upper line begins at the left
with three short ascending steps, then continues to the right as a bar carrying
several evenly spaced inspection tick marks along its length. The lower line has
no opening steps at all and continues as a plain bar with no tick marks. The
three opening steps on the upper line are bright steel blue; everything else is
pale cool grey.
```

**Check:** the upper line has the three-step opener and carries ticks; the lower
line has neither the steps nor any ticks.

### Zeek — `beacon-interval.png`

*The claim: a beacon is regularity, not payload — an even inter-connection
interval stands out where no signature would.*

```text
Two horizontal lines stacked with a gap, each carrying several short vertical
ticks. On the upper line the ticks are evenly spaced at one constant pitch along
the whole length. On the lower line the same number of ticks sit at visibly
varying gaps. The evenly spaced upper ticks are bright steel blue; the lower
ticks and both lines are pale cool grey.
```

**Check:** the upper tick gaps are equal within measurement; the lower gaps are
unequal. Measure the pitch of each row at 2x.

## Packet Analysis Tools

### Wireshark — `expert-info-inference.png`

*The deliberate break: a "previous segment not captured" flag is Wireshark's
inference about the frames it received — a capture gap, not a network event.*

```text
Two horizontal rows of equal blocks in sequence, stacked with a gap. The lower
row is identical to the upper row except that one block is absent, leaving a
gap in the sequence. A small caret sits above that gap, pointing down into it.
The caret above the gap is bright steel blue; both rows of blocks are pale cool
grey.
```

**Check:** the lower row is missing exactly one block relative to the upper row,
and the caret sits directly over that gap.

### tcpdump — `fragment-first-only.png`

*The deliberate break: only the first fragment carries the TCP header, so a
port filter passes it and silently drops every later fragment.*

```text
A single long bar on the left divided into three equal segments by two dividers,
feeding into a vertical gate line drawn across the middle of the frame. Beyond
the gate only the leftmost segment continues to the right edge; the other two
segments stop at the gate. The leftmost segment that passes the gate is bright
steel blue; the two stopped segments and the gate are pale cool grey.
```

**Check:** exactly one of the three segments passes the gate; the other two end
at it.

## SIEM & Detection Engineering Tools

### Sigma — `pipeline-remap.png`

*The claim: a processing pipeline re-expresses one abstract field against each
backend's schema — the field moves, it is not merely translated.*

```text
Three horizontal bars stacked with gaps, each divided into the same number of
cells. In the top bar one cell is filled solid at a fixed position. In each of
the two lower bars a single cell is filled solid, but at a different position
and a different width from the top bar and from each other. The three filled
cells are bright steel blue; every other cell is pale cool grey.
```

**Check:** the accented filled cell occupies a different column, and a different
width, in each of the three bars.

### Splunk Basics — `time-bound-buckets.png`

*The claim: a time range lets the engine discard whole buckets before opening
any of them — the bound is the primary filter.*

```text
A single horizontal row of equal blocks spanning the frame. A bracket above
spans only a small contiguous group of blocks near one end and drops a short
connector to each block in that group. Every block outside the bracket carries
one diagonal strike through it. The bracketed contiguous group is bright steel
blue; the struck-through outside blocks are pale cool grey.
```

**Check:** only the bracketed contiguous group is unstruck; every block outside
the bracket carries a strike.

---

# Offensive Tools

## Active Directory & Windows Attack Tools

### BloodHound — `attack-path-graph.png`

*The claim: BloodHound turns a mess of relationships into one continuous path
from a low-privilege foothold to Domain Admin.*

```text
A horizontal chain of small circles connected left to right by single arrows,
running the width of the frame. Two short dead-end stubs branch off downward
from two of the intermediate circles and end in smaller circles. The continuous
left-to-right chain of circles and arrows is bright steel blue; the two
downward stubs and their end circles are pale cool grey.
```

**Check:** one unbroken accented path runs end to end; the two stubs branch off
it and are not accented.

### Impacket — `dcsync-from-wire.png`

*The claim: Impacket speaks the protocols directly from the wire — one of its
tools pulls replication records with no agent on the target.*

```text
A single node on the left with several lines reaching rightward to separate
blocks stacked vertically on the right, each line at a distinct height. One line
— the one reaching the topmost block — carries several short cross-ticks along
its length, representing records returning along it. That tick-marked line and
the topmost block are bright steel blue; the other lines and blocks are pale
cool grey.
```

**Check:** exactly one of the fan-out lines carries return cross-ticks; it
reaches the single accented block.

### Mimikatz — `lsass-extract.png`

*The claim: Mimikatz reads the secrets the OS is holding straight out of
process memory and copies them out.*

```text
A large rectangle on the right divided into several internal cells by horizontal
dividers. From the left, a single arrow reaches in to touch one internal cell,
and a copy of that same cell is drawn detached out on the far left, joined to
the tail of the arrow. The reaching arrow and the detached copied cell are
bright steel blue; the rectangle and its other cells are pale cool grey.
```

**Check:** one internal cell has a matching detached copy outside the rectangle,
joined by the single arrow.

### NetExec — `credential-sweep.png`

*The claim: one credential swept across many hosts — breadth, where the finding
is the single host that accepts it.*

```text
A single token on the left with lines reaching to each block in a horizontal row
of equal blocks on the right, one line per block. One block in the row is filled
solid while every other block is outline only. The filled block and its line are
bright steel blue; the token, the other lines and the outline blocks are pale
cool grey.
```

**Check:** exactly one block in the row is filled; all blocks receive a line
from the single token.

### Responder — `llmnr-race.png`

*The deliberate break: Responder wins because it answers the broadcast query
faster than the legitimate server — the shorter path arrives first.*

```text
A single point on the left emits a short fan of lines spreading rightward, a
broadcast query. Two arrows return to that same point from the right: one short
and straight, one longer and drawn with a stepped, indirect route. The short
straight returning arrow is bright steel blue; the fan and the longer stepped
arrow are pale cool grey.
```

**Check:** two arrows return to the emitting point; the accented one is
measurably shorter and straighter than the other.

## Enumeration & Service Interaction Tools

### Gobuster — `wordlist-sweep.png`

*The claim: a fixed wordlist tried against a target — most paths bounce, a few
pass through.*

```text
A horizontal row of many short vertical strokes, all rising from a common
baseline to one shared horizontal line. A few of the strokes, scattered across
the row, continue past that shared line to a greater height. The strokes that
pass the line are bright steel blue; the strokes that stop at it and the line
itself are pale cool grey.
```

**Check:** most strokes stop at the shared line; a small minority pass it. Count
the ones that pass.

### Netcat — `bidirectional-pipe.png`

*The claim: netcat is a raw two-way pipe between two endpoints — data flows both
directions over one connection.*

```text
Two small squares, one at the left edge and one at the right edge, joined by a
single horizontal line across the frame. Along the upper half of the line short
ticks point rightward; along the lower half short ticks point leftward. The
connecting line is bright steel blue; the two end squares and the ticks are pale
cool grey.
```

**Check:** one line joins the two squares and carries ticks pointing in both
directions.

### dirsearch — `extension-expansion.png`

*The claim: dirsearch expands each wordlist entry into several extension
variants before it requests anything.*

```text
A vertical list of short horizontal strokes down the left side. From the right
end of each stroke a small fan of three sub-strokes extends further right, every
fan identical in shape and spread. One complete fan is bright steel blue; the
left strokes and the other fans are pale cool grey.
```

**Check:** each left stroke expands into the same number of sub-strokes; exactly
one fan is accented.

### enum4linux — `null-session-drawer.png`

*The claim: one null session against a host pulls several separate categories of
records out at once.*

```text
A single tall block on the left. From its right edge several separate stacked
lists of short horizontal rules extend to the right, each list at a distinct
height and of a different length. The source block and one of the extracted
lists are bright steel blue; the other lists are pale cool grey.
```

**Check:** one source block feeds several distinct extracted lists of differing
lengths.

### feroxbuster — `recursive-descent.png`

*The claim: a hit spawns a fresh sweep beneath it — recursion is the thing that
separates it from a flat fuzzer.*

```text
A horizontal row of vertical strokes rising to a common upper line, with one
stroke passing above that line. Directly beneath that one passing stroke, a
second, shorter horizontal row of vertical strokes begins, rising to a lower
common line, and one of those again passes above its line. The first-row stroke
that spawns the second row is bright steel blue; everything else is pale cool
grey.
```

**Check:** the accented first-row hit sits directly above the start of the
second row.

### ffuf — `fuzz-slot.png`

*The claim: ffuf marks one position in a request and substitutes each candidate
into that single slot, wherever it sits.*

```text
A single horizontal bar with one empty rectangular slot cut into it at a fixed
position along its length. To the left, a vertical stack of short tokens each
connects by a line to that one slot. The empty slot in the bar is bright steel
blue; the bar, the stack of tokens and their lines are pale cool grey.
```

**Check:** the bar has exactly one slot; every token in the stack points to it.

## Exploitation & Credential Testing Tools

### Hydra — `parallel-guess.png`

*The claim: Hydra drives many parallel attempts down one service until one
succeeds — depth against a single target.*

```text
Several horizontal arrows on the left, stacked at different heights, all
converging on a single tall block on the right. One arrow passes through the
block's face and out the other side; the rest stop at the face. The arrow that
passes through is bright steel blue; the block and the stopped arrows are pale
cool grey.
```

**Check:** many arrows hit one block; exactly one penetrates it.

### Metasploit Framework — `module-stack.png`

*The claim: an exploit is assembled from interchangeable modules — swap the
payload without touching the rest.*

```text
A vertical stack of several horizontal slabs aligned to a common width, forming
one clean column. One slab in the middle of the stack is drawn pulled out to the
side, offset from the column as if sliding out on rails, with a small gap where
it belongs. The offset slab is bright steel blue; the rest of the column is pale
cool grey.
```

**Check:** exactly one slab is offset from the otherwise aligned column, leaving
a gap at its position.

## Network Discovery Tools

### Nmap — `syn-scan-halfopen.png`

*The claim: a SYN scan never completes the handshake — it sends SYN, reads the
SYN-ACK, then tears down with a reset instead of the final ACK.*

```text
Two horizontal exchange diagrams stacked with a gap, each drawn between a left
point and a right point. The upper exchange has an arrow going right, then an
arrow coming left, then a short arrow going right that stops partway and ends in
a small perpendicular stub. The lower exchange has an arrow right, an arrow
left, then a full arrow going right that reaches the far point. The upper
exchange's third short stubbed arrow is bright steel blue; everything else is
pale cool grey.
```

**Check:** the upper exchange's third arrow is a short stub; the lower
exchange's third arrow reaches across to the far point.

### Masscan — `async-fire-forget.png`

*The claim: transmit and receive are decoupled — a dense outbound stream and a
separate, unrelated inbound trickle, which is how the rate gets so high.*

```text
Two horizontal lines stacked with a gap. The upper line carries many closely and
evenly spaced ticks along its whole length. The lower line carries only a few
sparse ticks at positions that do not line up with any on the upper line. The
dense even upper stream is bright steel blue; the sparse lower stream is pale
cool grey.
```

**Check:** the upper ticks are dense and evenly spaced; the lower ticks are
sparse and unaligned to the upper ones.

### RustScan — `batch-then-handoff.png`

*The claim: RustScan sweeps all ports fast, then hands the few open ones to a
second tool for the deep work.*

```text
A horizontal row of many short vertical strokes on the left, of which a few are
drawn taller than the rest. The taller strokes connect by converging lines to a
single block on the right. The taller strokes and their converging lines are
bright steel blue; the short strokes and the block are pale cool grey.
```

**Check:** only the taller strokes feed lines into the right-hand block; the
short strokes do not.

## OSINT & Reconnaissance Tools

### Amass — `subdomain-fan.png`

*The claim: Amass enumerates outward from one root name into a wide spread of
subdomains, some nesting a level deeper.*

```text
A single node at the left edge with many lines fanning rightward to a vertical
column of small end-marks. A few of those lines branch once more, near their
ends, into two shorter lines before their end-marks. The root node on the left
is bright steel blue; all the fanning lines and end-marks are pale cool grey.
```

**Check:** one root node, many leaf end-marks, and a few lines that branch a
second time.

### Shodan — `index-lookup.png`

*The claim: Shodan queries a pre-built index of already-scanned hosts — the
records exist before you ask, so you never send a packet to the target.*

```text
A horizontal row of equal record blocks, already drawn and complete. A query
bracket above the row spans several non-adjacent blocks and drops a short
connector down to each of the ones it selects. The selected non-adjacent blocks
are bright steel blue; the row and the bracket are pale cool grey.
```

**Check:** the query selects several non-adjacent blocks from a row that is
already complete before the bracket touches it.

### theHarvester — `aggregate-sources.png`

*The claim: theHarvester merges results from many separate public sources into
one consolidated list.*

```text
Several separate blocks stacked vertically on the left, each connected by a
single line to a common vertical list on the right. The consolidated list on the
right is bright steel blue; the source blocks and their lines are pale cool grey.
```

**Check:** several source blocks each feed one line into a single merged list.

## Password Cracking Tools

### Hashcat — `mask-keyspace.png`

*The claim: a mask defines the keyspace as the product of a candidate set at
each position.*

```text
A horizontal row of a few equal slots along a baseline. Above each slot stands a
vertical stack of short horizontal marks, the stacks differing in height from
slot to slot. One slot together with the stack above it is bright steel blue;
the other slots and stacks are pale cool grey.
```

**Check:** every slot carries its own stack of candidate marks; exactly one
slot-and-stack is accented.

### John the Ripper — `rules-mangle.png`

*The claim: mangling rules generate many variants from one base word by
appending and altering its end.*

```text
A single horizontal stroke on the left. To its right, several variant strokes
stacked, each the same base length as the original but with a small differing
appendage added at its right end. The original base stroke on the left is bright
steel blue; the variants are pale cool grey.
```

**Check:** every variant shares the base length and differs only in the trailing
appendage; the base stroke is accented.

### hash-identifier — `flat-candidates.png`

*The deliberate break: length and alphabet yield candidates, not certainty — so
every guess is offered with equal weight.*

```text
A single bar on the left connected by lines to several blocks stacked on the
right, every block the same size, drawn in outline only, none filled. The source
bar on the left is bright steel blue; the equal candidate blocks and their lines
are pale cool grey.
```

**Check:** the candidate blocks are all the same size and all unfilled — none is
singled out.

### name-that-hash — `ranked-candidates.png`

*The claim: name-that-hash improves on the flat list by ranking candidates by
confidence.*

```text
A single bar on the left connected by lines to a vertical column of blocks on
the right that decrease in size from top to bottom, the top block largest and
the bottom smallest. The largest top block is bright steel blue; the source bar,
the lines and the smaller blocks are pale cool grey.
```

**Check:** the right-hand blocks strictly decrease in size top to bottom; the
top, largest one is accented.

## Privilege Escalation Enumeration Tools

### LinPEAS — `checklist-sweep.png`

*The claim: LinPEAS runs a long battery of checks and raises the few that
matter.*

```text
A tall vertical column of short horizontal rules of equal length, evenly spaced.
A few of the rules, scattered down the column, carry a small raised marker at
their right end. The rules with end markers are bright steel blue; the rest are
pale cool grey.
```

**Check:** a small minority of rules carry the end marker; the marked rules are
the accented ones.

### WinPEAS — `grouped-checklist-sweep.png`

*The claim: the same battery approach on Windows, where the checks fall into
distinct groups.*

```text
A tall column of short horizontal rules of equal length, arranged in three
visually separated groups with clear gaps between the groups. Within one group
only, a few rules carry a small raised marker at their right end. The marked
rules are bright steel blue; every other rule is pale cool grey.
```

**Check:** the rules cluster into three separated groups; end markers appear in
exactly one group.

## Vulnerability Assessment Tools

### Nessus — `plugin-battery.png`

*The claim: a plugin-driven scanner probes one target with many checks and
ranks what it finds by severity.*

```text
A single block on the left. A vertical stack of horizontal probe lines reaches
from it across to a ranked column of blocks on the right whose sizes decrease
from top to bottom. The largest top finding block is bright steel blue; the
source block, the probe lines and the smaller findings are pale cool grey.
```

**Check:** the findings column decreases in size top to bottom; the largest is
accented.

### Nuclei — `template-match.png`

*The claim: a template matches when its shape fits a feature of the target;
otherwise it hovers, unmatched.*

```text
A horizontal target bar with a few distinct notches cut into its top edge at
different positions. Above the bar float several small template shapes; one
template's underside matches a notch exactly and is drawn seated down into it,
while the others hover above the bar unmatched. The seated matching template is
bright steel blue; the bar and the hovering templates are pale cool grey.
```

**Check:** exactly one template is seated in a notch; the rest hover clear of the
bar.

### OpenVAS — `feed-driven.png`

*The claim: an open feed continually adds new tests to the set the scanner runs.*

```text
A vertical column of stacked short horizontal rules on the right. A single line
enters from the left and adds several new rules to the bottom of the column, the
new rules drawn slightly inset from the left edge of the existing ones. The
newly added inset rules at the bottom are bright steel blue; the feed line and
the existing rules are pale cool grey.
```

**Check:** the accented rules sit at the bottom of the column, inset from the
rest, connected to the incoming feed line.

### SearchSploit — `offline-archive.png`

*The claim: a keyword search runs against a local, offline archive of exploit
entries.*

```text
A vertical stack of equal shelf rows on the right, each row with a small notch
on its left edge; a few of the rows share an identical notch shape. A bracket on
the left connects to exactly the rows whose notch matches. The matched rows are
bright steel blue; the other rows and the bracket are pale cool grey.
```

**Check:** only the rows whose left notch matches are connected to the bracket
and accented.

---

## Web Application Testing Tools

### Burp Suite — `intercept-proxy.png`

*The claim: Burp sits in the middle of the conversation and can hold a request
in flight — two legs meeting at a point that pauses.*

```text
Three points in a horizontal line, joined by two separate segments: a left
segment and a right segment meeting at the middle point. The left segment
arrives at the middle point with an arrowhead; the right segment leaves it
toward the right point. A small pause bracket, two short parallel uprights,
sits on the middle point. The pause bracket at the middle point is bright steel
blue; the two segments and the three points are pale cool grey.
```

**Check:** two distinct segments meet at the middle point, and that point alone
carries the pause bracket.

### Nikto — `known-issues-sweep.png`

*The claim: Nikto fires a fixed list of known-bad checks at a server — loud, and
a few of them land.*

```text
A single point on the left emitting a dense fan of many straight arrows toward a
tall block on the right. A few of the arrows land in small notches cut into the
block's left face; the rest strike the flat face and stop. The arrows that seat
in notches are bright steel blue; the fan and the block are pale cool grey.
```

**Check:** a dense fan reaches the block; only a few arrows seat in notches.

### OWASP ZAP — `spider-then-scan.png`

*The claim: ZAP crawls the app into a map first, then actively scans what the
crawl found.*

```text
On the left a single node fans into a small tree of end-marks. Each end-mark
connects by a horizontal line rightward to one rule in a vertical column of
probe rules on the right. The crawl's tree of end-marks on the left is bright
steel blue; the connecting lines and the probe column are pale cool grey.
```

**Check:** every crawl end-mark feeds exactly one probe rule; the tree is
accented.

### Postman — `request-response-pair.png`

*The claim: Postman organises structured requests into a saved collection and
pairs each with its response.*

```text
A vertical stack of request bars on the left, each carrying one small filled
parameter cell. One bar in the stack connects by a line across to a single
response bar on the right. The connected request bar and its response bar are
bright steel blue; the other request bars are pale cool grey.
```

**Check:** exactly one request bar links across to one response bar; the pair is
accented.

### SQLmap — `boolean-oracle.png`

*The claim: blind boolean injection reads data one bit at a time — identical
queries whose only difference is the length of what comes back.*

```text
Two identical horizontal query bars stacked with a gap, each with a return bar
extending to its right. Although the two query bars are exactly the same length,
the upper return bar is long and the lower return bar is short. The two
differing return bars are bright steel blue; the identical query bars are pale
cool grey.
```

**Check:** the two query bars are the same length; the two return bars differ in
length, and the return bars are accented.

### WPScan — `plugin-surface.png`

*The claim: the WordPress core is small; the plugin and theme sprawl is the
attack surface.*

```text
A single small block on the left, then a long horizontal row of many small
blocks of varying sizes extending to the right edge. A few of the row blocks
carry a small raised marker on top. The marked plugin blocks in the row are
bright steel blue; the small core block on the left and the unmarked row blocks
are pale cool grey.
```

**Check:** one small core block on the left, a long row of many varied blocks to
the right, a few of them marked and accented.

### curl — `raw-request-fields.png`

*The claim: curl gives you direct control over every field of the request.*

```text
A single long horizontal bar divided into several segments of differing widths
by clear dividers. One of the segments is drawn lifted out of the bar and set
just above its slot, to show it can be edited and replaced, with a gap where it
belongs. The lifted, editable segment is bright steel blue; the rest of the bar
is pale cool grey.
```

**Check:** the bar has several distinct segments; exactly one is shown lifted out
of its slot.

## Web-Based Tools & References

### Aperisolve — `stego-layer-stack.png`

*The claim: Aperisolve runs many stego analyses at once, pulling the image into
layers so a hidden one stands out.*

```text
A vertical stack of several thin horizontal layers, slightly offset from each
other like a fanned deck of cards. One layer in the middle of the stack carries
a small distinct mark that none of the other layers have. The marked layer is
bright steel blue; the other layers are pale cool grey.
```

**Check:** several fanned layers; exactly one bears a mark, and it is the
accented one.

### CrackStation — `lookup-table.png`

*The claim: a precomputed table maps a hash straight to its plaintext — a lookup,
not a crack.*

```text
A vertical list of paired cells, each pair a left cell joined by a short bridge
to a right cell. One pair's bridge is drawn solid and complete; the bridges of
the other pairs are faint and broken. The one complete pair with its solid
bridge is bright steel blue; the faint pairs are pale cool grey.
```

**Check:** exactly one pair has a complete bridge among otherwise broken ones.

### GTFOBins — `binary-breakout.png`

*The claim: a legitimate binary is coaxed into stepping outside its intended
confinement.*

```text
A rectangle containing one short horizontal line that runs along inside it. From
the right end of that line a second line turns and crosses the rectangle's
boundary to continue outside it. The line that crosses the boundary to the
outside is bright steel blue; the rectangle and the internal line are pale cool
grey.
```

**Check:** one line stays inside the rectangle; exactly one line crosses its
boundary to the outside.

### LOLBAS — `living-off-the-land.png`

*The claim: a native system binary does something extra and hostile while
looking exactly like its neighbours.*

```text
A horizontal row of identical blocks, evenly spaced. From the underside of one
block a small extra stroke descends that none of the other blocks have; the
block itself is drawn identically to the rest. The block with the descending
extra stroke is bright steel blue; the other blocks are pale cool grey.
```

**Check:** all blocks are identical except one, which has a single descending
stroke beneath it.

### revshells.com — `reverse-callback.png`

*The claim: a reverse shell has the target dial out to the attacker — the
opposite direction from a bind shell.*

```text
Two horizontal arrows stacked with a gap, each between a left point and a right
point. The upper arrow points from the left point to the right point. The lower
arrow points from the right point back to the left point. The lower,
right-to-left arrow is bright steel blue; the upper arrow and both points are
pale cool grey.
```

**Check:** the two arrows point in opposite directions; the accented one runs
right to left.

## Wireless Tools

### Kismet — `passive-channel-sweep.png`

*The claim: Kismet listens across channels and transmits nothing — every mark it
shows was received, never sent.*

```text
A vertical stack of horizontal channel lines. Short blips sit on several of the
lines at scattered positions along them. Nothing originates from the left edge —
there is no source point and no outbound stroke anywhere. The channel line
carrying the most blips is bright steel blue; the other lines and blips are pale
cool grey.
```

**Check:** all marks sit on the channel lines; nothing emanates from a source
point at the edge.

### aircrack-ng — `handshake-capture.png`

*The claim: capture the four-way handshake, then crack it offline against a
candidate list.*

```text
On the left, a vertical exchange of four short arrows alternating between an
upper point and a lower point (a four-step handshake). A bracket encloses all
four arrows and connects rightward to a stack of candidate strokes. The
four-arrow handshake inside the bracket is bright steel blue; the bracket and
the candidate stack are pale cool grey.
```

**Check:** exactly four alternating arrows sit inside the capture bracket.

### hcxtools — `pmkid-single-frame.png`

*The claim: the PMKID attack needs a single frame from the AP — no client, no
full handshake.*

```text
Two horizontal exchange diagrams stacked with a gap, each between a left point
and a right point. The upper diagram shows four alternating arrows between the
points. The lower diagram shows a single arrow from the left point to the right
point and nothing else. The single lower arrow is bright steel blue; the upper
four-arrow exchange is pale cool grey.
```

**Check:** the upper diagram has four arrows; the lower has exactly one.

---

# Writing Your Own Tools

## Building Network Scanners — `probe-timeout-bound.png`

*The claim: a probe must be bounded by a timeout, or a filtered port hangs the
scan forever.*

```text
Two horizontal probe lines stacked with a gap, each starting from a left point
and heading right. The upper line reaches a point partway across and ends there
at a short perpendicular cross-bar. The lower line passes that same point and
continues unbroken all the way to the right edge with no cross-bar. The upper
line's terminating cross-bar is bright steel blue; both lines otherwise are pale
cool grey.
```

**Check:** the upper line ends at a cross-bar at a defined point; the lower line
runs off the right edge with no terminator.

## Command & Control Design Principles — `jitter-spread.png`

*The deliberate break: a fixed check-in interval is a metronome a defender
catches; jitter widens the spread so the rhythm disappears.*

```text
Two horizontal lines stacked with a gap, each carrying several short vertical
ticks. On the upper line the ticks are evenly spaced at one constant pitch. On
the lower line the same number of ticks sit at clearly varying gaps around the
same average spacing. The unevenly spaced lower ticks are bright steel blue; the
even upper ticks and both lines are pale cool grey.
```

**Check:** the upper gaps are equal; the lower gaps are unequal, and the lower,
jittered ticks are the accented ones.

## Hashsmith Tool Architecture — `encode-vs-hash.png`

*The claim: an encoding is reversible and a hash is one-way — the whole design
refuses to conflate them.*

```text
Two horizontal pairs stacked with a gap. In the upper pair two equal bars are
joined by a double-headed arrow pointing both ways between them. In the lower
pair a longer bar joins by a single one-way arrow to a shorter fixed-width bar,
with no return arrow. The lower one-way arrow is bright steel blue; the upper
double-headed arrow and all bars are pale cool grey.
```

**Check:** the upper arrow has heads at both ends; the lower arrow has one head
and points to a shorter bar.

## Security Tool Architecture & Design Patterns — `pure-core-edges.png`

*The claim: the value is a pure core with no I/O, reached only through thin
swappable edges.*

```text
A central block sitting on a horizontal line, flanked by one thin block on its
left and one thin block on its right, each joined to the centre by a single
short link. External arrows arrive at the outer thin blocks only; no external
arrow touches the central block directly. The central core block is bright steel
blue; the two thin edge blocks and the external arrows are pale cool grey.
```

**Check:** every external arrow terminates on a flanking block; none reaches the
centre except through a link.

## ShadowStep Tool Architecture — `remote-immutable-audit.png`

*The deliberate break: deleting a local log leaves the remote copy intact, and
the gap it leaves is itself the signal.*

```text
Two horizontal rows of equal entry blocks stacked with a gap. The upper row has
one block missing, leaving a gap in its sequence. The lower row is complete with
no gap. A caret sits above the gap in the upper row and a line drops from it
straight down to the intact block directly below in the lower row. The intact
lower block beneath the gap is bright steel blue; both rows and the caret are
pale cool grey.
```

**Check:** the upper row is missing exactly one block; the lower row is complete;
the accented block sits directly beneath the gap.

---

*Sixty-six prompts — the complete Phase 3 (Tooling & Scripting) content set.
Generate, audit by the Check line, flatten, and remap the accent from bright
steel blue to `#708090`, confirming separability after the remap.*
