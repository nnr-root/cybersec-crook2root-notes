---
title: "Asset Prompts — Networking"
tags:
  - tree/meta
  - type/reference
---

# Asset Prompts — Networking

One prompt per content note, ready to paste into **Nano Banana Pro**. The
Switching & the Link Layer branch is already generated and embedded and is not
repeated here; this covers the remaining nine branches.

## How to use this file

1. Paste the prompt body, then **append the shared style block** from
   §4.1 of [[Crook2Root Visual Identity]] verbatim. The style block is what
   makes fifty assets look like one set; the body only says what to draw.
2. Generate, then **audit by measurement, not by eye** (rule 12). Every prompt
   below ends with a **Check** line naming the one measurement that decides
   whether the asset is usable.
3. Run `docs/scripts/flatten.py` on the accepted still before committing
   (rule 9). For the notes marked **motion**, derive the GIF from the audited
   still with `docs/scripts/sweep.py` — never generate animation directly.
4. Colour is named in words, never as a hex value (rule 1). Remap the accent to
   `#42D4F4` after generation; everything else stays pale cool grey.

## Why these look the way they do

Every diagram below is built from **rows** — a bar divided into fields, several
bars stacked, a line of strokes standing on one rule. That is rule 10: asked for
a divided bar the model returns a 0.5px-accurate pitch, and asked for a true
two-dimensional lattice it returns the wrong number of columns at 20% spread.
Nothing here asks for a lattice.

Where two things must line up, they are **one stroke** (rule 7) — a divider that
continues upward and ends in a point is an arrow that cannot miss its divider,
because there is nothing to miss. Where several panels are transformations of
one another, the prompt says so as a transformation (rule 8) rather than
describing each panel separately.

---

# Network Foundations

## Network Types & Topologies — `broadcast-domain-edge.png`

*The note's claim: hosts in one broadcast domain reach each other directly;
hosts across a router do not. The arc is the domain.*

```text
A single wide horizontal bar spanning the frame, divided into two regions of
equal width by one tall vertical stroke that extends well above and well below
the bar. Both regions are subdivided into the same number of equal cells by
short vertical dividers that sit inside the bar only. A continuous shallow arc
rises from the top edge of the bar at the far left, passes over every divider
in the left region, and returns to the top edge of the bar at the tall stroke,
touching each divider it passes. The right region carries no arc at all;
instead one straight horizontal line leaves the tall stroke at the same height
the arc reached and stops at the first divider it meets. The tall vertical
stroke is bright pale cyan; everything else is pale cool grey.
```

**Check:** the arc must touch every divider in the left region and must not
cross the tall stroke. Crop at 2× and count contact points.

## The OSI Model — `quic-spans-layers.png`

*The case that ends the argument: QUIC occupies four bands at once.*

```text
Seven identical horizontal bars stacked one above another with an equal narrow
gap between each, all the same width, filling the centre of the frame. A single
tall rounded rectangle stands vertically across the right third of the stack,
its lower edge level with the lower edge of the fourth bar counting up from the
lowest, its upper edge level with the top edge of the highest bar, so that it
overlaps four bars and leaves the three lowest untouched. The rounded rectangle
is drawn in outline only and is bright pale cyan; the seven bars and every
other line are pale cool grey.
```

**Check:** the rounded rectangle must span exactly four bars. Measure its top
and bottom edge against the bar boundaries in pixels.

## The TCP-IP Model — `ip-hourglass.png`

*The narrow waist: many link technologies below, many applications above, one
protocol between.*

```text
A wide horizontal bar of modest height sits alone across the centre of the
frame. From its upper edge a fan of straight lines spreads upward and outward,
each ending at a small open square, the squares arranged along a wide arc near
the top of the frame. From its lower edge a matching fan spreads downward and
outward to a second row of small open squares near the bottom. The upper and
lower fans have the same number of lines and mirror each other about the
horizontal bar. The central bar is bright pale cyan; the fans and squares are
pale cool grey.
```

**Check:** the two fans must have equal line counts and mirror about the bar.
Count lines above and below.

## Encapsulation & Protocol Data Units — `frame-overhead-proportional.png`

*158 bytes leave the card to carry 100. The widths carry the whole lesson.*

```text
One single horizontal bar spanning almost the full width of the frame, divided
along its length into five segments by four vertical dividers. Reading from the
left edge, the first segment is narrow, the second is wider than the first, the
third is exactly as wide as the second, the fourth is very much the widest and
is about five times the width of the second, and the fifth is the narrowest of
all and about a quarter of the first. Every divider runs the full height of the
bar. The fourth segment is filled with a bright pale cyan tone; the four others
are empty with pale cool grey outlines.
```

**Check:** measure the five segment widths and confirm the ratio is close to
14 : 20 : 20 : 100 : 4. The fourth segment must be visibly larger than the other
four combined but not overwhelmingly so — that near-balance is the teaching.

## Network Devices & Traffic Paths — `router-rewrites-outer.png`

*The same packet either side of a router: both outer fields replaced, every
inner field untouched.*

```text
Two identical horizontal bars, one directly above the other with a clear gap
between them, the same width and aligned at both ends. Each bar is divided
along its length into five segments by four vertical dividers placed at exactly
the same positions in both bars. In the upper bar all five segments are empty
outlines. The lower bar is the upper bar with only its first and last segments
changed: those two are filled with a dense diagonal hatch, and its three middle
segments remain empty outlines identical to the ones above them. A short
vertical arrow points downward from the upper bar to the lower bar in the space
between them, positioned at the centre. The two hatched segments are bright
pale cyan; everything else is pale cool grey.
```

