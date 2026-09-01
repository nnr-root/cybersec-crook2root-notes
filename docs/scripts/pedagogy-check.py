#!/usr/bin/env python3
"""
Crook2Root pedagogy gate — enforces the Teaching Standard.

Companion to ci-check.py. Where ci-check.py guards STRUCTURE (no labs, no images,
no numbered tasks, valid frontmatter), this guards TEACHING: the patterns that
decide whether a correct note actually gets learned.

  ERRORS  (exit 1, blocks the commit)
    * minimising the reader's task — "you simply run", "just install",
      "all you have to do is", "it should be clear that". To a stuck reader
      these say "the problem is you". NOTE the rule targets the construction,
      not the word: "trivially forged" and "is simply matching state" are
      precise claims about attacker cost and mechanism, and are allowed.
    * generic heading labels — the four filler titles the corpus wore out
      ("The Mental Model", "Practical Usage", "Failure Modes and Interpretation",
      "Internals & Edge Cases"). A heading must name the move, not the slot.

  WARNINGS (reported, never block) — the authoring backlog
    * first command buried past 15% of the body  ......... The Cold Open
    * an error output with no mechanism paragraph ........ The Autopsy
    * no question asked anywhere in the body ............. One Pre-Question
    * an analogy with no stated breaking point
    * shell commands not re-verified in 12 months (needs `verified:` frontmatter)
    * addresses that are not on The Thread and not exempt under Lab Topology §5b
      (declare an exemption with a `thread-exempt:` frontmatter list, reason required)

Four patterns are deliberately NOT checked — The Break, The Twin, The Tell and
The Fade. A regex that "detected" a naive-model beat would only teach us to type
the trigger phrase. Those live on the review checklist in CONTRIBUTION.md.

Run from the vault root:
    python3 docs/scripts/pedagogy-check.py             # errors + warning counts
    python3 docs/scripts/pedagogy-check.py --warnings  # list the backlog
    python3 docs/scripts/pedagogy-check.py --fix-hedges --apply   # rewrite safe hedges
    python3 docs/scripts/pedagogy-check.py --json      # machine-readable
"""
import os
import re
import sys
import json

SKIP_DIRS = {".git", ".obsidian", "graphify-out", ".claude", ".archive", "_to_delete"}
GOV_FILES = {"AGENTS.md", "README.md", "CONTRIBUTION.md"}
COLD_OPEN_RATIO = 0.15
STALE_MONTHS = 12

FM = re.compile(r"^---\n(.*?)\n---", re.S)
EXAMPLE_FENCE = re.compile(r"^```(shell-session|console|bash|shell|powershell|text|sql|http)", re.M)

# ── errors ────────────────────────────────────────────────────────────────────
# Target the construction that does the damage, not the word.
#
# "Trivially forged", "trivially bypassed", "a connection is simply matching state"
# are precise: they characterise ATTACKER COST or MECHANISM MINIMALITY. Banning
# them would weaken the prose. What harms the reader is minimising THEIR task —
# "you simply run", "all you have to do is", "it should be clear that" — which
# tells someone who is stuck that the problem is them.
HEDGES = re.compile(
    # "you simply <instruction verb>" — but not "you simply used", which is "merely"
    r"\b(?:you|we)\s+(?:can\s+)?simply\s+(?:run|add|use|type|call|set|change|edit|"
    r"open|install|enable|disable|point|replace|copy|paste|do|follow|repeat|check)\b"
    r"|\bsimply\s+(?:run|add|use|type|call|set|change|edit|open|install|enable|"
    r"disable|point|replace|copy|paste|follow|repeat)\b"
    # "just <verb>" only when NOT negated — "doesn't just add noise" is "merely"
    r"|(?<!n't )(?<!not )\bjust\s+(?:run|add|type|install|copy|paste)\b"
    r"|\b(?:it|this)(?:'s| is)\s+simply\s+a\s+matter\b"
    r"|\bmost simply\b|\bsimply put\b"
    r"|\ball (?:you|we) (?:have to|need to) do is\b"
    r"|\bit should be (?:clear|obvious)\b"
    r"|\bas (?:you|we) (?:can see|already know)\b"
    r"|\bthe rest (?:is|should be) (?:easy|simple|straightforward|trivial)\b"
    r"|\bshould be (?:obvious|self-explanatory)\b"
    r"|\bany (?:beginner|novice) (?:can|should)\b", re.I)

