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

### Measured, 2026-08-31: the naive answer does not survive

The composer × reader 2×2 on `RIVERSIDE-30`
([results](../probes/riverside-30/RESULTS-selftransfer.md)), predicted before the
deciding arms ran:

| diverged of 30 | read by `gpt-oss` | read by `qwen` |
|---|---|---|
| composed by `gpt-oss` | **10.00** *(self)* | 9.67 *(cross)* |
| composed by `qwen` | 10.33 *(cross)* | **11.33** *(self)* |

`self − cross` across six paired briefs: `−1, +1, +1, 0, +1, +2`, mean **+0.667**,
sign test **`p = 0.375`**. **There is no self-transfer advantage**, and the point
estimate runs the *other* way — a model reads its own compaction slightly worse
than another model reads it, though not significantly so.

So *"naively yes, since the priors match perfectly"* is not supported. The
likeliest reason is on the instrument rather than in the agents: `RIVERSIDE-30`'s
divergence is **probe-attributable** — both readers always-diverge on the same
seven probes, Jaccard 0.654 — so matching composer to reader has little left to
buy.

**The `Φ` half is untouched.** L5's prediction that self-transfer shows *maximal*
phantom agreement needs an elicitation arm this run does not have, and it remains
the unmeasured and more interesting half. Nor is this `A → A'`: it is one model
composing and later reading with no shared state, which is the closest
operationalisation available and not the same thing.

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
| everything else | ~~**0 of 25**~~ **3 of 25** |

Fisher exact `p = 6.25e-05` on the six-message sample. ~~Across 150
probe-message pairs on non-interaction probes there were **zero**
divergences.~~ **Withdrawn 2026-08-04, same day**, by widening the measurement
to all four cells and twelve messages
([`headroom-2x2.json`](../experiments/E-001c-fluency-length-controlled/headroom-2x2.json)):
three non-interaction probes do diverge — `M02` (`R1, boundary`), `M12` (`R4`)
and `M29` (`R6, R1, scope`). The zero was a small-sample artifact and is struck
rather than quietly restated.

What survives the widening is the proportion, not the absolute: **21 of 24
divergence events (88%) are on interaction probes**, which are 9 of 34. And all
three exceptions land on **one** message — cell B, 234 words, which alone
accounts for 5 of the 24 events. One unusual message, not a general effect, but
the claim may no longer be stated as "never".

The recurring survivors are stable across both runs: `M14` (6 of 12), `M19`
(5 of 12), `M33` (5 of 12), `M25` (4 of 12), all interaction.

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

**The specification this yields.** Interaction probes diverge at **0.194 per
probe per message** at these lengths — measured on twelve messages and 21
events, against 0.204 on the first six and 11, so the number the design would be
costed against is stable where the absolute claim above was not. So:

| measure | expected diverged per message | expected `Â` |
|---|---|---|
| `MERIDIAN-34` as it stands (9 of 34 interaction) | 1.7 | 0.949 |
| 16 interaction-class probes | 3.1 | — |
| 34 interaction-class probes | 6.6 | **≈ 0.81** |

### The specification was built, and the projection was twice too generous

[`MERIDIAN-IX16`](../probes/meridian-ix16/) is that measure: sixteen probes, every
one requiring two or more rules to combine, written against the same source
specification and validated on the same six messages.

**The admission gate passed completely.** The rule was declared before the run —
a probe is admitted only if the sender, holding the full specification, returns
the key with a modal margin of at least 8 of 10 — and all **16 of 16** were
admitted, every one unanimous at 10/10. The specification decides all sixteen
cases and the model recovers all sixteen from it. Nothing was cut, so nothing
had to be rewritten.

**The headroom is real and half what was projected.**

| | per-probe divergence rate | diverged per message |
|---|---|---|
| `MERIDIAN-34`, same six messages | 0.049 | 2.0 of 34 |
| `MERIDIAN-IX16` | **0.104** | 1.67 of 16 |

Twice as sensitive per probe. But the projection above said **0.194**, and the
gap is a selection effect I walked into rather than noise:

> 0.194 was measured on the interaction probes that **survived** saturation. That
> survival was the selection. Four probes carried most of the signal, and
> projecting their rate onto probes not yet written assumed the new ones would
> all be like the survivors rather than like the class they were drawn from.