**Check:** the four dividers must sit at identical x-positions in both bars.
Read the divider coordinates in both rows and compare — a shift of more than a
few pixels makes the diagram say the opposite of what it means.

## Reachability Testing & ICMP — `silent-hop.png`

*Asterisks at a hop mean that hop did not reply, not that traffic stopped.*

```text
One continuous horizontal line runs the full width of the frame at mid-height.
Standing on that line at even intervals is a row of short vertical strokes, all
the same length, each rising above the line and ending in a small horizontal
crossbar. One stroke, positioned third from the left, is the exception: it
descends below the line instead of rising, and ends without a crossbar. The
horizontal line continues unbroken past every stroke including that one, and
extends beyond the last stroke to the right edge of the frame. The third stroke
is bright pale cyan; the line and all other strokes are pale cool grey.
```

**Check:** the horizontal line must be unbroken through the third stroke. A gap
there would teach the exact misreading the note exists to correct.

---

# Addressing & Subnetting

## IPv4 Addressing — `octet-boundary-illusion.png`

*A prefix that does not land on an octet boundary is where beginners' intuition
fails.*

```text
Two identical horizontal bars, one above the other, both spanning the frame and
aligned at both ends. Each bar is divided into four equal segments by three tall
dividers that rise above the bar and end in points, and each of those four
segments is further divided into eight small equal cells by short dividers
sitting inside the bar only. In the upper bar a heavy vertical rule falls
exactly on the second tall pointed divider. In the lower bar the heavy vertical
rule falls inside the third segment, between its third and fourth small cells,
where no tall divider stands. Both heavy rules are bright pale cyan; every other
line is pale cool grey.
```

**Check:** count the small cells — there must be eight in every segment, thirty
two across each bar. Then confirm the lower heavy rule sits between cells rather
than on a divider.

## Subnetting & CIDR — `prefix-slides.png`

*Moving the prefix one bit doubles the networks and halves the hosts.*

```text
Three horizontal bars of identical width stacked one above another with equal
gaps. Every bar is divided into the same number of small equal cells along its
whole length. In the topmost bar a single heavy vertical rule stands at one
quarter of the way along; in the middle bar the same rule stands one cell
further right; in the lowest bar one cell further right again. In each bar the
portion to the left of its heavy rule is filled with a solid tone and the
portion to the right is left empty. The three heavy rules are bright pale cyan;
every other line is pale cool grey.
```

**Check:** the three heavy rules must sit exactly one cell apart, and the filled
region must start at the left edge and end at the rule in every bar. Measure the
rule positions; a drift of half a cell destroys the point.

## VLSM & Route Summarization — `summarise-to-common-prefix.png`

*Four adjacent blocks share leading bits and collapse into one.*

```text
Four short horizontal bars of equal length stacked one above another with equal
gaps, all aligned at their left edges, occupying the upper half of the frame.
Each bar is divided into small equal cells along its length. Below them, in the
lower half of the frame, sits a fifth bar of the same length and cell size,
aligned to the same left edge. One heavy vertical rule crosses all five bars at
the same horizontal position, about two thirds of the way along, drawn as a
single continuous stroke that passes through every bar and the gaps between
them. To the left of that rule every cell in all five bars is filled with a
solid tone; to the right of it every cell is empty. The single continuous rule
is bright pale cyan; every other line is pale cool grey.
```

**Check:** the heavy rule must be one unbroken stroke through all five bars —
that is what makes the shared prefix visible. If it is drawn as five separate
segments they will not align, and the diagram fails.

## IPv6 Addressing — `address-doubles.png`

*The address is four times as long, and the space is not four times as large.*

```text
Two horizontal bars, one above the other, aligned at their left edges only. The
upper bar is short, occupying about a quarter of the frame width, and is divided
into four equal segments by three vertical dividers. The lower bar is exactly
four times the length of the upper bar, running to the right edge of the frame,
and is divided into sixteen equal segments by fifteen vertical dividers, each
segment therefore the same width as those in the bar above. A single horizontal
dimension line with a short vertical tick at each end runs beneath the lower bar
across its full length. The lower bar's outline is bright pale cyan; the upper
bar, the dividers and the dimension line are pale cool grey.
```

**Check:** measure both bars. The lower must be four times the upper to within a
few pixels, and every segment in both bars must be the same width as every
other.

## Address Assignment & DHCP — `lease-race.png`

*Two servers answer; the client takes the first reply.*

```text
One continuous horizontal line runs the full width of the frame at mid-height,
with a small open square sitting on it at the far left. Two straight lines leave
that square and travel to the right, one rising gently above the horizontal line
and one falling gently below it, each ending in a small open square of its own
near the right edge. From each of those two squares a return line travels back
toward the left, and the two return lines converge on a single point on the
horizontal line, close to the left square but not touching it. The return line
that arrives from below reaches the convergence point along a visibly shorter
path than the one from above. The lower outbound line, its square and its
shorter return are bright pale cyan; everything else is pale cool grey.
```

**Check:** the two return paths must meet at one point, and the cyan path must
be measurably shorter end to end. Trace both and compare lengths.

## NAT & Address Translation — `port-multiplex.png`

*Many inside conversations, one outside address, kept apart by port.*

```text
A row of small open squares stands in a vertical column at the left of the
frame. From each square a single straight line travels rightward and all of
those lines converge into one short horizontal bar standing alone at the centre
of the frame. From the right edge of that bar a single line continues to the
right edge of the frame. The central bar is divided along its length into as
many small equal cells as there are squares in the left column, and each
converging line meets the bar at the left edge of its own cell, in the same
top-to-bottom order as the squares. The central bar is bright pale cyan;
everything else is pale cool grey.
```

