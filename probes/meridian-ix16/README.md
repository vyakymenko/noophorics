# MERIDIAN-IX32 — probes that need two rules to combine

*The directory is named for where this started, sixteen probes; the measure is
now thirty-two. The name is left alone because links resolve to it.*

## Where it stands

**32 probes, 28 stable, 2.00 diverged per message — it does NOT clear the gate.**

~~32 probes, 31 admitted, 3.33 diverged per message. That clears E-002c's
outcome-variation gate of three.~~ **Withdrawn 2026-08-07**, by applying the
admission gate the way it should always have been applied: repeatedly. Five
sender passes instead of one rejected four probes as unstable, and the measure
on the 28 survivors gives **2.00** diverged per message at a per-probe rate of
**0.071** — still above `MERIDIAN-34`'s 0.049 on the identical six messages, and
below the gate.

**And the four rejected probes are four of the nine that ever discriminated.**
Of the 23 probes that never discriminated, none was rejected. Fisher exact
`p = 0.0035`. Discriminating power and modal stability are not merely in tension
here, they are anti-correlated, and the headroom this measure appeared to have
was substantially borrowed from probes that are not stable observables.

Keys for `X01`–`X16` are independently derived by a second model. `X17`–`X32`
are adjudicated by nothing. Neither batch is adjudicated by a person.

**One defect fixed, one standing.** The admission gate is now applied across five
sender passes rather than one, which is what produced the withdrawal above. What
still stands: `terse0` returns zero diverged probes on every measure tried, so
even a measure that cleared the gate on the mean would not clear it on that
message.

Everything after this is the history in the order it happened, because how a
measure was arrived at is most of what tells you whether to trust it.

---

## The first sixteen

The admission rule below was recorded before the first validating run
([`validation.json`](validation.json)). All **16 of 16** were admitted, the
sender unanimous at 10/10 on every hand-derived key — a claim the second run
later qualified; see the last section.

Per-probe divergence was **0.104**, twice `MERIDIAN-34`'s, but 12 of the 16
probes never discriminated at all: ten events sat on `X11`, `X06`, `X07` and
`X16`. At that rate sixteen probes yield 1.67 diverged per message, **below** the
gate of three, and clearing it looked to need about 29.

So sixteen was a working prototype and not yet a usable measure. It was half of
one.

## The second sixteen, and a prediction recorded before they ran

Those four that discriminated share a shape the other twelve do not:

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

### It held

| group | n | rate | probes that fired |
|---|---|---|---|
| predicted **to** discriminate | 12 | **0.181** | 5 of 12 |
| predicted **not** to | 4 | **0.000** | 0 of 4 |
| the original sixteen | 15 | 0.078 | 3 of 15 |

Thirteen events on the first group, **zero** on the second across all 24
probe-message pairs. Fisher exact `p = 0.0339`.

The structure is sharper than the rate. Every one of the nine probes that ever
discriminated turns on the **paired regime** (`R5`, in seven of nine) or on
**verdict precedence** (`R9`, in four). Not one categorical override
discriminated, in either batch — `R7`, `R6` and `R10` are silent across 32 probes
and six messages.

**The design rule, earned rather than guessed:** a brief keeps a rule as a rule
and loses the qualifier attached to a number. Write probes where a number's
applicability depends on a regime, and the brief will state the number once and
drop which regime it belonged to.

### ~~The measure now clears the gate~~ — it did not, under a gate applied once

~~**3.33 diverged per message over 31 admitted probes**, against E-002c's
outcome-variation gate of 3.~~ True of single-pass admission and false of the
probe set. See the section below and the head of this file.

The narrow-clearance caveat stands and got worse: `terse0` returns zero on the
stable subset too, as it does on `MERIDIAN-34` and on `qwen`.

### And the admission gate itself is defective

`X06` was admitted at margin **10/10** in the first validation and **cut at 4/10**
in the second. Same probe, same model, same specification; the modal answer did
not change, its stability did.

So "16 of 16 admitted" was true of one measurement and not of the probe. An
admission rule applied once is not an admission rule — it is a snapshot, and
[Problem 14](../../theory/open-problems.md) is exactly about the difference. A
usable version of this measure needs the gate applied across **repeated** runs,
with a probe admitted only if it is stable in all of them. That is not done here,
and `X06` is left in the file, cut by the run that could see it, precisely so the
defect stays visible.

Note what that costs: `X06` discriminated 3 of 6 messages. The instability is
concentrated in a probe that was *working*, which is the uncomfortable direction.

### The gate was then applied properly, and it took the measure down with it

Five sender passes over all 32 probes, admitting a probe only if it returns the
key at margin ≥ 8 in **every** pass it appears in:

