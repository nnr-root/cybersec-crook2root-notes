#!/usr/bin/env python3
"""
Assign the missing difficulty tags in Networking and OS Internals.

Difficulty answers one question: what does this room assume of the reader?
Each assignment below was made from the note's position in its parent's
curriculum order plus the depth of the subject itself, not from word count.

The five Cryptography notes get `difficulty/info` because they are branch
groupings ("The leaves in this branch"), not lessons — which is also why they
correctly carry no task numbering.

    python3 docs/scripts/tag-difficulty.py            # dry run
    python3 docs/scripts/tag-difficulty.py --apply
"""

import re
import sys

ASSIGN = {
    # ── Networking · Network Foundations (branch 1 — nothing precedes it) ──
    "Networking/Network Foundations/Encapsulation & Protocol Data Units.md": "easy",
    "Networking/Network Foundations/Network Devices & Traffic Paths.md": "easy",
    "Networking/Network Foundations/Reachability Testing & ICMP.md": "easy",

    # ── Networking · Addressing & Subnetting (branch 2) ──
    "Networking/Addressing & Subnetting/Subnetting & CIDR.md": "easy",      # 2/6
    "Networking/Addressing & Subnetting/Address Assignment & DHCP.md": "medium",  # 5/6

    # ── Networking · Switching (branch 3) ──
    "Networking/Switching & the Link Layer/MAC Addressing & Switch Operation.md": "easy",   # 2/6, follows Ethernet
    "Networking/Switching & the Link Layer/ARP & Neighbor Discovery.md": "medium",          # 3/6

    # ── Networking · Routing (branch 4) ──
    "Networking/Routing & the Network Layer/IP Forwarding & the Routing Table.md": "easy",  # 1/6, branch opener
    "Networking/Routing & the Network Layer/Static Routing & Default Gateways.md": "medium",

    # ── Networking · Transport (branch 5) ──
    "Networking/Transport Layer & Sockets/TCP Connections & State.md": "medium",
    "Networking/Transport Layer & Sockets/UDP & Connectionless Transport.md": "medium",

    # ── Networking · Security Architecture (branch 9 — assumes the domain) ──
    "Networking/Network Security Architecture/Firewall Architecture & Policy.md": "medium",

    # ── Networking · Analysis & Troubleshooting (branch 10 — assumes the domain) ──
    "Networking/Network Analysis & Troubleshooting/Packet Capture & Analysis.md": "medium",
    "Networking/Network Analysis & Troubleshooting/Structured Network Troubleshooting.md": "medium",
    "Networking/Network Analysis & Troubleshooting/Connectivity Diagnostics.md": "medium",

    # ── OS Internals · Linux ──
    "OS Internals/Linux/Linux IO Redirection and Piping.md": "easy",     # 3/13
    "OS Internals/Linux/Linux File System Hierarchy.md": "easy",         # 4/13
    "OS Internals/Linux/Linux Permissions and Processes.md": "medium",   # 6/13

    # ── OS Internals · Windows ──
    # Listed 10/14 only because the Windows branch front-loads kernel internals;
    # CMD and batch themselves assume nothing.
    "OS Internals/Windows/Windows Command Prompt & Batch.md": "easy",

    # ── OS Internals · macOS ──
    "OS Internals/macOS/macOS CLI and Unix Backend.md": "easy",          # 2/9
    "OS Internals/macOS/macOS APFS and File System.md": "medium",        # 3/9

    # ── Cryptography branch groupings — navigation, not lessons ──
    "Cryptography/Encoding & Obfuscation.md": "info",
    "Cryptography/Hashing & Passwords.md": "info",
    "Cryptography/Symmetric Encryption.md": "info",
    "Cryptography/Asymmetric Encryption.md": "info",
    "Cryptography/Applied Trust & Tooling.md": "info",
}

TYPE_TAG = re.compile(r"^(\s*-\s*)(type/\S+)\s*$", re.M)
INLINE = re.compile(r"^(tags:\s*\[)(.*?)(\])\s*$", re.M)
BLOCK = re.compile(r"^(tags:\s*\n(?:\s*-\s*\S+\s*\n)+)", re.M)


def add_tag(text, level):
    tag = f"difficulty/{level}"

    # Every entry in ASSIGN is a deliberate decision, so an existing tag is
    # corrected rather than skipped — that is how the Cryptography branch
    # groupings get moved onto difficulty/info.
    existing = re.search(r"difficulty/(info|easy|medium|hard)", text)
    if existing:
        if existing.group(0) == tag:
            return text, "already correct"
        return text.replace(existing.group(0), tag, 1), f"changed from {existing.group(1)}"

    head = text[:1200]

    # inline form:  tags: [a, b, c]
    m = INLINE.search(head)
    if m:
        return text.replace(m.group(0), f"{m.group(1)}{m.group(2)}, {tag}{m.group(3)}", 1), "inline"

    # block form: append after the last type/ entry, else after the last tag line
    m = BLOCK.search(head)
    if m:
        blk = m.group(1)
        t = TYPE_TAG.search(blk)
        if t:
            new = blk.replace(t.group(0), f"{t.group(0)}\n{t.group(1)}{tag}", 1)
        else:
            lines = blk.rstrip("\n").split("\n")
            indent = re.match(r"^(\s*-\s*)", lines[-1]).group(1)
            new = "\n".join(lines + [f"{indent}{tag}"]) + "\n"
        return text.replace(blk, new, 1), "block"

    return text, "NO TAGS BLOCK FOUND"


def main():
    apply = "--apply" in sys.argv
    counts = {}
    for rel, level in ASSIGN.items():
        try:
            src = open(rel, encoding="utf-8").read()
        except FileNotFoundError:
            print(f"  MISSING  {rel}")
            continue
        out, how = add_tag(src, level)
        ok = out != src
        counts[level] = counts.get(level, 0) + (1 if ok else 0)
        print(f"  {'✓' if ok else '·'} difficulty/{level:<7} [{how:<18}] {rel}")
        if ok and apply:
            open(rel, "w", encoding="utf-8").write(out)

    print(f"\n{'APPLIED' if apply else 'DRY RUN'} — " +
          " · ".join(f"{v} × {k}" for k, v in sorted(counts.items())))
    if not apply:
        print("Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
