---
title: "CPU Scheduling Algorithms"
aliases: ["CPU Scheduling", "FCFS", "Round Robin", "Priority Scheduling", "Starvation", "Deadlock", "Resource Exhaustion"]
tags:
  - tree/os
  - cyber/foundations/theory
  - type/concept
  - difficulty/medium
Domain:
  - "[[OS Theory and Architecture]]"
Color: "#FFA500"
---

# 🧠 CPU Scheduling Algorithms

> [!abstract] Note of [[OS Theory and Architecture]]
> CPU scheduling converts a finite set of processors into the illusion that many tasks progress at once. Policy determines throughput, latency, fairness, deadline guarantees, and resistance to resource exhaustion. A security engineer must understand both the textbook algorithms and the approximations used by real kernels.

## Parent Learning Order
Theory of Processes & Threads -> CPU Scheduling Algorithms -> Memory Management & Paging -> I-O & File System Paradigms

## Prerequisites & First Mental Model

Before studying an algorithm, picture one CPU and three ready tasks. Only one task can execute on that CPU at a time. The operating system therefore needs a policy for deciding **who runs next**, **how long it runs**, and **when it may be interrupted**. That policy is scheduling. On a multicore machine the same problem exists per logical CPU, with added decisions about migration, affinity, shared caches, and NUMA locality.

The minimum vocabulary is:

- A **task** is the schedulable entity—normally a thread in a modern general-purpose OS.
- A **CPU burst** is an interval during which a task performs computation before blocking, yielding, or finishing.
- An **I/O burst** is time spent waiting for storage, networking, a timer, or another event.
- The **ready queue** contains runnable tasks waiting for processor time.
- The **dispatcher** switches the processor from the selected old task to the selected new task.
- A **quantum** or **time slice** is the maximum continuous service granted by a time-sharing policy before reconsideration.
- **Preemption** means the OS interrupts a running task so another can run. **Cooperative** scheduling depends on the running task yielding or blocking.
- **Latency** measures delay, **throughput** measures completed work, and **fairness** measures how service is divided. These goals can conflict.
- A **workload** is the collection and arrival pattern of tasks presented to the scheduler.

Use a grocery checkout as a first analogy, but do not mistake the analogy for the implementation. Customers are tasks, service time is a CPU burst, and checkout lanes are CPUs. FCFS serves arrival order; SJF favors the smallest cart; Round Robin serves a limited number of items before rotating customers. Real tasks differ because their future burst lengths are unknown, they block and wake asynchronously, they share locks, and moving them between processors changes cache locality.

The security question is not merely “is the CPU busy?” It is “can one identity manipulate admission, task count, priority, affinity, or work amplification so another identity receives unacceptably little service?” That question turns textbook scheduling into availability engineering.

### A worked baseline

Suppose `P1`, `P2`, and `P3` arrive at time zero with CPU bursts of 5, 3, and 1 milliseconds. Under FCFS order `P1 → P2 → P3`, their waiting times are 0, 5, and 8 ms. Under SJF order `P3 → P2 → P1`, the waits are 0, 1, and 4 ms. SJF improves the average, but if short jobs arrive forever, `P1` can starve. Every later algorithm is a different answer to this tension between efficiency, responsiveness, predictability, and fairness.

> [!tip] The analogy, and where it breaks
> A single doctor with a full waiting room deciding who is seen next: first-come, shortest-appointment-first, or by triage priority. The analogy breaks because the doctor cannot interrupt a consultation mid-sentence and resume it perfectly later — a preemptive scheduler does exactly that thousands of times a second, and the cost of that switch is itself part of what it must optimise.

## 1. Scheduling Model & Metrics

The **short-term scheduler** selects a runnable thread from a ready queue; the **dispatcher** performs the context switch. Admission and memory-pressure decisions are sometimes described as long-term and medium-term scheduling. Contemporary general-purpose systems schedule threads rather than whole processes because threads are the entities that own CPU contexts.

For process `i`, let arrival time be `Aᵢ`, first execution time `Sᵢ`, completion time `Cᵢ`, and total CPU burst time `Bᵢ`:

- **Turnaround time:** `Cᵢ - Aᵢ`
- **Waiting time:** `Cᵢ - Aᵢ - Bᵢ`
- **Response time:** `Sᵢ - Aᵢ`
- **Throughput:** jobs completed per unit time
- **Utilization:** fraction of available CPU time doing useful work
- **Fairness:** distribution of service relative to weights or entitlements
- **Deadline miss ratio:** critical for real-time systems