**Check:** count the cells in the central bar against the squares in the column
— they must match exactly. This is the one prompt here that asks two objects to
agree, so it is the one most likely to need a second generation.

---

# Routing & the Network Layer

## IP Forwarding & the Routing Table — `longest-prefix-ladder.png`

*Four routes match; the most specific wins.*

```text
Four horizontal bars stacked one above another with equal gaps, all aligned at
their left edges and all of the same total length, each divided into small equal
cells along its length. Reading from the top bar downward, the filled portion
starting at the left edge grows longer in each successive bar: the topmost has
no filled cells at all, the next has a short run, the next a longer run, and the
lowest is filled almost to its right end. A single heavy vertical rule crosses
all four bars as one continuous stroke at a position just beyond the end of the
lowest bar's filled run. The lowest bar's filled run is bright pale cyan; the
filled runs in the bars above it and every outline are pale cool grey.
```

**Check:** the filled runs must increase strictly downward, and the continuous
rule must sit to the right of all four. Measure each run's end coordinate.

## Static Routing & Default Gateways — `route-without-nexthop.png`

*The route resolves perfectly and the next hop does not answer.*

```text
One horizontal line runs from the left edge of the frame to a small open square
at the centre, and continues from the right side of that square toward the right
edge, where it stops short of the edge and ends in a small open circle. A second
horizontal line, drawn beneath the first and parallel to it, runs from the left
edge all the way to the right edge without interruption, passing below both the
square and the circle. The upper line is broken by a short clean gap immediately
before it reaches the circle. The circle and the gap are bright pale cyan; every
other line is pale cool grey.
```

**Check:** the gap must sit between the square and the circle, not elsewhere,
and the lower line must be genuinely unbroken. Both are single-measurement
checks at 2×.

## Interior Gateway Protocols — `count-to-infinity-climb.png`

*The numbers climb by two every two rounds while a loop runs underneath.*

```text
Three horizontal lines of equal length stacked one above another with equal
gaps, spanning the frame. Standing on each line at even intervals is a row of
short vertical strokes, one stroke per interval, all rows sharing the same
interval spacing so the strokes form aligned columns down the frame. Within each
row the strokes grow taller from left to right in even increments. Beneath the
lowest line, two curved arrows sit side by side between the second and third
columns, one arcing left to right and the other arcing right to left, their
heads meeting the strokes they point at as continuations of those strokes rather
than as separate marks. The two curved arrows are bright pale cyan; every line
and stroke is pale cool grey.
```

**Check:** the strokes must grow monotonically left to right in every row.
Measure stroke heights across one row; an out-of-order stroke reverses the
meaning.

## BGP & Internet Routing — `more-specific-wins.png`

*A longer prefix beats a shorter one regardless of who announced it.*

```text
Two horizontal bars, one directly above the other, aligned at their left edges.
The upper bar is long, running most of the frame width, and is drawn as an empty
outline. The lower bar is exactly half the length of the upper bar, starts at
the same left edge, and is filled with a solid tone. A single continuous
vertical stroke rises from the right end of the lower bar, crosses the upper
bar, and continues above it, ending in a point. The filled lower bar and the
rising stroke are bright pale cyan; the upper bar is pale cool grey.
```

**Check:** the lower bar must be half the upper to within a few pixels, and the
rising stroke must start exactly at its right end — that is why it is described
as one stroke rising from the bar rather than as an arrow placed near it.

## First-Hop Redundancy & Gateway Failover — `virtual-address-handover.png`

*Two real routers, one claimed address, and the host never notices.*

```text
Two small open squares sit side by side in the upper part of the frame with a
clear gap between them. Below and centred between them sits a third shape, a
small open circle, positioned so that its centre is exactly midway between the
two squares. A single straight line runs from the left square down to the
circle, and a second straight line runs from the right square down to the same
circle, the two meeting at its top edge. The left line is solid; the right line
is drawn as a dashed line of the same weight. Beneath the circle a single
straight line descends to a short horizontal bar at the bottom of the frame,
and that bar is unbroken across its full width. The circle and its descending
line are bright pale cyan; everything else is pale cool grey.
```

**Check:** the circle's centre must sit midway between the two squares. Measure
both horizontal distances — an off-centre circle implies one router owns the
address, which is the misconception.

## Routing Security & Path Validation — `baseline-versus-hijack.png`

*Same destination, same hop count, one hop different.*

```text
Two horizontal lines of equal length stacked one above another with a clear gap,
both aligned at their left and right edges. Standing on each line at identical
even intervals is a row of short vertical strokes, the same number on both lines
and in the same positions, each rising above its line and ending in a small
horizontal crossbar. Every stroke is identical except one: on the lower line,
the stroke third from the left is drawn at twice the height of its neighbours
and its crossbar is twice as wide. Both lines terminate at their right ends in
identical small open squares. The one tall stroke is bright pale cyan;
everything else is pale cool grey.
```

**Check:** the two rows must have the same stroke count at matching x-positions
— that identity is the entire point, since the finding is the single difference.
Compare the two rows' stroke coordinates directly.

---

# Core Network Services

## DNS Resolution & Records — `ttl-counts-down.png`

*A TTL that decrements is someone else's memory.*

