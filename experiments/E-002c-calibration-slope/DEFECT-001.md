# DEFECT-001 — the noise floor was computed on the wrong pair

**Found 2026-08-20, from files already committed, at no measurement cost.**
Affects the per-brief and per-rung **fidelity** column only. It does **not**
touch `β`, which is this experiment's registered primary quantity.

## The defect

[`runner.py:222`](runner.py) computes the permutation floor between the
**sender** and **PRIOR**:

```python
floor = mean_permutation_floor(raw["sender"], raw["PRIOR"], ...)
```

[`runner.py:241`](runner.py) then divides every **sender-versus-receiver**
fidelity by it:

```python
d_post   = mean_divergence(s_dists, r_dists, measure.weights)
fidelity = transfer_fidelity(d_prior, d_post, floor, epsilon)
```

Those are different pairs. `D_floor` is *finite-sample estimator bias for the
comparison being made* — the site's own definition calls it "a property of the
measurement, not of the agents" — and the permutation null pools **that pair's**
draws. Pool a different pair and you get a different floor.

Here the difference is an order of magnitude, because the two parties are not
alike:

| party | probes where all 16 draws are identical |
|---|---|
| sender | **33 of 33** — a point mass everywhere |
| PRIOR | 4 of 33 |
| receivers | between the two |

Pooling a point mass with the wide PRIOR distribution produces a large expected
divergence under permutation. Pooling it with a receiver, which is much closer
to the sender, produces a small one.

```
floor used for every brief (sender vs PRIOR)   0.041666
comparison-matched floors (sender vs receiver) 0.0076 – 0.0226
```

## What it does to the published numbers

Because a too-large floor *shrinks* the denominator `D_prior − D_floor`, every
fidelity is inflated. And the matched floor **falls as cost rises**, so the
inflation is largest at the top of the ladder: the defect does not merely shift
the column, it **steepens** it.

| rung | published | corrected | Δ | matched floor |
|---|---|---|---|---|
| 30 | 0.228 | **0.217** | −0.012 | 0.0226 |
| 70 | 0.456 | **0.424** | −0.032 | 0.0152 |
| 110 | 0.606 | **0.560** | −0.047 | 0.0118 |
| 150 | 0.848 | **0.784** | −0.064 | 0.0076 |

The climb across the ladder goes from **+0.62 to +0.57**, and the three briefs
that reported exactly `1.0000` (`r110_1`, `r110_2`, `r150_1`) were at the
`min(1.0, ·)` cap because their `d_post` fell below the mismatched floor. Under
matched floors they are **0.912, 0.915, 0.953**, and **no brief on the ladder
reaches 1.0** — the maximum is 0.9530.

Recorded as [retraction 17](../../RETRACTIONS.md).

## What is *not* affected

**`β` is untouched.** It is `_slope(observed_agreement, claims)`
([`runner.py:399`](runner.py)) and never reads the fidelity column. The
registered finding — sender `β = −0.02`, receiver `+0.28`, against 1 for
calibration — stands exactly as published.

**No gate decision flips.** `ceiling_fidelity` passed at 1.0 against a threshold
of 0.70; under a matched floor `CEILING` is 1.0000 and still passes. That gate
has a separate and older problem, recorded in
[the 2026-07-30 audit](../../journal/2026-07-30-two-audit-holes.md): it compares
an agent with a copy of itself and could not have failed.

## How it was found, and why that is the uncomfortable part

Not by an audit of this experiment. It surfaced while asking whether the ladder
could test [L1](../../theory/laws.md#l1) — three briefs appeared to reach
`F* = 1.0`, which is L1's stated refutation condition, and checking *why* they
reached it found the floor instead.

So a mismatched denominator sat in a published table for seventeen days and was
caught only because someone tried to use the column for something else. Nothing
checks it: `metrics/tests/test_metrics.py` tests `transfer_fidelity` against
values it is handed, and cannot know which pair produced them.

**The general form is worth stating, because it is not specific to this runner:**
a floor, a prior and a post that are not all computed over *the same pair of
parties* do not compose into a fidelity, and the type system that would have
caught it — one that carries the pair with the number — does not exist here.
`F*` already refuses to be reported without its reference `R` (error E-001);
this is the same lesson one argument along.

---

*This document is licensed CC BY 4.0.*
