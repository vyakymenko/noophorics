# NHP-0001 — Noophoric Handoff Protocol

**Status:** draft
**Version:** 0.1
**Date:** 2026-07-28
**Depends on:** [definitions.md](../theory/definitions.md)

---

## Abstract

A wire format for handing work between agents that carries a **fidelity
claim** rather than a completeness claim, and that ships the means of checking
that claim alongside it.

Every handoff today is an assertion: *here is what I know.* NHP-0001 makes it a
falsifiable assertion: *here is what I know, here is what I predict you will do
with it, and here are the probes that will tell us both if I was wrong.*

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

```json
{
  "nhp_version": "0.1",
  "sender": {"id": "orchestrator", "model": "claude-opus-5"},
  "task": "Migrate the billing module to the new tenant API.",

  "constraints": [
    "Never call resolve_tenant() with a null tenant_id.",
    "Legacy accounts migrated before 2025-06 have no tenant_id at all; they route through the compat shim.",
    "Do not change the public signature of BillingClient."
  ],

  "context": "The tenant model is hierarchical except for migrated accounts.",

  "probes": [
    {
      "id": "p1",
      "prompt": "A legacy account from 2025-03 needs billing. Call resolve_tenant() or the compat shim?",
      "options": ["resolve_tenant", "compat_shim"],
      "expected": "compat_shim"
    }
  ],

  "claim": {
    "predicted_agreement_rate": 0.85,
    "probe_measure_id": "billing-migration-v1@a91c3f"
  }
}
```

### 2.1 `constraints` — required, and required *first*

Constraints and prohibitions. [L4](../theory/laws.md#l4) conjectures these are
the **invariant core**: the part of an understanding that survives repeated
summarization intact. Descriptions decay across hops; boundaries do not.

Ordering is normative, not stylistic. If the message is truncated — by a
context limit, by a compaction pass, by a careless middle layer — the field
that survives should be the one that carries the most fidelity per token.

### 2.2 `context` — optional, and explicitly second-class

Declarative background. Useful, lower fidelity per token, first to be dropped
under pressure. [L6](../theory/laws.md#l6) predicts a handoff that is all
`context` and no `constraints` will underperform its own length.

### 2.3 `probes` — required

At least three probes covering the cases where the sender believes a
reasonable receiver could plausibly go wrong. These are the receipt.

Probes must be **decidable**: finite, discrete answer space. `expected` is the
sender's own answer, which is what makes divergence measurable without a human
adjudicator in the loop.

### 2.4 `claim` — required

`predicted_agreement_rate ∈ [0, 1]`: what fraction of the probes the sender
expects the receiver to answer as the sender would.

This single number is the protocol's most distinctive feature. It costs
nothing, and it converts every handoff into a calibration datapoint.

---

## 3. Receiver obligations

On receipt, before acting:

1. Answer every probe **without** consulting `expected`.
2. Report your own `predicted_agreement_rate` — again, before comparison.
3. Compare. Compute observed agreement `Â` and
   `Φ = mean(claims) − Â`.
4. If `Φ > θ` (default `θ = 0.15`), **do not proceed**. Request clarification
   on the specific probes that diverged, naming them.

Step 4 is the whole point. A high `Φ` is the signal that both parties are
confidently holding different models — the exact condition under which
proceeding is most expensive and least likely to be noticed.

Note the asymmetry with a plain accuracy check: a receiver that answers probes
*badly* but *knows* it answered badly is safe, because it will ask. A receiver
that answers badly and is confident is the failure this protocol exists to
catch.

---

## 4. Compaction

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

## 5. Open questions

Honest gaps in this draft, ordered by how much they worry us:

- **Probe generation is unsolved.** Who writes the probes, and how do we stop
  the sender from writing ones it knows the receiver will pass? A sender that
  generates its own exam has an obvious incentive problem. Adversarial probe
  generation by a third agent is the leading candidate and is untested.
- **`θ = 0.15` is a guess.** It has no empirical basis yet;
  [Problem 7](../theory/open-problems.md) is the work that would justify a
  number.
- **Probe cost.** Answering probes costs inference. The minimal probe set that
  detects `Φ > θ` at stated sensitivity is unknown.
- **Multi-hop `claim` composition.** If A hands to B hands to C, how do the
  claims compose? [L4](../theory/laws.md#l4) suggests multiplicatively, but
  that is a conjecture about fidelity, not about calibration.

---

## 6. Status

Draft. Not implemented, not validated, and deliberately published before
either — the protocol is a prediction about what will matter, and publishing it
early means it can be wrong in public.

Implementation and validation are tracked as future experiments (E-005+).

---

*This document is licensed CC BY 4.0.*
