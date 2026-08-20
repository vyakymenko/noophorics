# POWER — computed before collection, and it refuses the run

**2026-08-20. No draws exist.** [The pre-registration](PREREGISTRATION.md) §5
gates on this: *"If that fraction is below 0.80, this experiment does not run as
designed."*

**It is 0.117. The experiment does not run.**

## The model

L1's concavity limb needs a generative story concrete enough to simulate. Each
probe gets a cost threshold `t_i` — the message length at which the truncated
specification first resolves it. Then

    F*(C) = fraction of probes with t_i <= C

so `F*` is an empirical CDF and its **shape is the threshold distribution**.
Concave `F*` ⟺ most probes resolved early ⟺ decreasing threshold density. That
makes "concave" a statement about the probes rather than a curve fitted to
nothing.

Cost grid from truncating the 479-word specification at eight equal fractions,
using E-002c's own `cost = 1.4293·words + 74.13`:

    160, 245, 331, 416, 502, 588, 673, 759 tokens   (4.8x, against E-002c's 3.2x)

## The result, 32 probes, bootstrap over probes as declared

| truth | mean `a₂` | power |
|---|---|---|
| strongly concave | −5.28e−07 | **0.173** |
| moderately concave | −4.55e−07 | **0.117** |
| mildly concave | −2.68e−07 | 0.060 |
| linear (null) | −8.53e−08 | 0.023 |
| convex, against L1 | +1.13e−06 | 0.000 |

The null returns 0.023 against a nominal 0.025, so the test is calibrated. It is
not broken; it is blind.

## How many probes it would take

Holding the design fixed at eight rungs and a moderately concave truth:

| probes | power |
|---|---|
| 32 | 0.105 |
| 64 | 0.245 |
| 128 | 0.355 |
| 256 | 0.525 |
| **512** | **0.870** |
| 1024 | 0.990 |

**L1's concavity limb needs a probe measure of roughly 512 probes.** The largest
this programme owns is `MERIDIAN-34`, and `MERIDIAN-IX32` has 32 — of which
[retraction 15](../../RETRACTIONS.md) counts about **nine** independent prompt
templates. The instrument is off by more than an order of magnitude, and the
binding constraint is probe count: `F*` moves in steps of `1/32 ≈ 0.031`, so the
curve is quantised far more coarsely than the curvature it is meant to reveal.

More draws per probe do not help — they sharpen each probe's answer, not the
resolution of `F*`. More rungs do not help — the noise is probe-level.

## The first calculation was wrong, in the direction that would have killed it

The first attempt returned power 0.037–0.083 and bootstrapped **the eight
rungs**. The pre-registration declares a bootstrap over **the thirty-two
probes**, recomputing `F*` at every rung from the same resampled set. Those are
different tests: one probe set read at all eight rungs gives eight *correlated*
values, and a common level shift does not change curvature at all. Resampling
rungs discards exactly the structure the design leans on.

Corrected, the answer moved from 0.04–0.08 to 0.06–0.17 — still far under the
gate, so the verdict is unchanged. Recorded anyway, because a power calculation
that does not implement the declared decision rule is not a power calculation,
and it happened to fail safe here rather than by design.

## What this establishes, which is more than the experiment would have

L1 has never been tested, and the reason is not that nobody got to it. **No probe
measure in this programme can test it.** That is a fact about the instrument, it
was purchased for zero model calls, and it is worth more than 4.6 hours of draws
that could not have answered the question either way.

E-002c's four-rung ladder was underpowered for the same reason and nobody
computed it, which is how its numbers came to be read as bearing on L1 at all.

---

*This document is licensed CC BY 4.0.*
