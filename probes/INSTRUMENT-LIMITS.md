# What these probe measures can and cannot detect

**Measured 2026-08-20, zero model calls.** Every number here comes from
probe-bootstrapping [E-002c's raw draws](../experiments/E-002c-calibration-slope/results/E-002c-20260803T121500Z.json).

This file exists because [E-006 died on its own power gate](../experiments/E-006-ablation-ladder/VOID.md)
and the obvious next question — *is that specific to E-006?* — turns out to be
answerable for the whole remaining roadmap, cheaply, before anything is designed.

It is not.

## The measured noise

Resampling probes with replacement and recomputing `F*` from the same draws:

| quantity | 33 probes |
|---|---|
| SE of a single `F*` | **0.092** |
| SE of a difference of two `F*`, independent probe sets | 0.119 |
| SE of a difference of two `F*`, **same** probe set | **0.119** |

**Pairing on the probe set buys nothing.** Correlation between two briefs' `F*`
across the same resampled probes: `+0.120`, `−0.099`, `+0.013`, `+0.447` over
four brief pairs — around zero, with one exception. Which probes a brief loses is
a property of *that brief*, not of the probes, which is the same thing
[MERIDIAN-IX32's README](meridian-ix16/README.md) established from the other
direction. A paired design does not rescue an underpowered one here.

## What that costs each remaining planned experiment

Minimum detectable effect, two-sided 95%, 80% power, scaling as `1/√n`:

| probes | MDE on a difference of `F*` |
|---|---|
| **32** (`MERIDIAN-IX32`) | **0.338** |
| 34 (`MERIDIAN-34`, the largest owned) | 0.328 |
| 64 | 0.239 |
| 128 | 0.169 |
| 256 | 0.120 |

**E-003, the asymmetry matrix, attacks [L2](../theory/laws.md#l2).** Its statistic
is `F*(A→B) − F*(B→A)`. The two local models differ by **2.20 logits** of ability
on `MERIDIAN-IX32`, and on the same six briefs `gpt-oss` lost 9 probes of 32 where
`qwen` lost 2 — a raw gap of **0.219**. That is the size of asymmetry there is
reason to expect, and it sits **below** the 0.338 the instrument can resolve.
Roughly 64–128 probes would be needed.

**E-007, chain decay, attacks [L4](../theory/laws.md#l4).** L4c is the interesting
limb — constraints decaying more slowly than descriptions — and it is a difference
*between two classes of probe*, so the split halves each `n`. `MERIDIAN-IX32`
tagged by form gives at most about 16 per class:

| probes per class | MDE on the class gap |
|---|---|
| **16** | **0.479** |
| 32 | 0.338 |
| 64 | 0.239 |

**E-006, the ablation ladder, attacks [L1](../theory/laws.md#l1).** Void already.
Curvature is harder than a difference: about **512 probes**.

## The conclusion, stated plainly

~~**The instrument is the binding constraint on this programme, not the ideas.**~~
**Corrected 2026-08-20 — the ceiling was MERIDIAN's, not the programme's.**
`RIVERSIDE-30` was measured against briefs for the first time
([results](riverside-30/RESULTS-headroom.md)) and returns **10.00 diverged of 30**
against a gate of 3. Its divergence is **probe-attributable** where MERIDIAN's is
brief-attributable — eight probes diverge on every brief, inter-brief correlation
`+0.849 / +0.805 / +0.666` — so **pairing buys a factor of 2.58**, which the table
below assumes it does not. Measured directly rather than scaled, `RIVERSIDE-30`
resolves **0.128** with a paired design, not the 0.383 stated here, and **E-003
is powered on it.** The numbers below stand for MERIDIAN and are the reason the
roadmap looked closed. Keep reading them as MERIDIAN's.

**The instrument every experiment reached for is the binding constraint, not the
ideas and not the programme.**
Every experiment still on the roadmap needs a probe measure several times larger
than any that exists, and the requirement rises with the complexity of the
statistic — 64–128 for a difference, ~512 for a curvature.

That is why three laws have stood `conjectured` since founding with no experiment
against them. It was read as a queue. It is a ceiling.

## Effective probe count, measured 2026-08-20 — and the MDEs above are optimistic

Every MDE in the table above uses **raw** probe counts. Retraction 15 established
that `MERIDIAN-IX32`'s 32 probes are about nine independent prompt templates. So
the obvious question is what the other three measures are, and it turns out to be
the most consequential number in this file.

Single-link clustering on prompt similarity, all four measures at the same
thresholds:

| measure | raw | 0.80 | 0.85 | 0.90 | 0.95 | largest cluster @0.85 |
|---|---|---|---|---|---|---|
| `MERIDIAN-34` | 34 | 4 | **10** | 16 | 20 | 16 probes |
| `MERIDIAN-33` | 33 | 4 | **9** | 15 | 19 | 16 probes |
| `MERIDIAN-IX32` | 32 | 9 | **9** | 13 | 19 | 11 probes |
| **`RIVERSIDE-30`** | 30 | 21 | **25** | 27 | 30 | **4 probes** |

**`RIVERSIDE-30` is not like the others.** And it is not a length artifact — its
prompts are longer (294 chars against ~200), which would depress a similarity
ratio mechanically, so the same question was asked with Jaccard over word sets,
which is almost length-blind:

| measure | mean Jaccard | max | **pairs with J ≥ 0.8** |
|---|---|---|---|
| `MERIDIAN-34` | 0.444 | 0.944 | **25** |
| `MERIDIAN-33` | 0.449 | 0.944 | **25** |
| `MERIDIAN-IX32` | 0.398 | 0.969 | **18** |
| `RIVERSIDE-30` | 0.266 | 0.750 | **0** |

Zero near-duplicate pairs against eighteen to twenty-five. The difference is real
and it is structural.

What that does to the numbers above, at threshold 0.85:

| measure | raw | effective | MDE(raw) | **MDE(effective)** |
|---|---|---|---|---|
| `MERIDIAN-34` | 34 | 10 | 0.328 | **0.605** |
| `MERIDIAN-33` | 33 | 9 | 0.333 | **0.638** |
| `MERIDIAN-IX32` | 32 | 9 | 0.338 | **0.638** |
| `RIVERSIDE-30` | 30 | 25 | 0.349 | **0.383** |

**Every published MERIDIAN result rests on about nine effective probes, not
thirty-odd.** The ceiling is lower than the first half of this file states, and
the correction is a factor of about 1.9 on every MERIDIAN MDE.

### The programme already owns the instrument it needs to be building toward

`RIVERSIDE-30` is also the **only** probe measure here whose keys were ruled on
by readers who did not write them — three adjudicators, blind to the keys, each
under a different instruction, with a probe dropped if *any* of them answered
against the key **or** flagged it indeterminate
([ADJUDICATION](riverside-30/ADJUDICATION.md)).

So the best-adjudicated and least-templated measure in the repository is the same
file, and it has been used in exactly one experiment —
[E-004](../experiments/E-004-disagreement-detector/VOID.md) — which is void.
Everything else ran on MERIDIAN.

Two consequences, and the second is the one that matters:

1. `E-003` and `E-007` should run against `RIVERSIDE-30`, not MERIDIAN. It does
   not close the gap — 0.383 against the ~0.219 asymmetry E-003 expects — but it
   is 1.7× better than the measure they would otherwise have used.
2. **A successor measure must be built the way `RIVERSIDE-30` was built.** The
   "512 probes" figure assumes independent rows; scaled the MERIDIAN way it would
   be 512 probes worth about 140. `RIVERSIDE-30` demonstrates that 30 probes can
   be worth 25, from one author, in one sitting — so the ceiling is not a law
   about probe-writing, it is a fact about how these three measures happened to
   be written.

## What it does not license

**Not** that the laws are unfalsifiable. They are falsifiable at a probe count
nobody has built.

**Not** that building 512 probes solves it. [Retraction 15](../RETRACTIONS.md) is
the warning attached: `MERIDIAN-IX32`'s 32 probes are about **nine** independent
prompt templates, so a measure scaled the easy way would be 512 probes that are
ninety. Every MDE above assumes independent rows and is optimistic by whatever
factor the templating costs.

**Not** that these numbers transfer to another measure or another model. The
noise was measured on `MERIDIAN-33` with `gpt-oss:120b` in both roles. A second
reader would have its own, and today's work established that reader-specific
structure is real and that two readers cannot estimate its variance
([D-STUDY](meridian-ix16/D-STUDY.md)).

---

*This document is licensed CC BY 4.0.*
