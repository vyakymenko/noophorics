# The candidate report, on a generator it has not seen: a plan, committed before its code

**2026-10-30 · prospective plan for an offline confirmation, not an experiment.**
No model is called and no repository data is read. This plan is committed
before its code and before any result. Its predictions stay as written whatever
the run finds.

## What is being confirmed

The [bias-corrected results](2026-10-22-bias-corrected-results.md) left one
untested candidate for reporting `F*`. On the harness it was found on, it held
coverage; part of it — the Wald intervals — was chosen *after* that harness's
results were seen. A construction chosen on one set of data is confirmed only on
data it was not chosen on. This run freezes the candidate exactly as that report
describes it and tests it on a generator built for this plan.

**The candidate, frozen.** Per probe, the divergence is the two-sample
delete-one jackknife of the plug-in Jensen–Shannon divergence
([`bias_corrected.jsd_jk`](../metrics/validation/bias_corrected.py)), not clamped
and with no floor. Over the probe measure, `Ĝ = D̂_prior`, `M̂ = D̂_prior − D̂_post`.
From 400 draw-level bootstrap replicates, which resample each party's answers
within each probe as independent draws:

- **the Fieller set** for `F* = M/G` at `z = 1.96`, from the bootstrap covariance
  of `(M̂, Ĝ)`;
- **the movement's Wald interval** `M̂ ± z·sd(M*)`;
- **the gap's Wald interval** `Ĝ ± z·sd(G*)`.

Nothing else is reported, and no other estimator is compared: this is a
confirmation of one report, not a contest.

## The new generator

| | the harness the candidate came from | this plan |
|---|---|---|
| distributions | `u^c`, normalised, `u` uniform, `c` = 6 (sender) and 1.2 | **Dirichlet**, concentration 0.4 (sender) and 1.5 (diffuse) |
| options per probe | 3 | **3 and 5** |
| answers within a probe | independent | **independent, and correlated** |

**Correlated answers.** With persistence `ρ`, the first answer is drawn from the
party's distribution, and each later one repeats the previous answer with
probability `ρ` and is otherwise a fresh draw. Every answer still has the party's
distribution; consecutive answers are not independent. `ρ = 0` is the
independent case. `ρ = 0.3` is a dependence the bootstrap does not model.

The rest follows the previous plans: 33 probes; the prior moved toward the sender
by `g`, `prior = (1 − g)·b + g·sender`; the post receiver
`post = (1 − λ)·prior + λ·sender`; zero-gap cells with nothing moved
(post = prior = sender) and with a receiver moved away
(post = 0.7·sender + 0.3·w, `w` a fresh diffuse distribution). True divergences
are exact, true `F* = (D_prior − D_post)/D_prior`.

## The cells

`K ∈ {3, 5}` × `ρ ∈ {0, 0.3}` × `n ∈ {10, 16}` × `g ∈ {0, 0.8, 0.95}` ×
`λ ∈ {0.25, 0.75}` — 48 grid cells — plus the two zero-gap cells for every
`(K, ρ, n)`, 16 more. 400 trials per cell, 400 bootstrap replicates per trial,
every trial's seed fixed by its cell and index.

## Predictions, recorded before any code runs

With independent answers (`ρ = 0`):

- **C1.** The Fieller set covers the true `F*` in at least **0.93** of trials in
  every grid cell, at both `K` and both `n`.
- **C2.** The movement's Wald interval covers the true movement in at least
  **0.93** of trials in every grid cell. In the zero-gap cells it excludes zero on
  the side of moving away in at least **0.80** of antinoophor trials at `n = 16`,
  and excludes zero in at most **0.08** of null trials.
- **C3.** The gap's Wald interval covers the true gap in at least **0.90** of
  trials in every grid cell, and lies wholly above zero in at most **0.10** of
  null trials.
- **C5.** The share of bounded Fieller sets is below one half at `g = 0.95` in
  every grid cell. The candidate must keep widening where the gap closes.

With correlated answers (`ρ = 0.3`):

- **C4.** The Fieller set covers the true `F*` in **less than 0.93** of trials in
  at least **half** of the `ρ = 0.3` grid cells. This predicts a failure: the
  bootstrap treats correlated answers as independent and so understates the
  spread. It is registered so that the candidate's reach is stated before it is
  known, rather than after.

C1–C3 are held with moderate confidence. Five options at `n = 10` is two answers
per option, near the regime where Paninski (2003) warns that bias survives
correction and standard intervals understate the error.

## What would change what

If **C1, C2 and C3** hold, the output is a **proposal** for the repository owner:
that `F*` be reported, for independent draws, as this candidate — a Fieller set
from jackknife-corrected divergences, with the movement and the gap beside it,
each with its Wald interval — and that the point estimate become a summary of
those. The proposal states C4's result as the candidate's limit. Nothing in
`metrics/noophorics/` changes on the strength of a simulation; adopting it would
be the owner's change. If any of C1–C3 fails, the report says which and by how
much, there is no proposal, and Problem 12 stays as open as it is.

## Limits stated in advance

- Synthetic agents, one new generator family, a fixed frame. A second generator
  is better than one; it is not every generator.
- Correlated answers of one kind: persistence. Real dependence between an
  agent's answers may take other forms.
- The candidate is confirmed or not *as frozen*; nothing found here may be used to
  change it within this plan.

## Exposure

Drafted by `claude-opus-5-5`, which wrote both earlier simulations and their
reports, chose the Wald construction after the last one, and will score these
predictions itself. See [EXPOSURE.md](../EXPOSURE.md).

---

*This document is licensed CC BY 4.0.*
