# E-002c — Is confidence responsive to transfer at all?

**Status:** pre-registered, not yet run
**Registered:** 2026-07-31
**Earned by:** [E-002b's findings §6](../E-002b-phantom-agreement-ladder/FINDINGS.md) —
the quantity below was identified **after** that run and is therefore a
hypothesis, not a result
**Probe measure:** `MERIDIAN-33@256672ea3852`

> Committed before any data exists. If the results contradict what is written
> here, this file is not edited. The finding is added and this stands.

---

## 1. Why this exists, and why it is not E-002b again

E-002b asked whether `Φ` rises as fidelity falls, and answered `−0.9662` at
`p = 0.0005`. That statistic turned out to be **incapable of failing**:
recomputed against counterfactual parties tracking the outcome at slope `β`, it
returns `−0.977` at `β = 0, 0.25, 0.50, 0.90, 0.95` and `0.99` alike, breaking
only at exactly `1.0`. It would have read the same against 99%-calibrated
parties.

The quantity that *does* discriminate is the **calibration slope** itself:

```
β = d(claimed agreement) / d(observed agreement),  over briefs
```

Perfect calibration gives `β = 1`. Total unresponsiveness gives `β = 0`.

E-002b's post-hoc estimate was `β = +0.0386`, 95% CI `[−0.173, +0.127]` — but
it was computed after seeing the data, on an instrument that produced only four
distinct claim values, with sixteen briefs. E-002c commits it first and fixes
all three.

## 2. What changes from E-002b

| | E-002b | E-002c | why |
|---|---|---|---|
| primary quantity | `corr(fidelity, Φ)` | **`β`** | the old one cannot fail |
| elicitations `n_c` | 3 | **9** | 3 draws admit only {0, ⅓, ⅔, 1}; 963 of 1056 cells landed on 1.0 and the granularity is part of why |
| briefs `k` | 4 per rung | **6 per rung** | E-002b's CI on β was 0.30 wide; 24 briefs narrows it without changing the ladder |
| rungs | 30/70/110/150 | **unchanged** | the ladder worked; changing it would confound the comparison |
| claim-variance gate | none | **added** | see §5.1 |

Everything else — the probe measure, the model, the forced-choice elicitation,
the outcome-variation gate, `n = 16` draws — is held identical **on purpose**,
so that a difference between E-002b and E-002c is attributable to the changes
above rather than to a redesign.

## 3. Design

```
sender    : gpt-oss:120b + MERIDIAN source spec
PRIOR     : gpt-oss:120b + nothing
CEILING   : gpt-oss:120b + the source spec        (retained, and see §5.2)
rung r, brief j : gpt-oss:120b + brief_rj
```

Rungs 30 / 70 / 110 / 150 target words, `k = 6` briefs each, **24 briefs**.
`n = 16` draws per probe. `n_c = 9` elicitations per probe per party, giving
claims on a ten-point grid rather than a four-point one.

Elicitation is unchanged from E-002b: each party predicts the **counterpart's
verdict** from the probe's own options, and claimed agreement is scored
afterwards by comparison with that party's own modal verdict.

**Reference declaration (v0.4).** `R = sender`, regime *criterion-bearing*,
provenance: the MERIDIAN keys, adjudicated by their author only. `β`, `Φ` and
resolution take no reference; the fidelity reported alongside is therefore
**replication fidelity** and is labelled as such.

## 4. Hypotheses

**H1 — β is below 0.5.** The parties' confidence responds to transfer at less
than half the rate calibration requires. *Primary.* Directional and one-sided
by design: the interesting claim is unresponsiveness, and a β above 1 would be
a different and stranger finding, reported but not predicted.

**H2 — β is indistinguishable from zero.** Strictly stronger than H1 and stated
separately because it can fail while H1 holds. A β of 0.3 would refute H2 and
still be a large finding.

**H3 — the sender is less responsive than the receiver.** `β_sender < β_receiver`.
E-002b's post-hoc point estimates were −0.038 and +0.115, and its H4 (a
*level* difference in the same direction) was supported at p = 0.0033 under the
paired test. This asks whether the same asymmetry holds in the *slope*.

**H4 — resolution survives the finer instrument.** With `n_c = 9`, per-probe
resolution remains above zero. E-002b measured +0.1408 on a four-value grid
where 91.2% of cells were pinned at 1.0; this asks whether that was signal or
granularity.

**Recorded, not hypothesised:** `Φ` as a level, the conditional asymmetry, the
claim-value distribution, per-rung β, and how many briefs have a constant claim
series.

