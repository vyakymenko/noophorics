# Can the four registers survive being pinned to a common length?

**Instrument check, before registration.** No hypothesis is tested here and none
may be read off it. It exists to answer whether E-001c is buildable at all,
after [E-001b was voided](../E-001b-fluency-factorial/VOID.md) by its cost
parity gate.

**Answer: yes, with a calibration problem that is measured rather than assumed.**

---

## What was replaced

E-001b instructed `Stay within 350 tokens` — a **ceiling**. A ceiling bounds
above and says nothing about below, so it cannot produce parity even when
obeyed, and it was not obeyed: every cell exceeded it, the fluent cells by 76%.

E-001c states a **two-sided word band** instead, and verifies realised token
cost afterwards. Words rather than tokens because a model cannot observe its own
tokenizer, and E-001b is direct evidence that it does not honour a token limit.
Nothing else in the prompts changed: the same five blocks, the same two varying
blocks, only the output block swapped.

## Result 1 — cost parity is achieved

Target 220 words (band 198–242), k=3 per cell, `gpt-oss:120b`, think=medium,
temperature 0.7:

| | fluent (A, B) | terse (C, D) | ratio |
|---|---|---|---|
| **E-001b**, ceiling instruction | 614.3 tok | 399.7 tok | **1.537** |
| **E-001c**, two-sided word band | 381.3 tok | 418.5 tok | **1.097** |

The 1.5× gap collapses to 1.10, and the *ordering reverses* — terse now costs
slightly more per message than fluent, which is what one expects once length is
the controlled variable and register is free to vary within it.

Parity across cell means: **1.160**, inside the 1.30 threshold. Parity across
individual messages: **1.320**, marginally outside it, driven entirely by
within-cell spread (a terse message at 474 tokens against a fluent one at 359).
The runner requires both readings to pass, so this configuration would still be
voided — see the calibration below, which is the reason it is close rather than
comfortable.

## Result 2 — the manipulation survives

This is the half that mattered more. Convergence bought by destroying the
distinction would be a null experiment with extra steps.

| structural marker | fluent | terse | ratio |
|---|---|---|---|
| mean sentence length (words) | 21.08 | 12.19 | 1.73 |
| connectives per 100 words | 2.15 | 0.61 | 3.52 |
| bullet fraction | 0.00 | 0.00 | — |

The two registers remain clearly separated at a common length: fluent writes
sentences nearly twice as long and uses subordinating connectives three and a
half times as often. Neither register produced bullet lists, so "terse" is
manifesting as short declarative sentences rather than as note form.

**These are proxies, not a validity check.** They distinguish prose from notes;
they do not establish that the *intended* style distinction is what survived.
Establishing that needs independent blind rating, and it is a precondition of
E-001c's registration, not something this script can supply. What the numbers do
rule out is the loud failure mode — pinning the length did not collapse the
registers into one.

## Result 1b — the calibration, confirmed rather than assumed

Asking for **203** words, as the offset predicted:

| target | compliance | parity across messages | parity across cell means | verdict |
|---|---|---|---|---|
| 220 | 50% | 1.320 | 1.160 | fail |
| **203** | **56%** | **1.290** | **1.108** | **pass** |

Both readings now pass, and the style separation survives the shift (fluent
19.75 vs terse 11.52 mean sentence words; 1.77 vs 0.70 connectives per 100).

The overshoot is **cell-dependent**, which the single-target correction cannot
remove: A +14.4%, B +8.3%, C −2.8%, D +3.0%. Fluent registers run long, terse
ones land. Word counts therefore do not equalise across cells — but the
requirement is cost parity, and cost parity is what passes.

## Result 1c — `max/min` over messages is the wrong statistic, and this is why

`1.290` against a threshold of `1.30` is not a pass, it is a warning. The
maximum and minimum of a sample both drift outward as the sample grows, so
`max/min` is **not scale-free**: the same design fails the same gate simply for
collecting more messages.

Parametric bootstrap from the observed per-cell cost distributions
(normal, 20 000 draws):

