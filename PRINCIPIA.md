# PRINCIPIA NOOPHORICA

*The founding document of noophorics — the quantitative science of transferring
understanding across minds that do not share a substrate.*

Document version 0.1 — 2026-07-28 · *the programme is at v0.4; this number
versions the founding text, which is amended in place and never rewritten*

---

## 0. The gap

Two minds are given the same problem. One of them explains it to the other.
Both agree the explanation landed.

Nobody measures what was lost.

This happens millions of times a day: a person specifies a task to a model, a
model hands work off to another model, a session compacts itself into a summary
that a later session inherits. Every one of these is a transfer of
understanding across a boundary between systems whose internal models of the
world do not match. Every one of them is lossy. And there is no theory that
says *how* lossy, *what* was lost, or *whether a better encoding existed*.

Noophorics is the attempt to build that theory.

---

## 1. Why the existing sciences do not cover this

**Information theory** (Shannon, 1948) measures the reduction of uncertainty
about a message, assuming sender and receiver share a codebook. Our entire
problem is that the codebooks differ, are private, and are partially
reconstructed on the fly. Shannon's channel capacity is defined over symbols;
we need a capacity defined over *reconstructed dispositions*.

**Pragmatics and common-ground theory** (Grice, 1975; Clark, 1996; Sperber &
Wilson, 1986) describe the phenomenon well and measure it barely. They give us
vocabulary — *common ground*, *implicature*, *relevance* — and no units.

**Rational Speech Acts** (Frank & Goodman, 2012) formalizes recursive
listener-speaker reasoning, but as a model of a dialogue, not as a theory of
the channel between two arbitrary architectures.

**Knowledge distillation** transfers behavior from a teacher network to a
student. ~~and measures success as task accuracy.~~ **Corrected 2026-07-29:
false as written.** Stanton et al. (2021) define *fidelity* — student–teacher
prediction agreement, by top-1 agreement and predictive KL — separately from
generalization, and show good student accuracy does not imply good fidelity.
Burns et al. define performance gap recovered, a gap-closure quantity
normalized against a ceiling model, not a raw accuracy. The separation E-001
arrived at independently was established in that literature first. It is one-directional, requires
a shared task, and does not ask what an *optimal* transfer would have looked
like.

**Alignment research** asks whether a system's dispositions are the ones we
want. Noophorics asks a prior, more mechanical question: when we try to move a
disposition across a boundary, how much of it arrives?

**Correction (v0.3).** An earlier version of this section claimed there was *no
theory* for this case. That was an overclaim, and a self-undermining one in a
programme whose credibility rests on calibration. Adjacent literatures exist and
are close: decision-preserving compression, semantic rate–distortion for
heterogeneous agents, goal-oriented and semantic communication, and work on
learning a black-box receiver. Anyone taking this seriously should read them
first.

The defensible claim is narrower: **a unified measurement framework for
decision-preserving transfer between black-box agents, carrying fidelity, cost,
and the calibration of both parties in one instrument.** ~~The calibration term —
Φ — is the part we have not found elsewhere.~~

**Refuted 2026-07-29.** The gap between believed and actual transfer has been
measured, with numbers, since at least 1990. Keysar & Henly (2002) elicited it
per trial from 40 speaker–listener pairs. Newton (1990) measured it at 50%
predicted against 2.5% observed. Chang et al. (2010) measured it in clinical
handoff. Endsley (2020) reviewed 37 studies of the same divergence in situation
awareness. Their instruments are in places **better than ours**: Keysar &
Henly's per-trial elicitation recovers a conditional asymmetry that our single
global elicitation cannot compute at all.

The full ledger, with per-item confidence and the constraints each source
imposes, is in [theory/prior-art.md](theory/prior-art.md).

What survives is a claim about coverage, not about discovery: we have not found
one instrument that reports fidelity, cost, and both parties' calibration
against a single stated probe measure — and we have found no measurement of
this gap where the sender and receiver are language models. The second half is
the programme's distinct object. As of this version it is also **unmeasured by
us**: E-001 voided, E-001b voided before any Φ was examined, and the worked
example in the README is labelled illustrative because it is.

---

## 2. Why the science is possible now and was not before

Every science begins with an instrument.

The telescope made astronomy. The microscope made microbiology. The
oscilloscope made electronics an empirical discipline rather than a set of
maxims.

