# E-002b — findings

**The first run in this repository to reach analysis.** Every prior experiment
voided. All gates passed; all four rungs of the ladder produced outcome
variation.

Four of five pre-registered hypotheses came back supported. Then the numbers
were checked, and what they support is not quite what was predicted.

---

## 1. The pre-registered result, as run

| | value | p (Holm) | 95% CI | |
|---|---|---|---|---|
| **H1** bias positive | +0.2961 | 0.0005 | [+0.2200, +0.3649] | supported |
| **H2** resolution above chance | +0.1408 | 0.0005 | [+0.0678, +0.2206] | supported |
| **H3** conditional asymmetry | +0.8721 | 0.0005 | [+0.8135, +0.9236] | supported |
| **H4** sender worse than receiver | +0.0505 | 0.0033 † | [+0.0227, +0.0789] | supported † |
| **H5** Φ rises as fidelity falls | −0.9662 | 0.0005 | [−0.9932, −0.9293] | supported ‡ |

† corrected — see §4. ‡ measured with an estimator that could not have failed — see §5.

## 2. One fact stands behind most of it

The parties claimed agreement on **95.5%** of the 1056 probe-party cells, nearly
invariantly, while actual agreement ranged from **0.515 to 0.970** across briefs.

```
claim spread across briefs   sender 0.091   receiver 0.192
outcome spread                              0.455
variance ratio, observed : claimed                22.8 : 1
```

`Φ = claimed − observed`, so where the claims barely move, `Φ` is `−observed`
plus a constant. Three of the five hypotheses inherit that:

- **H1** is the pinning stated as a level: `0.9552 − 0.6591 = 0.2961`, exactly.
- **H3**'s measured 0.8721 is **95.8%** of the 0.9104 that perfectly constant
  claims at 0.9552 would produce with no conditional structure at all.
- **H5** is discussed in §5, where the problem turns out to be different and
  worse.

This does **not** make them false, and the distinction matters: *algebraically
related to another quantity* and *vacuous* are not the same thing. What it means
is that they are one finding reported five times, not five findings.

## 3. What survives independently

**H2 — resolution — is the only hypothesis the pinning cannot reach.** Perfectly
constant claims give resolution exactly 0 by construction, so `+0.1408` is
genuine per-probe signal: the parties do have *some* insight into which probes
diverged.

Its base is narrow and must be stated with it, and stating it precisely took
two attempts. **963 of 1056 cells sit at exactly 1.0** — "we will agree" from
both parties on 91.2% of the cases. The distribution is
`1.0: 963 · ⅔: 56 · ⅓: 25 · 0.0: 12`.

The number that matters is **93 of 1056** — every cell not at 1.0 — because a
cell at 0.0 is unanimous but still differs from a cell at 1.0 and therefore
carries variance. "Non-unanimous" would give 81 and would be the wrong quantity:
it counts hesitation, where resolution needs *difference*.

By party: 21 of 528 sender cells and 72 of 528 receiver cells move at all. Five
of sixteen briefs have a literally constant sender claim series and contribute
zero sender resolution by construction; two do for the receiver.

The signal is real and it rests on 8.8% of the data.

## 4. H4 was reported as not supported. That was our defect, not the data's

`Φ_sender − Φ_receiver = (C_s − O) − (C_r − O) = C_s − C_r`. The observed term
cancels **identically**, so the pinning cannot touch H4 at all — and the
arithmetic confirms it: `0.980429 − 0.929924 = 0.05050505`, exactly the reported
value.

The [pre-registration](PREREGISTRATION.md) names the **brief** as the
exchangeable unit, and both parties are measured on the same sixteen briefs. The
runner built H4's confidence interval from the paired per-brief differences and
computed its p-value with an **unpaired two-sample** permutation. One hypothesis
got a paired interval and an unpaired test, which is why the results file
carries `"supported": true` beside `"significant_at_005": false` — a
contradiction sitting in the record, unremarked, until it was read.

