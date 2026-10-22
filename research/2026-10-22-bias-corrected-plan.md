# Bias-corrected divergences: a follow-up plan, committed before its code

**2026-10-22 · prospective plan for an offline simulation, not an experiment.**
No model is called and no repository data is read. Committed before the code
exists and before any result does. The predictions below stay as written
whatever the run finds.

## Why this, now

The [vanishing-gap results](2026-10-16-vanishing-gap-results.md) left one thread
pointing somewhere specific. Near a vanishing gap, the Fieller set for `F*`
widened without bound and held its coverage. At the widest gap it lost coverage,
by about what a set of the right width around a *biased* ratio predicts
(Table 4 there). The gap's own interval failed everywhere, and at a true gap of
zero it lay wholly above zero in 84–96% of trials. Every failure sat on a
plug-in divergence. The report said that was a direction, not a tested cause.
This plan tests it: if the divergence estimates are corrected for their
small-sample bias, do the failures go away?

## The estimators

Jensen–Shannon divergence is `H(m) − ½[H(p) + H(q)]`, `m = (p + q)/2`. With equal
answer counts `n` per party, the plug-in estimate uses the empirical
frequencies, and `m̂` is the pooled frequency over `2n` answers. Three versions of
the per-probe divergence are compared, all in bits:

| estimator | per-probe divergence |
|---|---|
| **plug-in** | as now, `jensen_shannon` on empirical frequencies |
| **Miller–Madow** | each entropy plug-in plus `(k̂ − 1)/(2N ln 2)`, `k̂` the number of options seen, `N` its sample size (`n`, `n`, `2n`) |
| **jackknife** | the two-sample delete-one jackknife of the plug-in divergence: `θ̂ − (n−1)(θ̄₋ₐ − θ̂) − (n−1)(θ̄₋ᵦ − θ̂)`, `θ̄₋ₐ` the mean of the estimate with one of party A's answers left out |

The Miller–Madow form and the one-sample jackknife are as Paninski (2003)
states them for entropy, read in full for this plan; the two-sample jackknife
applies the same delete-one correction to each party's sample. Neither
corrected divergence is clamped at zero, so either can be negative.

With a corrected divergence the null bias that the permutation floor removes is
already, to first order, removed. So the corrected reports use **no floor**:
`M̂ = D̂_prior − D̂_post`, `Ĝ = D̂_prior`, `F̂ = M̂/Ĝ`. V0 and V2 of the previous
plan are carried alongside, from the same draws.

## Design, unchanged from the previous plan

Same harness, generator, 52 cells (`n ∈ {10, 16}`, `g ∈ {0, .6, .8, .9, .95, .98}`,
`λ ∈ {.25, .5, .75, 1}`, and the four zero-gap cells), 400 trials, 400
draw-level bootstrap replicates, `z = 1.96`, and **the same per-trial seeds,
drawn in the same order**. Reports per estimator: the Fieller set for `M̂/Ĝ`
from the bootstrap covariance; the percentile interval of the movement; the
percentile and basic intervals of the gap; the ratio's bias among trials with
`Ĝ > ε = 0.02`, as before; and `Ĝ`'s mean error against the true gap.

**A built-in check:** because the seeds and draw order are the same, the V0 and
V2 numbers this run produces must equal those in
[`vanishing-gap.json`](vanishing-gap.json) exactly. If they do not, the run is
not the comparison it claims to be, and no result below is read.

## Predictions, recorded before any code runs

- **B1.** The jackknife's `Ĝ` has a smaller absolute mean error against the true
  gap than V2's `Ĝ` in at least **40 of the 48** grid cells.
- **B2.** The jackknife Fieller set covers the true `F*` in at least **0.93** of
  trials in **every** grid cell. This is the claim that matters, and I hold it
  only moderately: Paninski (2003) warns that bias survives correction in
  undersampled regimes, and that standard intervals understate the error there.
  Three options and 10–16 answers is not deeply undersampled, but `n = 10` is
  close enough to matter.
- **B3.** The jackknife gap's percentile interval covers the true gap in at least
  **0.90** of trials in every grid cell, and in the two zero-gap null cells lies
  wholly above zero in at most **0.10**.
- **B4.** For every `(n, λ)`, the share of jackknife Fieller sets that are bounded
  is below one half at `g = 0.98`. The correction must not buy coverage by
  giving up the widening that made the set the right answer near zero.
- **No prediction** is registered for Miller–Madow. It is reported beside the
  jackknife, in full.

## What would change what

If B2 and B3 hold, the output is a **proposal** for the repository owner: report
`F*` from jackknife-corrected divergences as a Fieller set, beside the movement
and the gap with their intervals, with the point estimate as a summary. Nothing
in `metrics/noophorics/` changes on the strength of a simulation, and no
published result is recomputed. If either fails, the report says which and by
how much, and Problem 12 stays as open as it is.

## Limits stated in advance

- Everything in the previous plan's limits: synthetic agents, three options,
  independent draws, one generator, a fixed frame.
- Corrections derived for entropy are applied to a difference of entropies;
  their errors need not cancel.
- The jackknife variance is larger than the plug-in's. Coverage bought with
  width is reported with the width.

## Exposure

Drafted by `claude-opus-5-5`, which wrote the previous plan, its simulation and
its report, and read Paninski (2003) for this one. It is the author of the
predictions it will score. See [EXPOSURE.md](../EXPOSURE.md).

**Reference.** Paninski, L. (2003). Estimation of entropy and mutual information.
*Neural Computation*, 15(6), 1191–1253. doi:10.1162/089976603321780272.

---

*This document is licensed CC BY 4.0.*
