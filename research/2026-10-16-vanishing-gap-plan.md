# The vanishing denominator: a simulation plan, committed before the code

**2026-10-16 · prospective plan for an offline simulation, not an experiment.**
No model is called and no repository data is read. This plan is committed
before the simulation code exists and before any result does; what it predicts
below is recorded so it can be scored, and a prediction that fails stays here as
written. Problem 12 is not claimed solved by anything this plan can produce.

## The question, from Problem 12

[Problem 12](../theory/open-problems.md#12-the-vanishing-denominator) wants two
things:

1. an estimator that *degrades continuously* as the gap `D_prior − D_floor`
   shrinks, rather than one that is fine until it is undefined; and
2. a principled account of what to report when the parties already agree — in
   particular a way to express an antinoophor on a zero-gap measure.

Today `F*` is reported as a point, `min(1, M/G)` with `M = D_prior − D_post` and
`G = D_prior − D_floor`, and it is refused when `G ≤ ε = 0.02`
([`fidelity.py`](../metrics/noophorics/fidelity.py)). No interval exists for a
single `F*`.

## Why the candidate is Fieller's set

`F*` is a ratio of two estimated means, and the problem of a ratio whose
denominator may not be distinguishable from zero is old and has a known answer.
Fieller's confidence set for a ratio `ρ = μ_M / μ_G` collects every `r` for which
`M − rG` is not significantly different from zero. When `G` is significantly
non-zero the set is a bounded interval, not centred on the point estimate; when
it is not, the set is two unbounded rays or the whole real line. That is a
report that degrades continuously — it widens without bound as the evidence
for a gap disappears — instead of switching from a number to a refusal.

The case for it is stronger than taste. Von Luxburg & Franz (2009), whose text
was read for this plan, cite Gleser & Hwang (1987) and Koschat (1987) for the
result that any method unable to produce unbounded confidence sets for a ratio
can miss its stated confidence level by an arbitrary amount. Under that result
no always-bounded interval for `F*` near a vanishing gap is trustworthy at its
nominal level, and the present report is always bounded: refused, or capped at 1.
Fieller's set is exact for bivariate-normal `(M, G)`; here `(M̂, Ĝ)` are means
over 33 probes of per-probe estimates with draw-sampling noise, so normality is
an approximation, which is one thing the simulation measures.

The judge–advisor literature is not cited as precedent for any of this; it has
the defect, not a solution.

## What is held fixed and what is sampled

**The frame is fixed (axiom A2).** Each trial draws one set of 33 synthetic
probes, and the truth is `F*` on *those* probes. The uncertainty quantified is
draw-level: finite answers per probe. Generalising over probes is
[Problem 6](../theory/open-problems.md#6-probe-measure-generalization) and is
out of scope.

**Ground truth.** As in [`synthetic.py`](../metrics/validation/synthetic.py):
three options per probe; a sender distribution with concentration 6.0 and a
diffuse distribution `b` with concentration 1.2, from that file's generator. The
prior is moved toward the sender by `g`: `prior = (1 − g)·b + g·sender`. The post
receiver is `post = (1 − λ)·prior + λ·sender`. True `D` values are exact
Jensen–Shannon divergences in bits, the true floor is zero, true
`F* = (D_prior − D_post)/D_prior`, and true movement `M = D_prior − D_post`.

**Sampling.** Each party answers `n` times per probe, i.i.d. from its true
distribution.

## The cells

| factor | levels |
|---|---|
| draws per probe `n` | 10, 16 |
| gap closure `g` | 0, 0.6, 0.8, 0.9, 0.95, 0.98 |
| transfer `λ` | 0.25, 0.5, 0.75, 1.0 |
| zero-gap cells (`g = 1`) | null: post = sender; antinoophor: post = 0.7·sender + 0.3·`w`, `w` a fresh diffuse distribution |

That is 48 cells plus 4 zero-gap cells, with **400 trials per cell** and **400
bootstrap replicates per trial**. Every trial's seed is fixed by its cell and
index.

## Estimators

All three share `M̂ = D̂_prior − D̂_post`. `b̂_q` is the floor on
`(sender, post)` — the library default — and `b̂_p` the floor on
`(sender, prior)`.

| variant | numerator | denominator |
|---|---|---|
| **V0**, the library default | `M̂` | `D̂_prior − b̂_q` |
| V1, floor on the prior pair | `M̂` | `D̂_prior − b̂_p` |
| V2, both terms floor-corrected | `M̂ − b̂_p + b̂_q` | `D̂_prior − b̂_p` |

**The floor is computed exactly.** The library estimates the permutation floor
by Monte Carlo over shuffles. Its limit is the expectation of the
Jensen–Shannon divergence over uniformly random splits of the pooled draws,
which for three options is a finite sum over a multivariate hypergeometric
distribution. The simulation uses that sum. A test must show it agrees with
`permutation_floor` at large permutation counts before any result is read.

**Reports compared, per variant:**

- *Gated, capped point* — the present report: `min(1, M/G)` if `G > ε`, else
  refused.
- *Percentile interval* — 2.5th and 97.5th percentiles of the bootstrap ratio
  over replicates with `G* > 0`, capped and uncapped.
- *Fieller set* — `{r : (M̂ − rĜ)² ≤ z²(V_MM − 2r·V_MG + r²·V_GG)}`, `z = 1.96`,
  with the covariance of `(M̂, Ĝ)` from the bootstrap. It is classified as
  bounded, two rays, or the whole line.
- *Movement interval* — the percentile interval of `M*`, reported beside `Ĝ` and
  its interval, for want 2.

The bootstrap resamples each party's answers within each probe, which is the
draw-level sampling the frame-fixed truth calls for.

## What is measured

Per cell: the true gap; the gate's pass rate; bias, root-mean-square error and
the share at the cap for each point report, conditional on being reported;
coverage of the true `F*` for each interval — **unconditionally**, with a
refusal counted as a miss, and conditionally on being reported; the share of
Fieller sets in each of the three shapes and the median width of the bounded
ones; and, for the movement interval, coverage of the true `M` and in the zero-
gap cells the share excluding zero.

## Predictions, recorded before any code runs

- **P1.** The *V0 Fieller set* covers the true `F*` in at least **0.93** of
  trials in every cell where `F*` is defined. 0.93 is two Monte Carlo standard
  errors below 0.95 at 400 trials. I hold this less firmly than the others:
  `M̂` carries the upward small-`n` bias of plug-in divergences, and bias
  comparable to its standard error would cost coverage. If V0 fails and V2
  passes, that is the finding, not a reason to change P1.
- **P2.** The percentile intervals, capped or not, fall below 0.93 coverage in
  some cell with `g ≥ 0.9`, and the present gated report — a refusal counting
  as a miss — falls below it in every cell with `g ≥ 0.95`.
- **P3.** For every `(n, λ)`, the share of Fieller sets that are bounded is
  lower at `g = 0.98` than at `g = 0`, and at `g = 0.98` it is below one half.
- **P4.** In the zero-gap antinoophor cells the movement interval excludes zero,
  on the side of moving away, in at least **0.8** of trials at `n = 16`. In the
  zero-gap null cells it excludes zero in at most **0.08** of trials.
- **No prediction** is registered for the *sign* of the gated, capped report's
  bias. The cap can only lower a value (retraction 23); the gate selects which
  values are reported, and which way that selection pushes is what the
  simulation is for.

## What would change what

If P1 holds, the plan's output is a *proposal*, for the repository owner, that
`F*` be reported as `Ĝ` and `M̂` with their intervals plus the Fieller set for
their ratio, with the point estimate demoted to a summary. Nothing in
`metrics/` changes on the strength of a simulation, and no existing result is
recomputed. If P1 fails for every variant, the report says so and Problem 12
stays exactly as open as it is. Either way, the variant comparison is reported in
full, as evidence for the open `floor_on` question in `fidelity_from_draws`.

## Limits stated in advance

- Synthetic agents, three options, independent draws, uniform weights. Real
  agents may give dependent draws within a probe, which this does not model.
- One generator of distributions. A different generator could move every
  number here.
- The frame is fixed. This says nothing about a fidelity's stability across
  probe measures — that is the most dangerous falsifier on the site, and this
  plan does not touch it.

## Exposure

Drafted by `claude-opus-5-5`, which has read Problem 12, the prior-art pages,
the fidelity estimator and the synthetic harness, and wrote retraction 23. It is
the author of the prediction it will score. See [EXPOSURE.md](../EXPOSURE.md).

---

*This document is licensed CC BY 4.0.*
