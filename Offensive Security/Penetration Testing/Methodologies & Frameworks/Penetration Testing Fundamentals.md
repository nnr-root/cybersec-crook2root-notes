---
title: "Penetration Testing Fundamentals"
aliases:
  - Pentesting Infos
  - Pentesting Fundamentals
  - What is Penetration Testing
tags:
  - tree/offensive
  - cyber/offensive/methodology
  - type/concept
  - difficulty/easy
Domain: "[[Methodologies & Frameworks]]"
Color: "#DC143C"
---

# 🎯 Penetration Testing Fundamentals

> [!warning] Authorized testing only
> Everything in this domain rests on one non-negotiable: a penetration test happens *with written permission, inside an agreed scope*. The same action is a professional service with authorization and a crime without it. That boundary is the first thing to internalize.

## Parent Learning Order
Penetration Testing Fundamentals -> Rules of Engagement & Scoping -> Penetration Testing Standards & Frameworks -> Cyber Kill Chain -> Threat Modeling & MITRE ATT&CK

## What This Whole Domain Is For

Before any tool or exploit, you need the *mental frame* of the job: what a penetration test is, how it differs from criminal hacking, what the words vulnerability / threat / risk actually mean, and what separates a professional operator from someone who just runs scanners. This note is that frame — the vocabulary and mindset every later leaf assumes. Get this right and the technical leaves make sense as *evidence-gathering toward a risk story*; skip it and you are just poking systems.

> [!tip] The analogy, and where it breaks
> A penetration test is like hiring someone to break into your own building to find the unlocked windows before a burglar does — same skills as the burglar, opposite purpose and full permission. The analogy breaks on *reporting*: a burglar wants to get in and stay hidden, whereas your value as a tester is almost entirely in what you *write down and explain* afterward — the break-in is worthless without the clear, prioritized, business-framed report that lets the owner fix the windows.

**Prerequisites:** none — this is the entry point to Offensive Security. It only assumes you understand a computer talks to other computers over a network.

## What Is Penetration Testing?

Penetration testing, or "pentesting", is an authorised security assessment that is performed on systems, applications, or networks. It is carried out with explicit permission from the system owner within agreed boundaries.

Penetration testing is important because modern systems are complex and constantly changing. These factors make it difficult for organisations to identify all weaknesses through design and development alone. Well-built systems can also contain weaknesses that could expose them to attacks. A penetration test fills this gap and helps organisations understand how these weaknesses could be abused, which allows them to prioritise fixes and reduce risk before the weaknesses can be exploited by attackers.