The paired sign-flip test the design implies, on the same data, 100 000 draws:

```
per-brief differences:  11 positive, 3 zero, 2 negative
mean                    +0.0505
unpaired (as computed)  p = 0.3849
paired   (as designed)  p = 0.0033
```

**H4 is supported.** The sender is worse calibrated than the receiver, which is
the direction the human literature predicts — in Keysar & Henly's Experiment 2,
overhearers who knew the intended meaning but did not speak showed no bias. The
mechanism ports.

This is a conformance repair, not a change of plan: the analysis specification
named one exchangeable unit and the code used it for the interval and abandoned
it for the test. `paired_permutation` now exists in the library with this case
in its docstring.

## 5. H5 measured the right thing with an estimator that could not fail

H5 predicted that `Φ` rises where fidelity falls, and reported
`corr(fidelity, Φ) = −0.9662`, p = 0.0005.

Counterfactual claim vectors were constructed in which the parties track
observed agreement at slope `β` — `β = 1` being perfect calibration — and the
statistic recomputed:

| β | 0.00 | 0.25 | 0.50 | 0.75 | 0.90 | 0.95 | 0.99 | 1.00 |
|---|---|---|---|---|---|---|---|---|
| corr(fid, Φ) | −0.977 | −0.977 | −0.977 | −0.977 | −0.977 | −0.977 | −0.977 | +0.477 |

**Identical to four decimal places at every level of calibration except exactly
1.0.** The correlation would have read ≈ −0.98 if the parties had been 99% well
calibrated. It carries essentially no information about the quantity H5 exists
to measure.

The column that *does* carry it is `sd(Φ)`, which scales as `(1 − β)`:

| β | 0.00 | 0.25 | 0.50 | 0.75 | 0.90 | 0.99 | 1.00 |
|---|---|---|---|---|---|---|---|
| sd(Φ) | 0.156 | 0.117 | 0.078 | 0.039 | 0.016 | 0.002 | 0.000 |

**Reproduce both tables:** [`metrics/validation/beta_sweep.py`](../../metrics/validation/beta_sweep.py).
It reads the committed results file, recomputes H5 from the raw record as a
check (−0.9662, matching), and prints the sweep and the covariance
decomposition. Until 2026-07-31 these numbers existed only as prose in this
section — no file produced them — which is
[the audit hole of two days earlier](../../journal/2026-07-30-two-audit-holes.md)
repeated in a document about that hole.

Covariance decomposition of the reported effect:

```
cov(fid, Φ) = cov(fid, claimed) − cov(fid, observed)
   −0.05453 =        +0.00155   −        0.05608
```

Claim movement contributes **−2.8%**; outcome movement contributes **102.8%**.

The phenomenon H5 was reaching for is real. The statistic chosen to catch it was
not capable of missing.

## 6. What the run actually measured — post-hoc, and labelled as such

Not pre-registered. Identified after the fact, and reported here as a
hypothesis for a successor rather than as a result of this one.

The informative quantity is the **calibration slope**: how much a claim moves
when the outcome moves. Perfect calibration gives 1.0; total unresponsiveness
gives 0.0.

```
pooled     β = +0.0386    95% CI [−0.1730, +0.1266]
sender     β = −0.0375    95% CI [−0.1905, +0.0394]
receiver   β = +0.1147    95% CI [−0.1706, +0.2538]
```

Zero of 20 000 bootstrap resamples reached β ≥ 0.5. The sender's point estimate
is faintly **anti**-calibrated.

Nothing in the design forced this. On the worst brief, `r070_1`, observed
agreement was **0.5152** — calibration required a claim near 0.52, the entire
interval below was available, and the parties said **0.9646**.

> ~~**The parties' confidence is very nearly unresponsive to how much actually
> transferred.**~~

That sentence is what this run supported, and it was stronger than what was
pre-registered. Both halves of that had to be said together, which is why the
successor was registered rather than the sentence promoted.

