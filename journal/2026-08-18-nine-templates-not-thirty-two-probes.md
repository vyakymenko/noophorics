# The measure was nine templates and every p-value counted thirty-two

**2026-08-18.** `MERIDIAN-IX32` has thirty-two probes. It does not have
thirty-two independent readings, and three published significance levels were
computed as though it did. They are withdrawn as [retraction
15](../RETRACTIONS.md).

The defect is visible in two lines of the probe file:

| probe | prompt | key | stability |
|---|---|---|---|
| `X17` | …Combined figure count is **70**. | `HANDLED` | fails the gate |
| `X18` | …Combined figure count is **71**. | `RETURNED` | passes |

One token apart, opposite verdicts. `X21`/`X22` differ the same way (8 → 7) and
`X24`/`X25` likewise (30 → 21). These are minimal pairs straddling a numeric
threshold, which is careful probe design and ruinous arithmetic: Fisher's exact
test over thirty-two rows treats a pair that shares 99.5% of its text as two
independent elicitations.

Single-link clustering of the prompts gives **nine clusters** at similarity
0.80–0.85, the largest holding eleven probes, with all observed instability
inside two of them.

## Why there is no corrected number

The instinct is to recompute at the cluster level and publish that instead. It
does not survive contact with the data: the cluster-level `p` runs from
**0.111 at threshold 0.80 to 0.006 at 0.95**. Any figure quoted is a report on
where the clustering line was drawn, not on the measure. So the entry withdraws
the p-values and substitutes nothing, which is the honest shape of this
particular correction.

That makes #15 a kind this ledger had not held. Retractions 12, 13 and 14
withdraw a **quantity** — a number replaced by a better number. This one
withdraws a **warrant**: the arithmetic was performed correctly on a sample
without the structure the test assumes. It also reaches backwards, because one
of the p-values it strikes was retraction 14's own supporting evidence.

The counts are untouched. Four of nine is still four of nine.

## What survives is sharper than what it replaces

Of **1 440** `gpt-oss:120b` sender draws, nineteen are non-key, and **all
nineteen fall on `R5`-tagged probes** — the paired-submission rule. No probe
outside `R5` has ever returned a margin below 10, in any pass, at any gate. The
individual draw is a unit that genuinely is independent, and the concentration
is not an artifact of where a threshold sits.

Two things keep that from being another post-hoc tag hunt. The `R5` label was
committed at **2026-08-10 09:29:56**, nine hours before the first `IX32` sender
pass — prior to every instability datum, and not drawn to fit it. And selecting
`R5` from among ten rules is corrected by exact enumeration over all
`C(32,4) = 35 960` relabelings, which returns `p = 0.0016`. The uncorrected
`0.00042` was never a measurement: `C(6,4)/C(32,4)` is what *any* six-probe
family capturing all four would print, so quoting it to four figures implied a
resolution the design cannot deliver.

None of this reopens the repair route. `R5` carries **45 of the 49** divergence
events, so the region holding all the instability holds nearly all the signal.
What it corrects is a generalisation: "harder is where the instability lives"
should read "one rule is where both live."

## Three things found while looking at something else

**The reuse guard asserted a model it had never read.** `headroom_check.py`
printed *"sender reused from X (same model, spec, measure and n)"* while
comparing only the draw count and the measure id. The function never returned
the model, so nothing could have compared it — a `gpt-oss` sender would have
been accepted verbatim under `--model qwen3.5:35b`, with the log affirming the
match. Not a gate that cannot fail: a claim printed where no gate existed.

**The exposure log recorded half a measure for eight days.** `157b80f` took the
probe file from sixteen probes to thirty-two and did not touch `EXPOSURE.md`.
The file already contained the paragraph explaining why this happens — *"the
exposure grew because the agent kept working"* — written six days before the
drift it describes. It was caught by an agent reading the log in order to add
its own row, which is luck rather than a mechanism. Nothing checks that file.

**The next run costs five times what the README says.** Measured at the
runner's real settings, `qwen3.5:35b` is **123.9 s/call** against
`gpt-oss:120b`'s **5.8 s/call**, a factor of twenty-one. "About eleven hours"
for five qwen sender passes is fifty-five.

## What is running now

`qwen3.5:35b` as receiver on `MERIDIAN-IX32`, which had never been done — the
existing qwen file carries a sender and nothing else. A
[prediction](../probes/meridian-ix16/PREDICTION-qwen-receiver.md) was committed
before it started, turning on one probe: `X19` is tagged `R8` and not `R5`, it
never diverged for `gpt-oss` across twelve messages, and qwen's sender wobbles
on it. If divergence follows a model's *own* sender margins, `X19` diverges. If
it follows the rule, it does not.

The first of six messages has landed and the prediction is already wrong in an
interesting direction. On `fluent0` qwen diverged on `X11` and `X26` — the
**same two probes** `gpt-oss` diverged on, from the same brief. Neither is one
the prediction named. Since every sender mode equals the key in every pass, that
means two architectures independently lost the same two qualifiers, which
suggests divergence is a property of what the brief drops rather than of who
reads it. One message is one message, and `X19` has five more chances.

---

*This document is licensed CC BY 4.0.*