| k per cell | messages | median `max/min` | **P(fail 1.30)** | cell-means `max/min` | P(fail) |
|---|---|---|---|---|---|
| 3 | 12 | 1.279 | 40% | 1.130 | 0% |
| 4 | 16 | 1.308 | 54% | 1.124 | 0% |
| 6 | 24 | 1.347 | 74% | 1.118 | 0% |
| **8** | **32** | **1.375** | **86%** | 1.115 | 0% |
| 12 | 48 | 1.415 | 96% | 1.112 | 0% |

At E-001b's own pre-registered `k = 8`, a design with genuinely parous costs
fails the across-messages gate **86% of the time**. A gate that gets harder as
you collect more data penalises statistical power, and would have voided E-001c
for the sin of being adequately sampled. The cell-means reading is flat across
every `k`.

So the ambiguity flagged in the void — the pre-registration said "across cells",
the runner compared messages — resolves in favour of the pre-registration, on a
statistical argument rather than a convenient one. The argument is that the
sample max/min is not scale-invariant, which is true regardless of which side it
favours; but the resolution does happen to favour the reading that passes, and
that is stated here rather than left for a reader to notice.

The runner is corrected to use cell means, and E-001c will register that reading
explicitly. A stricter successor worth considering is an **equivalence test**
(TOST) on cost across each axis: "the difference is inside a pre-specified
negligible band" is the claim actually wanted, and a ratio threshold is a crude
stand-in for it.

## Result 3 — the model overshoots, systematically and in one direction

Six of twelve messages fell outside the ±10% band. **Every miss was long. None
was short.**

    target 220 words -> realised mean 238.2  (+8.3%)

A one-sided error is much better news than a symmetric one: it is a calibration
offset, not noise. Asking for 203 words should centre the realised distribution
on 220. That prediction is being measured at k=4 before it is relied on, because
predicting a calibration and assuming it are different things, and this
experiment has already spent a day on the difference.

## Result 5 — the blind rating: the terse arm survives, the fluent arm does not

**The precondition this document set for E-001c's registration is now answered,
and the answer is "partly".** Instrument: [blind_rating.py](blind_rating.py).
Raters were `codex` (ChatGPT subscription) and `claude-opus-4-8` (Anthropic
API) — two providers, two authentication paths, neither of them the composer.

### The forced choice says everything is fine, and it cannot say otherwise

Every fluent message paired against every terse one, 64 pairs, order randomised
per pair:

```
codex             64/64 = 1.000   cluster CI [1.000, 1.000]   chose-first 0.42
claude-opus-4-8   64/64 = 1.000   cluster CI [1.000, 1.000]   chose-first 0.42
agreement                64/64
```

No position bias — both raters chose the first passage 42% of the time, matching
the 42% rate at which the fluent message was shown first.

That result is worth nothing, and the reason is the reason it was worth building
the second arm. A forced choice makes the rater name one of two passages even
when **neither** is the thing described, and it will name the wordier one, which
tracks the label perfectly. A score of 64/64 establishes that the two registers
are distinguishable — which the structural markers above already said.

