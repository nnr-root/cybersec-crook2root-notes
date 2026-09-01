---
title: "Linux Boot Process & systemd"
aliases: ["Linux Boot", "systemd Boot", "initramfs", "PID 1"]
tags:
  - tree/os
  - cyber/foundations/linux
  - cyber/defensive/boot-security
  - type/concept
  - difficulty/medium
Domain:
  - "[[Linux]]"
Color: "#FFA500"
---

# 🚀 Linux Boot Process & systemd

> [!abstract] Master Note of [[Linux]]
> Follow Linux from powered-off silicon to a usable multi-user system. The boot chain is both a reliability pipeline and a chain of trust: firmware chooses code, the bootloader chooses a kernel, initramfs discovers the real root, and PID 1 constructs userspace.

## Parent Learning Order
Linux Introduction & Distributions -> Linux CLI & Core Commands -> Linux I-O Redirection & Piping -> Linux File System Hierarchy & Editors -> Linux Boot Process & systemd -> Linux Permissions & Process Management -> Linux Memory & Storage Internals -> Linux Networking, Transfers & Curl -> Linux Security Controls & Hardening -> Linux Observability, Logging & Forensics -> Linux Advanced Mechanics & Privilege Escalation -> Linux Kernel Internals -> Linux Documentation & Note-Taking

## Start from zero — why boot exists

> *Power arrives and RAM contains no operating system at all. What runs first, and how does it know where to find a kernel?*
>
> Hold your answer — the section below is the response.

When power arrives, RAM contains no operating system and the CPU begins at a firmware-defined reset location. **Booting** is the staged process that discovers hardware, selects trusted code, places a kernel and its initial data in memory, establishes the real root filesystem, and starts the long-running services that make the machine useful. Each stage has only enough knowledge to load the next one; no single component performs the entire job.

Learn five roles before their implementation details. **Firmware** initializes the platform and chooses a boot entry. A **bootloader** selects and loads a kernel. The **kernel** initializes privileged execution, memory, devices, and scheduling. An **initramfs** is a temporary early userspace that can unlock or assemble the storage containing `/`. **PID 1** is the first process in the real userspace and supervises service startup and shutdown; on most current distributions it is systemd.

Prerequisites are the concepts of CPU, RAM, filesystem, process, and service. You do not need to know UEFI variables or unit syntax yet. First memorize the causal chain and ask one diagnostic question at every transition: what component is running now, what artifact must it find, what evidence proves success, and where would its failure be recorded?

> [!tip] The analogy, and where it breaks
> Waking a large building: the caretaker checks the doors, the lights come on floor by floor, and each department opens only once the ones it depends on are ready. The analogy breaks because the building can also start most departments *simultaneously* rather than in sequence — systemd's parallel, dependency-driven startup is what makes a modern boot fast and its failures harder to read.

## Boot as a chain of custody

Power-on begins in platform firmware. Legacy BIOS executes a boot sector with few integrity guarantees. Modern UEFI initializes hardware, exposes boot services and variables, and loads EFI executables from an EFI System Partition. With **Secure Boot**, firmware verifies the next component against trusted keys. Many distributions load a signed shim, which verifies GRUB or a unified kernel image, which in turn verifies or selects the kernel and initramfs. Secure Boot proves approved code identity; it does not prove that approved code is bug-free or configured safely.

The bootloader selects a kernel image, initramfs, command line, and sometimes device tree. The compressed kernel unpacks, initializes architecture state, memory management, scheduler, interrupts, and built-in drivers, then mounts the initramfs as a temporary root. The kernel starts its first userspace program—normally `/init` in initramfs. Early userspace loads storage drivers, assembles RAID/LVM, unlocks LUKS, discovers the root filesystem, and performs `switch_root` into it. The kernel then executes the real init, normally systemd as PID 1.

```mermaid
sequenceDiagram
    participant H as Hardware
    participant F as UEFI firmware
    participant B as shim/bootloader
    participant K as Linux kernel
    participant I as initramfs /init
    participant S as systemd PID 1
    participant U as Multi-user services
    H->>F: Reset vector & platform initialization
    F->>F: Verify Secure Boot policy
    F->>B: Load signed EFI executable
    B->>B: Select entry, kernel, initramfs & cmdline
    B->>K: Exit boot services & transfer control
    K->>K: Decompress; CPU, memory, scheduler & drivers
    K->>I: Mount temporary root; execute /init
    I->>I: Discover storage; unlock LUKS; activate LVM
    I->>K: Mount real root; switch_root
    K->>S: exec /sbin/init as PID 1
    S->>S: Load units; resolve dependency transaction
    S->>U: Start targets, sockets, mounts & services
```


