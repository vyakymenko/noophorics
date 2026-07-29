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

That second half is the programme's distinct object, and as of v0.3 it is
**unmeasured by us**. E-001 voided; E-001b voided before any `Φ` was examined.
The repository has never measured `Φ`.

---

## 2. `F*` is a normalized-recovery statistic

| source | relation | confidence |
|---|---|---|
| Burns et al., *Weak-to-Strong Generalization*, arXiv:2312.09390; ICML 2024, PMLR 235:4971–5012 | Defines *performance gap recovered*, `PGR = (weak-to-strong − weak) / (strong ceiling − weak)` — the same shape as `F*`, sign reversed because `D` is minimized where performance is maximized. | primary source read |

The form is generic and predates that paper too. **No priority claim is made
here, and no earlier instance may be cited** until one is verified — several
plausible ancestors (Cohen's κ, Murphy's skill score, Hake's normalized gain)
were named by the review and are *not* verified, so they are not written down as
citations.

Two differences must accompany any statement of the parallel: PGR's terms are
task performance against ground truth while `F*`'s are divergence from the
sender; and Burns et al. neither define nor endorse an agreement-normalized
PGR — that substitution is ours.

---

## 3. Fidelity-versus-correctness was separated in ML first

| source | relation | confidence |
|---|---|---|
| Stanton, Izmailov, Kirichenko, Alemi & Wilson (2021), *Does Knowledge Distillation Really Work?*, NeurIPS 34, 6906–6919 | Distinguishes **fidelity** (student–teacher agreement; top-1 agreement, predictive KL) from **generalization**, and shows good student accuracy does not imply good fidelity. | primary source read |
| Burns et al. (above) | High student–supervisor agreement is their *failure* signal — the imitation mode an auxiliary confidence loss exists to suppress. | primary source read |

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

*This document is licensed CC BY 4.0.*
