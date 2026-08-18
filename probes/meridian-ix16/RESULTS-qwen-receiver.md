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
the qualifier. The second is **the reader's own uncertainty** — all seven are
`R5`, six of the seven sit at `gpt-oss`'s wobble points, and a model that is
unanimous on them loses none of them.

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
