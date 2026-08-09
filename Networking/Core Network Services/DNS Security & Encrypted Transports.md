---
title: "DNS Security & Encrypted Transports"
aliases: ["DNSSEC", "DoH", "DoT", "DNS over HTTPS", "DNS Tunneling", "Subdomain Takeover"]
tags:
  - tree/networking
  - cyber/networking/dns
  - type/technique
  - level/root
Domain:
  - "[[Core Network Services]]"
Color: "#42D4F4"
---

# 🔐 DNS Security & Encrypted Transports

> [!abstract] Note of [[Core Network Services]]
> DNS was designed with no authentication and no confidentiality, and the two gaps were closed by entirely separate technologies that people routinely confuse. This note separates them precisely — one proves an answer is genuine, the other hides the question — and covers the abuse cases that neither solves.

## Parent Learning Order
DNS Resolution & Records -> DNS Security & Encrypted Transports -> Local Name Resolution & Service Discovery -> Network Time Synchronization -> Email Transport Protocols -> Network Management Protocols

## Start at Zero: Two Different Problems

Classic DNS runs over UDP port 53 in cleartext with no signatures. That creates two independent weaknesses, and the single most common conceptual error in this topic is treating them as one.

| Problem | Question it raises | Technology that addresses it |
| --- | --- | --- |
| **No authenticity** | Is this answer genuine, or forged by someone on the path? | **DNSSEC** |
| **No confidentiality** | Can anyone observing the network see what I looked up? | **DoT / DoH** (encrypted transport) |

DNSSEC signs answers but transmits them in the clear — anyone watching still sees every name you resolve. DoH encrypts the conversation but proves nothing about whether the answer is truthful — a malicious resolver returns whatever it wants over a perfectly encrypted channel. **They are complementary, not alternatives**, and deploying one does not deliver the other's benefit.

**Prerequisites:** how DNS resolution and caching work.

> [!tip] The analogy, and where it breaks
> A sealed envelope and a notarised letter solve different problems: the seal stops anyone reading it in transit, the notary proves the contents are genuine. The analogy breaks mainly because people assume one implies the other. Encrypted transport seals the question; DNSSEC notarises the answer. A perfectly sealed envelope can still contain a forgery, which is why an encrypted lookup can still return an attacker's address.

## DNSSEC: Proving the Answer Is Genuine

**DNSSEC (DNS Security Extensions)** adds cryptographic signatures to DNS records. A zone owner signs its records with a private key; a validating resolver verifies the signature with the corresponding public key. If the signature does not verify, the answer is rejected rather than returned.

The trust model is a **chain** that mirrors the delegation hierarchy. Each zone's signing key is vouched for by its parent, up to the root zone whose key is a well-known trust anchor.

```mermaid
flowchart TB
    Root["Root zone key — the trust anchor"] --> DS1["DS record in root vouches for .com's key"]
    DS1 --> COM[".com zone key"]
    COM --> DS2["DS record in .com vouches for example.com's key"]
    DS2 --> EX["example.com zone key"]
    EX --> SIG["RRSIG signatures over the actual records"]
    SIG --> V["Validating resolver verifies the whole chain or REJECTS the answer"]
```

The records involved: **DNSKEY** holds a zone's public keys, **RRSIG** holds signatures over record sets, **DS** sits in the *parent* zone and vouches for the child's key, and **NSEC/NSEC3** provide authenticated denial — proving a name genuinely does not exist rather than letting an attacker forge a "no such name" reply.

Verify validation is working:

```bash
dig www.example.com A +dnssec +multiline | grep -E "flags:|RRSIG"
```

Expected excerpt when validation succeeded:

```text
;; flags: qr rd ra ad; QUERY: 1, ANSWER: 2
www.example.com. 300 IN RRSIG A 13 3 300 (...)
```

The **`ad` flag** — Authenticated Data — is the finding. It means the resolver cryptographically validated the chain. Its absence means either the zone is unsigned or your resolver is not validating; both are common, and distinguishing them matters.