```text
Three horizontal bars of identical length stacked one above another with equal
gaps, all aligned at both ends, each divided into the same number of small equal
cells along its length. Reading downward, the filled run starting at the left
edge is longest in the topmost bar, one cell shorter in the middle bar, and two
cells shorter in the lowest. To the right of all three bars, separated by a
clear gap, stands a fourth bar of the same length and cell size whose filled run
starts at the left edge and is exactly as long as the topmost bar's. The fourth
bar's filled run is bright pale cyan; the three stacked runs and every outline
are pale cool grey.
```

**Check:** the three stacked runs must shorten by exactly one cell each, and the
isolated fourth must match the topmost exactly. Measure all four run lengths.

## DNS Security & Encrypted Transports — `signed-but-unvalidated.png`

*Records carry signatures; the resolver does not check them.*

```text
Two horizontal bars, one above the other, aligned at both ends and of equal
length. Each is divided into four equal segments by three vertical dividers at
matching positions. In the upper bar every segment carries a small solid mark
centred within it. In the lower bar the segments are identical empty outlines
with no marks at all. A single continuous vertical stroke descends from the
right end of the upper bar to the right end of the lower bar, ending in a point.
The marks in the upper bar are bright pale cyan; every other line is pale cool
grey.
```

**Check:** all four upper segments must carry a mark and all four lower
segments must be empty. Any stray mark below inverts the meaning.

## Local Name Resolution & Service Discovery — `first-answer-wins.png`

*The name was asked out loud and a stranger answered first.*

```text
A single small open square sits at the left of the frame. From it a horizontal
line runs rightward and, partway along, splits into three straight lines that
fan outward and rightward at shallow angles, each ending in a small open square
near the right edge, the three squares arranged one above another. From each of
those three squares a return line travels back leftward, and the three converge
on a single point on the original horizontal line. The return line from the
middle square meets that point along a visibly shorter path than the other two.
The middle square, its outbound line and its shorter return are bright pale
cyan; everything else is pale cool grey.
```

**Check:** the three returns must meet at one point, and the cyan return must be
measurably the shortest. Trace and compare all three.

## Network Time Synchronization — `tolerance-cliff.png`

*Nothing fails at four minutes; everything fails at five.*

```text
One long horizontal bar spanning the frame, divided into many small equal cells
along its length. A single heavy vertical rule crosses the bar about four fifths
of the way along, drawn as one continuous stroke that rises well above the bar
and descends well below it. Every cell to the left of that rule is filled with a
solid tone; every cell to the right is empty. There is no gradual change of any
kind approaching the rule — the last filled cell sits immediately against it.
The heavy rule is bright pale cyan; the filled cells and every outline are pale
cool grey.
```

**Check:** the fill must terminate hard at the rule with no intermediate tone.
Sample pixel values across the three cells either side; any gradient there
teaches the opposite of the note.

## Email Transport Protocols — `every-check-passes.png`

*Three verdicts, all honest, and the message is still hostile.*

```text
Four horizontal bars of equal length stacked one above another with equal gaps,
aligned at both ends. The upper three bars are each filled completely with a
solid tone from end to end. The lowest bar is separated from the three above it
by a gap twice as wide as the others, and it is a single empty outline with no
fill and no divisions. A single continuous vertical stroke descends from the
left end of the topmost bar, past the left ends of all four, and ends in a
point below the lowest. The lowest bar's outline is bright pale cyan; the three
filled bars and the stroke are pale cool grey.
```

**Check:** the three upper bars must be completely filled and the lowest
completely empty. Partial fill anywhere breaks the "every check passed" reading.

## Network Management Protocols — `flow-shape-anomaly.png`

*The finding is in the shape of the metadata, not its content.*

```text
Three horizontal bars stacked one above another with equal gaps, all starting at
the same left edge. The upper two bars are short and of almost exactly the same
length as each other, ending well before the middle of the frame. The lowest bar
starts at the same left edge and runs to the right edge, making it many times
longer than either bar above it. A horizontal dimension line with a short
vertical tick at each end runs beneath the lowest bar across its full length.
The lowest bar is filled with a solid bright pale cyan tone; the two short bars
and the dimension line are pale cool grey.
```

**Check:** the two short bars must be within a few pixels of each other in
length, and the long bar must be at least eight times either. Measure all three.

---

# Transport Layer & Sockets

## Ports & Sockets — `five-tuple-separates.png`

*One destination port, many conversations, kept apart by the source port.*

```text
A short horizontal bar stands alone at the right of the frame, divided along its
length into several small equal cells. To its left, a column of small open
squares is arranged one above another. From each square a single straight line
travels rightward and meets the bar at the left edge of its own cell, the lines
arriving in the same top-to-bottom order as the squares, so that no two lines
cross. Every line is the same weight and none touches another. The bar is
bright pale cyan; the squares and lines are pale cool grey.
```

**Check:** no two lines may cross, and the cell count must equal the square
count. Both are countable at 2×.

## TCP Connections & State — `handshake-three-strokes.png`

*Three segments, two independently chosen numbers, each confirmed once.*

```text
Two vertical lines stand parallel at the left and right of the frame, running
the full height. Three horizontal strokes cross between them, one above another
with equal vertical gaps. The topmost runs from the left line to the right and
ends in a point at the right. The middle runs from the right line to the left
and ends in a point at the left. The lowest runs from the left line to the right
and ends in a point at the right. Each stroke is one continuous line including
its point, with no separate arrowhead. The middle stroke is bright pale cyan;
the two vertical lines and the other two strokes are pale cool grey.
```

**Check:** each arrowhead must be continuous with its stroke, not a detached
triangle — that is rule 7 applied, and detached heads drift.