# Bare discourse markers: not condescending on their own, but they add nothing.
# Warning tier, so they never block a commit.
FILLER = re.compile(r"^\s*(?:Obviously|Of course),\s", re.I)

GENERIC_HEADINGS = {
    "the mental model",
    "practical usage",
    "failure modes and interpretation",
    "internals & edge cases",
    "internals and edge cases",
    "mental model",
    "practical use",
}

# ── warnings ──────────────────────────────────────────────────────────────────
ERROR_LINE = re.compile(
    r"(?i)\b(error|denied|refused|failed|failure|invalid|no such file|"
    r"cannot|can't|unable to|not permitted|rejected|timed out|unauthorized)\b")
MECHANISM = re.compile(
    r"(?i)(because|the reason|rejected (it|the|because)|refused (it|because)|"
    r"why it fail|what went wrong|caused by|never (saw|reached|got)|"
    r"before (it|the) .{0,40}(saw|reached)|checks? (for|that)|validat|"
    r"parser|kernel|driver|stage|at that point|the check )")
ANALOGY = re.compile(
    r"(?i)(think of it (as|like)|is like a|as if it were|imagine (a|an|you)|the analogy)")
ANALOGY_BREAK = re.compile(
    r"(?i)(analogy (breaks|stops|fails|ends|is)|where (the|this) analogy|breaks down|"
    r"stops being accurate|don't carry that|unlike a|the analogy is imperfect)")
PROSE_Q = re.compile(r"\?")
VERIFIED = re.compile(r"^verified:\s*(\d{4})-(\d{2})-(\d{2})\s*$", re.M)

# ── The Thread ────────────────────────────────────────────────────────────────
# Every address in the corpus must be either a Meridian address, a reserved
# documentation range, or a value whose identity is itself the lesson (§5b of
# docs/Crook2Root Lab Topology.md). Anything else is scenery that should be on
# The Thread.
IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
PROTECTED_IPS = {
    "0.0.0.0",            # wildcard bind
    "169.254.169.254",    # the real cloud-metadata address
    "8.8.8.8", "8.8.4.4", "1.1.1.1", "9.9.9.9",   # real public resolvers, named as such
    "255.255.255.255",    # limited broadcast
}
def _thread_ok(ip):
    if ip in PROTECTED_IPS or ip.startswith(("127.", "255.", "224.", "239.")):
        return True                                  # identity is the lesson
    o = ip.split(".")
    try:
        a, b = int(o[0]), int(o[1])
    except ValueError:
        return True
    if (a, b) in {(192, 0), (198, 51), (203, 0)}:    # RFC 5737 documentation
        return True
    if a == 10 and b in (10, 20):                    # Meridian corporate + DMZ
        return True
    if a == 169 and b == 254:                        # link-local
        return True
    return False


# A note may declare addresses exempt under Lab Topology §5b by listing them in
# frontmatter with a reason, e.g.
#     thread-exempt:
#       - "10.99.0.: veth pair on the reader's own machine — local reproduction"
# Each entry must carry a reason; a bare address is rejected so exemptions stay
# reviewable rather than becoming a silent opt-out.
# 802.11 captures label fields as DA:/SA:/BSSID: and "DA" is itself valid hex,
# so a bare six-group match can start on the label and slide one octet left.
# The trailing lookahead forces the match onto the real address.
MAC = re.compile(r"\b(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}(?![:0-9a-fA-F])")
MAC_OK_PREFIX = "00:00:5e:00:53:"
MAC_PROTECTED = {"ff:ff:ff:ff:ff:ff", "00:00:00:00:00:00", "01:00:5e:00:00:01",
                 "33:33:00:00:00:01", "01:80:c2:00:00:00"}   # broadcast / multicast / STP


