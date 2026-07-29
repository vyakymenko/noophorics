# NHP-0001 — Noophoric Handoff Protocol

**Status:** draft
**Version:** 0.2 *(v0.1 published 2026-07-28; four defects found and repaired below)*
**Date:** 2026-07-29
**Depends on:** [definitions.md](../theory/definitions.md) ·
[handoff.py](../metrics/noophorics/handoff.py)

---

## Abstract

A wire format for handing work between agents that carries a **fidelity
claim** rather than a completeness claim, and that ships the means of checking
that claim alongside it.

Every handoff today is an assertion: *here is what I know.* NHP-0001 makes it a
falsifiable assertion: *here is what I know, here is what I predict you will do
with it, and here are the probes that will tell us both if I was wrong.*

---

## 0. What changed in v0.2, and why it is at the top

v0.1 was published with no implementation, on the stated ground that publishing
early lets a protocol be wrong in public. It was wrong in public. Writing the
implementation surfaced four defects, every one of which survives a careful
reading of the v0.1 prose:

| # | Defect | Consequence |
|---|---|---|
| **D1** | The answer key shipped inside the payload the receiver reads | Every `Â` measured under v0.1 is an upper bound of unknown tightness |
| **D2** | The gate fires on `Φ` alone | A handoff where nothing transferred and both parties knew it **passes** |
| **D3** | `Â` is raw agreement, uncorrected | On a lopsided probe set, `0.85` can be *below* the score for not reading the message |
| **D4** | `θ = 0.15` with a floor of three probes | The decision threshold is finer than the measurement grid |

None were found by rereading the document. All four were found by trying to
make it run — which is the argument for the norm that a protocol ships with an
implementation, and against the v0.1 rationale for publishing without one.

The defective clauses are struck through in place below rather than deleted.

---

## 1. Motivation

Current agent handoffs are prose blobs optimized for looking complete. They
carry no way to detect that the receiver reconstructed something different, so
divergence surfaces downstream as wrong action, and nobody traces it back.

Two design commitments follow from the theory:

