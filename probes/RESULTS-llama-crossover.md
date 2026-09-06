# Result: no crossover, and the third model is not a subject

**Run 2026-09-06.** Sender accuracy on both domains, `n = 10`, `think` field
omitted so both models sit at their own default — the only shape both accept,
[amended into the prediction before any draw](PREDICTION-llama-crossover.md).
Scored against that prediction. Instrument data.

## The table

| model | `MERIDIAN-34` | `RIVERSIDE-30` | RIVERSIDE − MERIDIAN |
|---|---|---|---|
| `gpt-oss:120b` | **1.000** (0 wrong of 34) | **0.967** (1 of 30) | −0.033 |
| `llama3.3:70b` | **0.824** (6 wrong of 34) | **0.467** (16 of 30) | **−0.357** |

`acc(llama) − acc(gpt-oss)`: **−0.176** on MERIDIAN, **−0.500** on RIVERSIDE.

## The prediction held on both clauses, and failed on the third

Predicted: *no crossover; `acc ≥ 0.90` on both; the sign of
`acc(llama) − acc(gpt-oss)` does not flip.*

- **No crossover. Held.** The sign is negative on both domains. `llama3.3` is
  worse everywhere, not differently-better anywhere.
- **Sign does not flip. Held.**
- **`acc ≥ 0.90` on both. FAILED, badly** — 0.824 and 0.467 against E-004's
  subject gate of 0.90.

So the pre-registered third outcome fires: **`llama3.3:70b` is not a subject.**
A model that recovers 14 of 30 keys from the *full specification* has no
measurable domain prior — it is not reading the rules, and the 0.357 spread
between domains describes how differently two tasks punish a non-reader, not a
prior.

## The regime is not the explanation, and that was worth checking

`llama3.3` cannot run at `think=medium` at all, so the obvious worry was that
0.467 measures the regime rather than the model. It does not: **`gpt-oss` scores
0.967 on RIVERSIDE with the field omitted — identical to its published
`think=medium` figure.**

The reason is that omitting `think` is *not* disabling reasoning. It leaves each
model at its default, and `gpt-oss`'s default reasons. `llama3.3` has no
reasoning mode to default to. That asymmetry is the honest description of this
comparison, and it is why the table above is a **default-vs-default** measurement
rather than a matched-regime one.

## What it costs the roadmap

E-003 needed a pair whose **domain prior and general capability disagree**.
`llama3.3` cannot supply it: it is uniformly weaker, which is a capability
difference and exactly what [retraction 5](../RETRACTIONS.md) says is not worth
measuring.

**The blocker moves as the prediction said it would.** From *model selection* to
**domain selection** — the two domains here are the same task type, deterministic
application of numbered rules to boundary cases, differing in surface topic and
barely in structure. Nothing a model holds a prior *about* separates them. A
crossover needs a domain pair that does, and that is a probe measure and a month,
not a download.

## What the download is still good for

The pre-registered reading of this outcome stands: independence of lineage is
what a **rater** and a **third reader** need, and neither needs accuracy on this
task.

- **E-001c's register filter.** `blind_rating.py` requires a rater that is not
  the composer, and with two local models one of them always was. `llama3.3` is
  a third lineage and a clean rater.
- **The D-study's obstacle 3.** A rater facet with two levels has no variance to
  estimate. This is a third level.

Both of those are judgements about *text*, not applications of the rules
`llama3.3` demonstrably cannot apply. Whether that distinction survives contact
with a rating run is itself untested and should be predicted before it is.

## Limits

One measurement per model per domain. Sender accuracy is a coarse proxy for a
domain prior and this run shows it can be too coarse to mean anything at all: at
0.467 the quantity being proxied is absent. Nothing here compares to any
published `think=medium` number, by construction.

---

*This document is licensed CC BY 4.0.*
