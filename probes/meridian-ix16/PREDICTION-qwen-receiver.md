# Prediction: `qwen3.5:35b` as receiver on `MERIDIAN-IX32`

**Recorded 2026-08-18, before the run. Committed separately from any result, so
that a prediction which fails cannot be quietly reread as the one that
succeeded.** This is the same device `predicted_discriminating` performs for
`X17`–`X32`, and it is used here for the same reason.

## What is being run

Six messages already on disk, 32 probes, 10 draws, `qwen3.5:35b` as receiver,
sender reused from [`adjudication-qwen-32.json`](adjudication-qwen-32.json).
**qwen has never been run as a receiver against this measure** — that file
carries `parties: ["sender"]` and nothing else, verified across every blob in
the object database.

```bash
python3 experiments/E-001c-fluency-length-controlled/headroom_check.py \
  --probes probes/meridian-ix16/probes.json \
  --model qwen3.5:35b --draws 10 \
  --reuse-sender probes/meridian-ix16/adjudication-qwen-32.json \
  --out probes/meridian-ix16/receiver-qwen-32.json
```

Instrument data. No hypothesis in `theory/` is touched and no experiment
registers against this.

## The two hypotheses, and the probe that separates them

[Retraction 15](../../RETRACTIONS.md) left one statement standing: of 1 440
`gpt-oss:120b` sender draws, 19 are non-key and all 19 fall on `R5`-tagged
probes. Two readings of that survive, and they are not the same claim.

**H-wobble.** A probe diverges where *that model's own* spec-holder is least
certain. The sender's hesitation, not its answer, marks where a 230-word brief
fails to carry. On `gpt-oss` this is exact: 7 probes ever returned a margin
below 10 and all 7 discriminate, `corr(min-margin, messages fired) = −0.766`.

**H-rule.** A probe diverges because of what it asks — the `R5` paired-regime
joint — independently of which model reads it. `R5` carries 45 of 49 divergence
events.

On `gpt-oss` the two are indistinguishable, because its wobble set is a subset
of `R5`. **On qwen they come apart**, because qwen's wobble set is not:

| | `gpt-oss:120b` | `qwen3.5:35b` |
|---|---|---|
| probes with any margin < 10 | `X06 X09 X16 X17 X21 X22 X24` | `X16 X19` |
| all inside `R5`? | yes, 7 of 7 | **no** — `X19` is `R8`, not `R5` |

`X19` is the decisive probe. It is tagged `R8, boundary, interaction`; it is
**not** `R5`; it **never diverged for `gpt-oss` across all twelve messages**;
and qwen's sender wobbles on it at margin 8.

- **H-wobble predicts `X19` diverges for qwen.**
- **H-rule predicts it does not.**

## The prediction, per probe

`probes.json` carries `predicted_diverging_qwen_receiver` on every probe: `true`
for `X16` and `X19`, `false` for the other thirty. That is H-wobble's literal
and strong form, recorded as stated rather than hedged.

It is very likely to be partly wrong, and the partial failure is the
informative part. Read the outcome as:

| outcome | reading |
|---|---|
| `X19` diverges | H-wobble survives its sharpest test. Sender margin is a **pre-transfer** predictor of post-transfer divergence — a candidate for [Problem 11](../../theory/open-problems.md), which asks exactly for divergence predicted before collection. |
| `X19` does not diverge, and qwen's divergences sit on `R5` | H-rule. Divergence is a property of the rule the probe asks about, and sender margin is a `gpt-oss` coincidence. |
| neither — qwen diverges on nothing | Saturation, as on `MERIDIAN-34` where qwen returned `Â = 1.000` on three messages. Then "escape the anti-correlation by choosing a model" is closed: qwen is stable **and** has no signal. |
| qwen diverges widely, on both | Both are wrong at this operating point and divergence is not predicted by either. |

## What this run cannot do, stated in advance

It cannot produce a probe-level 2×2 with a significance level. qwen's *rejected*
set is empty — all 32 margins are ≥ 8 after one pass — so the unstable row is
zero and Fisher returns `p = 1.0` for every possible receiver outcome. Anyone
reaching for that table afterwards should stop here instead.

It also inherits the defect that retraction 15 records: 32 probes are ~9 prompt
templates, so no count over them is 32 independent readings. The `X19` test is
a **single named probe** with a direction fixed in advance, which is why it is
the statement this file makes and a rate is not.

And qwen's sender has been drawn **once**. One pass cannot establish that its
margins are stable, by exactly the argument that produced the repeated gate for
`gpt-oss` — `X06` passed four of five passes at 10/10 before failing the fifth.
So a qwen probe recorded here at margin 10 may not be one.

## Cost, measured rather than estimated

`qwen3.5:35b` at the runner's settings (`think=medium`, `temperature=0.7`) was
timed at **123.9 s per call warm**, six calls, model resident throughout —
against `gpt-oss:120b`'s 5.8 s/call derived from the gate-run timestamps, a
factor of 21. This run is 1 920 calls, so **≈ 66 hours**.

The README's "about eleven hours" for five qwen sender passes is an
underestimate by roughly five times: the same arithmetic gives 55 hours.

---

*This document is licensed CC BY 4.0.*
