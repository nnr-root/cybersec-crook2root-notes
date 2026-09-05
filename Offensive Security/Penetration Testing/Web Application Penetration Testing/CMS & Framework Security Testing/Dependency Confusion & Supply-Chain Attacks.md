---
title: "Dependency Confusion & Supply-Chain Attacks"
aliases: ["Dependency Confusion", "Supply Chain Attacks", "Namespace Confusion", "Package Confusion", "Typosquatting"]
tags: [tree/offensive, cyber/offensive/web/supply-chain, type/technique, difficulty/medium]
Domain: "[[CMS & Framework Security Testing]]"
Color: "#DC143C"
verified: 2026-09-05
---

# 📦 Dependency Confusion & Supply-Chain Attacks

> [!warning] Authorized testing only
> Dependency confusion testing requires explicit authorization. Publishing a package to a public registry — even a benign one — is a permanent act that can affect any organization whose build system resolves that name. All testing uses a pre-agreed package name in the target's own private registry namespace, and no package is published to a public registry without written authorization from the target and confirmation that the name is reserved.

## Parent Learning Order
Framework & CMS Testing Methodology -> WordPress Security Testing -> Dependency Confusion & Supply-Chain Attacks

## When the Build System Fetches the Wrong Package

> *Your organization has a private npm package called `meridian-internal-utils` hosted on an internal registry. A developer adds it to `package.json`. Where does `npm install` look first?*
>
> Hold your answer — the section below is the response.

Modern applications are assembled more than they are written: hundreds of
dependencies — direct, transitive, open-source, and internal — are resolved at
build time and stitched into the final artefact. **Supply-chain attacks** target
that resolution process rather than the application code itself, inserting
malicious code into the build *before* the developer sees it, via packages the
build system fetches automatically.

**Dependency confusion** (also called *namespace confusion*) is the most
impactful variant discovered in recent years: an attacker publishes a package to
a *public* registry (npm, PyPI, Maven Central, RubyGems) with the same name as
the victim's *private, internal* package. Package managers resolve public
registries before — or instead of — private ones unless explicitly configured
otherwise, so the build system fetches and executes the attacker's package,
believing it to be the internal one. Alex Birsan's 2021 research demonstrated
this against Apple, Microsoft, PayPal, and dozens of other organizations using
only names extracted from public artefacts like JavaScript bundles and
`requirements.txt` files.

**Typosquatting** is a related but distinct technique: the attacker publishes a
package with a name that is a plausible typographical variant of a popular one
(`reqeusts`, `colorma`, `lodahs`). A developer who miskeys the name installs the
attacker's version. The confusion variant exploits resolution order on a *correct*
name; the typosquatting variant exploits a *wrong* name that resolves to an
attacker-controlled one.

> [!tip] The analogy, and where it breaks
> Dependency confusion is like a postal scam that exploits the sorting office's
> rules: your company ships internal memos under the label "Meridian Internal
> Mail" through a private courier. An attacker registers a new public postal
> service that also accepts packages labelled "Meridian Internal Mail" and
> publishes its address in the global phone book. When a new employee looks up
> the address to send a memo, the public listing appears first — so the memo goes
> to the attacker. The analogy breaks on scale: unlike a single memo, a
> `package.json` fetch runs in every developer's local build, every CI pipeline,
> and every container build, so one public package registration can intercept
> thousands of independent build events simultaneously.

**Prerequisites:** [[Framework & CMS Testing Methodology]] (understanding the
build pipeline), and basic package manager mechanics for the target ecosystem.

## How package managers resolve names — and where confusion enters

Every package manager has a resolution order that determines which registry is
consulted when a package name is requested. The default in most ecosystems
**favours public registries**, and private registry configuration must be explicit:

| Ecosystem | Default public registry | Private registry mechanism | Confusion vector |
|---|---|---|---|
| **npm / yarn** | `registry.npmjs.org` | `.npmrc` scoped config or `--registry` flag | Unscoped names resolve to npm public; scoped names (`@meridian/...`) require explicit scope-to-registry mapping |
| **pip / PyPI** | `pypi.org` | `--index-url` or `[global]` in `pip.conf` | If `--extra-index-url` is used alongside a private index, PyPI wins on version ordering |
| **Maven (Java)** | Maven Central | `<repositories>` in `pom.xml` | First matching repository wins; Central is typically first unless overridden |
| **RubyGems** | `rubygems.org` | `source` directive in `Gemfile` | A Gemfile with both a private source and `rubygems.org` fetches whichever has the higher version number |
| **NuGet (.NET)** | `nuget.org` | `nuget.config` `packageSources` | Highest version number across all configured sources wins |