## TCP Reliability & Congestion Control — `window-collapse.png`

*Loss by duplicate acknowledgement halves the window; loss by timeout collapses
it.*

```text
A row of vertical strokes standing on one continuous horizontal line that runs
the full width of the frame, the strokes evenly spaced. Reading left to right
the strokes grow taller in even increments up to a point about a third of the
way along, where the next stroke is exactly half the height of the one before
it; from there they grow in even increments again up to a point about two thirds
along, where the next stroke drops to the shortest height in the whole row; from
there they grow in even increments once more to the right edge. The two strokes
that drop are bright pale cyan; the horizontal line and every other stroke are
pale cool grey.
```

**Check:** measure the two drops. The first must be half the preceding stroke,
the second must be the row minimum. Equal drops would erase the asymmetry that
is the entire lesson.

## UDP & Connectionless Transport — `amplification-ratio.png`

*Sixty-four bytes in, three and a half thousand out.*

```text
Two horizontal bars, one above the other, aligned at their left edges. The upper
bar is very short, occupying about a fiftieth of the frame width. The lower bar
starts at the same left edge and runs to the right edge of the frame. Both bars
are the same height. A horizontal dimension line with a short vertical tick at
each end runs above the upper bar across its length, and a matching dimension
line runs below the lower bar across its length. The lower bar is filled with a
solid bright pale cyan tone; the upper bar and both dimension lines are pale
cool grey.
```

**Check:** measure the ratio of the two bar lengths — it must be dramatic and
roughly fifty to one. A ratio of five to one understates the mechanism to the
point of being wrong.

## QUIC & Modern Transport — `same-id-two-flows.png`

*Two five-tuples, one session, and only the connection ID says so.*

```text
Two horizontal bars of equal length, one above the other with a clear gap,
aligned at both ends. Each bar is divided into three segments by two vertical
dividers, and in both bars the two dividers sit at identical positions. In each
bar the leftmost segment is filled with a dense diagonal hatch and the middle
segment is empty. The rightmost segment of the upper bar and the rightmost
segment of the lower bar are both filled with the same solid tone. The hatch in
the upper bar runs in one diagonal direction and the hatch in the lower bar runs
in the opposite diagonal direction. The two solid rightmost segments are bright
pale cyan; every other line and both hatches are pale cool grey.
```

**Check:** the two dividers must sit at identical x-positions in both bars, and
the two rightmost segments must be identically filled. That identity beside the
opposed hatches is the whole diagram.

## Transport Layer Threats & Controls — `slow-exhaustion-flat.png`

*Ten thousand connections, and the bandwidth graph never moves.*

```text
Two horizontal lines of equal length stacked one above another with a clear gap,
spanning the frame. Standing on the upper line at even intervals is a row of
short vertical strokes, all the same very short height, unchanged from left to
right across the whole width. Standing on the lower line at the same even
intervals is a row of vertical strokes that grow taller from left to right in
even increments, the leftmost as short as those above and the rightmost many
times taller. Both lines run unbroken from edge to edge. The lower row of
growing strokes is bright pale cyan; the upper row and both lines are pale cool
grey.
```

**Check:** the upper row must be genuinely flat — measure several stroke heights
and confirm they match within a pixel or two. A drifting upper row destroys the
contrast the note is built on.

---

# Web & Application Protocols

## HTTP Fundamentals — `bearer-token-moves.png`

*The same string presented by a different client is the same user.*

```text
Two small open squares sit one above the other at the left of the frame with a
clear gap between them. A single small solid shape sits at the centre of the
frame, midway between the two squares vertically. From each square a straight
line travels rightward to a third, larger open square at the right of the frame,
and each of those two lines passes exactly through the small solid shape on its
way. Both lines are identical in weight and both terminate at the same point on
the left edge of the large square. The small solid shape is bright pale cyan;
everything else is pale cool grey.
```

**Check:** both lines must pass through the solid shape and arrive at the same
point. If they arrive at different points the diagram says the server can tell
them apart, which is the opposite of the note.

## HTTPS & the TLS Handshake — `two-verifications.png`

*The site that warns is benign; the one that does not is hostile.*

```text
Two horizontal bars of equal length, one above the other with a clear gap,
aligned at both ends. Each is divided into four equal segments by three vertical
dividers at matching positions. Every segment in the upper bar carries a small
solid mark centred within it. In the lower bar the first three segments carry
identical marks and the fourth is empty, and a short vertical stroke rises from
the top edge of that empty fourth segment and ends in a point above the bar. The
upper bar's outline is bright pale cyan; every mark, the lower bar and the
rising stroke are pale cool grey.
```

**Check:** the upper bar must have four marks and the lower exactly three, with
the rising stroke over the empty one. Count marks at 2×.

## Web Architecture & Proxies — `path-around-the-edge.png`

*A control that can be bypassed was never in the path.*

```text
A small open square sits at the left of the frame and a second at the right. A
straight horizontal line runs between them at mid-height, and standing across
that line at its midpoint is a tall vertical bar that fully interrupts it, so
the line stops at the bar's left edge and resumes at its right edge. A second
line leaves the left square, curves downward well below the vertical bar,
passes beneath it without touching, and rises to rejoin the right square. The
curved lower line is continuous from square to square. The curved line is bright
pale cyan; the straight line, both squares and the vertical bar are pale cool
grey.
```

**Check:** the curved line must be unbroken and must clear the vertical bar
entirely. Any contact between them reads as inspection, which is the point being
denied.

## REST & Modern API Transport — `one-character-apart.png`