This is the shape of [E-002b's H5](../E-002b-phantom-agreement-ladder/FINDINGS.md):
an estimator that could not fail, built here by the same hand that wrote that
section up.

### Judged one at a time, three of eight fluent messages are lists

Each message classified on its own against the fluent instruction's own words,
with "a list" available as an honest answer:

```
                  called CONNECTED PROSE
codex             fluent 5/8    terse 0/8
claude-opus-4-8   fluent 5/8    terse 0/8
```

The two raters agree **message by message, 8 of 8**, and fail the same three:
`A0`, `A1`, `B2`. Independent providers converging on the same three texts is
not rater noise; it is a property of those texts.

```
fluent prose rate  5/8 = 0.625   exact CI [0.245, 0.915]
terse  prose rate  0/8 = 0.000   exact CI [0.000, 0.369]
```

**The terse instruction works completely.** Every terse message is a list, which
is what it asked for.

**The fluent instruction works about five times in eight**, with an interval so
wide it spans a quarter to nine tenths. Reading the messages shows why: both
registers produce a labelled list of ten rules, and the fluent one writes each
item as a complete sentence rather than relating the items to one another. Its
instruction asks for *"the relationships between points spelled out in the
words"*, and on three of eight compositions nothing of the kind appears.

### What this costs the registration

E-001c **cannot be registered as it stands**. Its fluent cells would be roughly
62% pure, and the impurity is invisible to any check that works by telling the
two registers apart — which is every check this document had before today.

The remedy is rejection sampling on the **absolute** judgment: compose, have two
raters from different providers classify the message alone, keep it only if both
say connected prose. At the observed rate that is about 1.6 compositions per
accepted fluent message, on top of the 2 per accepted message that the word band
already costs. Roughly three compositions per usable fluent message.

That remedy has to be *registered*, with the raters named, because a filter
applied after seeing the outcome is not a filter. Whether the wide interval on
5/8 justifies more messages before registering is a judgment for the
registration; the honest reading is that eight messages establish the terse arm
and leave the fluent rate barely bounded.

---

## Result 4 — replicated at k = 4, and the fluent register has a length of its own

Re-run 2026-08-03 at target 203, `k = 4`, to produce messages for the blind
rating. The earlier run at this target discarded its messages, which is why it
had to be repeated; see [blind_rating.py](blind_rating.py).

```
                    2026-07-29 (k=4)    2026-08-03 (k=4)
compliance                  56%                 44%
parity across messages     1.290               1.303   fails 1.30
parity across cell means   1.108               1.054   passes
mean sentence words     f 19.75 / t 11.52   f 20.00 / t 11.35
connectives per 100w     f 1.77 / t 0.70     f 1.88 / t 0.81
```

The style separation replicates closely. The parity readings do not, and they
fail in the direction Result 1c predicted: the across-messages statistic
crossed 1.30 on a design whose cell means sit at 1.054. That is the
non-scale-free behaviour argued there, observed rather than simulated, and it is
the second time the same design has been judged differently by the two readings.
The cell-means reading governs, as the pre-registration will say.

**The new observation is the spread, not the mean.**

```
              n   mean words   sd     range
fluent (A,B)  8      226.4     1.5    225 - 230
terse  (C,D)  8      200.9    14.5    184 - 225
band for target 203: 182 - 223
```

Every fluent message overshot the band, and they overshot it to *the same place*:
a standard deviation of 1.5 words across eight compositions, against 14.5 for
terse. The fluent instruction is not loosely overshooting a target, it is
imposing a length of its own and ignoring the one asked for.

Two consequences for the registration, both stated here and neither resolved:

- **A single word target cannot land both registers in one band.** The offset
  correction in Result 1b assumed a common overshoot; there are two, and they
  differ in spread by an order of magnitude. Per-cell targets would fix the
  band and confound register with instruction, which is worse.
- **A tight distribution is not obedience.** `sd = 1.5` on a missed target reads
  as a strong prior about how long connected prose should be, not as a model
  trying and failing to comply. Whether that is a property of this register
  instruction, this model, or prose in general is not something this check can
  say.

Compliance at 50% also sets the price of rejection sampling on *words*: roughly
two compositions per accepted message. Affordable — and worth contrasting with
rejection sampling on *cost*, which the [voided
run](../E-001b-fluency-factorial/VOID.md) showed has acceptance **zero** for
every band, because the two families' realised costs were disjoint.

## What E-001c needs before it can be registered

1. **The calibration confirmed**, not predicted. In progress.
2. **Independent blind rating** that the four cells still instantiate the
   intended registers at a pinned length. The structural markers are not
   sufficient and are not offered as sufficient.
3. **A decision on the parity reading.** E-001b's pre-registration said "across
   cells" and its runner compared messages. E-001c will state one, require
   both, and evaluate them at composition — where their inputs already exist —
   rather than after the sweep.
4. **M33 repaired or removed.** `MERIDIAN-34` is superseded for new experiments
   ([SENSITIVITY-M33](../E-001b-fluency-factorial/SENSITIVITY-M33.md)); a probe
   whose key the source does not determine should not be inherited.

Registration follows those. Not before.

---

*This document is licensed CC BY 4.0.*