## Firmware, boot entries & kernel command line

UEFI boot variables identify loader paths and order. `efibootmgr -v` displays them. The EFI System Partition is normally FAT and mounted at `/boot/efi`; access should be restricted because modifying a trusted loader path can persist below userspace. Measured boot extends hashes into TPM Platform Configuration Registers, enabling remote attestation or secrets bound to expected measurements. It complements Secure Boot by recording what executed.

The kernel command line is security-sensitive. It controls root device, console, LSM selection, IOMMU, mitigations, recovery behavior, and debugging. Inspect it through `/proc/cmdline`. Options that disable mitigations, enable permissive modes, expose serial consoles, or start an emergency shell can weaken the system. Protect bootloader editing with platform policy and disk encryption; otherwise an operator with physical access may change arguments.

```shell-session
$ cat /proc/cmdline
BOOT_IMAGE=/vmlinuz-6.8.0-45-generic root=/dev/mapper/vg-root ro quiet splash iommu=on
$ bootctl status 2>/dev/null | sed -n '1,12p'
System:
      Firmware: UEFI 2.80
 Firmware Arch: x64
   Secure Boot: enabled
  TPM2 Support: yes
$ efibootmgr -v | head -3
BootCurrent: 0003
BootOrder: 0003,0001
Boot0003* Linux Boot Manager HD(...)/File(\\EFI\\systemd\\systemd-bootx64.efi)
```

## Kernel initialization & initramfs

Early kernel messages reveal CPU features, memory map, security mitigations, driver binding, and root discovery. `dmesg` may be restricted because addresses and hardware details help attackers; use authorized elevated access. Built-in drivers are available before mounting a filesystem, while loadable modules in initramfs support storage, encryption, and filesystems needed for root.

An initramfs is a compressed cpio archive. Distribution generators such as dracut or initramfs-tools assemble hooks, modules, firmware, cryptsetup, and configuration. A missing NVMe, RAID, LVM, dm-crypt, or filesystem module commonly produces an emergency shell because root cannot be found. Regenerate initramfs after changing storage-critical drivers or cryptographic configuration, and retain a known-good kernel entry.

```shell-session
$ lsinitramfs /boot/initrd.img-$(uname -r) | grep -E 'cryptroot|dm-crypt|nvme' | head
usr/lib/modules/6.8.0-45-generic/kernel/drivers/nvme/host/nvme.ko.zst
scripts/local-top/cryptroot
$ systemd-analyze time
Startup finished in 8.421s (firmware) + 2.318s (loader) + 3.774s (kernel) + 6.902s (userspace) = 21.416s
graphical.target reached after 6.201s in userspace.
```

**The deliberate break:** systemd is often described as "init with more features," which implies it does the same thing in the same order, only bigger.

It does not run things in an order at all. systemd is a **dependency engine**: it starts everything whose dependencies are satisfied, in parallel, as soon as they are satisfied. There is no script executing top to bottom. That is why boot got faster, and it is also why a service that "worked yesterday" can fail today with no configuration change — the race it had been winning, it lost. If you are looking for the line that starts your service, there isn't one; there is a declared relationship, and it may not say what you assume.

**How you'd spot it:** `systemd-analyze critical-chain` shows what actually gated the boot, and `systemctl list-dependencies` shows the relationships. A service failing intermittently at boot is almost always a missing `After=` or `Requires=`, not a broken service.

## systemd: dependency engine & supervisor

PID 1 has special duties: adopt orphaned descendants, reap exited children, establish the service graph, manage shutdown, and react to kernel/userspace events. systemd models resources as units: services, sockets, timers, paths, mounts, automounts, devices, slices, scopes, and targets. Dependencies include requirement (`Requires=`), ordering (`After=`), and activation relationships; ordering does not imply requirement.

A service unit defines execution and lifecycle. `Type=simple` considers the process started immediately; `notify` waits for a readiness message; `forking` supports traditional double-fork daemons; `oneshot` performs a finite action. `Restart=` defines recovery. Socket activation lets systemd own a listening socket and start a service on demand. Timer units replace many cron use cases with dependency, logging, randomized delay, and persistent catch-up.

