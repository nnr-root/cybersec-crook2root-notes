#!/usr/bin/env python3
"""
Add the six missing worked examples in Networking.

These six notes were the only Networking leaves with no command/output block.
Their archived labs were the prose-instruction kind ("run a known attack pattern
and confirm the IDS alerts") with no commands to mine, so these examples are
authored rather than recovered.

Each new section is inserted immediately before that note's Security
Implications task, and all tasks are then renumbered sequentially.

    python3 docs/scripts/add-examples.py            # dry run
    python3 docs/scripts/add-examples.py --apply
"""

import re
import sys

PROV = ("> [!note] Representative output\n"
        "> Reconstructed from a lab of this shape rather than copied from one "
        "capture. Field layouts and flag names match the named tool; addresses "
        "and identifiers are synthetic.\n")

IDS = """## Worked Example: What a Sensor Sees, Misses, and Infers

Three captures against one Suricata sensor show the whole argument of this note:
a signature is precise but narrow, a small change defeats it, and encryption
moves the evidence from content to metadata.

""" + PROV + """
**A known pattern, matched.** A request carrying an obvious SQL injection
string crosses the sensor, and the signature engine names it exactly:

```shell-session
analyst@sensor:~$ tail -n 1 /var/log/suricata/fast.log
04/12/2026-14:22:07.118431  [**] [1:2013028:7] ET WEB_SERVER Possible SQL
Injection Attempt SELECT FROM [**] [Classification: Web Application Attack]
[Priority: 1] {TCP} 198.51.100.24:51422 -> 192.0.2.10:80
```

Every field here is actionable: `1:2013028:7` identifies the exact rule that
fired, the classification tells an analyst what kind of problem this is, and the
five-tuple says who did it to whom. This is the strength of signature detection —
when it fires, it fires with an explanation.

**The same attack, URL-encoded.** The request means the same thing to the web
server, but no longer matches the literal bytes the rule looks for:

```shell-session
analyst@sensor:~$ tail -n 1 /var/log/suricata/fast.log
04/12/2026-14:19:44.902017  [**] [1:2013028:7] ET WEB_SERVER Possible SQL
Injection Attempt SELECT FROM [**] ... {TCP} 198.51.100.24:51188 -> 192.0.2.10:80
analyst@sensor:~$ # after re-sending the request as %53%45%4c%45%43%54 ...
analyst@sensor:~$ tail -n 1 /var/log/suricata/fast.log
04/12/2026-14:19:44.902017  [**] [1:2013028:7] ET WEB_SERVER Possible SQL
Injection Attempt SELECT FROM [**] ... {TCP} 198.51.100.24:51188 -> 192.0.2.10:80
```

**The timestamp did not change** — that is the finding. The last line is still
the *previous* alert, because the encoded request produced no new one. A rule
matching raw bytes sees different bytes; whether the target decodes them back to
the same query is not the rule's concern. This is the known-only limitation made
concrete, and it is why normalization before matching is a core IDS design
problem rather than a detail.

**Encrypted traffic, inferred.** Once the same session runs inside TLS the
sensor cannot read the payload at all — but it can still describe the
conversation:

```shell-session
analyst@sensor:~$ jq -c 'select(.event_type=="tls")' /var/log/suricata/eve.json | tail -1
{"timestamp":"2026-04-12T14:31:55.402113+0000","flow_id":1885274419203371,
"src_ip":"192.0.2.10","dest_ip":"203.0.113.77","dest_port":443,
"tls":{"sni":"cdn-updates.example.net","version":"TLS 1.3",
"ja3":{"hash":"e7d705a3286e19ea42f587b344ee6865"}}}
```

No payload appears, and none can. What remains is still substantial: the
requested name in `sni`, the negotiated `version`, and `ja3` — a hash of how the
client proposed the handshake, which fingerprints the *client software* rather
than the content. A JA3 hash that matches no browser in the environment, talking
to a name registered last week, is a detection built entirely from metadata. That
is the shift this note describes, visible in one log line.

"""

