# The model-selection blocker and the instrument blocker are the same blocker

**Computed 2026-09-01 from run files already on disk. Zero model calls.**

[E-003 is recorded as blocked on model selection](../journal/2026-08-28-the-good-instrument-was-sitting-unused.md),
with the conclusion that this is the better of two bad positions because
*"a third model is a download and a probe measure is a month."* Read against the
measured accuracies, that conclusion does not survive as stated.

## Every sender accuracy this programme owns

| domain | `gpt-oss:120b` | `qwen3.5:35b` |
|---|---|---|
| `MERIDIAN-IX32`, 32 probes | 32/32 = **1.000** | 32/32 = **1.000** |
| `MERIDIAN-34`, 34 probes | 34/34 = **1.000** | 34/34 = **1.000** |
| `RIVERSIDE-30`, 30 probes | 29/30 = **0.967** | 30/30 = **1.000** |

Across 62 distinct probes on two domains, the two models differ on **one probe.**

## Why that is not "qwen is stronger"

It is, but the ordering is not the obstacle. **There is almost no capability
variance for a domain prior to disagree with.** L2's sharper form needs a pair
where domain prior and general capability point opposite ways; that requires both
quantities to vary. On the material this programme owns, one of them barely does.

## And qwen's ceiling closes the search further

`qwen` scores 1.000 on both domains. Nothing can beat 1.000, so **no pair
containing `qwen` can show a crossover**, whatever the third model is. Any
crossover must therefore be between `gpt-oss` and a new model, and must live in a
domain where `gpt-oss` is not already at ceiling. There is exactly one:
`RIVERSIDE-30`, where it scores 0.967.

So the third model has to satisfy both halves at once:

- **beat `gpt-oss` on `RIVERSIDE-30`** — 30/30, matching `qwen`; and
- **lose to `gpt-oss` on `MERIDIAN`** — below 32/32, where both incumbents are
  perfect.

That is: fail the domain both current models ace, and ace the domain that trips
the stronger of them. Not impossible, and not the profile a model is likely to
have by accident. **A third model is a download, but it is a download plus an
unusual profile, and nothing in the record says such a model exists.**

## What this actually says

The two blockers this programme has been treating as alternatives are one
blocker. [INSTRUMENT-LIMITS](INSTRUMENT-LIMITS.md) found the instrument too
coarse to resolve the effects the roadmap plans. This file finds that the same
domains are too *easy* to separate the models the roadmap would use. Both are the
same fact seen twice: **competent models score at or near 1.000 on the domains
this repository owns**, so there is no room either to resolve an effect or to
distinguish a reader.

A harder domain fixes both. A third model fixes neither on its own, because a
model weak enough to vary is a capability gap, and a capability gap is not what
L2's sharper form asks for.

## What would refute this

A local model measured at 30/30 on `RIVERSIDE-30` and below 32/32 on
`MERIDIAN-IX32`. That is a cheap test — 62 probes, about 620 calls — and it is
the right next measurement, because this file is an argument from two models and
an argument is not a measurement. The prediction for it should be written before
it runs, as [PREDICTION-crossover](riverside-30/PREDICTION-crossover.md) was for
the model this shell cannot reach.

---

*This document is licensed CC BY 4.0.*
