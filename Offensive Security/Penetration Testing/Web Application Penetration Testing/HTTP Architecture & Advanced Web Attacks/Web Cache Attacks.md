---
title: "Web Cache Attacks"
aliases: ["Web Cache Poisoning", "Web Cache Deception", "Cache Poisoning", "Cache Deception"]
tags: [tree/offensive, cyber/offensive/web/http/cache, type/technique, difficulty/medium]
Domain: "[[HTTP Architecture & Advanced Web Attacks]]"
Color: "#DC143C"
---

# 🗄️ Web Cache Attacks

> [!warning] Authorized simulation only
> Cache attacks can serve poisoned content to *other users* or leak *other users'* private data. Prove them in a lab you build with synthetic data, and treat production testing as high-risk requiring explicit authorization. Use benign markers only.

## Parent Learning Order
Server-Side Request Forgery -> HTTP Request Smuggling -> Web Cache Attacks -> WAF Testing & Bypass Methodology

## Attacking the Thing That Serves Many Users One Copy

A **web cache** (CDN edge, reverse proxy) stores a copy of a response and serves it to many users, to cut latency and load (the mechanism is in the Networking Application Delivery leaf). That "one copy for many users" property is exactly what makes it an attack target: if an attacker can get a *malicious* copy into the cache, it is served to every subsequent user; and if the cache stores a *private* response under a key others can request, it leaks that user's data.

Two attacks exploit this from opposite directions:

| Attack | Direction | Result |
| --- | --- | --- |
| **Cache Poisoning** | Attacker puts bad content *into* the cache | Malicious response served to all users |
| **Cache Deception** | Attacker tricks the cache into storing a *victim's private* response | Attacker retrieves another user's data |

Both hinge on the **cache key** — the set of request features the cache uses to decide "is this the same request?" A mismatch between what the cache keys on and what the server uses to build the response is the vulnerability.

> [!tip] The analogy, and where it breaks
> Cache poisoning is like slipping a forged notice into a shared bulletin board everyone reads; cache deception is like a shared printer caching your private document under a name a stranger can retrieve. The analogy breaks on *scale and automation* — the "bulletin board" serves millions instantly, and the attacker can precisely engineer which request features are keyed, so the poisoning is targeted and reproducible, not a hopeful pin on a corkboard.

**Prerequisites:** the Networking Application Delivery leaf (caching), HTTP headers, and cache-key concepts.

## Cache Poisoning: Getting Bad Content Cached

Cache poisoning exploits an **unkeyed input** — a request feature the server uses to build the response but the cache *ignores* when computing its key. If the server reflects an `X-Forwarded-Host` header into a response, but the cache keys only on the URL, then:

1. Attacker sends a request with a malicious `X-Forwarded-Host` (reflected into the response, e.g. a script URL).
2. The cache stores that poisoned response under the *normal* URL key (ignoring the header).
3. Every subsequent user requesting that URL gets the poisoned response — no header needed.

```bash
# find an unkeyed header that changes the response but not the cache key (your own lab cache)
curl -s "http://127.0.0.1:8112/page" -H "X-Forwarded-Host: evil.example" | grep -o 'evil.example'
```

```text
evil.example
```

The `X-Forwarded-Host` was reflected into the response. If the cache does not include that header in its key (the common case), this poisoned response gets cached and served to everyone — an XSS or redirect delivered at cache scale.

## Cache Deception: Stealing Private Responses

Cache deception works the other way: trick the cache into storing a *dynamic, private* page as if it were a *static, cacheable* file. If a cache is configured to cache anything ending in `.css` or `.js`, and the server ignores the extra path segment:

```text
attacker lures victim to:  /account/settings/nonexistent.css
server returns:  the victim's private /account/settings page (ignoring the .css)
cache stores it:  under the .css key, believing it's a static file
attacker then requests:  /account/settings/nonexistent.css  -> gets the VICTIM's cached private page
```

The victim's authenticated response is cached under a URL the attacker can request, so the attacker retrieves the victim's private data. The root cause is the same key mismatch: the cache decides "cacheable" from the extension, the server builds a private response, and they disagree.

```mermaid
flowchart TD
    K["Cache key = subset of request features"] --> P{"Server uses an UNKEYED input?"}
    P -->|"reflects unkeyed header"| POISON["Poisoning: malicious response cached for all"]
    K --> D{"Cache 'cacheable' rule != server's private/dynamic response?"}
    D -->|"caches by extension"| DECEIVE["Deception: victim's private page cached under attacker-fetchable key"]
    POISON --> M["Root cause: cache-key vs. response-building mismatch"]
    DECEIVE --> M
```

## Attacks that hit everyone but the tester

- **Affects other users.** Both attacks impact people other than the tester — a poisoned cache serves everyone; deception steals a victim's data. Prove in a lab with synthetic users; production testing is high-risk.
- **Finding the unkeyed input.** Poisoning requires an input that changes the response but not the key — systematically test headers (`X-Forwarded-Host`, `X-Forwarded-Scheme`, etc.) for reflection *and* confirm the cache ignores them.
- **Cache-key opacity.** You often cannot see the exact cache key; infer it by observing which request changes produce a cache HIT vs. MISS. Misjudging the key wastes effort.
- **TTL and eviction.** A poisoned entry lasts only until it expires; the impact window is the TTL. Note it, and re-poisoning may be needed for sustained impact.
- **Benign proof.** Demonstrate with a harmless reflected marker (a canary hostname) that gets cached, not a working XSS against real users.

## Security Implications — Detection & Defense

- **Key the cache on everything the response depends on.** The definitive fix: if the server uses a header to build the response, that header must be part of the cache key (or the server must not reflect it). The mismatch is the vulnerability.
- **Do not reflect unkeyed input** into cacheable responses — `X-Forwarded-Host` and similar should never flow into a response the cache stores under a URL-only key.
- **Cache by content, not extension.** Deception is defeated by caching decisions based on actual content-type and cache-control headers, not the URL suffix — and by never caching authenticated/private responses.
- **`Cache-Control: private/no-store`** on personalized responses prevents them being cached at all — the direct deception fix.
- **Detection** looks for anomalous cache entries (a private page cached publicly) and for reflected-header content in cached responses; the durable defense is correct cache-key configuration, audited against what the server actually varies on.

## Summary

You should now be able to:

- Explain why a shared cache is an attack target, and the difference between poisoning (bad content in) and deception (private data out).
- Find an unkeyed reflected header, poison a cache so a victim gets the malicious cached response, and explain cache deception's extension trick.
- Explain why the cache-key/response mismatch is the root of both attacks, why keying on everything the response varies on (and never caching private responses) is the fix, and how this relates to smuggling-based cache poisoning.

---
> 🔼 Up: [[HTTP Architecture & Advanced Web Attacks]]