Penetration testing is an essential security service for many reasons. It ensures that organisations can prioritise remediation efforts based on the level of risk associated with the weaknesses. It helps protect the confidentiality of sensitive customer data such as payment information or personally identifiable information (PII), which ensures compliance with many regulatory frameworks and industry standards such as Payment Card Industry Data Security Standard ([PCI-DSS(opens in new tab)](https://www.pcisecuritystandards.org/standards/pci-dss/)) and General Data Protection Regulation ([GDPR(opens in new tab)](https://gdpr-info.eu/)). Real-world attack scenarios and assessment of the overall security posture of an organisation ensures that security controls are effective. This process provides assurance to the leadership, stakeholders, and customers that weaknesses are being addressed proactively.

## Penetration Testing vs Malicious Hacking

While penetration testers and malicious attackers may use similar tools, the way they operate is totally different. The core factors in the table below separate penetration testing from malicious hacking:

|Core Factor|Penetration Tester|Malicious Attacker|
|---|---|---|
|Authorisation|Penetration testers operate with explicit written consent from the system owner.|Attackers operate without consent and violate the rights and security of the organisation.|
|Scope|Penetration testers operate within a clearly defined scope that is set by the organisation in order to protect critical systems.|Attackers are not restricted by scope and will target anything that helps them achieve their goal.|
|Coverage|Penetration testers aim for broad coverage and assess multiple areas of a system.|Attackers focus on the quickest or most effective path to success, and often target systems and data that can provide financial benefit.|
|Responsibility|Penetration testers are accountable for their actions and the impact of their work, and are expected to act professionally at all times.|Attackers do not feel accountable for their actions and do not take responsibility for the damage that they cause.|
## Web Application Penetration Testing

Web application penetration testing focuses on finding gaps and weaknesses in a web application. Testing is commonly performed from a user perspective by interacting with the application's user interface and its APIs. The goal is to assess how the application handles user input, authentication, authorisation, sessions, and data processing. Weaknesses in web applications can have great impact on its users because web applications are usually exposed to the internet.

## Network Penetration Testing

Network penetration testing focuses on finding vulnerabilities in the underlying infrastructure that connects systems together. Testing could be performed from an external or an internal user perspective.

External network penetration testing is performed from an external user perspective with little to no access to information about the externally exposed systems. This type of assessment focuses on external-facing infrastructure such as internet-facing servers, firewalls, VPN gateways, and remote access services. The goal is to evaluate how these systems are exposed and assess the security controls that protect these systems against unauthorised users.

Internal network penetration testing, on the other hand, is an "assumed breach" scenario where a threat actor already has access to a system in the network. This type of assessment evaluates what an attacker could do next, such as moving between systems, escalating privileges, or accessing sensitive data. The goal is to assess trust relationships, access controls, and network segmentation to identify weak configurations and determine whether the security controls can limit the impact of a compromise.

Ultimately, modern web applications and networks are built with different interconnected components and systems. Identifying the attack surface helps organisations find all entry points that could contain weaknesses and provide unauthorised access to threat actors. Additionally, it helps in defining the scope of a penetration test prior to the engagement execution.

## Vulnerability

A vulnerability is a weakness or gap in an organisation's environment that could be exploited to compromise the security of systems, data, or operations. While it does not cause harm on its own, it presents an opportunity for exploitation.

Vulnerabilities come in many types. For simplicity, we will focus on technical vulnerabilities, which are weaknesses in software, systems, or configurations that can be exploited due to coding errors, insecure settings, or flawed system design.

For example, a web server running outdated software with known flaws is a vulnerability. The weakness exists, but nothing happens unless it is taken advantage of.

## Threat

A threat is anything that can exploit a vulnerability and cause harm to an organisation's environment. It represents a source of danger that can take advantage of a weakness to compromise the confidentiality, integrity, and availability of the organisation's systems.

Threats may include malicious actors such as cybercriminals, insider threats, or tools that are used to perform automated attacks. They may also be non-malicious events like system failures, human error, or environmental incidents.

For example, an attacker scanning the internet for outdated servers is a threat. They have the capability and intent to exploit the vulnerability.

More recently, attackers utilise artificial intelligence (AI) to automate attacks, discover weaknesses at scale, and accelerate exploitation. This makes AI a significant threat in modern environments due to its capacity to increase the speed and sophistication of attacks.

## Risk

Risk is the potential damage that could occur if a threat successfully exploits a vulnerability. We can determine the overall risk of a vulnerability by combining the impact and likelihood of exploitation. In some cases, a vulnerability that may look harmless could cause significant risk if it affects critical systems. In contrast, a vulnerability that may look harmful could only cause minimal risk if it exists in an isolated environment.

The following formula is commonly used to simplify the calculation of overall risk: `Vulnerability * Threat = Risk`.

This formula is a simplified model intended to illustrate the relationship between the contributing factors, rather than a formal risk calculation. A vulnerability on its own does not pose a risk if there is no threat that can leverage it. Likewise, a threat cannot cause impact if there is no vulnerability to exploit. 

Below are practical examples of how risk is calculated.

**Low Risk**

Imagine a web application displays detailed error messages when invalid input is submitted.

- **Vulnerability:** Verbose error messages revealing internal file paths
- **Threat:** Attackers triggering errors to gather system information
- **Risk:** Limited information disclosure that may help reconnaissance but does not directly compromise the system

**High Risk**

Imagine a web application that allows users to change an account ID parameter in a request and access other users’ data.

- **Vulnerability:** Broken access control allowing unauthorised access to user data
- **Threat:** Attackers modifying request parameters to retrieve or alter other sensitive user information
- **Risk:** Exposure or manipulation of sensitive customer data, leading to data privacy violations and regulatory consequences

## Risk Management

Risk management is a structured process that many organisations use to identify, evaluate, and control security risks over time. Effective risk management means understanding which risks matter most and applying appropriate controls to eliminate or reduce their impact or likelihood of exploitation.

Risk management is typically an ongoing cycle consisting of four stages:

- **Identification**: Identifying assets, vulnerabilities, and potential threats that could affect the organisation.
- **Analysis**: Evaluating risks to determine the potential impact and likelihood of exploitation, which translates to the severity of each risk and helps plan remediation efforts.
- **Mitigation**: Reducing or controlling identified risks. This may include applying security patches, strengthening access controls, improving configurations, implementing monitoring tools, or redesigning insecure processes.
- **Monitoring**: Continuous monitoring of risks to ensure that controls remain effective, new vulnerabilities are detected, and emerging threats are addressed promptly.

In some cases, organisations may choose to accept or transfer risk if mitigation is not practical or cost-effective. Accepting a risk is usually chosen if the impact is minimal and the cost of reducing the risk outweighs the benefit. Transferring risk means shifting the responsibility to a third party, such as purchasing an insurance policy that would cover the cost that comes with the risk.

An example where a company would accept the risk is if they discover that their internal web application displays the server version in the server header. The company decides to accept the risk because the version is up to date, the web application is only exposed internally, and it does not contain sensitive data. However, mitigating the risk is costly and requires time and resources.

In contrast, an example where a company would transfer the risk is if they operate an online platform that stores personal and payment information of their customers. The company decides to transfer the risk by purchasing a cyber insurance policy to cover the financial cost if a data breach occurs, because even though security controls are in place and effective, the risk cannot be fully removed.
## Common Causes and Resulting Vulnerabilities

The table below maps each common cause to a resulting vulnerability that an attacker could exploit.

| Root Cause                 | Example Scenario                                                                                  | Resulting Vulnerability                                                                                 |
| -------------------------- | ------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------- |
| Human Assumptions          | Developer assumes users only upload images to a profile photo field, no validation is in place.   | Unrestricted file upload: An attacker uploads a web shell and executes OScommands on the server.        |
| Software Bugs              | Form data is concatenated into a database query rather than handled through parameterised inputs. | SQL injection: An attacker crafts input to extract or modify sensitive records from the database.       |
| System Complexity          | Multiple integrated services make it easy to overlook a misconfigured APIendpoint.                | Exposed admin API: An attacker reaches admin functions that were never meant to be publicly accessible. |
| Over-Customisation         | Custom authentication replaces a standard framework with logic that is hard to maintain.          | Weak authentication: Outdated hashing and broken session logic expose user accounts to takeover.        |
| Technical and Design Flaws | Authenticated session is issued before the MFA step is completed.                                 | MFA bypass: An attacker navigates to authenticated pages without completing the MFA process.            |
## Good vs Bad Mindset During a Penetration Test

In order to produce meaningful results from a penetration test, it is critical to have a methodical and structured approach. In addition, the ability to adapt to changing environments is essential for maintaining quality throughout different assessments. Having a strong foundation and process not only helps achieve comprehensive coverage but also ensures that overall risk is properly assessed.

A good mindset when performing penetration tests includes several qualities. The following examples highlight characteristics that expand on these qualities:

- **Understanding the system**: In most cases, systems behave differently from one another. Having a strong understanding of how the target operates will help testers plan ahead and gain the context to explore potential exploitation opportunities.
- **Attention to detail**: Observing how the application behaves and noticing small differences in certain scenarios often results in impactful findings.
- **Constant curiosity**: Constantly asking "What if?" type of questions helps uncover many ideas that can be explored and open further opportunities to identify weaknesses.
- **Prioritising critical areas**: Focusing on high-impact functions before lower-risk features ensures that effort is directed towards areas where security issues would cause greater business impact.
- **Thinking in context**: Understanding how a feature is used and what data it handles helps assess risk more accurately and allows findings to be evaluated based on real-world consequences rather than technical severity alone.
- **Creative thinking**: Hardened systems usually create an assumption that weaknesses may not exist. Approaching these systems with creativity allows a tester to identify weaknesses that could otherwise be overlooked. This approach may involve linking two vulnerabilities in order to achieve greater impact.

A poor mindset when performing penetration tests can reduce the quality of an assessment and lead to missed or inaccurate findings. The following examples highlight characteristics that could result in unreliable testing:

- **Rushing to exploitation:** Attacking a system without understanding how it works often leads to overlooked weaknesses. Additionally, this approach can increase the risk of disrupting systems, which could lead to limitations in testing.
- **Ignoring context:** Focusing only on technical success without considering business impact could result in findings that are lacking real-world relevance.
- **Over-reliance on tools:** Depending too much on automated tools without proper analysis may produce false positives or miss logic-based issues that require manual testing.
- **Making assumptions:** Assuming how a system or functionality works without verification may cause testers to overlook important behaviours.
- **Tunnel vision:** It is easy to become fixated on one functionality, especially if a tester thinks that it will lead to a critical finding. This behaviour typically leads to time wasted, which can reduce coverage and prevent exploration of other areas that may contain more significant weaknesses.
- **Blindly following a checklist**: While having a comprehensive checklist is useful in ensuring full coverage, depending on it too much could reduce a tester's ability to think creatively and lead to missed opportunities for more significant findings. Additionally, it could create an assumption that testing is finished once the checklist is completed.

The table below summarises the contrast between effective and ineffective mindsets during a penetration test.

| Effective Mindset                                                      | Ineffective Mindset                                                     |
| ---------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Understand the system: Study how the target operates before testing    | Rushing to exploitation: Attacking without understanding the system     |
| Attention to detail: Notice subtle behavioural differences             | Ignoring context: Reporting findings without business relevance         |
| Constant curiosity: Ask "what if?" to uncover new opportunities        | Over-reliance on tools: Missing logic flaws that require manual testing |
| Prioritise critical areas: Focus effort on high-impact functions first | Making assumptions: Guessing system behaviour without verification      |
| Think in context: Assess risk by real-world consequence                | Tunnel vision: Fixating on one area at the cost of coverage             |
| Creative thinking: Chain vulnerabilities for greater impact            | Blindly following a checklist: Missing deeper issues outside the list   |
## Common Best Practices During a Penetration Test

Applying best practices throughout a penetration test helps maintain consistency and improve the overall quality of the engagement. The following examples highlight common habits that strengthen the testing process and the value of the final results:

**Maintaining Good Notes**

Keeping detailed notes throughout a penetration test helps a tester track their activity, findings, and observations as the assessment progresses. Good notes make it easier to reproduce issues later if required, and ensure that nothing important is forgotten.

For instance, if a vulnerability is discovered early in the assessment, having detailed notes allows the tester to revisit it later without repeating the entire process.

**Collecting Evidence**

Similar to maintaining good notes, collecting evidence such as screenshots, tool output, or logs supports the validity of findings and provides clear proof of impact. Collecting evidence while testing helps save time by avoiding unnecessary reproduction of issues during reporting, which could take a considerable amount of time.

**Managing Time**

Penetration tests are performed within fixed timelines. Managing time effectively allows a tester to balance effort across different areas and ensure that sufficient time is spent on critical functions and reporting. Instead of spending hours on a low-impact feature, it is better to prioritise authentication or access control functionalities where security failures would have a greater impact.

Additionally, working on the report as you go is a good habit that significantly helps in managing time effectively. Oftentimes, reporting effort is included in the timeline and ensuring that it is performed within the timeline is crucial in preventing burnout and ensuring that deliverables are submitted in a timely manner. One scenario where reporting as you go becomes useful is when a critical risk finding is discovered towards the end of an engagement. Documenting new findings alongside existing ones and collecting evidence can be time consuming. This could create unnecessary pressure, especially when the engagement is about to conclude.

**Proactive Communication**

Maintaining proactive communication during a penetration test helps keep the engagement on track by providing regular progress updates and highlighting blockers early. Communicating roadblocks allows issues to be addressed as soon as possible. While no engagement is perfect, proactive communication ensures that effort can be redirected when needed, support can be provided, and the overall impact on coverage can be reduced.

**Staying Professional**

Professional behaviour throughout the penetration testing lifecycle builds trust between the tester and the organisation that is being assessed. Respecting scope boundaries, handling sensitive data responsibly, and conducting testing in a controlled manner are some of the essential habits that maintain professionalism.

Professionalism also applies when it comes to communicating a finding to stakeholders. Explaining a finding's business impact rather than just the technical details helps stakeholders understand its significance. It also reinforces the tester's credibility and reliability.

## Putting the Vocabulary Together

```mermaid
flowchart LR
    V["Vulnerability<br/>(a weakness)"] -->|"exploited by"| T["Threat<br/>(actor + capability + intent)"]
    T --> R["Risk = impact x likelihood"]
    R --> D{"Decision"}
    D -->|"mitigate"| M["Patch / control"]
    D -->|"accept"| A["Document & monitor"]
    D -->|"transfer"| I["Insurance / 3rd party"]
    M --> RM["Risk management cycle:<br/>identify -> analyse -> mitigate -> monitor"]
    A --> RM
    I --> RM
```

A vulnerability alone is not risk; a threat alone is not risk. **Risk is what happens when a threat can reach a vulnerability, weighted by business impact** — and the organization then *decides* what to do with each risk. Your report's job is to make those decisions well-informed.

## Worked Mapping: A Finding Driven to a Risk Decision

The reasoning this domain builds toward is turning a technical fact into a business
decision a stakeholder can own. Here that reasoning is carried out in full for two
findings — one that must be fixed and one that may rationally be accepted — as the
worked artifact a report contains.

| Step | High-risk finding | Low-risk finding |
|:--|:--|:--|
| Vulnerability | `/api/invoice/{id}` returns any invoice without checking ownership | The server response includes a precise version banner |
| Threat | Any authenticated low-privilege user changes `{id}` | An attacker fingerprints the version to look up known CVEs |
| Impact | Exposure of all customers' financial data → regulatory + reputational | Marginal — speeds recon slightly; no direct access |
| Likelihood | Trivial — no special access, just increment the ID | Low value — banner alone grants nothing |
| **Risk** | **High** (high impact × high likelihood) | **Low** (low impact × low leverage) |
| Decision | **Mitigate** — enforce object-level authorization server-side | **Accept** — patch on the normal cycle; note in the report |
| Retest | Request another user's invoice ID → expect `403`; own invoice still `200` | None required — informational |

The two rows exist to make one point: a risk rating is a defensible argument, not a
scanner's label. The high finding is high because impact and likelihood are both high,
and the recommendation is to enforce authorization server-side rather than hide the ID
— because hiding the identifier addresses neither the impact nor the likelihood. The
banner is low because, argued honestly to a skeptical stakeholder, it grants an
attacker nothing on its own; an organisation can rationally accept it and spend the
remediation budget on the invoice endpoint instead.

The mastery signal the note names is exactly this: being able to defend both the rating
*and* the decision — including the decision to accept — to someone who will be
accountable for it. A finding that cannot be driven to a decision a stakeholder can
own is not yet a finding; it is a bug report.

## Summary

You should now be able to:

- Define penetration testing, state why authorization+scope is what separates it from crime, and correctly use the words vulnerability, threat, and risk.
- Take a raw finding and turn it into a defensible risk story (impact × likelihood) with a concrete remediation and retest, and distinguish web vs network testing scope.
- Explain the risk-management cycle and when accept/transfer beats mitigate, articulate the good-vs-bad tester mindset, and justify why the report — not the exploit — is the deliverable.

---
> 🔼 Up: [[Methodologies & Frameworks]]
