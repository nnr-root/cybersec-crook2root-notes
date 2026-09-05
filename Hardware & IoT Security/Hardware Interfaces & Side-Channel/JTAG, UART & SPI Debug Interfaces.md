---
title: JTAG, UART & SPI Debug Interfaces
aliases:
  - JTAG
  - UART Debug
  - Hardware Debug Interfaces
tags:
  - tree/hardware
  - cyber/content
  - difficulty/practitioner
Domain:
  - "[[Hardware Interfaces & Side-Channel]]"
Color: "#9A6324"
verified: 2026-09-05
---

# JTAG, UART & SPI Debug Interfaces

> [!abstract] One sentence
> Embedded hardware ships with debug interfaces — JTAG, UART, and SPI — that give engineers low-level access to processors and memory, and give attackers the same access when those interfaces are left enabled in production.

**Before you read:** You open a Meridian Freight environmental sensor and find a row of four unpopulated header holes labelled TX, RX, GND, VCC near the main SoC. What are they, what tool do you need, and what might you find if you connect? Hold your answer.

## Parent Learning Order
[[Hardware Interfaces & Side-Channel]] → **JTAG, UART & SPI Debug Interfaces** → [[Side-Channel & Fault Injection]]

---

## UART — Universal Asynchronous Receiver/Transmitter

UART is a serial point-to-point protocol. On embedded Linux devices it almost always exposes the bootloader console and a root shell.

### Identifying UART Pads

```
Look for: 3–4 pads / through-holes near the main SoC or CPU module
Common labels: TX, RX, GND, VCC (or unlabelled — use a multimeter)
Voltage: 3.3V or 5V logic; some industrial devices use 1.8V

Steps to identify unlabelled pads:
  1. GND: continuity to chassis / capacitor ground
  2. VCC: ~3.3V DC with device on, ~0V with device off
  3. TX: oscillates at boot (attach oscilloscope or logic analyser)
  4. RX: static at logic high (device is listening)
```

### Connecting and Finding Baud Rate

```bash
# Equipment: USB-to-UART adapter (FTDI FT232R, CP2102, CH340G)
# Connect: adapter TX → device RX, adapter RX → device TX, GND → GND
# Do NOT connect VCC if the device is powered from its own supply

# Try common baud rates; watch for readable boot text
for baud in 115200 57600 38400 19200 9600; do
  echo "Trying $baud..."
  screen /dev/ttyUSB0 $baud  # Ctrl+A, K to kill and try next
done

# Or use baudrate.py (detects automatically from timing of stop bits)
python3 baudrate.py -p /dev/ttyUSB0
```

### What You Find at the UART Console

```
U-Boot 2021.04 (Aug 15 2026 - 14:22:10 +0000)
DRAM:   256 MiB
Net:    eth0: LAN9514

Hit any key to stop autoboot:  3 2 1 0
Meridian Sensor v2.1.4 ##

/ # id
uid=0(root) gid=0(root)
/ # cat /etc/shadow
root:$1$xyz$abcdefghijklmnop:18000:0:99999:7:::
```

If U-Boot drops to its shell (you hit a key during countdown):

```
=> printenv bootargs
bootargs=console=ttyS0,115200 root=/dev/mmcblk0p2 rw
=> setenv bootargs "${bootargs} init=/bin/sh"  # boot directly to shell
=> boot
```

---

## JTAG — Joint Test Action Group

JTAG (IEEE 1149.1) is an industry standard debug interface that provides full control of a processor: halt, step, read/write all registers, read/write any memory address. In security terms: full debug control of a running system.

### Identifying JTAG Headers

```
Look for: 10, 14, or 20-pin headers (or unpopulated pads) near the CPU
Common pinouts: ARM 10-pin JTAG, ARM 20-pin JTAG, MIPS EJTAG
Tools: JTAGulator (auto-discovers JTAG pinout from unlabelled pads),
       SEGGER J-Link, Bus Blaster, or a Raspberry Pi with OpenOCD
```

### OpenOCD — Memory Extraction via JTAG

```bash
# Install OpenOCD
apt install openocd

# Config for a generic ARM Cortex-M4 target via J-Link
cat > meridian-sensor.cfg << 'EOF'
source [find interface/jlink.cfg]
transport select jtag
source [find target/stm32f4x.cfg]
EOF

openocd -f meridian-sensor.cfg
# Open On-Chip Debugger 0.12.0
# Info : JTAG tap: stm32f4x.cpu tap/device found: 0x4ba00477

# In a second terminal, connect via telnet
telnet localhost 4444

> halt
> targets
    TargetName         Type       Endian TapName            State
--  ------------------ ---------- ------ ------------------ ------------
 0* stm32f4x.cpu       cortex_m   little stm32f4x.cpu       halted

# Dump flash memory (internal — firmware, keys, hardcoded creds)
> dump_image meridian-internal-flash.bin 0x08000000 0x100000
# Dumps 1MB of internal flash to file

# Read a specific memory address
> mdw 0x20000000 32  # read 32 words from SRAM start
```

> [!tip] The analogy, and where it breaks
> JTAG is a maintenance door built into the CPU itself — not an application, not an OS, not a network service. It exists below every software security control.
>
> **The deliberate break:** JTAG can be disabled by blowing eFuses (one-time programmable bits) that lock the debug interface. Once blown, JTAG is permanently off — there is no software way to re-enable it. Secure boot often pairs with eFuse-locked JTAG. An attacker who finds JTAG open on a production device has found a vendor mistake, not a software flaw.

---

## SPI — Serial Peripheral Interface

SPI connects the CPU to peripheral chips: flash memory, sensors, ADCs. We covered SPI flash reading with a clip in [[Firmware Extraction & Analysis]]. JTAG can also access SPI-attached peripherals through the CPU's debug interface once you have a JTAG session.

```bash
# From an OpenOCD session — read SPI flash via CPU SPI controller
# (specific commands depend on the SoC; this is a generic ARM example)
> mww 0x40013000 0x00000344   # configure SPI controller for flash read
> mww 0x40013008 0x03000000   # send READ command (0x03) + 3-byte address
> mdw 0x4001300C              # read response from FIFO
```

---

## Security Implications

- **No software defence applies:** JTAG and UART operate below the OS, bootloader, and application stack. File system encryption, application-level authentication, and TLS are all irrelevant once debug access is established.
- **Persistence:** an attacker with JTAG can patch code running in memory, inject backdoors into the firmware binary, and re-flash modified firmware — all without leaving traces in application logs.
- **Supply-chain risk:** devices that ship with JTAG enabled and no authentication are vulnerable at the point of physical access anywhere in the supply chain — warehouse, transit, or end customer.

---

## Summary

- UART exposes the bootloader console and usually a root shell; identifying it requires a multimeter (for voltage) and logic analyser (for TX activity at boot), and connecting requires only a $5 USB-UART adapter.
- JTAG provides processor-level halt, register access, and memory read/write — including internal flash; OpenOCD with a J-Link or Bus Blaster turns JTAG access into a full firmware dump with a handful of commands.
- Both interfaces bypass all software security controls; the only effective mitigations are eFuse-based JTAG disable (permanent, done at manufacturing) and physically blocking pad access with conformal coating or potting compound.

---
> 🔼 Up: [[Hardware Interfaces & Side-Channel]]
