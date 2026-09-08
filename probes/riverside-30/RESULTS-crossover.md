# Result: the crossover run had already been made, a month before it was predicted

[The prediction](PREDICTION-crossover.md) was written 2026-09-01 and opens:
**"No `claude-*` model has ever read `RIVERSIDE-30`."** It says the measurement
"has not been made", that the API key is not available in this shell, and that
the file therefore "exists first and alone, which is the order the programme's
own discipline requires."

The measurement had been made. It is in this repository, in a file the
prediction cites two paragraphs later.

**Scored 2026-09-08 against data collected 2026-08-03. Zero model calls.**

---

## The premise was false, and the file that refutes it is the one being cited

[E-004](../../experiments/E-004-disagreement-detector/VOID.md) ran
`claude-opus-4-8` as a sender against two probe measures and recorded the result
under its pre-registration's "recorded, not hypothesised" heading. The raw
artifact is
[`E-004-20260803T161541Z.json`](../../experiments/E-004-disagreement-detector/results/E-004-20260803T161541Z.json),
committed in `801ac86` on 2026-08-03:

```
"RIVERSIDE-30": {"claude-opus-4-8": 0.7333…, "gpt-oss:120b": 0.9666…, "qwen3.5:35b": 1.0}
"measures":     {"RIVERSIDE-30": "RIVERSIDE-30@2e6afe2f3c92"}
```

`RIVERSIDE-30@2e6afe2f3c92` is the **identical measure hash** the prediction was
written against, and the accuracy is the identical quantity — `runner.py:164`
computes `1.0 - len(wrong) / len(ids)` over modal answers against the keys, which
is what "sender accuracy" means everywhere else here.

Three independent places in the repository already said so:

| where | what it said | dated |
|---|---|---|
| E-004 `VOID.md`, the accuracy table | `claude-opus-4-8` **0.733** on `RIVERSIDE-30` | 2026-08-03 |
| [E-001c `PARAMETERS.md`](../../experiments/E-001c-fluency-length-controlled/PARAMETERS.md) | "E-004 put `claude-opus-4-8` at 0.909 … and **0.733 on a second one**" | 2026-08-03 |
| the prediction itself | cites E-004 for its `MERIDIAN` figure, in the paragraph that claims the `RIVERSIDE` run does not exist | 2026-09-01 |

The third row is the one worth sitting with. The prediction reached into E-004
for the number it wanted and did not look at the row underneath it.

## The prediction, scored

Both sharp clauses hold.

| clause | outcome |
|---|---|
| `claude-opus-4-8` sender accuracy on `RIVERSIDE-30` **below 1.000** | **HELD** — 0.733 (22 of 30) |
| `acc(claude) − acc(gpt-oss)` **negative on both domains** | **HELD in sign** — −0.233 and −0.091, on a comparison E-004 itself declares confounded; see below |

**From E-004, one run, 16 draws per probe, both measures** — the only cells here
that are like-for-like with each other:

| model | `MERIDIAN-33` | `RIVERSIDE-30` |
|---|---|---|
| `gpt-oss:120b` | 1.000 | 0.967 |
| `qwen3.5:35b` | 1.000 | 1.000 |
| `claude-opus-4-8` | **0.909** | **0.733** |
| **Δ claude − gpt-oss** | **−0.091** | **−0.233** |

**From elsewhere, for context, and not commensurable with the table above** —
different runs, different draw counts, different sampling regimes:

| model | `MERIDIAN-34` | source |
|---|---|---|
| `gpt-oss:120b` `think=medium` | 1.000 | E-001b gate table |
| `qwen3.5:35b` `think=low` | 1.000 | E-001b gate table |
| `claude-opus-4-8` | 0.882 | E-001b gate table |
| `llama3.3:70b`, `think` omitted | 0.824 | [2026-09-06](../RESULTS-llama-crossover.md) |

`llama3.3`'s `RIVERSIDE-30` figure of 0.467 belongs to that second table's regime,
not the first's, and is left out of the grid deliberately: its own results file
says *"nothing here compares to any published `think=medium` number, by
construction."*

