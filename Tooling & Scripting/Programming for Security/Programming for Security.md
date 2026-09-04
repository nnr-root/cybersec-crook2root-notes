---
title: "Programming for Security"
aliases: ["Security Programming"]
tags:
  - tree/tooling
  - cyber/tooling/programming
  - cyber/moc
Domain: "[[Tooling & Scripting]]"
Color: "#708090"
---

# Programming for Security

> [!abstract] Engineering branch
> Languages and engineering practices for safe automation, high-performance utilities, and composable operator workflows.

```mermaid
flowchart LR
    R["Reach for the work"] --> PY["Python: write it fast"]
    PY --> GO["Go: ship one binary"]
    GO --> CPP["C++: control every byte"]
    CPP --> SH["Bash: compose Unix tools"]
    SH --> PS["PowerShell: compose Windows objects"]
```

Read these in order. Each one is reached for when the previous one has run out
of something — speed, portability, control — and the last two are not further
rungs but the two orchestration languages, one per platform.

## 🗺️ Zero-to-Mastery Learning Path

1. [[Python]]
2. [[Go]]
3. [[C++]]
4. [[Bash]]
5. [[PowerShell]]

## Practical selection

| The job | Reach for | Because |
|:--|:--|:--|
| Rapid API, parsing or evidence automation | **Python** | the library exists, and readability outlives the script |
| A portable concurrent binary to hand someone | **Go** | one static file, cheap goroutines, no runtime to install |
| Byte-exact layout, no garbage collector, ABI work | **C++** | nothing between you and the memory — which is the risk too |
| Chaining existing Unix programs into a pipeline | **Bash** | the tools do the work; Bash only connects them |
| Driving Windows, .NET or Active Directory | **PowerShell** | the pipeline carries typed objects, so nothing is parsed |

The two orchestration languages sit at the bottom for the same reason and fail
in opposite ways. Bash passes **text** between programs, so every stage
re-guesses the structure and a filename with a space can become two arguments.
PowerShell passes **objects**, so nothing is re-parsed — and that same reach
into the whole .NET runtime is why it is the most productive
post-exploitation platform on Windows.

---
> 🔼 Up: [[Tooling & Scripting]]
