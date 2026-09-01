---
title: "Prototype Pollution & DOM Security"
aliases: ["Prototype Pollution", "DOM Security", "JavaScript Prototype Pollution"]
tags: [tree/offensive, cyber/offensive/web/client-side/prototype, type/technique, difficulty/hard]
Domain: "[[Client-Side Web Security]]"
Color: "#DC143C"
---

# 🧬 Prototype Pollution & DOM Security

> [!warning] Authorized simulation only
> Prototype pollution can escalate to XSS or RCE via gadgets. Prove it with a benign polluted property observed in a controlled context, never a working exploit against real users. Test only in-scope applications you build or are authorized to assess.

## Parent Learning Order
CORS & Clickjacking -> Cross-Site Scripting -> CSRF & SameSite Testing -> Prototype Pollution & DOM Security

## Poisoning the Blueprint Every Object Shares

> *You set one property on one object. How many objects changed?*
>
> Hold your answer — the section below is the response.

In JavaScript, almost every object inherits from a shared blueprint: `Object.prototype`. Properties on that blueprint are visible to *every* object in the program. **Prototype pollution** is a flaw where attacker input can *write* to that shared blueprint — typically via a specially-crafted key like `__proto__` — so a property the attacker sets appears on *all* objects at once. This is uniquely dangerous because it corrupts the application globally: a single polluted property can change how unrelated code behaves, and combined with a "gadget" (code that reads that property), it escalates to XSS or even server-side code execution in Node.js.

The root cause is a **recursive merge or property-set that trusts attacker-controlled keys** — copying user JSON into an object without rejecting `__proto__`, `constructor`, and `prototype` keys.

> [!tip] The analogy, and where it breaks
> Prototype pollution is like editing the *default template* every document in an office inherits from — change one line in the template and every future and existing document silently gains it. The analogy breaks on reach: an office template only affects documents, whereas `Object.prototype` underlies *all program logic*, so a polluted property can alter security checks, rendering, and control flow in code that never touched the attacker's input.

**Prerequisites:** JavaScript objects and prototypes, JSON handling, and XSS (the common escalation).

## The Mechanism: `__proto__` as a Write Target

When code recursively merges attacker-controlled data (a common pattern for config, query params, or JSON bodies), a key named `__proto__` may be interpreted not as a normal property but as a reference to the object's prototype:

```text
attacker sends:  {"__proto__": {"isAdmin": true}}
vulnerable merge writes to:  Object.prototype.isAdmin = true
result:  EVERY object now has .isAdmin === true
```

Now any code that checks `if (user.isAdmin)` — even for a user object that never had that property set — sees `true`, because it inherits it from the polluted prototype. The pollution is invisible in the object's own properties; it lives on the shared prototype.

```bash
# demonstrate the pollution mechanism in Node (or any JS engine)
node -e '
const merge = (t,s) => { for (const k in s) { if (typeof s[k]==="object") { t[k]=t[k]||{}; merge(t[k],s[k]); } else t[k]=s[k]; } return t; };
const user = {};
merge({}, JSON.parse("{\"__proto__\":{\"polluted\":\"CANARY\"}}"));   // attacker input
console.log("a fresh, unrelated object now has:", ({}).polluted);
'
```

```text
a fresh, unrelated object now has: CANARY
```

A brand-new empty object `{}` — never touched by the attacker — now has `.polluted === "CANARY"`, because the merge wrote to `Object.prototype`. That global contamination from one input is the finding.

## From Pollution to Impact: Gadgets

Prototype pollution alone sets a property everywhere; the *impact* comes from a **gadget** — existing code that reads a polluted property in a dangerous way:

- **XSS gadget** — a template engine or DOM sink that reads a config property you polluted, injecting your value as HTML.
- **Auth bypass gadget** — code checking `user.isAdmin` that now sees the polluted `true`.
- **RCE gadget (Node.js)** — a property that flows into `child_process` options, a require path, or template compilation, reaching command execution.

This mirrors the deserialization gadget-chain idea: the attacker supplies data, and the *application's own code* turns it into impact. The pollution is the primitive; the gadget is the escalation.

```mermaid
flowchart TD
    I["Attacker JSON with __proto__ key"] --> M{"Recursive merge trusts the key?"}
    M -->|"Yes"| P["Object.prototype polluted globally"]
    M -->|"No (key rejected)"| S["Safe"]
    P --> G{"Gadget reads the polluted property?"}
    G -->|"HTML sink"| X["XSS"]
    G -->|"auth check"| A["Privilege bypass"]
    G -->|"Node exec path"| RCE["Server-side RCE"]
    G -->|"none"| L["Pollution present, impact latent"]
```

## Pollution with no gadget is still a finding

- **Pollution without a gadget.** You can pollute the prototype but find no gadget to escalate — still a finding (the pollution primitive), because a future code change or library update can add a gadget. Report the primitive.
- **Invisible in own-properties.** The polluted property does not appear in the object's own keys (`Object.keys()` misses it) — check inherited properties (`obj.polluted`, `in` operator) to detect it.
- **Proving with a working exploit.** A benign polluted property (a canary) observed on an unrelated object proves the flaw; chaining to a real XSS/RCE is over-proving unless the gadget analysis is the point.
- **Client vs. server.** Client-side pollution escalates to DOM XSS; server-side (Node.js) can reach RCE. Identify where the vulnerable merge runs.
- **Framework nuance.** Modern libraries increasingly reject `__proto__`, so a failed payload may mean a patched library — try `constructor.prototype` and other paths before concluding safe.

## Security Implications — Detection & Defense

- **Reject dangerous keys** (`__proto__`, `constructor`, `prototype`) when merging or setting properties from untrusted input — the direct fix. Use `Object.create(null)` for maps (no prototype to pollute), or a `Map` instead of a plain object.
- **Freeze the prototype** (`Object.freeze(Object.prototype)`) as defense-in-depth so it cannot be written even if a merge is flawed.
- **Use safe merge libraries** and keep dependencies updated — many prototype-pollution CVEs are in popular utility libraries (lodash, jQuery historically), so the flaw often arrives via a dependency.
- **Schema-validate untrusted JSON** so unexpected keys like `__proto__` are rejected before any merge.
- **Detection** is hard because the payload is valid JSON; look for `__proto__`/`constructor` keys in inputs and the downstream *effects* (unexpected global property behavior). The durable defense is prevention at the merge boundary.

## Summary

You should now be able to:

- Explain why writing to `Object.prototype` affects every object, and why a `__proto__` key in untrusted JSON is dangerous.
- Demonstrate prototype pollution with a benign canary and escalate it via an existing gadget (auth bypass), and detect pollution via inherited (not own) properties.
- Explain how gadgets turn the pollution primitive into XSS/RCE, why the pollution is invisible in own-properties, and why key rejection, `Object.create(null)`, and prototype freezing are the layered fixes.

---
> 🔼 Up: [[Client-Side Web Security]]
