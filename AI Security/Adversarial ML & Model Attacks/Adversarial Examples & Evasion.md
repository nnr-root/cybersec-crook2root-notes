---
title: Adversarial Examples & Evasion
aliases:
  - Adversarial ML
  - FGSM
  - Adversarial Patches
tags:
  - tree/ai
  - cyber/content
  - difficulty/practitioner
Domain:
  - "[[Adversarial ML & Model Attacks]]"
Color: "#F032E6"
---

# Adversarial Examples & Evasion

> [!abstract] One sentence
> Adversarial examples are inputs engineered to cause a machine-learning model to misclassify — small, often imperceptible perturbations that expose the gap between a model's decision boundary and human perception.

**Before you read:** A Meridian Freight access-control system uses a ResNet-50 image classifier to verify employee badge photos at the door. You have white-box access to the model weights (stolen from the vendor's update package). Without physically forging a badge, can you craft an image that the camera would classify as an authorised employee? Hold your answer.

## Parent Learning Order
[[Adversarial ML & Model Attacks]] → **Adversarial Examples & Evasion** → [[Model Extraction & Inversion]]

---

## Why Models Are Vulnerable

Neural networks learn high-dimensional statistical patterns, not the semantic features humans use. Their decision boundaries are linear in many local directions — small steps along those directions cross the boundary without visibly changing the input.

```
Human sees:  a cat
Model sees:  a vector of 224×224×3 float values → latent space → logits → softmax

Adversarial perturbation: δ chosen so that (input + δ) maps to "dog" logit > "cat" logit
Constraint:  ||δ||∞ < ε (e.g. ε=8/255 — invisible to human eye at 8-bit colour depth)
```

---

## Attack Taxonomy

### White-Box Attacks (Gradient Access)

**FGSM — Fast Gradient Sign Method** (Goodfellow et al., 2014)

The simplest adversarial attack: take one step in the direction that maximises loss.

```python
import torch, torch.nn.functional as F

def fgsm(model, x, y_true, epsilon=8/255):
    x_adv = x.clone().requires_grad_(True)
    loss = F.cross_entropy(model(x_adv), y_true)
    loss.backward()
    # Step in the sign of the gradient (maximises loss)
    perturbation = epsilon * x_adv.grad.sign()
    return torch.clamp(x + perturbation, 0, 1)

x_adv = fgsm(model, badge_tensor, label_authorised, epsilon=8/255)
pred = model(x_adv).argmax()
# pred → 'employee_7' (authorised) despite x_adv looking identical to the attacker's photo
```

**PGD — Projected Gradient Descent** (Madry et al., 2018)

FGSM iterated: take many small steps and project back to the ε-ball after each. Stronger but slower.

```python
def pgd(model, x, y_true, epsilon=8/255, alpha=2/255, steps=40):
    x_adv = x.clone()
    for _ in range(steps):
        x_adv.requires_grad_(True)
        loss = F.cross_entropy(model(x_adv), y_true)
        loss.backward()
        x_adv = x_adv.detach() + alpha * x_adv.grad.sign()
        # Project onto ε-ball around original input
        x_adv = torch.clamp(x_adv, x - epsilon, x + epsilon).clamp(0, 1)
    return x_adv
```

> [!tip] The analogy, and where it breaks
> FGSM is like a one-shot lockpick attempt; PGD is a patient safe-cracker making many tiny turns. Both need the lock's blueprint (gradient access).
>
> **The deliberate break:** white-box attacks require model weights — typically unavailable to external attackers. But adversarial examples often **transfer**: a perturbation computed against model A fools model B at non-trivial rates, enabling black-box attacks.

---

### Black-Box Attacks (No Gradient Access)

**Transfer Attack:** generate on a locally trained substitute model, apply to target.

**Score-Based Attack (Zeroth-Order Optimisation):** query the model for class probabilities, estimate gradient from output differences, iterate.

```python
# Simplified NES (Natural Evolution Strategy) query attack
# Query model with small random perturbations, estimate gradient from score changes
for step in range(500):
    noise = torch.randn_like(x) * sigma
    pos_score = model(x + noise).softmax(1)[0, target_class]
    neg_score = model(x - noise).softmax(1)[0, target_class]
    grad_estimate = (pos_score - neg_score) * noise / (2 * sigma)
    x_adv = x_adv + alpha * grad_estimate.sign()
# Each iteration = 2 model queries; 500 iterations = 1000 queries
```

**Decision-Based Attack:** works with only the final label — no probabilities needed. Queries: ~10,000+ to cross the boundary.

---

## Physical-World Attacks

Adversarial perturbations can be printed and placed in the real world.

| Attack | Method | Real demo |
|---|---|---|
| Adversarial patch | Bright printable patch in frame corner fools classifier regardless of main subject | Evades YOLO object detector; person classified as "toaster" |
| Adversarial glasses | Printed eyeglass frames fool face recognition | LFW benchmark: attack success >80% |
| Stop sign sticker | Precisely placed sticker causes "Speed Limit 45" classification | University of Washington (2017) physical attack |
| Adversarial T-shirt | Printed pattern causes person to be invisible to person-detector | Evaded YOLOv2 in lab conditions |

**Meridian Freight physical-world scenario:** A printed adversarial patch affixed to the edge of an employee badge photo could cause the ResNet-50 access-control classifier to predict a different (authorised) employee identity, bypassing the physical gate — without any digital access to the camera feed.

---

## Defences and Their Limits

| Defence | Mechanism | Failure mode |
|---|---|---|
| Adversarial training | Augment training set with PGD examples at each batch | Expensive; defends against the attack type seen in training; adaptive attacks bypass |
| Randomised smoothing | Add Gaussian noise at inference; certify radius around clean input | Certified radius is often smaller than practical attack perturbation |
| Feature squeezing | Reduce colour depth / apply median filter before inference | PGD + EOT (Expectation Over Transformation) breaks spatial defences |
| Input purification | Run input through a denoiser before classification | Adaptive adversary optimises through the denoiser |
| Ensemble voting | Multiple diverse models vote; attacker must fool all | Transferability across architectures partially breaks this |
| Certified defences | Convex-hull relaxation proofs (IBP, CROWN) | Provable only within tiny ε; compute scales poorly to large networks |

**No current defence is both efficient and certifiably robust at practical perturbation radii.** For high-stakes physical deployments, the correct control is liveness detection, multi-factor authentication, and human oversight — not adversarial-robustified classifiers alone.

---

## Security Implications

- **Evasion in deployment:** spam filters, malware classifiers, and network IDS models trained on ML are adversarially evadable in principle; black-box attacks require only repeated API access.
- **Physical security:** access control and surveillance systems using image classifiers face real-world adversarial patch attacks that do not require any digital access to the camera feed or model.
- **Responsible disclosure:** adversarial ML vulnerabilities in production systems should follow the same coordinated disclosure path as traditional CVEs — the attack surface is real and exploitable.

---

## Summary

- Adversarial examples exploit the gap between model decision boundaries and human perception; white-box attacks (FGSM, PGD) use gradients directly while black-box attacks use query feedback or transferability.
- Physical-world attacks — printed patches, glasses frames, T-shirt patterns — show that the threat is not limited to digital pipelines; camera-based access control systems in the real world are a viable target.
- No defence is both practical and certifiably robust at useful perturbation sizes; defence-in-depth (liveness detection, MFA, human oversight) is the correct posture for high-stakes deployments.

---
> 🔼 Up: [[Adversarial ML & Model Attacks]]
