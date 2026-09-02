# Prediction: does the fluent register's length floor move with the model?

**Recorded 2026-08-31, before `qwen3.5:35b` composes anything under the
calibrated instruction.**

## Why this is being run

[E-001c is void](VOID.md) because cell A — fluent × declarative — could not reach
the registered band of **182–231** words. Its floor sat at 232 against a ceiling
of 231, and 0 of 40 attempts passed both the band and the register filter. That
was measured on `gpt-oss:120b` alone, and the void's own wording calls the
manipulation *unsatisfiable* rather than underpowered.

If the floor is a property of **the generator**, a second model should sit
somewhere else and the E-001 line — L5 and L6, dead since 2026-08-04 — may be
revivable by changing models. If it is a property of **the task**, a second model
lands in the same place and the void is confirmed rather than merely repeated.

**I already asserted the first and had to withdraw it.** On 2026-08-30 I wrote
that `qwen` "satisfies" the band because it composed 240/239/241 where `gpt-oss`
gave 423/389/403 — but the band is 182–231, so 240 misses it too, and `gpt-oss`'s
own calibrated cell A means **242.1**, essentially the same place. That claim is
[struck](../../probes/riverside-30/RESULTS-selftransfer.md). This run is the
measurement I should have made before writing it.

## The design

`floor_by_register.py --model qwen3.5:35b`, unchanged otherwise: same script,
same `source-spec.md`, same calibrated two-sided instruction, same band, 12
compositions per cell across all four cells. Only the model differs, so the
comparison is like-for-like in a way my earlier one was not.

Baseline, `gpt-oss:120b`, from `floor-by-register.json`:

| cell | axes | range | in band |
|---|---|---|---|
| **A** | fluent × declarative | **232–308** | **0 of 12** |
| B | fluent × contrastive | 223–237 | some |
| C | terse × declarative | 184–232 | most |
| D | terse × contrastive | 189–225 | all |

## The prediction

**Cell A on `qwen` also fails: ≤ 2 of 12 inside the band, and a mean above 231.**

The reason is the coincidence that killed my earlier claim: two models, two
specifications and two different instructions all landed at ~240 words. That
looks like a floor of the compression task rather than of a generator.

| outcome | reading |
|---|---|
| **≤ 2 of 12 in band, mean > 231** | The floor is the task's, not the model's. E-001c's void is **confirmed on a second model** and the E-001 line stays dead for a better reason than before. |
| **≥ 6 of 12 in band** | The floor is generator-specific. E-001c voided on a property of `gpt-oss`, the manipulation is satisfiable after all, and **L5/L6 become testable again** — the most consequential outcome available here. |
| 3–5 of 12 | Marginal. Neither reading is licensed and the honest report is that 12 per cell cannot separate them. |

Cells B, C and D are recorded but carry no prediction; the void was cell A's.

## Cost and limits

48 compositions on `qwen3.5:35b`, roughly **1–1.5 hours**.

Composition only — no probes, no register rating. E-001c's gate was **both**
filters, band *and* two blind raters calling the text prose, and this run
measures only the first. A cell that reaches the band here would still have to
pass the register filter before anything is revived, and that is a separate run
with its own raters.

---

*This document is licensed CC BY 4.0.*