*Same token, one digit different, another account's record.*

```text
Two horizontal bars of equal length, one above the other with a clear gap,
aligned at both ends. Each is divided into a long left segment and a short right
segment by a single vertical divider, both dividers at the same position. The
long left segments of both bars are filled with an identical dense diagonal
hatch running in the same direction. The short right segment of the upper bar is
empty; the short right segment of the lower bar is filled with a solid tone. The
lower bar's short right segment is bright pale cyan; both hatches and every
outline are pale cool grey.
```

**Check:** the two hatches must be visually identical in direction and density,
and the two dividers must sit at the same x-position. The identity of the left
portion is what makes the right-hand difference legible.

## WebSockets & Real-Time Protocols — `one-request-then-none.png`

*The handshake is the only HTTP request in the conversation.*

```text
Two vertical lines stand parallel at the left and right of the frame, running
the full height. Near the top, a single horizontal stroke crosses from the left
line to the right and ends in a point. Immediately below it, a tall vertical bar
stands between the two lines, interrupting nothing but sitting clearly in the
space, its top edge just below that first stroke. Below the bar, a dense row of
short horizontal strokes crosses between the two vertical lines, one above
another with small equal gaps, alternating in direction so that they end in
points alternately at the right and at the left. The tall vertical bar is bright
pale cyan; every stroke and both vertical lines are pale cool grey.
```

**Check:** the tall bar must sit below the single top stroke and above the whole
dense row, touching neither. Its position is the entire argument.

## Application Delivery & Load Balancing — `health-check-two-failures.png`

*Too shallow keeps a broken backend; too deep withdraws a working service.*

```text
Two horizontal lines of equal length stacked one above another with a clear gap,
spanning the frame. Standing on the upper line at even intervals is a row of
short vertical strokes, all rising above the line and all ending in small
horizontal crossbars, with no exceptions anywhere in the row. Standing on the
lower line at the same even intervals is a row of strokes of the same height,
none of which ends in a crossbar — every one of them stops bare. A short
vertical arrow points downward in the gap between the two lines at the centre.
The lower row is bright pale cyan; the upper row and both lines are pale cool
grey.
```

**Check:** every stroke in the upper row must have a crossbar and none in the
lower row may have one. A single exception in either row makes both halves of
the lesson ambiguous.

---

# Wireless Networking

## Wireless Fundamentals & 802.11 — `airtime-overhead.png`

*Half the channel is protocol before a second device exists.*

```text
Two horizontal bars of the same total length, one above the other with a clear
gap, aligned at both ends. Each is divided into two segments by a single
vertical divider. In the upper bar the divider sits slightly past the midpoint,
so the left segment is a little larger than the right. In the lower bar the
divider sits very close to the right end, so the left segment occupies almost
the whole bar and the right segment is a narrow sliver. In both bars the left
segment is filled with a dense diagonal hatch and the right segment is left
empty. Both hatched left segments are bright pale cyan; every outline is pale
cool grey.
```

**Check:** measure both dividers. Upper should sit near 47 percent from the left
and lower near 95 percent. Those two positions are the 53 percent and 5 percent
efficiencies the note computes.

## Wi-Fi Security & WPA — `search-space-cliff.png`

*A wordlist entry falls in minutes; twelve random characters never do.*

```text
A row of vertical strokes standing on one continuous horizontal line that runs
the full width of the frame, the strokes evenly spaced. The leftmost stroke is
very short. Each stroke to its right is dramatically taller than the one before
it, roughly tripling in height each time, so that the rightmost stroke reaches
the top edge of the frame and the difference between the first two is barely
visible beside the difference between the last two. The leftmost stroke is
bright pale cyan; the horizontal line and every other stroke are pale cool grey.
```

**Check:** confirm the growth is multiplicative rather than linear — measure the
ratio between successive stroke heights. Even increments would flatten an
exponential argument into a gradual one.

## Wireless Attacks & Rogue Infrastructure — `certificate-check-decides.png`

*One unset check, and credentials leave the device.*

```text
A single small open square sits at the left of the frame. From it two straight
lines travel rightward, one rising gently and one falling gently. The rising
line stops partway across the frame and ends in a short vertical bar that
crosses it at right angles, blocking it. The falling line continues all the way
to the right edge of the frame, where it ends in a small solid shape. Both lines
leave the square at the same point and are the same weight. The falling line and
its solid shape are bright pale cyan; the rising line, its blocking bar and the
square are pale cool grey.
```

**Check:** the rising line must terminate at the blocking bar with no
continuation beyond it, and the falling line must be unbroken to the edge.

## Wireless Reconnaissance & Defense — `two-claims-one-name.png`

*Identical names, different hardware addresses, and only the inventory decides.*

```text
Two horizontal bars of identical length, one above the other with a clear gap,
aligned at both ends. Each is divided into a long left segment and a short right
segment by a single vertical divider at the same position in both. The long left
segments of both bars are filled with an identical dense diagonal hatch running
in the same direction. The short right segment of the upper bar is filled with a
solid tone; the short right segment of the lower bar is filled with a coarse
dotted stipple, clearly different from both the hatch and the solid. The lower
bar's stippled right segment is bright pale cyan; everything else is pale cool
grey.
```

**Check:** the two left hatches must be indistinguishable and the two right
fills clearly distinct. If the left segments differ at all, the diagram loses
its claim that the name proves nothing.

## Bluetooth & Personal-Area Networks — `pairing-window.png`

*The pairing exchange is the whole protection, and it is brief.*