Optimizing one metric can damage another. Large batches maximize throughput but delay interactive work. Tiny time slices improve apparent responsiveness until context-switch and cache costs dominate. Security-sensitive infrastructure also needs **isolation**: one tenant's workload should not make another tenant's latency unbounded.

A **non-preemptive** policy lets a running task continue until it exits or blocks. A **preemptive** policy can interrupt it, usually after a timer event or when higher-priority work becomes runnable. Preemption improves responsiveness and fault containment but creates synchronization requirements inside kernels and applications.

**The deliberate break:** the obviously best scheduler is the one that runs the shortest job first — it provably minimises average waiting time, and the proof is not in dispute.

You cannot build it. Shortest-Job-First requires knowing how long each job will run *before* running it, and the operating system has no way to know that. Every real scheduler is therefore an approximation of an optimum it can never reach, guessing future burst length from past behaviour. Once you see that, the entire progression in this note stops being a list of algorithms and becomes a sequence of increasingly good guesses about a fundamentally unknowable quantity.

**How you'd spot the failure:** starvation and priority inversion look alike from outside — a task that never runs. Starvation means higher-priority work keeps arriving; inversion means a *lower*-priority task holds a lock the high-priority one needs. The fix for one makes the other worse, so identify which you have before touching priorities.

## 2. FCFS, SJF & SRTF

**First-Come, First-Served (FCFS)** is a FIFO queue. It is simple and avoids starvation if jobs eventually finish, but a long CPU-bound task at the head creates the **convoy effect**: short I/O-bound tasks wait, devices become idle, then all wake together.

Consider bursts `P1=8`, `P2=4`, and `P3=1`, all arriving at time zero. FCFS order `P1,P2,P3` yields waits `0,8,12`, averaging `6.67`. Ordering by burst length `P3,P2,P1` yields waits `0,1,5`, averaging `2`. This motivates **Shortest Job First (SJF)**, which minimizes average waiting time when burst lengths are known.

Future CPU demand is rarely known, so systems estimate it using exponential averaging:

```text
predicted_next = α × actual_last + (1 - α) × predicted_last
```

With `α` near one, recent behavior dominates; with a smaller `α`, history is smoother. **Shortest Remaining Time First (SRTF)** is preemptive SJF: a newly arrived task preempts the current one when its predicted remaining burst is shorter. Both policies can starve long jobs if short work continuously arrives.

For cybersecurity, the core lesson is adversarial workload shaping. If a service rewards tasks that appear short, a client may split expensive work into many superficially small requests. Admission control must account for aggregate identity, not only individual job size.

## 3. Round Robin

**Round Robin (RR)** gives each runnable task a time quantum `q` and rotates unfinished tasks to the queue tail. With N runnable tasks and negligible overhead, each receives roughly `1/N` of the CPU and waits at most `(N-1)q` before another turn.

Quantum selection is the central trade-off:

- If `q` is too large, RR approaches FCFS and interactive latency suffers.
- If `q` is too small, timer interrupts, context switches, TLB effects, and cache misses consume useful capacity.
- If workload count is unbounded, even a sensible `q` produces unacceptable revisit latency.

Suppose a context switch costs 5 μs. A 1 ms quantum spends about 0.5% of CPU time on the switch itself before accounting for cache disruption; a 50 μs quantum spends about 10%. This simple ratio explains why fairness cannot be pursued independently of hardware cost.

RR protects against a single endless loop better than non-preemptive FCFS, but it does not protect against an identity creating thousands of runnable tasks. Per-user process limits, CPU quotas, and hierarchical scheduling are necessary.

## 4. Priority Scheduling & Inversion

Priority schedulers select the highest-priority runnable thread. Priorities may be static, derived from importance, or dynamically adjusted from observed behavior. Without **aging**, low-priority jobs may starve.

Priority creates a subtle failure when a high-priority task waits for a lock held by a low-priority task while medium-priority tasks keep preempting the holder:

```mermaid
sequenceDiagram
    participant L as Low-priority holder
    participant K as Shared kernel lock
    participant H as High-priority service
    participant M as Medium-priority workload
    L->>K: acquire lock
    H->>K: request lock; block
    loop sustained workload
        M->>M: preempt L and consume CPU
    end
    Note over H,M: effective priority is inverted
    K-->>L: priority inheritance boosts L
    L->>K: finish critical section and release
    K-->>H: wake; acquire lock
```

