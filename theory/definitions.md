# Definitions

Formal definitions of the noophoric quantities. Every symbol used anywhere in
this repository is defined here. Reference implementations live in
[`metrics/noophorics/`](../metrics/noophorics/).

---

## 1. Primitives

### 1.1 Agent

An **agent** `A` is any system that, given a probe, produces a distribution
over answers. We write `A(π)` for that distribution.

We require nothing of the agent's internals. A human, a language model, a
committee, or the same model at a different point in a session are all agents.
An agent is defined entirely by its answer distributions over a probe space.

Crucially, `A(π)` is a *distribution*, not a point. Agents are stochastic, and
treating a single sampled answer as the agent's disposition is the most common
methodological error in this field.

### 1.2 Probe

A **probe** `π` is a decision whose answer depends on the understanding being
transferred, and which is **decidable**: its answer space is finite and
discrete.

Decidability is a methodological commitment, not a convenience. Free-text
answers do not admit a divergence measure that is stable across paraphrase, so
free-form probes must be resolved into a discrete space by a stated rubric
before they enter a measurement. If you cannot say what the possible answers
are, you do not have a probe.

### 1.3 Probe measure

A **probe measure** `P` is a distribution over probes. It is the noophoric
frame of reference: it defines *which* understanding is being measured.

Per axiom [A2](../PRINCIPIA.md#4-the-four-axioms), no noophoric quantity is
defined without one. In practice `P` is a finite probe set with weights,
uniform unless stated.

A probe measure is **admissible** for a transfer `A → B` iff the two agents
actually disagree on it before the transfer (see §3.3). Measuring fidelity on
probes where sender and receiver already agree is measuring nothing.

### 1.4 Noophoric act

A **noophoric act** is a triple `(A, m, B)`: sender `A` emits an artifact `m`;
receiver `B` conditions on `m`, becoming `B|m`.

`m` may be prose, structured data, code, a diagram, or a tool call. The theory
does not privilege any modality — it only measures what arrives.

---

## 2. Divergence

### 2.1 Per-probe divergence

For a single probe, the divergence between two agents is the Jensen–Shannon
divergence between their answer distributions, in bits:

```
d(A, B | π) = JSD( A(π) ‖ B(π) )
```

JSD is chosen over KL for three reasons: it is symmetric (noophoric divergence
should not depend on which agent we call the sender), it is finite for
distributions with disjoint support (agents routinely give answers the other
never gives), and with base-2 logarithms it is bounded in `[0, 1]`, so
per-probe values are directly comparable.

In practice the distributions are estimated from `n` independent samples per
probe. Sample count is a reported parameter, never an implementation detail:
JSD estimated from small `n` is biased upward.

### 2.2 Divergence over a probe measure

```
D(A, B | P) = E_{π ~ P} [ d(A, B | π) ]
```

Bounded in `[0, 1]`. `D = 0` means the agents are behaviorally indistinguishable
over `P`; `D = 1` means they never give the same answer.

### 2.3 Agreement rate

A coarser, more interpretable companion to `D`:

```
Â(A, B | P) = E_{π ~ P} [ 1( mode A(π) = mode B(π) ) ]
```

The fraction of probes on which the agents' modal answers match. `Â` is used
for phantom agreement (§5) because it is the quantity humans and models can
actually estimate about themselves — "what fraction of these would we answer the
same way?" — whereas nobody has calibrated intuitions about expected JSD.

---

## 3. The noise floor

> **v0.3 correction — the floor is estimator bias, not a property of the agents.**
>
> v0.1 called `D_floor` "the irreducible divergence caused by the parties' own
> stochasticity" and put it inside the *definition* of `F*`. That was a category
> error. Two perfectly aligned stochastic agents have **identical true
> distributions**, so their true JSD is exactly zero and `D_self → 0` as
> `n → ∞`. There is no irreducible divergence; there is finite-sample bias in
> the estimator, and nothing else.
>
> The consequence was not cosmetic. Because `D_floor` appeared in the
> definition, the *defined* quantity was a function of sample size — and a
> fidelity that changes when you sample more is not well-posed.
>
> **Corrected architecture.** `F*` is defined over true distributions:
> `F* = (D_prior − D_post) / D_prior`. All floor machinery below is **bias
> correction inside the estimator**, never part of the definition.

### 3.1 Self-divergence (deprecated)

```
D_self(A | P) = E_{π ~ P} [ JSD( A⁽¹⁾(π) ‖ A⁽²⁾(π) ) ]
```

Retained so v0.1 numbers stay recomputable. Do not use it: estimated from
half-sized sample sets, it is inflated relative to the divergences it was
subtracted from — measured at 0.175 versus 0.073 for two identical fair-coin
agents at n=6 versus n=12.

### 3.2 Floor, by permutation null

Pool a probe's draws from both agents, reshuffle into two groups of the
original sizes, and take the expected divergence:

```
D_floor(A, B | P, n) = E_{π ~ P} [ E_perm JSD( shuffle₁ ‖ shuffle₂ ) ]
```

Under the null the two groups come from one distribution, so this is exactly
what a perfectly aligned pair scores — at the same `n`, in the same answer
space, carrying the same estimator bias. Note the explicit `n`: this is a
property of the *measurement*, not of the agents.

**Correcting for it is not optional, and it is not sufficient.** Synthetic
validation shows the corrected estimator still carries ~0.11 of error at n=6.
No floor rescues too few samples; see
[`metrics/validation/synthetic.py`](../metrics/validation/synthetic.py).

### 3.3 Admissibility

A probe measure is admissible for a transfer iff

```
D(A, B | P) > D_floor(A, B | P) + ε
```

for a stated `ε` (default `0.02`). Below that threshold there is no gap to
close and fidelity is undefined — the denominator in §4.1 collapses.

---

## 4. Fidelity

### 4.1 Transfer fidelity

The fraction of the pre-existing, closable gap that the message actually
closed:

```
              D(A, B | P) − D(A, B|m | P)
F*(m) = ───────────────────────────────────────
          D(A, B | P) − D_floor(A, B | P)
```

- `F* = 1` — the message closed the entire closable gap. The receiver is now
  behaviorally indistinguishable from the sender over `P`, up to noise.
- `F* = 0` — the message changed nothing.
- `F* < 0` — the message made things **worse**. We call such a message an
  **antinoophor**. These are not rare, and any theory that cannot express them
  is incomplete.

`F*` is unbounded below and capped at 1 above. Report it unclipped; clipping
hides antinoophors, which are among the most informative observations in the
field.

### 4.1.1 The reference is an argument, not an assumption *(v0.4)*

The definition above says "the gap between sender and receiver" and never asks
why the sender is the target. For three versions that was an assumption wearing
a parameter's clothes, and
[E-001](../experiments/E-001-fluency-cost/FINDINGS.md) measured what it costs:
both receivers out-decided the sender against the key, `F*` ranked them the
other way, and 62% of the headline effect sat on the four probes where the
sender was wrong and a receiver was right.

A **reference disposition** `R` is a per-probe distribution over the answer
space, declared with `P` **before data exists**, carrying a recorded
provenance. Admissible constructions
([`reference.py`](../metrics/noophorics/reference.py)):

- `R_key` — a point mass on each key, or a distribution over the defensible
  readings where a key is contested. `M33` is exactly that case, and a binary
  key cannot express it while a distribution can.
- `R_panel` — a declared mixture over independent adjudicators, none of which
  wrote the message, authored the probes, or is the sender. **Inter-adjudicator
  agreement is reported alongside, and a unanimous panel is a warning rather
  than a validation**: a panel sharing the sender's bias reproduces "the sender
  is always right" at group level.
- `R_sender` — the replication reference.

```
D_R(X | P) = E_{π ~ P} [ JSD( R(π) ‖ X(π) ) ]

              D_R(B | P) − D_R(B|m | P)
F*_R(m) = ───────────────────────────────────
               D_R(B | P) − D_floor,R
```

**`F*_{R=sender} ≡ F*`, term for term.** Nothing is recomputed and no published
number moves; the test suite pins the identity. What changes is what may be
claimed.

**Which `F*` this generalises**, stated because this document defines two
objects. §3 defines `F*` over **true distributions** as
`(D_prior − D_post)/D_prior`; §4.1 and the code compute the **floor-corrected
estimator**. `F*_R` generalises the *definition*. The floor stays exactly where
v0.3 put it — inside the estimator, correcting finite-sample bias, never inside
the definition.

**The floor under a declared reference.** `D_floor` is a permutation null over
*the pair being compared*, so under `R` it is the null between `R`'s draws and
the receiver's. Where `R` carries no sampling noise — a key — there is nothing
to permute and **the null is undefined, not zero**. The receiver's finite-sample
bias does not vanish because the reference is exact. Setting it to zero is a
choice to leave that bias uncorrected, and it must be reported as one; doing it
silently would be [retraction #2](../RETRACTIONS.md) in a mirror.

**Admissibility gains a second condition.** Under a sender-independent `R` the
sender drops out of the first, so both are required:

1. `D_R(B | P) − D_floor,R > ε` — the receiver has headroom against the
   reference.
2. `D(A, B | P) > D_floor + ε` — sender and receiver disagree before transfer.
   Without this a "transfer" could be reported on a measure where the parties
   already agree, which §1.3 calls measuring nothing.

**The licensing rule.** The word *understanding* is licensed only where `R` is
**independent of the sender**. Independence from the *message* is not the
criterion and does not bite: the sender's own probe draws are not descendants of
its message, so `R_sender` would pass that test. Where `R` is the sender, the
reportable claim is **replication**, never understanding.

**And independence must be measured, not asserted.** The repository already
shipped a reference that was the sender resampled: the `CEILING` arm gave the
same model the same context and produced 25 of 25 **bit-identical** draw
sequences, mean JSD 0.0000, while passing a 0.70 gate at 1.0000
([journal](../journal/2026-07-30-two-audit-holes.md)).
`independence_of()` reports two distinct facts, because the first version of it
conflated them and would have rejected a legitimate key:

- **independent by construction** — from `R`'s provenance;
- **distinguishable on this measure** — from the measured `JSD(R, A)`.

A key drawn from the source specification is independently constructed. On a
measure where the sender answers every probe correctly it is nonetheless
behaviourally identical to the sender, `F*_key` equals `F*_sender` exactly, and
the reference choice cannot inform anything. Measured: on `MERIDIAN-33` with a
33/33 sender, `JSD(key, sender) = 0.0010`; on `MERIDIAN-34` with the E-001
sender, wrong on four probes, `0.1176`. **A perfect sender hides the entire
problem**, which is the argument for declaring `R` even where it provably does
not move the number.

**Prior art (added 2026-07-29).** `F*` is a normalized-recovery statistic and
the form is not ours. Burns et al. define *performance gap recovered*,
`PGR = (weak-to-strong − weak) / (strong ceiling − weak)` — the same shape with
the sign reversed, since `D` is minimized where performance is maximized
(arXiv:2312.09390 §3; ICML 2024, PMLR 235:4971–5012). The form is generic and
predates that paper too; we make no priority claim on it and this note is not
one either.

Two differences must be stated wherever the parallel is drawn. PGR's terms are
task performance against ground truth; `F*`'s are divergence from the sender.
And in Burns et al. high student–supervisor agreement is the *failure* signal —
the imitation mode their auxiliary confidence loss exists to suppress — which is
[E-001's defect](../experiments/E-001-fluency-cost/FINDINGS.md) arriving from
the opposite direction, earlier, in a literature we had not read.

### 4.2 Cost

```
C(m) = cost of the artifact
```

Default unit: tokens, measured with the receiver's tokenizer (the receiver is
who pays to read it). Alternatives — bits, wall-clock, human attention-seconds —
are permitted but must be stated. Cross-study comparison requires the same unit.

### 4.3 Noophoric efficiency

```
η(m) = F*(m) / C(m)
```

Understanding per unit cost, in fidelity per kilotoken. **Valid only where
`F*(m) ≥ 0`.**

> ~~"This is the quantity that engineering should optimize, and almost nothing
> currently does."~~
>
> **Defect, found 2026-07-29 by external review and confirmed by running our
> own code.** A ratio with a signed numerator is not an ordering. `F*` is
> deliberately unbounded below — that is the whole point of antinoophors — and
> dividing a negative number by cost makes the *cheaper* failure look worse:
>
> | message | `F*` | cost | `η` per ktok |
> |---|---|---|---|
> | short antinoophor | −1.0 | 100 tok | **−10.00** |
> | long antinoophor | −1.0 | 800 tok | **−1.25** |
>
> The message that spends eight times as much to do the same damage **ranks
> higher**. `η` inverts precisely on the observations §4.2 calls the most
> informative in the field, and it did so in the shipped implementation for
> three versions.
>
> The error is structural, not arithmetic: `F*/C` is a *rate*, and rates order
> correctly only on a fixed sign. Rate–distortion theory and the information
> bottleneck use a Lagrangian rather than a ratio for exactly this reason.

**Use instead, when the sign is not known in advance:**

```
V_λ(m) = F*(m) − λ · C(m)
```

`V_λ` is monotone in both arguments at every sign, so it orders messages the
way the field means to order them: more fidelity is better, more cost is worse,
always. `λ` is the exchange rate between fidelity and a token and must be
declared with any reported `V_λ` — it is a policy choice, and pretending a
ratio avoided that choice was part of the appeal of the ratio.

Sweeping `λ` traces the achievable frontier, which makes `V_λ` and the capacity
curve `K(C)` (§6.1) the same object viewed two ways. `η` is retained for
`F* ≥ 0`, where it is the familiar and legible quantity, and
[`efficiency()`](../metrics/noophorics/fidelity.py) now refuses a negative
fidelity rather than returning a number that cannot be compared.

---

## 5. Phantom agreement

The parties' *belief* about the transfer, minus what actually happened:

```
Φ = Ĉ − Â
```

where:

- `Â` is the observed agreement rate (§2.3),
- `Ĉ` is the **claimed** agreement rate: the mean of the sender's prediction
  and the receiver's self-report, each elicited as *"over probes of this kind,
  what fraction of your decisions would match the other party's?"*

Both terms are rates in `[0, 1]`, so `Φ ∈ [−1, 1]` and the subtraction is
meaningful.

- `Φ > 0` — **shared illusion.** Both parties overestimate how much landed.
- `Φ ≈ 0` — calibrated.
- `Φ < 0` — mutual underconfidence. More understanding transferred than either
  party believes. Rarer, and its own kind of failure: it causes redundant
  re-explanation and unnecessary escalation.

Report the sender's and receiver's claims separately as well as the mean. They
are frequently asymmetric, and the asymmetry is data.

---

## 6. Capacity and residual

### 6.1 Channel capacity between minds

```
K(A, B | P) = sup_m F*(m)
```

The best fidelity achievable by *any* message, at unbounded cost. This is the
noophoric analogue of Shannon capacity, and the central theoretical object of
the field.

`K` is not directly computable — the supremum ranges over all possible
artifacts.

**It must not be estimated as the maximum over a search.** That is the maximum
of noisy estimates, which is biased *upward*, with the bias growing in both the
search size and the per-estimate noise. At the noise level our own validation
reports, a 100-candidate search returns 0.85 when the truth is 0.60. A quantity
so estimated is not a lower bound on anything.

Estimate it instead by **sample splitting**: choose the best encoding on one
probe split, and report its fidelity on a split that played no part in choosing
it. That held-out score is unbiased for the selected encoding, and therefore is
a genuine lower bound (`capacity_lower_bound`).

Two conditions, both load-bearing:

- The holdout must consist of probes the **sender** never saw. Otherwise a
  lookup table wins — the counterexample that refuted axiom A3.
- The bound belongs to a **stated cost ceiling**. `K` is a curve `K(C)`, not a
  scalar; at unbounded cost over visible probes it is trivially 1.

Every reported bound must state its search size, its cost ceiling, and the
realised winner's curse (selection score minus held-out score), which measures
how much the search overfitted.

### 6.2 Residual

```
R(A, B | P) = 1 − K(A, B | P)
```

The untransferable remainder. Axiom [A3](../PRINCIPIA.md#4-the-four-axioms)
asserts `R > 0` in the general case. Characterizing what lives inside `R` —
and predicting its size from properties of the two agents — is
[Problem 1](open-problems.md).

---

## 7. Reporting standard

A noophoric measurement is reportable iff it states, at minimum:

| Field | Why |
|---|---|
| Probe measure `P` | A2 — the frame. Include the probe set or a hash of it. |
| Samples per probe `n` | JSD estimates are biased at small `n`. |
| `D_prior`, `D_post`, `D_floor` | So `F*` can be recomputed and audited. |
| `C(m)` and its unit | η is not comparable across units. |
| Sender and receiver identity | Model IDs, versions, decoding parameters. |
| `Ĉ` sender and receiver, separately | The asymmetry is data. |

A number reported without these is an anecdote. We accept anecdotes in
`journal/`; we do not accept them in `theory/`.

---

*This document is licensed CC BY 4.0.*