1. **The sender attaches probes.** A handoff without probes cannot be
   verified, and an unverifiable handoff is exactly where phantom agreement
   ([Φ](../theory/definitions.md#5-phantom-agreement)) lives.
2. **The sender states its predicted agreement rate.** This makes `Φ`
   computable at zero extra inference cost — the sender's claim is one number
   it already implicitly holds.

---

## 2. Message structure

The message is **two objects, not one**. This is the D1 repair and it is
structural, not a matter of discipline.

### 2.1 The payload — transmitted

```json
{
  "nhp_version": "0.2",
  "sender": {"id": "orchestrator", "model": "claude-opus-5"},
  "task": "Migrate the billing module to the new tenant API.",

  "constraints": [
    "Never call resolve_tenant() with a null tenant_id.",
    "Legacy accounts migrated before 2025-06 have no tenant_id at all; they route through the compat shim.",
    "Do not change the public signature of BillingClient."
  ],

  "context": "The tenant model is hierarchical except for migrated accounts.",

  "probe_measure_id": "a91c3f0b2e77",
  "probes": [
    {
      "id": "p1",
      "prompt": "A legacy account from 2025-03 needs billing. Call resolve_tenant() or the compat shim?",
      "options": ["resolve_tenant", "compat_shim"]
    }
  ],

  "claim": {"predicted_agreement_rate": 0.85}
}
```

### 2.2 The checkset — withheld

```json
{
  "probe_measure_id": "a91c3f0b2e77",
  "keys": {"p1": "compat_shim"}
}
```

`probe_measure_id` is a hash over **probes and keys together**. It appears in
both objects, so a sender that revises a key after seeing the receiver's
answers produces a checkset that no longer matches the payload the receiver
was given. That commitment is what makes the sender's own key admissible as
evidence at all.

> ~~**v0.1 §2:** `"probes": [{..., "expected": "compat_shim"}]`, with §3.1
> asking the receiver to answer "without consulting `expected`."~~
>
> **D1.** For a human that is an honour system. For a language model it is not
> even that: the key is in context, and an in-context answer is evidence about
> reading, not about what the receiver reconstructed from the constraints.
> `verify_no_key_leak()` walks the payload to arbitrary depth and **raises**
> on any answer-shaped field. A protocol whose central safeguard is "the
> receiver promises not to look" has no safeguard.

### 2.3 `constraints` — required, and required *first*

Constraints and prohibitions. [L4c](../theory/laws.md#l4c) conjectures these are
the **invariant core**: content in constraint form decays measurably more
slowly under repeated summarization than content in descriptive form.
Descriptions decay across hops; boundaries do not.

Ordering is normative, not stylistic. If the message is truncated — by a
context limit, by a compaction pass, by a careless middle layer — the field
that survives should be the one that carries the most fidelity per token.

> v0.1 cited **L4** for this. L4 was withdrawn in v0.3 of the theory as
> ill-typed — it multiplied fidelities measured against different prior gaps,
> and composed two antinoophors into a positive product. The claim this
> protocol actually leans on survived the restatement as **L4c**, and the
> citation is corrected rather than quietly dropped.

### 2.4 `context` — optional, and explicitly second-class

Declarative background. Useful, lower fidelity per token, first to be dropped
under pressure. [L6](../theory/laws.md#l6) predicts a handoff that is all
`context` and no `constraints` will underperform its own length.

### 2.5 `probes` — required

Probes must be **decidable**: finite, discrete answer space, and an answer the
source material actually determines.

Two requirements v0.1 did not have:

- **Independently adjudicated.** The sender writes the rules, writes the exam,
  and writes the key. This is the M33 failure
  ([SENSITIVITY-M33](../experiments/E-001b-fluency-factorial/SENSITIVITY-M33.md))
  in its purest form, and it is worse here than in an experiment, because there
  is no reviewer downstream. A key nobody else checked is a self-report;
  `adjudicate()` says so in its output unless told the key was adjudicated.
- **Enough of them.** See §5.

> ~~**v0.1 §2.3:** "At least three probes."~~
>
> **D4.** With three probes answered once each, `Â` can only be 0, ⅓, ⅔, or 1.
> The grid is 0.33 wide and the threshold is 0.15: before any question of
> sampling error, the gate is asked to resolve a difference the instrument
> cannot represent.

### 2.6 `claim` — required

`predicted_agreement_rate ∈ [0, 1]`: what fraction of the probes the sender
expects the receiver to answer as the sender would.

This single number costs nothing and converts every handoff into a calibration
datapoint. It remains the protocol's most distinctive feature — and §4 is about
why it cannot be the only thing the gate looks at.

---

## 3. Receiver obligations

On receipt, before acting:

1. Answer every probe. The key is not present to consult.
2. Report your own `predicted_agreement_rate` — before comparison.
3. Send answers and claim to the adjudicator, which holds the checkset.
4. Act on the returned decision (§4).

**Answers are draws, not verdicts.** Each probe is answered `n` times and every
draw is reported in order. A receiver that collapses its draws to a majority
before reporting has thrown away the variance the floor is computed from, and
this programme has already made the n=1 mistake once, in
[AMENDMENT-001](../experiments/E-001-fluency-cost/AMENDMENT-001.md), and had to
retract a diagnosis for it.

**A refusal is missing data.** A probe the receiver declines to answer is
excluded from `Â`, never counted as a miss.

---

## 4. The gate

Two gates. Both must pass.

```
fidelity     Â  ≥ 0.80        did the understanding transfer?
calibration  Φ  ≤ θ = 0.15    were the parties right about whether it did?
```

`Φ = mean(sender_claim, receiver_claim) − Â`, unchanged from v0.1.

> ~~**v0.1 §3.4:** "If `Φ > θ`, do not proceed."~~
>
> **D2.** Consider a sender claiming 0.30, a receiver claiming 0.30, and an
> observed 0.30. `Φ = 0`, the gate passes, and the parties proceed having
> agreed on three probes in ten. v0.1 green-lights a **well-calibrated
> catastrophe** — and the better calibrated the parties are, the more reliably
> it does so. `Φ` measures whether the parties were *right about* the transfer.
> It says nothing about whether the transfer happened, and a protocol acting on
> it alone is blind in exactly the direction it was built to see.
>
> Measured on the repaired implementation: a receiver diverging on 10 of 10
> probes, with both parties predicting it, gives `Φ = 0.00` — v0.1 proceeds,
> v0.2 blocks on fidelity.

The asymmetry v0.1 identified is still the right one and still holds under the
two-gate form: a receiver that answers badly and *knows* it is safe, because it
will ask. A receiver that answers badly and is confident is the failure this
protocol exists to catch. What v0.1 missed is that a receiver that answers
badly and is *correctly* unconfident still must not proceed — being right about
one's own confusion is not a licence to act on it.

### 4.1 `Â` is reported against its baseline

`Â` alone is not enough either. The baseline is what a receiver scores by
drawing from the distribution of correct answers **without reading anything**:
`Σ p(o)²` over the key marginal.

A probe set whose answers are nine `a`s and one `b` hands out **0.820** for
free. A receiver scoring 0.85 raw on it is at a corrected fidelity of 0.167,
and one scoring 0.80 is *below the baseline* — corrected `−0.111`, and, as
everywhere else in this programme, **not clipped**. An uncorrected `Â` is not
wrong, it is unfinished, and it systematically overstates.

Probe sets should be built with a balanced key marginal. When they are not, the
baseline is the number that says how little the raw score meant.

### 4.2 There is a third outcome

`proceed` is `true`, `false`, or **`null`** — the last meaning the evidence
cannot support a verdict. v0.1 could only say yes or no, so an underpowered run
was reported as a pass. Underpowered is not a pass.

---

## 5. How many probes

Two requirements, and the binding one is not the obvious one.

- **Grid.** `Â` is a multiple of `1/N`, so `N ≥ 1/θ`.
- **Noise.** `Â` has standard error `≤ 0.5/√N`. For the gate to separate
  `Φ = 0` from `Φ = θ` at 95%, the interval half-width must fit inside `θ`.

| θ | grid wants | noise wants | **required draws** |
|---|---|---|---|
| 0.20 | 5 | 25 | **25** |
| 0.15 | 7 | 43 | **43** |
| 0.10 | 10 | 97 | **97** |

Draws are probes × samples: 11 probes at 4 draws each satisfies θ = 0.15.

What v0.1's floor of three probes at one draw actually does, simulated 20 000
times against the v0.1 gate:

| true agreement | claim | v0.1 gate blocks | should |
|---|---|---|---|
| 0.85 | 0.85 | **39.4%** | pass |
| 0.60 | 0.85 | **78.5%** | block |

An honest handoff is stopped two times in five, and a 0.25 overclaim gets
through one time in five. The gate is mostly reading its own sampling noise.

`θ = 0.15` itself remains a guess with no empirical basis
([Problem 7](../theory/open-problems.md)). What v0.2 fixes is that the guess is
now at least measurable at the sample size the protocol asks for.

---

## 6. Compaction

When a handoff must be compressed, the ordering is:

1. Preserve `constraints` verbatim. Never paraphrase them — paraphrase is a
   transfer, and transfers are lossy.
2. Preserve `probes`. They are the only thing that can detect what the
   compaction destroyed.
3. Compress `context` freely.
4. Re-run the probes after compaction. Report retained fidelity, not
   compression ratio.

> A compaction that reports "reduced by 80%" without a fidelity number is
> making a claim about storage and letting the reader hear a claim about
> meaning.

---

## 7. Open questions

Honest gaps, ordered by how much they worry us:

- **Probe generation is unsolved.** Who writes the probes, and how do we stop
  the sender from writing ones it knows the receiver will pass? v0.2 makes the
  problem *visible* — the key is committed, and a self-written key is disclosed
  in the output — but disclosure is not a fix. Adversarial probe generation by
  a third agent is the leading candidate and is untested.
- **`θ = 0.15` is still a guess.** §5 makes it measurable, not justified.
- **The fidelity floor is also a guess.** `0.80` is a policy choice about how
  much divergence a caller will act on. Unlike θ, it may not have a
  domain-independent answer at all.
- **Probe cost.** §5 raises the required draws by an order of magnitude over
  v0.1. The minimal probe set that detects `Φ > θ` at stated sensitivity is
  unknown, and the honest reading of §5 is that the protocol is now expensive.
- **Multi-hop `claim` composition.** If A hands to B hands to C, how do the
  claims compose? Not multiplicatively — that was L4's error. Every hop should
  be scored against the **origin** in the origin's frame
  ([chain.py](../metrics/noophorics/chain.py)), but whether *calibration*
  composes the way fidelity does is untouched.

---

## 8. Status

Draft, implemented, unvalidated. The implementation
([handoff.py](../metrics/noophorics/handoff.py), 13 tests) is the thing that
found D1–D4; no live handoff has been run through it.

The v0.1 rationale — publish before implementing, so the protocol can be wrong
in public — produced a document with four defects that an afternoon of
implementation exposed. It was wrong in public, as advertised. The revised
norm: **a protocol ships with the code that runs it, and the code ships with
the tests that pin its failure modes.** Being publicly wrong is only a virtue
when the wrongness is cheap to find, and prose hides more than it reveals.

Validation against live agents is tracked as E-005.

---

*This document is licensed CC BY 4.0.*
