# E-002b — Does Φ rise where fidelity falls?

**Status:** pre-registered, not yet run
**Registered:** 2026-07-30
**Attacks:** [PRINCIPIA §5](../../PRINCIPIA.md), and
[Problem 11](../../theory/open-problems.md) by working around it
**Supersedes:** [E-002](../E-002-phantom-agreement/VOID.md), void
**Probe measure:** `MERIDIAN-33@256672ea3852`
**Instrument notes:** [INSTRUMENT.md](INSTRUMENT.md) — measured before this file

> Committed before any data exists. If the results contradict what is written
> here, this file is not edited. The finding is added and this stands.

---

## 1. The question

E-002 asked whether `Φ` is positive. It could not answer, because the transfer
was **perfect** — 0 of 33 probes diverged — and a belief cannot be wrong about
a case where nothing went wrong.

E-002b asks the question that was interesting all along:

> **Does phantom agreement grow as transfer degrades?**

If `Φ` is real, it is not a constant. It should be smallest where the transfer
worked and largest where it silently failed — that asymmetry is the entire
practical claim of the field. A `Φ` that does not track fidelity is a
measurement artifact of the elicitation, not a property of communication.

## 2. Design: constrain the channel, not the frame

The probe measure is **unchanged**. Hardening it after discovering it was too
easy would be tuning the frame until a result appears, which is
[Problem 6](../../theory/open-problems.md) wearing a disguise.

Instead the **brief budget** is swept, which is the theory's own cost axis.
Measured before registration ([INSTRUMENT.md](INSTRUMENT.md)):

| budget | realised | agreement | diverged |
|---|---|---|---|
| none | 0 words | 0.5152 | — |
| ~30 | 35 words | 0.6667 | 11 / 33 |
| ~70 | 84 words | 0.6667 | 11 / 33 |
| ~150 | 193 words | 0.9394 | 2 / 33 |
| ~200 | 180–260 words | 1.0000 | 0 / 33 |

**Rungs: 30, 70, 110, 150 target words**, `k = 4` briefs each, 16 briefs total.
The top rung is deliberately set below the saturation point: a rung at ~200
words transfers perfectly and measures nothing, and including it to make the
range look wider would be padding the design with a cell known in advance to be
empty.

```
sender    : gpt-oss:120b + MERIDIAN source spec
PRIOR     : gpt-oss:120b + nothing
CEILING   : gpt-oss:120b + the source spec
rung r, brief j : gpt-oss:120b + brief_rj
```

`n = 16` draws per probe per condition, `n_c = 3` elicitations per probe per
party. `n = 16` is stated as a limitation, not hidden: the JSD-based quantities
are noisier at 16 than at 30 and are reported as secondary. The primary
quantities are modal agreement and `Φ`, and a mode is stable well below the
sample size a divergence estimate needs.

`sender`, `PRIOR` and `CEILING` at n=30 already exist in the tracked cache and
depend on no brief. They are reused and the reuse is recorded, not hidden.

## 3. The elicitation has no default answer

This is the repair of E-002's fatal defect and the reason this is a new
registration rather than an amendment.

E-002 asked *"will your colleague reach the same verdict as you?"* and received
"yes" on 330 of 330 elicitations. Keysar & Henly's speakers were instead shown
two paraphrases and had to say **which one** the listener took — no
"everything is fine" response exists, and the agreement rate is computed
afterwards by the experimenter.

**E-002b elicits a verdict:**

- **sender**, shown its own brief: *"Your colleague has only this note — nothing
  else, and they cannot ask you anything. On this case, what verdict will they
  reach?"* → one of the probe's options.
- **receiver**: *"What verdict would the person who wrote your note reach on
  this case?"* → one of the probe's options.

A party's *claimed agreement* on a probe is then `1` if its predicted verdict
matches its own modal verdict, and `0` otherwise — exactly how 72% was computed
in 2002. Nothing about the key, the counterpart's answers, or any outcome
enters either prompt.

## 4. Hypotheses

**H1 — bias is positive.** Pooled over rungs, `Φ > 0`.

**H2 — resolution is above chance.** Per-probe claims are associated with
per-probe outcomes. The quantity E-002's instrument could not produce.

**H3 — the asymmetry replicates.** `P(claims match | actually diverged)` >
`P(claims diverged | actually matched)`. Keysar & Henly measured 46% against
12% in humans; this is the port.

**H4 — the sender is worse calibrated than the receiver.** In humans the bias
attaches to *producing* the message. If H4 fails while H1 holds, the mechanism
does not port.