NAC = """## Worked Example: A Port Deciding Whether to Let You In

802.1X is easiest to understand from the supplicant's side, where the whole
exchange is narrated line by line.

""" + PROV + """
**A successful authentication.** The client starts EAP on a wired interface and
the switch port transitions from unauthorized to forwarding:

```shell-session
analyst@ws-4471:~$ sudo wpa_supplicant -i enp3s0 -D wired -c /etc/wpa_supplicant/8021x.conf
enp3s0: CTRL-EVENT-EAP-STARTED EAP authentication started
enp3s0: CTRL-EVENT-EAP-METHOD EAP vendor 0 method 13 (TLS) selected
enp3s0: CTRL-EVENT-EAP-PEER-CERT depth=1 subject='/CN=Example Issuing CA'
enp3s0: CTRL-EVENT-EAP-SUCCESS EAP authentication completed successfully
enp3s0: CTRL-EVENT-CONNECTED - Connection to 01:80:c2:00:00:03 completed
```

`method 13` is EAP-TLS — certificate-based, with no password anywhere in the
exchange. The address the client "connects to" is `01:80:c2:00:00:03`, the
reserved multicast address for 802.1X itself; the supplicant is talking to the
port, not to a host, which is the point of authenticating at Layer 2.

**What the server decided, and what it attached.** On the RADIUS side the accept
carries more than a yes:

```shell-session
admin@radius:~$ sudo journalctl -u freeradius -n 6 --no-pager
Sending Access-Accept ID 214 from 10.20.0.5:1812 to 10.20.0.9:41003
  User-Name = "host/ws-4471.corp.example.com"
  Tunnel-Type = VLAN
  Tunnel-Medium-Type = IEEE-802
  Tunnel-Private-Group-Id = "310"
```

Those three tunnel attributes are the mechanism behind dynamic VLAN assignment.
The switch does not decide where this device belongs — the identity decision and
the placement decision are made together, centrally, and the port is configured
from the answer. A finance laptop and a visitor's laptop can share a physical
port and still land in different segments.

**A failure, and what the port does about it.** With an expired client
certificate the same exchange ends differently:

```shell-session
enp3s0: CTRL-EVENT-EAP-STATUS status='remote certificate verification'
        parameter='certificate has expired'
enp3s0: CTRL-EVENT-EAP-FAILURE EAP authentication failed
enp3s0: CTRL-EVENT-DISCONNECTED bssid=01:80:c2:00:00:03 reason=23
```

```shell-session
admin@radius:~$ sudo journalctl -u freeradius -n 2 --no-pager
Login incorrect (TLS Alert write:fatal:certificate expired):
  [host/ws-4471] (from client sw-access-01 port 14 cli 3c:52:82:1a:9b:04)
```

The port never reaches the forwarding state, so the device has link but no
network — no IP, no DHCP, nothing. This is the failure mode that generates help
desk tickets reading "the cable is plugged in but the internet is broken", and
recognising it as an authentication result rather than a cabling fault is most of
the diagnosis. Note also `port 14` and the client MAC in the server log: the
switch tells RADIUS exactly which physical port asked, which is what makes the
decision enforceable at the edge.

"""

BGP = """## Worked Example: Reading a Path, and Watching a More-Specific Win

BGP's failure mode is easier to believe once you have watched the routing table
prefer the wrong announcement without anything reporting an error.

""" + PROV + """
**The legitimate route.** From a router three autonomous systems away, the path
back to the origin is written out in full:

```shell-session
operator@router-c:~$ sudo vtysh -c "show ip bgp 203.0.113.0/24"
BGP routing table entry for 203.0.113.0/24
Paths: (1 available, best #1, table default)
  65002 65001
    10.0.23.2 from 10.0.23.2 (10.0.0.2)
      Origin IGP, valid, external, best (First path received)
      Last update: Sun Apr 12 09:41:18 2026
```

`65002 65001` is the AS-path read right to left: AS 65001 originated the prefix,
AS 65002 passed it along. That list is the entire basis on which the rest of the
Internet decides this route is genuine — a claim, propagated by other people's
routers, with no cryptographic backing at all.

**A more-specific announcement appears.** A second AS announces a /25 inside
that /24, and the table changes without complaint:

```shell-session
operator@router-c:~$ sudo vtysh -c "show ip bgp"
   Network          Next Hop      Metric LocPrf Weight Path
*> 203.0.113.0/24   10.0.23.2                       0 65002 65001 i
*> 203.0.113.0/25   10.0.13.2                       0 65003 i
```

Both routes are marked `*>` — valid and best *for their own prefix*. Nothing is
in conflict as far as BGP is concerned, because they are different prefixes. But
forwarding uses longest-prefix match, so every packet for the first half of that
range now leaves toward AS 65003:

```shell-session
operator@router-c:~$ sudo vtysh -c "show ip route 203.0.113.20"
Routing entry for 203.0.113.0/25
  Known via "bgp", distance 20, metric 0, best
  * 10.0.13.2, via eth1
```

This is the shape of almost every real hijack. Nothing was overwritten, no alarm
fired, and the destination still appears reachable — traffic simply goes
somewhere else first. Because the announcement is more specific it wins
everywhere it propagates, which is why a hijack of a /25 out of someone else's
/24 is both effective and hard to notice from inside the affected network.

**What origin validation catches.** With RPKI enabled and a ROA declaring AS
65001 as the only authorized origin, the router can now express an opinion:

```shell-session
operator@router-c:~$ sudo vtysh -c "show bgp ipv4 unicast rpki invalid"
   Network          Next Hop      Path
*  203.0.113.0/25   10.0.13.2     65003 i
```

The route is now marked `invalid` and, with a policy that acts on that state, is
never selected. Note what this does *not* prove: RPKI validates that the origin
AS is entitled to announce the prefix, not that the AS-path is truthful. An
attacker who forges a path ending in `65001` while still carrying the traffic
themselves produces a route that validates cleanly — which is exactly the residual
gap path validation exists to close.

"""

