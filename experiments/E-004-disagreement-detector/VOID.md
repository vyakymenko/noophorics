# E-004 is void — two of three models were never wrong

**Status:** void · closed · no successor registered
**Voided:** 2026-08-03, by gate G2, before any hypothesis was read
**Cost:** four days of local GPU, ~$1.50 of API, and the answer to a question
this design could not have given

---

## The gate that fired

[§5.1](PREREGISTRATION.md) requires **each model wrong at least twice on at
least one measure**, and says of it: *"this is the run's reason for existing"*
and *"if the 'each model wrong twice' gate fails the run is void, not
reinterpreted."*

```
errors, worst measure per model      threshold 2
  claude-opus-4-8    8               pass
  gpt-oss:120b       1               FAIL
  qwen3.5:35b        0               FAIL
```

Two of the three models are essentially never wrong. `qwen3.5:35b` answered all
63 probes across both measures correctly; `gpt-oss:120b` missed one.

The other two gates passed: every model cleared the 0.60 accuracy floor, and the
design produced 12 errors in total against a threshold of 12 — by one.

## Why this is fatal rather than disappointing

The detector flags a probe when two models' modal answers differ, with no key
and no threshold. Its question is whether that disagreement predicts error.

When one model makes every error, "the two models disagree" and "the expensive
one is wrong" are the same event, and the detector is correct by construction.
The results show exactly that:

| measure | pair | errors | flagged | hits | recall | precision |
|---|---|---|---|---|---|---|
| MERIDIAN-33 | claude + gpt-oss | 3 | 3 | 3 | 1.00 | 1.00 |
| MERIDIAN-33 | claude + qwen | 3 | 3 | 3 | 1.00 | 1.00 |
| MERIDIAN-33 | gpt-oss + qwen | 0 | 0 | 0 | — | — |
| RIVERSIDE-30 | claude + gpt-oss | 9 | 9 | 9 | 1.00 | 1.00 |
| RIVERSIDE-30 | claude + qwen | 8 | 8 | 8 | 1.00 | 1.00 |
| RIVERSIDE-30 | gpt-oss + qwen | 1 | 1 | 1 | 1.00 | 1.00 |

Perfect recall and perfect precision on every pair that has an error at all.
A detector that never misses and never false-alarms, across two domains, is not
a discovery — it is the signature of a design where the thing being detected and
the thing doing the detecting are the same event. The pair with no `claude` in
it produced **one** error on 63 probes, which is the whole of the independent
evidence.

**This is the exact defect E-004 was registered to repair.** The
[motivating observation](../../journal/2026-07-30-cross-sender-disagreement.md)
was unusable because `gpt-oss:120b` made zero errors, so what it showed was that
disagreement finds *claude's* errors. §2 of the pre-registration names that
defect and answers it with "three models, and a domain chosen so that **each
model is wrong somewhere**". The repair failed on its own terms: three models,
two domains, and it is `qwen3.5:35b` at zero this time instead of `gpt-oss`.

Reading the six cells as a result would have reported the defect as the finding,
with p-values of 0.0002 and better attached to it.

## What the run does establish, recorded and not hypothesised

The pre-registration lists **each model's accuracy** under "recorded, not
hypothesised". It is the only thing here worth carrying forward, and it is not
what anyone expected:

| | MERIDIAN-33 | RIVERSIDE-30 |
|---|---|---|
| `claude-opus-4-8` | 0.909 | **0.733** |
| `gpt-oss:120b` | 1.000 | 0.967 |
| `qwen3.5:35b` | 1.000 | 1.000 |

The most expensive model was the least accurate on both measures, and by a wide
margin on the harder one. Two open-weight models running on a laptop answered a
rule-application task the frontier model got wrong eleven times.

### The probes were audited, and they hold

VOID asked a successor to check first whether the probes measure what their
author believed. Checked here, because the answer bears on every future run that
reuses this measure.

**All eleven keys are derivable from the source specification, and each one
turns on a rule written to remove exactly the ambiguity the wrong answer falls
into.** The errors are one class: boundary resolution.

