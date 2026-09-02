---
title: "Linux Kernel Internals"
aliases: ["Linux Kernel", "eBPF", "cgroups", "namespaces", "Kernel Panic", "LKM"]
tags:
  - tree/os
  - cyber/foundations/linux
  - type/concept
  - difficulty/hard
Domain:
  - "[[Linux]]"
Color: "#FFA500"
---

# 🐧 Linux Kernel Internals

> [!abstract] Note of [[Linux]]
> Above the CLI sits the kernel — and the modern security battleground is here: **namespaces** and **cgroups** (the primitives that *are* containers), **eBPF** (the programmable observability/enforcement layer every serious tool now uses), loadable modules, and the panics that tell you something went very wrong.

## Parent Learning Order
Linux Introduction & Distributions -> Linux CLI & Core Commands -> Linux I-O Redirection & Piping -> Linux File System Hierarchy & Editors -> Linux Boot Process & systemd -> Linux Permissions & Process Management -> Linux Memory & Storage Internals -> Linux Networking, Transfers & Curl -> Linux Security Controls & Hardening -> Linux Observability, Logging & Forensics -> Linux Advanced Mechanics & Privilege Escalation -> Linux Kernel Internals -> Linux Documentation & Note-Taking

## Start from zero — the privileged mediator

> *Your program calls `read()` on a file. It has no ability to touch a disk. What actually happens at that instant?*
>
> Hold your answer — the section below is the response.

An application cannot safely control physical memory, schedule CPUs, or program devices directly. The **kernel** runs in a privileged CPU mode and mediates those shared resources. Ordinary programs run in user mode with isolated virtual address spaces. They request kernel operations through **system calls** such as `openat`, `read`, `mmap`, `clone`, and `sendmsg`. The system-call interface is an **ABI**: a binary contract covering call numbers, registers, argument layout, return values, and error conventions.

Keep mechanism separate from policy. A scheduler mechanism selects runnable tasks; policy determines priorities and quotas. Virtual memory provides mappings; permission and security policies decide which mappings are legal. A driver translates generic kernel operations into device behavior. A namespace changes what selected resources a task can see, while a cgroup accounts for and limits resources. None of these alone is “a container”; container runtimes compose them.

Prerequisites are processes, memory, files, permissions, and basic C-like function notation. Do not begin by loading modules or altering kernel tunables. First trace a harmless userspace command, identify its syscall transitions, and map each result to a kernel subsystem. Expert kernel work is evidence-driven: record exact kernel build, configuration, symbols, architecture, taint, command line, and reproduction conditions before explaining behavior.

> [!tip] The analogy, and where it breaks
> The building's structural engineering and utilities — invisible while working, and the thing every room silently depends on. The analogy breaks because you can safely *observe* this structure while it bears load: eBPF lets you attach instruments to a running kernel without stopping or rebuilding it, which has no real-world construction equivalent.

## User space vs kernel space
Processes run in **user space** (ring 3) and cross into **kernel space** (ring 0) via **syscalls** (`man 2 syscalls`, traced with `strace`). The kernel exposes itself through virtual filesystems: **`/proc`** (process/kernel state), **`/sys`** (device/kernel objects), **`/dev`**. This is the interface attackers and defenders both read.

## Namespaces — the "what a process can see" primitive
Namespaces virtualise global resources so a process gets its own view. Seven kinds: **mount, PID, network, UTS, IPC, user, cgroup**.
```bash
lsns                                   # list namespaces
unshare --user --map-root-user --net bash   # new user+net namespace
nsenter -t <pid> -n ip addr            # enter a container's network ns
```
> **User namespaces** let an unprivileged user be "root" *inside* the namespace — a powerful isolation tool and a recurring **privilege-escalation** surface (many LPE CVEs abuse `CLONE_NEWUSER`). Containers = namespaces + cgroups + capabilities; a container escape is usually a namespace/capability misconfiguration.

## cgroups — the "how much a process can use" primitive
**Control groups (v2)** limit and account CPU, memory, PIDs, and I/O per process group — the resource half of containers.
```bash
cat /sys/fs/cgroup/cgroup.controllers          # available controllers
systemd-cgls ; systemctl status <svc>          # cgroup tree
```
The classic **`release_agent` container-escape** abused a writable cgroup `release_agent` to run code on the host — a canonical example of why cgroup/namespace config is security-critical.

