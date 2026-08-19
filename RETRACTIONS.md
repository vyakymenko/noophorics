# Retractions

Every claim this programme has made and then withdrawn, with what killed it.
Nothing here is deleted from where it originally stood — each is struck through
in place, so a reader arriving at the original text sees the correction rather
than a clean document that never made the mistake.

This file exists because the site quotes a *count*, and a count nobody can audit
is worse than no count.

**Standing tally: 16 claims withdrawn, four experiments void, 1 finding
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

## Findings

A section that should have existed since 2026-08-02. The eleven above are claims
about the theory and its novelty; these are claims about *a measurement*, killed
by a better measurement. The first of them was struck correctly at its origin and
indexed nowhere, so the standing count was one short for two days and no check
could see it — `check_retracted.py` did not read experiment documents at all
until 2026-08-04.

The second is here on the same rule and not because it is comparable in weight.
It stood for one day, in an instrument note, and was killed by widening the very
measurement that produced it. A file that records only the expensive mistakes
would be a curated list rather than a ledger, and the cheap ones are the more
common failure.

The fourth, #15, is of a kind this ledger had not held before. The three above
withdraw a **quantity**; #15 withdraws the **warrant** — the arithmetic was
performed correctly on a sample that does not have the structure the test
assumes. It therefore reaches backwards into #14, whose own supporting evidence
was one of the p-values it strikes, and it cannot be repaired by recomputation:
a measure built from one-token variants of a shared prompt has no defensible
number of independent rows, only a range that moves with where the clustering
line is drawn. The lesson is not about Fisher's test. It is that
[A2](PRINCIPIA.md) makes the probe measure the frame of reference, and nobody
had asked how many *distinct* readings a frame of thirty-two probes contains.

