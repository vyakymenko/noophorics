# MERIDIAN-IX32 — probes that need two rules to combine

*The directory is named for where this started, sixteen probes; the measure is
now thirty-two. The name is left alone because links resolve to it.*

## Where it stands

**32 probes, 28 stable, 2.00 diverged per message — it does NOT clear the gate.**
**And on a second architecture it gives 0.83**, with only 2 of 32 probes losing
anything both models agree is lost ([results](RESULTS-qwen-receiver.md)).

~~32 probes, 31 admitted, 3.33 diverged per message. That clears E-002c's
outcome-variation gate of three.~~ **Withdrawn 2026-08-07**, by applying the
admission gate the way it should always have been applied: repeatedly. Five
sender passes instead of one rejected four probes as unstable, and the measure
on the 28 survivors gives **2.00** diverged per message at a per-probe rate of
**0.071** — still above `MERIDIAN-34`'s 0.049 on the identical six messages, and
below the gate.

**And the four rejected probes are four of the nine that ever discriminated.**
Of the 23 probes that never discriminated, none was rejected. ~~Fisher exact
`p = 0.0035`.~~ **The p-value is withdrawn 2026-08-18** — [retraction
15](../../RETRACTIONS.md) — because this measure is not 32 independent probes
and the test assumes it is; see [the counting defect](#the-counting-defect)
below. The **count** stands, and so does the direction: discriminating power and
modal stability are in tension here, and the headroom this measure appeared to
have was substantially borrowed from probes that are not stable observables.

**All 32 keys are twice-derived.** `qwen3.5:35b` was given the specification and
every probe cold, and returned **32 of 32**, each unanimous at 10/10
([`adjudication-qwen-32.json`](adjudication-qwen-32.json)). Still not adjudicated
by a person — that gap stands.

**And the instability does not transfer between models**, which qualifies the
headline finding below:

| probe | `gpt-oss:120b`, five passes | `qwen3.5:35b`, one pass |
|---|---|---|
| `X06` | 10, **4**, 10, 10, 10 | 10 |
| `X17` | 10, **6**, 8, 8 | 10 |
| `X21` | 8, 8, **6**, 10 | 10 |
| `X22` | 10, 10, **6**, **6** | 10 |

`qwen`'s only margins under 10 across all 32 are `X16` and `X19` at 8 — neither
in the rejected set. So "the probes that discriminate are the ones that will not
hold still" is true **of `gpt-oss:120b`**, and the probes it wavers on are read
unanimously by a model of another architecture. They are not ill-posed.

The caveat is the same one that produced the repeated gate in the first place and
it cuts against the hopeful reading: **`qwen` ran one pass**, and `X06` passed
four of five `gpt-oss` passes at 10/10. One pass cannot establish stability, by
exactly the argument this file already makes. Five `qwen` passes have not been
run. ~~They would cost about eleven hours.~~ **Corrected 2026-08-19:** qwen was
measured at **53.5 s/call** over a 1 920-call run, against `gpt-oss`'s 5.8 s/call
derived from the gate-run timestamps — a factor of nine. Five passes is 1 600
calls, so **about 24 hours**, not eleven.

What can be said: the anti-correlation is measured on one model, and the
instability behind it is not a property of the probes. ~~Whether a successor can
escape it by choosing a model is open, and now worth asking.~~

**Asked and answered, 2026-08-19 — the route is closed.** `qwen` was run as a
receiver over all six messages
([`RESULTS-qwen-receiver.md`](RESULTS-qwen-receiver.md)) and returns **0.83
diverged probes per message against a gate of 3**, where `gpt-oss` returns 3.83
on the identical briefs. Not saturation — qwen does diverge, on `X11` and `X26` —
but choosing the stable model costs nearly all the signal, so stability and
discriminating power trade off *across models* exactly as they trade off across
probes.

The sharper half is about the measure, not the models. **qwen's divergence set is
a strict subset of `gpt-oss`'s**, and the seven probes only `gpt-oss` loses are
all `R5`, six of them at its own wobble points. So of the nine probes that
discriminate here, seven are ones a second architecture does not lose at all, and
`MERIDIAN-IX32` measures *model-independent* transfer loss on **2 of its 32
probes**.

~~What looked like headroom was substantially one reader's uncertainty.~~
**Withdrawn 2026-08-19 — [retraction 16](../../RETRACTIONS.md).** Qualified once
that morning at `p = 0.0833`, then withdrawn outright the same day on three
independent grounds: the supporting statistic compared `gpt-oss`'s minimum over
four sender passes against `qwen`'s single pass (like-for-like it is **2 of 7**,
not 6); a model with **no reader×probe term at all** — one difficulty per probe
plus a single ability gap of **2.20 logits** — fits at deviance 10.54 on 8 df,
`p = 0.229`, and predicts the strict subset anyway; and the comparison was never
conditioned on that gap, which by [Dorans & Holland
(1992)](../../theory/prior-art.md) makes it **impact**, not differential
functioning. The counts stand. Why the seven separate the models is open, and
[D-STUDY.md](D-STUDY.md) states what would settle it: conditioning the comparison
(free), equalising the sender passes (~14 h), and a third reader, which this
hardware does not have.