```text
One long horizontal bar spanning the frame, divided into many small equal cells
along its length, every cell filled with a solid tone except for a single short
run of empty cells positioned about one fifth of the way along from the left.
That empty run is no more than three cells wide. A single continuous vertical
stroke rises from the top edge of the bar at the left boundary of the empty run
and ends in a point above the bar. The empty run and the rising stroke are
bright pale cyan; the filled cells and the bar outline are pale cool grey.
```

**Check:** the empty run must be short relative to the bar — measure it as a
fraction of total width. A wide gap makes the window look like an ordinary
phase rather than a brief exposure.

## Cellular & Long-Range Wireless — `downgrade-step.png`

*A fallback is the weakest option still permitted.*

```text
A row of vertical strokes standing on one continuous horizontal line that runs
the full width of the frame, evenly spaced, growing taller from left to right in
even increments. A single continuous curved arrow begins at the top of the
tallest stroke at the right, arcs above the whole row leftward, and descends to
end in a point at the top of the shortest stroke at the left, the point being a
continuation of the curve rather than a separate mark. The curved arrow is
bright pale cyan; the horizontal line and every stroke are pale cool grey.
```

**Check:** the arrow must terminate exactly at the top of the leftmost stroke.
It is described as one continuous curve for that reason — a detached head will
land somewhere near it instead of on it.

---

# Network Security Architecture

## Network Segmentation & Zero Trust — `blast-radius-shrinks.png`

*Twenty-six reachable services become six.*

```text
Two horizontal bars of identical total length, one above the other with a clear
gap, aligned at both ends. The upper bar is divided into many small equal cells
along its whole length, and every cell is filled with a solid tone. The lower
bar is divided into cells of exactly the same width as those above, but only a
short run of cells at its left end is filled; the rest of the bar is a single
empty span with no internal dividers at all. A horizontal dimension line with a
short vertical tick at each end runs beneath the lower bar, spanning only its
filled run. The lower bar's filled run is bright pale cyan; the upper bar and
the dimension line are pale cool grey.
```

**Check:** count filled cells in both bars. The lower must be roughly a quarter
of the upper — measure rather than trusting the impression, since a fill that
looks short can be half.

## Firewall Architecture & Policy — `range-written-out.png`

*A prefix that reads as tight and admits sixty-five thousand hosts.*

```text
Two horizontal bars, one above the other, aligned at their left edges. The upper
bar is short, occupying about a fiftieth of the frame width, and is filled with
a solid tone. The lower bar starts at the same left edge and runs to the right
edge of the frame, and is filled with the same solid tone. Both bars are the
same height. A horizontal dimension line with a short vertical tick at each end
runs above the upper bar across its length, and a matching dimension line runs
below the lower bar across its length. The upper short bar is bright pale cyan;
the lower bar and both dimension lines are pale cool grey.
```

**Check:** the ratio must be dramatic — roughly fifty to one or steeper. The
whole point is that the intended scope is invisibly small beside the written
one.

## Network Access Control — `admitted-then-assigned.png`

*Identity decides the segment, not the port.*

```text
A single small open square sits at the left of the frame. From it one straight
horizontal line travels rightward to a tall vertical bar standing across the
centre of the frame. From the right edge of that bar three straight lines fan
outward and rightward at shallow angles, one rising, one level and one falling,
each ending in a short horizontal bar near the right edge, the three end bars
arranged one above another. Only one of the three lines, the level one, is drawn
solid; the other two are dashed at the same weight. The tall central bar and the
solid level line are bright pale cyan; everything else is pale cool grey.
```

**Check:** exactly one of the three fan lines must be solid. Two solid lines
would say the decision admits more than one outcome at a time.

## VPNs & Encrypted Tunnels — `tunnel-carries-the-far-end.png`

*The tunnel secured the transport and extended the boundary.*

```text
Two concentric horizontal bars: an outer bar spanning the frame, and an inner
bar of the same length but half the height, centred within it so that a margin
of equal thickness runs above and below the inner bar along its whole length.
The inner bar is divided into several small equal cells by short vertical
dividers that do not extend into the outer margin. At the far right, both bars
end together at a small open square that sits outside the outer bar and touches
its right edge. The outer bar's outline is bright pale cyan; the inner bar,
its dividers and the square are pale cool grey.
```

**Check:** the margin above and below the inner bar must be equal along the full
length. An inner bar that drifts is a tunnel that leaks, which is a different
diagram.

## Intrusion Detection & Network Monitoring — `inline-versus-copy.png`

*One cannot break what it does not touch; the other earns blocking by becoming
load-bearing.*

```text
Two horizontal lines of equal length stacked one above another with a clear gap,
both spanning the frame from edge to edge. A tall vertical bar stands across the
upper line at its midpoint, fully interrupting it, so the line stops at the
bar's left edge and resumes at its right. A second tall vertical bar of the same
size sits beneath the lower line, below it and not touching it, at the same
horizontal position, and the lower line runs unbroken from edge to edge past it.
A short vertical stroke connects the lower line to the top of that second bar.
Both tall bars are bright pale cyan; both lines and the short connector are pale
cool grey.
```

**Check:** the upper line must be genuinely interrupted and the lower genuinely
unbroken. That single difference is the whole comparison.

## Egress Control & Web Proxies — `beacon-interval.png`

*Regular to a fraction of a second, which is a thing software does.*