| # | Claim | Killed by | Where |
|---|---|---|---|
| 12 | "The parties' confidence is very nearly unresponsive to how much actually transferred" — E-002b's headline pull-quote, labelled post-hoc when made | E-002c committed the quantity before collecting and measured `β = +0.1299`, CI `[+0.047, +0.223]`, which clears zero. Confidence **does** respond, at about an eighth of the rate calibration requires. The direction replicated and the magnitude did not. The unresponsive party is the **sender alone**, `β = −0.02` with its interval spanning zero — a narrower claim than the one withdrawn, and a sharper one. | [E-002b §6](experiments/E-002b-phantom-agreement-ladder/FINDINGS.md) · [E-002c §3](experiments/E-002c-calibration-slope/FINDINGS.md) |
| 13 | "Zero of the 25 non-`interaction` probes diverge at 230 words" — stated in Problem 15 from six messages, and read as the property that only interaction probes survive saturation | Widening the same measurement to twelve messages across all four cells found three: `M02`, `M12`, `M29`. A small-sample zero, killed within a day by the instrument that produced it. What survives is the proportion — 21 of 24 divergence events on 9 of 34 probes — and the divergence **rate** the specification is costed against, 0.194 against 0.204, which the widening left standing. | [Problem 15](theory/open-problems.md#15-φ-has-no-belief-component-where-the-manipulation-has-to-live) · [headroom-2x2.json](experiments/E-001c-fluency-length-controlled/headroom-2x2.json) |
| 14 | "`MERIDIAN-IX32` reaches 3.33 diverged probes per message and clears E-002c's outcome-variation gate" — the candidate probe measure built to repair Problem 15 | The admission gate behind that number had been applied **once**. Applied five times, admitting a probe only if it returns the key at margin ≥ 8 in every pass, it rejects four probes, and the measure on the 28 survivors gives **2.00** per message — below the gate. Worse for the repair than for the claim: all four rejected probes are among the nine that ever discriminated, and none of the twenty-three that never discriminated was rejected, `p = 0.0035`. The headroom was borrowed from probes that are not stable observables. | [MERIDIAN-IX32](probes/meridian-ix16/) · [Problem 15](theory/open-problems.md#15-φ-has-no-belief-component-where-the-manipulation-has-to-live) |
| 15 | Every Fisher exact `p` computed over `MERIDIAN-IX32`'s probes — `p = 0.0035` and `p = 0.0138` for the anti-correlation between discriminating power and modal stability, and `p = 0.0339` for the design rule that earned `X17`–`X32` | **The measure is not 32 independent probes.** `X17` and `X18` differ by one token — "Combined figure count is 70" against "71" — and carry opposite keys; so do `X21`/`X22` (8 → 7) and `X24`/`X25` (30 → 21). Single-link clustering of the prompts gives **9 clusters at similarity 0.80–0.85**, the largest holding 11 probes, and all instability falls inside 2 of them. Every one of these tests treats near-duplicate rows as independent draws. There is no corrected number to substitute, which is the point: the cluster-level `p` ranges from **0.111 at threshold 0.80 to 0.006 at 0.95**, so the result is a function of a clustering knob rather than of the data. What survives is at the **draw** level and is stronger — of 1 440 `gpt-oss:120b` sender draws, **19 are non-key and all 19 fall on `R5`-tagged probes**, a label committed 2026-08-10 09:29:56, nine hours before the first `IX32` sender pass and therefore prior to every instability datum. | [MERIDIAN-IX32](probes/meridian-ix16/) · [Problem 14](theory/open-problems.md#14-when-is-a-modal-answer-over-n-draws-a-stable-observable) |
| 16 | "Seven of the nine discriminating probes measured the reader, not the transfer" — and its corollary that `MERIDIAN-IX32` measures model-independent transfer loss on 2 of 32 probes *because* the other seven are one reader's uncertainty | Three independent grounds. **(a) The statistic was not like-for-like.** "Six of the seven sit at `gpt-oss`'s wobble points" compares `gpt-oss`'s *minimum over four sender passes* against `qwen`'s *single* pass; more passes means more chances to show a low margin. Counted one pass each it is **2 of 7**. **(b) No reader-specific term is needed.** A model with one difficulty per probe and a **single** reader-ability gap — no reader×probe interaction whatever — fits at deviance **10.54 on 8 df, `p = 0.229`**, with the gap at **2.20 logits**. The strict-subset structure is what that model predicts anyway. **(c) It is impact, not differential functioning.** [Dorans & Holland (1992)](theory/prior-art.md): DIF requires comparing examinees "supposed to be comparable with respect to the attribute measured"; an unconditioned difference between groups of unequal ability is *impact*, and Simpson's paradox is the named hazard. The comparison was never conditioned on the 2.20-logit gap. The counts survive — qwen loses 2 of 32, `gpt-oss` 9, qwen's set a strict subset — but *why* is open, and was published as answered. | [results](probes/meridian-ix16/RESULTS-qwen-receiver.md) · [prior-art §11](theory/prior-art.md) |

---

## Void experiments

| id | what it was going to measure | why it is void |
|---|---|---|
| [E-001](experiments/E-001-fluency-cost/FINDINGS.md) | fluency vs contrastiveness on fidelity and `Φ` | Sender refused to compose. Reopened as a construct critique: the headline quantity rewards mimicry, and 62% of its effect sat on four probes where the sender was wrong. |
| [E-001b](experiments/E-001b-fluency-factorial/VOID.md) | the same, factorially, with a cost-parity gate | The gate failed on the composed messages: fluent briefs cost 1.5× terse ones under an identical budget instruction. Style and length are entangled in the generator. Also [DEFECT-001](experiments/E-001b-fluency-factorial/DEFECT-001.md) — the analysis path had never been executed and would have crashed after 30 hours. |
| [E-002](experiments/E-002-phantom-agreement/VOID.md) | `Φ` for the first time, elicited per probe | 330 of 330 elicitations returned "yes, we will agree" — the instrument has a default answer, because it ported Keysar & Henly's granularity and not their forced-choice structure. And the transfer was perfect (0 of 33 probes diverged), so there was nothing for a belief to be wrong about. |
| [E-004](experiments/E-004-disagreement-detector/VOID.md) | whether a model can predict where another model will disagree | Two of the three registered models were never wrong: 1 error and 0 errors across the whole design. A detector of disagreement needs disagreement to detect, and reporting the run would have reported the defect as the result. |
| [E-001c](experiments/E-001c-fluency-length-controlled/VOID.md) | the E-001 question again, with length pinned by a two-sided word band | The fluent register's length floor sits **above** the band's ceiling — 232 words against 231, at 0 of 12 and 0 of 40. Fluent cells land in the band 5 times in 24 against terse cells' 23 in 24. The fluency instruction is partly a length instruction, so the manipulation is unsatisfiable rather than underpowered. Also [DEFECT-001](experiments/E-001c-fluency-length-controlled/DEFECT-001.md) — the first of the two runs voided on a copied instruction the band was never calibrated on, and establishes nothing. |

**This table was two rows stale until 2026-08-04.** E-004 voided on 2026-08-03
and E-001c on 2026-08-04, and neither was indexed here. The count on the front
page did not notice, because it counts `VOID.md` files rather than rows in this
table — so the number was right while the list a reader actually reads was
wrong. `check_counts.py` compares numbers to their sources and has nothing to
say about an index that omits an entry.

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
| **Problem 16, "a probe measure read by one agent confounds the frame with the reader"** | Drafted 2026-08-19 and refused the same day. It is generalizability theory's **fixed facet**, and Brennan (2003) states as a theorem that with all facets fixed "no generalization is involved, and all error variances are zero" — a known design cost with a known remedy (a D-study over a reader population), not an open question. Applying G-theory to *model* raters is also done (arXiv:2507.19980, seven AI raters). The empirical basis was independently unsound: see retraction 16 in the Findings table above. Recorded as [prior-art §11](theory/prior-art.md) instead, and the open-problem count does **not** move. |

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
