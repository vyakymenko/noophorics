# DEFECT-001 — the analysis path was never executed, and would have crashed

**Found:** 2026-07-29, ~4 hours into collection
**Status:** repaired; collection restarted
**Data on disk when found:** `sender` 34/34, `PRIOR` 34/34, `CEILING` 34/34,
`A0` 6/34, all at n=30, plus a stale `sender@claude-opus-4-8` 17/34 from the
provider comparison. No effect had been computed. No results file existed.

---

## What was wrong

`runner.py` called `_sensitivity(measure, raw_draws, ...)` — a function that was
**never defined**, with a variable `raw_draws` that **does not exist** (the
draws live in `raw`). Two `NameError`s on the same line, in the analysis block,
which runs only after the entire sweep completes.

Collection would have run for roughly thirty hours and then crashed before
writing anything.

## Why that was nearly fatal rather than merely annoying

The sample cache is written incrementally and tracked, so draws survive a
crash. The **messages do not**. They are composed at run start, held in memory,
and written only as part of the final results file. And composition runs at
`temperature = 0.7`, so re-composing does not recover them — it produces
different messages wearing the same labels.

A draw is only interpretable against the message it answered. Thirty hours of
draws with no record of which text produced them is not a damaged dataset, it
is not a dataset.

The cache made this worse rather than better. Its keys were condition labels
(`A0@gpt-oss:120b`), so a resumed run would have found a hit for `A0` and
attributed draws that answered the *old* A0 to the *new* one. It would have
reported a cache hit, produced numbers, and been wrong in a way nothing
downstream could detect.

## How it was found

Not by rereading the file. By starting to write a separate analyzer and asking
whether the results record was self-sufficient — at which point the missing
function was immediately visible.

The tests did not catch it because the test suite covers the metrics library,
and this is runner code. `--dry-run` did not catch it because `--dry-run` had
never been run *since the sensitivity call was added*. That is the whole
lesson: the call was added in the same commit that documented it, and the
documentation was checked while the code was not.

This is the third time in this repository that a change was verified by reading
rather than by running, and the second time the reading passed while the code
was broken.

## What was discarded and what was kept

| Condition | Status | Kept? |
|---|---|---|
| `sender`, `PRIOR`, `CEILING` | 34/34 each | **Kept.** Their contexts are the source spec and the empty string. They do not depend on any composed message, so re-composition cannot invalidate them. |
| `A0` | 6/34 | **Discarded.** Its draws answered a message that no longer exists. |

Cost of the restart: six probe-conditions, about twenty minutes. Cost of not
restarting: thirty hours producing an uninterpretable result.

## Repairs

1. **`sensitivity_without()` implemented.** It recomputes `d_prior`, the floor,
   the per-message table and all four effects over the measure with `M33`
   removed — not just the effects. Dropping a probe changes the denominator and
   the floor too, and reusing the full-measure values would compare effects
   computed against different bases.
2. **Analysis split from elicitation.** `derive_per_message()` and
   `compute_effects()` are pure functions over the draws. The only live calls
   left in the analysis path are the claim elicitations and the cost query, and
   both are stored in the record. Every derived number can now be recomputed
   from the committed record without contacting a model.
3. **Messages persisted immediately after composition**, to `messages.json`,
   before the sweep starts.
4. **Cache keys bound to message content.** Message conditions are keyed
   `label@model#sha256(message)[:10]`. A resumed run with re-composed messages
   now *misses* the cache instead of silently inheriting the wrong draws.
5. **Holm correction applied, not merely detected.** Separately found while
   reading the same block: the degeneracy condition set a flag and the
   p-values stayed uncorrected. The pre-registration says correction *is
   applied*. Detecting a multiplicity problem and reporting uncorrected
   p-values is worse than not detecting it, because the detection appears in
   the record as though it had been acted on.
6. **The full analysis path is now exercised by `--dry-run`** and was run before
   the restart.

## Is this an amendment?

The [amendment policy](PREREGISTRATION.md#5-amendment-policy) caps E-001b at
two, and [AMENDMENT-001](AMENDMENT-001.md) used one. This is recorded as a
defect repair rather than an amendment, on the following reasoning:

- No hypothesis, gate, threshold, sample size, cell structure, model or
  analysis specification changed. The pre-registration is untouched.
- Every repair moves the code **toward** the pre-registered plan. The M33
  sensitivity and the Holm correction were both specified and neither was
  executable. Making specified analysis executable is conformance.
- The discarded data is 6 of 1190 probe-conditions, discarded because it was
  uninterpretable, not because of anything it contained. Nothing had been
  analysed; there was no result to be steered by.

That classification is a judgment, and it is the kind of judgment an
experimenter makes in his own favour. It is recorded here in full, with the
data state at the time, so a reader who thinks this should count against the
cap has everything needed to say so. If it does count, E-001b's budget is
exhausted and any further change requires a new pre-registration under a new
ID — a consequence we accept in advance rather than argue about afterwards.

---

*This document is licensed CC BY 4.0.*
