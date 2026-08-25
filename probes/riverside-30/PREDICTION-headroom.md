# Prediction: does RIVERSIDE-30 have headroom at the operating point?

**Recorded 2026-08-20, before the sender or any receiver is drawn.** The briefs
exist (`briefs.json`, composed and written first so a refusal would be visible);
no probe has been answered.

## Why this is being run at all

[INSTRUMENT-LIMITS](../INSTRUMENT-LIMITS.md) recommended `RIVERSIDE-30` to E-003
and E-007 **on independence alone** — 25 of 30 probes independent against
MERIDIAN's nine of thirty-odd, and the only measure here adjudicated by readers
who did not write its keys.

Independence is worth nothing if the measure saturates, and `MERIDIAN-34` is the
cautionary case: independent enough, and saturated at 230 words, which is the
entire reason `MERIDIAN-IX32` was built. **Nobody has ever run `RIVERSIDE-30`
against a brief.** E-004 gave both models the full specification, where they
score 0.967 and 1.000 — that is the sender condition and says nothing about
transfer.

So the recommendation I published yesterday is untested, and this tests it.

## The briefs are longer than the operating point, and that is conservative

Target 230 words; `gpt-oss:120b` composed **423, 389 and 403**. They are used as
composed and **not** re-composed toward the band, because
[E-001c voided](../../experiments/E-001c-fluency-length-controlled/VOID.md) on
precisely that manoeuvre — the register's length floor sat above the band's
ceiling, and targeting a word band in this generator is a known-unsatisfiable
instruction. Retrying it would be repeating a void.

The length cuts one way only. Observed agreement rises with message length
across every rung this programme has measured, so **divergence at ~400 words is
a lower bound on divergence at 230**. If the measure clears the gate here, it
clears it at the operating point. If it does not, this run cannot tell whether
230 words would have.

Compression, for scale: 400 words carries **35%** of RIVERSIDE's 1 131-word
specification, against MERIDIAN's 230-of-479 = **48%**.

## The prediction

**`RIVERSIDE-30` returns ≥ 3 diverged probes per message**, clearing E-002c's
outcome-variation gate, at ~400 words.

Three reasons, stated so a failure is legible:

1. **Harsher compression.** Even at 400 words the brief carries 35% of the source
   against MERIDIAN's 48%.
2. **Answer diversity.** `RIVERSIDE-30` has **22 distinct keys** over 30 probes —
   dates, amounts, specific grant dates, named refusal reasons — where MERIDIAN
   has three verdicts shared by every probe. A receiver that has lost a detail
   has many more ways to be wrong, and fewer ways to be accidentally right.
3. **Low templating.** Zero probe pairs at Jaccard ≥ 0.8, against 18–25 in each
   MERIDIAN measure, so divergence events cannot pile onto one template.

| outcome | reading |
|---|---|
| **≥ 3 diverged/message** | The recommendation holds. `RIVERSIDE-30` is the instrument E-003 and E-007 should use, and it is the first non-saturated, low-template, independently adjudicated measure this programme has. |
| **1–3** | Headroom exists but below the gate at 400 words. Undetermined at 230, and the run would have to be repeated shorter — which E-001c says cannot be instructed. |
| **≤ 1** | Saturated like `MERIDIAN-34`. The INSTRUMENT-LIMITS recommendation was wrong on the half it did not measure, and must be struck. |

## What this run cannot establish

One model in both roles, so nothing about any second reader — the same limit
[D-STUDY](../meridian-ix16/D-STUDY.md) records. Three briefs, one composer, one
sitting. And the sender is drawn fresh here rather than reused, so its accuracy
against the key is itself a check: a sender that cannot recover `RIVERSIDE-30`'s
keys from the full specification would void the run before the receivers matter.

---

*This document is licensed CC BY 4.0.*
