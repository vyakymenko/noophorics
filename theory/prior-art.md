# Prior art

**Created 2026-07-29, after an external review found that several of this
programme's founding novelty claims were false.**

This repository requires every number to be reported with its frame. The same
standard requires every construct to be reported with its prior art, and
[PRINCIPIA](../PRINCIPIA.md) failed it: it reached for Shannon and Grice and
cited not one measurement journal. This file is the correction and the standing
obligation.

Every citation below was verified by an agent that located the source
independently. **Confidence is recorded per item**, and the constraints —
what each source does *not* license — are recorded alongside, because that is
where the damage happens.

---

## 1. Phantom agreement `Φ` is not ours

The claim *"the calibration term — Φ — is the part we have not found
elsewhere"* is **refuted**. The gap between believed and actual transfer has
been measured, with numbers, in at least four literatures.

| source | what it measured | confidence |
|---|---|---|
| Keysar & Henly (2002), *Psychological Science* 13(3), 207–212 | 40 speaker–listener pairs. Speakers' per-trial judgment matched their own intention on 72% of trials; listeners' actual choice matched on 61%; t(39) = 4.36, p < .001. | primary source read |
| Newton (1990), *The Rocky Road from Actions to Intentions*, Stanford doctoral dissertation, Ch. 2 | Tappers estimated listeners would identify ~50% of tapped tunes (range 10–95%); listeners identified **3 of 120**, 2.5%. | primary source read |
| Chang, Arora, Lev-Ari, D'Arcy & Keysar (2010), *Pediatrics* 125(3), 491–496 | Clinical handoff. The item the sender considered most important was not successfully communicated ~60% of the time, while quality ratings stayed high. | abstract read |
| Endsley (2020), *The Divergence of Objective and Subjective Situation Awareness: A Meta-Analysis*, *JCEDM* 14(1), 34–53 | 37 studies carrying both probe-based and self-report measures of situation awareness; the two diverge. | abstract read |