The prediction recorded before that run
([`PREDICTION-qwen-receiver.md`](PREDICTION-qwen-receiver.md)) named `X16` and
`X19` and scored **0 of 2**, with `X11` and `X26` diverging against it. Sender
margin predicts `gpt-oss`'s divergences at 7 of 7 and qwen's at 0 of 2 — qwen's
two divergences both sit at margin 10 — so it is not a portable predictor.

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
probe-message pairs. ~~Fisher exact `p = 0.0339`.~~ **Withdrawn 2026-08-18**,
[retraction 15](../../RETRACTIONS.md), on the counting defect below — the
thirteen-to-zero split is a fact about the probes and is unaffected; what it
cannot carry is a significance level computed as if the rows were independent.

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
never did.** ~~`p = 0.0035`.~~ Withdrawn 2026-08-18, [retraction
15](../../RETRACTIONS.md); the counts are unaffected. On the 28 survivors the
measure gives 2.00 diverged per message and 0.071 per probe, against 3.33 and
0.124 before.

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
| Fisher exact | ~~`p = 0.0035`~~ | ~~**`p = 0.0138`**~~ |
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

**And nothing about a brief predicts which quarter it lands in.** Across the
twelve:

| | mean diverged |
|---|---|
| fluent (A, B) | 1.83 |
| terse (C, D) | 2.33 |
| declarative (A, C) | 1.83 |
| contrastive (B, D) | 2.33 |

`corr(words, diverged) = −0.010` over 221–308 words. The two axis differences are
the same size in opposite directions with six messages a side, which is noise at
this `n`. And the three complete transfers come from **three different cells** —
`a2` fluent-declarative, `b1` fluent-contrastive, `c0` terse-declarative — at
250, 235 and 232 words, the middle of the range.

So at this operating point how much of a specification survives a brief is a
property of *that brief*, not of its length, its register or its selection
strategy. For a successor that matters twice: per-message variance will dominate
and cannot be designed away by choosing a cell, and a design needing outcome
variation **in every cell** cannot get it by writing a better prompt for the
cell.

### The counting defect

**Every Fisher exact `p` above is withdrawn, because this measure does not have
thirty-two independent rows.** `X17` and `X18` differ by one token — "Combined
figure count is 70" against "71" — and carry opposite keys, `HANDLED` and
`RETURNED`. So do `X21`/`X22` (8 → 7) and `X24`/`X25` (30 → 21). They are minimal
pairs straddling a numeric threshold, which is good probe design and fatal
arithmetic: a test over 32 rows treats them as 32 elicitations of independent
questions.

Single-link clustering of the prompts, and where the instability falls:

| similarity threshold | clusters | largest | clusters holding any instability |
|---|---|---|---|
| 0.80 | **9** | 11 probes | 2 |
| 0.85 | **9** | 11 probes | 2 |
| 0.90 | 13 | 9 probes | 3 |
| 0.95 | 19 | 7 probes | 4 |

There is no corrected p-value to put in their place, and that is the finding
rather than an apology for it: the cluster-level `p` runs from **0.111 at
threshold 0.80 to 0.006 at 0.95**, so any number quoted is a report on where the
clustering line was drawn. "Four of nine" is a count of probes, not of readings.

**What survives is at the draw level, and it is sharper than what it replaces.**
Of **1 440** `gpt-oss:120b` sender draws across the passes, **19 are non-key —
and all 19 fall on `R5`-tagged probes**: `X17` 4, `X21` 4, `X22` 4, `X06` 3,
`X24` 2, `X16` 1, `X09` 1. No probe outside `R5` has ever returned a margin below
10, in any pass, at any gate. The individual draw is the unit that *is*
independent here, and the concentration is not a threshold artifact.

Two things stop this being another post-hoc tag hunt. The `R5` label was
committed in `157b80f` at **2026-08-10 09:29:56**, nine hours before the first
`IX32` sender pass (`b37b0db`, 18:49:44) and a day before the gate runs — the
label is prior to every instability datum and was not drawn to fit it. And the
selection of `R5` from among the ten rules is corrected for: an exact
enumeration over all `C(32,4) = 35 960` relabelings, across the distinct tag
families a searcher could have written, returns `p = 0.0016`, not the `0.00042`
the uncorrected table gives. `0.00042` is in any case a floor and not a
measurement — `C(6,4)/C(32,4)` is what *any* six-probe family capturing all four
would print.

**What this does and does not do to the paragraph above.** It does not rescue the
repair route. `R5` carries **45 of the 49** divergence events (3.75 per message
against 0.33 for the other nineteen probes), so the region holding all of the
instability is the region holding nearly all of the signal — which is the
uncomfortable reading in sharper form, not a refutation of it. What it corrects
is the generalisation: instability is not spread across hard probes, it is
localised to one rule, and "harder is where the instability lives" should be read
as "one rule is where both live". Conditioning on `R5`, the association between
wobble and discrimination is `p = 0.0699` — and outside `R5` it is not weaker but
untestable, there being no instability there to correlate with anything.

And there is no stable discriminating joint to move to. `R1`&`R5` looked like one
— 4 of 4 discriminating, 0 of 4 unstable — but 0 of 4 is the *modal* outcome for
any four probes drawn from this measure (`P = 0.569`), 6 of its 11 events come
from `X24` alone, and `X24` clears the admission gate by exactly zero. Under
label permutation its rate gives `p = 0.309`.

*Recorded 2026-08-18. Analysis is over data already on disk; no new elicitation.*

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

~~`X17`–`X32` have not been adjudicated at all yet.~~ **Superseded 2026-08-16**
by [`adjudication-qwen-32.json`](adjudication-qwen-32.json), which derived all
32 keys cold; the head of this file has said so since, and this sentence sat
here contradicting it for two days. It is struck rather than deleted because the
gap it names — *nothing* had checked the second sixteen — was real when written,
and a reader arriving here should see that it closed rather than that it never
existed. The general gap above is untouched: convergent derivation by two models
is not independent adjudication, and no person has read these probes.

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
