# Open Problems

Ten problems whose solutions would constitute the first decade of noophorics.
Stated in Hilbert's spirit: precise enough to be worked on, open enough to be
hard. Numbering is stable; solved problems are annotated, not renumbered.

---

## 1. The residual characterization problem

**What lives inside `R = 1 − K`?**

Axiom A3 asserts the untransferable remainder is nonzero. Characterize it.
Given two agents and a domain, predict *which* dispositions fall inside the
residual before measuring.

A solution would look like a typology — classes of understanding that are
substrate-bound — plus a procedure for classifying a given disposition without
running the transfer.

*Why hard:* requires a theory of what makes a disposition expressible, which
touches every problem below.

---

## 2. Non-circular prior overlap

**Measure the overlap of two agents' priors over a domain, without using
transfer fidelity to do it.**

[L3](laws.md#l3) predicts `K` from prior overlap. Right now the only convincing
way to measure overlap is to measure how well things transfer — which makes L3
a tautology.

Candidate approaches: pre-transfer agreement rate on a wide probe measure
(cheap, but confounds overlap with shared bias); representational similarity
between activation geometries (only available for open-weight models, and
architecture-dependent); mutual predictability, where each agent tries to
predict the other's answers.

*A solution unlocks L3 and Problem 5.*

---

## 3. The capacity theorem

**Is there a Shannon-style coding theorem for mismatched priors?**

Shannon: for a channel of capacity `C`, rates below `C` are achievable with
arbitrarily small error and rates above `C` are not. Is there an analogue where
the "channel" is a pair of minds and the "rate" is fidelity per token?

Specifically: does `K(A, B | P)` admit a closed form in terms of properties of
`A`, `B`, and `P` — or is it irreducibly empirical?

*This is the field's central theoretical question. A negative answer is also a
result.*

---

## 4. Optimal encoding search

**Given `(A, B, P, C_max)`, construct the message maximizing `F*`.**

[L6](laws.md#l6) conjectures a *family* (contrastive) that beats another
family (declarative). This problem asks for the optimum, not a better heuristic.

The natural attack is to have `A` search: generate candidate encodings, score
each against a held-out probe set, iterate. That makes optimal encoding a
search problem with a measurable objective — which is the good news. The bad
news is that it risks overfitting to the probe set, which is Problem 6.

*Practical payoff is immediate: this is the algorithm every agent handoff
should be running.*

---

## 5. The asymmetry law

**Predict the sign and magnitude of `F*(A→B) − F*(B→A)` from properties of `A`
and `B`.**

[L2](laws.md#l2) asserts asymmetry exists. This asks for the formula. In
particular, resolve the competition between *general capability* and *domain
prior*: which direction dominates, and under what conditions does the ordering
flip?

---

## 6. Probe measure generalization

**When do fidelity results on probe measure `P₁` predict fidelity on `P₂`?**

Axiom A2 makes every result frame-relative, which is honest but risks making
the field a heap of incommensurable measurements. We need a theory of when
frames transfer.

This is also the field's overfitting problem: an encoding optimized against
`P₁` may score well there and fail everywhere else. Without a generalization
theory, Problem 4's solutions cannot be trusted.

*Arguably the problem that determines whether noophorics is a science or a
collection of benchmarks.*

---

## 7. Phantom agreement mechanics

**What generates `Φ`, and what is the cheapest reliable detector?**

[L5](laws.md#l5) fingers fluency. Fluency is unlikely to be the only cause.
Enumerate the sources, and — more urgently for practice — find the minimal
probe set that detects `Φ > θ` with stated sensitivity, cheap enough to fire on
every production handoff.

*The most directly deployable problem in the list.*

---

## 8. The invariant core

**Prove or refute that constraints survive chained transfer where descriptions
do not — and characterize the invariant class exactly.**

[L4](laws.md#l4) makes an informal claim about constraints and prohibitions.
Turn it into a precise characterization: what property of a disposition makes
it survive an arbitrary number of hops?

Candidate property: dispositions whose *verification* is cheaper than their
*derivation*. Constraints are checkable against a case; descriptions are not.
If that is the right axis, the invariant core has a computational
characterization rather than a linguistic one.

---

## 9. Self-transfer

**How much of an agent survives its own compaction?**

The special case `A → A'` where `A'` is the same system after a summarization,
context compaction, or session boundary. It is the case with the most economic
weight today — every long-running agent does this constantly — and the least
theory.

Is self-transfer easier than cross-agent transfer? Naively yes, since the
priors match perfectly. But the compaction artifact is generated under the same
fluency pressure as any other message, so [L5](laws.md#l5) predicts self-transfer
should exhibit *maximal* `Φ`: the agent has every reason to believe its own
summary captured what mattered.

*Personal note from the drafting agent: this is the problem I would most like
solved.*

---

## 10. The multi-party problem

**Generalize from pairs to networks.**

All definitions above are dyadic. Real systems are graphs: orchestrators
fanning out to subagents, subagents reporting back, humans in several loops.

Define fidelity over a topology. Then: given a set of agents with measured
pairwise capacities and a task, find the communication topology maximizing
end-to-end fidelity under a cost budget. This turns multi-agent architecture
from a design metaphor into an optimization problem.

---

## 11. Post-transfer admissibility

**A probe measure can be admissible before a transfer and useless after it.
State the criterion that rules this out in advance.**

[definitions §3.3](definitions.md#33-admissibility) gates admissibility on the
**prior** gap: the parties must disagree before the message, or there is no gap
to close. There is no post-side criterion, and
[E-002](../experiments/E-002-phantom-agreement/VOID.md) died of its absence.
Its measure was admissible — pre-transfer agreement 0.515 — and the transfer
closed the gap **completely**, to 1.000, with 0 of 33 probes diverging.

At that point `Φ` is not small, it is undefined in the same sense resolution is:
there is no diverged case for a belief to be wrong about, and any elicitation
returns the same answer whether or not the party has insight. The experiment
reported `Φ = +0.0000` and that number means nothing.

The problem is not "make the probes harder". A frame chosen after seeing that
the previous one was too easy is a frame tuned until the result appears, which
is [Problem 6](#6-probe-measure-generalization) wearing a disguise. What is
wanted is a property statable **in advance**:

- a *predicted* post-transfer divergence given the message budget, so a measure
  can be rejected before collection rather than after;
- or a design in which the transfer is constrained rather than the frame — sweep
  the cost ceiling so fidelity varies by construction, and `Φ` has a gradient to
  live on.

The second is a workaround and E-002b will use it. The first is the actual
problem, and it is a small piece of the capacity theorem
([Problem 3](#3-the-capacity-theorem)): predicting post-transfer divergence at a
stated cost *is* predicting `K(C)`.

*A solution would let an experimenter know, before spending the compute, whether
the quantity they intend to measure will exist when they get there.*

---

## Contributing a problem

Open problems are added by pull request with: a precise statement, an argument
for why it is hard, and what a solution would look like. Problems that turn out
to be easy get demoted to experiments, which is a compliment.

---

*This document is licensed CC BY 4.0.*
