# E-001b — Fluency × Contrastiveness, factorial

**Status:** pre-registered, not yet run
**Registered:** 2026-07-29
**Attacks:** [L5](../../theory/laws.md#l5), [L6](../../theory/laws.md#l6)
**Supersedes:** [E-001](../E-001-fluency-cost/), which is closed as
non-inferential

> Committed before any data exists. If results contradict what is written here,
> this file is not edited — the finding is added and this stands as written.

---

## 1. Why this is not a rerun

[E-001's findings](../E-001-fluency-cost/FINDINGS.md) closed it. Four defects
were structural, not fixable by more samples:

**Its two conditions confounded the two laws.** "Narrative" was *fluent and
declarative*; "contrastive" was *terse and contrastive*. Any difference between
them could have been fluency, contrastiveness, or both — and L5 is about the
first while L6 is about the second. E-001 could not have separated them
whatever it found.

**One message per condition.** The unit of analysis is the message, not the
probe. 34 probes gave a comfortable-looking `n` while the treatment had `n = 1`,
so the result would have been evidence about two specific texts.

**The headline quantity rewarded mimicry.** Both receivers out-decided the
sender; fidelity ranked them the other way; 62% of the effect sat on the four
probes where the sender was wrong and one receiver was right.

**`n = 6` was below the estimator's usable range** — ~0.11 of error at the
operating point, per [validation](../../metrics/validation/synthetic.py).

---

## 2. Design

### 2.1 Factorial, 2 × 2

| | **Declarative** | **Contrastive** |
|---|---|---|
| **Fluent** | polished explanatory prose | polished prose about boundaries |
| **Terse** | bare list of facts | bare list of boundaries |

Fluency and contrastiveness are crossed, so their main effects separate.
**L5 lives on the fluency margin; L6 lives on the contrastiveness margin.**

### 2.2 Messages are the experimental unit

**`k = 4` independently generated messages per cell**, 16 in total. Each is
generated in a fresh context so the generations are independent rather than
variations on a first draft.

Every hypothesis is tested with the **message** as the unit of analysis. Probe
level enters only as within-message noise.

### 2.3 Conditions

| Condition | Receiver's context | Purpose |
|---|---|---|
| `PRIOR` | nothing | `D_prior`, the shared denominator |
| 16 treatments | one message each | the design |
| `CEILING` | the full source spec | upper reference |
| `CLASS_PRIOR` | *(synthetic)* | the decisiveness control, computed not sampled |

### 2.4 Parameters

| Parameter | Value | Why |
|---|---|---|
| Samples per probe `n` | 30 | validation: ~0.02 error at 30, ~0.11 at 6 |
| Probe measure | `MERIDIAN-34`, 24 visible / 10 **held out** | held-out probes exist so capacity is not won by a lookup table |
| Sender / receiver model | recorded per run, **same model both roles** | isolates encoding from prior mismatch |
| Message budget | 350 tokens | realised cost measured and reported |
| Floor | permutation null on sender vs `PRIOR`, **shared by all 16 cells** | one denominator, or the cells are not comparable |
| `ε` | 0.02 | |

### 2.5 Cost, stated honestly

34 probes × 30 samples × (16 treatments + 3 baselines) ≈ **19,400 receiver
calls**, plus 16 generations and the claim elicitations. This is 20× E-001 and
requires concurrency to finish in reasonable wall-clock. If the budget forces a
reduction, **`k` is reduced before `n`** — `n` below 30 is not a measurement,
whereas `k = 3` is merely weaker.

---

## 3. Hypotheses

Stated on **decomposed** quantities. Aggregate `F*` is not a primary outcome
for any hypothesis; reporting it alone is a methodological error
([definitions §3](../../theory/definitions.md)).

| ID | Hypothesis | Quantity | Predicted |
|---|---|---|---|
| **H1** | Contrastive encodings transfer more understanding | `fidelity_where_sender_right`, contrastiveness main effect | contrastive > declarative |
| **H2** | Fluent encodings inflate phantom agreement | `Φ`, fluency main effect | fluent > terse |
| **H3** | Contrastive encodings are more efficient | `η` on the same quantity as H1 | contrastive > declarative |
| **H4** | Fluency does not buy understanding | `fidelity_where_sender_right`, fluency main effect | **no effect** |

**H4 is a predicted null and is declared as such in advance.** It is the
sharpest thing here: L5 says fluency moves *belief* without moving *transfer*.
Confirming H2 while failing to reject H4 is the result the programme predicts;
a fluency effect on understanding would damage L5 more than a null on H2 would.

### 3.1 Also recorded, not hypothesised

Error replication per cell, the class-prior baseline, accuracy gain, and
`Φ_sender` / `Φ_receiver` separately. Interaction terms are **reported but not
tested** — a 2×2 with `k = 4` is not powered for interaction, and pretending
otherwise is how a null becomes a discovery.

---

## 4. Analysis plan

Fixed before data collection.

1. Shared floor by permutation null on sender vs `PRIOR`.
2. Admissibility: abort if `D_prior − floor ≤ ε`.
3. Per message: decomposition, `Φ_sender`, `Φ_receiver`, realised cost.
4. **Main effects by permutation test over messages** (not probes): 10,000
   permutations of the cell labels, seeded, two-sided. The exchangeable unit is
   the message.
5. Bootstrap 95% CI over messages for every reported effect. **No point
   estimate is reported without one.**
6. `α = 0.05`. H1 and H2 are separate hypotheses about separate quantities and
   are not multiplicity-corrected against each other — **unless** the claim gap
   between cells is under 0.05, in which case `Φ` has degenerated into `−Â`,
   H2 is H1 restated, and Holm correction is applied. This condition is checked
   automatically and its outcome recorded.
7. H4 is assessed by CI: it survives if the fluency main effect on
   `fidelity_where_sender_right` has a 95% CI containing zero **and** a width
   under 0.15. A wide CI containing zero is not evidence of no effect and will
   not be reported as one.

### 4.1 Gates — the run is void if any fails

| Gate | Threshold |
|---|---|
| Sender accuracy vs key | > 0.90 |
| Sender error **count** | ≤ 2 of 34 |
| `CEILING` fidelity | > 0.70 |
| Refusals in any cell | 0 — a refusal is missing data and voids the run |
| Cost parity across cells | max/min realised cost ≤ 1.30 |

The error-count gate exists because E-001's sender passed a mean-accuracy gate
at 0.882 while its four errors carried 62% of the headline. A gate on the mean
cannot protect a statistic whose effect concentrates.

### 4.2 Declared limitations

- One domain. Nothing here generalises across domains, and
  [Problem 6](../../theory/open-problems.md) is unsolved.
- One model, both roles. Cross-model transfer is E-003's job.
- The four style descriptions are the experimenters'; only the prompts
  implementing them are written blind.
- Classifier refusal behaviour is model-specific and **unstable over time**
  ([Amendment 003](../E-001-fluency-cost/AMENDMENT-003.md)). Refusal rate is
  measured at the start and end of every run; a change between them voids it.

---

## 5. Amendment policy

Pre-specified, because E-001 amended its instrument three times and nothing
bounded that. An amendment norm that permits unlimited amendment is not a norm.

**Permissible without a new pre-registration** — instrument only, and only
these:

1. Replacing the domain, if the current one cannot be composed against.
2. Fixing a defect in the metrics library, with the correction applied to all
   cells identically.
3. Reducing `k` for budget, per §2.5.

**Not permissible.** Changing `n`, the hypotheses, the gates, the analysis
plan, the factorial structure, or **the model**. The model is the *subject* of
L5, not the ruler: a claim about systems trained on human text cannot survive
swapping which system is being measured.

**Cap: two amendments.** A third voids E-001b entirely and requires a new
pre-registration under a new ID. Amend-until-the-result-appears is bounded at
two attempts.

**Disclosure.** Every amendment states what data existed on disk when it was
committed — tracked or not. The sample cache is now tracked precisely so this
is checkable rather than asserted.

---

## 6. What each outcome means

| H1 (contrastiveness) | H2 (fluency → Φ) | H4 (fluency → understanding) | Reading |
|---|---|---|---|
| ✓ | ✓ | null holds | Both laws survive on separated axes. The strongest available support, and the first positive result this programme would have. |
| ✓ | ✗ | null holds | L6 supported, L5 wounded. Contrastive encodings transfer better without fluency inflating confidence — the field keeps its engineering claim and loses its pathology. |
| ✗ | ✓ | null holds | L6 refuted, L5 supported. The programme refocuses entirely onto calibration, and the handoff prescription is withdrawn. |
| — | — | **rejected** | Fluency *does* buy understanding. L5's mechanism is wrong regardless of what Φ does, and the "feels worst / works best" framing goes. |
| ✗ | ✗ | null holds | Encoding form does not matter here. Both laws `contested`; E-001c would need a domain with more interacting constraints before anything general is concluded. |

---

## 7. Reproduction

```bash
python3 experiments/E-001b-fluency-factorial/runner.py --dry-run
python3 experiments/E-001b-fluency-factorial/runner.py --samples 30 --k 4
```

Results carry every field of the reporting standard plus raw draws for every
condition, so every number is recomputable from the committed record.

---

*This document is licensed CC BY 4.0.*