```text
A row of short vertical strokes standing on one continuous horizontal line that
runs the full width of the frame. Every stroke is the same height and the gaps
between consecutive strokes are all identical, except that one stroke, sitting
about two thirds of the way along, is drawn at four times the height of the
others while keeping exactly the same spacing from its neighbours as they have
from each other. A horizontal dimension line with a short vertical tick at each
end runs beneath the horizontal line, spanning the gap between the first two
strokes. The one tall stroke is bright pale cyan; every other stroke, the line
and the dimension line are pale cool grey.
```

**Check:** measure every gap. They must be equal to within a pixel or two —
the regularity *is* the finding, so uneven spacing here is fatal in exactly the
way rule 11 describes.

---

# Network Analysis & Troubleshooting

## Structured Network Troubleshooting — `passed-the-test-not-the-layer.png`

*Every layered check passed and the fault was below the pivot.*

```text
Four horizontal bars stacked one above another with equal gaps, all the same
length and aligned at both ends. Each of the upper three bars carries a small
solid mark centred within it. The lowest bar carries no mark; instead it is
divided into two segments by a single vertical divider near its right end, and
the short right segment is filled with a dense diagonal hatch. A single
continuous vertical stroke descends from the centre of the topmost bar through
all four, ending in a point below the lowest. The hatched segment in the lowest
bar is bright pale cyan; every mark, bar and the stroke are pale cool grey.
```

**Check:** the three upper marks must be present and identical, and the fault
must sit only in the lowest bar. A mark in the lowest bar or a missing mark
above would say the checks caught it.

## Connectivity Diagnostics — `silence-two-answers.png`

*A hundred percent loss above, succeeded below, both correct.*

```text
Two horizontal lines of equal length stacked one above another with a clear gap,
both spanning the frame. On the upper line, a small open square sits at the left
and a second at the right, and the line between them is broken by a wide clean
gap in the middle. On the lower line, small open squares sit at the same left
and right positions, and the line between them is continuous with no gap at all.
The two lines are otherwise identical in length, weight and endpoint positions.
The lower continuous line is bright pale cyan; the upper broken line and all
four squares are pale cool grey.
```

**Check:** the four squares must sit at matching x-positions on both lines. The
identity of the endpoints is what makes the two different answers about the same
pair of hosts.

## Packet Capture & Analysis — `switch-sends-you-nothing.png`

*The capture is not empty; it is full of your own traffic.*

```text
A tall vertical bar stands at the centre of the frame. From its left edge a
single straight horizontal line runs to a small open square at the left edge of
the frame. From its right edge three straight lines fan outward and rightward at
shallow angles, each ending in a small open square, the three arranged one above
another near the right edge. A fourth line leaves the right edge of the tall bar
and runs level to a small solid shape below and left of the three squares. Only
the line to that solid shape and the line to the left square are drawn solid;
the three fanning lines are dashed at the same weight. The tall bar and the
solid shape are bright pale cyan; everything else is pale cool grey.
```

**Check:** exactly two lines may be solid and exactly three dashed. The ratio is
the point — most of the segment's traffic never arrives.

## Traffic Analysis & Flow Inspection — `baseline-decays.png`

*A baseline built while an intruder was resident makes them normal.*

```text
A row of vertical strokes standing on one continuous horizontal line that runs
the full width of the frame, evenly spaced and all the same height, except that
one stroke about a quarter of the way along from the left is drawn at three
times the height of the others. A horizontal dimension line with a short
vertical tick at each end runs beneath the horizontal line, beginning at the
left edge and ending part way along, and it extends far enough to the right to
include the tall stroke within its span. The tall stroke is bright pale cyan;
every other stroke, the line and the dimension line are pale cool grey.
```

**Check:** the dimension line must extend past the tall stroke, enclosing it.
That enclosure is the whole diagram — a baseline window containing the anomaly
it is supposed to exclude.

## Protocol Debugging & Deep Inspection — `two-parsers-disagree.png`

*The same bytes, split two different ways.*

```text
Two horizontal bars of identical length, one above the other with a clear gap,
aligned at both ends, both the same height. The upper bar is divided into
segments by three vertical dividers placed at uneven intervals along its length.
The lower bar is divided into segments by three vertical dividers placed at
different uneven intervals, none of which lines up with any divider above it.
The outer outlines of the two bars are identical in every respect. The lower
bar's dividers are bright pale cyan; the upper bar's dividers and both outlines
are pale cool grey.
```

**Check:** no divider in the lower bar may share an x-position with one above.
Confirm all six coordinates — a coincidental alignment weakens the claim that
the two readings are independent.

## Performance & Latency Analysis — `impairment-persists.png`

*Only impairment that continues to the destination is real.*

```text
Two horizontal lines of equal length stacked one above another with a clear gap,
both spanning the frame. Standing on each line at identical even intervals is a
row of short vertical strokes, the same number on both lines at matching
positions. In the upper row every stroke is the same short height except one,
about a third of the way along, which is much taller; the strokes after it
return to the short height. In the lower row the strokes are short up to the
same position, and from that stroke rightward every stroke is tall and stays
tall to the end of the row. The lower row's tall strokes are bright pale cyan;
everything else is pale cool grey.
```

**Check:** in the upper row exactly one stroke may be tall; in the lower row
every stroke from that position rightward must be tall. Count both rows — this
contrast is the most misread pattern in the branch and a single stray stroke
inverts it.

---

## Coverage

Fifty-four prompts across nine branches. The Switching & the Link Layer branch
was generated earlier and its six assets are already embedded, bringing the
Networking domain to sixty notes with a dedicated visual once these are run.

Nothing here asks for a two-dimensional lattice, a state change part-way through
a clip, a labelled inventory of shapes, or a colour named as a hex value. Every
one of those was paid for once already.
