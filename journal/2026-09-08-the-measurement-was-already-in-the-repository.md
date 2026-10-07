# The measurement was already in the repository

**2026-09-08.** Eleven days that produced one first measurement, one correction
worth more than the claim it corrected, one model chosen for a reason that turned
out to be false — and, at the end, an audit that read every number in the arc
against the file it came from and found three of them wrong. All three were mine,
all three were on the front page, and none of them was caught by reading.

## Problem 9, measured for the first time

Does a model recover its own composed brief better than another model recovers
it? The naive answer is obviously yes — the priors match perfectly — and
[Problem 9](../theory/open-problems.md) has stood since founding without a
number attached.

Predicted first: *no self-transfer advantage, |self − cross| under 1.5 diverged
probes in both rows, sign not consistently in self's favour.* Then the 2×2, three
briefs per composer, ten draws per probe:

| diverged of 30 | read by `gpt-oss` | read by `qwen` | row mean, self − cross |
|---|---|---|---|
| composed by `gpt-oss` | **10.00** *(self)* | 9.67 *(cross)* | **+0.33** |
| composed by `qwen` | 10.33 *(cross)* | **11.33** *(self)* | **+1.00** |

~~Self is *worse* on both rows~~, by +0.667 across all six pairings — four positive,
one negative, one tie, sign test **p = 0.375**. The prediction held; the direction
is not established. ~~What is established is the absence of the advantage everyone
would assume~~, and the likeliest reason is the instrument rather than the agents:
`RIVERSIDE-30`'s divergence is probe-attributable, and both readers always
diverge on the same seven probes.

*Both struck clauses withdrawn 2026-10-07, [retraction 22](../RETRACTIONS.md).
The `gpt-oss` row's sign depends on how one tied modal cell, its self-reader's
`b2`, is broken; under the other admissible choice its mean is 0. And `p = 0.375` over six pairs that
share their composers, readers and briefs shows no observed advantage without
establishing that there is none. "The prediction held" is true of its numerical
clause and its main sentence; its outcome table's holding row also asked for
inconsistent signs, and did not get them.*

Between rows the comparison is confounded and was declared so beforehand:
`gpt-oss` composed at 423/389/403 words against the same 230-word instruction
where `qwen` gave 240/239/241. I wrote that this meant `qwen` satisfies E-001c's
band and that the void might be model-specific — and withdrew it the next day, on
arithmetic that was available when I wrote it. The band is **182–231**. All three
of `qwen`'s compositions are *above* the ceiling.

## The fluent floor belonged to one model

E-001c died saying, in words [retraction 18](../RETRACTIONS.md) has since
withdrawn, that the fluent register's length floor sits above the band's
ceiling, so the manipulation was unsatisfiable rather than underpowered. Same
script, same specification, same calibrated instruction, same band, one model
changed:

| in band, of 12 | `gpt-oss` | `qwen` |
|---|---|---|
| **A** fluent × declarative | **0** | **11** |
| **B** fluent × contrastive | 5 | 12 |

[Retraction 18](../RETRACTIONS.md). The void itself stands — E-001c ran on
`gpt-oss`, that model could not compose inside its own band, and the experiment
correctly died. What went was the generalisation from one generator to the
register.

## Three numbers that were wrong

Then an audit: every figure in the eleven days, re-read against the file it is
stated in, by a reader instructed to refute rather than confirm. Sixty-one
figures in the first arc, sixty-five in the second, sixty-two in the third.

**[Retraction 19](../RETRACTIONS.md) — a wrong gloss on a right finding.** The
results file above reports `gpt-oss`'s fluent floor as **223** and then says, in
the next sentence, that it "sits above" the ceiling of **231**. It sits eight
words below. The claim is true only of cell A, whose floor is 232; cell B's floor
is 223 and it lands in band 5 of 12 — so `gpt-oss` reaches the band under a
fluency instruction, in the contrastive cell. That sentence went into the ledger
and onto the front page and stood for six days, because nobody subtracted the
number under it from the number beside it.

