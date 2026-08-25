# Result: RIVERSIDE-30 is not saturated, and the ceiling was MERIDIAN's

**Run 2026-08-20, `gpt-oss:120b`, 30 probes, `n = 10`, three briefs of 423, 389
and 403 words.** Scored against [the prediction committed
beforehand](PREDICTION-headroom.md). Instrument data.

## The prediction held, with room

**Predicted: ≥ 3 diverged probes per message. Measured: 10.00 of 30.**

| brief | words | diverged | agreement |
|---|---|---|---|
| `b0` | 423 | 9 | 0.700 |
| `b1` | 389 | 9 | 0.700 |
| `b2` | 403 | 12 | 0.600 |
| **mean** | | **10.00 of 30** | **0.667** |

Per probe that is **0.333**, against `MERIDIAN-IX32`'s **0.120** at 230 words —
and this was measured at roughly *double* the message length, which by every
rung this programme has measured is the direction that *reduces* divergence. The
230-word figure would be higher.

The sender recovered 29 of 30 keys from the specification (0.967), so the probes
are not defective. Its one error is `T30`, where it answers `GRANTED, new
effective due date 24 April` against a key of `DENIED` — **the identical probe
and identical direction `gpt-oss` failed in E-004** seventeen days earlier at a
different draw count. That is a stable disagreement with an adjudicated key, not
sampling noise, and it is left standing rather than dropped.

Receivers are confidently wrong where they diverge: median margin **8**, mean
7.9, unanimous on 14 of 30 events. Transfer loss, not coin-flips.

## The structural finding, which matters more than the rate

**On `RIVERSIDE-30`, divergence is a property of the probe. On MERIDIAN it was a
property of the brief.**

| | `RIVERSIDE-30`, 3 briefs | `MERIDIAN-IX32`, 6 messages |
|---|---|---|
| mean diverged | 10.00 of 30 | 3.83 of 32 |
| union of diverged sets | 13 | 9 |
| **intersection** | **8** | **0** |
| pairwise Jaccard of the sets | 0.800, 0.750, 0.615 | — |

Eight probes diverge on **every** brief. On MERIDIAN, **no** probe diverged on
all six messages. Seventeen `RIVERSIDE` probes never diverge at all, so the
measure has a stable hard core and a stable easy core rather than a shifting
target.

That inverts [what this line established on
MERIDIAN](../meridian-ix16/README.md) — that how much of a specification
survives is a property of *that brief* — and it explains why pairing bought
nothing there.

## Which unblocks E-003

Probe-bootstrapping the three briefs, measured directly rather than scaled:

| | `RIVERSIDE-30` | MERIDIAN |
|---|---|---|
| inter-brief correlation | **+0.849, +0.805, +0.666** | +0.120, −0.099, +0.013, +0.447 |
| SE of a difference, independent probes | 0.118 | 0.119 |
| SE of a difference, **same** probes | **0.046** | 0.119 |
| **pairing buys** | **×2.58** | ×1.00 |

| design | MDE at 80% power |
|---|---|
| unpaired | 0.330 |
| **paired** | **0.128** |

**E-003 expects an asymmetry of about 0.219** — `gpt-oss` lost 9 probes of 32
where `qwen` lost 2 on the same six briefs. **`0.128 < 0.219`, so E-003 is
powered on `RIVERSIDE-30` with a paired design.**

## What this corrects in a file published yesterday

[INSTRUMENT-LIMITS](../INSTRUMENT-LIMITS.md) concluded *"the instrument is the
ceiling, not the queue"* and put `RIVERSIDE-30` at an MDE of **0.383**. Two
things were wrong with that number, both because it was **scaled from MERIDIAN's
noise rather than measured on RIVERSIDE**:

1. It assumed pairing buys nothing. True of MERIDIAN, false here by a factor of
   2.58.
2. It therefore reported an unpaired MDE for a statistic that is naturally
   paired.

The corrected reading: **the ceiling was MERIDIAN's, not the programme's.** Three
laws have stood unattacked, and the reason is not that no instrument can carry
the tests — it is that the instrument every experiment reached for is nine
effective probes with brief-attributable noise, while the one measure with 25
effective probes and probe-attributable noise sat unused after a single void
experiment.

**Not corrected:** E-006 and L1. Curvature needs ~512 probes and pairing does not
help a curvature the way it helps a difference; that verdict stands.

## Limits

One model in both roles, so nothing about a second reader. Three briefs, one
composer, one sitting — and the inter-brief correlations rest on three points.
The briefs are ~400 words against the 230 the rest of the programme uses, which
is conservative for the rate and **not** obviously conservative for the
correlation structure. `T30`'s standing disagreement with its adjudicated key is
unexplained.

---

*This document is licensed CC BY 4.0.*