BT = """## Worked Example: What a Device Broadcasts Before You Connect

The personal-area attack surface is easiest to grasp by looking at what devices
emit continuously, to anyone, with no connection and no pairing.

""" + PROV + """
**Classic discovery.** A scan names the devices in range and tracks their signal
strength:

```shell-session
analyst@lab:~$ bluetoothctl
[bluetooth]# scan on
Discovery started
[NEW] Device 4C:87:5D:2A:11:E9 Wireless Earbuds
[NEW] Device 3B:1F:04:9C:77:A2 Car-Audio-8842
[CHG] Device 4C:87:5D:2A:11:E9 RSSI: -54
[CHG] Device 4C:87:5D:2A:11:E9 RSSI: -41
```

Two things are already available without any interaction: a stable address and a
name that often describes the product, the owner, or both. The falling-then-rising
`RSSI` is a crude distance signal — enough to tell that the device is approaching.

**Low-energy advertising, in detail.** `btmon` shows the raw advertising reports
that BLE devices broadcast on a fixed interval:

```shell-session
analyst@lab:~$ sudo btmon
> HCI Event: LE Meta Event (0x3e) plen 42
      LE Advertising Report (0x02)
        Address type: Random (0x01)
        Address: 6F:2C:19:D4:8A:33 (Static)
        Data length: 26
        Flags: 0x06
          LE General Discoverable Mode
          BR/EDR Not Supported
        Complete Local Name: Fitness Band 4
        Service Data (UUID 0x180f): 4b
        RSSI: -67 dBm (0xbd)
```

`Service Data (UUID 0x180f)` is the standard Battery Service, and `4b` is 75% —
a device reporting its battery level to the whole room. Harmless in itself, and a
good illustration of how much a beacon says before any trust is established.

**The line that matters for privacy** is `Address: … (Static)`. BLE supports
resolvable private addresses that rotate every fifteen minutes precisely so a
device cannot be followed between locations. A *static* random address never
rotates, so this beacon is a durable identifier — anyone with a receiver can
recognise the same wearable in a shop today and an office tomorrow. The failure
here is not broken cryptography; it is a device that never enabled the privacy
feature, which is exactly the cheap-endpoint constraint this note opened with.

"""

CELL = """## Worked Example: What the Modem Reports About Its Serving Cell

A phone's own modem exposes the two facts an IMSI-catcher cannot hide: which
generation it has been persuaded to use, and which cell it is attached to.

""" + PROV + """
**Normal attachment.** On a healthy modern network the modem reports mutual
authentication and a current radio technology:

```shell-session
analyst@lab:~$ mmcli -m 0
  --------------------------------
  Status   |             state: connected
           |       power state: on
           |       access tech: lte
           |    signal quality: 71% (recent)
  --------------------------------
  3GPP     |      operator id: 23415
           |    operator name: Example Mobile
           |     registration: home
```

```shell-session
analyst@lab:~$ mmcli -m 0 --location-get
  --------------------------------
  3GPP location |    operator code: 23415
                |          tracking area code: 0A1C
                |                     cell id: 01A2B3C4
```

`access tech: lte` matters more than the signal quality. From 4G onward the
network must prove itself to the device as well as the reverse, so a device that
stays on LTE or 5G cannot be attached to a tower that does not hold the operator's
keys.

**A forced downgrade.** The same modem, moments later, in the presence of a
device suppressing the LTE bands:

```shell-session
analyst@lab:~$ mmcli -m 0
  --------------------------------
  Status   |             state: connected
           |       access tech: gsm
           |    signal quality: 94% (recent)
  --------------------------------
  3GPP     |      operator id: 23415
           |     registration: home
```

```shell-session
analyst@lab:~$ mmcli -m 0 --location-get
  --------------------------------
  3GPP location |          cell id: 0F00FF01
```

Three signals together tell the story, and no single one is conclusive. The
access technology has dropped to `gsm`, where the network never authenticates
itself to the phone. The signal quality has jumped to 94% — a nearby transmitter,
not a distant tower. And the cell ID is one never previously seen in this area.
A phone showing full bars on a two-generation-old technology in a city with LTE
coverage everywhere is reporting an anomaly, even though every individual field
looks like a normal successful connection.

This is why the fix was generational rather than a patch: the vulnerability is
that an older protocol *without* mutual authentication remains reachable, so the
defence is refusing to speak it. A device configured to require LTE or better
simply fails to attach instead of attaching to an impostor.

"""

