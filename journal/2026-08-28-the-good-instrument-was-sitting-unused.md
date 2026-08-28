# Three laws were blocked by the wrong instrument

**2026-08-28.** Nine days that began by trying to test [L1](../theory/laws.md#l1)
and ended by finding that the reason three laws have stood unattacked since
founding was never the ideas, and never — as I published mid-way — the
programme's instruments in general. It was the one instrument every experiment
happened to reach for.

## E-006 died at zero model calls, on a gate it set for itself

The ablation ladder for L1 was pre-registered with a power calculation committed
*before* collection and a rule that below 0.80 it would not run. It returned
**0.117**. The null returned 0.023 against a nominal 0.025, so the test was
calibrated — not broken, blind.

Holding the design fixed, the probe count needed for 0.80 power:

| probes | 32 | 64 | 128 | 256 | **512** |
|---|---|---|---|---|---|
| power | 0.105 | 0.245 | 0.355 | 0.525 | **0.870** |

[Void before collection](../experiments/E-006-ablation-ladder/VOID.md). 2 880
calls not spent, and a fact bought instead: L1's concavity limb needs about 512
probes and the largest measure here has 34.

My first power calculation was wrong and is recorded — it bootstrapped the eight
*rungs* where the pre-registration declares the thirty-two *probes*. Corrected,
the verdict held. But a power calculation that does not implement its own
declared decision rule is not a power calculation; it failed safe by luck.

## So I asked the same question of the rest of the roadmap, and got it wrong

Probe-bootstrapping E-002c's raw draws gave the noise the programme actually has,
and the answer looked like a ceiling: E-003's expected asymmetry of 0.219 sits
under the 0.338 that 32 probes resolve; E-007's L4c splits the probes into
classes and resolves 0.479. I wrote *"the instrument is the binding constraint on
this programme, not the ideas"* and published it.

**That file computed its MDEs from raw probe counts**, an hour after
[retraction 15](../RETRACTIONS.md) established that `MERIDIAN-IX32`'s 32 probes are
about nine independent templates. Correcting my own arithmetic found the thing
worth finding:

| measure | raw | effective @0.85 | pairs at Jaccard ≥ 0.8 |
|---|---|---|---|
| `MERIDIAN-34` | 34 | 10 | 25 |
| `MERIDIAN-33` | 33 | 9 | 25 |
| `MERIDIAN-IX32` | 32 | 9 | 18 |
| **`RIVERSIDE-30`** | 30 | **25** | **0** |

Zero near-duplicate pairs against eighteen to twenty-five, and not a length
artifact — Jaccard over word sets is nearly length-blind and separates them the
same way. **Every published MERIDIAN result rests on about nine effective
probes.**

`RIVERSIDE-30` is also the only measure here whose keys were ruled on by readers
who did not write them. The best-adjudicated and least-templated measure in the
repository is the same file, and it had been used in exactly one experiment —
[E-004](../experiments/E-004-disagreement-detector/VOID.md), which is void.

## It has headroom, and the divergence belongs to the probes

Nobody had ever run it against a brief. Predicted ≥ 3 diverged per message
beforehand; measured **10.00 of 30** against a gate of 3, at ~400 words rather
than the 230 operating point, which is the conservative direction.

Then the same three briefs to a second reader, with the eight always-diverging
probes named in the prediction file first. Predicted Jaccard ≥ 0.4; measured
**0.654**.

| | `MERIDIAN-IX32` | `RIVERSIDE-30` |
|---|---|---|
| `gpt-oss` diverged | 9 of 32 | 13 of 30 |
| `qwen` diverged | **2 of 32** | **12 of 30** |
| strict subset? | **yes** | **no** |

On MERIDIAN the stronger reader simply lost less and its losses nested inside the
weaker one's — an *ability* difference. On RIVERSIDE both lose comparably and
lose the same things, which is what it looks like when the probes rather than the
readers carry the signal. So pairing works here (×2.46 and ×1.80, reader-dependent)
where on MERIDIAN it bought exactly nothing.

**The ceiling was MERIDIAN's, not the programme's**, and the sentence I published
is struck where it stands.

## Two smaller things, one of them satisfying

[Retraction 17](../RETRACTIONS.md): E-002c computed its noise floor between the
**sender and PRIOR** and divided **sender-versus-receiver** fidelities by it. The
sender is a point mass on all 33 probes and PRIOR is not, so the mismatched floor
was an order of magnitude too large and inflated the whole ladder — and because
the matched floor falls as cost rises, it *steepened* the column as well. `β`, the
registered quantity, never reads that column and is untouched. The estimator now
refuses the mistake: `fidelity_from_draws` takes draws rather than floats, so the
mismatch cannot be written.

And `T30`. `gpt-oss` answered it against its adjudicated key twice, seventeen days
apart, and I left it standing unexplained rather than dropping it. `qwen`'s sender
answers with the key, agreeing with all three blind adjudicators. It was one model
being reliably wrong about one probe — **the adjudication standard was vindicated
by its own anomaly.**

## Where it leaves the roadmap

E-003 is still blocked, for a reason I had to correct myself on twice. Not power:
`RIVERSIDE-30` resolves 0.135–0.183 against an expected 0.219. L2's sharper form
needs a model pair whose **domain prior and general capability disagree**, and
`qwen` is stronger or level on both domains available. Measuring only that an
asymmetry exists is [retraction 5](../RETRACTIONS.md), withdrawn as tautological.

**Blocked on model selection.** Which is a better position than blocked on the
instrument, because a third model is a download and a probe measure is a month.

---

*This document is licensed CC BY 4.0.*
