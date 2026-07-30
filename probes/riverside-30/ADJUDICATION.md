# RIVERSIDE-30 — adjudication record

**The first probe measure in this repository whose keys were ruled on by
readers who did not write them.** That requirement entered
[CONTRIBUTING](../../CONTRIBUTING.md) after `M33` — a probe written by the
person who wrote the rules, which read as obvious to its author and turned out
to be undetermined by the source text, after it had become load-bearing in an
analysis.

---

## Procedure

One agent authored the specification and 30 cases, **blind** to what the measure
would be used for. Three further agents received the specification and the cases
and **not the keys**, and for each case reported two things: their answer, and
whether the specification *determines* an answer at all. Each read under a
different instruction — strict-literal, practitioner, adversarial.

A probe was to be dropped if any adjudicator answered against the key **or**
flagged it indeterminate, even where all three happened to agree. That second
trigger is the point of asking.

## Result

**90 votes, 90 agreements with the key, 0 indeterminacy flags. All 30 ship.**

A clean sweep is also what an unused flag looks like, so the flag was checked
for life rather than assumed: all three adjudicators filed long specific defect
lists about the specification while judging that none reached an answer. One
prefaced eight defects with "none of these changed an answer above, but each is
a latent hole." The zero is a finding, not a floor effect.

## The part worth keeping: authors cannot predict their own defects

The author ranked six probes by fragility before adjudication. Three were
corroborated by an independent reader and three were not.

**T17 is the instructive case.** The author flagged it for chained computation
and wrote "no interpretive gap I can find". All three adjudicators found an
actual gap in the same rule — whether the re-shelving day moves when it falls
on a closed day — which the author had not seen. One wrote: *"T17 escapes this
only by luck (18 and 22 March are both open)."*

The author flagged the right probe **for the wrong reason** and would not have
fixed the real defect from his own analysis. That is the argument for
independent adjudication being a requirement rather than a courtesy, and it is
now measured rather than asserted.

## What this record does NOT establish

- **The adjudicators are not independent of everything.** All four agents come
  from one model family, and [E-004](../../experiments/E-004-disagreement-detector/PREREGISTRATION.md)
  includes a model of that family among its subjects. "Independent of the
  author" is what was achieved; "independent of the systems that will be
  measured on it" is not, and the two are being kept apart deliberately.
- **The local models were deliberately NOT used to adjudicate**, though they
  were available. Using E-004's own subjects to filter its probe measure would
  drop exactly the probes those models disagree on — and E-004's detector *is*
  their disagreement. The measure would have been selected to make the
  experiment find nothing, by construction. This is recorded because the
  temptation was real and the reasoning is not obvious.
- **No item difficulty was measured.** Every probe is at ceiling for this panel,
  so the author's difficulty predictions are untested.

## What it exposed in the metrics library

`RIVERSIDE-30` has **28 distinct answer spaces across 30 probes** — dates,
amounts, verdict strings — where `MERIDIAN-33` has one shared space.
`key_marginal_baseline()` pooled the keys and returned **0.098**, which is not a
chance rate but an artifact of the keys being nearly unique. The correct rate is
uniform guessing within each probe: **0.333**.

That assumption had been unstated since the function was written and was
invisible while only one measure existed. `seal()` now records each probe's
option space in the checkset, so the baseline never has to guess.

---

*This document is licensed CC BY 4.0.*
