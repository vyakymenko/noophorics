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

**The instrument is the binding constraint on this programme, not the ideas.**
Every experiment still on the roadmap needs a probe measure several times larger
than any that exists, and the requirement rises with the complexity of the
statistic — 64–128 for a difference, ~512 for a curvature.

That is why three laws have stood `conjectured` since founding with no experiment
against them. It was read as a queue. It is a ceiling.

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
