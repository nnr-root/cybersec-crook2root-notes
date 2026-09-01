---
title: "Linux I/O Redirection & Piping"
aliases: ["IO Redirection", "Piping", "Pipes", "Command Chaining", "Redirection"]
tags:
  - tree/os
  - cyber/foundations/linux
  - type/technique
  - difficulty/easy
  - level/apprentice
Domain:
  - "[[Linux]]"
Color: "#FFA500"
---

# 🔗 Linux I/O Redirection & Piping

> [!abstract] Master Note of [[Linux]]
> The Unix philosophy: small tools that each do one thing, **composed** into something powerful. Redirection and pipes are the glue. Master these operators and you can answer almost any question about a system in a single line — the jump from *typing* commands to *engineering* them.

## Parent Learning Order
Linux Introduction & Distributions -> Linux CLI & Core Commands -> Linux I-O Redirection & Piping -> Linux File System Hierarchy & Editors -> Linux Boot Process & systemd -> Linux Permissions & Process Management -> Linux Memory & Storage Internals -> Linux Networking, Transfers & Curl -> Linux Security Controls & Hardening -> Linux Observability, Logging & Forensics -> Linux Advanced Mechanics & Privilege Escalation -> Linux Kernel Internals -> Linux Documentation & Note-Taking

## Start from zero — programs exchange byte streams

A command-line program usually begins with three open **file descriptors**: standard input (`0`), standard output (`1`), and standard error (`2`). A descriptor is a small process-local integer referring to an open kernel object. The object might be a terminal, regular file, pipe, socket, or device. Programs read and write bytes; the shell decides where those bytes come from and go to before execution begins.

A **redirection** changes one command's descriptor destination. A **pipeline** connects one process's output to another process's input through a bounded kernel buffer. A **separator** decides whether commands run sequentially, conditionally, concurrently, or in a shared syntactic expression. These are related but different operations. The symbols are interpreted by the shell, not normally passed as arguments to the program.

Prerequisites are intentionally small: know how to run `printf`, `cat`, and `wc`, and know that zero exit status means success. Use `printf` instead of ambiguous `echo` behavior in scripts. Start with harmless text in a temporary directory, predict the descriptor graph on paper, execute the line, then compare stdout, stderr, files, and `$?` with your prediction. That habit scales from a two-command pipeline to production evidence processing.

> [!tip] The analogy, and where it breaks
> An assembly line where each worker takes what the previous one produced and passes the result along, never storing the whole batch. The analogy breaks in one important place: the line has a *second* chute for rejects (stderr) which by default does not follow the main belt, which is why errors appear on screen even when output is redirected to a file.

## The three streams
Every process has three default channels, each with a **file descriptor** number:

- **stdin (0)** — input, normally the keyboard.
- **stdout (1)** — normal output, normally the screen.
- **stderr (2)** — error output, also the screen but a *separate* stream (so you can split errors from results).

Redirection rewires these streams to/from files; pipes wire one process's stdout into the next's stdin.

## The operators
| Operator | Meaning | Example |
| --- | --- | --- |
| `\|` | **Pipe** — stdout of left → stdin of right | `cat f \| grep err` |
| `>` | Redirect stdout to a file (**overwrite**) | `nmap ... > scan.txt` |
| `>>` | Redirect stdout to a file (**append**) | `echo done >> log` |
| `<` | Feed a file into stdin | `mysql db < dump.sql` |
| `2>` | Redirect **stderr** | `find / 2> /dev/null` |
| `&>` / `>&` | Redirect **both** stdout+stderr | `cmd &> all.log` |
| `2>&1` | Send stderr to *wherever stdout goes* | `cmd > all.log 2>&1` |
| `;` | Run sequentially, **regardless** of success | `id; hostname` |
| `&&` | Run next **only if** previous **succeeded** | `make && ./run` |
| `\|\|` | Run next **only if** previous **failed** | `ping -c1 h \|\| echo DOWN` |
| `&` | Run the command in the **background** | `python3 -m http.server &` |

## Why `2>/dev/null` is everywhere
`find` and friends spam `Permission denied` to **stderr** for every directory you can't read. Sending stream **2** to the black-hole device `/dev/null` discards that noise, leaving only real results on stdout:
```shell-session
$ find / -perm -4000 -type f 2>/dev/null      # only the SUID hits, no error flood
/usr/bin/sudo
/usr/bin/passwd
```

