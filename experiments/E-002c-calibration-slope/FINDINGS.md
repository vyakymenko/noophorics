# E-002c — findings

**The first pre-registered positive result this programme has produced.** All
six gates passed, all twenty-four briefs analysed, all four registered
hypotheses resolved.

Three of the four came back supported. The fourth failed, and its failure is the
most useful thing here: it corrects a sentence this repository was already
saying.

---

## 1. The registered result

| | value | 95% CI | p (Holm) | |
|---|---|---|---|---|
| **H1** `β < 0.5` | +0.1299 | [+0.0474, +0.2234] | interval decision | supported |
| **H2** `β` indistinguishable from 0 | +0.1299 | [+0.0474, +0.2234] | interval decision | **not supported** |
| **H3** sender less responsive than receiver | +0.2997 | [+0.1509, +0.4713] | 0.0009 | supported |
| **H4** resolution survives the finer grid | +0.3074 | [+0.2156, +0.4035] | 0.0002 | supported |

H1 and H2 carry no p-value by design: the claim is about a magnitude, and a
p-value against a nil null answers a question nobody asked. They are decided by
where the interval falls, which is what the
[pre-registration](PREREGISTRATION.md#5-analysis-plan) says.

```
β pooled     +0.1299   CI [+0.0474, +0.2234]
β sender     −0.0200   CI [−0.0903, +0.0490]     contains zero
β receiver   +0.2797   CI [+0.1386, +0.4391]     excludes zero
β pooled, corrected for attenuation (reliability 0.7153)   +0.1816
```

`β` is the calibration slope: how far a claim moves when the outcome moves.
Perfect calibration is 1.0; total unresponsiveness is 0.0.

## 2. The outcome the pre-registration named in advance

Its [§7](PREREGISTRATION.md#7-what-each-outcome-means) lists four ways the run
could land. This is the second:

> **H1 holds, H2 fails** — responsiveness is real but far below calibration.
> Also a result, and a more interesting one for engineering: a partial signal
> can be amplified.

Writing that down before collecting is why this section can be short. There is
no argument to have about whether a nonzero-but-small β counts as a finding.

## 3. This corrects something we were already saying

[E-002b §6](../E-002b-phantom-agreement-ladder/FINDINGS.md) reported a *post-hoc*
slope and concluded, in a pull-quote:

> ~~The parties' confidence is very nearly unresponsive to how much actually
> transferred.~~

That was honest about its own status — labelled post-hoc, flagged as needing a
successor to commit it before collecting. The successor has now run, and the
sentence is **too strong**.

| | pooled | sender | receiver |
|---|---|---|---|
| E-002b, post-hoc, n = 16 | +0.0386 `[−0.173, +0.127]` | −0.0375 | +0.1147 |
| E-002c, registered, n = 24 | **+0.1299** `[+0.047, +0.223]` | −0.0200 | **+0.2797** |

The direction replicates and the magnitude does not. E-002b's interval contained
zero, so "very nearly unresponsive" was the most that data could say. With a
better-powered instrument the interval clears zero: **confidence does respond to
transfer, at about an eighth of the rate calibration requires.**

The corrected sentence is:

> **The receiver's confidence tracks transfer at a bit over a quarter of the
> rate calibration requires — `β = 0.28`. The sender's does not track it at
> all — `β = −0.02`, interval spanning zero.**

Both halves are measured, and the second is the sharper claim: `β_sender`'s
interval contains zero and its point estimate is faintly negative, on 24 briefs
spanning observed agreement from 0.485 to 0.970.

## 4. The sender and the receiver are not the same instrument

This is the part E-002b could not resolve and this run can.

```
                mean     sd       range            variance vs outcome
observed        0.7475   0.1591   0.485 – 0.970    —
claimed sender  0.9752   0.0357   0.845 – 1.000    19.8 : 1
claimed receiver 0.8843  0.0740   0.731 – 0.983     4.6 : 1
```

The sender sits at 0.975 and barely moves while the outcome moves across half
its range. The receiver moves twice as much and its slope clears zero. H3 puts a
number on the gap: **+0.2997**, `[+0.151, +0.471]`, Holm-corrected p = 0.0009,
by a paired sign-flip on the per-brief `β` contributions. That p-value is not
the one this document first reported — see §6.

Per rung, the asymmetry is visible without any statistics:

| rung | observed agreement | claimed sender | claimed receiver | fidelity |
|---|---|---|---|---|
| 30 | 0.631 | 0.9574 | 0.8451 | +0.228 |
| 70 | 0.692 | 0.9820 | 0.8810 | +0.456 |
| 110 | 0.778 | 0.9944 | 0.8737 | +0.606 |
| 150 | 0.889 | 0.9669 | 0.9371 | +0.848 |

Observed agreement climbs 0.26 and fidelity climbs 0.62 across the ladder. The
sender's claim ends **lower than it started at rung 110** and never leaves the
0.957–0.994 band.

## 5. H4: the earlier resolution was not a granularity artifact

E-002b measured per-probe resolution at **+0.1408** on a four-value claim grid
where 91.2% of cells sat at exactly 1.0, and said plainly that the signal rested
on 8.8% of the data. H4 asked whether that was signal or grid.

At `n_c = 9`, which admits ten distinct claim values:

```
all ten values were used
1270 of 1584 probe-party cells at 1.0     80.2%
 314 moving                               19.8%
resolution  +0.3074   CI [+0.2156, +0.4035]
```

Resolution more than **doubled** on the finer instrument. The parties do know
something about *which* probes diverged, and the coarse grid was hiding it
rather than manufacturing it.

The pinning is still the dominant feature — four cells in five are at 1.0 — but
it is weaker than E-002b's 91.2%, and the sender/receiver split above shows
where the remaining pinning lives.

## 6. H3 was tested on the wrong quantity, and it is the same shape as last time

Found by re-reading this run's own code after the findings were written, not by
a check. The conclusion does not move. What was published for two days was a
p-value belonging to a different quantity.

H3's **value** and **interval** are a difference of *slopes*:
`β_receiver − β_sender = +0.2997`, bootstrapped over briefs. Both correct, both
what the hypothesis claims.

Its **p-value** came from a paired sign-flip on the per-brief *claim levels* —
`C_receiver − C_sender` — which is a difference of *means*. It was numerically
identical to `recorded_sender_worse_than_receiver`, sign-flipped: `−0.0909`
against `+0.0909`, p `0.0001` against `0.0001`. So a registered hypothesis was
being significance-tested by a statistic the analysis plan explicitly excludes
from the hypothesis family, and Holm was dividing alpha over it.

The [plan](PREREGISTRATION.md#5-analysis-plan) says H3 is tested "by a **paired**
sign-flip permutation on the per-brief `β`-contributions". An OLS slope is a sum
of per-brief terms, so the difference decomposes exactly:

```
d_i = (O_i − Ō)·[(C_r,i − C̄_r) − (C_s,i − C̄_s)] / Σ(O − Ō)²      Σ d_i = β_r − β_s
```

Checked against the reported effect before use: the contributions sum to
`+0.299731`, the reported value is `+0.299731`. Sign-flipping them, 10 000
draws, same seed:

```
as registered   p = 0.0009   (Holm 0.0009)   19 of 24 contributions positive
as computed     p = 0.0001   — the level gap, a different quantity
```

**H3 still holds.** One number moved in the results file and nothing else: raw
draws, gates, every other value, interval and p are byte-identical across the
correction.

The part worth keeping is not the repair. It is that this is
[E-002b's H4](../E-002b-phantom-agreement-ladder/FINDINGS.md#4-h4-was-reported-as-not-supported-that-was-our-defect-not-the-datas)
again — an interval on one quantity and a test on another — in the experiment
registered to avoid exactly that, in a function whose comment three lines above
the defect *cites that defect by name*. Knowing the failure mode, writing it
down, and citing it in the code did not prevent committing it a second time.

What would have caught it is not vigilance. It is a check that asserts the
statistic a hypothesis reports and the statistic it tests are computed from the
same numbers — and no such check exists. Recorded as a task, not performed here,
because inventing it while correcting an instance of it is how a fix gets
fitted to one case.

## 7. What this settles in the theory

[E-002b §8](../E-002b-phantom-agreement-ladder/FINDINGS.md) recorded a debt:

> `Φ` is defined as a **level** — claimed minus observed — and §5 contains no
> derivative, variance or slope term anywhere. So "confidence does not respond
> to transfer" cannot be reported as a measurement of `Φ` as currently defined.
> It needs a companion quantity, and naming it is a theory change.

`β` is that quantity, and it is now measured under a registration that named it
before the data existed. It is added to
[definitions](../../theory/definitions.md) and [lexicon](../../lexicon.md) in the
same commit as this file, which is the review that debt asked for.

`Φ` and `β` are independent and both are needed. `Φ` says how far belief sits
from outcome; `β` says whether belief moves when outcome moves. A party can have
`Φ = 0` and `β = 0` — claiming the mean every time — and that party is
maximally uninformative while scoring perfectly on the older quantity. That is
the same argument [PRINCIPIA §7.2](../../PRINCIPIA.md) makes for bias versus
resolution, one level up.

## 8. What must not be claimed

- **Not** that confidence is unresponsive. It responds; the interval excludes
  zero. The unresponsive party is the **sender**, and that is a narrower claim
  than the one E-002b's post-hoc made.
- **Not** that `β = 0.13` is a property of language models. One model in both
  roles (`gpt-oss:120b`), one probe measure (MERIDIAN-33), one domain, 24
  briefs. A model predicting its own copy is the easiest case for calibration,
  which makes a *low* β conservative and everything else narrower than it looks.
- **Not** that the attenuation correction is the headline. Reliability is
  0.7153 and the corrected β is +0.1816; both are reported because the
  pre-registration says to report both and correct neither silently.
- **Not** that H3 shows senders are worse calibrated *in general*. It shows one
  model, given the sender's framing and the artifact it wrote, claims 0.975 and
  does not move. Whether that is about the role or about having authored the
  text is a separate experiment nobody has run.
- **Not** that the ladder shows a causal dose-response. Rung is message cost and
  the briefs were composed per rung; fidelity rising with cost is L1's
  territory, and L1 is not what this run registered.

## 9. Provenance

Collection ran 2026-07-31 19:06 to 2026-08-02 16:58 local, 28 512 model calls,
zero retries used. The
[results file](results/E-002c-20260802T135817Z.json) is what that run wrote.

A [third file](results/E-002c-20260803T121500Z.json) is the current record: the
same analysis with H3 tested on the quantity §6 describes. One p-value differs
from the second file; the draws and every other field are identical.

A [second file](results/E-002c-20260802T204415Z.json) carries the same analysis
re-run from the completed cache after three **reporting** defects were fixed in
the runner: H1 could not print as supported because the summary gated on a
p-value it deliberately does not have, H3's verdict was computed and never
recorded, and the declared multiplicity family listed five members where the
correction was applied to the registered four. Both files are kept. Every
computed field — every value, p, Holm-adjusted p, CI, gate, and all 28 512 raw
draws — is identical between them; the diff is verdicts and one declaration.

The re-run made **zero model calls**: `ollama` was not running while it
executed, so any attempt would have failed loudly rather than quietly redrawing.

---

*Raw record: [`results/`](results/). This document is licensed CC BY 4.0.*
