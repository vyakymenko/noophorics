# Retractions

Every claim this programme has made and then withdrawn, with what killed it.
Nothing here is deleted from where it originally stood — each is struck through
in place, so a reader arriving at the original text sees the correction rather
than a clean document that never made the mistake.

This file exists because the site quotes a *count*, and a count nobody can audit
is worse than no count.

**Standing tally: 11 claims withdrawn, four experiments void, 1 finding
established.**

The last two numbers were both stale until 2026-08-04, and in opposite
directions. The void count missed [E-001c](experiments/E-001c-fluency-length-controlled/VOID.md);
the findings count still said zero after [E-002c](experiments/E-002c-calibration-slope/FINDINGS.md)
landed, so this file went on advertising a cleaner failure record than the
programme had earned. A file whose whole purpose is that a count can be audited
had two counts nobody was auditing. `check_counts.py` now reads the void number
here as well as on the site; the findings number is not mechanically derivable
— an experiment with a `FINDINGS.md` and no `VOID.md` is not the same thing as
an established result — so it stays a judgement, and it stays visible here.

---

## Axioms and definitions

| # | Claim | Killed by | Where |
|---|---|---|---|
| 1 | **A3** — no bounded message closes an arbitrary prior gap | A 113-token lookup table reaching `F* = 1`. Restated for held-out probes under bounded cost. | [PRINCIPIA §4](PRINCIPIA.md) |
| 2 | `D_floor` is "the irreducible divergence caused by the parties' own stochasticity", and belongs inside the *definition* of `F*` | Two perfectly aligned stochastic agents have identical true distributions, so their true JSD is exactly zero. The floor is **estimator bias**, and a fidelity that changes when you sample more is not well-posed. | [definitions §3](theory/definitions.md) |
| 3 | `η = F*/C` is "the quantity engineering should optimize" | A ratio with a signed numerator is not an ordering. At `F* = −1`, a 100-token antinoophor scores −10.00 and an 800-token one −1.25, so the message that spends eight times as much to do the same damage ranks higher. Replaced by `V_λ = F* − λC`. | [definitions §4.3](theory/definitions.md) |
| 4 | Falsification criterion 2 — "`Φ ≈ 0` means the pathology does not exist" | Bias and resolution are independent. A party predicting 0.70 on every probe and averaging 0.70 has `Φ = 0` and no ability to say which probes it got wrong; it is maximally pathological and the criterion scored it as our refutation. | [PRINCIPIA §7](PRINCIPIA.md) |

## Laws

| # | Claim | Killed by | Where |
|---|---|---|---|
| 5 | **L2** headline form | Tautological as stated. | [laws.md](theory/laws.md#l2) |
| 6 | **L4** — fidelity is multiplicative along a chain | Ill-typed: it multiplied fractions of different prior gaps, and two antinoophors composed to a positive product. Measured: hops of −0.629 and −1.000 multiply to +0.629. Restated as L4a/L4b/L4c. | [laws.md](theory/laws.md#l4) |
| 7 | **L6** is "the field's first engineering prescription" | I-PASS, deployed and outcome-measured since 2014 across nine programmes and 10 740 admissions. | [laws.md](theory/laws.md#l6) · [prior-art §5](theory/prior-art.md) |
| 8 | **L5** is "our sharpest conjecture" | The human half is Carpenter et al. (2013) and Deslauriers et al. (2019). Status stays `conjectured` — a prior is not a test — but the framing was ours to lose. | [laws.md](theory/laws.md#l5) · [prior-art §4](theory/prior-art.md) |

## Novelty claims

| # | Claim | Killed by | Where |
|---|---|---|---|
| 9 | `Φ` is "the part we have not found elsewhere", and is what "everyone had felt, nobody had weighed" | Keysar & Henly (2002), Newton (1990), Chang et al. (2010), Endsley (2020). It was weighed in 1990, and their instruments are in places better than ours. | [PRINCIPIA §1, §5](PRINCIPIA.md) · [prior-art §1](theory/prior-art.md) |
| 10 | Knowledge distillation "measures success as task accuracy" | Stanton et al. (2021) define fidelity separately from generalization and show accuracy does not imply it — E-001's construct failure, from a NeurIPS abstract, five years early. | [PRINCIPIA §2](PRINCIPIA.md) · [prior-art §3](theory/prior-art.md) |
| 11 | "Fidelity-versus-correctness was separated in ML **first**" | Cronbach (1955) separated an accuracy score from an assumed-similarity score, each with its own decomposition; Edwards et al. (2006) measured team mental-model similarity and accuracy as two quantities and compared them as predictors. Both predate the ML work. The content survives; the primacy word does not. | [prior-art §3](theory/prior-art.md) |

---

## Void experiments

| id | what it was going to measure | why it is void |
|---|---|---|
| [E-001](experiments/E-001-fluency-cost/FINDINGS.md) | fluency vs contrastiveness on fidelity and `Φ` | Sender refused to compose. Reopened as a construct critique: the headline quantity rewards mimicry, and 62% of its effect sat on four probes where the sender was wrong. |
| [E-001b](experiments/E-001b-fluency-factorial/VOID.md) | the same, factorially, with a cost-parity gate | The gate failed on the composed messages: fluent briefs cost 1.5× terse ones under an identical budget instruction. Style and length are entangled in the generator. Also [DEFECT-001](experiments/E-001b-fluency-factorial/DEFECT-001.md) — the analysis path had never been executed and would have crashed after 30 hours. |
| [E-002](experiments/E-002-phantom-agreement/VOID.md) | `Φ` for the first time, elicited per probe | 330 of 330 elicitations returned "yes, we will agree" — the instrument has a default answer, because it ported Keysar & Henly's granularity and not their forced-choice structure. And the transfer was perfect (0 of 33 probes diverged), so there was nothing for a belief to be wrong about. |

---

## Refused entry

Drafted, checked, and never committed. They are not withdrawals — they never
reached `theory/` — but they are recorded so that nobody, including their
author, drafts them again.

| claim | why it was refused |
|---|---|
| `WOA` attributed to Yaniv & Kleinberger (2000) | That paper publishes the **complement**, `WOE = \|a−f\|/\|a−i\|`. Every number in it is a WOE; the citation would have inverted all of them. |
| "Normalized gain is known to correlate with pretest score" | **Contradicted by the paper cited for it.** Hake (1998) reports `r = +0.02` across 62 courses, and that near-zero correlation is his central justification for the measure. |
| The judge–advisor weighting/accuracy separation as "a fourth independent arrival at the fidelity-versus-correctness split" | The field reports the two quantities separately but does not theorise a split. That reading is ours and may be recorded only as ours. |
| Edwards et al. (2006) cited for "accuracy predicted performance where similarity did not" | Unsupported by the only text available. The abstract says accuracy was the *stronger* predictor, which presupposes similarity predicted too. |

The second one is the instructive one: it would have imported a criticism of a
statistic **from the paper that refutes the criticism**, because the criticism
circulates more widely than the measurement does.

---

## What this list is for

Two things, and neither is penance.

A refuted claim is a **measurement**. Knowing that `η` inverts on antinoophors,
or that a cost-parity gate cannot be met by instructing a budget, is knowledge
the programme did not have before, and it was purchased at a price. A file
containing only survivors would tell a flattering lie about how the field got
here, and would make the same mistakes available to the next person.

And it is an **audit surface**. The count on the front page is checkable against
this table, the table is checkable against the struck-through text, and the
struck-through text is checkable against git. A programme whose subject is the
gap between confidence and evidence should be the easiest one in the world to
catch overstating itself.

---

*This document is licensed CC BY 4.0.*
