# Prediction: is self-transfer easier? The composer × reader 2×2

**Recorded 2026-08-28, before either qwen-composed arm is drawn.** The briefs
exist (`briefs-qwen.json`); no probe has been answered against them.

## What this measures

[Problem 9](../../theory/open-problems.md) asks whether self-transfer is easier
than cross-agent transfer — *"naively yes, since the priors match perfectly"* —
and calls itself the problem its author would most like solved. It has no
measurement.

Completing the 2×2 on `RIVERSIDE-30` gives one:

| | read by `gpt-oss` | read by `qwen` |
|---|---|---|
| **composed by `gpt-oss`** | **10.00** *(self)* | **9.67** *(cross)* |
| **composed by `qwen`** | ? *(cross)* | ? *(self)* |

The top row is already on disk. Each row is a **length-matched** reader
comparison, which is what makes the design survive the confound below.

**This is not Problem 9's `A → A'` exactly.** That is one system after its own
compaction; this is one *model* composing and later reading, in separate
contexts with no shared state. It is the closest operationalisation available
here and the gap is stated rather than glossed.

## The confound, named before it can be discovered afterwards

`gpt-oss` composed at **423, 389, 403** words against a 230-word instruction.
`qwen` composed at **240, 239, 241** — it hits the target.

So the two rows differ in length by ~40%, and length drives divergence. **Any
comparison *between* rows is confounded and will not be made.** The claim rests
only on the *within-row* differences, where both readers see the identical text.

That length difference is itself worth recording.
[E-001c voided](../../experiments/E-001c-fluency-length-controlled/VOID.md)
because the fluent register's length floor sat above the word band's ceiling —
232 words against 231 — and concluded the instruction was *unsatisfiable*. It was
measured on `gpt-oss`. `qwen` satisfies it. That void may be model-specific in
exactly the way the discriminating/stability anti-correlation turned out to be.

## The prediction

**No self-transfer advantage: |self − cross| < 1.5 diverged probes in both rows,
and the sign is not consistently in self's favour.**

Against the naive expectation, and following from what this measure has already
shown. `RIVERSIDE-30`'s divergence is **probe-attributable** — both readers
always-diverge on the same seven probes, Jaccard 0.654 — so who wrote the brief
and who reads it should matter little compared with which probe is asked.

The top row already points this way and was not chosen for it: self 10.00
against cross 9.67, i.e. **self-transfer very slightly worse**, well inside noise.

| outcome | reading |
|---|---|
| both rows within 1.5, signs inconsistent | Prediction holds. Self-transfer is not easier here, and Problem 9's "naively yes" is wrong at this operating point on this measure. |
| self clearly better in both rows | Self-transfer advantage is real and the probe-attributable finding is weaker than it looked. |
| self clearly **worse** in both rows | A model reads its own compaction *less* well than another model does — the strongest possible form of the pathology this programme studies, and it would need immediate replication before anyone believed it. |
| rows disagree in sign | Composer-specific, and the 2×2 cannot settle Problem 9 without more composers. |

## Cost and limits

`gpt-oss` on qwen-briefs: 900 calls ≈ **1.5 h**. `qwen` on qwen-briefs: 900 calls
≈ **13.4 h**.

Divergence is scored against **each reader's own sender**, so "self" and "cross"
compare like with like on the reference. Three briefs per composer, two
composers, one measure, one sitting. Nothing here measures `Φ`, so L5's
prediction that self-transfer shows *maximal* `Φ` is untouched — that needs an
elicitation arm this run does not have.

---

*This document is licensed CC BY 4.0.*
