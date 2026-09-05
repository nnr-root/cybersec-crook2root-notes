---
title: Firmware Extraction & Analysis
aliases:
  - Firmware Analysis
  - Firmware Reversing
  - binwalk
tags:
  - tree/hardware
  - cyber/content
  - difficulty/practitioner
Domain:
  - "[[Firmware Analysis & Extraction]]"
Color: "#9A6324"
verified: 2026-09-05
---

# Firmware Extraction & Analysis

> [!abstract] One sentence
> Firmware is the software baked into a device at manufacturing time — extracting it exposes credentials, private keys, OS configurations, and vulnerability surfaces that survive every application-layer defence above them.

**Before you read:** You are assessing a network-attached environmental sensor on the Meridian Freight plant floor. The device runs an embedded Linux variant, ships with no SSH key rotation, and its web admin panel returns a `Server: lighttpd/1.4.35` header. The vendor has not published CVEs for this model. What would you extract, and how? Hold your answer.

## Parent Learning Order
[[Firmware Analysis & Extraction]] → **Firmware Extraction & Analysis** → [[JTAG, UART & SPI Debug Interfaces]]

---

## What Firmware Is

Firmware is persistent software stored in non-volatile memory (NAND/NOR flash, eMMC) that initialises hardware and runs the device OS. Unlike application software, firmware:

- Ships pre-compiled for a specific CPU architecture (MIPS, ARM, x86, RISC-V)
- Is rarely updated after deployment, especially on OT/industrial gear
- Contains hardcoded keys, credentials, and configuration that the vendor embedded at build time
- Often exposes a full Linux filesystem (SquashFS, JFFS2, cramfs) when unpacked

The firmware image is the ground truth about what runs on the device — every security control built on top of it is only as strong as the firmware underneath.

---

## Extraction Methods

### Method 1 — Logical: Vendor Web UI / OTA Download

The easiest path. Many vendors publish firmware update files publicly, or the device admin panel exposes a firmware download function.

```bash
# Identify model and firmware version from the HTTP banner
curl -s -I http://192.0.2.10/admin/ | grep -i server
# Server: lighttpd/1.4.35

# Download vendor firmware update (manufacturer's site)
wget https://vendor.example/firmware/sensor-v2.1.4.bin

# OR trigger device self-update and intercept with Burp / tcpdump
tcpdump -i eth0 -w update-capture.pcap host 192.0.2.10
```

**Limitation:** vendor-published images may be stripped or encrypted. If the device runs signed/encrypted firmware, logical extraction yields a blob you cannot directly analyse.

---

### Method 2 — Physical: SPI Flash Chip Reading

Most consumer and OT devices store firmware in an SPI NOR flash chip (Winbond, Macronix, ISSI). The chip can be read directly with a clip-on probe — no disassembly or soldering required for many packages.

```
Equipment needed:
  • SOIC-8 / SOP-8 clip (Pomona 5250 or equivalent)
  • CH341A USB programmer (< $5) or Bus Pirate
  • flashrom (Linux utility)

Steps:
  1. Power off the device
  2. Clip onto the SPI flash chip (identify with markings + datasheet)
  3. Connect clip to CH341A
  4. Read the flash:
```

```bash
# Read full SPI flash content
flashrom -p ch341a_spi -r firmware-dump.bin
# Reading old flash chip contents... done.

# Verify read integrity (read twice, compare)
flashrom -p ch341a_spi -r firmware-dump2.bin
md5sum firmware-dump.bin firmware-dump2.bin
# hashes should match
```

> [!tip] The analogy, and where it breaks
> SPI flash reading is like photocopying someone's notebook while they sleep — non-destructive and leaves no trace on the device.
>
> **The deliberate break:** some devices use encrypted flash (Secure Boot with eFuse-locked keys). The clip still reads the chip, but the content is ciphertext. You need the key — which may be in the MCU's internal flash, extractable only via JTAG or fault injection.

---

### Method 3 — UART Console

Many embedded devices leave a UART (serial) debug port on the PCB. If accessible at boot, it prints the bootloader (U-Boot), kernel messages, and sometimes drops into a root shell.

```bash
# Connect USB-UART adapter (FTDI / CP2102) to TX/RX/GND pads
# Identify baud rate (common: 115200, 57600, 9600)
screen /dev/ttyUSB0 115200

# Watch boot output — look for:
# "Hit any key to stop autoboot" (U-Boot)
# "/ # " (root shell)
# Or: login prompt — try root/admin/1234/blank
```

---

