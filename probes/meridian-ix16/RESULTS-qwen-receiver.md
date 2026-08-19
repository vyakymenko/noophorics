# Result: `qwen3.5:35b` as receiver on `MERIDIAN-IX32`

**Run completed 2026-08-19, 28h 33m wall-clock, 1 920 calls.** Scored against
[the prediction committed before it ran](PREDICTION-qwen-receiver.md). Instrument
data; no hypothesis in `theory/` is touched.

## The prediction failed, and it failed cleanly

`predicted_diverging_qwen_receiver` was `true` for `X16` and `X19` and `false`
for the other thirty.

| | |
|---|---|
| true positives | **0** |
| false positives | **2** (`X16`, `X19` — neither diverged on any message) |
| false negatives | **2** (`X11`, `X26` — both diverged, both predicted not to) |

**H-wobble is refuted for `qwen3.5:35b`.** Its two wobble probes are `X16` and
`X19`, both at sender margin 8; neither ever diverged. Both of its actual
divergences sit at sender margin **10** — perfect confidence. Sender margin
predicted `gpt-oss`'s divergences at 7 of 7 and predicts qwen's at 0 of 2, so it
is not a portable predictor and the [Problem 11](../../theory/open-problems.md)
reading the prediction file hoped for does not hold.

`X19` was the decisive probe and it never fired, which is the answer H-rule
predicted. But H-rule does not survive intact either: `X11` diverged on three
messages for both models and is **not** `R5` — it is the only non-`R5` probe in
either model's divergence set.

## What the run actually found

| message | qwen diverged | `gpt-oss` diverged |
|---|---|---|
| `fluent0` | 2 | 2 |
| `fluent1` | 1 | 5 |
| `fluent2` | 2 | 2 |
| `terse0` | 0 | 0 |
| `terse1` | **0** | **7** |
| `terse2` | **0** | **7** |
| **total** | **5** | **23** |

**qwen's divergence set is a strict subset of `gpt-oss`'s.** qwen loses
`{X11, X26}`; `gpt-oss` loses those plus seven more. Nothing is lost by qwen and
kept by `gpt-oss`.

That splits the measure into two classes that had never been distinguished,
because until now it had only ever been read by one model:

| class | probes | qwen margin | `gpt-oss` min margin | `R5`? |
|---|---|---|---|---|
| **lost by both** | `X11`, `X26` | 10, 10 | 10, 10 | no, yes |
| **lost by `gpt-oss` only** | `X06 X07 X16 X17 X21 X22 X24` | 10 except `X16` at 8 | 4, 10, 8, 6, 6, 6, 8 | all seven |

The first class is transfer loss: both spec-holders are unanimous, both receivers
confidently return a different answer, and the brief demonstrably fails to carry
the qualifier. The second **looks like** the reader's own uncertainty — all seven
are `R5`, six of the seven sit at `gpt-oss`'s wobble points, and a model that is
unanimous on them loses none of them.

### That attribution is withdrawn — [retraction 16](../../RETRACTIONS.md)

**Added 2026-08-19, correcting this document's own first version**, which stated
the second class as reader uncertainty rather than as a reading of it.

Splitting `gpt-oss`'s nine discriminating probes by `gpt-oss`'s **own** sender
margin:

| `gpt-oss` sender | probes | qwen also loses |
|---|---|---|
| unanimous (10) | `X07 X11 X26` | **2 of 3** |
| wobbles (4–8) | `X06 X16 X17 X21 X22 X24` | **0 of 6** |

Fisher two-sided **`p = 0.0833`**. Suggestive, not significant, and the counting
defect of [retraction 15](../../RETRACTIONS.md) applies with force: at similarity
0.85 the three unanimous probes are two clusters (`X07`+`X26`, `X11`) and the six
wobbling ones are three (`X06`+`X17`+`X21`+`X22`, `X16`, `X24`), so the real
table is nearer 2×3 than 3×6 and carries no significance at all.

**The rival explanation is not excluded.** If this were simply one difficulty
dimension with qwen the abler reader, qwen would lose the probes `gpt-oss` loses
*most often*. It does not: `X06`, `X17` and `X21` are lost 3 of 6 by `gpt-oss` —
as often as `X11` and `X26` — and qwen loses them 0 of 6. Rank correlation
between the two models' per-probe loss counts is **0.466** over the nine. That
weakens pure difficulty-plus-ability; it does not refute it, and on this `n`
nothing here could.