**H5 — Φ is negatively associated with fidelity across the ladder.** The
experiment's reason for existing. Where the brief transfers less, the parties'
confidence should overshoot more.

**Recorded, not hypothesised:** `F*` per rung, the decomposition, realised
cost, the identity of the diverging probes at each rung, and whether the same
probes diverge across rungs — the ladder probe recorded counts and not
identities, and "the same 11 probes" and "two disjoint sets of 11" mean very
different things.

## 5. Analysis plan

1. Shared floor by permutation null on `sender` vs `PRIOR`, 300 permutations,
   seeded. Admissibility gate on the prior gap.
2. Per probe: observed match = `1(mode sender = mode receiver)`; claimed match
   as defined in §3.
3. **Bias** `Φ` per party and pooled, with a bootstrap 95% CI **over briefs**.
   The brief is the exchangeable unit. Probes within a brief are not
   independent observations of the treatment.
4. **Resolution** by point-biserial and Goodman–Kruskal γ, within party,
   brief-level bootstrap CI.
5. **Asymmetry** as two conditional rates, permutation test over briefs.
6. **H5** by the association between per-brief `Φ` and per-brief
   `fidelity_where_sender_right`, across all 16 briefs, with a permutation test
   over briefs and a bootstrap CI. Reported per rung as well as pooled.
7. `α = 0.05`; H1–H5 are one family on one dataset and are **Holm-corrected**.
8. No point estimate without a CI.

### 5.1 Gates

| gate | threshold | evaluated |
|---|---|---|
| sender accuracy vs key | > 0.90 | before the sweep |
| sender error count | ≤ 2 of 33 | before the sweep |
| prior admissibility | `D_prior − floor > 0.02` | before the sweep |
| CEILING fidelity | > 0.70 | before the sweep |
| **per-rung outcome variation** | a rung must have **≥ 3 and ≤ 30** of 33 probes diverging, pooled over its briefs | as each rung completes |
| **surviving rungs** | ≥ 3 rungs must pass the above, or the run is void | as each rung completes |
| refusals | 0 | continuously |

The outcome-variation gate is the [Problem 11](../../theory/open-problems.md)
workaround made operational. A rung where every probe matches — or every probe
diverges — supports no claim about calibration, because there is nothing for a
prediction to discriminate. Such a rung is **dropped**, not voided; the ladder
survives losing a rung and the pre-registration says so in advance.

**Constant claims are not a gate.** E-002 voided on exactly that and it was the
wrong quantity to gate on: a party claiming agreement on every probe while the
parties diverge on a third of them is the *strongest* form of the pathology,
not an instrument failure. That case is now a result. See
[INSTRUMENT.md §1](INSTRUMENT.md).

### 5.2 Declared limitations

- **One model in both roles.** A model predicting its own copy is the easiest
  case for calibration; a positive H1 here is conservative. Cross-provider is
  E-003.
- **One domain.** [Problem 6](../../theory/open-problems.md) is unsolved.
- **`n = 16`.** Below the range where the divergence estimator is comfortable.
  Modal agreement, the primary quantity, is not affected.
- **The rungs were chosen after seeing the ladder.** That is instrument work and
  it is disclosed: the measurements are in [INSTRUMENT.md](INSTRUMENT.md),
  committed before this file, and they contain no hypothesis test.
- The elicitation is a language-model self-report and inherits whatever
  pathologies those have. That is the object of study, not a confound.

## 6. Amendment policy

Permissible without a new registration, instrument only: fixing a defect in the
metrics library, applied identically everywhere; and reducing `k` for budget.
**Not permissible:** changing `n`, `n_c`, the rungs, the hypotheses, the gates,
the analysis plan, the elicitation wording, or the model.

**Cap: one amendment.** E-001 amended three times, E-001b twice, E-002 zero and
died anyway. The budget does not grow.

## 7. What each outcome means

- **H5 holds** — `Φ` tracks the failure of transfer. The field's practical claim
  survives its first real test, and phantom agreement becomes a usable warning
  signal rather than a slogan.
- **H5 fails, H1 holds** — the parties are uniformly overconfident regardless of
  how well the transfer went. `Φ` is then a property of the elicitation, not of
  the communication, and the field's motivating story is wrong in an
  interesting way.
- **H1 fails across every rung** — the corrected falsification criterion fires,
  provided H2 also fails. Both must vanish; either alone is compatible with the
  pathology being real.
- **Fewer than 3 rungs survive the outcome gate** — void, and Problem 11 gets
  harder rather than being worked around.

---

*This document is licensed CC BY 4.0.*