WIFI = """## Worked Example: Two Access Points, One Name

An evil twin is not subtle in a capture. It is subtle only to the client, which
selects by name.

""" + PROV + """
**The airspace, with both APs present:**

```shell-session
analyst@lab:~$ sudo airodump-ng wlan0mon

 CH  6 ][ Elapsed: 2 mins ][ 2026-04-12 15:04

 BSSID              PWR  Beacons  #Data, #/s  CH   MB   ENC  CIPHER AUTH ESSID

 A4:2B:8C:11:0D:E2  -62      184      12    0   6  130   WPA2 CCMP   PSK  corp-wifi
 00:11:22:33:44:55  -31      612     104    3  11   54e  WPA2 CCMP   PSK  corp-wifi
 A4:2B:8C:11:0D:E3  -63      181       0    0   6  130   WPA2 CCMP   MGT  corp-guest
```

Two rows advertise `corp-wifi` with different BSSIDs, and four fields separate
them. The second is **31 dB stronger**, which at these levels means far closer.
Its **max rate is 54e**, the signature of a software access point on a generic
adapter rather than the 130 Mbit/s of the real enterprise hardware. It sits on a
**different channel**, and its **beacon count is more than triple** the
legitimate AP's over the same window — an impatient transmitter advertising hard.
The first three octets also differ: `A4:2B:8C` is a real vendor allocation shared
with the guest SSID on the same physical AP, while `00:11:22` is a placeholder
that appears in no vendor registry.

**The client moving across.** A deauthentication frame arrives, and the
association that follows lands on the wrong BSSID:

```shell-session
analyst@lab:~$ sudo tcpdump -i wlan0mon -e -n 'wlan type mgt' -c 4
15:06:22.104881 BSSID:a4:2b:8c:11:0d:e2 SA:a4:2b:8c:11:0d:e2 DA:9c:b6:d0:44:1f:07
    DeAuthentication (7): Class 3 frame received from nonassociated STA
15:06:22.118440 BSSID:00:11:22:33:44:55 SA:9c:b6:d0:44:1f:07 DA:00:11:22:33:44:55
    Assoc Request (corp-wifi) [1.0 2.0 5.5 11.0 Mbit]
15:06:22.121973 BSSID:00:11:22:33:44:55 SA:00:11:22:33:44:55 DA:9c:b6:d0:44:1f:07
    Assoc Response AID(1) :: Successful
```

The deauthentication claims to come from the legitimate AP — the source address
is simply written, exactly as with an Ethernet frame, and management frames on an
open or PSK network carry no authentication of their own. Fourteen milliseconds
later the client has associated with the impostor and its user has noticed
nothing, because from the client's perspective it reconnected to a network it
knows by name.

The decisive detail is what the client compared before choosing: an SSID string
and a signal strength. It never asked the access point to prove it was the same
one as yesterday, because on a PSK network there is nothing it could have asked.

"""

WORK = {
    "Networking/Network Security Architecture/Intrusion Detection & Network Monitoring.md": IDS,
    "Networking/Network Security Architecture/Network Access Control.md": NAC,
    "Networking/Routing & the Network Layer/BGP & Internet Routing.md": BGP,
    "Networking/Wireless Networking/Bluetooth & Personal-Area Networks.md": BT,
    "Networking/Wireless Networking/Cellular & Long-Range Wireless.md": CELL,
    "Networking/Wireless Networking/Wireless Attacks & Rogue Infrastructure.md": WIFI,
}

SEC_TASK = re.compile(r"^## Task \d+ — Security Implications\s*$", re.M)
ANY_TASK = re.compile(r"^## Task \d+ — (.*)$", re.M)


def apply_to(text, section):
    m = SEC_TASK.search(text)
    if not m:
        return text, "no Security Implications task found"
    out = text[:m.start()] + section + text[m.start():]
    n = [0]

    def renum(mm):
        n[0] += 1
        return f"## Task {n[0]} — {mm.group(1)}"

    # the inserted block has no number yet; give it one in document order
    out = out.replace("## Worked Example:", "## Task 0 — Worked Example:", 1)
    out = ANY_TASK.sub(renum, out)
    return out, f"inserted, {n[0]} tasks renumbered"


def main():
    apply = "--apply" in sys.argv
    for rel, section in WORK.items():
        try:
            src = open(rel, encoding="utf-8").read()
        except FileNotFoundError:
            print(f"  MISSING  {rel}")
            continue
        out, how = apply_to(src, section)
        ok = out != src
        print(f"  {'✓' if ok else '✗'} [{how}] {rel}")
        if ok and apply:
            open(rel, "w", encoding="utf-8").write(out)
    print(f"\n{'APPLIED' if apply else 'DRY RUN'}")
    if not apply:
        print("Re-run with --apply to write.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