**Priority inheritance** temporarily raises the holder to the highest waiting priority. A **priority ceiling** assigns a resource a ceiling and raises a holder accordingly, preventing certain deadlocks and bounding inversion. Neither fixes oversized critical sections; security-critical locks need bounded work and observability.

## 5. Multi-Level Feedback Queues

A **Multi-Level Feedback Queue (MLFQ)** approximates SJF without knowing burst lengths. New tasks enter a high-priority queue with short quanta. A task that consumes its quantum is demoted as likely CPU-bound; a task that blocks quickly remains responsive. Lower queues use larger quanta to reduce overhead. Periodic global boosts prevent starvation.

Naive MLFQ is gameable: a program can yield just before its quantum expires to preserve high priority. Robust accounting tracks cumulative CPU use across yields and enforces quotas over a window. This is a recurring security principle—policy must charge the actor for total cost, not trust a behaviorally convenient boundary.

## 6. Fair Scheduling: CFS & EEVDF Concepts

Linux's historical **Completely Fair Scheduler (CFS)** models an ideal processor that runs every task simultaneously at a weighted share. Each task accumulates **virtual runtime**; tasks with less weighted runtime are favored. A red-black tree historically made the leftmost, least-served task efficient to select. Nice values translate into weights, so a higher-weight task's virtual runtime advances more slowly for the same physical CPU time.

Modern Linux scheduling incorporates **Earliest Eligible Virtual Deadline First (EEVDF)** concepts. Tasks become eligible according to lag relative to fair service and receive virtual deadlines based on requested slices. This improves latency behavior while preserving weighted fairness. The lasting idea is more important than one kernel version: production schedulers combine fairness accounting with latency-sensitive selection and per-CPU run queues.

Multiprocessor systems add **CPU affinity**, load balancing, NUMA locality, and migration cost. Moving a thread can lose warm caches and place it far from its memory. Security teams may pin sensitive or high-integrity workloads to dedicated cores to reduce jitter and cross-tenant microarchitectural exposure, although pinning can reduce resilience if poorly planned.

## 7. Real-Time Scheduling

Real-time correctness concerns deadlines, not average speed. **Rate Monotonic Scheduling (RMS)** assigns higher priority to tasks with shorter periods. For N independent periodic tasks with deadlines equal to periods, the classic sufficient utilization bound is:

```text
U = Σ(Cᵢ/Tᵢ) ≤ N(2^(1/N) - 1)
```

The bound approaches about 69.3% as N grows. **Earliest Deadline First (EDF)** dynamically runs the task with the nearest deadline and can theoretically schedule independent preemptible workloads up to 100% utilization under ideal assumptions.

General-purpose kernels also expose fixed-priority FIFO and RR classes. Granting untrusted code real-time priority is dangerous: a non-blocking loop can prevent ordinary administrative and monitoring tasks from running. Systems therefore restrict real-time scheduling, reserve runtime for the kernel, and use watchdogs.

## 8. Starvation, Deadlock & Resource Exhaustion

Scheduler starvation is indefinite denial of CPU service. Lock starvation is indefinite denial of a synchronization resource. Deadlock is a cycle in which no participant can proceed. They are distinct and require different evidence: run-queue delay, lock-wait duration, and wait-for graphs.

Availability attacks exploit amplification. A tiny request may trigger catastrophic regular-expression backtracking, expensive decompression, recursive parsing, cryptographic verification, or an unbounded task fan-out. The adversary spends little while the target consumes many CPU-seconds. Effective defenses include complexity-aware input limits, per-principal budgets, bounded worker pools, timeouts, circuit breakers, and backpressure.

Process floods combine PID-table exhaustion, memory pressure, context switching, and scheduler contention. The safe educational pattern is to model limits—not run a fork bomb. Inspect and constrain a disposable shell or container:

```bash
ulimit -u
ps -eLo pid,tid,psr,stat,pri,ni,pcpu,comm --sort=-pcpu | head
systemd-run --user --scope -p CPUQuota=20% -p TasksMax=64 ./cpu-lab
```

Expected observations:

```text
$ ulimit -u
256
$ systemctl --user status run-*.scope
Tasks: 8 (limit: 64)
CPU: 4.812s
CPUQuotaPerSecUSec=200ms
```

