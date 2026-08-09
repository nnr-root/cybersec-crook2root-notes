---
title: "OS Theory & Architecture"
aliases: ["OS Theory and Architecture", "OS Theory"]
tags:
  - tree/os
  - cyber/moc
Domain:
  - "[[OS Internals]]"
Color: "#FFA500"
---

# 🧠 OS Theory & Architecture

> [!abstract] Sub-index of [[OS Internals]]
> Before platform-specific study, master the **Computer Science & Computer Engineering** principles shared by every operating system: execution, scheduling, memory, storage, and devices. These foundations explain race conditions, resource exhaustion, memory corruption, forensic artifacts, and hardware-backed isolation.

## 🗺️ Zero-to-Mastery Curriculum

1. [[Theory of Processes and Threads|Theory of Processes & Threads]] — begin with execution identity, process and thread state, IPC, synchronization, memory ordering, races, deadlocks, and priority inversion.
2. [[CPU Scheduling Algorithms]] — learn how runnable work receives CPU time, from classical algorithms through fair and real-time scheduling, then model starvation and resource-exhaustion resistance.
3. [[Memory Management and Paging|Memory Management & Paging]] — follow every address through page tables and TLBs, then master demand paging, replacement, COW, NUMA, allocators, corruption primitives, and mitigation layers.
4. [[I-O and File System Paradigms|I-O & File System Paradigms]] — complete the foundation by tracing syscalls through VFS, caches, journals, device queues, interrupts, DMA, IOMMU isolation, crash consistency, and forensic evidence.

## Completion Standard

Finish the laboratory and **Crook → Operator → Root** checkpoint in each masterclass. At Root level, you should be able to move from a symptom—latency, corruption, a crash, lost data, or anomalous device activity—to the responsible OS abstraction and a defensible experiment that proves the root cause.

---
> 🔼 Up: [[OS Internals]]
