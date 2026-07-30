# Conjectural Laws

Six conjectures. **None is established, two have been restated after their
original forms were found defective, and the defects are recorded in place.**
Each law states what would kill it and which experiment attacks it.

| | status |
|---|---|
| L1 | conjectured |
| L2 | conjectured — headline form withdrawn as tautological (v0.3) |
| L3 | conjectured — operationalization blocked on Problem 2 |
| L4 | conjectured — original form withdrawn as ill-typed (v0.3) |
| L5 | conjectured |
| L6 | conjectured |

**Status vocabulary:** `conjectured` (stated, untested) · `supported`
(survived ≥1 pre-registered test) · `contested` (mixed evidence) ·
~~`refuted`~~ (struck through, kept in place, never deleted).

Notation is defined in [definitions.md](definitions.md).

---

> **v0.4 — every law below is stated in `F*`, and `F*` now takes a reference.**
>
> [A2](../PRINCIPIA.md) widened from a stated probe measure `P` to a stated pair
> `(P, R)`. Read every `F*` in this file as `F*_R`, and note that for most of
> these laws the choice of `R` is not cosmetic: it changes what the law claims.
> Where it does, the law says so under its own heading rather than relying on a
> reader to carry this paragraph down the page.

## L1 — Law of diminishing noophoric return

> `F*(C)` is concave in message cost and saturates strictly below 1.

Longer explanations buy progressively less understanding, and the curve
flattens at a ceiling that is not 1. The ceiling is the capacity `K`; the
distance to 1 is the residual `R`.

**Which reference *(v0.4)*.** Any, and the law is unchanged by the choice. L1 is
about the *shape* of `K(C)` — concave, saturating below 1 — and concavity in
cost is a property of the curve, not of what it is measured toward. The
saturation *level* does depend on `R`; the claim that there is one does not.

**Why we expect it.** Early tokens carry the load-bearing structure; later
tokens elaborate what the receiver has already reconstructed. Beyond some
point the message is spending cost re-encoding what the receiver's prior
already supplied.

**Refuted if:** `F*(C)` is linear over a substantial range, or reaches 1.0
(floor-corrected) for arbitrary sender/receiver pairs.

**Status:** `conjectured`
**Attacked by:** planned E-002 (ablation ladder: same message truncated at
8 cost levels, fidelity curve fitted)

---

## L2 — Law of asymmetry

> `F*(A → B) ≠ F*(B → A)`, and the sign of the difference is predictable from
> the asymmetry of the two priors.

Human→model and model→human transfers are not mirror images, and neither are
transfers between two models of different capability or training.

**Why we expect it.** Transfer requires the receiver to *reconstruct*, not
merely to store. A receiver with a richer prior over the domain closes the gap
from fewer bits. Direction therefore matters whenever the priors are unequal —
which is always.

**Sharper form (the interesting version):** the asymmetry is not simply
"toward the more capable model." We expect direction of *domain* prior to
dominate direction of general capability, which would mean a weaker model with
domain grounding receives better than a stronger model without it.

**The headline form is a tautology and is withdrawn as a law.** `F*(A→B) ≠
F*(B→A)` is almost surely true of any two noisy real quantities, and "refuted if
equal within noise" makes its truth a function of statistical power rather than
of the world. Stated that way it could only ever be confirmed.

**What is actually claimed (L2, v0.3):** the *sign* of `F*(A→B) − F*(B→A)` is
predicted by the direction of **domain** prior, and that prediction beats the
direction of **general capability** where the two disagree. That is refutable by
a single pair chosen so the two point opposite ways.

**Which reference, and why it matters here more than anywhere else *(v0.4)*.**
Under the pre-v0.4 convention `F*(A→B)` scored movement toward **A** and
`F*(B→A)` scored movement toward **B**. The two directions had *different
targets*, and the law subtracted one from the other.