## Firmware Analysis with binwalk

Once you have a firmware blob, `binwalk` identifies and extracts embedded file systems, compressed archives, and executable code.

```bash
# Identify structures in the blob
binwalk firmware-dump.bin
# DECIMAL       HEXADECIMAL     DESCRIPTION
# 0             0x0             uImage header
# 64            0x40            LZMA compressed data
# 1048640       0x100040        Squashfs filesystem, little endian, version 4.0

# Extract everything recursively
binwalk -eM firmware-dump.bin
# Creates _firmware-dump.bin.extracted/
ls _firmware-dump.bin.extracted/squashfs-root/
# bin  etc  lib  sbin  usr  var  www

# Now treat squashfs-root as a Linux filesystem
```

---

## What to Hunt in an Extracted Filesystem

### Hardcoded Credentials

```bash
FS="squashfs-root"

# /etc/passwd and /etc/shadow — extract password hashes
cat $FS/etc/shadow
# root:$1$xyz$abcdefghijklmnop:18000:0:99999:7:::  ← MD5-crypt, crackable

# Grep for hardcoded passwords in config files
grep -ri "password" $FS/etc/ --include="*.conf" --include="*.cfg" -l
grep -ri "admin_pass\|default_pass\|hardcoded" $FS/ -l

# Default credentials in web server config
grep -r "admin" $FS/usr/www/ 2>/dev/null | grep -i "pass\|auth"
```

### Private Keys and Certificates

```bash
find $FS -name "*.pem" -o -name "*.key" -o -name "*.crt" 2>/dev/null
# /etc/ssl/private/server.key  ← device TLS private key; if shared across all units, every device is broken

# Check if it's a real key
openssl rsa -in $FS/etc/ssl/private/server.key -noout -text 2>/dev/null | head -5
```

### Binary Vulnerability Surface

```bash
# Identify CPU architecture of executables
file $FS/bin/busybox
# ELF 32-bit LSB executable, ARM, EABI5 version 1 (SYSV)

# Check for stack canaries, NX, RELRO
checksec --file=$FS/usr/sbin/httpd
# RELRO: No RELRO  |  Stack Canary: No  |  NX: No  ← classic embedded binary

# Find SUID binaries
find $FS -perm /4000 2>/dev/null
```

### Meridian Freight Worked Example

Sensor at 192.0.2.10, firmware `sensor-v2.1.4.bin` extracted via SPI clip:

```bash
binwalk -eM sensor-v2.1.4.bin
grep -r "password" squashfs-root/etc/ 2>/dev/null
# squashfs-root/etc/config/system.conf:admin_password=Meridian2024!

# That credential also valid on the web admin panel — confirmed via:
curl -s -u admin:Meridian2024! http://192.0.2.10/api/system/info | python3 -m json.tool
# {"model":"MFS-100","fw":"2.1.4","uptime":1209600,"plant":"meridian-east"}

# Private key for TLS found shared across all deployed units:
openssl x509 -in squashfs-root/etc/ssl/server.crt -noout -subject
# subject=CN=Meridian Freight Sensor, O=Meridian Freight, C=UK
# Serial number shared → decrypts traffic from all sensors on the plant floor
```

**How you'd spot it:** on the defender side, firmware integrity monitoring — comparing a fresh extraction hash against the vendor-published SHA256 — detects tampered images. Network monitoring for unexpected outbound connections from sensor IPs catches post-exploitation.

---

## Security Implications

- **Credentials:** hardcoded credentials in firmware survive firmware updates unless explicitly rotated in new images — check the `diff` between versions, not just the latest release.
- **Key sharing:** a single TLS private key embedded in every unit means one firmware extraction breaks confidentiality for every device of that model globally.
- **Unpatchable surface:** many embedded Linux kernels are 5–10 years old; without a running update mechanism, known kernel CVEs remain permanently exploitable on deployed units.

---

## Summary

- Firmware extraction ranges from downloading a vendor update package to reading SPI flash directly with a clip-on probe; physical methods are non-destructive and leave no forensic trace on the device.
- `binwalk -eM` is the standard first step — it carves embedded filesystems, compressed archives, and kernel images out of a raw blob and presents them as a navigable Linux tree.
- High-value targets inside an extracted filesystem are `/etc/shadow` hashes, private TLS keys, hardcoded credentials in config files, and binaries compiled without stack canaries or NX — the absence of compiler mitigations makes embedded binaries disproportionately exploitable.

---
> 🔼 Up: [[Firmware Analysis & Extraction]]