| probe | key | `claude-opus-4-8` | the rule that settles it |
|---|---|---|---|
| T01 | 15 March | 16 March | **1.2** — a period of *n* days from `D` ends at `D+n`; *"D is never counted"* |
| T14 | 30 May | 31 May | 1.2, from the current effective due date |
| T10, T21 | DENIED | GRANTED | **3.2** window is the due date and the two days before it; T10 also needs the **1.3** closed-day move |
| T16 | in time | lapsed 4 May | **4.3** — a collection period ending on a closed day runs to the next open day; 4 May is a Sunday |
| T09 | overdue, not forfeit | forfeit | **6.4** — forfeit at the end of overdue day 30; 21 May is day 29 |
| T06 | $0 | $2 | **6.2** — no fee on overdue days 1 and 2 |
| T15 | GRANTED | DENIED | **7.2** — same-date order puts payments before renewal requests, so $24 − $6 = $18, below the $20 suspension bar |

Every key was adjudicated by three readers working from the specification alone,
before any model saw it. The audit finds nothing to revise. **The measure is
valid and reusable**, and it turns out to isolate something narrow and sharp:
inclusive-versus-exclusive counting, and the tie-break rules that resolve it.

### Two kinds of error, and only one of them is about the model

Over 16 draws per probe, the eleven errors split:

```
unanimous or near-unanimous, wrong     T01 16/16   T15 16/16   M14 16/16
                                       M19 16/16   M26 15/16   T09 15/16
                                       T14 15/16   T06 14/16
near coin-flip                         T10  9/16   T16  8/16   T21  6/16
```

Eight are systematic. The model reads a rule one way and reads it that way every
time; on T01 and T15 the correct answer was never drawn at all. That is a
property of how the rule was applied, and it survives any argument about
sampling temperature.

**The other three are a problem with the design, not the model.** On T21 the
wrong answer took the modal slot 6 votes to 5. A different sixteen draws would
have produced a different error set, and therefore a different flag set, a
different recall and a different p-value.

That is worth stating separately from the gate that voided this run, because it
would have applied even had the gate passed: **an error set defined by the modal
answer over `n = 16` is unstable wherever the draw distribution is flat.** Any
successor needs either more draws on the probes that turn out flat, or a rule
that abstains rather than forcing a modal answer through a near-tie. Neither is
in this design.

**What this is not.** It is not a benchmark, not a capability claim, and not
generalisable. Two probe measures of 33 and 30 items, one domain each, one
sampling regime, modal answer over 16 draws. `claude-opus-4-8` was called
through the API with no temperature parameter — the design records that its
distribution comes from the model's own nondeterminism rather than a knob, which
is a different sampling regime from the two local models at `temperature = 0.7`.
That difference is registered and declared, and it is a live alternative
explanation for the accuracy gap that this run cannot separate from capability.

Ninety per cent of a *ceiling* task is also a strange place for a frontier
model. That was the first thing to check and it is checked above: the probes
measure what their author believed, and what they measure is boundary
arithmetic.

## What is not claimed

- **Not** that disagreement fails as an error detector. This run cannot say. It
  produced no usable evidence either way, which is what a fired gate means.
- **Not** that the six p-values mean anything. They are computed and stored in
  the results file because the analysis ran to completion before the gate was
  read, and they are void along with the rest.
- **Not** that `claude-opus-4-8` is worse at reasoning than a 35B open model.
  See the sampling-regime difference above.
- **Not** that the design was wrong to try. The gate is the design working.

## The draws survive

189 cells, every one at exactly `n = 16`, all committed. Any successor that
wants a domain where all three models err has 63 probes' worth of evidence about
which probes are hard for whom, and the errors are listed by id in the results
file.

A successor is **not registered**. Registering one requires a probe measure
where the failure above cannot recur — which means either harder probes or
models closer in capability, and choosing either after seeing this table is
choosing on the outcome. That decision belongs in its own document, written
before the measure exists.

## Record

- Collection: 2026-07-31 10:58 to 2026-08-03 15:13, three runs.
  [Interrupted once](INTERRUPTED.md) by a socket timeout at 104/126 and resumed;
  the third arm was [blocked](BLOCKED-NOTE.md) on billing for three days.
- BLOCKED-NOTE decided in advance that a two-model run would be void. That
  question never arose: the third arm ran, and the run is void for a different
  reason found by a different gate.
- Raw record: [`results/E-004-20260803T161541Z.json`](results/) — the three-model
  analysis. Two earlier files in the same directory are single-arm runs that
  analysed only the models named on their command line and computed no effects.

---

*This document is licensed CC BY 4.0.*