## Capabilities — root, decomposed
Instead of all-or-nothing root, the kernel splits privilege into **capabilities** (`man 7 capabilities`). `CAP_SYS_ADMIN` ("the new root"), `CAP_SYS_PTRACE`, `CAP_NET_RAW`, `CAP_SETUID`.
```bash
getcap -r / 2>/dev/null                 # files with capabilities (privesc hunt)
capsh --print                            # current process capabilities
```

## eBPF — the programmable kernel
**eBPF** runs sandboxed, verified programs inside the kernel on hooks (syscalls, network, tracepoints) without loading a module. It powers modern **observability** (`bpftrace`, `bcc`), **networking** (Cilium), and **security/EDR** (Falco, Tetragon) — and, in offensive research, **stealthy rootkits/hooks**.
```bash
sudo bpftrace -e 'tracepoint:syscalls:sys_enter_execve { printf("%s %s\n", comm, str(args->filename)); }'
sudo execsnoop-bpfcc                     # every exec, live (bcc)
```
> eBPF is double-edged: the same hook that gives a defender per-syscall visibility gives an attacker a kernel-resident vantage point — hence eBPF programs themselves are now audited.

## Loadable Kernel Modules (LKMs)
Drivers/features loaded at runtime — and the classic **kernel rootkit** vector.
```bash
lsmod ; modinfo <mod> ; sudo insmod x.ko ; sudo rmmod x
```
On modern systems **Secure Boot + module signing** block unsigned modules. Kernel exploits (LPE) often target a driver or a race to load code at ring 0.