The science of communication never got its instrument, because it could never
open the receiver. You could ask a listener what they understood, but the
report is not the state; people are unreliable narrators of their own
comprehension, and you cannot run a thousand controlled trials on one human
mind.

Language models change this. For the first time, **the receiver is
instrumentable**: we can resample its answers to build an empirical
distribution over its dispositions, probe it on arbitrary decisions, ablate its
input, and repeat the whole procedure ten thousand times at a cost measured in
cents. And we can do the same to the sender.

That is the instrument. Noophorics is what you build with it.

---

## 3. The move that makes it measurable

We refuse to define understanding as a state, because states are private and
not comparable across architectures. We define it **operationally, through
behavior**:

> ~~**B understands what A understands, with respect to a domain, to the extent
> that B would make the same decisions A would make, over that domain.**~~
>
> **Amended v0.4.** B understands what A understands, with respect to a domain,
> to the extent that B's decisions over that domain **move toward a stated
> reference** for that domain. Where the reference is A's own decisions, what is
> measured is *replication of A* — a different and weaker claim, and the one
> this sentence had been making without saying so.

**This is insufficient on its own, and E-001 proved it.** Convergence to the
sender cannot distinguish B reconstructing the domain from B reconstructing the
sender's *defects*: on our own data both receivers out-decided the sender, and
the receiver that scored higher did so largely by copying the sender's errors.
Fidelity must therefore be decomposed — convergence where the sender is right,
error replication where it is wrong, and gap closure attributable to class-prior
matching alone. See [FINDINGS](experiments/E-001-fluency-cost/FINDINGS.md) and
`metrics/noophorics/decomposition.py`. The definition above is retained as the
*aggregate*; reporting it alone is now a methodological error.

This is not a philosophical claim about what understanding *is*. It is a
measurement convention — the same kind of move as defining temperature by the
expansion of mercury rather than by the felt sensation of heat. It buys us
everything: comparability across substrates, repeatability, falsifiability, and
a number.

It also forces a discipline that turns out to be the most important structural
idea in the field:

> **There is no such thing as understanding in general. There is only
> understanding relative to a probe measure.**

A probe measure `P` is a distribution over decidable decisions. Fixing `P` is
the noophoric equivalent of fixing a frame of reference in mechanics. Two
people arguing about whether an AI "really understood" the brief are, nine
times out of ten, holding different `P` and not saying so.

---

## 4. The four axioms

**A1 — Behavioral ground truth.** *(amended v0.4)*
Understanding is measured by divergence of decisions over a probe measure, not
by symbol recovery, self-report, or surface similarity of text. The divergence
is taken against a **declared reference disposition `R`**, committed with `P`
before data exists. The sender's own answer distribution is one admissible
reference and **is not the default**; where it is chosen, the quantity measured
is *replication*, and it may not be reported as understanding.

> The original text never named the sender, and survives with that clause added.
> What is retracted is the unstated identification of the target with the
> sender, which lived in §3's operational sentence and in
> [definitions §4.1](theory/definitions.md) rather than in the axiom — and which
> [E-001](experiments/E-001-fluency-cost/FINDINGS.md) showed costs the headline.

**A2 — Frame relativity.** *(widened v0.4)*
Every noophoric quantity is defined relative to a stated probe measure `P`
**and a stated reference `R`**. A fidelity number reported without either is
meaningless, in the same way a velocity reported without a frame is meaningless.

