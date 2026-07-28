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

### 3.1 Self-divergence

An agent is not deterministic. Sampled twice, it diverges from itself:

```
D_self(A | P) = E_{π ~ P} [ JSD( A⁽¹⁾(π) ‖ A⁽²⁾(π) ) ]
```

where `A⁽¹⁾` and `A⁽²⁾` are independently drawn sample sets from the same agent
under identical conditions.

### 3.2 Floor

```
D_floor(A, B | P) = ½ ( D_self(A | P) + D_self(B | P) )
```

This is the divergence you would measure between two *perfectly aligned* agents
with the same stochasticity. It is the irreducible remainder. No transfer can
push measured divergence below it, and a fidelity measure that ignores it will
systematically report ceilings below 1 and mistake sampling noise for
untransferred meaning.

**Correcting for the floor is not optional.** It is the single detail that
separates a noophoric measurement from a plausible-looking number.

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

Understanding per unit cost. This is the quantity that engineering should
optimize, and almost nothing currently does. Report η in fidelity per
kilotoken to keep the numbers legible.

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
artifacts. It is estimated as `K̂ = max over a search budget of N candidate
encodings`, which is a lower bound. Every reported `K̂` must state its search
procedure and `N`; a capacity estimate without them is a fidelity measurement
wearing a bigger hat.

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