**What DNSSEC does not do**, stated plainly because it is widely overestimated: it does not encrypt anything, it does not authenticate the *user*, it does not protect the last hop between your device and your resolver unless that link is separately secured, and adoption remains partial so many zones are simply unsigned. It also introduces operational risk — a signing or key-rollover mistake makes a zone fail validation, which for validating resolvers means the domain becomes unreachable rather than merely unverified. That failure mode is a real deterrent to adoption and worth acknowledging honestly.

## Encrypted Transports: Hiding the Question

The second gap is that cleartext queries expose browsing behaviour to anyone on the path.

| Transport | Port | Characteristics |
| --- | --- | --- |
| **Do53** (classic) | UDP/TCP 53 | Cleartext; visible and blockable by port |
| **DoT** (DNS over TLS) | 853 | Encrypted; on a dedicated port, so it is visibly DNS and easy to permit or block deliberately |
| **DoH** (DNS over HTTPS) | 443 | Encrypted inside ordinary HTTPS; indistinguishable from web traffic |
| **DoQ** (DNS over QUIC) | 853 | Encrypted over QUIC; avoids TCP head-of-line blocking |

The distinction between DoT and DoH is organizational rather than cryptographic. Both encrypt equally well. But DoT uses a dedicated port, so a network operator can see that DNS is happening and apply policy to it. DoH hides inside HTTPS on port 443, so it is **indistinguishable from web browsing** — deliberately so, to resist censorship.

That design choice creates a genuine tension worth stating fairly. For a user on a hostile network, DoH protects privacy and resists surveillance and manipulation. For an enterprise defender, DoH used by a client that bypasses the organization's resolver removes DNS visibility — one of the highest-value telemetry sources — and can bypass DNS-based filtering entirely. Malware adopted DoH for exactly this reason: its lookups become invisible to network monitoring.

Neither position is simply correct. The practical enterprise posture is to **run an internal DoH/DoT resolver and require its use**, so clients get encrypted transport on the untrusted last hop while the organization retains logging at the resolver. Blocking DoH outright is increasingly impractical, since it is just HTTPS.

```bash
kdig -d @1.1.1.1 +tls www.example.com          # DoT
curl -sH 'accept: application/dns-json' \
  'https://cloudflare-dns.com/dns-query?name=www.example.com&type=A'   # DoH
```

Expected excerpt from the DoH query:

```text
{"Status":0,"TC":false,"RD":true,"RA":true,"AD":false,
 "Answer":[{"name":"www.example.com","type":1,"TTL":300,"data":"203.0.113.10"}]}
```

Note `"AD":false` — encrypted transport delivered the answer confidentially, and it is still not DNSSEC-validated. This single field demonstrates the note's central point better than any explanation.

## Abuse Cases Neither Technology Solves

**DNS tunnelling** encodes arbitrary data into query names and response records, using DNS as a covert channel for command-and-control or exfiltration. It works because DNS must generally be permitted outbound, and because resolvers will faithfully forward queries for any domain to that domain's authoritative server — which the attacker controls.

Detection is behavioural, and the indicators are distinctive:

- Abnormally long or high-entropy query names (encoded data, not words).
- Very high query volume to a single domain from one host.
- Unusual record types such as TXT or NULL in high volume.
- Regular timing intervals suggesting an automated beacon rather than human browsing.
- Consistently low TTLs to force repeated lookups.

```bash
sudo tcpdump -i eth0 -nn 'udp port 53' -A | grep -oE '[a-z0-9]{40,}'
```

A stream of long random-looking labels is the signature. Note that neither DNSSEC nor encryption helps here — the queries may be perfectly signed and perfectly encrypted, and are still exfiltration. This is why resolver-level logging and analytics remain necessary regardless of transport security.

**Subdomain takeover** exploits stale records. If `old-app.example.com` is a CNAME pointing at a cloud resource that was decommissioned, an attacker who claims that resource name at the provider now controls content served at your subdomain — inheriting your domain's reputation, cookies scoped to the parent domain, and any trust users place in it. The fix is record hygiene: remove DNS entries when the resource they point to is retired. This is a configuration-management failure that DNS security technologies do not address at all.

