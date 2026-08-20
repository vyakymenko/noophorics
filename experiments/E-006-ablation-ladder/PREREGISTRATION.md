# E-006 — Is `F*(C)` concave? The ablation ladder for L1

**Pre-registered 2026-08-20, before any data exists.** No `results/` directory,
no draws, nothing on disk from this experiment when this file is committed.

## 1. What is being tested, and what is not

[L1](../../theory/laws.md#l1): *"`F*(C)` is concave in message cost and saturates
strictly below 1."*

**This experiment tests the concavity limb only.** The saturation limb is out of
scope, and not because it is hard — because it is not testable on this material.
[Retraction 1](../../RETRACTIONS.md) records a 113-token lookup table reaching
`F* = 1`, after which A3 was restated for **held-out** probes under bounded cost.
`MERIDIAN-IX32`'s probes are derived from the MERIDIAN specification, so a
message that *is* the specification closes the gap by construction. Any ladder
whose top rung is the source will report `F* = 1` at the top and will have
measured its own construction.

L1's own text licenses the split: *"L1 is about the shape of `K(C)` — concave,
saturating below 1 — and concavity in cost is a property of the curve, not of
what it is measured toward. The saturation level does depend on `R`."*

**Declared, so it cannot be read the other way later:** the top rung of this
ladder is the full specification and **will** score `F* = 1.0`. That is an anchor,
not a finding, and it is not evidence against L1's saturation limb.

## 2. Why this is not E-002c's ladder

E-002c ran four cost rungs and its per-brief fidelities look like an `F*(C)`
curve. They are not one: its briefs were **composed independently per rung**, so
the object is a between-message gradient in which content varies with cost.
E-002c's own findings said so before anyone tried to use it otherwise. This
experiment truncates **one** message, so cost is the only thing that varies.

It also runs after [DEFECT-001](../E-002c-calibration-slope/DEFECT-001.md): every
fidelity here is computed by `fidelity_from_draws`, which takes draws rather than
floats and puts the floor on the pair it corrects.

## 3. Design

| | |
|---|---|
| message | the MERIDIAN source specification, 479 words, truncated |
| rungs | 8, at 12.5% … 100% of the specification's **words**, cumulative from the start |
| probe measure | `MERIDIAN-IX32@f058de0f906e`, 32 probes |
| model | `gpt-oss:120b`, `think=medium`, `temperature=0.7` |
| draws | `n = 10` per probe per party |
| parties | `PRIOR` (empty context) + 8 rungs; **sender reused** from `gate-run5.json`, same model, measure and `n` |
| `F*` | `fidelity_from_draws(sender, PRIOR, rung, floor_on="post")` |
| cost | receiver's tokenizer, recorded per rung |

Truncation is by word count from the start of the document, so rung `k` is a
strict prefix of rung `k+1`. Prefixes cut mid-sentence; that is what an ablation
is, and the alternative — truncating at section boundaries — would make cost
confounded with which sections survive.

Calls: `9 × 32 × 10 = 2 880`. At the measured `5.8 s/call` for this model,
**≈ 4.6 hours**.

## 4. Hypothesis and decision rule, fixed now

**H1 (primary).** Fitting `F* = a₀ + a₁C + a₂C²` over the 8 rungs, **`a₂ < 0`**.

Decision by interval, not by p-value: bootstrap over the **32 probes** — resample
probes with replacement, recompute `F*` at every rung from the same draws, refit,
and take the 95% percentile interval of `a₂`.

- interval entirely below 0 → **concave**, L1's shape supported on this material
- interval entirely above 0 → **convex**, against L1
- interval spanning 0 → **undetermined**, and reported as undetermined

The bootstrap resamples probes and not rungs, because rungs are the design and
probes are the sample.

**H2 (secondary, descriptive).** `F*` is non-decreasing across rungs. L1 does not
require monotonicity and no verdict rests on this; it is recorded because a
non-monotone ladder would indicate the truncation is destroying structure rather
than removing it.

## 5. Power, computed before the run rather than after

The obvious failure of this design is finding "no concavity" with a design that
could not have found concavity. E-002c's ladder was underpowered for exactly this
and nobody checked.

**To be computed and committed before collection, in `POWER.md`:** simulate a
genuinely concave curve saturating at plausible `K`, sample at these 8 costs with
the per-rung variance observed in E-002c's ladder, refit, and report the fraction
of simulations whose bootstrap interval falls entirely below 0.

**If that fraction is below 0.80, this experiment does not run as designed.**
Either the rung count rises or the hypothesis is withdrawn before any draw. A
design that cannot detect its own effect is not evidence of absence, which is
what [retraction 16](../../RETRACTIONS.md) was withdrawn for.

## 6. Gates

| gate | threshold | when |
|---|---|---|
| admissibility | `d_prior − d_floor > 0.02` at every rung | per rung |
| outcome variation | ≥ 3 rungs with distinct diverged counts | after collection |
| sender reuse | model, measure and `n` must match, enforced by the runner | at start |
| power | ≥ 0.80 in §5 | **before** collection |

**Void if:** admissibility fails at more than two rungs, or the power gate fails.

## 7. What this cannot establish

- Nothing about the **saturation level**, per §1.
- Nothing about **any other reader**. One model in both roles is one self-pair.
  Today's finding that the wobble/divergence association holds for `gpt-oss` and
  is untestable on `qwen` applies here too: a curve shape measured on one reader
  is that reader's curve until a second one is run.
- Nothing about **other messages**. One specification, one truncation path.
- The probes are ~9 prompt templates, not 32 independent rows
  ([retraction 15](../../RETRACTIONS.md)). The probe bootstrap in §4 inherits
  that: it resamples 32 correlated rows and its interval is correspondingly
  optimistic. Stated here so it is not discovered afterwards.

---

*This document is licensed CC BY 4.0.*
