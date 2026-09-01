# The Pattern Glossary

**The Name**, from the Teaching Standard §2: give the deep structure a label the
reader can carry, and reuse that exact label everywhere it reappears. Named
patterns are chunks, and chunking is what expertise physically is. A reader who
has met "parser differential" six times across networking, web and crypto has a
unit of thought. A reader who met six unnamed instances has six facts.

**One pattern, one name.** A pattern with two names is two patterns. Before
inventing a label, check this file; before adding one, confirm it recurs in at
least three notes across at least two domains.

Every instance below was verified to exist in the corpus.

---

## Parser Differential

> **Two components disagree about where a value ends, or what it means — and the
> one that validates is not the one that acts.**

The security boundary is not the validator. It is the *gap* between the
validator's reading of the input and the executor's reading of the same bytes.
Anything that closes the gap fixes the whole class; anything that patches one
payload fixes nothing.

| Where it appears | The two readers |
|:--|:--|
| **HTTP Request Smuggling** | Front-end proxy and back-end server disagree on `Content-Length` vs `Transfer-Encoding` |
| **SQL Injection** | The application treats input as data; the database's parser reads it as grammar |
| **NoSQL Injection** | A scalar is expected; the driver deserialises an object carrying operators |
| **File Inclusion & Path Traversal** | The validator sees a filename; the filesystem resolves a path |
| **XML External Entity Testing** | The schema check and the entity resolver read the same document differently |
| **File Upload Security Testing** | Extension check, MIME check and the server's execution decision each read a different part |
| **Ethernet & Frame Structure** | A device that parses payloads differently from its neighbour creates an evasion surface |

**The Tell:** two components in the path that both interpret the same input, with
only one of them validating. Ask which one *acts*, and whether it re-reads.

**Why it transfers:** these look nothing alike on the surface — a header, a quote
mark, a `../`, a JSON object. Compare where the two readers diverge in any two of
them and the shared shape is unmistakable. That instructed comparison is the
single strongest transfer lever in the research behind this standard: 48% versus
19%.

---

## Unauthenticated Claim

> **A field that anyone can write, which the receiver acts on as though someone
> verified it.**

The protocol defines no check, so there is nothing to bypass — the attack is
simply telling the truth's shape without the truth.

| Where it appears | The claim nobody verifies |
|:--|:--|
| **MAC Addressing & Switch Operation** | The source MAC is whatever the sender wrote; the switch *learns* from it |
| **ARP & Neighbor Discovery** | An ARP reply asserts an IP-to-MAC binding with no proof |
| **Address Assignment & DHCP** | A client accepts the first DHCP offer; nothing distinguishes the real server |
| **BGP & Internet Routing** | An AS announces reachability for a prefix it does not own |
| **Web Architecture & Proxies** | `X-Forwarded-For` is set by the client and trusted downstream |
| **Ethernet & Frame Structure** | The EtherType is a sender's claim about the payload |

**The Tell:** a value that arrives from the network and is used in a decision,
with no signature, no shared secret, and no out-of-band confirmation behind it.

**The fix is always the same shape:** bind the claim to something the claimant
cannot forge (DAI and DHCP snooping bind to a port; RPKI binds a prefix to an AS),
or stop treating it as evidence.

---

## Verification Chosen by the Input

> **The thing being verified gets to say how it should be verified.**

A special case of trusting an unauthenticated claim, but worth its own name
because the fix is so specific: the *server* decides the algorithm, never the
message.

| Where it appears | What the input dictates |
|:--|:--|
| **JWT Security** | The token's `alg` header selects the verification method — `none`, or RS256→HS256 confusion |
| **TLS and PKI** | A certificate verifies only against a trust store; add a rogue root and every forgery passes |
| **Digital Signatures** | A signature is meaningless without pinning which key and which hash were expected |

**The Tell:** verification code that reads a parameter *out of the untrusted
object* to decide how to check the untrusted object.

---

## Shared Secret, No Per-Party Binding

> **One secret authenticates everyone, so it identifies no one and cannot be
> revoked for one party.**

| Where it appears | The shared secret |
|:--|:--|
| **Wi-Fi Security & WPA** | WPA2-Personal: one passphrase for every device, and capturing a handshake moves the attack offline |
| **Broken Access Control** | A predictable or shared identifier standing in for authorisation |
| **Insecure Deserialization Testing** | A signing key shared across services turns any holder into a signer |

**The Tell:** ask who else holds this, and what happens when one of them leaves.
If the answer is "we change it for everybody", it is a shared secret, not an
authenticator.

---

## Time-of-Check to Time-of-Use

> **The state verified and the state used are separated by a window someone else
> can act in.**

| Where it appears | The window |
|:--|:--|
| **Race Condition & Concurrency Testing** | Between the balance check and the debit |
| **Server-Side Request Forgery** | Between validating a URL and fetching it — DNS can answer differently the second time |

**The Tell:** a check and an action on the same resource that are not atomic. If
you can describe a moment *between* them, it is exploitable in principle.

---

## Adding a pattern

1. Confirm it appears in **three or more notes across two or more domains**.
   Fewer than that is a topic, not a pattern.
2. Name the *mechanism*, not the exploit. "Parser differential", not "smuggling".
3. Add the row table and the Tell — a pattern without a recognition cue cannot be
   used by a reader who has not already met it.
4. Use the exact name in every note listed, in **bold**, so the corpus reads as
   one vocabulary.