On cgroup v2, `cpu.max` expresses quota and period, while `cpu.stat` exposes usage and throttling:

```text
$ cat /sys/fs/cgroup/c2r-lab/cpu.max
20000 100000
$ cat /sys/fs/cgroup/c2r-lab/cpu.stat
usage_usec 5831042
nr_periods 308
nr_throttled 114
throttled_usec 17299831
```

The nonzero `nr_throttled` proves policy contained CPU demand. In an investigation, correlate it with request rates, identities, thread counts, queue depth, and p95/p99 latency.

## 9. Scheduler Observability & Side Channels

Average CPU usage can hide scheduling failures. Important signals include runnable-queue length, per-thread wait time, involuntary context switches, steal time in virtual machines, throttling time, migrations, and deadline misses. Linux tools such as `ps`, `pidstat`, `vmstat`, `perf sched`, and pressure stall information reveal different layers. Equivalent concepts exist in Windows performance counters and event tracing.

Shared cores also create side channels. Simultaneous multithreading lets mutually untrusted threads contend for execution ports, caches, and predictors. Timing may reveal victim behavior even when page permissions are correct. Mitigations include reducing co-tenancy, core scheduling, disabling SMT for selected threat models, partitioning workloads, and removing secret-dependent control flow.

## 11. Troubleshooting & Evidence Interpretation

Scheduler problems are frequently misdiagnosed because utilization is easier to see than delay. A host can report 40% average CPU while one latency-sensitive thread waits behind affinity constraints, cgroup throttling, lock contention, or a saturated single core. Troubleshoot from the affected thread outward:

| Symptom | Scheduling hypothesis | Confirm with | Distinguish from |
| --- | --- | --- | --- |
| High load average, modest CPU use | runnable or uninterruptible waiters | `vmstat`, task states, pressure stall information | pure CPU saturation |
| One core at 100% | affinity, single-thread bottleneck, IRQ concentration | per-CPU utilization, affinity mask, interrupt counts | whole-host exhaustion |
| Periodic latency spikes | quota-period throttling or timer batching | `cpu.stat`, latency timeline | random application slowness |
| High context-switch rate | too many runnable threads, tiny work units, lock wakeups | `pidstat -w`, scheduler trace | useful parallel throughput |
| Important task delayed | priority inversion or starvation | priorities, lock owner, run-queue delay | deadlock |

Collect a short, time-bounded baseline:

```bash
uptime
vmstat 1 5
pidstat -u -w -p ALL 1 5
cat /proc/pressure/cpu
cat /sys/fs/cgroup/cpu.stat
```

Representative output that indicates cgroup throttling is:

```text
some avg10=18.42 avg60=9.07 avg300=2.31 total=8812452
usage_usec 7219931
nr_periods 412
nr_throttled 189
throttled_usec 24187220
```

The PSI `some` value means at least some runnable work was delayed for CPU. The throttling counters show that a bandwidth policy, not merely global contention, denied execution. If `pidstat -w` shows very high involuntary context switches but useful throughput falls, inspect quantum, wake-up patterns, thread-pool size, and lock contention. If a high-priority thread is sleeping, identify its wait object before blaming the scheduler; it may be correctly blocked on I/O or a mutex.

Avoid three common errors. First, `nice` is a weight and policy input, not an exact percentage guarantee. Second, process CPU percentage can exceed 100% when reporting aggregates across cores. Third, load average on Linux includes certain uninterruptible waits, so it is not a synonym for CPU demand. A defensible conclusion names the constrained resource, the scheduling class and hierarchy involved, the affected identity, the measured delay, and the policy change that restores bounded service.

## Summary

You should now be able to:

- Calculate waiting, response, and turnaround time; distinguish preemptive from non-preemptive scheduling; explain FCFS, SJF, SRTF, RR, and priority scheduling.
- Tune quantum and priority with awareness of context-switch cost; diagnose starvation and inversion; use CPU quotas, task limits, and scheduler telemetry to contain an authorized resource-exhaustion lab.
- Reason about MLFQ gaming, weighted fairness, EEVDF/CFS concepts, SMP/NUMA placement, real-time schedulability, and adversarial workload economics; design policy that preserves availability under hostile multi-tenant demand.

---
> 🔼 Up: [[OS Theory and Architecture]]
