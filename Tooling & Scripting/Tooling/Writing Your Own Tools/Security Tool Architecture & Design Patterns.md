---
title: "Security Tool Architecture & Design Patterns"
aliases: ["Security Tool Architecture", "Tool Design Patterns"]
tags: [tree/tooling, cyber/tooling/development/architecture, type/concept, difficulty/hard]
Domain: "[[Writing Your Own Tools]]"
Color: "#708090"
---

# Security Tool Architecture & Design Patterns

Anyone can write a 200-line script that scans or hashes. Turning that into a *tool* — testable, reusable, extensible, and safe to run on a real engagement — is an engineering problem with well-known answers. This note is the architecture that the rest of the "Writing Your Own Tools" branch applies to specific cases.

> [!warning] Authorized tooling
> A security tool that touches targets must carry scope enforcement and reproducible evidence as first-class features, not afterthoughts.

## Parent Learning Order
Security Tool Architecture & Design Patterns -> Building Network Scanners -> Command & Control Design Principles -> Hashsmith Tool Architecture -> ShadowStep Tool Architecture

## Separating the engine from the edges

> *One decision separates a script from a tool. Which decision?*
>
> Hold your answer — the section below is the response.

The single decision that separates a script from a tool is **separating the engine from the edges**.

The layers on the diagram — CLI/config in, a *pure* core engine, pluggable capabilities, bounded concurrency, structured evidence out — are just a disciplined way to keep concerns apart. A script mashes all five into one file; a tool gives each a boundary. The payoff is concrete: a pure engine (no argparse, no sockets) can be unit-tested with plain inputs and reused as a library, and the edges (how args come in, how results go out) become thin and swappable.

## Logic that knows nothing about CLI or output

The core pattern in code — the logic knows nothing about the CLI or the output format:

```python
# engine.py — pure: no argparse, no print, no sys.exit; returns typed results
def scan_port(host: str, port: int, timeout: float) -> PortResult:
    ...                                  # testable with plain inputs

# cli.py — the thin edge that maps argv → engine → JSON
def main(argv):
    args = parse(argv)                   # the ONLY place that reads argv
    results = [scan_port(h, p, args.timeout) for h,p in args.targets]
    emit_json(results)                   # the ONLY place that writes output
```

Then the **strategy/plugin pattern** lets you add capabilities without editing the engine:

```python
CODECS = {}                              # a registry
def register(name): 
    return lambda cls: CODECS.setdefault(name, cls)
@register("base64")
class Base64Codec: ...                   # a new codec = a new file, engine untouched
```

Round it out with a `--dry-run`/scope guard, `--format json` output carrying a run id and versions, unit tests on the engine, and stable exit codes (`0` ok, `1` finding/mismatch, `2` bad invocation).

## The god script, and the moment you try to test it

The anti-pattern this architecture prevents is the **god script** — and you feel its cost the moment you try to test it:

```python
# the god script — everything in one function
def main():
    args = sys.argv                      # CLI
    for host in open(args[1]):           # I/O
        s = socket.socket(); s.connect(...)   # network
        if b"OpenSSH" in banner: print("vuln!")  # logic + output tangled
# → how do you unit-test "is this banner vulnerable?" WITHOUT a live socket?
#   You can't. The logic is welded to argv, the filesystem, and the network.
```

**The deliberate break:** the god script *works* — until you need to test the detection logic, reuse it in another tool, add a second output format, or hand it to a teammate. Every one of those requires a live network and a specific CLI, because the logic is inseparable from the edges. Extract `is_vulnerable(banner) -> bool` into a pure function and it becomes trivially testable with string inputs, reusable anywhere, and stable to refactor. That is the whole lesson: **the value isn't in any one pattern, it's in keeping the core logic free of I/O.** Everything downstream (plugins, concurrency, JSON evidence, scope guards) is easy to add *around* a clean engine and painful to retrofit into a tangled one — which is why architecture is a day-one decision, not a cleanup task.

The payoff is not abstract — it is a test suite that runs in milliseconds with no target at all. Once `is_vulnerable(banner) -> bool` is pure, its entire behaviour is exercised with string literals:

```shell-session
operator@lab:~$ python3 -m pytest test_engine.py -q
test_engine.py::test_openssh_old   PASSED   # is_vulnerable("SSH-2.0-OpenSSH_7.4") is True
test_engine.py::test_openssh_patched PASSED # is_vulnerable("SSH-2.0-OpenSSH_9.6") is False
test_engine.py::test_empty_banner  PASSED   # is_vulnerable("") is False, no crash
3 passed in 0.02s
```

Three edge cases — an old version, a patched one, and the empty banner that a god script would have thrown on — all checked without a socket, a target, or a specific CLI. The same engine now backs a `--format json` flag and a library import for free, because none of them touch the logic. That is the whole return on the architecture: the test that was impossible in the god script is trivial here, and it is impossible to write it *before* the extraction and trivial *after*, which is why the extraction is the first refactor to make.

**How you'd spot it:** the test is whether you can exercise the logic with no network at all. If checking a detection rule requires standing up a live target and driving one specific CLI, the engine and the edges are fused. A pure function taking a banner and returning a boolean is testable with strings, which is why that extraction is the refactor that pays for itself first.

## Summary

You should now be able to:

- Name the single principle that turns a script into a maintainable tool.
- Show how the strategy/registry pattern adds a capability without editing the engine.
- Take a "god script" and explain what becomes possible once the detection logic is extracted into a pure, I/O-free function.

---
> 🔼 Up: [[Writing Your Own Tools]]
