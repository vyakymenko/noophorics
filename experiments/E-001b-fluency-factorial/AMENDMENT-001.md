# E-001b — Amendment 001: k raised from 4 to 8

**Date:** 2026-07-29
**Amendment:** 1 of the 2 permitted by [PREREGISTRATION.md §5](PREREGISTRATION.md)
**Data on disk at commit time:** **none.** No runner exists, no cell has been
generated, no probe has been sampled. The sample cache is tracked and empty.

---

## Why

The pre-registration set `k = 4` messages per cell **without a power
calculation**. That was the omission: `k` is the parameter the whole design
rests on, and it was chosen by feel.

Computed after committing the pre-registration and before writing any
apparatus — permutation test over messages, between-message sd of 0.10 on
`fidelity_where_sender_right`:

| `k` | effect 0.05 | effect 0.10 | effect 0.20 |
|---|---|---|---|
| 3 | 0.14 | 0.31 | 0.88 |
| **4** | 0.16 | **0.49** | 0.95 |
| 6 | 0.23 | 0.67 | 1.00 |
| **8** | 0.30 | **0.80** | 1.00 |

**At the pre-registered `k = 4`, a 0.10 effect is detected by a coin flip.**
That is the effect size worth caring about here: E-001's aggregate gap between
its two conditions was 0.138, and the gap on the where-sender-is-right
component — the quantity H1 now targets — was 0.058.

A design that would miss the effect it was built to find is not a conservative
design. It is a design whose null result means nothing, which is worse than no
experiment, because a null would be reported as evidence.

## What changes

`k = 4` → **`k = 8`**. Nothing else: the hypotheses, gates, analysis plan,
factorial structure, `n = 30`, and the model are all untouched.

Cost roughly doubles, to ~38,000 receiver calls. §2.5's rule stands — if budget
forces a cut, `k` drops before `n`.

## Standing

This is the first of two permitted amendments. One remains. A third voids
E-001b and forces a new pre-registration under a new ID.

Note what is *not* claimed: raising `k` cannot favour any hypothesis, since it
changes only the resolution of the test and not its direction. But it is still
an amendment, it is still counted, and the honest reading is that the
pre-registration should have carried this table in the first place.

**Even at `k = 8`, a 0.05 effect is detected 30% of the time.** E-001b is
powered for a moderate effect and blind to a small one, and any null it
produces must be reported with that stated.
