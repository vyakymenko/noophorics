# E-001c — does fluency buy understanding, once length is controlled?

**Registered 2026-08-03, before any experimental datum exists.** The feasibility
messages this document calibrates against are instrument data and are **not**
E-001c's data; they are discarded before collection begins.

Successor to [E-001b](../E-001b-fluency-factorial/VOID.md), which was voided by
its own cost-parity gate before any outcome was examined.

---

## 1. Why this exists

L5 says fluency inflates phantom agreement. L6 says contrastive encodings
transfer more per unit cost. Both are claims about *encoding*, and both are
untestable while a more fluent message is also a longer one — which it was in
[E-001](../E-001-fluency-cost/FINDINGS.md), by 76%, and in E-001b, by 54%.

E-001c pins length and lets register vary inside it. If fluency still moves `Φ`
when it can no longer buy words, the effect is about the writing. If it does
not, L5 was measuring length.

## 2. What changed from E-001b, and why

Four changes. The first three are repairs the void and its feasibility check
established; the fourth is the reporting standard moving under the programme.

**A two-sided word band replaces the token ceiling.** A ceiling bounds above and
says nothing below, so it cannot produce parity even when obeyed — and it was
not obeyed. Words rather than tokens because a model cannot observe its own
tokenizer, and E-001b is direct evidence it does not honour a token limit.

**Cost parity is judged on cell means, not across messages.** The sample
`max/min` is not scale-free: both extremes drift outward as `n` grows, so the
same parous design fails the same gate for collecting more data.
[Feasibility Result 1c](FEASIBILITY.md) puts the failure rate at E-001b's own
`k = 8` at **86%**, and observed it directly at `k = 4` — messages 1.303 against
cell means 1.054 on one run. E-001b's own text said "across cells" while its
runner compared messages; this resolves that ambiguity in favour of the text,
on an argument that would hold whichever reading it favoured.

**Fluent messages are filtered by blind register judgment.** The
[rating](FEASIBILITY.md) found the fluent instruction produces the intended
register **5 times in 8**, CI `[0.245, 0.915]`, while the terse instruction
works every time. Both raters, from different providers, failed the same three
messages. A forced-choice rating scored 64/64 on the same data and could not
have detected this: it makes a rater name one of two passages even when neither
is the thing described. The filter is specified in §4.

**The reference is declared and `β` is reported.** Both are v0.4/v0.5 norms that
post-date E-001b. `F*` without a stated reference measured movement toward the
sender for three versions; and `Φ` is a level that cannot see whether belief
moves, which is what `β` is for.

## 3. Design

**Model.** `gpt-oss:120b`, both roles, `think=medium`, `temperature=0.7`.

**Probe measure.** `MERIDIAN-33`, the same instrument E-001b registered.

**Reference.** `R = the probe measure's key`, kind `key`, criterion-bearing.
Provenance: authored with the source specification, independently adjudicated.
This is not the sender, so `F*_R` measures understanding rather than
replication — the distinction E-001 cost a live run to find.

**Cells.** 2×2, unchanged from E-001b:

| | declarative | contrastive |
|---|---|---|
| **fluent** | A | B |
| **terse** | C | D |

**Length control.** One word target of **207**, band **±12% (182–231)**, stated
identically in all four cells. Calibrated on the feasibility messages, whose
realised range was 184–230 across both registers; a single target at ±10% admits
7 of 8 fluent and 6 of 8 terse, and ±12% admits all sixteen. Per-cell targets
were considered and rejected: they would fix the band by adding a second
difference between the registers, which is worse than a wide band.

**`k = 8` accepted messages per cell**, 32 in total, as E-001b registered.

**Elicitation `n_c = 9` per probe per party.**
[E-002c H4](../E-002c-calibration-slope/FINDINGS.md) measured resolution at
`+0.3074` on a ten-value grid against `+0.1408` on E-001b's four-value one — the
coarse grid was hiding signal, not manufacturing it.

## 4. The register filter