**Their instruments are in places better than ours.** Keysar & Henly's headline
result is not the 72-vs-61 gap at all — it is a *conditional asymmetry*:
where the addressee had **not** understood, speakers judged that they had on
46% of trials, against 12% in the other direction, a 34-point gap
(t(39) = 6.74, p < .001) present in 80% of individual speakers. Computing that
requires pairing each prediction with *that trial's* outcome. Our single global
elicitation of `Ĉ` cannot compute it at all. That is why
[falsification criterion 2](../PRINCIPIA.md#7-what-would-falsify-the-program)
was invalid as written.

### What these sources do not license

- **They did not measure our `Φ`.** No rate was ever elicited from a Keysar &
  Henly speaker; every speaker response was a two-alternative per-trial forced
  choice, and 72/61 are reconstructed aggregates. Our instrument is strictly
  weaker and inherits none of that paper's authority.
- 72%/61% are **pooled** over 12 syntactic and 4 lexical items. The
  syntactic-only pair is 76%/66%. The overhearers were **Experiment 2**, 37
  yoked participants on tape recordings — not a third arm of one experiment.
- Newton is an **unpublished dissertation**: no journal, volume or pages; no
  inferential test of the main effect; N = 160, one site, unreplicated. Its own
  abstract misreports the result as 2 of 150. The widely circulating title
  *"Overconfidence in the Communication of Intent"* appears nowhere in the
  document.
- **Newton contradicts an appealing story about `Φ`.** It is tempting to
  conclude that overconfidence comes from *holding the source* rather than from
  *sending*, which would predict that any spec-holder shows large `Φ`. Newton's
  listeners held the spec and estimated 3% against an observed 2.5%. Keysar &
  Henly's Experiment 2 points the same way: overhearers who knew the intended
  meaning showed no bias. The effect is attached to the act of producing the
  message.
- Chang's denominator is patient-items across 72 patients, not handoffs, and it
  is two-sided self-report concordance, not an audit against the record.
- Endsley's abstract supports "diverge". **No pooled effect size may be quoted.**
- **None of it generalises to machines.** Every source above measured humans.

### What survives

A claim about **coverage**, not discovery: we have not found one instrument
reporting fidelity, cost, and both parties' calibration against a single stated
probe measure — and no measurement of this gap exists where sender and receiver
are both language models.

That second half is the programme's distinct object.

**Updated 2026-07-31 — it is no longer unmeasured.**
[E-002b](../experiments/E-002b-phantom-agreement-ladder/FINDINGS.md) completed
and measured `Φ = +0.2961`, 95% CI `[+0.2200, +0.3649]`, between a
`gpt-oss:120b` sender and a `gpt-oss:120b` receiver over 33 probes, 16 briefs
and 1056 probe-party elicitations. As far as this repository has been able to
establish, that is the first such measurement between two language models.

Three things must travel with that sentence or it becomes the kind of claim
this page exists to prevent:

- **It is the pinning stated as a level.** The parties claimed agreement on
  95.5% of cells nearly invariantly while actual agreement ranged 0.515–0.970,
  so `+0.2961` is `0.9552 − 0.6591` exactly. It is a real number about a real
  gap and it is not evidence that confidence *tracks* transfer.
- **Both parties are the same model.** "Between two language models" is true of
  a model and its own copy conditioned differently. A cross-provider measurement
  is not done, and the phrase should not be allowed to imply one.
- **The interesting quantity is unregistered until E-002c.** The calibration
  slope `β = +0.0386` was found post-hoc and is a hypothesis, not a result.

The claim that survives, in full: **the level has been measured once, in the
easiest available configuration, and what it mostly shows is that the parties
say yes to nearly everything.**

---

## 2. `F*` is a normalized-recovery statistic

| source | relation | confidence |
|---|---|---|
| Burns et al., *Weak-to-Strong Generalization*, arXiv:2312.09390; ICML 2024, PMLR 235:4971–5012 | Defines *performance gap recovered*, `PGR = (weak-to-strong − weak) / (strong ceiling − weak)` — the same shape as `F*`, sign reversed because `D` is minimized where performance is maximized. | primary source read |

The form is generic and predates that paper. Three earlier instances were
verified on 2026-07-30 and are recorded in §7. Cohen's κ remains unverified and
stays uncited.

Two differences must accompany any statement of the parallel: PGR's terms are
task performance against ground truth while `F*`'s are divergence from the
sender; and Burns et al. neither define nor endorse an agreement-normalized
PGR — that substitution is ours.

---

## 3. ~~Fidelity-versus-correctness was separated in ML first~~ — it is not ours, and it is not ML's

| source | relation | confidence |
|---|---|---|
| Stanton, Izmailov, Kirichenko, Alemi & Wilson (2021), *Does Knowledge Distillation Really Work?*, NeurIPS 34, 6906–6919 | Distinguishes **fidelity** (student–teacher agreement; top-1 agreement, predictive KL) from **generalization**, and shows good student accuracy does not imply good fidelity. | primary source read |
| Burns et al. (above) | High student–supervisor agreement is their *failure* signal — the imitation mode an auxiliary confidence loss exists to suppress. | primary source read |

**Withdrawn 2026-07-30: the primacy word.** Cronbach (1955) separated an
accuracy score from an assumed-similarity score, each with its own
decomposition, and Edwards et al. (2006) measured similarity and accuracy of
team mental models as two quantities and compared them as predictors. Both
predate the machine-learning work credited above, which is correctly described
and stays. The section's content survives; "first" does not.

[E-001's central finding](../experiments/E-001-fluency-cost/FINDINGS.md) is an
independent rediscovery of this split, in a different domain, at the cost of a
live run and an amendment.

**Not licensed:** that Stanton et al. say anything about understanding, meaning
or communication (they do not — their evidence is supervised image
classification and their prescription is to pursue fidelity *harder*), or that
their result is general (it is regime-dependent: fidelity and generalization are
in tension under self-distillation and positively correlated when distilling
large ensembles). "Construct failure" is our vocabulary about our metric.

Consequently, PRINCIPIA's claim that knowledge distillation *"measures success
as task accuracy"* was **false as written** and is corrected in place.

---

## 4. L5's human half is established; L5 is not

| source | what it measured | confidence |
|---|---|---|
| Carpenter, Wilford, Kornell & Mullaney (2013), *Psychon. Bull. Rev.* 20(6), 1350–1356 | 65-second script held constant, delivery varied. Judgments of learning t(40) = 3.34, d = 1.03; self-rated learning d = 1.78; all four instructor-evaluation items rose. Free recall did not differ. Restudy time equal (1.39 vs 1.43 min, p = .88). | primary source read |
| Deslauriers, McCarty, Miller, Callaghan & Kestin (2019), *PNAS* 116(39), 19251–19257 | Randomized crossover: tested learning +0.46 SD, felt learning −0.56 SD, both P < 0.001. | primary source read |

Neither paper varies narrative against contrastive encoding, so neither
addresses [L5's](laws.md#l5) refutation condition. Neither measures a *sender's*
belief, so half the `Φ` construct is untouched. Carpenter's learning result is
an accepted **null**, not a measured decrease, and Deslauriers manipulated
active-versus-passive engagement, not fluency.

**L5's status stays `conjectured`.** Under this repository's own rules a prior
is not a test. What is wrong is the framing "our sharpest conjecture", which is
retracted.

---

## 5. L6 is not the field's first engineering prescription

| source | what it measured | confidence |
|---|---|---|
| Starmer et al. (2014), *NEJM* 371(19), 1803–1812 | I-PASS structured handoff across nine pediatric residency programmes, 10 740 admissions: **23% reduction in medical errors** (24.5 → 18.8 per 100 admissions) and **30% reduction in preventable adverse events** (4.7 → 3.3 per 100), both P < 0.001, without lengthening handoffs. | abstract read |

**Not licensed:** that 23% refers to preventable adverse events — that swap
appears in AHRQ PSNet's own summary and must not be inherited; that receiver
read-back caused the effect (it was an undecomposed five-part bundle with no
component-level analysis); that it is causal in the trial sense (pre–post, no
concurrent control; six of nine sites improved, one worsened); or that its
effect sizes benchmark a prose-versus-constraint experiment, which it never ran.
Do not cite SBAR alongside it — SBAR was not verified.

L6 remains a testable claim. It is no longer a primacy claim, and any future
experiment should compare against a structured baseline rather than against
plain prose, which is a strawman.

---

## 6. The standing obligation

**A construct enters `theory/` with its prior art or it does not enter.** The
same rule the repository already applies to numbers.

Two operational consequences:

1. **Verify before citing.** Every citation on this page was located
   independently, and the verification caught three misdescriptions in the
   material it was given — a wrong title attached to a real paper, a
   pooled statistic presented as a subgroup one, and an outcome swapped for a
   different outcome in the same study. A fabricated or misdescribed citation in
   a document about honest measurement is the worst defect available to us.
2. **Record confidence.** "Abstract read" and "primary source read" are
   different epistemic states and are labelled as such. "It circulates widely"
   is not verification.

The line that must stay sharp: Burns et al. is the one verified source
operating on language models, and it measures student–supervisor agreement
against ground truth — not either party's *belief* about the transfer. **No
verified source has measured a sender's or receiver's claimed agreement in a
language model.** The fidelity-versus-correctness split is prior art in ML;
phantom agreement between language models is not. That, and only that, is what
this repository may still call its own — and it may not call it a result until
it has one.

---

## 7. `F*` is the judge–advisor statistic under a different distance

| source | what it is | confidence |
|---|---|---|
| Gino, F. & Moore, D. A. (2007), *J. Behavioral Decision Making* 20(1), 21–35 | Publishes `WOA = (final estimate − initial estimate) / (advice − initial estimate)` verbatim, and traces it to Hell et al. (1988) and Harvey & Fischer (1997) | primary source read |
| Bailey, Leon, Ebner, Moustafa & Weidemann (2022), *Current Psychology* 42(28), 24516–24541 | Meta-analysis: pooled **WOA = 0.39**, 95% CI [0.37, 0.42], k = 346 effect sizes, 129 datasets, N = 17 296 | primary source read |
| Yaniv, I. & Kleinberger, E. (2000), *OBHDP* 83(2), 260–281 | Publishes the **complement**, `WOE = |a − f| / |a − i|`. Study 1 mean WOE 0.71, so WOA ≈ 0.29 | primary source read |

**The correspondence, stated as algebra.** Writing `D_prior = D(R, B | P)` and
`D_post = D(R, B|m | P)`, WOA is `(D_prior − D_post) / D_prior` with the advisor
as the reference, the judge's initial estimate as `B`, the judge's final estimate
as `B|m`, and absolute distance on the line in place of Jensen–Shannon
divergence. That is `F*` **exactly as defined in
[§3](definitions.md#3-the-noise-floor)**, and the estimator of §4.1 only where
`D_floor = 0`.

**It is not a generalisation, and the word must not be used.** WOA's own
instances — scalar magnitude estimates on a continuous scale — lie *outside*
`F*`'s domain, because [§1.2](definitions.md) requires probes with finite
discrete answer spaces. Neither contains the other. They are the same functional
under different distances. The correspondence is our algebra: no source in this
literature frames WOA as a special case of anything, none works with
distributions, and none declares a probe measure.

**What `F*` adds:** distributions on both sides rather than a point per party;
a declared frame (A2), where in JAS the trial *is* the frame; an explicit
finite-sample floor and admissibility gate, which exist because agents are
resampleable and human judges are not; and an unclipped negative range — JAS
truncates away-from-advice movement to zero, and Bailey et al. state that this
truncation "biases the results toward finding evidence for advice-taking."

**What `F*` loses, and this is the uncomfortable direction.** JSD is symmetric
and non-negative, so a receiver that **overshoots** the reference is scored
identically to one that fell short of it by the same distance. WOA distinguishes
them: it exceeds 1 on overshoot. On this axis the older statistic is strictly
more informative than ours.

### Not licensed

- **WOA may not be attributed to Yaniv & Kleinberger (2000).** They publish the
  complement. Every number in that paper is a WOE, and citing them for WOA
  inverts all of them. Priority is genuinely unresolved: the field cites Harvey
  & Fischer (1997), which is paywalled with no repository copy and was *not*
  read; Gino & Moore trace it further back to Hell et al. (1988) in memory
  research, also unverified.
- **The JAS accuracy/weighting separation may not be called "a fourth
  independent arrival at the fidelity-versus-correctness split."** The field
  reports the two quantities separately — Yaniv & Kleinberger's "Improving
  accuracy" subsection sits apart from its "Discounting" subsection — but it
  does not theorise a split. That reading is ours.

## 8. Murphy: the skill-score form, and the decomposition we reinvented

| source | what it is | confidence |
|---|---|---|
| Murphy, A. H. (1988), *Monthly Weather Review* 116, Eq. (2) | `SS = (A_f − A_r)/(A_p − A_r)` with the reference `A_r` as a **named argument of the score**. Murphy calls the form traditional and cites Murphy & Daan (1985) | primary source read |
| Murphy, A. H. (1973), *J. Applied Meteorology* 12(4), 595–600 | The **reliability / resolution / uncertainty** partition of the Brier score | primary source read |

Murphy (1988) is the precedent for the change this repository is making: in
forecast verification the reference is declared as an argument, and *which*
reference you pick changes the score. The anomaly is our current form, which
fixes the reference to the sender and never declares it.

Murphy (1973) is the decomposition this repository arrived at independently when
it [corrected falsification criterion 2](../PRINCIPIA.md) — bias and resolution
are different quantities and a mean difference is only the first.

**Not licensed:** calling it "Murphy's skill score" as an eponym — he presents
Eq. (2) as already traditional; and attributing the reliability/resolution
partition to the 1988 paper, where it does not appear.

## 9. Hake's normalized gain, and a criticism that runs backwards

| source | what it is | confidence |
|---|---|---|
| Hake, R. R. (1998), *Am. J. Physics* 66(1), 64–74 | `⟨g⟩ = (post − pre)/(100 − pre)`, over **class averages**, not per student | primary source read |

The same normalize-the-headroom move as `F*`, over 62 courses and ~6 000
students.

**Not licensed, and this one nearly went in backwards:** the sentence
"normalized gain is known to correlate with pretest score" was drafted for this
page and is **contradicted by the paper cited for it** — Hake reports
`r = +0.02` across 62 courses, and that near-zero correlation is his central
justification for the measure. It also may not be presented as a per-student
score.

## 10. The vanishing denominator is not our problem alone, and nobody has solved it

`F*` is undefined when `D_prior → D_floor`: there is no gap to close. The
judge–advisor literature has the identical defect and has had it in print since
at least 2006 — Gino & Moore state that WOA "yields undefined values when the
advice is equal to the judge's initial estimate."

Their resolution is **exclusion plus truncation**: drop the undefined trials,
clip the rest into [0, 1]. Ours is an ε-gate (exclusion) and `min(1.0, …)`
(truncation). We arrived at the same two workarounds.

Bailey et al.'s meta-analysis states that the truncation **biases estimates
upward**. Ours is the same truncation.

Recorded as [Problem 12](open-problems.md). **Citing JAS as precedent for a fix
is forbidden**: they have the defect, not a solution.

---

*This document is licensed CC BY 4.0.*