def _mac_ok(mac):
    m = mac.lower()
    return m.startswith(MAC_OK_PREFIX) or m in MAC_PROTECTED


EXEMPT_BLOCK = re.compile(r"^thread-exempt:\s*\n((?:\s+-\s+.*\n?)+)", re.M)


def declared_exempt(fm_block):
    m = EXEMPT_BLOCK.search(fm_block)
    if not m:
        return [], []
    good, bad = [], []
    for line in m.group(1).strip().split("\n"):
        entry = line.strip().lstrip("-").strip().strip('"\'')
        if ":" not in entry or not entry.split(":", 1)[1].strip():
            bad.append(entry)
            continue
        # an entry is "<prefix>: <reason>"; a MAC prefix has its own colons, so
        # split on the last colon that is followed by a space
        mm = re.match(r"^\s*(\S+?):\s+(.+)$", entry)
        if not mm:
            bad.append(entry)
            continue
        prefix, reason = mm.group(1).strip(), mm.group(2).strip()
        if not reason:
            bad.append(entry)
        elif re.match(r"^\d{1,3}(\.\d{1,3}){0,3}\.?$", prefix) or \
             re.match(r"^(?:[0-9a-fA-F]{2}:){1,5}[0-9a-fA-F]{0,2}$", prefix):
            good.append(prefix.lower())
        else:
            bad.append(entry)
    return good, bad


def fence_mask(lines):
    """True for any line that is a fence marker or sits inside a fence."""
    mask = [False] * len(lines)
    infence, marker = False, None
    for i, line in enumerate(lines):
        m = re.match(r"^(`{3,}|~{3,})", line)
        if m:
            mask[i] = True
            if not infence:
                infence, marker = True, m.group(1)
            elif m.group(1)[0] == marker[0] and len(m.group(1)) >= len(marker):
                infence, marker = False, None
            continue
        mask[i] = infence
    return mask


def is_index(rel, text):
    stem = os.path.splitext(os.path.basename(rel))[0]
    parent = os.path.basename(os.path.dirname(rel))
    top = rel.split(os.sep)[0]
    return stem == parent or stem == top or "cyber/moc" in text


def note_files(root):
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            if not f.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(dp, f), root)
            if rel.startswith("docs" + os.sep) or f in GOV_FILES:
                continue
            if os.sep not in rel and rel != "Cyber Security.md":
                continue
            yield rel


def paragraphs_after(lines, mask, idx, n=3):
    """The next n prose paragraphs after line idx, skipping fences and headings."""
    out, buf = [], []
    for i in range(idx, len(lines)):
        if mask[i]:
            continue
        s = lines[i].strip()
        if not s:
            if buf:
                out.append(" ".join(buf))
                buf = []
                if len(out) >= n:
                    break
            continue
        if s.startswith("#"):
            if buf:
                out.append(" ".join(buf))
                buf = []
            if len(out) >= 1:
                break          # a new section starts: the autopsy was owed here
            continue
        buf.append(s)
    if buf:
        out.append(" ".join(buf))
    return out[:n]