**Superseded 2026-08-02 by [E-002c](../E-002c-calibration-slope/FINDINGS.md).**
This interval contained zero, so "very nearly unresponsive" was the most this
data could say. A pre-registered run on 24 briefs puts the pooled slope at
`+0.1299`, interval `[+0.047, +0.223]` — clear of zero. Confidence *does*
respond, at about an eighth of the rate calibration requires. The unresponsive
party is the **sender** alone: `β_sender = −0.0200` with an interval spanning
zero, against `β_receiver = +0.2797` with an interval clear of it.

The direction here replicated. The magnitude did not, and reporting the stronger
sentence as a finding would have been wrong in a way this run could not have
detected.

## 7. Against the human literature, we discriminate worse, not better

The results file sets `0.9016 / 0.0295` beside Keysar & Henly's `0.46 / 0.12`,
which invites the reading that the models replicated the asymmetry two and a half
times more strongly. Normalised against each study's **own** claim rate, the
opposite holds:

| | claim rate `c` | forced by pinning `2c−1` | measured | attributable to pinning | residual discrimination |
|---|---|---|---|---|---|
| Keysar & Henly (2002) | 0.72 | 0.44 | 0.34 | 77.3% | **22.7%** |
| E-002b | 0.955 | 0.910 | 0.872 | 95.8% | **4.2%** |

The models discriminate roughly **five times worse** than the human speakers.
And a second thing follows that this repository has never said: **Keysar &
Henly's own headline is itself mostly base-rate.** Both directions of that
sentence are new and neither is flattering to a naive comparison.

## 8. What this costs the theory

[definitions §5](../../theory/definitions.md) defines `Φ` as a **level** —
claimed minus observed — with three regimes keyed to its sign. Invariance is a
**slope**, and §5 contains no derivative, variance or slope term anywhere.

So "confidence does not respond to transfer" cannot be reported as a measurement
of `Φ` as currently defined. It needs a companion quantity, and naming it is a
theory change that belongs in its own commit with its own review — not smuggled
in as an interpretation of this run.

Recorded as a task, not performed here.

**Discharged 2026-08-02.** `β` is defined in
[definitions §5.1](../../theory/definitions.md) and
[lexicon](../../lexicon.md), pre-registered in
[E-002c](../E-002c-calibration-slope/PREREGISTRATION.md) before its data
existed, and measured there. The order is the point and it is dated: the
quantity was named first.

## 9. What must not be claimed

- **Not** that phantom agreement was measured at +0.2961. That number is the
  pinning stated as a level, and reporting it as the field's central quantity
  would be reporting one fact five times.
- **Not** that H5 confirms Φ tracks fidelity. Its estimator returns the same
  value against a 99%-calibrated counterfactual.
- **Not** that the asymmetry is stronger than in humans. Normalised, it is five
  times weaker.
- **Not** that the calibration slope is a pre-registered finding. It is not, and
  a successor must commit it before collecting.
- **Not** that any of this generalises. One model in both roles, one domain,
  n = 16 draws, sixteen briefs. A model predicting its own copy is the easiest
  case for calibration, which makes a positive H1 conservative and everything
  else narrower than it looks.

## 10. The uncomfortable part

Four of five hypotheses came back supported, with p-values of 0.0005, on the
first run this programme ever completed. Every one of those numbers is correct.

Taken at face value they would have read as a strong confirmation. What they
mostly show is that the parties said "yes" to almost everything, and that a
programme which had spent a week building gates against fooling itself still
needed an adversarial pass to notice — because the trap this time was not a
broken instrument or an unexecuted code path, but **five true statements about
one fact**, arriving with the shape of a result.

The one hypothesis the pinning could not reach was reported as a failure,
because of an unpaired test where the design said paired.

---

*Raw record: [`results/E-002b-20260731T064958Z.json`](results/). This document is licensed CC BY 4.0.*
