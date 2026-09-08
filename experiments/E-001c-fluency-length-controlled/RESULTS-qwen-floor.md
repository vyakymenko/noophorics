# Result: the fluent floor belongs to the generator, not to the register

**Run 2026-08-31, `qwen3.5:35b`, 48 compositions.** Same script
([`floor_by_register.py`](floor_by_register.py)), same `source-spec.md`, same
calibrated two-sided instruction, same band, 12 per cell. **Only the model
differs** — which is exactly what my earlier, withdrawn comparison failed to hold
fixed. Scored against [the prediction committed
beforehand](PREDICTION-qwen-floor.md).

## The prediction failed, and badly

**Predicted: cell A on `qwen` also fails — ≤ 2 of 12 in band, mean above 231.**

| cell | axes | `gpt-oss:120b` | `qwen3.5:35b` |
|---|---|---|---|
| **A** | fluent × declarative | 232–308, mean 245.0, **0/12** | 197–232, mean 216.6, **11/12** |
| **B** | fluent × contrastive | 223–237, mean 231.1, **5/12** | 209–230, mean 217.6, **12/12** |
| C | terse × declarative | 184–232, mean 207.3, 11/12 | 197–230, mean 219.8, 12/12 |
| D | terse × contrastive | 189–225, mean 211.4, 12/12 | 190–257, mean 218.7, 11/12 |

Eleven of twelve, against a predicted two. The single miss is **232 words —
out by one**, and it is also `gpt-oss`'s *minimum across twelve attempts*. The
two distributions in cell A barely touch.

## What it establishes

**The fluent register's length floor is a property of `gpt-oss:120b`, not of the
fluent register.**

| | `gpt-oss` | `qwen` |
|---|---|---|
| fluent floor, min over cells A and B | **223** | **197** |
| fluent cells in band, of 24 | **5** | **23** |
| terse cells in band, of 24 | 23 | 23 |

~~The band ceiling is 231. `gpt-oss`'s fluent floor sits above it; `qwen`'s sits
**34 words below** it.~~

**Withdrawn 2026-09-08 — [retraction 19](../../RETRACTIONS.md). The table above
refutes the sentence under it.** `gpt-oss`'s fluent floor is **223**, which is
**eight words *below*** the 231 ceiling, not above it. The claim is true only of
cell **A**, whose floor is 232; cell B's floor is 223 and cell B lands in band
**5 of 12**. So `gpt-oss` reaches the band under a *fluency instruction* — in the
contrastive cell — and what it cannot do is fluent × declarative specifically,
which is the cell [VOID.md](VOID.md) names in its gate. `qwen`'s 34 words is
correct.

**That is a claim about length, not about register.** This run measures the band
alone; the register half of E-001c's gate is untested here, as §"L5/L6 are not
revived" below already says. [VOID.md](VOID.md) records that of the two live
cell-A messages that did reach the band, **neither was judged fluent prose** — so
"`gpt-oss` composes fluently inside the band" is exactly the inference this file
is not entitled to make, and an earlier draft of this correction made it.

What this does **not** touch: the in-band counts that carry
[retraction 18](../../RETRACTIONS.md) — 11 of 12 against 0 of 12 in cell A, 12 of
12 against 5 of 12 in cell B — are measured, unaffected, and are the evidence
that the floor belongs to the generator rather than the register. The heading
above stands; one sentence of gloss under it did not.

And the sharper form: [VOID.md](VOID.md) concluded *"the floor belongs to the
fluency axis"* from fluent cells landing in band 5 times in 24 against terse
cells' 23. **On `qwen` it is 23 and 23.** There is no fluency-axis length effect
at all — so what the void identified was not a property of writing fluently but
of one generator writing fluently.

Recorded as [retraction 18](../../RETRACTIONS.md).

## What it does *not* do — the void still stands

**E-001c is still void, and correctly so.** It ran on `gpt-oss:120b`, that model
could not compose inside its own registered band, and the experiment died. None
of that is disturbed. What is withdrawn is the *reason* as generalised: *"the
manipulation is unsatisfiable rather than underpowered"* is true of `gpt-oss` and
false of `qwen`.

**And L5/L6 are not revived by this.** E-001c's gate was **both** filters — the
band *and* two blind raters judging each message prose. This run measures only
the band. On `gpt-oss` the register filter passed 16 of 40 while the intersection
of the two passed 0; the register half is untested here and is the half that
carries the manipulation. A successor would need to run the rating arm on
`qwen`'s compositions before anything is claimed about L5 or L6.

So the honest statement is narrow and worth having anyway: **the E-001 line was
closed for a reason that turns out to be model-specific.** It is not open. It is
no longer closed for the stated reason.

## Limits

Twelve compositions per cell, one model, one specification, one instruction, one
sitting. Composition only — no probes, no ratings, no fidelity. `qwen` also
produced the run's single widest outlier (257 words in cell D), so its
length-following is tighter, not perfect.

---

*This document is licensed CC BY 4.0.*