The same shape repeats inside the new measure: **12 of its 16 probes never
discriminated at all.** Ten divergence events sit on four probes — `X11` ("would
be PADDED but also fails R1"), `X06` and `X07` (paired figure limits), and `X16`
(R4's exact boundary inside a pair). Discriminating power concentrates whatever
the measure, which is a fact about the domain and not about either measure's
construction.

**So sixteen probes is not enough after all.** At 0.104, clearing E-002c's
outcome-variation gate of three diverged probes needs **29**, and a 34-probe
measure of this class would expect 3.5 per message. The earlier table said 16 and
was labelled "a target to design against and measure, not a prediction"; it has
now been measured, and the target moves.

### What a brief drops, stated as a rule and then tested

Twelve of the first sixteen discriminated nothing, and the four that did shared a
shape: a **number** whose applicability depends on a **regime** — the paired
figure maximum of 70 against the solo 45, the shared minimum of 8, `R4`'s exact
five years inside a pair — or **verdict precedence**, `R9`'s PADDED losing to any
second failure. What discriminated nothing was categorical: `R7`'s override,
`R6`'s Track D exemption, `R10`'s clock reset.

Sixteen further probes were written to test that rather than to assume it, with
the prediction recorded **per probe, in the probe file**, before any of them ran:

| group | n | rate | fired |
|---|---|---|---|
| predicted **to** discriminate | 12 | **0.181** | 5 of 12 |
| predicted **not** to | 4 | **0.000** | 0 of 4 |

Thirteen events against zero, over 24 probe-message pairs on the second group.
Fisher exact `p = 0.0339`. And the structure is sharper than the rate: **all nine
probes that ever discriminated turn on the paired regime (`R5`, seven of nine) or
on verdict precedence (`R9`, four).** Across 32 probes and six messages, not one
categorical override discriminated.

> A brief keeps a rule *as a rule* and loses the qualifier attached to a number.

That is the design rule the successor needed, and it is now earned rather than
guessed. ~~[`MERIDIAN-IX32`](../probes/meridian-ix16/) reaches **3.33 diverged per
message over 31 admitted probes**, clearing the gate.~~ **Withdrawn the same day
— see below.** The design rule survives; the claim that the measure built on it
clears the gate does not.

### Discriminating power and stable observability are anti-correlated

The admission gate had been applied once. Applied five times — a probe admitted
only if it returns the key at margin ≥ 8 in **every** pass — it rejects four
probes: `X06`, `X17`, `X21`, `X22`.

**All four are among the nine that ever discriminated. None of the twenty-three
that never discriminated was rejected.** Fisher exact `p = 0.0035`.

On the 28 survivors the measure gives **2.00 diverged per message** at a
per-probe rate of **0.071** — still above `MERIDIAN-34`'s 0.049, and **below the
gate of three.** The headroom that appeared to clear it was substantially
borrowed from probes that are not stable observables.

So the repair does not work as stated, and the reason is not a defect in these
sixteen probes:

> At this operating point, a probe that separates a spec-holder from a brief is
> markedly more likely to be one whose own modal answer is unstable.

[Problem 14](#14-when-is-a-modal-answer-over-n-draws-a-stable-observable) is
therefore not a caveat attached to this repair. It is the binding constraint on
it. "Write harder probes" may not be a route to headroom at all, because harder
is where the instability lives — and a measure cannot buy discrimination with
observations it cannot trust.

That leaves the successor needing **both** open problems solved, not one: a probe
class that discriminates, and a reduction that stays meaningful where it does.
Neither this measure nor this programme has the second.

**The admission procedure is defective and the measure records it.** `X06` was
admitted at margin 10/10 in the first validation and cut at 4/10 in the second —
same probe, same model, same specification, the modal answer unchanged and its
stability not. An admission rule applied once is a snapshot, which is
[Problem 14](#14-when-is-a-modal-answer-over-n-draws-a-stable-observable) again
and from a new direction: it is not only the probes that need a stability
criterion, it is the gate that admits them. And the instability landed on a probe
that was discriminating 3 of 6 messages, which is the uncomfortable direction.

The widened run also measured the whole 2×2 for the first time, which the
six-message run could not:

| cell | | words | `Â` | diverged |
|---|---|---|---|---|
| A | fluent · declarative | 308, 251, 250 | 0.971 | 2, 1, 0 |
| B | fluent · contrastive | 237, 235, 234 | 0.941 | 0, 1, 5 |
| C | terse · declarative | 232, 224, 221 | 0.941 | 0, 3, 3 |
| D | terse · contrastive | 225, 225, 223 | 0.912 | 4, 2, 3 |

Contrastive cells sit below declarative ones on both rows, and fluent above
terse on both columns. **Neither ordering may be read as a result.** These
messages carry no register verdicts — `floor_by_register.py` composed them to
measure length and did not rate them — the cells differ in length as well as in
register, `n = 3` per cell, and the whole set was selected after its lengths were
known. It is recorded because a successor's power calculation needs a per-cell
rate and there was none.

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

### It is not one model's quirk. The other local model is worse.

Every limitation section in this programme says one model and nothing
generalises, and the saturation claim above rested on exactly one. So it was run
again on `qwen3.5:35b`, same six messages, same measure, same `n = 10`.

**Fluent arm, three messages at 232–233 words: `Â = 1.000` on all three. Zero
diverged probes of 34.** Against `gpt-oss:120b`'s 0.941–0.971 on the same
messages. The second model does not soften the finding, it removes the last of
the headroom.

The degenerate explanation was checked before the result was believed, because a
receiver that answers everything the same way scores 1.000 for free:

| | answers used | matches the key |
|---|---|---|
| `qwen3.5:35b` sender | `HANDLED` 13, `RETURNED` 18, `PADDED` 3 | **34 of 34** |
| `qwen3.5:35b` receivers (×3) | identical distribution | **34 of 34** each |
| `gpt-oss:120b` sender | identical distribution | **34 of 34** |

Both models use all three options, in the same proportions, and both answer the
whole measure correctly from the source specification. The receivers of the
smaller model then reproduce all thirty-four from a 232-word message.

**But the measure is not trivial in general**, and that distinction matters for
the successor. [PARAMETERS](../experiments/E-001c-fluency-length-controlled/PARAMETERS.md)
records `claude-opus-4-8` at 0.882 with four errors on this same measure, and
[E-004](../experiments/E-004-disagreement-detector/VOID.md) independently put it
at 0.909. `MERIDIAN-34` discriminates *between* models. What it cannot do is
discriminate *within* a model's own sender–receiver pair at 230 words — which is
the only comparison the E-001 line needs.

**The terse arm agrees, and the run then died.** `terse0`, 232 words, came back
at `Â = 1.000` with zero diverged probes and a mean divergence of 0.0031 — the
lowest of the five. So both registers are at ceiling for this model, not only the
fluent one.

Its provenance is worse than the others' and is stated rather than smoothed over:
`terse0`'s numbers survive **in the run log only**. The write that would have
persisted them is the write that failed — a transient `EPERM` on a file that was
writable a second earlier and a second later — and the exception took the process
down after seventeen hours, so `terse1` and `terse2` were never drawn.
[`headroom-qwen.json`](../experiments/E-001c-fluency-length-controlled/headroom-qwen.json)
therefore contains the sender and the three fluent messages, and this paragraph's
figure does not appear in it.

Four messages of six, both registers, every one at `Â = 1.000`. The two missing
messages would have to disagree with all four to change the reading, and the
arithmetic they would have to overturn is a ceiling.

### One candidate repair is now measured and does not work

Before rebuilding a probe measure, the cheaper question is whether the *outcome
statistic* is what saturates. `Â` is the fraction of probes whose **modal**
answers match — a coarse quantity, and one [Problem 14](#14-when-is-a-modal-answer-over-n-draws-a-stable-observable)
governs. Mean Jensen–Shannon divergence reads the whole distribution and needs no
mode at all. If it had range where `Â` has none, the repair would be a line of
analysis rather than sixteen new probes.

It does not. Measured on the same six messages, with the raw draws kept this
time:

| | fluent0 | fluent1 | fluent2 | terse0 | terse1 | terse2 |
|---|---|---|---|---|---|---|
| `Â` | 0.941 | 0.941 | 0.971 | 0.971 | 0.912 | 0.912 |
| mean JSD | 0.0409 | 0.0405 | 0.0290 | 0.0192 | 0.0498 | 0.0563 |

**`corr(JSD, Â) = −0.958`**, and the relative spread of the two is the same to
within a twentieth — 0.95 against 1.00. Divergence is the modal disagreement
count wearing a hat. **The repair is the probe measure, not the statistic.**

What the exercise did establish is that sub-modal information exists and is not
negligible: **27% of total divergence, averaged over messages, comes from probes
whose modes agree** — invisible to `Â` by construction. It is also wildly
uneven, from 0% to 52%, and it runs the opposite way to the modal count: the
better-aligned receivers carry their residual disagreement under the mode, the
worse-aligned ones have it captured by the mode. Real, but not enough to carry a
design.

### And the probes that survive are the ones whose modes are least trustworthy

This is the collision with [Problem 14](#14-when-is-a-modal-answer-over-n-draws-a-stable-observable),
and it qualifies the specification above rather than confirming it.

| | mean modal margin (of 10) | unanimous | margin ≤ 4 |
|---|---|---|---|
| `interaction` probes | 8.53 | 73% | **15.0%** |
| everything else | 9.90 | 98% | 0.8% |
| the four recurring survivors | 7.25 | 52% | **28.8%** |

**43% of all divergence events sit on a receiver margin of 4 or less**, and three
are exact ties. The sender is unanimous on all nine probes that ever diverge, so
the instability is entirely on the receiver's side — which is what an incomplete
transfer ought to look like, and is also exactly what Problem 14 says the modal
reduction cannot be trusted to represent.

Filtering for stability costs most of the signal. Keep only interaction probes
whose mean margin is ≥ 8.5 and six of the nine survive — but they carry **10 of
the 35 divergence events**. Sensitivity and stability trade against each other
directly here.

So "sixteen interaction-class probes" is necessary and not sufficient. Sixteen
probes *like these* would deliver outcome variation of which roughly a third is
a coin-flip the analysis cannot distinguish from a disposition. The open problem
is sharper than it was: **find probes that are hard and concentrated**, or solve
Problem 14 first. `M19`, `M26` and `M34` are the existing proof that the
combination is possible; three of thirty-four is not proof that it is findable at
scale.

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