Composed messages are admitted to a cell only if **both** of two raters,
judging the message **alone**, classify it as its cell's register.

**Raters, named in advance:** `codex` (ChatGPT subscription) and
`claude-opus-4-8` (Anthropic API). Two providers, two authentication paths, and
neither is the composer. A rater sees one passage, the two-option question in
[`blind_rating.py`](blind_rating.py), and nothing else — no specification, no
prompt, no cell label, no indication that an experiment exists.

**The question is absolute, not comparative.** A forced choice between a fluent
and a terse message cannot fail: the rater must name one even when neither is
connected prose, and it will name the wordier one. That is an estimator that
cannot fail, which is
[the E-002b H5 defect](../E-002b-phantom-agreement-ladder/FINDINGS.md), and it
scored 64/64 on messages of which three in eight were lists.

**Budget: 40 composition attempts per fluent cell**, 16 per terse cell. At the
observed rates — 0.625 prose for fluent, 1.0 list for terse — eight accepted
messages need about 13 fluent attempts and 8 terse. The cap is generous and
exists so that a run cannot compose indefinitely; **exhausting it voids the
run**, because a cell that cannot be filled is a cell whose register the model
cannot reliably produce, and that is a finding rather than something to work
around.

**Rejected messages are recorded, not discarded.** Their count, their register
verdicts and their text go in the results file. The rejection rate per cell is a
measurement of how reliably each instruction lands.

## 5. Hypotheses

Stated on **decomposed** quantities. Aggregate `F*` is not a primary outcome for
any hypothesis.

| ID | Hypothesis | Quantity | Predicted |
|---|---|---|---|
| **H1** | Contrastive encodings transfer more understanding | `fidelity_where_sender_right`, contrastiveness main effect | contrastive > declarative |
| **H2** | Fluent encodings inflate phantom agreement | `Φ`, fluency main effect | fluent > terse |
| **H3** | Contrastive encodings are more efficient | `V_λ` on the same quantity as H1 | contrastive > declarative |
| **H4** | Fluency does not buy understanding | `fidelity_where_sender_right`, fluency main effect | **no effect** |

**H4 is a predicted null, declared as such in advance.** It is the sharpest
claim here: L5 says fluency moves *belief* without moving *transfer*. Confirming
H2 while failing to reject H4 is what the programme predicts. A fluency effect
on understanding would damage L5 more than a null on H2 would.

**H3 is stated on `V_λ = F*_R − λC`, not on `η`.**
[Retraction 3](../../RETRACTIONS.md) withdrew `η` as an ordering: a ratio with a
signed numerator ranks a cheap failure above an expensive one. `λ` is declared
now, before data: **`λ = 0.001` per receiver token**, chosen so that the cost
range this design produces (roughly 320–420 tokens) moves `V_λ` by about 0.1 —
the same order as the fidelity differences E-001 observed. `η` is reported
alongside where `F* ≥ 0` and is not a hypothesis.

### 5.1 Recorded, not hypothesised

Error replication per cell, the class-prior baseline, accuracy gain, `Φ_sender`
and `Φ_receiver` separately, **`β` per party** (v0.5 reporting standard),
per-probe resolution, the register rejection rate per cell, and realised word
and token distributions. Interaction terms are **reported but not tested** — a
2×2 at `k = 8` is not powered for interaction.

## 6. Analysis plan

Fixed before data exists.

1. Shared floor by permutation null on sender vs `PRIOR`, 300 permutations,
   seeded; admissibility gate on the prior gap.
2. Per message: decomposition against `R`, `Φ_sender`, `Φ_receiver`, realised
   cost, `V_λ`.
3. **Main effects by permutation test over messages**, 10 000 permutations of
   the cell labels, seeded, two-sided. The exchangeable unit is the **message**.
4. Bootstrap 95% CI over messages for every reported effect. **No point estimate
   without one.**