The critical insight across all ecosystems: **a higher version number on the
public registry wins** in many default configurations, regardless of the private
registry entry. An attacker who publishes `meridian-internal-utils@9999.0.0`
to npm will outbid any real version on the private registry.

## Finding candidate names for authorized testing

Private package names appear in more places than most developers realize:

```bash
# 1. JavaScript bundle — package names often leak in function/class names and map files
strings build/main.js | grep -E "require\(|from ['\"]" | grep -v node_modules | sort -u

# 2. requirements.txt / package.json committed to a public repo or CDN
# search for target-unique prefixes in public GitHub
# (always under authorization — confirm scope before extracting any names)

# 3. Docker image layers — package install steps in RUN directives
docker history --no-trunc app.meridian.test/api:latest | grep "pip install\|npm install"

# 4. CI/CD pipeline definitions (Jenkinsfile, .github/workflows, .gitlab-ci.yml)
# often committed to version control and visible in public repos
grep -r "install\|registry" .github/workflows/ | grep "internal\|private\|meridian"

# 5. Error messages — a failed build log may name the package it couldn't fetch
```

For an authorized assessment, the output of these steps is a list of package
names to verify against the relevant public registry — checking whether the name
is already registered, and whether the organization has claimed it.

## The resolution order test — without publishing anything

A safe, passive test determines whether the build system *would* resolve a public
package over a private one, without actually publishing one:

```bash
# npm: check whether a private package name is registered on npm public
npm view meridian-internal-utils 2>&1
# "npm error code E404" -> name is unclaimed on public npm — vulnerable to confusion

# pip: check PyPI
pip index versions meridian-internal-utils 2>&1
# "ERROR: No matching distribution found" -> unclaimed on PyPI

# Confirm private registry scope configuration (as a build system audit)
cat .npmrc
# Expected safe config: @meridian:registry=https://registry.meridian.test
# Vulnerable config: registry=https://registry.meridian.test (no scope pinning)
#   + unscoped private package name -> resolves to npm public as fallback
```

An unclaimed name on the public registry combined with an unscoped private
package name (or a misconfigured resolution order) is the full finding — it does
not require a publish to demonstrate.

## Lockfile integrity: the defense that also needs testing

A lockfile (`package-lock.json`, `Pipfile.lock`, `Gemfile.lock`) records the
exact resolved version and checksum of every dependency. When the lockfile is
committed and respected, a new install uses the recorded resolution rather than
querying the registry — a lockfile entry for the private registry URL pins the
source. Two testing checks:

```bash
# 1. Is the lockfile committed to version control?
git log --oneline -- package-lock.json | head -3
# No commits -> lockfile not tracked -> fresh installs re-resolve from registry

# 2. Does the lockfile record the private registry URL for internal packages?
grep "meridian-internal-utils" package-lock.json
# Expected: "resolved": "https://registry.meridian.test/..."
# Vulnerable: "resolved": "https://registry.npmjs.org/..." -> wrong source is pinned
```

A missing or misconfigured lockfile means every install is a live registry
resolution — a publish-time injection window that the lockfile was designed to
close.

## Worked Example: spotting the gap without a publish

An authorized dependency audit of a Node.js application on the Meridian lab
network identifies the confusion surface passively.

**Step 1: extract private package names from the build artefact.**

```shell-session
analyst@lab:/tmp/sc-lab$ strings build/bundle.js | grep "require(" | \
  grep "meridian" | sort -u
require("meridian-shipping-calc")
require("meridian-auth-helpers")
```

Two internal packages with no npm scope prefix (`@meridian/...`).

**Step 2: check whether the names are claimed on the public registry.**

```shell-session
analyst@lab:/tmp/sc-lab$ for pkg in meridian-shipping-calc meridian-auth-helpers; do
>   result=$(npm view "$pkg" 2>&1)
>   echo "$pkg: $result"
> done
meridian-shipping-calc: npm error code E404 Not Found
meridian-auth-helpers:  npm error code E404 Not Found
```

Neither name is registered on npm. Any version published to npm under either
name would be fetched by a default-configured `npm install`.

**Step 3: confirm the resolution order is vulnerable.**

