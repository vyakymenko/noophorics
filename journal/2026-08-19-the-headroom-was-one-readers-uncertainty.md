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
architecture does not lose at all.** What looked like this measure's headroom was
substantially one model's hesitation. Strip that and `MERIDIAN-IX32` measures
model-independent transfer loss on **two of its thirty-two probes**.

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
