# E-001b is void — the cost parity gate failed before the sweep ran

**Status:** void · closed · superseded by E-001c (not yet registered)
**Voided:** 2026-07-29, after composition, before any probe outcome was examined
**Gate:** cost parity across cells, `max/min realised cost ≤ 1.30`
([PREREGISTRATION §4.1](PREREGISTRATION.md))

---

## The numbers

Realised cost of the 32 composed messages, measured with the sender's own
tokenizer (`prompt_eval_count`), all four cells given the identical instruction
to write within a 350-token budget:

| cell | style | n | mean tokens | min | max |
|---|---|---|---|---|---|
| A | fluent · declarative | 8 | 620.0 | 561 | 688 |
| B | fluent · contrastive | 8 | 608.6 | 559 | 716 |
| C | terse · declarative | 8 | 406.6 | 366 | 441 |
| D | terse · contrastive | 8 | 392.8 | 365 | 432 |

| reading of the gate | ratio | threshold | verdict |
|---|---|---|---|
| across messages (as coded) | **1.962** | 1.30 | FAIL |
| across cell means (as worded) | **1.579** | 1.30 | FAIL |

The pre-registration says "cost parity across **cells**"; the runner computed
max/min across **messages**. That discrepancy is real and is recorded here —
but it did not have to be adjudicated, because both readings fail. Which is the
only reason this document can be trusted: the author noticed the ambiguity
while already knowing which way it would resolve, and it resolved the same way
regardless.

## What was and was not seen

Voiding is a decision, and a decision made after seeing outcome data is not the
same decision. So, precisely:

**Examined:** message word counts, message token costs, cache key names and
counts, the persisted messages' fingerprints.
**Not examined:** any probe answer, any divergence, any fidelity, any `Φ`, any
effect. No analysis was run. No results file exists.

The draws on disk at void time are `sender`, `PRIOR` and `CEILING` — the three
conditions that do not depend on any composed message — plus nothing else. The
sweep over message conditions had not begun.

## Why this is a finding and not just a mishap

E-001's fatal defect was that its two conditions confounded style with cost: a
longer message transfers more by containing more, so any fidelity difference
between a polished narrative and a terse list is unattributable.

E-001b's whole answer to that was **a shared token budget plus a parity gate**.
Every cell received the same `budget=350` instruction. The gate existed to
check that the instruction worked.

It did not work. Instructed identically, the model produced fluent messages at
**1.5×** the cost of terse ones. The budget is not a constraint the model
honours uniformly across style instructions — asking for fluent prose in 350
tokens and terse prose in 350 tokens does not produce two messages of 350
tokens, it produces one of ~614 and one of ~400.

That is the finding, and it is more general than this experiment:

> **Style and length are entangled in the generator.** A style manipulation
> instructed by prompt cannot be assumed cost-neutral, and an experiment
> comparing styles "at equal cost" must *verify* cost parity rather than
> instruct it.

Both laws under test are stated with that clause. [L5](../../theory/laws.md#l5):
fluency inflates `Φ` faster than it raises `F*`. [L6](../../theory/laws.md#l6):
*"At equal cost*, encoding the cases where we would diverge transfers more
fidelity than encoding what I understand." If equal cost is unattainable by
instruction, then testing either law requires constraining generation — and the
constraint may change what the styles *are*. That difficulty was not visible
before this run and is now the central design problem for the successor.

## Why the successor is E-001c and not an E-001b amendment

The [amendment policy](PREREGISTRATION.md#5-amendment-policy) enumerates a
closed list of permissible instrument changes: replacing the domain, fixing a
defect in the metrics library, reducing `k` for budget. Changing how messages
are composed is not on it, and the policy's "not permissible" list includes the
gates and the analysis plan.

The available repairs all change the generating process for the experimental
unit:

1. ~~**Rejection sampling to a realised-cost band.** Compose, measure, resample
   until within tolerance. Preserves the style manipulation; changes the
   distribution of messages to one conditioned on length.~~
   **Refuted within the hour, by data already on disk when it was proposed.**
   The two style families' realised costs are **disjoint** — fluent
   `[559, 716]` tokens, terse `[365, 441]`, with 118 tokens of clear air
   between them. No band intersects both, so acceptance is zero for *every*
   band. The proposal was not expensive, it was impossible, and it was written
   without checking sixteen numbers that were already measured.
2. **Truncation to a common budget.** Rejected: fluent structure loads its
   payload late, so truncation removes different content from different cells —
   a new confound in place of the old one.
3. **Abandon equal cost; test the per-cost quantities directly.** Changes the
   hypotheses, so it needs a new registration in any case.
4. **Replace the ceiling with a two-sided target.** The diagnosis that makes
   this the candidate: `Stay within {budget} tokens` is a **one-sided
   constraint used to enforce a two-sided requirement**. A ceiling bounds above
   and says nothing about below, so it cannot produce parity even when obeyed —
   and it was not obeyed. Every cell exceeded 350 tokens; the fluent cells by
   76%. A model cannot observe its own tokenizer, so the successor states a
   **word** band and verifies the realised token cost afterwards.

Option 4 is the candidate for **E-001c**, and it is not yet known to work.
Whether the four registers survive being pinned to a common length is an open
instrument question, measured in
[`E-001c/feasibility.py`](../E-001c-fluency-length-controlled/feasibility.py)
before anything is registered. Convergence is not sufficient: if "fluent at 220
words" is indistinguishable from "terse at 220 words", the manipulation has been
destroyed rather than controlled, and there is nothing left to test L5 or L6
against. **E-001c does not exist until that measurement says it can.**

This is not classified as an amendment. E-001b is closed as void, and the
repair is registered under a new ID with its own hypotheses committed before
its own data — which is what the norm is for.

## What carries forward

- **The messages.** 32 composed messages with their fingerprints and realised
  costs, in [`messages.json`](messages.json). They are the evidence for the
  finding above and are not discarded.
- **The three message-independent conditions.** `sender`, `PRIOR` and `CEILING`
  at n=30 remain valid for the same model, spec and probe measure, and are
  retained in the sample cache for E-001c.
- **The repaired runner.** [DEFECT-001](DEFECT-001.md) — the analysis path was
  never executable and would have crashed after the full sweep. Found and fixed
  in the same session, before this.

## The uncomfortable part

Three defects in one experiment on one day. Two were found by attempting to run
things rather than by reading them, and one of those only because the other
forced a restart. Had the analysis path not crashed, this sweep would have run
for thirty hours and *then* reported void on a gate that was already decidable
from the composed messages.

The cost parity gate is computable the moment composition finishes. It was
placed at the end of the analysis instead. **Gates that can be evaluated early
should be evaluated early**, and E-001c will evaluate every gate at the earliest
point its inputs exist.

The third is the one worth dwelling on, because it is not a coding error. The
first version of this document proposed rejection sampling as the repair — a
paragraph of confident reasoning about a procedure that sixteen already-measured
numbers, sitting in the same directory, prove has acceptance zero. It took
twenty minutes to refute and would have taken two to check.

That is the failure this programme is about. The proposal was fluent, internally
coherent, and written by someone who believed it. Nothing about the writing
signalled that it had not been checked, and had it not been checked here it
would have been checked by whoever tried to build E-001c. A well-formed artifact
produced confidence out of proportion to the evidence behind it, in a document
about an experiment testing whether well-formed artifacts produce confidence out
of proportion to the evidence behind them.

`Φ` is not only something the instruments measure.

---

*This document is licensed CC BY 4.0.*