def check(root="."):
    errors, warnings = [], []

    for rel in note_files(root):
        path = os.path.join(root, rel)
        text = open(path, encoding="utf-8", errors="replace").read()
        lines = text.split("\n")
        mask = fence_mask(lines)
        body = FM.sub("", text)
        fm_block = (FM.match(text).group(1) if FM.match(text) else "")

        # ── ERROR: hedge words (prose only) ───────────────────────────────────
        for i, line in enumerate(lines):
            if mask[i] or line.lstrip().startswith("#"):
                continue
            # a negation can sit on the previous line ("doesn't\njust copy"), so carry
            # a little left-context in and ignore matches that start inside it
            lead = (lines[i - 1][-16:] + " ") if i and not mask[i - 1] else ""
            for m in HEDGES.finditer(lead + line):
                if m.start() < len(lead):
                    continue
                errors.append(f"{rel}:{i+1}: minimising the reader's task — \"{m.group(0).strip()}\" "
                              f"tells someone who is stuck that the problem is them")
            if FILLER.match(line):
                warnings.append(f"{rel}:{i+1}: sentence opens on a filler discourse marker "
                                f"(\"Obviously,\" / \"Of course,\") — cut it")

        # ── ERROR: generic heading labels ─────────────────────────────────────
        for i, line in enumerate(lines):
            if mask[i]:
                continue
            m = re.match(r"^#{2,4}\s+(.+?)\s*$", line)
            if m and m.group(1).strip().lower().rstrip(":") in GENERIC_HEADINGS:
                errors.append(f"{rel}:{i+1}: generic heading \"{m.group(1)}\" — "
                              f"name the move this section makes, not the slot it fills")

        if is_index(rel, text):
            continue

        # ── WARNING: The Cold Open ────────────────────────────────────────────
        total_words = max(len(body.split()), 1)
        m = EXAMPLE_FENCE.search(body)
        if m:
            ratio = len(body[:m.start()].split()) / total_words
            if ratio > COLD_OPEN_RATIO:
                warnings.append(f"{rel}: first command at {ratio*100:.0f}% of the body "
                                f"(target <{COLD_OPEN_RATIO*100:.0f}%) — open on the artifact")
        else:
            warnings.append(f"{rel}: no command, dump or capture anywhere — "
                            f"a claim about behaviour needs the observation that confirms it")

        # ── WARNING: The Autopsy ──────────────────────────────────────────────
        infence, start = False, None
        for i, line in enumerate(lines):
            if re.match(r"^(`{3,}|~{3,})", line):
                if not infence:
                    infence, start = True, i
                else:
                    infence = False
                    block = "\n".join(lines[start + 1:i])
                    if ERROR_LINE.search(block):
                        nxt = " ".join(paragraphs_after(lines, mask, i + 1, 2))
                        if not MECHANISM.search(nxt):
                            warnings.append(
                                f"{rel}:{start+1}: error output with no mechanism paragraph — "
                                f"name what rejected it, at which stage, and what it checked")
                            break

        # ── WARNING: One Pre-Question ─────────────────────────────────────────
        prose = "\n".join(l for i, l in enumerate(lines)
                          if not mask[i] and not l.lstrip().startswith(("#", ">", "|")))
        if not PROSE_Q.search(prose):
            warnings.append(f"{rel}: no question asked anywhere in the body — "
                            f"add one pre-question on the load-bearing idea, and answer it")

        # ── WARNING: analogy with no breaking point ───────────────────────────
        if ANALOGY.search(body) and not ANALOGY_BREAK.search(body):
            warnings.append(f"{rel}: analogy with no stated breaking point — "
                            f"say which part of it does not carry over")

        # ── WARNING: off-Thread addresses ─────────────────────────────────────
        exempt, malformed = declared_exempt(fm_block)
        for e in malformed:
            errors.append(f"{rel}: malformed thread-exempt entry \"{e[:60]}\" — "
                          f"each must read '<address prefix>: <reason>'")
        def _declared(v):
            v = v.lower()
            return any(v == e or v.startswith(e.rstrip(".") + ".") or v.startswith(e)
                       for e in exempt)

        off = sorted({ip for ip in IPV4.findall(body)
                      if not _thread_ok(ip) and not _declared(ip)})
        off_mac = sorted({m for m in MAC.findall(body)
                          if not _mac_ok(m) and not _declared(m)})
        if off_mac:
            shown = ", ".join(off_mac[:3]) + (f" (+{len(off_mac)-3} more)" if len(off_mac) > 3 else "")
            warnings.append(f"{rel}: {len(off_mac)} MAC(s) off The Thread — {shown}. "
                            f"Move to 00:00:5E:00:53:xx, or declare exempt "
                            f"(a MAC teaching the OUI or the locally-administered bit cannot move)")
        if off:
            shown = ", ".join(off[:4]) + (f" (+{len(off)-4} more)" if len(off) > 4 else "")
            warnings.append(f"{rel}: {len(off)} address(es) off The Thread — {shown}. "
                            f"Move onto Meridian, or confirm they are exempt "
                            f"(Lab Topology §5b)")

        # ── WARNING: staleness ────────────────────────────────────────────────
        if EXAMPLE_FENCE.search(body):
            v = VERIFIED.search(fm_block)
            if not v:
                warnings.append(f"{rel}: shell commands but no `verified:` date in frontmatter")
            else:
                import datetime
                d = datetime.date(int(v.group(1)), int(v.group(2)), int(v.group(3)))
                age = (datetime.date.today() - d).days
                if age > STALE_MONTHS * 30:
                    warnings.append(f"{rel}: commands last verified {age} days ago "
                                    f"(over {STALE_MONTHS} months) — re-run them")

    return errors, warnings


