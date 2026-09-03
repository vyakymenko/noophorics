# Prediction: does `llama3.3:70b` cross over between MERIDIAN and RIVERSIDE?

**Recorded 2026-09-03, while the weights are still downloading.** No probe has
been answered by this model. [Why this model](THIRD-MODEL.md).

## The measurement

Sender accuracy — the model given the full specification, answering every probe,
`n = 10` — on both domains this repository owns:

- `MERIDIAN-34` (34 probes), where `gpt-oss:120b` and `qwen3.5:35b` both score
  **1.000**
- `RIVERSIDE-30` (30 probes), where `gpt-oss` scores **0.967** and `qwen`
  **1.000**

640 calls. This replaces the
[`claude-opus-4-8` crossover test](riverside-30/PREDICTION-crossover.md), which
is still unrun because no Anthropic key is reachable in this shell; that
prediction stands as written and is not superseded, only overtaken.

## The prediction

**No crossover, and `llama3.3` clears the sender gate on both domains.**

Sharply, so it can be wrong in public:

- **`acc ≥ 0.90` on both**, clearing E-004's bar. If it fails this, it is not a
  subject and nothing else here applies.
- **`acc(llama) − acc(gpt-oss)` has the same sign on both domains**, or is zero
  on both. A crossover means the sign flips.
- Most likely outcome by my reading: **at or near ceiling on both**, like the two
  models already here.

## Why, so the reasoning is falsifiable and not just the conclusion

Both domains are the same *task type*: deterministic application of numbered
rules to boundary cases. `MERIDIAN` is submission handling, `RIVERSIDE` is
equipment lending — different surface topic, near-identical structure. A
crossover needs the domains to differ in something a model could hold a **prior**
about: subject matter it has seen more of, register, provenance. These two barely
differ that way.

That is the same argument the `claude-opus-4-8` prediction makes, and it is worth
noting that it is an argument about **the domains**, not about any model. If it
is right, no third model helps and the block is not "a download" — it is a probe
measure on a genuinely different subject, which is a month.

## What each outcome means, fixed now

| outcome | reading |
|---|---|
| **no crossover, both near ceiling** | E-003 stays blocked, now measured against **three** models rather than argued from two. The blocker is relocated from *model selection* to *domain selection*, and the cost of unblocking rises accordingly. |
| **crossover** — below `gpt-oss` on one domain, at or above on the other | E-003 unblocks on a pair already in hand. The most consequential outcome available, and the one I am predicting against. |
| **fails the 0.90 gate on either** | Not a subject. It can still serve as a **rater** for E-001c's register filter and as a third *reader* for the D-study, both of which need independence rather than accuracy on this task. The download is not wasted; the crossover question is. |

## What this cannot establish

Sender accuracy is a **proxy for a domain prior, and a coarse one**. A crossover
here would be grounds for registering E-003, not a result. Two domains, one task
type, one measurement each. And a model at ceiling tells you the instrument
cannot separate it from the others, which is not the same as the models being
alike — the distinction [retraction 16](../RETRACTIONS.md) was withdrawn for
missing.

---

*This document is licensed CC BY 4.0.*
