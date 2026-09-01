---
title: "Sigma"
aliases: ["sigma", "sigma rules"]
tags: [tree/tooling, cyber/tooling/defensive/sigma, type/tool, difficulty/hard]
Domain: "[[SIEM & Detection Engineering Tools]]"
Color: "#708090"
---

# Sigma

Sigma is the **vendor-neutral detection rule format** — "the YARA of logs, the GitHub of detections." You write a detection once as a small YAML file describing the logic, and a converter (`pySigma`/`sigmac`) compiles it into whichever SIEM query language you run: Splunk SPL, Elastic KQL, Microsoft Sentinel KQL, and dozens more. It decouples the *detection idea* from the *platform*, so detection engineering survives a tool change.

> [!warning] Portable logic, not portable data
> A Sigma rule compiles anywhere, but it only *fires* if your logs carry the fields it references. Field mapping is the real work.

## Parent Learning Order
Splunk Basics -> Sigma

## The portable half of the detection pipeline

> *"Office spawned PowerShell" is the same detection idea in Splunk, Elastic and Sentinel. What is different about it in each?*
>
> Hold your answer — the section below is the response.

Sigma is the **rule**, not the platform — the portable half of the pipeline.

The insight: a detection like "Office spawned PowerShell" is the *same idea* everywhere, but Splunk expresses it in SPL, Elastic in KQL, Sentinel in its own KQL. Sigma writes the idea **once** in YAML and lets a compiler translate it to each backend — so a rule shared on GitHub can be deployed by anyone, on any SIEM, without a rewrite. That's the whole value proposition: detection logic that isn't hostage to one vendor.

## Logsource, detection, condition, then compile

A Sigma rule is `logsource` (where) + `detection` (what) + `condition` (how they combine):

```yaml
title: Office Application Spawning PowerShell
logsource: { product: windows, category: process_creation }
detection:
  selection:
    ParentImage|endswith: '\winword.exe'
    Image|endswith: '\powershell.exe'
  condition: selection
level: high
```

Compile it to your backend:

```shell-session
analyst@lab:~$ sigma convert -t splunk office_spawns_powershell.yml
ParentImage="*\\winword.exe" Image="*\\powershell.exe"
analyst@lab:~$ sigma convert -t elasticsearch office_spawns_powershell.yml
ParentImage:*\\winword.exe AND Image:*\\powershell.exe
```

One YAML, two backends, identical logic. The public **SigmaHQ** repo ships thousands of community rules mapped to MITRE ATT&CK.

## The field taxonomy that makes a valid rule never fire

"Write once, run anywhere" has a crucial asterisk — the **field taxonomy**:

```shell-session
# The rule references 'ParentImage' (Sysmon's field name)
analyst@lab:~$ sigma convert -t splunk office_spawns_powershell.yml
ParentImage="*\\winword.exe" ...
# But this SIEM ingests the same event with the field named 'parent_process_path'
#   → the compiled query is syntactically valid but matches NOTHING
```

**The deliberate break:** the Sigma rule compiles to perfectly valid SPL, yet it **never fires** — because your SIEM stored the parent-process field as `parent_process_path`, not `ParentImage`. Sigma translates the *query syntax* across vendors, but it cannot know how *your* logs are named or normalized; if the field names don't line up, the rule is silent. This is why real Sigma deployment hinges on a **pipeline/field-mapping** (pySigma "processing pipelines") that maps the rule's canonical field names onto your actual log schema — and why log normalization is the unglamorous foundation of detection engineering. The portability is real and valuable, but it moves the hard problem from "rewrite the query" to "normalize the data" — solve that once and a whole library of community detections lights up at once.

**How you'd spot it:** a rule that compiles cleanly and returns zero results *forever* is the signature — genuinely rare behaviour returns zero sometimes, a broken field mapping returns zero always. Test by stripping the condition down: if `index` and `sourcetype` alone return events but adding one field predicate returns none, that field name does not exist in your schema.

## Summary

You should now be able to:

- Explain the problem Sigma solves that writing SPL directly does not.
- Name the three parts of a Sigma rule, and how you turn one into a Splunk query.
- Explain why a valid compiled Sigma rule can still match nothing, and what makes it actually fire.

---
> 🔼 Up: [[SIEM & Detection Engineering Tools]]
