---
title: "Go for Security Engineering"
aliases: ["Golang Security Engineering", "Go"]
tags: [tree/tooling, cyber/tooling/programming/go, type/concept, difficulty/medium]
Domain: "[[Programming for Security]]"
Color: "#708090"
verified: 2026-09-05
---

# Go for Security Engineering

> [!abstract] Note of [[Programming for Security]]
> Go's pitch for security work is one static binary and concurrency cheap enough to stop thinking about. This note covers what that buys, and why the second half of that sentence is the trap — a goroutine costs almost nothing, which is exactly why nothing stops you from opening more sockets than your own machine can hold.

Go is what you graduate to when a Python tool needs to be *fast and deployable*. It compiles to a single static binary you can drop onto any host with no runtime or dependencies, cross-compiles trivially, gives you cheap concurrency, and is memory-safe. That combination — the reason so many modern scanners, agents, and collectors are written in Go (nuclei, RustScan's peers, most cloud tooling).

> [!warning] Authorized use
> Go's easy concurrency makes it easy to build something that floods a target. Bound it.

## Parent Learning Order
Python -> Go -> C++ -> Bash -> PowerShell

## One static binary, cheap concurrency

> *You need to hand a fast concurrent scanner to someone on a machine you have never seen. What makes Go's answer simpler than Python's?*
>
> Hold your answer — the section below is the response.

Go is the **deployable-speed** corner of the map.

Reach for Go when you've outgrown Python's speed or deployment story: you need a fast concurrent tool that runs as *one file* on a stranger's machine. Its two superpowers are the **static binary** (`GOOS`/`GOARCH` cross-compile → a Linux/Windows/ARM executable from your laptop, no interpreter to install) and **goroutines** (concurrency so cheap you can launch thousands) — while staying memory-safe, unlike C++.

**Prerequisites:** Python's concurrency model, and why an interpreter has to be installed before a script can run.

> [!tip] The analogy, and where it breaks
> Hiring is expensive, so a firm that could take on a thousand staff for the price of one would take on a thousand. The analogy breaks on the building: the desks, the phone lines and the front door were sized for a hundred, and none of them belong to the hiring manager. Goroutines are the cheap staff; file descriptors and the target's connection table are the building.

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

**How you'd spot it:** watch descriptors and connection state while the tool runs. `ss -s` climbing into the tens of thousands, or `too many open files` in your own output, means the concurrency is unbounded. The subtler tell is a scan that gets *slower and less accurate* as you raise the worker count — that is the target shedding load and your own stack thrashing, not throughput.

### The same scan, with and without a bound

Twenty thousand ports, dialled two ways, on a host whose descriptor limit has been set to 1024. The program counts its own peak in-flight goroutines and reports the first error that is not an ordinary connection refusal:

```text
unbounded    peak in-flight goroutines:   1046   first non-refusal error: dial tcp 127.0.0.1:1074: socket: too many open files
pool of 200  peak in-flight goroutines:    200   first non-refusal error: <nil>
```

Read the first row carefully, because the failure is not the one people expect. Nothing crashed and no goroutine leaked — Go scheduled every one of them happily. What ran out was a resource Go does not manage: file descriptors, which belong to the operating system and were exhausted at 1024 while the runtime cheerfully queued more work against them. From that point on, `dial` returns an error that has nothing to do with the port being open or closed, and a scanner that does not distinguish the two reports those ports as filtered. **The tool does not fail; it lies.**

Note also that the peak reached 1046, past the limit itself. A goroutine exists before its socket does, so the count of things trying to dial always runs slightly ahead of the count of things that can. There is no worker number that makes this safe by being *close enough* to the limit — the bound has to be well under it.

The second row is the same twenty thousand ports through a pool of two hundred. The peak is exactly two hundred, by construction, and there is no error at all. That is the whole argument for a worker pool: it does not make the scan slower, it makes the concurrency a number you chose rather than a number the port list happened to imply.

## Security Implications

**A single static binary is an operational advantage and a review problem.** Handing a client one file that runs anywhere with no runtime to install is why Go is popular for tooling — and it is why Go is popular for malware. There is no source to read at the far end, so a Go tool arriving in an estate is opaque in a way a Python script is not, and the same property that makes your scanner easy to deploy makes an implant easy to deploy.

**Unbounded concurrency is a denial of service you commit by accident.** The measurement above exhausts the operator's own descriptors; pointed at a client it is thousands of simultaneous connections to their infrastructure. A scan that degrades a production service is an incident regardless of intent, and a worker pool is the difference between a test and an outage.

**The race detector finds what testing cannot.** `go build -race` instruments memory access and reports two goroutines touching shared state without synchronisation. Data races are invisible until they corrupt output, and corrupted output in a security tool is a false negative someone acts on. Running the test suite under `-race` in CI is cheap and is where these are found.

**Errors are values, which means they are ignorable.** Go has no exceptions, so a discarded error is a silent branch — `c, _ := net.Dial(...)` compiles, runs, and treats every failure as a success. In a scanner that is the difference between "closed" and "we never asked". `errcheck` and vetting for the blank identifier catch it.

**Cross-compilation crosses trust boundaries too.** `GOOS=windows go build` from a Linux workstation is a genuine convenience and it means the binary you hand over was never executed on the platform it targets. Test on the target platform before it reaches a client's estate.

All scanning described here must target systems within an authorized scope. Concurrency settings are part of scope: a rate that is fine in a lab is a flood on a production network.

## Summary

You should now be able to:

- Name the two properties that make Go well suited to deployable security tools.
- Write a bounded worker-pool scanner, and show how you'd cross-compile it for Windows.
- Explain why cheap goroutines still need bounding, and what `-race` catches.

---
> 🔼 Up: [[Programming for Security]]
