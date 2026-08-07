# The paper

`noophorics-2026.tex` — a draft reporting the programme's one established result
and its four voids, intended for arXiv (`cs.CL`, cross-list `cs.AI`).

**It is a draft, not a submission.** It was assembled by an agent from the
committed record and has not been through the author's own revision. Nothing here
is submitted anywhere by anything other than a human hand.

## Building it

```bash
brew install tectonic
tectonic -X compile paper/noophorics-2026.tex
```

**It compiles clean** — no errors, no warnings, no overfull boxes. `tectonic` is
the toolchain to use here: a single self-contained binary from a Homebrew
formula, needing no `sudo`, against `basictex` which ships an installer package
that does. This README previously said the paper "has never been compiled"
because the machine had no TeX; that was true of `pdflatex` and false of the
problem, and the first compile found two tables running past the right margin
that every structural check had passed.

arXiv compiles LaTeX source on upload, so the `.tex` is the deliverable and the
PDF is a build artifact — gitignored, because a committed PDF drifts from its
source the moment anyone edits a number in it.

## Checking it

```bash
python3 paper/check_numbers.py
```

The paper says every figure in it is traceable to a committed results file. That
is a claim, so it is checked rather than asserted: 26 figures read from the
results JSON on one side and from the LaTeX on the other, failing when **either**
moves. A checker that only read the paper would pass on a paper that quietly
disagreed with its own data.

It has already earned its place twice. It caught a sign dropped from
`β_sender`, and it reported the observed-agreement sd as wrong — where the paper
was right and the checker had reached for the sample sd against a source that
reports the population one. A check that can only ever accuse the document is
not much of a check.

## What was open in it, and how it was settled

- ~~**Authorship.**~~ Settled: one name from `AUTHORS.md`, plus an
  *Acknowledgement of machine assistance* section that states the part which
  matters here — the assisting model is also one of this programme's measurement
  subjects, so it cannot judge whether the open problem it drafted is real. It
  never held a probe measure in context, and the section says that too, because
  it is what keeps those weights usable as a subject later.
- ~~**Title.**~~ Settled: reduced to the one claim the paper *establishes*. The
  dropped clause was about what the paper closes, which "four voids" already
  carries.

## Constraints this draft is under

Every number in it is traceable to a committed results file. Where it cites
outside work it obeys `theory/prior-art.md`, which records for each source
whether the primary text or only the abstract was read, and what may be claimed
from it. Two constraints from that ledger are load-bearing here and are stated in
the paper itself: Endsley (2020) is cited from its abstract and supports only
that the two measures diverge, with **no pooled effect size quoted**; Newton
(1990) is an unpublished dissertation.

If a reviewer asks for a number this draft does not have, the answer is that we
do not have it — not that it can be estimated.

---

*This document is licensed CC BY 4.0.*
