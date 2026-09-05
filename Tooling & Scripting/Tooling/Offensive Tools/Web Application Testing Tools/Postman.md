---
title: "Postman"
aliases: ["postman", "Newman"]
tags: [tree/tooling, cyber/tooling/offensive/web/postman, type/tool, difficulty/medium]
Domain: "[[Web Application Testing Tools]]"
Color: "#708090"
verified: 2026-09-05
---

# Postman

> [!abstract] Note of [[Web Application Testing Tools]]
> Postman organises collections of API requests, injects auth through environment variables, and codifies checks as assertions a CLI runner gates a pipeline on. This note covers the variable-and-environment model that makes cross-user testing two clicks, and why the secrets that model stores are the tool's real security exposure.

Postman is the graphical API workbench. Where curl sends one request, Postman organizes **collections** of requests, manages **environments** and variables, handles complex auth (OAuth2, Bearer, HMAC), and runs **test scripts** against responses. For modern targets that are mostly JSON APIs, it is the fastest way to map an API, replay authenticated calls, and automate a regression suite — including a CLI runner (`newman`) for CI.

> [!warning] Authorized targets only
> Postman replays real, often authenticated, API calls. Use a dedicated test environment and credentials, and never point a collection at production without scope.

## Parent Learning Order
curl -> Postman -> Burp Suite -> OWASP ZAP -> Nikto -> WPScan -> SQLmap

## Structured input, structured output, gated by auth

> *Testing one API request by hand is easy. What is the hard part?*
>
> Hold your answer — the section below is the response.

An API is a set of endpoints that take structured input (usually JSON) and return structured output, gated by authentication. Testing one request by hand is easy; the hard part is testing *many* requests, as *different users*, *repeatedly*, without re-typing tokens. Postman's answer is three layers stacked on top of a single request.

```mermaid
flowchart TD
    C["Collection (grouped requests)"] --> R["Request builder: method, URL, headers, body, auth"]
    E["Environment: {{base_url}}, {{token}}"] -.injects.-> R
    R --> S["Response"]
    S --> T["Tests tab (JS assertions)"]
    T --> N["Newman CLI -> CI pipeline"]
```

`{{variables}}` are the key idea: define `{{base_url}}` and `{{token}}` once in an *environment*, reference them everywhere, and switch from staging to your low-priv test user by changing one dropdown.

## Importing a spec, or pasting a curl command

**Build a request** by importing an OpenAPI/Swagger spec (Postman generates the whole collection) or pasting a curl command — *Import → Raw text → paste `curl ...`* converts it into a Postman request instantly. That curl↔Postman bridge means everything you learned in **curl** transfers directly.

**Capture auth once, reuse everywhere.** Put a login request first, then in its *Tests* tab save the returned token to an environment variable so every later request is authenticated:

```javascript
// Tests tab of the /login request
const body = pm.response.json();
pm.environment.set("token", body.access_token);
pm.test("login ok", () => pm.response.to.have.status(200));
```

Subsequent requests set `Authorization: Bearer {{token}}` and just work — no copy-paste.

**Find access-control bugs by swapping environments.** Save `customer_a` and `customer_b` tokens in two environments, then fire the *same* `GET /api/orders/{{order_id}}` at customer B's object using customer A's token — a classic IDOR/BOLA test, run in two clicks.

## Newman, and turning a collection into a CI gate

Postman's real power at the Root level is **Newman**, the CLI runner that turns a saved collection into a repeatable, CI-gating test suite:

```shell-session
operator@ci:~$ newman run api-tests.postman_collection.json -e staging.postman_environment.json
→ Login
  POST https://staging.meridian.test/login [200 OK, 412B, 141ms]
  ✓  login ok
→ Cross-tenant read (should be 404)
  GET https://staging.meridian.test/api/orders/9001 [200 OK, 512B, 88ms]
  1✗  expected 404 but got 200
┌─────────────────────────┬──────────┬──────────┐
│                         │ executed │   failed │
├─────────────────────────┼──────────┼──────────┤
│              assertions │        6 │        1 │
└─────────────────────────┴──────────┴──────────┘
```

**The deliberate break:** the "Cross-tenant read" test *expected a 404* — proof that customer A cannot see customer B's order — but got **200**. Newman fails the run (non-zero exit), so the broken-access-control regression blocks the pipeline. This is the payoff of Postman over curl: the authorization test is codified as an assertion, run every build, not a one-off manual check that rots.

**How you'd spot it:** a suite worth keeping asserts on status codes that should be *refusals*. A collection where every test expects `200` is checking that the API works, not that it is safe. In CI the signal is Newman's exit code — a cross-tenant test that starts passing after a deploy has caught a real access-control regression.

Internals worth knowing: Postman variables have a **scope chain** (global → collection → environment → local), and a subtle bug is a stale global shadowing an environment value — check the variable's resolved value in the console. Pre-request scripts run *before* the request (used for HMAC signing or timestamp nonces). And beware secret hygiene: tokens saved in environments are stored locally and can sync to the cloud — use "secret" variable type and never commit exported environments containing live credentials.

## Security Implications

**A Postman collection is a place secrets go to leak.** Environments and requests routinely hold live tokens, API keys and passwords, and a collection or environment file committed to a git repository or shared with a teammate carries them along — exported Postman files are a recurring source of real credential breaches. Keep secrets in environment variables, never in the request, and never commit an environment file that holds a live token.

**It replays real, authenticated requests, so a collection is as dangerous as where it points.** A suite aimed at production runs as a real user and can create, modify or delete real data. A dedicated test environment and a low-privilege test account are what keep a regression run from being a production incident.

**Codified authorization tests are its security payoff.** The cross-tenant assertion — request customer B's object with customer A's token and expect a 404 — turns a broken-access-control check into something Newman runs every build and fails the pipeline on, rather than a one-off manual test that rots. That is the case for Postman over curl in a security context: the check outlives the tester.

## Summary

You should now be able to:

- Explain what collections, environments and `{{variables}}` each solve that raw curl does not.
- You have two users' tokens. Describe the two-click IDOR test Postman makes trivial.
- Explain how a Newman assertion turns a manual authorization check into a CI gate, using the cross-tenant 404 example.

---
> 🔼 Up: [[Web Application Testing Tools]]
