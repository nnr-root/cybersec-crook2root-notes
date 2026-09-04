---
title: "GTFOBins"
aliases: ["GTFOBins", "gtfobins"]
tags: [tree/tooling, cyber/tooling/offensive/web-tools/gtfobins, type/tool, difficulty/medium]
Domain: "[[Web-Based Tools & References]]"
Color: "#708090"
---

# GTFOBins

> [!abstract] Note of [[Web-Based Tools & References]]
> GTFOBins is the second half of a LinPEAS finding: it turns "this binary is exploitable" into the exact command that gives you root. This note covers why an ordinary program becomes an escalation path once granted extra power, the `-p` flag that the classic escape depends on, and why the fix is removing the misconfiguration rather than the binary.

GTFOBins (`gtfobins.github.io`) is a curated reference of legitimate Unix binaries that can be **abused to break out of a restricted context** — escalate via SUID or sudo, escape a limited shell, read/write protected files, or transfer data. It doesn't run anything; it's the lookup that turns "I found a weird SUID binary" into "here's the exact command that gives me root."

> [!warning] Authorized privilege escalation only
> The escapes here yield real elevated access. Use only on hosts you are authorized to assess.

## Parent Learning Order
GTFOBins -> LOLBAS -> CrackStation -> Aperisolve -> revshells.com

## Programs that do more than their name suggests

> *`find` finds, `vim` edits, `tar` archives. What else can they do?*
>
> Hold your answer — the section below is the response.

Unix ships hundreds of small programs, and many can do more than their name suggests. `find` can execute commands. `vim` can spawn a shell. `tar` can run a program on checkpoint. If one of those is granted extra power — a **SUID bit** (runs as its owner, often root) or a **sudo rule** — that hidden capability becomes a privilege-escalation path.

```mermaid
flowchart LR
    P["LinPEAS finds: SUID /usr/bin/find  OR  sudo tar"] --> G["look up the binary on GTFOBins"]
    G --> F{"which function is granted?"}
    F -->|SUID| Su["SUID escape command"]
    F -->|sudo| So["sudo escape command"]
    Su --> R["root shell"]
    So --> R
```

GTFOBins is the second half of a **LinPEAS** finding: LinPEAS says *"this binary is exploitable"*; GTFOBins tells you *how*.

## Indexed by the capability you already have

The site indexes each binary by *function* — `shell`, `suid`, `sudo`, `file-read`, `file-write`, `command`, `capabilities`. You look up the binary and the capability you have. Example: LinPEAS reports `find` is SUID-root. GTFOBins' `find` → `suid` entry gives:

```shell-session
low@target:~$ ls -l /usr/bin/find
-rwsr-xr-x 1 root root ... /usr/bin/find
low@target:~$ /usr/bin/find . -exec /bin/sh -p \; -quit
# id
uid=1000(low) euid=0(root)
```

Or a passwordless `sudo tar` (from GTFOBins' `tar` → `sudo` entry):

```shell-session
low@target:~$ sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/sh
# id
uid=0(root)
```

Each entry is a copy-paste recipe, annotated with the exact privilege it requires.

## The -p flag, and why shells drop privilege without it

The **`-p` flag on the `find` escape is not optional** — and forgetting it is the classic mistake:

```shell-session
low@target:~$ /usr/bin/find . -exec /bin/sh \; -quit      # no -p
$ id
uid=1000(low) gid=1000(low)          ← still low-priv!
low@target:~$ /usr/bin/find . -exec /bin/sh -p \; -quit   # -p keeps euid
# id
uid=1000(low) euid=0(root)
```

**The deliberate break:** the SUID binary runs with `euid=0`, but modern shells **drop privileges on startup** unless told not to — `bash`/`sh` reset the effective UID to the real UID for safety. The `-p` flag tells the shell to *preserve* the elevated euid; without it, you spawn a shell as root's child that immediately demotes itself back to you. GTFOBins gives the correct command, but understanding *why* `-p` matters (SUID sets euid, the shell drops it) is the difference between "the recipe didn't work" and root. The deeper lesson: GTFOBins is a map of *why least privilege and removing SUID bits matter* — every entry is a binary a hardened host shouldn't leave exploitable.

**How you'd spot it:** run `id` the instant the shell opens. `euid=0` means you kept the privilege; `uid=1000 … euid=1000` means the shell demoted itself and `-p` was missing. One command separates a working escalation from a shell that merely looks like one.

## Security Implications

**The defence is removing the grant, not the binary.** Every GTFOBins escape needs a *misconfiguration* to work — a SUID bit that need not be set, a sudo rule broader than the task requires. You cannot remove `find` or `tar` from a system, but you can strip the SUID bit and scope the sudoers entry, which closes the path without touching the program. GTFOBins is therefore an audit checklist for the defender: enumerate the host's SUID binaries and sudo rules and check each against the site.

**The abuse has a behavioural signature even though the binary is legitimate.** A SUID binary spawning `/bin/sh`, or `tar`/`vim`/`find` launching a shell as a child, is the tell — the process is trusted but its behaviour is not. That parent-child pattern is what host monitoring keys on, exactly as LOLBAS teaches on Windows.

**`sudo -l` is the finding you want and the audit you should run.** A `NOPASSWD` entry for any binary with a GTFOBins `sudo` function is a direct root path; reading the sudoers policy is both the attacker's first move and the defender's remediation review.

All escalation here is authorised post-exploitation on in-scope hosts; the escapes yield real root.

## Summary

You should now be able to:

- Turn a LinPEAS finding into an actual escalation with GTFOBins.
- Look up and apply the escape for `sudo -l` showing NOPASSWD on `vim`.
- Explain why the `-p` flag is required on the SUID `find` escape, in terms of real vs. effective UID.

---
> 🔼 Up: [[Web-Based Tools & References]]