## The glue tools you pipe into
| Tool | Job | Example |
| --- | --- | --- |
| `grep` | keep matching lines | `... \| grep 200` |
| `cut -d: -f1` | slice columns by delimiter | `cut -d: -f1 /etc/passwd` |
| `awk '{print $1}'` | field-aware text processing | `... \| awk '{print $9}'` |
| `sed 's/a/b/g'` | stream find-and-replace | `... \| sed 's/ /_/g'` |
| `sort` / `uniq -c` | order / count duplicates | `sort \| uniq -c` |
| `tr` | translate/delete chars | `tr 'A-Z' 'a-z'` |
| `tee file` | write to file **and** screen | `... \| tee out.txt` |
| `xargs` | turn stdin into arguments | `... \| xargs -I{} curl {}` |

## Practical chained one-liners
```shell-session
# Top 10 IPs hitting a web server, by hit count
$ cat access.log | cut -d' ' -f1 | sort | uniq -c | sort -rn | head
   4213 10.10.10.9
    880 198.51.100.9

# Every unique user on the box, from /etc/passwd
$ cut -d: -f1 /etc/passwd | sort

# Hunt secrets across a web root, keep a copy while watching it scroll
$ grep -rniE "password|api[_-]?key|secret" /var/www 2>/dev/null | tee creds.txt

# Only exploit if the host is alive
$ ping -c1 10.10.10.5 &>/dev/null && echo "[+] up, launching" || echo "[-] down"

# Download every URL listed in a file, 4 at a time
$ cat urls.txt | xargs -P4 -I{} wget -q {}

# Extract all IPv4 addresses from any text
$ grep -oE '([0-9]{1,3}\.){3}[0-9]{1,3}' file | sort -u
```

## Command & process substitution
- **`$(...)`** — run a command and drop its **output** in place:
  ```shell-session
  $ kill $(pgrep -f suspicious.py)     # kill by matched name
  $ echo "Kernel: $(uname -r)"         # embed output in a string
  ```
- **`<(...)`** — turn a command's output into a **file** an argument can read:
  ```shell-session
  $ diff <(ls dir1) <(ls dir2)         # compare two listings with no temp files
  ```

## Here-docs & here-strings — feed multi-line input
```shell-session
$ cat <<'EOF' > payload.py             # write a block to a file
import os; os.system("/bin/sh")
EOF
$ base64 -d <<< "cGFzc3dk"             # here-string: feed one line to stdin
passwd
```

> [!tip] Beginner → Expert
> **A beginner** runs `grep`, copies the result, runs the next command by hand. **An expert** pipes the whole investigation into one expression — `cut | sort | uniq -c | sort -rn` is a reflex, not a lookup. Composition *is* the skill.

## How the shell builds a pipeline

Redirection is performed by the shell before the program begins. The shell parses operators, opens the requested files, duplicates file descriptors with operations equivalent to `dup2(2)`, creates pipes with `pipe(2)`, then starts each command. A program normally has no idea whether descriptor 1 points at a terminal, regular file, socket, or pipe. `test -t 1` and `isatty(3)` are how interactive tools detect the difference.

```mermaid
sequenceDiagram
    participant U as Operator
    participant S as Shell parser
    participant K as Kernel FD table
    participant A as Producer
    participant B as Consumer
    U->>S: journalctl -u ssh | grep Failed > hits.txt
    S->>K: open hits.txt; pipe(); fork()
    K-->>A: stdout = pipe write end
    K-->>B: stdin = pipe read end; stdout = hits.txt
    A->>B: byte stream with log records
    B->>K: write matching records to file
    K-->>U: exit status of final pipeline
```

Ordering matters because descriptors are evaluated left to right. `cmd >all.log 2>&1` first points stdout at the file, then duplicates that destination onto stderr. `cmd 2>&1 >all.log` first points stderr at the current terminal and only then moves stdout, so errors remain on screen. Demonstrate this with a command that emits to both streams:

```shell-session
$ sh -c 'echo normal; echo failure >&2' >all.log 2>&1
$ cat all.log
normal
failure
$ sh -c 'echo normal; echo failure >&2' 2>&1 >normal.log
failure
$ cat normal.log
normal
```

Additional descriptors are useful for reliable scripts. `exec 3>audit.log` opens descriptor 3 for the current shell; `printf ... >&3` writes a dedicated audit channel without mixing it into ordinary output. Named pipes created by `mkfifo` provide a filesystem rendezvous between unrelated processes, unlike anonymous pipelines whose endpoints are inherited through process creation.

## Exit status, pipe failure & safe chaining

Every command exits with an integer: zero means success and nonzero means failure. Inspect it with `$?`. In Bash, a pipeline normally returns only the final command's status. That can hide an upstream failure: `false | tee result` appears successful because `tee` succeeded. Enable `set -o pipefail` so the pipeline fails if any component fails. Production scripts commonly begin with `set -Eeuo pipefail`: stop on unhandled errors, reject unset variables, propagate pipeline failures, and preserve error traps.

