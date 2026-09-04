---
title: "macOS CLI & Unix Backend"
aliases: ["macOS CLI", "Zsh", "diskutil", "networksetup", "Homebrew"]
tags:
  - tree/os
  - cyber/foundations/macos
  - type/technique
  - difficulty/easy
Domain:
  - "[[macOS]]"
Color: "#FFA500"
---

# 🍎 macOS CLI & Unix Backend

> [!abstract] Note of [[macOS]]
> macOS is Unix-certified, but it is not GNU/Linux wearing a graphical shell. This masterclass develops safe Zsh fluency, maps the BSD userland, teaches Apple-specific administration, and turns native commands into a repeatable security investigation workflow.

## Parent Learning Order
macOS Darwin & XNU Kernel -> macOS CLI & Unix Backend -> macOS APFS & File System -> macOS Processes & Daemons -> macOS Identity, Keychain & Credentials -> macOS Networking Internals -> macOS Security Mechanisms -> macOS Binaries & Runtime Loading -> macOS Observability, Incident Response & Forensics

## Zsh, Unix Semantics & Safe Command Work

> *You type a command name and press Enter. Where does the shell look for it, and in what order?*
>
> Hold your answer — the section below is the response.

### Vocabulary & First Mental Model

A **terminal emulator** is the window that displays a text session. A **shell** is the program inside that session that reads commands; modern macOS uses Zsh by default. A **command** resolves to a shell keyword, function, alias, built-in, script, or executable. An **argument** is one value passed to that command. The **working directory** is the process's current location in the filesystem. An **environment variable** is inherited process configuration; `PATH` is the ordered list of directories searched for executable names. **Standard input**, **standard output**, and **standard error** are streams numbered 0, 1, and 2. An **exit status** of zero conventionally means success; a nonzero value describes failure or a special result.

Use this mental model for every shell line: Zsh first parses and expands the text, resolves the command, constructs an argument vector and redirections, launches or runs the command, then records its exit status. Quoting errors therefore happen before the target utility starts, while utility errors happen after it receives arguments. Distinguishing those phases is the foundation of reliable administration and incident collection.

The default interactive shell is `/bin/zsh`. Login shells read `/etc/zprofile` and then `~/.zprofile`; interactive shells read `/etc/zshrc` and `~/.zshrc`. Environment setup belongs in `.zprofile`, while aliases and interactive behavior normally belong in `.zshrc`. This distinction matters when a command works in Terminal but fails in a LaunchAgent: background jobs do not inherit the same interactive startup files or `PATH`.

```bash
echo "$SHELL"
echo "$ZSH_VERSION"
print -l $path
setopt | sort | sed -n '1,20p'
```

Expected output:

```text
/bin/zsh
5.9
/opt/homebrew/bin
/usr/local/bin
/usr/bin
/bin
/usr/sbin
/sbin
```

Zsh arrays are one-indexed by default, glob qualifiers can select files by metadata, and unquoted glob failures produce `no matches found`. Defensive scripts should use explicit quoting, absolute paths for privileged operations, `set -euo pipefail` where semantics are understood, and a controlled `PATH`. Never assume Linux flags. macOS ships BSD variants of `sed`, `stat`, `date`, `ps`, and other tools; GNU documentation may describe incompatible options.

```bash
# Safe inventory pattern: no changes, explicit paths, timestamped output.
case_dir="$PWD/macos-lab-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$case_dir"
/usr/bin/sw_vers > "$case_dir/sw_vers.txt"
/usr/sbin/system_profiler SPHardwareDataType > "$case_dir/hardware.txt"
/usr/bin/id > "$case_dir/identity.txt"
/usr/bin/shasum -a 256 "$case_dir"/*.txt
```

Basic file investigation combines `file`, `stat`, extended attributes, ACLs, and hashes:

```bash
file /Applications/TextEdit.app/Contents/MacOS/TextEdit
stat -x /Applications/TextEdit.app
ls -leO@ ~/Downloads
xattr -l ~/Downloads/sample.pkg
shasum -a 256 ~/Downloads/sample.pkg
```

`ls -l` does not show the full authorization picture. `-e` prints ACLs, `-O` prints BSD flags, and `-@` prints extended attributes. A quarantined download may therefore look ordinary until `com.apple.quarantine` is examined.

> [!tip] The analogy, and where it breaks
> A polished storefront with a fully equipped workshop behind it — the graphical layer and the Unix command line acting on the same underlying goods. The analogy breaks because the storefront sometimes enforces rules the workshop must also respect: privacy consent prompts can block a command-line action, so the terminal is not an unrestricted back door.

## Native Administration Map

### System Identity & Hardware

```bash
sw_vers
uname -m
sysctl -n machdep.cpu.brand_string 2>/dev/null || true
system_profiler SPHardwareDataType SPSoftwareDataType
scutil --get ComputerName
scutil --get LocalHostName
hostname
```

