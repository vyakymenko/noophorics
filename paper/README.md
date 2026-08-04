# The paper

`noophorics-2026.tex` — a draft reporting the programme's one established result
and its four voids, intended for arXiv (`cs.CL`, cross-list `cs.AI`).

**It is a draft, not a submission.** It was assembled by an agent from the
committed record and has not been through the author's own revision. Nothing here
is submitted anywhere by anything other than a human hand.

## Building it

There is no LaTeX toolchain on the machine this was written on, so **the source
has never been compiled**. It passes a structural check — balanced environments,
matched braces, even inline math delimiters, every `\cite` resolving to a
`\bibitem`, every `\ref` to a `\label` — and that is not the same as compiling.

```bash
brew install --cask basictex     # or MacTeX, or use Overleaf
pdflatex noophorics-2026.tex && pdflatex noophorics-2026.tex
```

arXiv compiles LaTeX source on upload, so the `.tex` is the deliverable either
way. Compile it once before trusting it.

## Checking it

```bash
python3 paper/check_numbers.py
```

The paper says every figure in it is traceable to a committed results file. That
is a claim, so it is checked rather than asserted: 24 figures read from the
results JSON on one side and from the LaTeX on the other, failing when **either**
moves. A checker that only read the paper would pass on a paper that quietly
disagreed with its own data.

It has already earned its place twice. It caught a sign dropped from
`β_sender`, and it reported the observed-agreement sd as wrong — where the paper
was right and the checker had reached for the sample sd against a source that
reports the population one. A check that can only ever accuse the document is
not much of a check.

## What is still open in it

- **The floor-by-register table.** Marked `% FLOOR-TABLE:` in the source. It is
  filled from `experiments/E-001c-fluency-length-controlled/floor-by-register.json`,
  produced by `floor_by_register.py`. Until that lands, the negative result rests
  on cell A only.
- **Authorship.** One name, taken from `AUTHORS.md`. Whether the agent
  contribution is acknowledged, and how, is the author's call — see
  [EXPOSURE.md](../EXPOSURE.md), which records that a model that is also one of
  this programme's measurement subjects read the pre-registrations while helping
  write this.
- **Title.** Two claims in one title is one too many. Pick the one the paper is
  actually about.

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
