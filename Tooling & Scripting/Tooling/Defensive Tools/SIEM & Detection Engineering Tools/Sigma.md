---
title: "Sigma"
aliases: ["sigma", "sigma rules"]
tags: [tree/tooling, cyber/tooling/defensive/sigma, type/tool, difficulty/hard]
Domain: "[[SIEM & Detection Engineering Tools]]"
Color: "#708090"
verified: 2026-09-05
---

# Sigma

> [!abstract] Note of [[SIEM & Detection Engineering Tools]]
> Sigma is the vendor-neutral detection rule format — "the YARA of logs". You write a detection once as a small YAML file describing the logic, and a converter compiles it into whichever SIEM query language you run. It decouples the *detection idea* from the *platform*, so a rule library survives a tool change.

> [!warning] Portable logic, not portable data
> A Sigma rule compiles anywhere, but it only *fires* if your logs carry the fields it references, named the way the pipeline expects. Field mapping is the real work, and it is where every failed Sigma deployment fails.

## Parent Learning Order
Splunk Basics -> Sigma

**Prerequisites:** [[Splunk Basics]] first — you need to have written a query by hand to see what Sigma is saving you from. [[Sysmon]] helps too, since most community rules assume its field names.

## The portable half of the detection pipeline

> *"Office spawned PowerShell" is the same detection idea in Splunk, Elastic and Sentinel. What is different about it in each?*
>
> Hold your answer — the section below is the response.

Sigma is the **rule**, not the platform — the portable half of the pipeline.

The insight is that a detection like "Office spawned PowerShell" is the *same idea* everywhere, but Splunk expresses it in SPL, Elastic in Lucene or ES|QL, Sentinel in its own KQL. Sigma writes the idea **once** in YAML and lets a compiler translate it for each backend, so a rule shared on GitHub can be deployed by anyone on any SIEM without a rewrite. That is the value proposition: detection logic that is not hostage to one vendor.

> [!tip] The analogy, and where it breaks
> Sigma is a recipe and the backends are kitchens: the recipe says "sear the onions", each kitchen knows how its own stove works. The analogy breaks on ingredients. A recipe assumes the kitchen *has* onions and calls them onions. Sigma assumes your SIEM holds the event and names the field the way the rule does — and unlike a cook, a compiler that cannot find the ingredient does not stop and ask. It produces a perfectly valid query for a field you do not have.

## Logsource, detection, condition — and the pipeline that is not optional

A Sigma rule is `logsource` (where) + `detection` (what) + `condition` (how they combine):

```yaml
title: Office Application Spawning PowerShell
logsource:
    product: windows
    category: process_creation
detection:
    selection:
        ParentImage|endswith: '\winword.exe'
        Image|endswith: '\powershell.exe'
    condition: selection
level: high
```

Note what `logsource` is *not*: it names an abstract category, not a log channel or an event ID. `process_creation` is a concept. Turning it into something a SIEM can actually search is the job of a **processing pipeline**, and modern `sigma-cli` will not let you skip that decision:

```shell-session
analyst@lab:~$ sigma convert -t splunk office.yml
sigma list pipelines splunk

If you never heard about processing pipelines you should get familiar with them
(https://sigmahq-pysigma.readthedocs.io/en/latest/Processing_Pipelines.html).
If you know what you're doing add --without-pipeline to your command line.
```

That refusal is the tool teaching you its central concept. Supply a pipeline and the abstract rule becomes concrete:

```shell-session
analyst@lab:~$ sigma convert -t splunk -p sysmon office.yml
EventID=1 ParentImage="*\\winword.exe" Image="*\\powershell.exe"
```

The `sysmon` pipeline resolved `category: process_creation` into `EventID=1` — and it does the same job for every other category. The identical rule body written against `network_connection` becomes `EventID=3`:

```shell-session
analyst@lab:~$ sigma convert -t splunk -p sysmon net.yml
EventID=3 DestinationIp="198.51.100.9" DestinationPort=443
```

Pipelines also rename fields, and this is where the portability stops looking like translation and starts looking like mapping. The same two rules, compiled for Elastic with the ECS pipeline:

```shell-session
analyst@lab:~$ sigma convert -t lucene -p ecs_windows office.yml
process.parent.executable.caseless:*\\winword.exe AND process.executable.caseless:*\\powershell.exe
analyst@lab:~$ sigma convert -t lucene -p ecs_windows net.yml
destination.ip:198.51.100.9 AND destination.port:443
```