`sw_vers` provides the product version and build. `uname` provides the Darwin view. `system_profiler` provides rich structured inventory but can be slow, so query only needed data types. `ioreg` traverses IOKit registry data and is valuable for hardware and power investigations.

### Users, Groups & Directory Services

Local identity is resolved through Open Directory, not merely `/etc/passwd`:

```bash
id
dscl . -list /Users UniqueID
dscl . -read /Users/$(id -un)
dscacheutil -q user -a name "$(id -un)"
groups "$(id -un)"
sudo -l
```

System accounts commonly use UIDs below 500 and names beginning with `_`; do not label every such record suspicious. In enterprise fleets, directory search paths may include local and network nodes. `dscl /Search -read /Users/name` reflects that broader search policy.

### Disks, APFS & Mounts

`diskutil` is the supported high-level storage interface. Read-only enumeration should precede any operation that changes a disk:

```bash
diskutil list
diskutil apfs list
diskutil info /
mount
df -h
tmutil listlocalsnapshots /
```

Expected APFS excerpt:

```text
APFS Container (1 found)
|
+-- Container disk3 7A1F...
    Capacity Ceiling (Size): 494.4 GB
    +-> Volume disk3s1 Macintosh HD
    +-> Volume disk3s5 Macintosh HD - Data
```

Commands such as `diskutil eraseDisk`, `apfs deleteVolume`, and `repairVolume` are intentionally excluded from the lab because they can destroy evidence or data.

### Preferences, Property Lists & Profiles

```bash
defaults domains | tr ',' '\n' | sed -n '1,20p'
defaults read com.apple.finder
plutil -p ~/Library/Preferences/com.apple.finder.plist
profiles status -type enrollment
profiles show -type configuration | sed -n '1,80p'
```

`defaults` operates on preference domains and can interact with `cfprefsd`; directly editing a plist while its owning application runs may be overwritten. `plutil` validates and converts XML or binary property lists. Configuration profiles can enforce security controls, VPN settings, certificates, and privacy permissions, so assessment context must include MDM enrollment.

### Network Configuration

```bash
networksetup -listallhardwareports
networksetup -listallnetworkservices
networksetup -getinfo Wi-Fi
networksetup -getdnsservers Wi-Fi
scutil --dns
route -n get default
netstat -rn -f inet
ifconfig
```

Hardware-port names, service names, and BSD interfaces are different namespaces: the service `Wi-Fi` may map to `en0`. `scutil --dns` is more authoritative than reading `/etc/resolv.conf` because macOS uses a dynamic resolver with scoped configurations.

### Processes, Files & Search

```bash
ps aux
pgrep -alf 'process-name'
lsof -nP -iTCP -sTCP:LISTEN
lsof -p 1234
mdfind 'kMDItemFSName == "*.mobileconfig"c'
find ~/Library -type f -mtime -2 -print 2>/dev/null
fs_usage -w -f filesystem 1234
sample 1234 3 1
```

Spotlight (`mdfind`) is fast but reflects indexed data, exclusions, and metadata latency. `find` walks the filesystem directly. Use both and document the limitations.

```mermaid
flowchart LR
    Q["Investigation question"] --> I["Identity: id, dscl, sudo"]
    Q --> S["System: sw_vers, sysctl, system_profiler"]
    Q --> D["Storage: diskutil, mount, tmutil"]
    Q --> N["Network: scutil, networksetup, lsof"]
    Q --> P["Processes: ps, launchctl, sample, fs_usage"]
    Q --> C["Controls: codesign, spctl, profiles, csrutil"]
    I --> E["Timestamped evidence directory"]
    S --> E
    D --> E
    N --> E
    P --> E
    C --> E
    E --> H["Hash, preserve, interpret"]
```

## Homebrew, Architecture Boundaries & Automation

Homebrew installs to `/opt/homebrew` on Apple Silicon and `/usr/local` on Intel. A formula provides command-line software; a cask manages graphical applications or vendor packages; `brew services` integrates selected software with `launchd`.

```bash
brew --prefix
brew config
brew doctor
brew list --versions
brew services list
brew leaves
```

Expected Apple Silicon output begins with:

```text
HOMEBREW_VERSION: 4.x
ORIGIN: https://github.com/Homebrew/brew
HOMEBREW_PREFIX: /opt/homebrew
CPU: octa-core 64-bit arm_firestorm_icestorm
Rosetta 2: false
```

Security hinges on ownership, provenance, and execution context. A user-writable Homebrew binary must never be called by a root LaunchDaemon through an ambiguous `PATH`. Audit scripts for `sudo brew`, unpinned taps, automatic service startup, and shell initialization that prepends untrusted directories.

