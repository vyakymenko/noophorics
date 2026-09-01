# Prediction — does `claude-opus-4-8` cross over on RIVERSIDE-30?

**Written 2026-09-01, before the run. No `claude-*` model has ever read
`RIVERSIDE-30`.** The measurement below has not been made and the API key is not
available in this shell, so this file exists first and alone, which is the order
the programme's own discipline requires and the order it has repeatedly failed
to keep.

---

## Why this measurement, and why now

[E-003 is blocked on model selection](../../journal/2026-08-28-the-good-instrument-was-sitting-unused.md),
not on the instrument. L2's sharper form needs a model pair whose **domain prior
and general capability disagree** — one model stronger overall, the other
stronger on a particular domain. Measuring only that *some* asymmetry exists is
[retraction 5](../../RETRACTIONS.md), withdrawn as tautological.

`gpt-oss:120b` and `qwen3.5:35b` cannot supply that pair: `qwen` is stronger or
level on both domains this repository owns. The journal's own conclusion was that
**"a third model is a download and a probe measure is a month."**

There is already a third model in the record, and it is the one candidate whose
profile points the right way. On `MERIDIAN-34`, `claude-opus-4-8` scores
**0.882** with four errors ([E-001b PARAMETERS](../../experiments/E-001b-fluency-factorial/PARAMETERS.md))
and **0.909** in an independent E-004 run — against **1.000** for `gpt-oss:120b`.
A frontier model measurably *weaker* on one of our domains is exactly the shape
in which a crossover could live. It has never been run on `RIVERSIDE-30`.

## The prediction

**No crossover.** `claude-opus-4-8` will score at or below `gpt-oss:120b` on
`RIVERSIDE-30` as well, and E-003 will remain blocked.

Stated sharply enough to be wrong:

- `claude-opus-4-8` sender accuracy on `RIVERSIDE-30` will be **below 1.000**,
  where both local models are at or near ceiling.
- The gap will be **in the same direction** as on `MERIDIAN-34`. Specifically,
  `acc(claude) − acc(gpt-oss)` will be **negative on both domains**.

## Why I expect that, so the reasoning can be wrong in public

Both domains are the same *task type*: deterministic application of numbered
rules with boundary cases, resolving to one of three verdicts. `MERIDIAN` is
submission handling; `RIVERSIDE` is equipment loan, temporal and sequential. A
crossover needs the two domains to differ in something a model could have a
*prior* about — subject matter, register, provenance of the text. These two
differ in surface topic and barely in structure.

So the `MERIDIAN` gap most likely reflects **capability at this task type**, not
a domain prior. If that is what it is, it transfers, and there is no crossover to
find.

## What each outcome means

- **No crossover, as predicted.** E-003 stays blocked, and the block is now
  measured against three models rather than argued from two. The cost of finding
  a crossover rises: it is not a matter of trying the models already in the
  record, and "a third model is a download" is not the whole answer, because the
  obvious third model does not help. What would then be needed is a **domain**
  whose subject matter one model has a prior about and the other does not — which
  is a probe measure, and a month.
- **Crossover.** `claude-opus-4-8` at or above `gpt-oss` on `RIVERSIDE` while
  below it on `MERIDIAN`. E-003 unblocks immediately on a pair already registered
  in this programme, and the blocker was three hundred API calls wide the whole
  time.
- **Both at ceiling.** `RIVERSIDE-30` saturates for `claude` too, and the
  measurement is uninformative about priors. Note this is *not* the same as no
  crossover: it would say the instrument cannot see the difference, not that the
  difference is absent.

## What this cannot establish

One measurement of one model on one domain. Sender accuracy is not a domain
prior; it is a proxy, and a coarse one. A crossover here would be grounds for a
registration, not a result — E-003 would still have to be written and run.

This file also does **not** read the probe items. `claude-opus-5` authored the
`MERIDIAN-IX32` probes and is recorded in [EXPOSURE.md](../../EXPOSURE.md) as
contaminated for that measure; `RIVERSIDE-30` has stayed clean for `claude-*`
and the run below must not be the thing that spoils it. The script loads the
items; the agent driving it has not seen them and will not print them.

---

*This document is licensed CC BY 4.0.*
