# Seven of the nine probes measured the reader, not the transfer

**2026-08-19.** `MERIDIAN-IX32` has been read by a second architecture, and the
route it was built to open is closed. The run also answers a question the
measure could not have asked while only one model had ever read it.

`qwen3.5:35b` had never been run as a receiver against this measure — the file
that exists for it carries a sender and nothing else. Twenty-eight and a half
hours, 1 920 calls, the six briefs already on disk.

| message | qwen diverged | `gpt-oss` diverged |
|---|---|---|
| `fluent0` | 2 | 2 |
| `fluent1` | 1 | 5 |
| `fluent2` | 2 | 2 |
| `terse0` | 0 | 0 |
| `terse1` | **0** | **7** |
| `terse2` | **0** | **7** |
| total | **5** | **23** |

**0.83 diverged probes per message against a gate of three**, where `gpt-oss`
gives 3.83 on the identical briefs.

## The prediction failed, which is the useful part

A [prediction](../probes/meridian-ix16/PREDICTION-qwen-receiver.md) was committed
before the run, in its own commit, naming `X16` and `X19`. It scored **0 of 2**,
with `X11` and `X26` diverging against it.

The hypothesis it tested was that a probe diverges where *that model's own*
spec-holder is least certain. On `gpt-oss` that is nearly exact — every probe it
ever wavered on discriminates. It does not transfer. qwen's two wobble probes
never diverged, and **both of qwen's actual divergences sit at sender margin
10**, its highest confidence. Sender margin predicts one model's losses at 7 of 7
and the other's at 0 of 2, so it is not the cheap pre-transfer detector
[Problem 11](../theory/open-problems.md) asks for.

## What two readers buy that one cannot

qwen's divergence set is a **strict subset** of `gpt-oss`'s. Nothing is lost by
qwen and kept by `gpt-oss`. That splits the measure in a way a single reader
cannot:

| | probes | lost by |
|---|---|---|
| both spec-holders unanimous, both receivers wrong | `X11`, `X26` | both models |
| `gpt-oss` uncertain, qwen unanimous | `X06 X07 X16 X17 X21 X22 X24` | `gpt-oss` only |

The first class is transfer loss: the brief demonstrably fails to carry the
qualifier and two independent readers confidently get it wrong. The second is the
reader's own uncertainty wearing transfer loss's clothes — all seven are `R5`,
six sit at `gpt-oss`'s wobble points, and a model that is unanimous on them loses
none of them.

So of the nine probes that discriminate here, **seven are ones a second
architecture does not lose at all**, and `MERIDIAN-IX32` measures
model-independent transfer loss on **two of its thirty-two probes**.

**This entry's central claim is withdrawn — [retraction
16](../RETRACTIONS.md) — on the day it was published.** It said the headroom
"was substantially one model's hesitation." That asserts a cause, and three
things kill it.

*The statistic was not like-for-like.* "Six of seven sit at gpt-oss's wobble
points" compares `gpt-oss`'s **minimum over four** sender passes against
`qwen`'s **single** pass. More passes, more chances to show a low margin.
Counted one pass each it is **2 of 7**.

*No reader-specific term is needed.* One difficulty per probe plus a single
reader-ability gap — **no reader×probe interaction at all** — fits at deviance
10.54 on 8 df, `p = 0.229`, gap 2.20 logits. The strict subset is what that
model predicts anyway.

*And it is impact, not differential functioning.* [Dorans & Holland
(1992)](../theory/prior-art.md) require conditioning on the attribute measured
before an item may be called differentially functioning; an unconditioned
difference between readers of unequal ability is **impact**, with Simpson's
paradox as the named hazard. I never conditioned on the 2.20-logit gap.

The whole framing was also prior art, which a literature search found the same
day: the reader is a **fixed facet** in generalizability theory, and Brennan
(2003) states as a theorem that with all facets fixed "no generalization is
involved, and all error variances are zero." Recorded as [prior-art
§11](../theory/prior-art.md); the drafted open problem was **refused entry**.

The counts survive — qwen loses 2 of 32, `gpt-oss` 9, strict subset. Why is
open. **The title of this entry is wrong and is kept**, because the URL is
published and renaming it to hide the error would be the tidier lie.

That is the closing of the escape route, and it closes for a reason nobody
proposed. The worry was that qwen would be stable but saturated. It is neither —
it diverges, just barely. Choosing the stable model costs nearly all the signal,
so stability and discriminating power trade off *across models* exactly as
[they were found to trade off across probes](../probes/meridian-ix16/).

## Two corrections this run forced

**The cost was overstated twice, in opposite directions.** The README said five
qwen sender passes would take about eleven hours; measured, qwen runs at 53.5
s/call, making it about twenty-four. But the prediction file said this run would
take sixty-six hours, from a timing measurement taken while two other jobs were
competing for the machine; it took twenty-eight and a half. A rate measured under
load is not a rate.

**The reused sender now carries its draws.** Mean divergence is reported for all
six messages rather than refused, because the reuse path had been collapsing the
sender to a point mass and discarding raw draws the file already contained. The
same commit stopped it asserting a model it had never read.

## What this leaves

Two probes of thirty-two produce divergence both readers agree on, and the design
rule that produced the other thirty is not a rule for producing those two. A
successor needs `X11`/`X26`-shaped probes and no account yet of what shape that
is — `X11` is the only non-`R5` probe in either divergence set, which is the one
hint on offer.

The single qwen sender pass remains a single pass, and the two-class split rests
on its margins.

---

*This document is licensed CC BY 4.0.*