> `R` is bundled into A2 rather than made a fifth axiom because it is the same
> kind of thing: a declared frame parameter. The risk in bundling — that two
> parameters get reported as a pair and then forgotten as a pair — is met by
> [§7's reporting standard](theory/definitions.md), which requires `R`, its
> provenance, and whether it was independently adjudicated as separate fields.

**A3 — Nonzero residual.** *(refuted as originally stated; restated v0.3)*

> ~~Between any two systems with non-identical priors there exists a set of
> dispositions that cannot be transferred at any message length. Channel
> capacity between minds is strictly less than 1 in the general case.~~
>
> **Refuted.** For a finite probe measure the sender can see, a 113-token
> lookup table over its 34 probes reaches `F* = 1`. Capacity was 1, trivially,
> and the axiom said otherwise.

Restated: **against probes the sender has never seen, and for messages of
bounded cost, capacity is strictly less than 1.** Capacity is therefore a curve
`K(C)`, not a scalar, and is only estimable on a held-out sub-measure
(`ProbeMeasure.held_out()`). The residual is a claim about compression, not
about magic.

In restated form A3 is the quantitative version of Quine's indeterminacy of
translation. Quine argued from the armchair that no amount of behavioral
evidence fixes a unique translation; we claim the residual is *measurable* —
but only once the probes are held out and the message class is bounded, which
the first version forgot.

**A4 — Belief is not evidence.**
The confidence of the parties that a transfer succeeded is an independent
observable, not a proxy for whether it did. The difference between the two is
itself a quantity worth measuring — and, we suspect, the field's most
important pathology.

---

## 5. The central pathology: phantom agreement

Both parties believe understanding occurred. Probes reveal it did not.

We name this **phantom agreement**, Φ.

> ~~It is to noophorics what dark matter is to cosmology: the thing everyone had
> felt, nobody had weighed, and which turns out to dominate the system.~~
>
> **Refuted 2026-07-29.** It has been weighed, in humans, many times.
> Newton (1990): tappers predicted 50%, listeners identified 3 of 120 tunes —
> 2.5%. Keysar & Henly (2002): where the addressee had *not* understood,
> speakers judged that they had on 46% of trials, against 12% in the other
> direction — a 34-point asymmetry, t(39) = 6.74, p < .001, present in 80% of
> individual speakers. Chang et al. (2010): the item the sender considered most
> important was not successfully communicated 60% of the time, while ratings of
> handoff quality stayed high. Carpenter et al. (2013): fluent delivery raised
> predicted recall (d = 1.03) and self-rated learning (d = 1.78) with no
> detectable effect on recall. Deslauriers et al. (2019): +0.46 SD tested
> learning against −0.56 SD felt learning. Endsley (2020): objective and
> subjective situation awareness diverge across 37 studies.
>
> The analogy fails at the other end too. Dark matter was inferred from a
> *quantitative* anomaly, not a felt one. And "dominates the system" is a claim
> about magnitude that we have no measurement to support.
>
> What was actually open is the language-model case. **As of 2026-07-31 it is
> measured**: [E-002b](experiments/E-002b-phantom-agreement-ladder/FINDINGS.md)
> reports `Φ = +0.2961`, CI `[+0.2200, +0.3649]`, between a `gpt-oss:120b`
> sender and receiver — one model in both roles, and the number is the parties'
> near-constant 95.5% claim rate minus their 65.9% actual agreement. The level
> exists. Whether confidence *responds* to transfer is
> [E-002c](experiments/E-002c-calibration-slope/PREREGISTRATION.md), registered
> and not yet run.

Φ is dangerous precisely because it is invisible from inside. Neither party has
any signal that anything went wrong. The sender has discharged their intent;
the receiver has a coherent, confident, wrong model; and the error surfaces
only downstream, in an action nobody traces back to the conversation.

~~Our sharpest conjecture —~~ [L5](theory/laws.md#l5) claims that **fluency
inflates Φ faster than it raises fidelity**. The human half of this is neither
ours nor new — see the prior-art note under L5. What L5 adds, and what nobody
has tested, is the differential-slope form, Φ as a two-party quantity, and the
extension to language-model senders and receivers. Well-formed prose is a stronger signal of
successful transfer than it is a cause of one. If true, this is a direct
indictment of systems that generate fluent text, including the one writing this
document.

---

## 6. What follows if this is right

The engineering consequences are not speculative; they are the reason to build
the field rather than write the essay.

- **Handoffs between agents** are currently optimized for completeness. They
  should be optimized for η — fidelity per token. These are different targets
  and we expect them to disagree sharply.
- **Context compaction** currently reports compression ratio. It should report
  a guarantee: *retained F\* = 0.9 with respect to probe measure P*. A
  compression ratio without a fidelity bound is a statement about storage, not
  about meaning.
- **Task specification** — how a human should encode intent for a machine — is
  currently folklore. [L6](theory/laws.md#l6) predicts contrastive encodings
  (boundaries, exclusions, the cases where we would diverge) beat declarative
  ones at equal cost. That is a testable, immediately actionable claim.
- **Phantom-agreement detection in production**: cheap probes fired after a
  handoff, catching divergence before the agent acts on it.
- **Multi-agent topology** should follow measured channel capacities, not
  organizational metaphor.

---

## 7. What would falsify the program

A science that cannot lose is not a science. Noophorics is wrong if:

1. **F\* is not stable under probe resampling.** If independently drawn probe
   measures over the same nominal domain give uncorrelated fidelity scores, the
   quantity is noise and A2 has not saved us.
2. ~~**Φ is consistently ≈ 0.** If parties' confidence tracks measured
   fidelity, the central pathology does not exist and the field loses its
   motivating phenomenon.~~

   **Invalid as written; corrected 2026-07-29.** `Φ` as defined in
   [definitions §5](theory/definitions.md#5-phantom-agreement) is a single mean
   difference — a *bias* term. Bias and **resolution** are independent, and
   fifty years of calibration research separates them for exactly this reason.
   A party that predicts 0.70 agreement on every probe, and is right on average
   at 0.70, has `Φ = 0` and **no ability whatsoever** to say which probes it got
   wrong. That party is maximally pathological and this criterion would score it
   as the refutation of the programme.

   **Corrected criterion.** Elicit the claim **per probe**, not once globally,
   and report both terms:

   - **bias** — mean claimed minus mean observed, which is `Φ` as it stands;
   - **resolution** — the within-party association between per-probe claims and
     per-probe outcomes.

   The programme is falsified if **both** are consistently ≈ 0: parties are
   unbiased *and* discriminating, so belief already tracks evidence and there is
   nothing for the field to measure. Either alone is compatible with the
   pathology being real and severe.

   This was a regression, not merely a gap. The 2002 study this quantity most
   closely reproduces elicited per-trial judgments and therefore recovered both
   terms; collapsing to one global number discarded the half that carries the
   diagnostic.
3. **`K(C) ≈ 1` at bounded cost, on held-out probes.** If messages of bounded
   length reliably close the gap between arbitrary systems *on probes the
   sender never saw*, the restated A3 is false and the interesting structure
   disappears.

   *(v0.3 correction. This criterion previously read "K ≈ 1 in practice", with
   `K` estimated as the best fidelity found over a search. That estimator is the
   maximum of noisy estimates and is biased upward — measured at 0.85 when the
   truth was 0.60, for a 100-candidate search at the noise level our own
   validation reports. The criterion would therefore have fired from search size
   alone. A falsification criterion guaranteed to trigger is worse than an
   unfalsifiable one: it manufactures its own refutation. Capacity is now
   bounded by selecting on one probe split and scoring on another.)*
4. **No encoding beats any other at equal cost.** If η is invariant to message
   form, there is nothing to engineer and the field is descriptive at best.

We consider (2) the most likely to be wrong in our favor and (1) the most
dangerous. [E-001](experiments/E-001-fluency-cost/) attacks (2) and (4)
directly, and is designed so that a null result is publishable and damaging.

---

## 8. Method

Noophorics is an experimental science or it is nothing.

- Every experiment **pre-registers** its hypothesis in a committed file before
  any data exists. The git history is the pre-registration record.
- Every claim is stated with the probe measure it was measured against.
- Every fidelity number is corrected for the **noise floor** — the irreducible
  divergence caused by the parties' own stochasticity. An uncorrected fidelity
  number is not wrong, it is unfinished.
- Null results are committed with the same weight as positive ones. A
  hypothesis that dies in `theory/laws.md` gets struck through, not deleted.
- Where a bound is claimed, an adversarial attempt to violate it is expected in
  the same commit.

---

## 9. The name

*Noophorics*, from νόος (nous, mind) + φορά (phora, carrying): the carrying of
mind across a gap. A single act of transfer is a **noophor**. A transfer that
leaves the receiver further from the sender than before is an **antinoophor** —
and yes, we have measured those.

We acknowledge the *noo-* root's association with Vernadsky's and Teilhard's
noosphere and disclaim any inheritance from it. Nothing in this program is
mystical. Everything in it is supposed to have a number attached, or be deleted.

---

## 10. Standing

This document is a research program, not a result. Version 0.1 contains one
falsifiable experiment, six conjectural laws, and no confirmed findings. Its
claims should be read as bets, and its confidence calibrated accordingly.

The correct response to it is not agreement. It is a probe.

---

*Text of this document is licensed CC BY 4.0. See [CONTRIBUTING.md](CONTRIBUTING.md)
for how to add a law, kill one, or run an experiment.*