```bash
ls -ld "$(brew --prefix)" "$(brew --prefix)/bin"
find "$(brew --prefix)/bin" -type l -maxdepth 1 -print | sed -n '1,20p'
codesign -dv --verbose=4 "$(command -v some-tool)" 2>&1
```

Rosetta introduces another boundary. `arch` reports the current execution architecture, while `file` reveals available binary slices:

```bash
arch
file "$(command -v zsh)"
sysctl -in sysctl.proc_translated 2>/dev/null || echo native
```

For repeatable collection, prefer a script that emits command, timestamp, exit status, and output without modifying the host:

```zsh
#!/bin/zsh
set -u
out="${1:-./macos-triage}"
mkdir -p "$out"
run() {
  local name="$1"; shift
  {
    print -r -- "timestamp=$(date -u +%FT%TZ)"
    print -r -- "command=$*"
    "$@"
    print -r -- "exit_status=$?"
  } >"$out/$name.txt" 2>&1
}
run version /usr/bin/sw_vers
run identity /usr/bin/id
run listeners /usr/sbin/lsof -nP -iTCP -sTCP:LISTEN
run extensions /usr/bin/systemextensionsctl list
/usr/bin/shasum -a 256 "$out"/*.txt >"$out/SHA256SUMS"
```

### Shell Parsing, Quoting & Privilege Boundaries

The shell performs expansions before a program receives its argument vector: parameter expansion, command substitution, arithmetic expansion, word splitting in specific contexts, pathname generation, and redirection. Security bugs appear when untrusted text is rebuilt into shell syntax rather than passed as one quoted argument. Prefer arrays and direct execution:

```zsh
files=("$HOME/Library/Application Support"/*.plist(N))
for f in "${files[@]}"; do
  /usr/bin/stat -x "$f"
done
```

Do not use `eval` to process filenames, and do not parse `ls`. NUL-delimited pipelines preserve spaces and newlines where tools support them. Before `sudo`, determine which variables survive, which working directory is used, and which executable path will resolve. A secure privileged script establishes a minimal environment and validates that every path is absolute, expected, and not a symlink when that distinction matters.

```bash
type -a python3
command -v python3
sudo -V | grep -E 'Environment|Path' | sed -n '1,20p'
```

Shell history is useful but incomplete evidence: users can disable it, Zsh may share history among sessions, commands can begin with configured ignore patterns, and secrets may be exposed accidentally. Preserve it under authorization, correlate it with process and file evidence, and never treat absence as proof a command did not run.

## Troubleshooting Workflow

Start with context rather than repeating commands: record architecture, macOS build, shell, effective identity, current directory, `PATH`, active Homebrew prefix, and whether the process runs locally, through SSH, or under launchd. Use `type -a`, `command -v`, `file`, and `codesign -dv` to identify what will actually execute. Compare exit status, stdout, and stderr separately. When a command behaves differently in a script, inspect quoting, glob expansion, locale, permissions, environment inheritance, and Apple Silicon versus Rosetta execution before modifying the system.

**The deliberate break:** macOS is BSD underneath, so Unix habits read as transferring directly — the same commands, the same flags, the same results.

The userland differs in ways that change outcomes **quietly rather than loudly**. BSD tool flags diverge from their GNU equivalents, the default shell is zsh with different globbing and word-splitting rules, Homebrew installs to different prefixes per architecture and may shadow system tools for some users and not others, and System Integrity Protection places directories beyond the reach of root itself. A command copied from a Linux runbook does not error — it succeeds, differently.

**How you'd spot it:** when a familiar command behaves oddly, establish which implementation you actually invoked before debugging the behaviour: `which` and `--version` settle whether you are holding the BSD tool or a Homebrew GNU one, and that single check explains most of these surprises. And read a permission denial while running as root as SIP rather than as permissions — no amount of `chmod` or `sudo` resolves it, and continuing to try obscures the real answer.

## Cybersecurity Implications

- BSD/GNU differences can invalidate collection scripts and quietly omit evidence.
- Interactive shell startup files are common persistence and command-hijacking surfaces.
- `diskutil`, `scutil`, Directory Services, profiles, and extended attributes reveal macOS state that Linux-only workflows miss.
- Absolute paths and controlled environments protect privileged automation from `PATH` substitution.
- Native collection tools reduce deployment friction but still require timestamps, hashes, error capture, and documented limitations.

## Summary

You should now be able to:

- Navigate Zsh safely and explain why BSD flags differ from GNU/Linux.
- Build a non-destructive inventory using native identity, storage, network, process, and control commands with realistic output interpretation.
- Automate forensic-quality collection across Intel and Apple Silicon while controlling `PATH`, architecture translation, privileges, provenance, and evidence integrity.

---
> 🔼 Up: [[macOS]]
