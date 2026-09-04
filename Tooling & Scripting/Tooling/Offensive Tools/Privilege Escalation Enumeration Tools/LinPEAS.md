---
title: "LinPEAS"
aliases: ["linpeas", "PEASS-ng"]
tags: [tree/tooling, cyber/tooling/offensive/privesc/linpeas, type/tool, difficulty/hard]
Domain: "[[Privilege Escalation Enumeration Tools]]"
Color: "#708090"
---

# LinPEAS

> [!abstract] Note of [[Privilege Escalation Enumeration Tools]]
> LinPEAS runs hundreds of local privilege-escalation checks and colour-ranks the results — which is its value and its trap, because the colour is a heuristic and the finding that works is often uncoloured. This note covers how to read the ranking by specificity rather than by colour, and why a read-only script that changes nothing is still one of the loudest things you can run on a host.

LinPEAS (part of PEASS-ng) is *the* Linux privilege-escalation enumeration script. Dropped onto a compromised host, it inspects hundreds of local vectors — SUID binaries, sudo rules, cron jobs, writable paths, kernel version, capabilities, cleartext credentials — and prints a **colour-ranked** report so you can jump straight to the likely path to root. It is read-only reconnaissance; it changes nothing.

> [!warning] Authorized post-exploitation only
> Run only on hosts you are authorized to assess. LinPEAS is noisy (thousands of reads and commands) and will appear in host telemetry.

## Parent Learning Order
LinPEAS -> WinPEAS

## Finding the one thing that trusts you too much

> *Escalating to root means finding one thing. What kind of thing?*
>
> Hold your answer — the section below is the response.

Escalating from a normal user to root means finding **one thing that is misconfigured to trust you more than it should**: a program that runs as root but you can influence, a file root reads that you can write, or a kernel old enough to have a known exploit. The vectors are always the same handful of categories.

The left column of the diagram is LinPEAS's entire checklist. You do not memorise commands for each — LinPEAS runs them all — but you must recognise the categories so you can *read the output*: a writable SUID binary means "check GTFOBins," a `NOPASSWD` sudo rule means "run that command as root," an old kernel means "look up a CVE."

**The deliberate break:** LinPEAS colours its output red and yellow, and the reflex is to read the highlights as a findings list — work down the red lines and you have your escalation.

The colouring is a heuristic ranking, not a verdict, and its least reliable output is the one that looks most exciting. A red kernel line is a *version match*, and enterprise distributions back-port security fixes without changing the version string, so the same banner appears on exploitable and patched hosts alike. Meanwhile the finding that actually works is frequently uncoloured, because LinPEAS has no signature for it — a custom SUID binary nobody has catalogued, a cron entry referencing a directory you happen to own, a backup script running as root that reads a file you can write. The tool enumerates; the decision is still yours.

**How you'd spot it:** rank by specificity rather than by colour. A named misconfiguration you can point at — this file, this path, this sudo rule — is worth more than any "possible exploit" line derived from a version number. Verify a kernel candidate against the distribution's changelog before pursuing it, and read the uncoloured sections in full, particularly writable paths, cron, and anything in root's `PATH` that you can reach.

## Running it, and keeping the output as evidence

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

## Reading the colour ranking correctly

LinPEAS ranks findings with a colour scheme, and the single most important skill is reading that ranking correctly:

```shell-session
low@target:/tmp$ ./linpeas.sh | grep -i 'RED\|99%'
   [95%+ PE] /usr/bin/find is SUID (GTFOBins escape)
low@hardened:/tmp$ ./linpeas.sh -a | grep -c '95%'
0
```

**The deliberate break / contrast:** on the vulnerable host, LinPEAS flags the SUID `find` at high confidence; on a hardened host the same sweep finds **nothing** at that confidence — the SUID bit is stripped, sudo is tightly scoped, the kernel is patched. But note the trap in the *other* direction: LinPEAS colour is a **heuristic, not proof**. A yellow "possible" finding may be a dead end (e.g., a SUID binary with no GTFOBins entry), and a genuinely exploitable path can appear un-highlighted if it is novel. You verify every candidate by hand; LinPEAS narrows 300 checks to 3, it does not exploit for you.

Operational internals: run with `-a` for all checks (slower, thorough) or targeted flags to stay quiet; LinPEAS works even without root by reading what your user can; and because it shells out to many binaries, a locked-down host (no `curl`/`wget`, restricted `/tmp` noexec) forces you to transfer and run it creatively — itself a signal of a well-hardened target.

## Security Implications

**Read-only does not mean quiet — the reading is the signal.** LinPEAS changes nothing, but it shells out to hundreds of binaries in seconds: a burst of `find`, `cat`, `ss`, `ls`, `getcap` and dozens more, all spawned by one low-privileged user in a tight window. To `auditd` or Sysmon-for-Linux that exec storm has no benign equivalent, and it is a far stronger detection than any file signature because it does not depend on recognising the script.

**Getting it onto the host is its own IOC.** A `curl`/`wget` of `linpeas.sh` into `/tmp`, a `chmod +x`, and an execution from a world-writable directory is a recognisable drop-and-run sequence. A host that blocks it — no outbound fetch tools, `/tmp` mounted `noexec` — forces creative transfer, which is itself evidence of a hardened target.

**The findings are hygiene failures the defender should have found first.** Every category LinPEAS ranks — writable SUID binaries, `NOPASSWD` sudo rules, world-writable cron targets, cleartext credentials in config files — is a misconfiguration the host owner can enumerate on their own systems with the same tool. The durable fix is removing the misconfiguration, not detecting the scanner, because the scanner only reads what a real attacker would read by hand.

All use here is authorised post-exploitation on in-scope hosts; the sweep is noisy and attributable by design.

## Summary

You should now be able to:

- Name the one thing every privilege-escalation vector has in common.
- LinPEAS highlights `(root) NOPASSWD: /usr/bin/tar`. Turn it into a root shell and explain why it works.
- Explain why LinPEAS's colour ranking is a heuristic, and why a low-confidence line still needs manual verification (both directions of error).

---
> 🔼 Up: [[Privilege Escalation Enumeration Tools]]