5. `α = 0.05`. H1–H4 are one family and Holm-corrected where a p-value is used.
6. **Every hypothesis is tested on the statistic it reports.** The effect, its
   interval and its p-value must be computed from the same array; where they are
   not, the analysis is wrong regardless of what it finds. This is stated
   because it has failed twice — [E-002b H4](../E-002b-phantom-agreement-ladder/FINDINGS.md)
   under a paired interval with an unpaired test, and
   [E-002c H3](../E-002c-calibration-slope/FINDINGS.md) with a slope difference
   reported and a level difference tested. See
   [Problem 13](../../theory/open-problems.md).
7. H4 is assessed by interval: it survives if the fluency main effect on
   `fidelity_where_sender_right` has a 95% CI containing zero **and** a width
   under 0.15. A wide interval containing zero is not evidence of no effect and
   will not be reported as one.
8. **Modal answers are gated.** A probe whose modal answer wins by fewer than
   `n/4` draws is reported as unresolved and excluded from the decomposition,
   with the excluded count stated. [Problem 14](../../theory/open-problems.md)
   is open; this is a stopgap, not a solution, and it is registered so that the
   exclusion rule is not chosen after seeing which probes it removes.

### 6.1 Gates — the run is void if any fails

| Gate | Threshold | When |
|---|---|---|
| Sender accuracy vs key | > 0.90 | before analysis |
| Sender error **count** | ≤ 2 of 33 | before analysis |
| `CEILING` fidelity | > 0.70 | before analysis |
| Refusals in any cell | 0 | continuously |
| **Cost parity across cell means** | max/min ≤ 1.30 | before analysis |
| Register filter exhausted in any cell | voids | during composition |
| Unresolved probes | ≤ 4 of 33 | before analysis |

The error-count gate exists because E-001's sender passed a mean-accuracy gate
at 0.882 while its four errors carried 62% of the headline. A gate on the mean
cannot protect a statistic whose effect concentrates.

### 6.2 Declared limitations

- One domain, one model in both roles, one probe measure. Nothing generalises.
- The four style descriptions are the experimenters'; only the prompts
  implementing them were written blind.
- **The fluent register imposes a length of its own.** Feasibility Result 4:
  fluent messages land at 226 words with `sd = 1.5` against `sd = 14.5` for
  terse. The band admits both, but the fluent arm is not complying with the
  target so much as coinciding with it. If a future calibration moves the
  target, that coincidence may not survive.
- The register filter's acceptance rate was estimated on **eight** fluent
  messages. `[0.245, 0.915]` is not a precise rate, and the composition budget
  in §4 is sized for the pessimistic end.
- Classifier refusal behaviour is model-specific and unstable over time; refusal
  rate is measured at the start and end of every run and a change between them
  voids it.

## 7. Amendment policy

**Permissible without a new registration** — instrument only:

1. Replacing the domain, if the current one cannot be composed against.
2. Fixing a defect in the metrics library, applied identically to all cells.

**Not permissible:** changing the model, the cells, the hypotheses, the gates,
the reference, the probe measure, the raters, `λ`, or the word band after
composition begins.

**Cap: one.**

## 8. What each outcome means

- **H2 holds, H4 survives** — fluency moves belief and not transfer, at
  controlled length. This is what L5 predicts and the first evidence for it that
  is not confounded with message length.
- **H2 holds, H4 rejected** — fluency moves both. L5 is not refuted but it is no
  longer the interesting claim, because a fluency effect on understanding is a
  larger finding than a fluency effect on confidence.
- **H2 fails** — the phantom-agreement effect in E-001 was length, not register.
  That retires a headline this programme has repeated, and it is the outcome
  that would cost the most.
- **A register filter exhausts its budget** — the model cannot reliably produce
  one of the four registers at a fixed length, and the 2×2 is not buildable with
  this instruction set. That is a finding about instructions, and the successor
  is a different prompt rather than a different analysis.
- **The parity gate fires** — cost cannot be equalised across registers even
  with a two-sided band, and the confound this experiment exists to remove is
  not removable this way.

---

*This document is licensed CC BY 4.0. It is immutable once committed; corrections
are recorded as amendments beside it, never as edits to it.*