The pre-registered branch that fires is **"No crossover, as predicted"**, whose
reading was written in advance: *"E-003 stays blocked … What would then be needed
is a **domain** whose subject matter one model has a prior about and the other
does not — which is a probe measure, and a month."*

That is the conclusion
[published 2026-09-06](../RESULTS-llama-crossover.md) off the `llama3.3` run. It
was already determined, on a frontier model, on 2026-08-03.

## What this costs, and what it does not

**It does not weaken the conclusion, and it pre-dates it — but "four models" is
not four orderings.** `qwen3.5:35b` is 1.000 on both, a tie at ceiling, which
[the prediction](PREDICTION-crossover.md) registered in advance as its own branch:
*"this is **not** the same as no crossover: it would say the instrument cannot see
the difference, not that the difference is absent."* And `llama3.3:70b` is not a
subject at all — a model recovering 14 of 30 keys from the full specification has
no measurable domain prior, so its ordering is not evidence about priors either.
What the record actually holds is **one** model measured below `gpt-oss` on both
domains under conditions its own experiment declares confounded, one model at
ceiling on both, and one non-subject. No crossover has been found; that is not the
same as its having been ruled out, and the file said so first.

**E-004 declared the confound before it produced the number.** Its void note
records that `claude-opus-4-8` was called with no temperature parameter against
two local models at `temperature = 0.7`, that this *"is a live alternative
explanation for the accuracy gap that this run cannot separate from capability"*,
and, in its "what is not claimed" list, ***"Not** that `claude-opus-4-8` is worse
at reasoning than a 35B open model."* That caveat is inherited here in full. It
does not rescue a crossover — a regime penalty depressing `claude` on both domains
cannot manufacture a *false* absence of one — but it works the other way: a uniform
penalty could **mask** a real crossover, and the `MERIDIAN` column is at ceiling,
where any gap is compressed. So the honest reading is that the prediction's clauses
hold as *accuracy* statements and that the inference from them to *domain priors*
carries E-004's confound with it.

**What is withdrawn is the reason the question was thought open.** The whole
2026-09-01 → 2026-09-06 arc — "the obvious third model has never read
`RIVERSIDE-30`", 42 GB of weights, 1 280 probe calls — was launched to settle a
question this repository had already settled and filed. `llama3.3` was a
different candidate and its run is not void; but it was not the *reason* the
run happened, and the reason was wrong.
[Retraction 20](../../RETRACTIONS.md).

**The exposure claim survives, as a claim about the log.** The prediction also
says "`RIVERSIDE-30` has stayed clean for `claude-*`", and
[EXPOSURE.md](../../EXPOSURE.md) still records no `claude-*` agent against this
measure. That file logs agents whose *working context* carried material forward; a
model called as a stateless subject is not contaminated by it, which is the same
logic under which E-001c's `gpt-oss` composer was recorded as uncontaminated while
the agent directing it was not. So the claim is sound — with the caveat EXPOSURE
states about itself, that it is "a lower bound written by the party with the
incentive to under-report", has already drifted once for eight days, and that
nothing checks it. A future run may still use `claude-*` here.

**One miscitation goes with it, without a ledger row.** E-001c's `PARAMETERS.md`
and the prediction both call 0.882 and 0.909 figures on "the same measure". They
are not: 0.882 is `MERIDIAN-34` (E-001b) and 0.909 is `MERIDIAN-33` (E-004),
distinct measures with distinct hashes and 34 against 33 probes. Nothing inverts
— claude is below `gpt-oss` on both — so this is corrected in place rather than
withdrawn.

## What this cannot establish

Sender accuracy is a proxy for a domain prior and a coarse one; that limit was
stated in the prediction and is not repaired by the data turning up early. One
model on two domains of the same task type still cannot show a crossover that
isn't there to show. And this file scores a prediction against data that
pre-dates it, which is a weaker epistemic act than a pre-registered run: the
result could not have surprised the person writing the prediction, because it was
already sitting where they were looking.

---

*This document is licensed CC BY 4.0.*