**Malicious resolvers** return whatever they choose. A resolver configured by a rogue DHCP lease or by malware answers with attacker-controlled addresses, over encryption if you like. DNSSEC validation at the *client* would catch forged answers for signed zones, which is precisely why validation location matters — validating only at a resolver you do not trust provides no protection.

## Security Implications

**Layer the two technologies deliberately.** Encrypted transport protects the last hop and user privacy; DNSSEC protects answer integrity end to end. An organization wanting both runs a validating resolver reachable over DoT/DoH and requires clients to use it.

**DNS telemetry is worth preserving.** Resolver logs record intent before encrypted traffic hides everything else — they surface newly registered domains, algorithmically generated names, tunnelling, and beaconing. Any architecture change that removes DNS visibility, including uncontrolled client DoH, should be a conscious decision with a compensating control, not an accident.

**Filtering at DNS is efficient but bypassable.** Blocking resolution of known-malicious domains is cheap and effective against commodity threats. It is not a boundary control: an attacker who uses direct IP addresses, an alternative resolver, or DoH to a third party is unaffected. Treat it as a broad filter, not a barrier.

**Availability is the underrated risk.** DNSSEC misconfiguration makes a domain unreachable to validating resolvers. Registrar or authoritative-server compromise redirects an entire domain regardless of any other control. Registrar account security, registry locks, and monitoring for unexpected NS or DS changes protect against the highest-impact DNS failures, which are administrative rather than protocol-level.

All testing described here must target domains and resolvers within an authorized scope. Tunnelling in particular must be confined to a lab with a domain you control.

## Authorized Lab: Separate Authenticity from Confidentiality

Use a lab client, a validating resolver, and a signed zone you control.

1. **Observe cleartext exposure.** Capture a classic query and confirm the name is plainly readable:

```bash
sudo tcpdump -i eth0 -nn -A -c 2 'udp port 53'
```

2. **Enable encrypted transport.** Configure the client to use DoT or DoH. Repeat the capture and confirm the query name is no longer visible — only an encrypted session to the resolver.
3. **Show that encryption is not validation.** Using the encrypted transport, query a name and check the `AD` flag. Confirm it is false for an unsigned zone despite the transport being fully encrypted.
4. **Enable DNSSEC.** Sign your lab zone and enable validation on the resolver. Query again and confirm the `ad` flag now appears.
5. **Break a signature deliberately.** Modify a signed record without re-signing. Confirm the validating resolver now returns SERVFAIL rather than the record — demonstrating that DNSSEC fails closed, and why a signing mistake causes an outage:

```bash
dig www.lab.internal A +dnssec
```

Expected excerpt:

```text
;; ->>HEADER<<- opcode: QUERY, status: SERVFAIL, id: 41022
```

6. **Demonstrate tunnelling detection.** In the isolated lab, send a series of queries with long encoded labels to a domain you control. Confirm that both DNSSEC validation and encrypted transport leave the tunnel fully functional, then detect it by query-name length and volume rather than by content.
7. **Cleanup.** Restore the correct signatures, revert resolver and client transport configuration, and confirm normal resolution with the `ad` flag intact.

Expected interpretation:

```text
Cleartext        -> query names readable by anyone on the path
DoT/DoH          -> names hidden, but AD still false: no integrity guarantee
DNSSEC enabled   -> ad flag appears; answers are cryptographically verified
Broken signature -> SERVFAIL, not a warning: DNSSEC fails closed
Tunnelling       -> unaffected by either technology; detected behaviourally
```

## Crook → Operator → Root Checkpoint

- **Crook:** State the two distinct DNS weaknesses and name the technology addressing each; explain why encrypting a query does not make its answer trustworthy.
- **Operator:** Verify DNSSEC validation via the `ad` flag, configure and confirm encrypted transport, and recognize DNS tunnelling by query length, entropy, volume, and timing.
- **Root:** Explain the DNSSEC chain of trust from the root anchor down, and why validation location determines whether it protects you; argue the DoH privacy-versus-visibility tension fairly and describe the internal-resolver posture that resolves it; explain why subdomain takeover and registrar compromise are DNS risks that no protocol extension addresses.

---
> 🔼 Up: [[Core Network Services]]
