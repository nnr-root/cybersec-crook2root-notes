---
title: "Go for Security Engineering"
aliases: ["Golang Security Engineering", "Go"]
tags: [tree/tooling, cyber/tooling/programming/go, type/concept, difficulty/medium]
Domain: "[[Programming for Security]]"
Color: "#708090"
---

# Go for Security Engineering

Go is what you graduate to when a Python tool needs to be *fast and deployable*. It compiles to a single static binary you can drop onto any host with no runtime or dependencies, cross-compiles trivially, gives you cheap concurrency, and is memory-safe. That combination — the reason so many modern scanners, agents, and collectors are written in Go (nuclei, RustScan's peers, most cloud tooling).

> [!warning] Authorized use
> Go's easy concurrency makes it easy to build something that floods a target. Bound it.

## Parent Learning Order
Python -> Go -> C++ -> Bash

## One static binary, cheap concurrency

> *You need to hand a fast concurrent scanner to someone on a machine you have never seen. What makes Go's answer simpler than Python's?*
>
> Hold your answer — the section below is the response.

Go is the **deployable-speed** corner of the map.

Reach for Go when you've outgrown Python's speed or deployment story: you need a fast concurrent tool that runs as *one file* on a stranger's machine. Its two superpowers are the **static binary** (`GOOS`/`GOARCH` cross-compile → a Linux/Windows/ARM executable from your laptop, no interpreter to install) and **goroutines** (concurrency so cheap you can launch thousands) — while staying memory-safe, unlike C++.

## A worker pool over channels

The idiomatic concurrent pattern is a **worker pool over channels**:

```go
func scan(host string, ports []int, workers int) {
    jobs := make(chan int, len(ports))
    var wg sync.WaitGroup
    for w := 0; w < workers; w++ {           // BOUNDED pool of workers
        wg.Add(1)
        go func() {
            defer wg.Done()
            for p := range jobs {
                c, err := net.DialTimeout("tcp", fmt.Sprintf("%s:%d", host, p), 2*time.Second)
                if err == nil { c.Close(); fmt.Printf("%d open\n", p) }
            }
        }()
    }
    for _, p := range ports { jobs <- p }
    close(jobs); wg.Wait()
}
```

```shell-session
$ GOOS=windows GOARCH=amd64 go build -o scan.exe   # cross-compile from Linux → a Windows .exe
```

`context.Context` for cancellation/timeouts, interfaces for pluggable modules, `go test` + `-race` for correctness.

## When goroutines are so cheap you launch too many

Goroutines are *so* cheap that the mistake is launching too many:

```go
// UNBOUNDED — one goroutine per port, all at once
for _, p := range allPorts {         // 65,535 goroutines
    go probe(host, p)                // → thousands of simultaneous sockets
}                                     //   fd exhaustion + a flood of the target
```

**The deliberate break:** because a goroutine costs almost nothing, it's tempting to spawn one per unit of work — and with 65,535 ports you've just opened tens of thousands of concurrent connections, exhausting file descriptors on your side and flooding the target on theirs (the same self-DoS as the hand-built scanner, one language up). Cheap concurrency doesn't remove the need to *bound* it — a fixed **worker pool** (N goroutines draining a channel) keeps in-flight work at a level the OS and target can bear. The `-race` detector is the other Go essential: it catches data races (two goroutines touching shared state) that are invisible until they corrupt output in production. Go's whole value proposition for security work is "concurrent, fast, and a single portable binary" — but the concurrency is a tool you aim, not a firehose you open. When you need *lower* than Go can go (byte-exact layout, no GC pauses, exploit dev), that's the signal to drop to C++.

## Summary

You should now be able to:

- Name the two properties that make Go well suited to deployable security tools.
- Write a bounded worker-pool scanner, and show how you'd cross-compile it for Windows.
- Explain why cheap goroutines still need bounding, and what `-race` catches.

---
> 🔼 Up: [[Programming for Security]]
