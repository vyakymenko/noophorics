# The ledger, read against the text

**2026-10-07.** Nothing was measured today and no model was called. The work was
reading [RETRACTIONS.md](../RETRACTIONS.md) against the files it governs, and it
moved the count from twenty-one to twenty-four. All three new withdrawals were
already in the repository, and so was the evidence against them.

## Withdrawn claims that were still being stated

The ledger's first job is that a withdrawn claim is never restated as live.
Retractions 13, 15, 18 and 19 each still had live copies: fourteen spans, struck
today across six files.

- **Retraction 18**, filed 2026-09-02, withdrew "the fluent register's length
  floor sits above the band's ceiling" in its own row. Eighteen lines lower, in
  the void table of the same file, E-001c's row went on saying exactly that, and
  E-001c's own `VOID.md` went on heading its evidence with "The floor belongs to
  the fluency axis", the other half of the same row.
- **Retraction 15**, filed 2026-08-18, withdrew the `MERIDIAN-IX32` Fisher
  p-values. The probe file struck its copies that day, and
  [Problem 15](../theory/open-problems.md) went on printing `p = 0.0339` and
  `p = 0.0035` as live.
- The ledger's own row 14 went on printing `p = 0.0035` beside its count, the
  p-value row 15 withdrew from beneath it. A design note added the day after
  row 15 computed a fresh Fisher `p` over the same 32 probes and called the
  association "established".
- **Retraction 13**, filed 2026-08-05, withdrew the property that only
  interaction-tagged probes survive saturation. Problem 15 kept it as a bold
  headline, its sentence about seven untagged two-rule probes kept the zero, and
  the `MERIDIAN-IX32` README restated the property two days after it was
  withdrawn, beside the "3 of the other 25" that contradicts it.
- Problem 15 also called 229–232 words "the fluent register's floor", which is
  the conflation retraction 19 named: that is cell A's floor, and the fluent
  row's is 223.
- The self-transfer result went on calling the two models' 240 and 242.1 words
  "the opposite of a model-specific void" after `qwen` put cell A in band 11 of 12.

`check_retracted.py` could see almost none of them. It indexes `~~struck~~`
spans, and the ledger quotes a withdrawn claim in quotation marks. Its shingles
are six words long, and a bare p-value is shorter than that. `probes/` is not
among the files it reads. And it never reads `RETRACTIONS.md` as a target at all,
so nothing inside the ledger — row 14, which sits directly above the row that
withdrew its number, or the void table — could ever have fired it. These are
reasons the check did not fire. They are not an account of why nobody re-read the
void table, and that account is not available.

Striking the void-table clause put its wording in the index, and the checker
found one more copy at once. It was a quotation in the
[2026-09-08 entry](2026-09-08-the-measurement-was-already-in-the-repository.md),
and its acknowledgement sat five words outside the window.

## Three new withdrawals

**[Retraction 22](../RETRACTIONS.md) — the self-transfer verdict.** "There is no
self-transfer advantage" and "what is established is the absence of the naive
advantage" rested on a sign test at `p = 0.375`. The test ran over six pairs that
share two composers, two readers and their briefs, and a large `p` does not
establish an absence. "Self is worse on both rows" depends on how one tied
modal cell is broken — the `gpt-oss` self-reader's `b2`, one of three ties in the
run: under its other admissible co-mode the `gpt-oss` row mean is 0. Both audits
had said this, on 2026-09-09 and 2026-09-28, and both sat as drafts for human
review until today. The counts stand. The verdict does not, and
neither does the headline "the naive answer does not survive". What the data
carry is that the naive answer is **not supported**.

**Retraction 23 — a sign the page it cites contradicts.** Problem 12 said our
`min(1.0, …)` cap carries "the same bias, in the same direction, for the same
reason" as the judge–advisor literature's truncation, which biases upward. A cap
from above cannot raise a number: `min(1, x) ≤ x`. JAS's upward bias comes from
clipping *negative* advice-taking to zero, and `F*` is never clipped below zero.
[prior-art §7](../theory/prior-art.md) says both of those things, three sections
above the sentence that contradicts them. Problem 12 itself is unchanged. The
vanishing denominator is one defect in both fields, and nobody has solved it.