```ini
[Unit]
Description=Inventory collector lab
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=inventory
Group=inventory
ExecStart=/usr/local/libexec/inventory-collect
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ProtectHome=yes
ReadWritePaths=/var/lib/inventory

[Install]
WantedBy=multi-user.target
```

Use `systemctl cat` to see the vendor unit plus drop-ins, `systemctl show` for resolved properties, `systemd-analyze verify` before deployment, and `journalctl -u` for lifecycle logs. Never edit files under `/usr/lib/systemd/system`; use `/etc/systemd/system` or `systemctl edit` so package upgrades remain manageable.

## Boot troubleshooting from symptom to layer

Classify the failure before changing anything:

1. No firmware screen: power, board, firmware, or display.
2. Firmware cannot find loader: boot variables or EFI System Partition.
3. Bootloader appears but kernel does not start: image, signature, configuration, or CPU handoff.
4. Kernel starts but initramfs shell appears: storage driver, encryption, UUID, LVM/RAID, or root filesystem.
5. Root mounts but emergency target appears: `/etc/fstab`, unit dependency, filesystem check, or critical service.
6. Multi-user starts but application fails: service-specific configuration, identity, sandbox, network, or dependency.

Useful evidence includes previous-boot journal (`journalctl -b -1`), current kernel messages, failed units, critical chain, fstab, block identifiers, and generated mount units.

```shell-session
$ systemctl --failed
  UNIT                  LOAD   ACTIVE SUB    DESCRIPTION
● data.mount            loaded failed failed /data
$ systemd-analyze critical-chain multi-user.target
multi-user.target @6.201s
└─data.mount @1.802s +4.120s
  └─dev-mapper-vg\x2ddata.device @1.790s
$ journalctl -b -p warning..alert --no-pager | tail -3
data.mount: Failed to mount /data: wrong fs type, bad option, bad superblock
```

## Unified kernel images, rescue & rollback

A **Unified Kernel Image (UKI)** packages an EFI stub, kernel, initrd, command line, OS metadata, and optionally signatures into one EFI executable. This reduces ambiguity about which initramfs and command line accompany a kernel and fits measured-boot workflows. It does not remove the need for protected keys, revocation, rollback policy, or recovery entries. Keep a separately tested rescue path and understand whether boot counting automatically falls back after repeated failure.

Recovery must be designed before the outage. Maintain at least one known-good kernel/initramfs pair, verified rescue media, LUKS recovery material, filesystem and LVM documentation, console access, and backups of boot metadata. In an initramfs shell, avoid speculative repair. Confirm block devices with `blkid`, activate expected LVM groups, inspect mappings, mount root read-only, and collect errors. If filesystem repair is required, follow filesystem-specific guidance on an unmounted device and preserve an image when evidence or data value justifies it.

```shell-session
$ findmnt /boot /boot/efi; ls -lh /boot/vmlinuz-* /boot/initrd.img-* | tail -4
$ kernel-install list 2>/dev/null || bootctl list
         type: Boot Loader Specification Type #1 (.conf)
        title: Ubuntu 24.04 (6.8.0-45-generic) (default)
           id: 6.8.0-45-generic.conf
$ systemctl get-default
graphical.target
```

Practice rollback in the VM: boot the previous entry, verify kernel and services, regenerate the broken initramfs from a mounted/chrooted system if necessary, and document the exact exit criteria for returning to normal boot.

## Security implications

Boot security is cumulative. Signed firmware handoff is undermined by an editable loader; signed kernels are undermined by an unprotected command line; encrypted root can be undermined by an untrusted initramfs; hardened services are undermined by writable units or environment files. Keep firmware and bootloaders updated, enforce signatures and measured boot where required, encrypt storage, restrict recovery paths, minimize initramfs contents, protect `/boot`, and sandbox services. Preserve multiple known-good kernels and tested recovery media so hardening does not become fragility.

## Summary

You should now be able to:

- narrate firmware → bootloader → kernel → initramfs → real root → PID 1 → target.
- inspect boot state, build and validate units, analyze dependency timing, and recover a root-device or mount failure in a VM.
- design a signed/measured/encrypted chain of trust, explain early-userspace storage discovery, and harden service startup without sacrificing recoverability.

---
> 🔼 Up: [[Linux]]