## 5. Analysis plan

1. Shared floor by permutation null, 300 permutations, seeded; admissibility
   gate on the prior gap.
2. Per brief: mean claimed agreement per party, mean observed agreement.
3. **β** by ordinary least squares of per-brief claim on per-brief observed,
   pooled and per party, with a **bootstrap 95% CI over briefs**, 20 000
   resamples. The brief is the exchangeable unit.
4. **H1** supported iff the CI's upper bound is below 0.5. **H2** supported iff
   the CI contains 0. Stated as interval decisions, not p-values, because the
   claim is about a magnitude and a p-value against a nil null answers a
   question nobody asked.
5. **H3** by a **paired** sign-flip permutation on the per-brief
   `β`-contributions, 10 000 draws. Paired because both parties are measured on
   the same briefs — the defect [E-002b's H4](../E-002b-phantom-agreement-ladder/FINDINGS.md)
   was reported under.
6. **H4** by point-biserial and Goodman–Kruskal γ, brief-level bootstrap CI.
7. **Attenuation.** β is attenuated by sampling noise in the per-brief claim
   means. Report the raw β *and* the reliability-corrected β, with the
   reliability computed from the within-brief variance. Report both; correct
   neither silently.
8. H1–H4 are one family and are Holm-corrected where a p-value is used.
9. No point estimate without a CI.

### 5.1 Gates

| gate | threshold | when |
|---|---|---|
| sender accuracy vs key | > 0.90 | before the sweep |
| sender error count | ≤ 2 of 33 | before the sweep |
| prior admissibility | `D_prior − floor > 0.02` | before the sweep |
| cost parity across rungs | reported, **not gated** — the ladder varies cost by design | — |
| per-rung outcome variation | 3 ≤ mean diverged ≤ 30 of 33 | as each rung completes |
| surviving rungs | ≥ 3, else void | as each rung completes |
| **claim variance** | across briefs, `var(claimed) > 0` **and** at least 4 of 24 briefs have a non-constant claim series | before analysis |

**The claim-variance gate is new and it is the one that matters.** β is a slope
of claim on outcome; if every claim is identical, β is `0/x` — not "zero
responsiveness measured" but "no measurement possible". E-002b had no such gate
and came within a hair of it: five of sixteen briefs had a literally constant
sender claim series.

**A constant claim series is not automatically a void.** If claims vary *across*
briefs while being constant *within* them, β is still estimable and the run
proceeds — the gate is on between-brief variance, which is what β consumes.

### 5.2 Declared limitations

- **One model in both roles**, one domain. A model predicting its own copy is
  the easiest case for calibration; a low β here is therefore conservative.
- **`CEILING` is not an independent arm.** It is the sender resampled — 32 of 33
  bit-identical draws in E-002b — so its gate cannot fail and is retained only
  for continuity with the earlier record. See
  [the journal entry](../../journal/2026-07-30-two-audit-holes.md). It is
  **reported, not gated**, and a successor should replace it.
- **β assumes linearity.** If responsiveness is real but confined to the extremes
  — flat in the middle, moving only when transfer collapses — a linear slope
  understates it. Per-rung β is recorded so that shape is visible.
- **Attenuation cuts one way.** Sampling noise biases β *toward* zero, which is
  the direction of the hypothesis. That is why §5.7 requires the corrected value
  beside the raw one.

## 6. Amendment policy

Permissible: fixing a defect in the metrics library, applied identically
everywhere. **Not permissible:** changing `n`, `n_c`, `k`, the rungs, the
hypotheses, the gates, the analysis plan, the elicitation wording, or the model.

**Cap: one.**

## 7. What each outcome means

- **H1 and H2 hold** — confidence is unresponsive to transfer, measured with a
  statistic that could have said otherwise. That is the programme's first
  pre-registered positive result, and it is a stronger claim than `Φ > 0`.
- **H1 holds, H2 fails** — responsiveness is real but far below calibration.
  Also a result, and a more interesting one for engineering: a partial signal
  can be amplified.
- **H1 fails** — the parties *are* substantially calibrated, and E-002b's
  post-hoc β was an artifact of its four-value claim grid. That outcome would
  retire the post-hoc reading and is the reason it was never reported as a
  finding.
- **The claim-variance gate fires** — the elicitation cannot produce variation
  at `n_c = 9` either, and the instrument, not the world, is the subject.

---

*This document is licensed CC BY 4.0.*
