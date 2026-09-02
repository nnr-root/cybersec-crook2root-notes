#!/usr/bin/env python3
"""
Rank the corpus by how much a production pass would improve each note.

The two gates already find most of what a pass fixes, but they report one line
at a time across four hundred files, which tells you nothing about where to
start. This aggregates their warnings per note, weights them by what each class
actually costs a reader, adds three checks the gates do not make, and prints
the notes worth opening first.

Weights are the point. A missing `verified:` date applies to 294 notes and
carries no triage signal, so it scores zero.

On the command checks, and why they are two checks rather than one. The first
version flagged any command-looking span in prose that the note never showed,
and fired on thirty notes, mostly wrongly: `cat f` in an explanation, a
container image called `docker-default`, `powershell.exe` as a program name.
Naming a tool without demonstrating it is perfectly fine when the tool has its
own note. So:

  - a command named in the Tell is an instruction the reader is meant to
    follow, and a note whose Tell names a command it never shows is teaching a
    check nobody can run. Per-note, high weight.
  - a tool the corpus names in prose and demonstrates nowhere at all is a hole
    in the whole corpus rather than in one note. Weighted lower, reported once.

usage: triage.py [--top 25] [--all] [--csv out.csv] [--gaps]
"""
import argparse, csv, os, re, subprocess, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SKIP = {".git", ".archive", ".obsidian", "docs", "assets", "graphify-out", ".github", ".githooks"}

WEIGHTS = [
    (re.compile(r"address\(es\) off The Thread"),      6, "off-Thread address"),
    (re.compile(r"MAC\(s\) off The Thread"),           6, "off-Thread MAC"),
    (re.compile(r"no command, dump or capture"),       4, "shows nothing"),
    (re.compile(r"no pre-question"),                   3, "no pre-question"),
    (re.compile(r"no worked example"),                 3, "no worked example"),
    (re.compile(r"generic heading"),                   3, "generic heading"),
    (re.compile(r"minimising the reader"),             3, "reader-minimising"),
    (re.compile(r"analogy with no stated breaking"),   2, "analogy unbounded"),
    (re.compile(r"\bthin \("),                         2, "thin"),
    (re.compile(r"no ## Summary"),                     2, "no Summary"),
    (re.compile(r"words of prose before the first"),   1, "slow to first command"),
    (re.compile(r"no difficulty tag"),                 1, "no difficulty tag"),
    (re.compile(r"filler discourse marker"),           1, "filler opener"),
    (re.compile(r"embedded asset"),                    0, "asset unverified"),
    (re.compile(r"`verified:` date|last verified"),    0, "verified date"),
]

BLOCK  = re.compile(r"```[a-zA-Z]*\n(.*?)```", re.S)
# a note whose artefact is source code, not a session transcript
SOURCE = re.compile(r"```(python|go|golang|c|cpp|rust|java|javascript|ts|typescript|"
                    r"ruby|perl|php|powershell|yaml|json|dockerfile|make)\n", re.I)
# findings that assume a note demonstrates commands and shows what came back.
# They are correct for a networking or forensics note and meaningless for one
# whose whole subject is code someone will run themselves.
TRANSCRIPT_SHAPED = {"shows nothing", "no worked example", "slow to first command",
                     "command block(s), no output shown"}
FENCE  = re.compile(r"^```", re.M)
INLINE = re.compile(r"`([^`\n]{2,90})`")
TELL   = re.compile(r"\*\*How you'd spot(?: the [^:]{1,40})?:\*\*(.*?)(?=\n\n|\n#|\Z)", re.S)

TOOL = re.compile(r"^(sudo\s+)?([a-z][\w.\-]{1,20})\b")
# a span only counts as a command if it carries a flag, a path, or a subcommand
LOOKS_RUNNABLE = re.compile(r"\s-{1,2}[A-Za-z]|\s/|\s[a-z]+\s")
NOT_A_COMMAND = re.compile(r"[|<>{}]|\.\.\.|^[A-Z]|_")


def commands_in(span):
    """The tool name a runnable-looking inline span invokes, or None."""
    s = span.strip()
    if NOT_A_COMMAND.search(s) or not LOOKS_RUNNABLE.search(s):
        return None
    m = TOOL.match(s)
    return m.group(2) if m else None


def is_index(path, text, words):
    stem = os.path.splitext(os.path.basename(path))[0]
    parent = os.path.basename(os.path.dirname(path))
    return stem == parent or "Zero-to-Mastery Learning Path" in text or words < 250


