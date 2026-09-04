#!/usr/bin/env python3
"""
Check the arithmetic in addressing notes.

Prose can be reviewed by reading it. Worked examples cannot: a wrong bit in a
binary expansion or a broadcast address that is off by one reads exactly like a
correct one, and a learner doing the conversion by hand is the only person who
will ever notice. This verifies the claims a note makes about addresses:

  - a dotted-decimal address shown beside its binary expansion
  - a dotted-quad mask shown beside a prefix length
  - a mask/prefix/total/usable row in a reference table
  - a stated network, broadcast or host range for a given address and prefix

Everything it checks is arithmetic with one right answer, so a finding here is
a defect rather than an opinion.

usage: addrmath.py [path ...]        (default: the whole repo)
"""
import ipaddress, os, re, sys

SKIP = {".git", ".archive", ".obsidian", "assets", "graphify-out", ".github", ".githooks"}

OCTET = r"(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)"
DOTTED = r"%s(?:\.%s){3}" % (OCTET, OCTET)
BIN8 = r"[01]{8}"
# a binary expansion may carry a space marking the prefix boundary, as ipcalc prints
DOTTED_BIN = r"[01\s]{8,11}(?:\.[01\s]{8,11}){3}"

RE_ADDR_BIN = re.compile(r"(%s)\s*(?:=\s*\d+\s*)?\s+(%s)" % (DOTTED, DOTTED_BIN))
RE_MASK_PFX = re.compile(r"(%s)\s*=\s*(\d{1,2})\b" % DOTTED)
RE_TABLE = re.compile(
    r"^\|\s*`?/(\d{1,2})`?\s*\|\s*`?(%s)`?\s*\|\s*([\d,]+)\s*\|\s*([\d,]+)\s*\|" % DOTTED, re.M)
RE_NETBC = re.compile(
    r"(Network|Broadcast|HostMin|HostMax)\s*:\s*(%s)(?:/(\d{1,2}))?" % DOTTED, re.I)
RE_CTX_PREFIX = re.compile(r"(%s)/(\d{1,2})" % DOTTED)


def b(v):
    return format(v, "08b")


def check(path):
    out = []
    lines = open(path, encoding="utf-8").read().split("\n")
    ctx = None                      # the most recent address/prefix seen above

    for i, line in enumerate(lines, 1):
        m = RE_CTX_PREFIX.search(line)
        if m:
            try:
                ctx = ipaddress.ip_interface("%s/%s" % (m.group(1), m.group(2)))
            except ValueError:
                pass

        # a dotted address beside its binary expansion
        for m in RE_ADDR_BIN.finditer(line):
            dec, bits = m.group(1), m.group(2).replace(" ", "")
            if len(bits) != 35:
                continue
            want = ".".join(b(int(o)) for o in dec.split("."))
            if bits != want:
                bad = [j for j in range(4) if bits.split(".")[j] != want.split(".")[j]]
                out.append("%s:%d: binary does not match %s — octet %s reads %s, should be %s"
                           % (path, i, dec, ", ".join(str(j + 1) for j in bad),
                              ", ".join(bits.split(".")[j] for j in bad),
                              ", ".join(want.split(".")[j] for j in bad)))

        # a dotted mask stated as equal to a prefix length
        for m in RE_MASK_PFX.finditer(line):
            mask, pfx = m.group(1), int(m.group(2))
            if pfx > 32:
                continue
            try:
                real = ipaddress.IPv4Network("0.0.0.0/%s" % mask).prefixlen
            except ValueError:
                continue
            if real != pfx:
                out.append("%s:%d: %s is /%d, written as /%d" % (path, i, mask, real, pfx))

        # a stated network, broadcast or usable bound for the prefix in scope
        if ctx is not None:
            for m in RE_NETBC.finditer(line):
                kind, val = m.group(1).lower(), m.group(2)
                net = ctx.network
                want = {"network": net.network_address,
                        "broadcast": net.broadcast_address,
                        "hostmin": net.network_address + 1,
                        "hostmax": net.broadcast_address - 1}[kind]
                if net.prefixlen >= 31:
                    continue
                if ipaddress.IPv4Address(val) != want:
                    out.append("%s:%d: %s of %s is %s, written as %s"
                               % (path, i, kind, net, want, val))

    # reference tables: prefix, mask, total, usable
    text = "\n".join(lines)
    for m in RE_TABLE.finditer(text):
        pfx, mask, total, usable = int(m.group(1)), m.group(2), \
            int(m.group(3).replace(",", "")), int(m.group(4).replace(",", ""))
        line_no = text[:m.start()].count("\n") + 1
        try:
            real = ipaddress.IPv4Network("0.0.0.0/%s" % mask).prefixlen
        except ValueError:
            continue
        if real != pfx:
            out.append("%s:%d: table row /%d gives mask %s, which is /%d"
                       % (path, line_no, pfx, mask, real))
        want_total = 2 ** (32 - pfx)
        want_usable = want_total - 2 if pfx <= 30 else want_total
        if total != want_total:
            out.append("%s:%d: /%d has %d addresses, table says %d"
                       % (path, line_no, pfx, want_total, total))
        if usable != want_usable:
            out.append("%s:%d: /%d has %d usable, table says %d"
                       % (path, line_no, pfx, want_usable, usable))
    return out


def main():
    roots = sys.argv[1:] or ["."]
    findings, checked = [], 0
    for root in roots:
        if os.path.isfile(root):
            findings += check(root); checked += 1; continue
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d not in SKIP and not d.startswith(".")]
            for f in sorted(fn):
                if f.endswith(".md"):
                    findings += check(os.path.join(dp, f)); checked += 1
    for x in findings:
        print("  " + x)
    print("\n%d file(s) checked, %d arithmetic finding(s)" % (checked, len(findings)))
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main())
