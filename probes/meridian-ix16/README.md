# MERIDIAN-IX32 — probes that need two rules to combine

*The directory is named for where this started, sixteen probes; the measure is
now thirty-two. The name is left alone because links resolve to it.*

**Status: validated on one model, not adjudicated.** The admission rule below was
recorded before the validating run, and the result is in
[`validation.json`](validation.json).

**All 16 of 16 admitted**, every one with the sender unanimous at 10/10 on the
hand-derived key. The specification decides all sixteen cases and `gpt-oss:120b`
recovers all sixteen from it. Nothing was cut.

**Per-probe divergence at 221–233 words: 0.104**, against `MERIDIAN-34`'s 0.049
on the identical six messages — twice the sensitivity per probe. But 12 of the 16
probes never discriminated at all: ten events sit on `X11`, `X06`, `X07` and
`X16`. At this rate sixteen probes yield 1.67 diverged per message, **below**
E-002c's outcome-variation gate of three; clearing it needs about **29** probes
of this class, and 34 would expect 3.5.

So sixteen was a working prototype and not yet a usable measure. It was half of
one.

## The second sixteen, and a prediction recorded before they ran

Of the first sixteen, **twelve discriminated nothing**. All ten divergence events
sat on four probes — `X11`, `X06`, `X07`, `X16` — and those four share a shape the
other twelve do not:

- a **number** meeting a **regime**: the paired figure maximum of 70 against the
  solo 45, the shared minimum of 8, R4's exact five years inside a pair
- **verdict precedence**: R9's PADDED losing to any second failure

What discriminated nothing was categorical: R7's override, R6's Track D
exemption, R10's clock reset. A brief seems to keep a rule *as a rule* and lose
the qualifier attached to a number.

`X17`–`X32` test that. Twelve are number-meets-regime and **predicted to
discriminate**; four are categorical overrides and **predicted not to**. Each
probe carries the prediction in its own `predicted_discriminating` field, so the
result is scored rather than remembered — and so a prediction that fails cannot
be quietly reread as the one that succeeded.

If the twelve beat 0.104 and the four fall below it, the design rule is: *write
probes where a number's applicability depends on a regime the brief has room to
state only once.* If they do not, the rule is wrong and sixteen more probes of
the wrong kind is what this measure will have cost.

`MERIDIAN-34` is saturated at the message lengths this programme's fluency line
requires. Both local models answer it correctly from the source specification —
34 of 34 — and their receivers reproduce nearly all of it from a 230-word brief:
`Â = 0.941–0.971` for `gpt-oss:120b` and `1.000` for `qwen3.5:35b`.
[Problem 15](../../theory/open-problems.md) has the numbers.

The only probes that survived that saturation were its **interaction**-tagged
ones: 6 of 9, against 3 of the other 25, and the three that recur across two
independent datasets are all interaction. This measure is that class and nothing
else.

## The design rule

A summary compresses. What it compresses *away* first is not the hardest rule
but the **least compressible clause** — the qualifications that only matter when
two rules meet:

- R10 resets the R3 venue clock to the withdrawal date, *and* a withdrawal is
  not an acceptance under R4
- R6 exempts a Track D manuscript from R2 **only**, and from no other rule
- R7 overrides everything "including R9"
- R9's PADDED verdict applies only when R8 is the *sole* failure
- R5 requires both manuscripts to satisfy R1 and R2 independently, but only one
  of them to satisfy R3, and permits exactly two

Every probe here turns on one of those joints. None can be answered from a rule
stated in isolation, which is what a 230-word brief has room for.

## The admission rule, declared in advance

A probe is admitted to the measure only if, on the **sender** — the party
holding the full specification —

1. the modal answer over 10 draws equals the key, and
2. the modal margin is **at least 8 of 10**.

Failing (1) means the probe is wrong or the specification does not decide it, and
a probe whose answer the spec-holder cannot recover is not a hard probe but a
defective one. Failing (2) means the answer is unstable at the source, which
[Problem 14](../../theory/open-problems.md) says makes the modal reduction a
coin-flip — and a measure built to fix saturation must not buy its headroom by
importing ambiguity.

**Probes that fail are cut, not rewritten.** Rewriting a probe until the sender
agrees with me is fitting the instrument to the answer I wanted.

The measure is worth having only if it then shows what `MERIDIAN-34` cannot:
receiver divergence at 230 words. That number decides whether this file is an
instrument or a discarded attempt, and it is not known as this is written.

## Provenance

Authored 2026-08-07 by `claude-opus-5`, working in this repository. Recorded in
[EXPOSURE.md](../../EXPOSURE.md): that model can no longer serve as a subject
against this measure, and cannot judge whether these probes are good. The keys
were derived from the specification by hand and are checked here only by the
sender's own answers, which is a weak check — it can catch a probe the spec does
not decide, and cannot catch a probe where the author and the model are wrong in
the same direction. `probes/riverside-30/ADJUDICATION.md` is the standard this
has not met; independent adjudication is owed before any experiment registers
against it.

---

*This document is licensed CC BY 4.0.*
