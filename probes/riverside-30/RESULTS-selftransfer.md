# Result: no self-transfer advantage, and if anything the sign runs the other way

**Completed 2026-08-31.** The composer × reader 2×2 on `RIVERSIDE-30`, four
conditions, three briefs each, `n = 10`. Scored against [the prediction committed
before the qwen-composed arms ran](PREDICTION-selftransfer.md). Instrument data.

## The 2×2

| diverged of 30 | read by `gpt-oss` | read by `qwen` |
|---|---|---|
| **composed by `gpt-oss`** | **10.00** *(self)* | 9.67 *(cross)* |
| **composed by `qwen`** | 10.33 *(cross)* | **11.33** *(self)* |

`self − cross`, per brief, **positive means self is worse**:

| | `b0` | `b1` | `b2` | row mean |
|---|---|---|---|---|
| top row, `gpt-oss` composed | −1 | +1 | +1 | **+0.33** |
| bottom row, `qwen` composed | 0 | +1 | +2 | **+1.00** |

All six: `−1, +1, +1, 0, +1, +2`, mean **+0.667**, sd 0.94. Sign test 4 positive,
1 negative, 1 zero — **two-sided `p = 0.375`**.

## Scoring the prediction, including the part that missed

Predicted: *"|self − cross| < 1.5 diverged probes in both rows, and the sign is
not consistently in self's favour."*

- **Row means +0.33 and +1.00 — both under 1.5. Met.**
- **Self is never favoured on a row mean. Met**, and more strongly than the
  wording anticipated: self is *worse* in both rows rather than merely not
  better.
- **One per-brief comparison breached the threshold**: `qwen` on its own `b2`
  diverges 14 against `gpt-oss`'s 12, a gap of **+2**. The prediction's clause
  was written at the row level and is met there, but the per-brief spread is
  wider than 1.5 and that is recorded rather than smoothed into the mean.

**There is no self-transfer advantage on this measure.** A model reads its own
compaction no better than another model reads it, and the point estimate runs
slightly the other way — self worse by 0.67 probes of 30. At `p = 0.375` that
direction is not established; what is established is the absence of the naive
advantage.

## What this says about Problem 9

[Problem 9](../../theory/open-problems.md) asks whether self-transfer is easier
than cross-agent transfer and answers *"naively yes, since the priors match
perfectly."* **It had no measurement. It has one now, and the naive answer does
not survive it** — not reversed, but not supported either.

The result is what the rest of this line predicted. `RIVERSIDE-30`'s divergence
is probe-attributable: both readers always-diverge on the same seven probes at
Jaccard 0.654. If the probes carry the signal, matching the composer to the
reader should buy little, and it buys nothing measurable.

## What it does not establish

**Not Problem 9's `A → A'`.** That is one system after its own compaction. This
is one model composing and later reading in separate contexts with no shared
state — the closest operationalisation available, and the gap was stated before
the run rather than after.

**Nothing about `Φ`.** L5 predicts self-transfer should show *maximal* phantom
agreement — the agent has every reason to trust its own summary. This run has no
elicitation arm and touches that not at all. The interesting half of Problem 9 is
still unmeasured.

**No between-row comparison**, as declared beforehand: `gpt-oss` composed at
423/389/403 words and `qwen` at 240/239/241, a ~40% gap, and length drives
divergence. Every claim above is within-row, where both readers see identical
text.

Six paired comparisons, two composers, one measure, one sitting.

## One thing worth carrying forward

`gpt-oss` was instructed to write ~230 words and produced 423/389/403. `qwen`
produced 240/239/241.

~~`qwen` satisfies it comfortably, so [E-001c's void](../../experiments/E-001c-fluency-length-controlled/VOID.md)
may be model-specific in exactly the way the discriminating/stability
anti-correlation turned out to be.~~ **Withdrawn 2026-08-31, the day after it was
written, on arithmetic that was available when it was written.**

E-001c's band is **182–231** words. `qwen`'s 240/239/241 are all *above* the
ceiling, so it does not satisfy the band either. Worse for the claim: E-001c's
cell A on `gpt-oss` under its **calibrated** instruction has a mean of **242.1**
words, and `qwen` here has a mean of **240.0**. The two models land in the same
place, which is the opposite of a model-specific void.

What survives is a narrower and different fact. On the **identical** instruction
and specification, `qwen` produced 240 where `gpt-oss` produced 405 — so the two
differ sharply in *length-instruction compliance*. That is not what E-001c
voided on, and it does not revive the E-001 line: a proper test would run
E-001c's own calibrated cell-A instruction against `qwen` and count how many of
40 land inside 182–231, and that has not been done.

The coincidence of 240 and 242.1 across two models, two specifications and two
instructions is worth more than the retracted claim was: it suggests ~240 words
may be a **floor for this kind of compressed briefing regardless of reader**,
which would *strengthen* E-001c's void rather than undermine it. Three
compositions is not a basis for asserting that.

---

*This document is licensed CC BY 4.0.*