**Retraction 24 — a `p` under the wrong table.** `p = 6.25e-05` is
`C(9,6)/C(34,6)`, the p-value of 6 of 9 against 0 of 25. That zero was withdrawn
as retraction 13 on 2026-08-05, the day it was written, when twelve messages
replaced six. The retraction struck the count and left its p-value standing
beneath the corrected cell — a table that now pairs a six-message count with a
twelve-message one. Both it and the `p = 0.006` beside it treat `MERIDIAN-34`'s
34 probes as independent, and those probes form ten prompt clusters at
similarity 0.85. That is retraction 15's defect, on a measure retraction 15 did
not cover.

## Counts that were not checked against their own files

`theory/open-problems.md` opened with "Ten problems" above fifteen headings. Every
file that quotes the count was checked against those headings, but the file's own
first line was not. In `RETRACTIONS.md`, the tally's void number was checked and
its claims number was not, even though every other copy of that count is taken
from it. Both are claims in [`check_counts.py`](../tools/check_counts.py) now.

The checker's numeral vocabulary was a second list that had to be kept in step
with seven hand-written alternations. The front-page one stopped at
*Twenty-one*, so today's correct sentence would have failed as PATTERN NOT FOUND.
The alternations are built from one table now. Building it turned up a latent
false match: with no word boundary, "often open problems" read as "ten open
problems". Four new tests cover these changes, and all four fail against the
previous checker. `AGENTS.md` told every agent that a retraction moves "eleven
translations"; there are nineteen, and that line is checked now too.

## What was left alone

The `MERIDIAN-IX32` heading "Discriminating power and stable observability are
anti-correlated" still stands. The ledger withdrew the p-values that supported
it, and the probe file's author kept the direction as a count. Striking the
heading would be a new withdrawal, not the enforcement of an old one, so it waits
for a decision.

Two prediction files restate retraction 18's void reason in the context above
their predictions — `probes/riverside-30/PREDICTION-selftransfer.md`, which also
calls "that void may be model-specific" wrong, and `PREDICTION-headroom.md`. They
were left as written: a prediction file is the record of what was believed when
it was committed, and editing it to agree with later knowledge is the thing this
repository exists to forbid. The paper draft states retraction 18's framing in
its abstract and a section title; its README now says so, and the `.tex` is
unchanged.

`check_retracted.py` still does not read `probes/`. Of today's strikes there,
only one — the absence clause in `RESULTS-selftransfer.md` — has a guard that
survives regeneration: the self-transfer audit refuses to rebuild unless it stays
struck, and that audit is in the pre-push list as of today. The others are held
by nothing mechanical.

## Provenance

Who wrote the three claims is recorded unevenly. Retraction 24's section was
authored by `claude-opus-5`, by its own exposure row. Retraction 22's is
attributed to that model only by inference. Retraction 23's commit carries no
agent attribution and predates the exposure log, so its author is not recorded.
The retractions were drafted by `claude-opus-5-5`, after an eleven-agent read-only
workflow of that model surfaced them, and an eight-agent workflow of the same
model reviewed the draft and found eleven defects in it, among them two wrong
dates, a wrong line count and a correction written as prose instead of a strike.
The repository owner chose, for each, to file it as a numbered retraction. The
rows' wording and some of their grounds were added in drafting. A model of the
same family is not independent review, though it is not the same agent
retracting its own finding of the day before, which is what is recorded against
[retraction 16](../RETRACTIONS.md). [EXPOSURE.md](../EXPOSURE.md) records what
the agents reported reading, including what some of them saw by accident, and is
a lower bound on it.

**Next:** [Problem 13](../theory/open-problems.md#13-a-hypothesiss-reported-statistic-and-its-tested-statistic-are-not-checked-against-each-other).
Three times now an interval and a p-value in one claim were computed from
different quantities. No check binds the two to one registered estimand, and any
further E-002-family run would inherit that gap.

---

*This document is licensed CC BY 4.0.*