## Kernel panics & Oops
- An **Oops** is a recoverable kernel error (kills the offending task, logs a stack trace to `dmesg`); a **panic** is unrecoverable (system halts).
- Read them via `dmesg`, `/var/log/kern.log`, or persisted **kdump**/`pstore` crash dumps.
```bash
dmesg -T | grep -iE 'oops|panic|BUG|segfault'
```
> **Defensive signal:** repeated Oopses/segfaults on a service are a fingerprint of **exploit development / fuzzing** in progress (see the Offensive tree's exploit-dev notes).

> [!tip] Beginner → Expert
> **An expert** knows containers are just **namespaces + cgroups + capabilities**, reaches for **eBPF** to watch every `execve` live, hunts file **capabilities** for privesc, and reads `dmesg` panics as either a bug — or someone building an exploit.

## Syscall ABI & execution path

The kernel is a privileged event-driven program. User code cannot directly dereference kernel memory or program hardware; it requests services through the architecture's syscall ABI. On x86-64, the syscall number and arguments are placed in defined registers before the `syscall` instruction transfers control through an entry trampoline. The kernel validates pointers, copies data across the user/kernel boundary, checks credentials and policy, performs work, and returns a value or negative errno. glibc wraps many calls, but applications can invoke the ABI directly.

```mermaid
sequenceDiagram
    participant A as User process
    participant L as libc wrapper
    participant E as Architecture entry code
    participant K as Kernel subsystem
    participant S as LSM/audit/trace hooks
    A->>L: openat(AT_FDCWD, path, O_RDONLY)
    L->>E: syscall instruction + registers
    E->>K: dispatch __x64_sys_openat
    K->>K: copy path; resolve mount/dentry/inode
    K->>S: permission & policy hooks
    S-->>K: allow or -EACCES
    K-->>E: file descriptor or -errno
    E-->>L: return to ring 3
    L-->>A: fd or -1 with errno
```

`strace` observes syscall entry/exit through `ptrace` or seccomp-assisted mechanisms. It reveals the contract between program and kernel, not every internal function. `perf`, ftrace, tracepoints, kprobes, and eBPF provide deeper views with different overhead and trust implications.

```shell-session
$ strace -e trace=openat,read,close -o /tmp/trace.log cat /etc/hostname
labhost
$ sed -n '1,5p' /tmp/trace.log
openat(AT_FDCWD, "/etc/hostname", O_RDONLY) = 3
read(3, "labhost\n", 131072)             = 8
close(3)                                  = 0
```

## Processes, scheduling & synchronization

Linux represents processes and threads as tasks. `clone3` selects which resources a child shares: address space, descriptors, signal handlers, namespaces, and more. The scheduler chooses runnable tasks by class and policy; ordinary workloads use fair scheduling, while real-time policies require careful privilege and admission control. Per-CPU run queues, scheduler domains, CPU affinity, NUMA placement, interrupts, and deferred work affect latency.

Kernel code synchronizes with spinlocks, mutexes, read-copy-update (RCU), atomics, wait queues, and sequence locks. Context determines what may sleep: interrupt context cannot block like process context. Race conditions appear when lifetime or ordering assumptions fail—use-after-free, double-fetch, and time-of-check/time-of-use defects are security-critical examples. Kernel sanitizers such as KASAN, KCSAN, UBSAN, and lockdep help expose these bugs in test kernels.

## Namespaces & cgroups v2 in detail

Namespace membership is per task and inherited across creation unless changed. User namespaces map ranges of UIDs/GIDs between inner and outer views. A namespace does not automatically virtualize every kernel resource, and cross-namespace handles such as file descriptors can intentionally retain access. Inspect `/proc/<pid>/ns`, `uid_map`, `gid_map`, and `mountinfo` rather than trusting container labels.

cgroups v2 presents one unified hierarchy. Controllers distribute resources through files such as `cpu.max`, `memory.max`, `memory.high`, `pids.max`, and `io.max`. A task belongs to one cgroup in the hierarchy. `memory.high` throttles under pressure; `memory.max` is a hard boundary that can trigger cgroup-local OOM selection. Pressure Stall Information (`/proc/pressure/*`) quantifies time tasks are delayed by CPU, memory, or I/O scarcity.

```shell-session
$ systemd-run --user --scope -p MemoryMax=256M -p TasksMax=64 bash
Running scope as unit: run-u236.scope
$ systemctl --user show run-u236.scope -p ControlGroup -p MemoryMax -p TasksMax
ControlGroup=/user.slice/user-1000.slice/user@1000.service/app.slice/run-u236.scope
MemoryMax=268435456
TasksMax=64
$ cat /proc/pressure/memory
some avg10=0.00 avg60=0.03 avg300=0.01 total=924401
```

## eBPF verifier, maps, BTF & CO-RE

An eBPF program is bytecode loaded with the `bpf` syscall and attached to a hook: tracepoint, kprobe, uprobes, cgroup, socket, XDP, traffic control, or LSM. Before loading, the verifier symbolically explores program paths. It tracks register types and ranges, pointer provenance, stack initialization, bounded loops, helper-call contracts, and reference lifetime. Rejection protects kernel integrity; acceptance is not a proof that the program's business logic is correct.

**Maps** are kernel objects shared between eBPF programs and userspace: hashes, arrays, LRU maps, ring buffers, per-CPU maps, program arrays, and others. They carry configuration and telemetry. **BTF** describes kernel and program types. **CO-RE** (Compile Once—Run Everywhere) uses BTF relocations so one object can adapt field offsets across compatible kernels rather than compiling on every target.

```shell-session
$ sudo bpftool prog list
42: tracepoint  name exec_audit  tag 9f2b1a...  gpl
        loaded_at 2026-07-31T15:40:00+0300  uid 0
        xlated 696B  jited 421B  memlock 4096B  map_ids 17
$ sudo bpftool map show id 17
17: ringbuf  name events  flags 0x0
        key 0B  value 0B  max_entries 262144  memlock 266240B
$ sudo bpftool btf list | head
1: name [vmlinux] size 6623451B
```

The eBPF security model depends on kernel version, privilege, unprivileged-BPF policy, JIT hardening, lockdown, and hook type. Restrict who can load programs, inventory pinned objects under `/sys/fs/bpf`, and treat unexpected programs as privileged code.

## io_uring & asynchronous I/O

`io_uring` shares submission and completion rings between user space and kernel to reduce syscall overhead and support asynchronous file/network operations. The application places submission queue entries, the kernel performs work, and completion queue entries report results. Registered buffers, files, personalities, and worker threads improve performance but create complex object lifetimes and a historically rich kernel attack surface. Security baselines may restrict `io_uring` through sysctls, seccomp, or service policy when applications do not require it.

## Modules, symbols & trusted kernel extension

An LKM executes with kernel privilege. `modprobe` resolves dependencies and configuration, while `insmod` loads a specific object. Modules may expose parameters, sysfs objects, device nodes, network protocols, or filesystems. `/proc/kallsyms`, exported symbols, `modinfo`, and `/sys/module` help explain loaded code. Secure Boot lockdown and module-signature enforcement reduce unauthorized loading, but signed vulnerable drivers remain dangerous.

```shell-session
$ cat /proc/sys/kernel/modules_disabled
0
$ modinfo -F signer i915 | head -1
Build time autogenerated kernel key
$ cat /proc/sys/kernel/tainted
0
```

Taint flags record conditions such as proprietary or out-of-tree modules, forced loads, hardware errors, and prior warnings. They do not prove compromise but matter when assessing crash reliability.

## Panic, Oops & crash-debug workflow

An Oops includes fault type, registers, instruction pointer, call trace, loaded modules, CPU/task context, and taint state. Preserve the complete message; the first fault is usually more useful than secondary failures. `pstore` can survive reboot in firmware-backed storage. `kdump` boots a capture kernel after panic and writes a `vmcore`. Offline analysis with matching unstripped `vmlinux`, debug symbols, and the `crash` utility can inspect tasks, stacks, memory, modules, and logs.

```shell-session
$ sudo kdump-config show 2>/dev/null || systemctl status kdump
$ ls -lh /var/crash
total 1.2G
-rw------- 1 root root 1.2G Jul 31 16:02 vmcore
$ crash /usr/lib/debug/boot/vmlinux-6.8.0-45-generic /var/crash/vmcore
crash> sys
KERNEL: 6.8.0-45-generic
PANIC: "BUG: unable to handle page fault"
```

## Troubleshooting from userspace symptom to kernel cause

First decide whether the fault belongs to application logic, the syscall contract, policy enforcement, resource pressure, a driver, or the kernel itself. Preserve `uname -a`, kernel command line, boot ID, taint state, loaded modules, relevant sysctls, cgroup and namespace membership, and the first error timestamp. Reproduce with the smallest workload on the same build. Use `strace` for syscall boundaries, `perf` or tracing for latency and CPU behavior, and kernel logs for warnings; do not begin with an invasive probe when a stable interface answers the question.

An `EINVAL` often means arguments violate a syscall or driver contract. `ENOMEM` may describe allocation policy or cgroup limits, not exhausted physical RAM. `EPERM` may be capability, LSM, seccomp, lockdown, or namespace policy. A hung task in `D` state requires its kernel stack and wait channel, not repeated signals. For an Oops, preserve the first complete trace, registers, instruction pointer, task, modules, and matching symbols; later faults may be consequences.

```shell-session
$ ps -o pid,stat,wchan:28,cmd -p 7124
  PID STAT WCHAN                        CMD
 7124 D    io_schedule                  backup-reader
$ sudo cat /proc/7124/stack
[<0>] io_schedule+0x4a/0x80
[<0>] folio_wait_bit_common+0x12b/0x310
[<0>] filemap_read_folio+0x97/0xd0
```

This establishes a storage-backed wait but not its root cause. Correlate block latency, device errors, filesystem state, and the specific mapping before attributing a kernel defect.

**The deliberate break:** namespaces and cgroups are described as isolation, so a container reads as a boundary of roughly the same kind as a virtual machine.

They are **views and limits over a single shared kernel**. Each namespace hides one class of resource and each is opt-in, so the boundary is exactly the set of namespaces that were actually applied — anything not namespaced is shared, a retained file descriptor crosses the view it was opened outside of, and an excess capability reaches straight past the abstraction. And because the kernel is shared, one kernel vulnerability is reachable from inside every container on the host simultaneously. The boundary is real and it is per-resource, which is a different guarantee from a wall.

**How you'd spot it:** enumerate what was *not* isolated rather than admiring what was. The retained capability set from `capsh --print` inside the container, and the cgroup limits applied from outside it, describe the actual boundary far better than the fact that something is containerised. Treat eBPF programs and loadable modules as the same observation from the other direction — anything with that much observability power has exactly that much persistence power, so inventory them and require signing.

## Security implications

Kernel privilege makes small mistakes systemic. Namespace isolation can be pierced by retained handles or excess capabilities; resource control fails when cgroup limits are absent; eBPF and modules create powerful observability and equally powerful persistence surfaces; asynchronous I/O multiplies lifetime complexity. Keep kernels current, minimize enabled attack surface, restrict privileged APIs, enforce signed modules, inventory eBPF objects, and preserve crash evidence.

## Summary

You should now be able to:

- explain user/kernel mode, syscalls, tasks, namespaces, cgroups, capabilities, modules, and panics.
- trace syscalls, inspect namespace mappings and cgroup v2 controls, inventory eBPF maps/programs, and triage an Oops.
- reason about ABI entry, synchronization and lifetime, verifier state, BTF/CO-RE portability, `io_uring`, module trust, and postmortem kernel debugging.

---
> 🔼 Up: [[Linux]]
