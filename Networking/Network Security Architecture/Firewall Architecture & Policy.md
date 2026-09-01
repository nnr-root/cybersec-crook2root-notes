---
title: "Firewall Architecture & Policy"
aliases: ["Packet Filter", "Stateful Inspection", "NGFW", "Firewall Rules", "Default Deny"]
tags:
  - tree/networking
  - cyber/networking/secarch
  - type/concept
  - difficulty/medium
  - level/apprentice
Domain:
  - "[[Network Security Architecture]]"
Color: "#42D4F4"
---

# 🧱 Firewall Architecture & Policy

> [!abstract] Note of [[Network Security Architecture]]
> A firewall is a policy decision made on every packet, and the quality of that decision depends far more on how the rules are written than on the product. This note traces firewalls from simple packet filters to application-aware inspection, and then focuses on the discipline of policy — default-deny, rule ordering, and the reviews that keep a rule base from rotting into a liability.

## Parent Learning Order
Firewall Architecture & Policy -> Network Segmentation & Zero Trust -> VPNs & Encrypted Tunnels -> Intrusion Detection & Network Monitoring -> Egress Control & Web Proxies -> Network Access Control

## A Decision on Every Packet

> *Your firewall permits 443 inbound to the web server. Does it stop SQL injection?*
>
> Hold your answer — the section below is the response.

A **firewall** enforces a policy about which traffic may pass a boundary. For every packet or connection, it asks a question — "does a rule permit this?" — and either forwards or drops. That is the entire concept; everything else is how sophisticated the question can be and how well the rules are written.

Firewalls evolved through generations, each seeing more:

| Generation | Decides on | Sees | Limitation |
| --- | --- | --- | --- |
| **Packet filter** | Individual packets, five-tuple | Addresses, ports, flags | No memory of connections |
| **Stateful firewall** | Connections | Connection state, related flows | No understanding of content |
| **Next-generation (NGFW)** | Applications and users | Application identity, user, content | Complexity, performance, TLS blindness |

A **packet filter** examines each packet in isolation against static rules. It is fast and simple but stateless — it cannot tell a reply to a request your host made from an unsolicited packet crafted to look like one, so permitting return traffic requires broad, abusable rules.

A **stateful firewall** tracks connections in a table. When it permits an outbound flow, it records the five-tuple and automatically allows the matching return traffic. This makes policy both tighter and simpler — "permit outbound HTTPS" and replies are handled implicitly — and it is the baseline for any serious firewall today.

A **next-generation firewall** goes further, identifying the *application* regardless of port (recognizing that traffic on 443 is a file transfer, not web browsing), tying decisions to *user identity*, and inspecting *content*. This power comes at the cost of complexity, performance, and a hard dependency on being able to see inside TLS — which, as encryption becomes universal, is an increasing blind spot.

**Prerequisites:** IP addresses, ports, and the five-tuple.

> [!tip] The analogy, and where it breaks
> A doorman with a guest list. The sound version admits only names on the list and turns away everyone else; the doomed version tries to memorise every troublemaker in the city and admits all others. The analogy breaks at statefulness: a doorman does not need to remember that *you* went out in order to let your taxi back in, whereas that memory of an outbound conversation is exactly what a stateful firewall keeps and what makes tight policy practical.

**The deliberate break:** "the firewall blocks attacks" is the mental model almost everyone starts with, and it quietly assumes the firewall knows what an attack is.

It does not. A firewall matches a **policy about connections** — addresses, ports, protocol, and for a stateful one, whether this packet belongs to a flow it already permitted. If your rule allows 443 inbound to the web server, it allows every request that arrives on 443, benign and hostile alike. The firewall is not failing when an SQL injection reaches your application; it is doing exactly what it was configured to do.

**How you'd spot an over-broad rule:** read the address range as its literal extent, not its notation. A `/16` in a permit rule is 65,534 hosts — write it out before approving it.

## Stateful Inspection in Practice

The stateful model is worth seeing concretely, because it is where most policy lives.

```bash
sudo nft list ruleset
```

Expected excerpt:

```text
table inet filter {
  chain input {
    type filter hook input priority filter; policy drop;
    ct state established,related accept
    ct state invalid drop
    iif "lo" accept
    tcp dport 22 ip saddr 10.10.0.0/16 accept
    tcp dport 443 accept
  }
}
```

Read this top to bottom, because that is how it executes:

- **`policy drop`** is the foundation — **default deny**. Anything not explicitly permitted is dropped. This is the single most important property of a sound firewall: the rule base states what is *allowed*, and everything else is denied by default. The opposite (default allow, block known-bad) is unwinnable, because you cannot enumerate all bad traffic.
- **`ct state established,related accept`** is the stateful heart: return traffic for existing connections is permitted because a connection exists, not because an address is trusted. `related` covers helper flows like an FTP data connection tied to a control connection.
- **`ct state invalid drop`** discards packets that match no known connection and are not a valid new one — a cheap, high-value rule.
- **`tcp dport 22 ip saddr 10.10.0.0/16 accept`** permits SSH only from internal addresses. Restricting by both port and source is far stronger than by port alone.

Rules are evaluated **in order**, and the first match wins. This makes ordering a correctness property: a broad `accept` placed above a specific `drop` renders the drop dead, silently permitting what you meant to block. Auditing a rule base means reading it as the firewall does — sequentially — not as a set.

## Where Firewall Policy Goes Wrong

**Rule bloat.** Rules accumulate over years. Each is added for a reason; few are ever removed. The result is a rule base nobody fully understands, containing overlapping, redundant, and contradictory entries. A rule that overlaps a broader one above it never fires; a rule for a decommissioned service is a hole nobody remembers opening. Periodic rule review — removing unused rules, tightening broad ones, confirming each still has a justification — is what keeps the policy an asset rather than an accumulating liability.

**Overly broad rules.** `permit any any` on a segment, or a rule allowing an entire `/8` where a `/24` was intended, authorizes vastly more than the author realized. Because address ranges hide their size in the notation, reviewing a rule base by expanding every range to its literal extent reveals the gap between intent and effect.

**Any-any-any at the bottom that should be a deny.** A rule base without an explicit final deny relies on the default, which is fine only if the default is drop. Making the final deny explicit — and logging it — turns "everything else" into visible, investigable events.

```mermaid
flowchart TD
    P["Packet arrives"] --> R1{"Rule 1 match?"}
    R1 -->|"Yes"| A1["Apply rule 1 action, STOP"]
    R1 -->|"No"| R2{"Rule 2 match?"}
    R2 -->|"Yes"| A2["Apply rule 2 action, STOP"]
    R2 -->|"No"| RN{"...more rules..."}
    RN -->|"No match"| D["Default policy: DROP (and log)"]
```

## Security Implications

**Default-deny is the difference between a firewall and a suggestion.** A default-allow posture requires enumerating all malicious traffic, which is impossible, so it always leaks. Default-deny requires enumerating legitimate traffic, which is finite and knowable. Every sound firewall policy is a default-deny with an explicit allowlist, and inverting that is the most consequential mistake in firewall design.

**A firewall is not a complete boundary.** It enforces policy on traffic that passes through it, and does nothing about traffic that goes around it — an unmanaged wireless access point, a VPN that tunnels past it, a compromised host initiating outbound connections the policy permits. The firewall is one layer; treating it as the security boundary invites bypass. This is a central motivation for segmentation and zero trust, covered next.

**Logging is half the value.** A firewall that drops silently prevents an attack but records nothing. A firewall that logs its denies turns every blocked attempt into telemetry — reconnaissance scans, policy violations, and misconfigurations all surface in the deny log. Logging the final default-deny rule specifically captures everything the explicit rules did not anticipate.

**Egress is as important as ingress, and more neglected.** Most firewall attention goes to inbound rules, but outbound control catches data exfiltration, malware calling home, and connections to known-bad destinations. A default-deny *outbound* policy — permitting only necessary outbound traffic — is one of the highest-value and least-common controls, and it is where the egress-control material extends this note.

**Complexity is itself a risk.** Next-generation features add power and add ways to misconfigure. A firewall with hundreds of application-aware rules, user mappings, and inspection profiles has a large surface for the one mistake that opens a hole. Simplicity in the rule base is a security property.

All firewall configuration and testing described here must target only systems within an authorized scope. Modifying rules on a shared firewall affects every flow it governs, and probing a firewall's policy is reconnaissance that is logged.

## Summary

You should now be able to:

- Explain what a firewall decides on every packet and the difference between a stateless packet filter and a stateful firewall; state why default-deny is the sound posture.
- Read a stateful ruleset, explain the `established,related` rule and first-match-wins ordering, and diagnose a dead rule caused by a broader rule above it.
- Explain why default-allow is unwinnable and default-deny is finite; argue why egress control and deny-logging are high-value and neglected, and why a firewall is one layer rather than a complete boundary — motivating segmentation and zero trust.

---
> 🔼 Up: [[Network Security Architecture]]