# ── the one safe autofix: hedges that delete cleanly ──────────────────────────
SAFE_HEDGE_SUBS = [
    (re.compile(r",\s+of course,\s+"), " "),
    (re.compile(r"\bOf course,\s+"), ""),
    (re.compile(r"\s+,?\s*of course\b"), ""),
    (re.compile(r"\bis simply\b"), "is"),
    (re.compile(r"\bare simply\b"), "are"),
    (re.compile(r"\bsimply a\b"), "a"),
    (re.compile(r"\bsimply an\b"), "an"),
    (re.compile(r"\bsimply the\b"), "the"),
    (re.compile(r"\bSimply put,\s*"), ""),
    (re.compile(r"\bsimply\s+"), ""),
    (re.compile(r"\bObviously,\s+"), ""),
    (re.compile(r",\s+obviously,\s+"), " "),
    (re.compile(r"\bobviously\s+"), ""),
    (re.compile(r"\bis trivially\b"), "is"),
    (re.compile(r"\btrivially\s+"), ""),
]


def fix_hedges(root=".", apply=False):
    changed, n = 0, 0
    for rel in note_files(root):
        path = os.path.join(root, rel)
        src = open(path, encoding="utf-8").read()
        lines = src.split("\n")
        mask = fence_mask(lines)
        out, hits = [], 0
        for i, line in enumerate(lines):
            if mask[i] or line.lstrip().startswith("#") or not HEDGES.search(line):
                out.append(line)
                continue
            new = line
            for pat, rep in SAFE_HEDGE_SUBS:
                new = pat.sub(rep, new)
            new = re.sub(r"  +", " ", new)
            # sentence-initial capital may have been eaten
            new = re.sub(r"(^|(?<=[.!?] ))([a-z])",
                         lambda mm: mm.group(1) + mm.group(2).upper(), new, count=1)
            if new != line:
                hits += 1
            out.append(new)
        if hits:
            changed += 1
            n += hits
            if apply:
                open(path, "w", encoding="utf-8").write("\n".join(out))
    print(f"{'rewrote' if apply else 'would rewrite'} {n} hedge line(s) in {changed} file(s)")
    if not apply:
        print("re-run with --apply to write; anything left over needs a human sentence")


def main():
    args = sys.argv[1:]
    if "--fix-hedges" in args:
        fix_hedges(".", apply="--apply" in args)
        return 0

    errors, warnings = check()

    if "--json" in args:
        print(json.dumps({"errors": errors, "warnings": warnings,
                          "error_count": len(errors), "warning_count": len(warnings)}, indent=2))
        return 1 if errors else 0

    if errors:
        print(f"✗ {len(errors)} PEDAGOGY ERROR(S):\n")
        for e in errors:
            print(f"  ERROR  {e}")
    else:
        print("✓ pedagogy gate passed — 0 errors")

    if warnings:
        if "--warnings" in args:
            print(f"\n{len(warnings)} teaching backlog item(s) (do not block):")
            for w in warnings:
                print(f"  todo   {w}")
        else:
            print(f"  ({len(warnings)} teaching backlog warnings — run with --warnings to list)")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