**And two further grounds, found the same day, withdraw it rather than qualify
it.** First, the statistic was not like-for-like: `gpt-oss` has **four** sender
passes and `qwen` **one**, so "min margin" gives `gpt-oss` four chances to show a
low value against `qwen`'s one. Counted one pass each, the probes "at a wobble
point" are **2 of 7**, not 6 —

| probe | `gpt-oss` per pass | min of 4 | 1 pass | `qwen` 1 pass |
|---|---|---|---|---|
| `X06` | 10, 10, 10, **4** | 4 | 10 | 10 |
| `X17` | **6**, 8, 8, 10 | 6 | 6 | 10 |
| `X21` | 8, **6**, 10, 8 | 6 | 8 | 10 |
| `X22` | 10, **6**, **6**, 10 | 6 | 10 | 10 |
| `X16` | 10, 10, 8, 10 | 8 | 10 | 8 |
| `X24` | 10, 8, 8, 10 | 8 | 10 | 10 |
| `X07` | 10, 10, 10, 10 | 10 | 10 | 10 |

Second, **no reader-specific term is needed at all.** Fitting one difficulty per
probe plus a *single* reader-ability gap, with no reader×probe interaction,
gives a gap of **2.20 logits** and deviance **10.54 on 8 df, `p = 0.229`** — the
no-interaction model is not rejected, and under it the strict subset is what you
would expect to see.

And by [Dorans & Holland (1992)](../../theory/prior-art.md) an unconditioned
difference between readers of unequal ability is **impact**, not differential
item functioning; the comparison was never conditioned on the 2.20-logit gap,
and Simpson's paradox is the named hazard. See [prior-art
§11](../../theory/prior-art.md).

What stands without qualification is arithmetic: qwen loses 2 of 32 probes,
`gpt-oss` loses 9, and qwen's set is a strict subset. Why the other seven
separate the models is **open**.

## The consequence, which is worse than the one it replaces

**qwen returns 0.83 diverged probes per message against E-002c's gate of 3.**
`gpt-oss` returns 3.83 on the same six messages.

So "escape the anti-correlation by choosing a model" — open, and named worth
asking, when the single qwen sender pass came back 32 of 32 — is **closed**. Not
because qwen saturates (it does not; it diverges on two probes) but because
choosing the stable model costs nearly all the signal. Stability and
discriminating power trade off *across models* exactly as they were found to
trade off across probes.

And the sharper reading is about the measure rather than the models. Of the nine
probes that discriminate for `gpt-oss` on these six messages, **seven are ones a
second architecture does not lose at all.** What looked like the measure's
headroom was substantially one reader's uncertainty. Strip the reader-specific
component and `MERIDIAN-IX32` measures transfer loss on **2 of its 32 probes**.

A successor that wants model-independent outcome variation needs probes of the
`X11`/`X26` kind, and 2 of 32 is the rate at which writing to this design rule
produced them.

## Provenance and corrections to the prediction file

- Sender reused from [`adjudication-qwen-32.json`](adjudication-qwen-32.json),
  and the reuse guard checked the model this time — it had asserted a match it
  never tested until `969115d`.
- Mean divergence is reported for all six messages (0.0082–0.0560) rather than
  refused. The same commit made the reused sender carry its raw draws, so the
  Jensen–Shannon divergence is against real distributions and not a point-mass
  reconstruction.
- **Cost was overstated.** The prediction file says ≈ 66 hours from a measured
  123.9 s/call. Actual: 28h 33m, 53.5 s/call. The timing run had been competing
  with other work on the machine. The prediction file is left as written.
- qwen's sender remains a **single pass**. A margin of 10 recorded there may not
  be stable, by the argument that produced the repeated gate for `gpt-oss`, and
  the two-class split above rests on those margins.
- The counting defect of [retraction 15](../../RETRACTIONS.md) applies here too:
  `X11` and `X26` are not two independent readings, and no rate over these
  probes is a rate over 32 independent rows.

---

*This document is licensed CC BY 4.0.*
