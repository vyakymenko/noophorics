# Result: the probe-attributable structure survives a second reader

**Run 2026-08-28, `qwen3.5:35b`, 30 probes, `n = 10`, the same three
`gpt-oss`-composed briefs.** Scored against [the prediction committed
beforehand](PREDICTION-qwen.md). Instrument data.

## The prediction held

**Predicted: Jaccard ≥ 0.4 between the two readers' diverged sets. Measured:
0.654.**

| brief | `gpt-oss` | `qwen` | shared | Jaccard | of the 8 named probes |
|---|---|---|---|---|---|
| `b0` | 9 | 10 | 8 | 0.727 | 7 of 8 |
| `b1` | 9 | 8 | 7 | 0.700 | 7 of 8 |
| `b2` | 12 | 11 | 8 | 0.533 | 7 of 8 |
| **mean** | **10.00** | **9.67** | | **0.654** | |

The eight always-diverging probes were **named in the prediction file before
`qwen` answered anything**, so the overlap is not computed against a set chosen
afterwards.

## What it settles

`RIVERSIDE-30`'s divergence is a property of **the measure**, not of
`gpt-oss:120b`. Both readers land on nearly the same probes:

| | `gpt-oss` | `qwen` | shared |
|---|---|---|---|
| union of diverged sets | 13 | 12 | **9** |
| diverge on *every* brief | 8 | 7 | **7** |

`gpt-oss` always-diverges on `T01 T02 T10 T11 T14 T16 T17 T19`; `qwen` on
exactly the same set minus `T01`.

**And it is not a subset relation**, which is the whole contrast with MERIDIAN:

| | MERIDIAN-IX32 | RIVERSIDE-30 |
|---|---|---|
| `gpt-oss` diverged | 9 of 32 | 13 of 30 |
| `qwen` diverged | **2 of 32** | **12 of 30** |
| strict subset? | **yes** | **no** |

On MERIDIAN the stronger reader simply lost less, and its losses were a subset of
the weaker one's — an *ability* difference. On RIVERSIDE both readers lose
comparably and lose the same things, which is what a measure looks like when the
probes, not the readers, carry the signal. `qwen` recovered **30 of 30** keys
from the specification against `gpt-oss`'s 29, so this is not the weaker model
compensating.

## The pairing gain holds, at a lower factor for `qwen`

| reader | SE unpaired | SE paired | pairing | inter-brief corr | **paired MDE** |
|---|---|---|---|---|---|
| `gpt-oss:120b` | 0.118 | 0.048 | **×2.46** | +0.834, +0.795, +0.650 | **0.135** |
| `qwen3.5:35b` | 0.117 | 0.065 | **×1.80** | +0.693, +0.771, +0.787 | **0.183** |

MERIDIAN gave ×1.00 and correlations around zero. So the gain is real on this
measure and **reader-dependent in size** — 2.46 against 1.80. Any MDE quoted for
`RIVERSIDE-30` must name its reader; the 0.128 in
[RESULTS-headroom](RESULTS-headroom.md) is `gpt-oss`'s, and the honest range
across the two readers is **0.135–0.183**.

## `T30` resolves, and in the adjudicators' favour

[The headroom run](RESULTS-headroom.md) recorded `gpt-oss` answering `T30` as
`GRANTED, new effective due date 24 April` against an adjudicated key of
`DENIED` — twice, seventeen days apart. It was left standing and unexplained.

**`qwen`'s sender answers `DENIED`.** It agrees with the key and with all three
blind adjudicators. So `T30` is not a contestable key that slipped through
adjudication; it is one model being reliably wrong about one probe, and the
adjudication standard is vindicated rather than undermined by it.

`T30` also diverges in exactly one brief for each reader — `b2` for `gpt-oss`,
`b0` for `qwen` — so it contributes almost nothing to either rate.

## Limits

Two readers still cannot estimate a variance component
([D-STUDY](../meridian-ix16/D-STUDY.md) obstacle 3); this shows the structure
survives a reader, not how much of it is reader variance. All three briefs are
`gpt-oss`-composed, so `qwen` is throughout reading another model's writing —
the direction E-003 would isolate and [cannot](../../theory/laws.md#l2). Three
briefs, one composer, ~400 words rather than the 230 operating point.

---

*This document is licensed CC BY 4.0.*