**[Retraction 20](../RETRACTIONS.md) — the measurement existed.** On 2026-09-01 I
wrote a prediction opening *"No `claude-*` model has ever read `RIVERSIDE-30`"*,
noted the API key was unavailable, and filed it unrun. E-004 measured
`claude-opus-4-8` against `RIVERSIDE-30@2e6afe2f3c92` — the identical hash — at
**0.733** on 2026-08-03. E-001c's parameters file had quoted that figure for a
month. The prediction cites E-004 two paragraphs later, for the number it wanted,
and did not read the row underneath.

Scored against that data, both its sharp clauses hold: below 1.000, and
`acc(claude) − acc(gpt-oss)` negative on both domains. **No crossover** now rests
on four models instead of three. It also rested on enough evidence a month before
I argued it — which means the whole third-model arc, 42 GB of weights and 1 280
probe calls, was launched to settle a question this repository had already
settled and filed.

**[Retraction 21](../RETRACTIONS.md) — the gate belonged to a different
experiment.** `llama3.3:70b` came in at 0.824 and 0.467 against `gpt-oss`'s 1.000
and 0.967, and I published that it "fails E-004's 0.90 subject gate on both".
E-004 registered `accuracy > 0.60`, and its own void note says every model
cleared it. On E-004's real gate `llama3.3` **passes** `MERIDIAN-34`. The 0.90
threshold is real — it is the sender-accuracy gate in E-001b, E-001c, E-002b and
E-002c — and `llama3.3` fails *that* on both, so the conclusion survives and its
citation did not. The same shape as [retraction 16](../RETRACTIONS.md): the counts
held, the reason given for them did not.

Five smaller corrections went with them: an MDE quoted without naming its reader
in a file that says in terms it must be named, a `MERIDIAN-33` figure called
`MERIDIAN-34`, a `MERIDIAN-IX32` receiver count still cited as capability evidence
after [retraction 16](../RETRACTIONS.md) withdrew that reading, a run described as
made *at matched default* when one of its models has no reasoning mode to default
to, and a raw markdown strikethrough sitting in the site's HTML, rendering as
literal tildes to every visitor and invisible to the checker that looks for `<s>`.

A sixth was found by reviewing this entry before publishing it, and belongs here
rather than in a footnote: the correction above first read *"`gpt-oss` can compose
fluently inside the band"*. It cannot be said. The 5-of-12 is a **band** count from
a run that measures length alone, and E-001c's void records that of the two live
messages that reached the band, neither was judged fluent prose. A correction that
overclaims is not a correction.

## Where it leaves the roadmap

`check_counts.py` opens by saying a number in prose reads as true. It guards
ten counts. Every one of the three claims above was a number in prose it does
not cover — and the audit that found them is not yet a script, which is the next
thing worth building.

**Built the next day.** [`tools/check_provenance.py`](../tools/check_provenance.py)
reproduces two of the three from the repository's own files: it indexes every
threshold registered in an `experiments/*/PREREGISTRATION.md` gate table and every
model×measure pair any result artifact records, then reads prose back against
both. Run against the tree the day before, it finds retractions 20 and 21 without
being told they exist — four claims, exit 1. It does **not** find retraction 19,
and says so in its own docstring: that one is prose contradicting a table cell it
does not name, which is not a regex. Nor does it catch every *instance* — the same
miscitation in `theory/laws.md` sits thirty words from an unrelated "withdrawn"
and reads as a quotation. Both gaps are measured and written into the tool rather
than left for a reader to discover.

**E-003 is blocked on domain selection**, unchanged and better evidenced: four
models, two domains of one task type, and nothing a model holds a prior *about*
separating them. That is a probe measure and a month, not a download.

---

*This document is licensed CC BY 4.0.*