That is **not** the defect [L4](#l4) was withdrawn for, and it is worth being
exact rather than tidy. L4 multiplied fractions of two *different prior gaps*.
L2 subtracts fractions of the *same* gap — JSD is symmetric, so
`D(A,B) = D(B,A)` exactly, and both directions normalize by one denominator.
The comparison is coherent. What differs is the target, not the base.

But there are now **two distinct laws** wearing one statement, and they are not
the same claim:

- **L2-replication** — `R = the sender of each direction`. Asks: *who copies
  whom more readily?* This is what the law has meant for three versions.
- **L2-criterion** — `R` shared and sender-independent, e.g. a key. Asks:
  *which direction of briefing produces the more correct receiver?* Both
  directions score against one fixed target.

The **sharper form** — that domain prior beats general capability — is stated
for **L2-criterion**, because "the weaker model with domain grounding receives
better" is a claim about ending up *right*, not about ending up *like the
sender*. Under L2-replication a model that copies its briefer perfectly scores
1.0 whether or not either party understands the domain, which is the mimicry
E-001 measured.

**Refuted if:** across pairs where domain prior and general capability point in
opposite directions, the sign of the asymmetry follows capability, or follows
neither at better than chance.

**Depends on:** [Problem 2](open-problems.md). Without a non-circular measure of
prior overlap, "direction of domain prior" is not independently observable and
L2 remains a promissory note.

**Status:** `conjectured` · *headline form withdrawn as tautological*
**Attacked by:** planned E-003, cross-provider (fidelity matrix over a grid of
sender/receiver pairs, both directions)

---

## L3 — Law of prior overlap

> `K(A, B | P)` increases monotonically with the overlap of the two agents'
> priors over the domain of `P`, and there exists a minimum shared basis below
> which no message length helps.

Below that basis, `F*(C) → 0` for all `C`. You cannot explain color to someone
with no visual system — but L3 claims this is not a binary, it is a curve with
a floor, and the floor is measurable.

**Why it matters.** L3 is the constructive form of axiom A3. A3 says the
residual is nonzero; L3 says its size is a function of something we can vary
and measure.

**The hard part** is measuring prior overlap independently of the fidelity it
is supposed to predict. Circular operationalization is the standing threat to
this law. See [Problem 2](open-problems.md).

**Refuted if:** a non-circular overlap measure exists and fails to predict `K`.

**Status:** `conjectured` · *operationalization incomplete*
**Attacked by:** unassigned — needs Problem 2 solved first

---

## L4 — The curse of the summary <a id="l4"></a>  *(restated v0.3; original was ill-typed)*

> ~~Fidelity is multiplicative along a chain of transfers,
> `F*(A→B→C) ≈ F*(A→B) · F*(B→C)`~~

**Withdrawn as written.** Two defects, both fatal to the statement:

- **Frames.** `F*(A→B)` is a fraction of the A–B prior gap; `F*(B→C)` is a
  fraction of the B–C gap. Multiplying them multiplies two percentages of
  different bases. And `F*(A→C)` was never defined — axiom A2 requires a stated
  probe measure *and pair*, and the composite names a pair whose prior gap
  nobody measured.
- **Sign.** `F*` is unbounded below, so two antinoophors compose to a positive
  product. Measured: hops of `−0.629` and `−1.000` multiply to `+0.629`. Two
  transfers that each left the receiver *further* from the sender are reported
  as a substantially successful chain.

**Restated.** Score every hop against the **origin**, in the origin's frame,
sharing one prior gap and one floor (`metrics/noophorics/chain.py`). Then:

<a id="l4a"></a>**L4a — decay.** Chain fidelity in the origin's frame is non-increasing in hop
count.

<a id="l4b"></a>**L4b — geometric decay.** While fidelity remains positive, `log F*` is
approximately linear in hop count; the chain has a half-life measured in hops.

<a id="l4c"></a>**L4c — the invariant core.** Content expressed as **constraints and
prohibitions** decays measurably more slowly than content expressed as
**descriptions**.

**Which reference *(v0.4)*.** Any, and unchanged. L3 relates capacity to prior
overlap between the two agents; both terms are pairwise and neither is a
target. Note that this is the law [Problem 2](open-problems.md) says is
currently a tautology, and v0.4 does not repair that.

**Which reference *(v0.4)*.** L4 already anticipated this. Its whole restatement
was that every hop must be scored **against the origin, in the origin's frame**,
sharing one prior gap and one floor — which is a declared reference by another
name, fixed before the chain runs. In v0.4 vocabulary: `R = the origin`, and it
is a sender reference, so L4a–L4c are claims about **replication decay**. Whether
*correctness* decays along a chain at the same rate is a separate law nobody has
stated.

**Why we expect it.** Constraints are compact, checkable against a case, and
resist paraphrase; descriptions are none of those. "Never call this endpoint
with a null tenant" survives ten summarizations. "The tenant model is roughly
hierarchical, with some exceptions" does not survive two.

**What changed in what is claimed.** The original also asserted a core surviving
*arbitrarily many* hops. That existence claim is unfalsifiable by any finite
experiment — failure at any observed N only kills the candidate composition,
never the existence. It is dropped. L4c compares two *decay rates*, which a
six-hop chain can refute.

**Refuted if:** chain fidelity is not monotone (L4a); `log F*` is not
approximately linear over the positive range (L4b); or constraint-form and
description-form content show decay slopes that are statistically
indistinguishable (L4c).

**Status:** `conjectured` · *restated after the original was found ill-typed*
**Attacked by:** planned E-004 (six-hop chain, content tagged by form, every hop
scored against the origin)

---

## L5 — Fluency inflates phantom agreement <a id="l5"></a>

> The more fluent and well-organized a message, the more `Φ` rises — and it
> rises faster than `F*` does.

Eloquence increases the *belief* that understanding transferred more than it
increases the transfer.

**Which reference *(v0.4)*.** `Φ` does not take one — it compares a claimed
agreement rate against an observed one, and both are between the two parties.
`F*` does. So L5's "faster than `F*`" clause inherits a reference, and the law
is stated for a **sender-independent** `R`: the worry is that fluency buys
confidence without buying correct decisions. Under `R = sender` the law would
compare rising confidence against rising mimicry, which is a different and less
alarming claim. At equal cost, a polished narrative and a terse list
of boundary cases produce different `Φ` and different `F*`, in opposite
directions.

**Why we expect it.** Fluency is a signal both parties read as comprehension.
The sender feels discharged because the artifact is well-formed; the receiver
feels informed because the artifact is easy to process. Neither of those
feelings is evidence about decisions. Processing fluency is a known source of
misplaced confidence in human cognition; we conjecture it is at least as strong
in systems trained on human text, and possibly stronger, since fluency is
closer to their training objective than accuracy of transfer is.

**This is an indictment of the systems writing most of today's handoffs,
including the one that drafted this document.** That is a reason to test it,
not a reason to soften it.

**Refuted if:** at equal cost, narrative and contrastive encodings produce
statistically indistinguishable `Φ`, or narrative produces *lower* `Φ`.

**Prior art.** The human metacognitive version of this effect has substantial
support and is **not ours**. Carpenter et al. (2013) held a 65-second script
constant and varied delivery only: judgments of learning (t(40) = 3.34,
d = 1.03), self-rated learning (d = 1.78) and all four instructor-evaluation
items rose with fluency; free recall did not differ in either experiment, and
restudy time was equal (1.39 vs 1.43 min, p = .88) — the "at equal cost" clause,
incidentally satisfied. Deslauriers et al. (2019) found tested and felt learning
anticorrelated in a randomized crossover (+0.46 SD, −0.56 SD, both P < 0.001),
with perceived instructor effectiveness (+0.51 SD) displacing instruction type
as the predictor of felt learning.

Neither paper varies narrative against contrastive encoding, so neither
addresses L5's refutation condition. Neither measures a *sender's* belief, so
half the Φ construct is untouched. Carpenter's learning result is an accepted
null, not a measured decrease, and Deslauriers manipulated active versus passive
engagement rather than fluency. L5's untested content is therefore (a) two
positive slopes with different gradients, not one slope and one flat line;
(b) Φ as a two-party quantity; and (c) that any of this holds when sender and
receiver are language models — which no human study can settle. Only (a)–(c)
are what E-001c must establish, and under this repository's own rules a prior
is not a test.

**Status:** `conjectured`
**Attacked by:** [E-001](../experiments/E-001-fluency-cost/) — primary
hypothesis H2

---

## L6 — Optimal encoding is contrastive, not declarative <a id="l6"></a>

> At equal cost, encoding *"the cases where we would diverge"* transfers more
> fidelity than encoding *"what I understand."*

Do not send the model. Send the boundaries of the model.

**Which reference *(v0.4)*.** L6 is stated for a **sender-independent** `R`.
"Encoding the cases where we would diverge transfers more fidelity" is a claim
about the receiver *deciding correctly*, and under `R = sender` it degrades into
a claim about the receiver *answering like the sender* — which a contrastive
brief could satisfy by transmitting the sender's errors more efficiently than a
declarative one. That is not a hypothetical: it is the mechanism
[E-001](../experiments/E-001-fluency-cost/FINDINGS.md) measured, where 62% of
the effect sat on probes the sender got wrong.

**Why we expect it.** The receiver already has a prior. A declarative
description spends cost re-encoding the parts of the sender's model the
receiver would have reconstructed anyway. A contrastive encoding spends cost
only on the delta — precisely the probes where the two agents currently
disagree. Under the definition of `F*`, which measures gap closure and not
information delivered, the contrastive encoding is spending every token on the
numerator.

> ~~This is the field's first engineering prescription, and it directly
> contradicts how nearly every handoff, summary, and spec is written today.~~
>
> **Refuted 2026-07-29.** Structured-handoff prescriptions with mandated content
> slots and a receiver-synthesis step have been deployed and outcome-measured
> since 2014. The I-PASS bundle, evaluated across nine pediatric residency
> programmes and 10,740 admissions, was associated with a **23% reduction in
> medical errors** (24.5 → 18.8 per 100 admissions) and a 30% reduction in
> preventable adverse events (4.7 → 3.3 per 100), both P < 0.001, without
> lengthening handoffs (Starmer et al., *NEJM* 371(19), 2014).
>
> L6 is not first. What L6 claims that I-PASS does not test is the contrast
> itself — I-PASS was compared against unstandardized usual care, not against
> declarative prose at equal cost — and it claims it for machine receivers,
> about which I-PASS says nothing. It remains a testable claim; it is no longer
> a primacy claim.
>
> Three things this citation does **not** license. I-PASS was an undecomposed
> five-part bundle, so receiver read-back is not shown to have caused the
> effect. It was pre–post without a concurrent control, so it is not causal in
> the trial sense — six of nine sites improved significantly and one worsened.
> And its effect sizes are not a benchmark for a prose-versus-constraint
> experiment, because it never ran that contrast.

**Refuted if:** contrastive encodings show `η ≤` declarative encodings at equal
cost, across domains.

**Status:** `conjectured`
**Attacked by:** [E-001](../experiments/E-001-fluency-cost/) — primary
hypothesis H1

---

## Relationships

L5 and L6 are independent claims that E-001 tests jointly, and their
combination is what makes the pair dangerous: if both hold, **the encoding
that transfers best is the one that feels worst**, and every party's
subjective sense of a good handoff is anticorrelated with its quality.

L1 and L3 both concern the ceiling; L1 says it exists, L3 says what sets it.
L2 says the ceiling is direction-dependent. L4 says it compounds.

---

## Adding or killing a law

Laws enter this file only with a stated refutation condition. Laws leave it
never — a refuted law is struck through with a link to the experiment that
killed it, because knowing what is false is the larger part of the record.

See [CONTRIBUTING.md](../CONTRIBUTING.md).

---

*This document is licensed CC BY 4.0.*