def gate_findings():
    out = defaultdict(list)
    for script in ("ci-check.py", "pedagogy-check.py"):
        p = subprocess.run([sys.executable, os.path.join(ROOT, "docs", "scripts", script), "--warnings"],
                           cwd=ROOT, capture_output=True, text=True)
        for line in (p.stdout + p.stderr).splitlines():
            # the gates prefix each finding with a severity token; drop it before
            # the path match, or the path captured includes it and matches nothing
            line = re.sub(r"^(todo|warn|error|note|-)\s+", "", line.strip())
            m = re.match(r"(.*?\.md)(?::\d+)?:\s*(.*)$", line)
            if m:
                out[m.group(1)].append(m.group(2))
    return out


def collect(root):
    notes = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP and not d.startswith(".")]
        for f in sorted(fn):
            if f.endswith(".md"):
                p = os.path.join(dp, f)
                notes[os.path.relpath(p, root)] = open(p, encoding="utf-8").read()
    return notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--csv")
    ap.add_argument("--gaps", action="store_true", help="list tools the corpus names but never demonstrates")
    a = ap.parse_args()

    notes = collect(ROOT)
    gate = gate_findings()

    # every tool the corpus demonstrates anywhere, from the fenced blocks
    shown_anywhere = set()
    for text in notes.values():
        for b in BLOCK.findall(text):
            for line in b.splitlines():
                m = TOOL.match(line.strip())
                if m:
                    shown_anywhere.add(m.group(2))

    rows, corpus_gaps, skipped = [], defaultdict(set), 0

    for rel, text in notes.items():
        words = len(text.split())
        if is_index(os.path.join(ROOT, rel), text, words):
            skipped += 1
            continue

        blocks = "\n".join(BLOCK.findall(text))
        prose = BLOCK.sub("", text)
        shown_here = set()
        for line in blocks.splitlines():
            m = TOOL.match(line.strip())
            if m:
                shown_here.add(m.group(2))

        code_note = bool(SOURCE.search(text))

        score, labels = 0, []
        for msg in gate.get(rel, []):
            for pat, w, label in WEIGHTS:
                if pat.search(msg):
                    if code_note and label in TRANSCRIPT_SHAPED:
                        break
                    if w:
                        score += w
                        labels.append(label)
                    break

        # the Tell names a check the note does not show
        missing_in_tell = set()
        for tell in TELL.findall(prose):
            for span in INLINE.findall(tell):
                tool = commands_in(span)
                if tool and tool not in shown_here:
                    missing_in_tell.add(span.strip())
        if missing_in_tell:
            score += 5
            labels.append("Tell names a check it never shows (%s)" % ", ".join(sorted(missing_in_tell)[:2]))

        # tools this note names that nothing in the corpus ever demonstrates
        for span in INLINE.findall(prose):
            tool = commands_in(span)
            if tool and tool not in shown_anywhere:
                corpus_gaps[tool].add(rel)

        runs = len(re.findall(r"```(?:bash|sh|shell|console)\n", text))
        outs = len(re.findall(r"```(?:text|output|console)\n", text))
        if runs and outs == 0 and not code_note:
            score += 3
            labels.append("%d command block(s), no output shown" % runs)
        if words > 400 and not FENCE.search(text):
            score += 4
            labels.append("no code, output or diagram anywhere")

        if score:
            rows.append((score, words, rel, labels))

    rows.sort(key=lambda r: (-r[0], r[1]))

    if a.gaps:
        print("Tools the corpus names in prose and demonstrates nowhere:\n")
        for tool, where in sorted(corpus_gaps.items(), key=lambda kv: -len(kv[1])):
            print("  %-16s named in %d note(s)  e.g. %s" % (tool, len(where), sorted(where)[0]))
        return

    print("%d content notes carry findings (%d index/orientation pages skipped)\n" % (len(rows), skipped))
    print("%-5s %-7s %s" % ("score", "words", "note"))
    print("-" * 100)
    for score, words, rel, labels in (rows if a.all else rows[:a.top]):
        print("%-5d %-7d %s" % (score, words, rel))
        print("%13s %s" % ("", "; ".join(sorted(set(labels)))))
    if not a.all and len(rows) > a.top:
        print("\n... %d more; --all to list, --csv to export, --gaps for corpus-wide holes"
              % (len(rows) - a.top))

    if a.csv:
        with open(a.csv, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["score", "words", "note", "findings"])
            for r in rows:
                w.writerow([r[0], r[1], r[2], "; ".join(sorted(set(r[3])))])
        print("\nwrote %s" % a.csv)


if __name__ == "__main__":
    main()
