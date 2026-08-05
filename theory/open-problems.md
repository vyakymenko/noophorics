# Open Problems

Ten problems whose solutions would constitute the first decade of noophorics.
Stated in Hilbert's spirit: precise enough to be worked on, open enough to be
hard. Numbering is stable; solved problems are annotated, not renumbered.

---

## 1. The residual characterization problem

**What lives inside `U = 1 − K_R`?**

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

## 12. The vanishing denominator

**`F*` is undefined as `D_prior → D_floor`. Nobody has solved this, including
the field that has had it since the 1990s.**

Fidelity normalizes by the gap available to close. When sender and receiver
already agree, there is no gap, the denominator collapses, and the quantity is
undefined rather than large. [§3.3](definitions.md#33-admissibility) handles it
by refusing to measure — an ε-gate — and [`fidelity.py`](../metrics/noophorics/fidelity.py)
caps the result at 1 above.

**This is not our problem alone.** The judge–advisor statistic `WOA =
(final − initial)/(advice − initial)` is the same functional
([prior-art §7](prior-art.md)), and Gino & Moore (2007) state the identical
defect in print: WOA "yields undefined values when the advice is equal to the
judge's initial estimate." Their field's resolution is **exclusion plus
truncation** — drop the undefined trials, clip the rest into [0, 1].

We arrived at exactly those two workarounds independently, and their meta-analysis
([Bailey et al. 2022](prior-art.md), N = 17 296) reports that the truncation
**biases estimates upward**. Our `min(1.0, …)` is the same truncation, so our
numbers carry the same bias, in the same direction, for the same reason.

Two things are wanted and neither exists:

- an estimator that degrades continuously as the gap shrinks, rather than one
  that is fine until it is undefined;
- a principled account of what should be reported when two parties agree before
  the transfer — which is not "nothing happened", because a message can still
  move a receiver *away*, and an antinoophor on a zero-gap measure is currently
  inexpressible.

This is the pre-transfer twin of [Problem 11](#11-post-transfer-admissibility).
Together they say the quantity is well-behaved only in the middle of its range,
and the theory currently gates both ends by declining to measure.

*Citing the judge–advisor literature as precedent for a **fix** is forbidden:
they have the defect, not a solution.*

---

## Contributing a problem

Open problems are added by pull request with: a precise statement, an argument
for why it is hard, and what a solution would look like. Problems that turn out
to be easy get demoted to experiments, which is a compliment.

## 13. A hypothesis's reported statistic and its tested statistic are not checked against each other

Three times now a claim in this repository has carried an interval computed from
one quantity and a p-value computed from another.

- [E-002b's H4](../experiments/E-002b-phantom-agreement-ladder/FINDINGS.md): a
  paired interval and an unpaired test, which reported a supported hypothesis as
  unsupported.
- [E-002c's H3](../experiments/E-002c-calibration-slope/FINDINGS.md): a slope
  difference with its bootstrap interval, and a p-value from a difference of
  *levels* — a quantity the same analysis plan excludes from the hypothesis
  family.
- The same file's H1 could not print as supported at all, because the summary
  gated the verdict on a p-value the hypothesis is registered not to have.

The third was caught by executing the analysis path; the first two were caught
by reading, after publication, by the person who wrote them. Vigilance did not
work: E-002c's defect sits three lines below a comment naming E-002b's defect.

**The problem.** State a machine-checkable relation between a reported effect
and the test that licenses it, strong enough to catch these and weak enough not
to forbid legitimate designs — an interval decision with no p-value is
legitimate and registered here, so "every effect must have a p-value" is the
wrong rule. A candidate: require every effect to name the array its statistic
was computed from, and fail when the effect's value and its p-value do not
derive from the same array. Whether that is expressible without rewriting every
runner is the open part.

**Why it is not a tooling ticket.** The three instances differ in mechanism and
agree in shape, which is what a defect *class* looks like. Naming the class is
theory work: it is a statement about what makes a measurement report internally
coherent, and this programme has no such statement.


## 14. When is a modal answer over `n` draws a stable observable?

Every experiment in this programme reduces a probe to one answer by taking the
mode of `n` draws, and then treats that answer as the thing measured. Nothing
states when that reduction is licensed.

[E-004](../experiments/E-004-disagreement-detector/VOID.md) shows the failure
concretely. Of eleven errors, eight were unanimous or nearly so — on two of them
the correct answer was never drawn in sixteen attempts. The other three were
near-ties: on `T21` the wrong answer took the modal slot **six votes to five**.
Those three probes are in the error set because of one draw. A different sixteen
would have given a different error set, a different flag set, and a different
p-value, and nothing in the design would have shown it.

The reduction is doing two incompatible jobs. Where the distribution is
concentrated it recovers a disposition. Where it is flat it manufactures one,
and the manufactured answer then enters the analysis indistinguishable from the
recovered ones.

**The problem.** State the condition under which a modal answer is a measurement
rather than a coin-flip, in a form an experiment can gate on before analysis.
Candidates, none obviously right: a minimum margin between first and second
place; a minimum concentration of the whole distribution; abstention where
neither holds, with abstained probes reported rather than dropped. Each changes
what "the agent's answer" means, which is why this is theory rather than a
threshold to pick.

**Why it is not solved by more draws.** More draws sharpen the estimate of a
distribution that may genuinely be near-uniform. If an agent is truly split
between two readings of a rule, no `n` makes the mode meaningful — and that
agent is arguably the most interesting case, since a split reading is exactly
what a probe measure ought to detect. Reporting it as one answer discards the
finding.

---

## 15. `Φ` has no belief component where the manipulation has to live

**Raised 2026-08-04, from files already committed, at no measurement cost.**

`Φ` is defined as claimed agreement minus observed agreement, and is read as a
belief quantity — the gap between what the parties think transferred and what
did. On the instrument this programme actually uses, it is not one.

Recomputed from
[E-002c's results](../experiments/E-002c-calibration-slope/results/E-002c-20260803T121500Z.json),
24 briefs, `gpt-oss:120b` in both roles:

```
claimed agreement, sender    mean 0.9752   sd 0.0357
observed agreement           mean 0.7475   sd 0.1591
corr(Φ_sender, −observed)          +0.977
var(claimed) / var(Φ_sender)        0.046
```

**Under five per cent of `Φ`'s variance is belief.** The claim sits against its
ceiling and barely moves, so `Φ` is the observed agreement rate with a minus
sign. This is the same pinning [E-002c §4](../experiments/E-002c-calibration-slope/FINDINGS.md)
reports as an asymmetry between the parties; what is new here is the
consequence for anything stated *on the level of* `Φ`.

And the observed rate is itself a function of message length:

| rung | brief words | observed | `Φ` sender |
|---|---|---|---|
| 30 | 29–35 | 0.631 | 0.326 |
| 70 | 64–84 | 0.692 | 0.290 |
| 110 | 118–166 | 0.778 | 0.217 |
| 150 | 162–182 | 0.889 | **0.078** |

`Φ` falls 0.192 per 100 words and observed agreement rises 0.203 per 100 words,
monotonically across every rung. By 182 words — the longest brief this programme
has ever measured — `Φ` is 0.078 and the probe measure is nearly saturated.

**Why this is a problem and not a parameter.** [L5](laws.md#l5) says fluency
raises `Φ` faster than it raises `F*`. Its prediction is *"`Φ` up, transfer
flat."* But if the claim is pinned, `Φ` can only rise when observed agreement
**falls** — so on this instrument the one outcome L5 names as its confirmation
is close to arithmetically unavailable, and the only route to a positive `ΔΦ`
is fluency *reducing* transfer, which refutes L5's sharp half rather than
supporting it.

The fluency line cannot step around this by choosing shorter messages.
[E-001c](../experiments/E-001c-fluency-length-controlled/VOID.md) measured the
fluent register's floor at 229–232 words in this generator — **47 words past the
longest brief on which any of this was ever measured**, in the direction where
observed agreement is climbing into its ceiling. Three experiments have now been
designed to detect a fluency effect on `Φ` at lengths where `Φ` is collapsing,
and none of them noticed, because all three voided during composition and the
sweep in that line has never run.

### Measured, 2026-08-04: the ceiling is where the extrapolation put it

The paragraphs above were an extrapolation from a ladder that stopped at 182
words. [`headroom_check.py`](../experiments/E-001c-fluency-length-controlled/headroom_check.py)
ran the draws out at the operating point, on six messages that already existed
on disk — three fluent and three terse, 221–233 words, so the contrast is
**length-matched** — against `MERIDIAN-34`, `n = 10`:

| register | words | `Â` | diverged probes of 34 |
|---|---|---|---|
| fluent | 232, 233, 233 | **0.951** | 1, 3, 1 |
| terse | 232, 224, 221 | **0.941** | 1, 2, 3 |

The whole between-register difference is `0.0098` — **one third of one probe.**

It is not an artifact of the modal reduction, which [Problem 14](#14-when-is-a-modal-answer-over-n-draws-a-stable-observable)
would otherwise put in doubt: the sender's 34 probes are unanimous at 10/10 with
a minimum margin of 10, and 90% of all receiver probe-columns are unanimous too.
These are concentrated dispositions, not coin-flips.

**Four of the six messages fall below E-002c's own outcome-variation gate**,
which wants at least 3 diverged probes. So the successor design does not merely
lose power out here — the gate that exists to catch exactly this would void the
run.

Two things follow, and the second is the one that costs.

**The probe measure is saturated at the length the fluent register requires.**
`MERIDIAN-34` is answered correctly from any competent 230-word brief in either
register. The E-001 line's successor is therefore **a different probe measure,
not a different prompt** — which contradicts what
[E-001c's VOID](../experiments/E-001c-fluency-length-controlled/VOID.md) says its
own §8 named, and that document should be read with this beside it.

**And this measurement cannot be read as evidence for L5's predicted null.** It
is tempting: a length-matched register contrast showing fluent and terse
transferring within a third of a probe of each other looks like "fluency does not
buy understanding," which is L5's H4. It is not. At saturation everything looks
identical, and nothing here can separate *fluency does not help* from *the
instrument cannot tell*. The six messages were also chosen after their lengths
were known. This is instrument data and it stays instrument data.

### What survives saturation, and what that specifies

Not every probe dies at 230 words. Six of the 34 still diverged on at least one
of the six messages, and they are not a random six.

**Every one of them is tagged `interaction`.**

| | still diverges at 230 words |
|---|---|
| `interaction`-tagged | **6 of 9** |
| everything else | **0 of 25** |

Fisher exact `p = 6.25e-05`. Across 150 probe-message pairs on non-interaction
probes there were **zero** divergences. The surviving probes are `M25`, `M33`,
`M19`, `M26`, `M34`, `M14`; `boundary` contributes 0 of 10 and `override` 0 of 3.

It replicates on an independent instrument. On [E-002c's](../experiments/E-002c-calibration-slope/FINDINGS.md)
brief ladder — a different measure (`MERIDIAN-33`), different messages, a
different experiment — the probes still diverging on the longest briefs are led
by `M25` (5 of 7) and `M14` (4 of 7), and the three probes common to both
datasets are `M14`, `M25`, `M26`. All three are `interaction`.

**And the tag is not a synonym for "cites two rules."** All nine interaction
probes cite two or more rules, but so do seven probes that are not tagged
interaction — and **none of those seven diverges**. Rule count alone gives
`p = 0.006` against the tag's `6.25e-05`. What distinguishes them is that the
answer depends on the rules *combining*, not on both being mentioned. That is a
harder thing to write, and it is also the thing the probe authors' hand-applied
tag turns out to have captured — which is a small independent validation of the
tag.

**The specification this yields.** Interaction probes diverge at **0.204 per
probe per message** at these lengths; everything else at 0.000. So:

| measure | expected diverged per message | expected `Â` |
|---|---|---|
| `MERIDIAN-34` as it stands (9 of 34 interaction) | 1.8 | 0.946 |
| 15 interaction-class probes | 3.1 | — |
| 34 interaction-class probes | 6.9 | **≈ 0.80** |

E-002c's outcome-variation gate wants at least 3 diverged probes. **Fifteen
interaction-class probes clear it; the current measure does not.** Twenty-eight
of `MERIDIAN-34`'s probes never diverged on any of the six messages, so at this
operating point they contribute nothing but ceiling.

**What this extrapolation assumes, and it may not hold.** That new interaction
probes would behave like the nine that exist, which is exactly the kind of
assumption a saturated measure has already falsified once. That probe
divergences are independent, when they plainly cluster on shared rules — `M25`
and `M26` both cite `R10, R3`. That one domain and one model generalise, which
this programme's own limitation sections deny every time. The rate rests on
**11 divergence events**. Treat the table as a target to design against and
measure, not as a prediction.

**What a solution would look like.** Any one of these, and none is obviously
right:

- a probe measure built predominantly of interaction-class probes, per the
  specification above. This is the concrete, boring version and it is probably
  the right one — but writing probes whose answers depend on rules *combining*,
  without making them ambiguous, is the hard part, and
  [Problem 14](#14-when-is-a-modal-answer-over-n-draws-a-stable-observable) is
  what stands in the way: an interaction probe that is merely confusing produces
  a flat distribution, and a flat distribution's modal answer is a coin-flip
  that the analysis cannot distinguish from a disposition;
- a belief quantity that does not subtract the outcome. Claimed agreement
  reported against observed rather than differenced from it, with the
  pinning stated rather than absorbed. `β` ([E-002c](../experiments/E-002c-calibration-slope/FINDINGS.md))
  is a step in this direction and is why that experiment exists;
- a restatement of L5 whose confirmation is reachable on a saturating measure.
  Note that this cannot be chosen *after* seeing which form is satisfiable —
  that is the same error as picking a band because it was measured to work.

**This is the pre-registration twin of [Problem 12](#12-the-vanishing-denominator).**
Problem 12 says `F*` is undefined when there is no gap to close before the
transfer. This says `Φ` is uninformative when there is no gap left after it.
Together they bound the operating range of both of this programme's headline
quantities, from opposite ends, and neither bound has ever been stated as a
precondition an experiment must check before it registers.

---

*This document is licensed CC BY 4.0.*