```bash
#!/usr/bin/env bash
set -Eeuo pipefail
trap 'printf "failed at line %d\n" "$LINENO" >&2' ERR

journalctl --since -1h --no-pager \
  | awk '/Failed password/{print $(NF-3)}' \
  | sort | uniq -c | sort -nr \
  | tee failed_sources.txt
```

Quote expansions unless word splitting is intentional. `rm $dir/*` behaves unpredictably when `$dir` is empty or contains whitespace; `find "$dir" -type f -print0 | xargs -0 ...` safely handles spaces and newlines. Prefer `while IFS= read -r line` for exact line processing. Avoid the useless-use-of-`cat` argument when a tool already accepts a filename, but prioritize readability over dogma.

## Buffering, backpressure & concurrency

A pipe has a finite kernel buffer. If the consumer is slow, the producer blocks when the buffer fills: this is **backpressure**. Programs may line-buffer output to a terminal but block-buffer it in a pipe, causing apparently delayed logs. `stdbuf -oL` can request line buffering for compatible programs. `tee` forks a stream to display and storage; process substitution can send copies to multiple analyzers.

```shell-session
$ sudo tcpdump -l -n -i any tcp port 22 \
    | stdbuf -oL awk '/Flags \[S\]/{print strftime(),$3}' \
    | tee -a syn-observations.log
2026-07-31 14:02:18 192.0.2.40.51544
```

When parallelizing, bound concurrency. `xargs -P8` or GNU `parallel -j8` can accelerate hashing or metadata collection, but unbounded background jobs can exhaust PIDs, descriptors, memory, or network capacity. Preserve input-to-output association with explicit labels and unique output paths.

## Practical forensic pipelines

Pipelines are strongest when every stage has a testable contract. The following counts successful SSH source addresses from structured journal output without editing evidence:

```shell-session
$ journalctl -u ssh --since '2026-07-31 00:00' -o cat --no-pager \
  | sed -nE 's/.*Accepted .* from ([0-9.]+) port.*/\1/p' \
  | sort | uniq -c | sort -nr
     17 10.20.30.14
      3 10.20.30.77
```

For NUL-safe file hashing:

```shell-session
$ find /etc -xdev -type f -print0 \
  | sort -z \
  | xargs -0 sha256sum > etc.sha256
$ wc -l etc.sha256
1847 etc.sha256
```

The `-xdev` boundary prevents traversal into mounted pseudo-filesystems, while NUL delimiters preserve hostile filenames. Never parse `ls` output in automation; use `find -print0`, shell globs, or structured formats.

## Troubleshooting a broken pipeline

Debug pipelines from left to right. Run each stage independently on a small known input, capture its stdout and stderr separately, and confirm its exit status. Then reconnect one pipe at a time. Enable `set -o pipefail` and inspect `PIPESTATUS` immediately after a Bash pipeline; otherwise a successful final formatter can conceal an upstream read or parse failure. Use `set -x` to reveal expansions, but disable it around secrets because traces can expose values.

Empty output may mean the producer emitted nothing, the parser expected a different delimiter, buffering delayed delivery, or an earlier redirection stole the stream. Duplicate records often result from retry or fan-out semantics. A hung pipeline may be waiting for EOF, blocked by backpressure, or reading from the terminal unexpectedly. Check open descriptors and processes with `lsof -p`, `/proc/<pid>/fd`, `ps --forest`, and a bounded `strace -f -e read,write,pipe,dup2` in a lab.

```shell-session
$ set -o pipefail
$ producer | parser | tee result.txt
parser: record 14: invalid field count
$ printf 'pipeline=%d stages=%s\n' "$?" "${PIPESTATUS[*]}"
pipeline=65 stages=0 65 0
```

The correct repair belongs to the failing contract: data format, descriptor routing, quoting, termination, buffering, or status propagation—not an extra `2>/dev/null` that hides evidence.

## Security implications

Shell composition can preserve evidence or destroy it. Unquoted variables, glob expansion, unsafe `eval`, ambiguous redirection, and unchecked pipeline status are common causes of command injection and automation failure. Defensively, use fixed commands, strict mode, least-privileged output paths, explicit delimiters, and immutable source evidence. Operationally, remember that command lines may appear in shell history, audit records, and process listings.

## Summary

You should now be able to:

- distinguish stdin, stdout, stderr, pipes, overwrite, append, and conditional chaining.
- write quoted, NUL-safe pipelines with `pipefail`, structured outputs, bounded parallelism, and reliable error channels.
- explain descriptor duplication and kernel backpressure, debug buffering and hidden failures, and construct evidence-preserving pipelines whose result can be independently verified.

---
> 🔼 Up: [[Linux]]