```shell-session
analyst@lab:/tmp/sc-lab$ cat .npmrc
registry=https://registry.meridian.test
# no scope prefix — applies to all packages including public ones
# a public package with the same name outbids the private one if higher versioned
```

The `.npmrc` sets the private registry as default but without scope pinning —
`npm install` will still fall back to `registry.npmjs.org` for packages not
found on the private registry. Since neither name exists on the private registry
*or* the public one yet, either publication wins.

**The finding (without a publish):** two unscoped private package names are
unclaimed on the public registry, with no lockfile pinning and no scope-based
isolation. A version published to npm at any version number above the internal
one would be fetched by all developer and CI builds.

**Remediation verified passively:**

```bash
# Correct: scope-pin in .npmrc maps the scope to the private registry
@meridian:registry=https://registry.meridian.test
# Then rename packages to @meridian/shipping-calc — scoped names cannot be
# confused with public unscoped names in any npm version
```

## Treating lockfiles as the complete defense

- **Lockfiles do not protect un-pinned builds.** A `npm ci` respects the
  lockfile; `npm install` with no lock regenerates it — and a compromised
  resolution at regeneration time writes the wrong source into the new lockfile.
  CI pipelines must use `npm ci` (or equivalent) to get lockfile protection.
- **High-version anchoring.** Private package managers can publish an internal
  version at `9999.0.0` to out-version any public confusion package — this is a
  mitigation, not a fix. Scoped naming is the structural fix.
- **Transitive dependencies.** The direct dependencies are visible; their
  transitive dependencies may also be private packages with unclaimed names in
  the same organization. Audit the full dependency graph, not just `package.json`.
- **Scoped names are not universally safe.** npm scopes (`@meridian/...`) require
  correct scope-to-registry mapping in `.npmrc`; a missing or misconfigured
  mapping reverts to npm public even for scoped names.
- **Typosquatting is a separate surface.** Confusion attacks use exact name
  matches; typosquatting attacks target mistyped names. Both require separate
  mitigations — confusion needs scoped names and lockfile integrity, typosquatting
  needs input validation at the package manager CLI level and the organization's
  allowed-package list.

**The deliberate break:** "we use a private registry" reads as protection against
supply-chain confusion.

A private registry stores your internal packages; it does not prevent the package
manager from also consulting a public registry. Unless resolution order is
explicitly configured — scope-pinned for npm, `--index-url` (not `--extra-index-url`)
for pip, explicit `<repositories>` ordering with Central disabled for Maven — the
build system will resolve both sources, and whichever has the higher version
number wins. The private registry and the attacker's public package both win
different races depending on version number alone.

**How you'd spot the misconfiguration:** compare the lockfile's `resolved` URLs
against the expected private registry URL for every internal package. Any
`registry.npmjs.org` URL for an internal package name is a past resolution from
the wrong source.

## Security Implications — the Developer's View

- **Scope all internal packages** (`@org/package-name`) and map that scope
  explicitly to the private registry — a scoped name cannot be claimed by an
  unscoped public package in any npm version, and the scope mapping prevents
  public fallback.
- **Use lockfiles and enforce them in CI** (`npm ci`, `pip install --require-hashes`,
  `mvn --strict-checksums`) — lockfile-based installs do not re-resolve from the
  registry, closing the live-resolution window.
- **Register package names on public registries as defensive placeholders** —
  claim the names (as empty packages owned by the organization) to prevent
  a third party from registering them, even if the packages will never be
  published there.
- **Audit transitive dependencies** with tools like `npm audit`, `pip-audit`,
  `Dependabot`, or `Snyk` — supply-chain confusion in a transitive dependency
  is identical in impact but harder to find manually.
- **Private registry with no public fallback** is the strongest structural
  control: a `npm config set registry` to an internal mirror that proxies only
  approved packages, with public fallback disabled at the network level.

## Summary

You should now be able to:

- Explain dependency confusion — exact-name collision between a private internal package and a public registry entry — and how the default version-ordering in npm, pip, and Maven allows a higher-versioned public package to win without any configuration error.
- Identify candidate private package names from build artefacts, error logs, and CI configurations, and verify whether those names are unclaimed on public registries without publishing anything.
- Explain why scope-pinning and lockfile enforcement (`npm ci`, not `npm install`) are the structural fixes, and why "we use a private registry" is not sufficient protection on its own.

---
> 🔼 Up: [[CMS & Framework Security Testing]]