| rejected | why | did it discriminate? |
|---|---|---|
| `X06` | 4/10 in pass 2, 10/10 in the other four | yes, 3 of 6 messages |
| `X17` | 6/10 in pass 3 | yes, 3 of 6 |
| `X21` | 6/10 in pass 4 | yes, 3 of 6 |
| `X22` | 6/10 in passes 4 and 5 | yes, 2 of 6 |

**Four of the nine probes that ever discriminated; none of the twenty-three that
never did.** `p = 0.0035`. On the 28 survivors the measure gives 2.00 diverged
per message and 0.071 per probe, against 3.33 and 0.124 before.

The reading is uncomfortable and worth stating flatly: **at this operating point,
a probe that separates a spec-holder from a brief is markedly more likely to be
one whose own modal answer is unstable.** That is not a flaw in these sixteen
probes. It is [Problem 14](../../theory/open-problems.md) turning out to be the
binding constraint on the whole repair, rather than a caveat attached to it —
and it means "write harder probes" may not be a route to headroom at all, because
harder is where the instability lives.

### Confirmed on twice the messages

The anti-correlation above rested on nine discriminating probes and six
messages, which is thin for a claim that decides a research line. Re-run on
**twelve** messages, all four cells, same 32 probes, sender reused
([`validation-12msg.json`](validation-12msg.json)):

| | six messages | twelve messages |
|---|---|---|
| divergence events | 23 | **49** |
| probes that discriminated | 9 of 32 | **12 of 32** |
| unstable probes that discriminate | 4 of 4 | **4 of 4** |
| stable probes that discriminate | 5 of 28 | 8 of 28 |
| Fisher exact | `p = 0.0035` | **`p = 0.0138`** |
| mean diverged per message, stable probes only | 2.00 | **2.08** |

It holds, and the sharpest way to say it is new:

> **The four unstable probes are 12% of the measure and carry 49% of its
> divergence events.**

Half the signal comes from an eighth of the probes, and that eighth is exactly
the eighth that fails a repeated admission gate. On the 28 stable probes the
measure gives 2.08 diverged per message against a gate of three — the same
answer the six-message run gave, on twice the data.

Three of the twelve messages produce **zero** divergence on the stable subset
(`a2`, `b1`, `c0`), joining `terse0`. A quarter of briefs transfer everything
this measure can see.

### What the divergences actually are

The obvious alternative explanation had to be ruled out before any of this means
anything: divergence is scored as *sender mode ≠ receiver mode*, so a probe whose
sender distribution is flat produces divergence by chance, with no transfer
failure at all. The four rejected probes are exactly the flat ones, so the worry
is pointed.

**Ruled out.** On the 23 divergence events the receiver's own modal margin has a
median of **8 of 10**, mean 7.1, unanimous in 7. On the 12 events that sit on
*stable* probes the median is also 8. The receiver is confidently giving a
different answer, which is transfer loss and not shared wobble.

**Every divergence is a dropped qualifier**, and the mechanism is legible probe
by probe: the paired figure maximum of 70 (`X06`, `X17`, `X21`), R1's
"exactly 22 satisfies" (`X24`), R4's exact five years (`X16`), R9's padding
allowance inside a pair (`X07`, `X22`), and R9's precedence clause — a submission
that would be PADDED but fails a second rule is RETURNED (`X11`, `X26`). The
brief carries the rule and loses the clause attached to it, which is the design
rule restated from the other side.

**The direction is not established, and the obvious statistic for it is an
artifact.** Seventeen of the 23 events make the receiver *stricter* than the
spec-holder, which sign-tests at `p = 0.0173` — and that number should not be
used. Five of the nine discriminating probes are `HANDLED`-keyed, and a
`HANDLED`-keyed probe **can only** err stricter, because nothing is more lenient
than HANDLED. The majority is partly forced by which keys those probes happen to
carry.

Conditioning on the only probes that could go either way, the two `PADDED`-keyed
ones: **4 of 4 events went stricter**, `p = 0.0625` one-sided. Suggestive, `n` is
four, and it is reported as suggestive.

## Provenance of the surrounding numbers

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

## The keys are three-way derived

`qwen3.5:35b` was given the specification and asked the original sixteen probes
cold, with no key and no contact with the author's reasoning. It returned
**16 of 16**, every one unanimous at 10/10, matching both the hand-derived key
and `gpt-oss:120b`. Recorded in
[`adjudication-qwen.json`](adjudication-qwen.json).

That closes the specific risk this README named — the author and the model wrong
in the same direction — with two models of different architecture agreeing. It
does **not** close the general one. Both models read the same specification, so
what has been shown is *convergent derivation*, not independent verification of
whether the specification says what its author thinks. Two readers who share a
prior can share an error. `probes/riverside-30/ADJUDICATION.md` remains the
standard and remains unmet.

`X17`–`X32` have not been adjudicated at all yet.

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