`ParentImage` did not survive as `ParentImage` in different punctuation — it became `process.parent.executable.caseless`. Sigma is not translating a query between dialects; the pipeline is re-expressing the rule against a different **schema**. And a pipeline can refuse outright when the target cannot express the rule at all:

```shell-session
analyst@lab:~$ sigma convert -t splunk -p sysmon -p splunk_cim office.yml
Error: The Splunk Data Model Sigma backend supports only the following fields for
process_creation log source: CommandLine,Computer,CurrentDirectory,Image,
IntegrityLevel,OriginalFileName,ParentCommandLine,ParentImage,...
```

Pipelines chain, each with a priority, so a real deployment stacks a logsource pipeline under a schema pipeline under a site-specific one. `sigma check rule.yml` validates a rule's structure before any of that, and the public **SigmaHQ** repository ships thousands of community rules mapped to MITRE ATT&CK — which is the actual payoff: get your pipeline right once and the whole library becomes deployable.

## The field taxonomy that makes a valid rule never fire

"Write once, run anywhere" has a crucial asterisk, and it is the same asterisk the outputs above have been circling:

```text
# The rule references 'ParentImage'
# The pipeline you chose maps it to 'process.parent.executable.caseless'
# Your SIEM actually stored it as 'parent_process_path'
#   -> the compiled query is syntactically valid and matches NOTHING
```

**The deliberate break:** the rule compiles to perfectly valid SPL or Lucene, and **never fires** — because the field name in the query does not exist in your index. Sigma translates the query *and* re-maps the field names, but only as far as the pipeline you gave it knows; it cannot know how *your* ingestion normalized the data. If your Sysmon comes in through a collector that renamed fields, no stock pipeline matches, and the rule is silent forever. This is why real Sigma deployment hinges on a **processing pipeline**, often a custom one, and why log normalization is the unglamorous foundation of detection engineering. The portability is real and valuable, but it moves the hard problem from "rewrite the query" to "normalize the data" — and that problem, solved once, lights up a whole library at once.

**How you'd spot it:** a rule that compiles cleanly and returns zero results *forever* is the signature — genuinely rare behaviour returns zero sometimes, a broken field mapping returns zero always. Test by stripping the query down: if the index and sourcetype alone return events but adding one field predicate returns none, that field name does not exist in your schema. The habit that prevents it entirely is to validate against known-true data — generate the behaviour deliberately on a test host and confirm the deployed rule fires — because a detection nobody has ever seen fire is not a detection, it is a hypothesis.

## Security Implications

A rule library is a map of your blind spots. Public Sigma rules are an enormous defensive gift and a precise adversary briefing at the same time: SigmaHQ tells anyone exactly which techniques are commonly detected, in what form, and — by omission — which are not. Attackers tune against public detections, which is why mature teams keep site-specific rules unpublished and why a detection keyed on an easily-changed string (an exact tool name, a default user agent) has a much shorter useful life than one keyed on a behaviour that is hard to vary.

The `level` field is a security control, not metadata. Community rules ship with a mix of `low` through `critical`, and importing the whole repository straight to alerting is how a SOC drowns in a day — a flood of low-value alerts is functionally identical to no detection at all, and worse than none because it consumes the attention that would have caught something. Import broadly, route by level and by measured false-positive rate, and treat the tuning as the deployment.

Finally, a Sigma rule is code from the internet that becomes a query with your SIEM's privileges. Rules can carry expensive constructs — leading wildcards, broad regex, unbounded `keywords` searches — that translate into queries costing far more than the reader expects, so an unreviewed bulk import is a self-inflicted availability problem on the platform. Convert, read the generated query, and cost it before it becomes a scheduled search running every five minutes across the estate.

## Summary

You should now be able to:

- Explain the problem Sigma solves that writing SPL directly does not, and name the three parts of a rule.
- Explain what a processing pipeline does — resolve an abstract `logsource` to a concrete event ID, and re-map field names onto a target schema — and why the tool refuses to convert without one.
- Explain why a valid compiled Sigma rule can still match nothing, how to prove a rule fires, and why importing a public rule library unfiltered is its own kind of failure.

---
> 🔼 Up: [[SIEM & Detection Engineering Tools]]
