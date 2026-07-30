# E-002 is void — the elicitation saturated, and so did the transfer

**Status:** void · closed · superseded by E-002b (not yet registered)
**Voided:** 2026-07-30, at the first brief's elicitation, by the pre-registered
degeneracy gate
**Cost:** ~4.5 hours of the ~13 the full sweep would have taken

---

## What the gate caught

The [pre-registration §5.1](PREREGISTRATION.md) gates the run on *elicitation
degeneracy*: a party that answers identically on every probe has zero
resolution **by construction**, so H2 would be untestable rather than false.

It fired on the first brief.

```
claim-sender@gpt-oss:120b#7c0bcdec32     165 judgments, distinct values: [True]
claim-receiver@gpt-oss:120b#7c0bcdec32   165 judgments, distinct values: [True]
```

330 binary judgments — 33 probes × 5 elicitations × 2 parties — and **every one
of them was "yes, we will agree."** Not a majority. All of them.

## And the outcome saturated too

The second degeneracy was predicted the day before, in
[RISK-NOTE.md](RISK-NOTE.md), and arrived exactly as described:

| quantity | value |
|---|---|
| sender–receiver agreement, pre-transfer | 0.5152 |
| sender–receiver agreement, post-transfer | **1.0000** |
| probes where they actually diverged | **0 of 33** |
| claimed agreement, both parties, every probe | 1.0000 |
| **Φ** | **+0.0000** |

Both parties said they would agree on everything. They agreed on everything.
They were right.

**This is not a measurement of Φ = 0.** It is precisely the pathological case
that the [corrected falsification criterion 2](../../PRINCIPIA.md) was rewritten
for the previous day: bias exactly zero, resolution **undefined**. Nobody
demonstrated any ability to tell a diverged case from a matched one, because
there were no diverged cases — and the elicitation would have returned "yes"
either way.

Reporting `Φ = 0.0000` here as evidence about the world would be the exact error
the corrected criterion exists to prevent. It is reported as an instrument
result, per [§7](PREREGISTRATION.md).

---

## Diagnosis 1 — the elicitation has a default answer

I ported Keysar & Henly's **granularity** and not their **structure**, and the
structure was the part doing the work.

Their speakers did not answer "did the listener understand?" They were shown
**two paraphrases** and had to say **which one** the listener had taken. The
72% is an aggregate the experimenters computed afterwards by checking how often
the chosen paraphrase matched the speaker's own intention. The instrument has
**no "everything is fine" response available** — the speaker must commit to a
reading, and the overconfidence shows up in *which* reading it commits to.

E-002 asked: *"Will your colleague reach the same verdict as you on this case?"*
That is a yes/no with an obvious default, and the model took it 330 times out of
330.

The
[citation verification](../../theory/prior-art.md) had already stated this
explicitly — *"the speaker's per-trial response was a binary choice between the
two projected paraphrases — WHICH reading the listener took — not a yes/no 'did
they get it'"* — and I built the yes/no anyway. The information was in the
repository before the runner was written.

**Repair.** The sender predicts the receiver's **verdict**, choosing among the
probe's own options. Agreement is scored afterwards, by comparison, exactly as
Keysar & Henly computed it. There is no way to answer "yes".

## Diagnosis 2 — the probe measure admits a perfect transfer

`MERIDIAN-33` is answerable from a 180–260 word brief with no loss at all. Once
the transfer is perfect there is nothing for a belief to be wrong *about*, and
`Φ` is not small — it is undefined in the same way resolution is.

This is a hole in the theory, not just in the experiment.
[definitions §3.3](../../theory/definitions.md) gates **admissibility on the
prior gap**: the parties must disagree *before* the transfer. There is no
post-side criterion. A probe measure can be perfectly admissible and still be
useless, because the quantity being measured evaporates when the transfer
succeeds.

Recorded as [Problem 11](../../theory/open-problems.md).

**Repair.** Do not harden the probes — that changes the frame and invites
tuning it until the result appears. Constrain the *channel*, which is the
theory's own axis: sweep the brief budget so that transfer quality varies by
design, and measure Φ across the ladder. Then Φ has a gradient to live on, and
the hypothesis becomes the interesting one — **does Φ rise where fidelity
falls?**

---

## What carries forward

- **The gate worked.** It was placed after the first brief rather than after the
  sweep, deliberately, following [E-001b's postmortem](../E-001b-fluency-factorial/VOID.md).
  It saved roughly eight and a half hours.
- **The risk note worked.** Outcome degeneracy was written down, with its
  mechanism, before any data existed. That it then happened is the second time
  in three days that pre-registration paid for itself in something other than
  virtue.
- **`sender`, `PRIOR` and `CEILING` at n=30** remain valid and carry into
  E-002b — they depend on no brief.
- **b0's draws** are retained and committed. The run is void; the data is real.

## The uncomfortable part

Three experiments have now voided, and each void was caught by machinery built
after the previous one. That is the system working. But the failure this time
was not an oversight — the correct instrument design was written down in this
repository, by a verification pass I commissioned, and I read it, quoted it in a
commit message, and then built the weaker thing.

The gap between having the information and using it is not fixed by having more
information. It is the same gap the programme claims to study, and it appeared
here between a document and its own author.

---

*This document is licensed CC BY 4.0.*
