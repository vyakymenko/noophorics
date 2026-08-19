# Working in this repository

Read this before changing anything. It applies to every agent, not only the one
that wrote it.

This is a research repository whose subject is the gap between what a party
believes was communicated and what was. It is therefore held to its own
standard: **a claim here is worth what its check is worth**, and the checks are
mechanical wherever they can be.

---

## The lanes

Work divides by **what a change asserts**, not by directory. A file can be in
both lanes on different lines.

### PRESENTATION lane — the site, the tooling, the plumbing

Free to change, no science review needed:

- CSS, layout, responsive behaviour, dark mode, print styles
- `<meta>`, Open Graph, JSON-LD **structure** (not its claim values), `robots.txt`,
  `sitemap.xml`, favicon, the OG image
- accessibility: heading order, landmarks, contrast, focus states, skip links
- performance and page weight
- `tools/build_journal.py`, `tools/build_translations.py` — the *rendering*, the
  markdown subset, the link resolution
- i18n plumbing: hreflang, `dir`, the language nav, the manifest

### SCIENCE lane — anything that asserts something

Not free to change. A change here is a change to a claim:

- `PRINCIPIA.md`, `theory/**`, `RETRACTIONS.md`, `lexicon.md`
- `experiments/**` — and **never** a `PREREGISTRATION.md`, which is immutable
  once committed
- `metrics/**` — the estimators and what they refuse to compute
- `probes/**` — a probe measure is the frame of reference (axiom A2)
- On the site, specifically:
  - the four `data-i18n-src="lede|move|phi|status"` passages
  - the retraction count and everything it links to
  - the `F*_R` quantity card
  - **every `<s>…</s>`** — those are struck-through retracted claims, and
    deleting one erases a correction rather than tidying markup
  - `docs/journal/**`, which is **generated** from `journal/` and
    `experiments/**`. Edit the source and rebuild; a hand-edit is lost on the
    next build and, worse, briefly makes the site disagree with the repository.

---

## Rules that are not style preferences

**Never delete a refuted claim.** Strike it through in place and say what killed
it. Strike it *at the headline*, not only in the body: `theory/laws.md` stated
L2's withdrawn form in its section blockquote for four versions while the
paragraph twenty lines below explained why it was withdrawn, and a 25-agent
audit read the file without seeing it. `tools/check_retracted.py` now indexes
every `~~span~~` and fails if its wording appears anywhere outside an `<s>` or
`~~` without the withdrawal acknowledged nearby — which means the check sees
exactly as much as the striking discipline gives it. A correction written as
prose instead of a strike is invisible to it. A file containing only survivors tells a flattering lie about how the field
got here. `RETRACTIONS.md` is the index and its count is quoted on the front
page; if you retract something, the count moves and so do eleven translations.

**Never edit a pre-registration.** If results contradict it, the finding is
added and the pre-registration stands as written. That contradiction is the
most valuable artifact an experiment produces. The git history *is* the
pre-registration record, which is also why this repository's history is never
rewritten — no force-push, no amend of a pushed commit.

**Never report a fidelity without its reference.** `F*` takes a declared `R`
(v0.4). Where `R` is the sender the quantity is *replication*, and calling it
understanding is the specific error E-001 cost a live run to find.

**A check needs its own check.** `tools/test_tools.py` exists because the three
checkers above were, for a while, evidenced only by printing a clean line on a
repository their author believed to be clean — the exact shape of a gate that
cannot fail. Each test there asserts the property that matters: red on the
defect the check exists to find, green on the legitimate case that most
resembles it. Writing them found two defects in the checkers and none in the
repository.

**Run the check, do not re-read the diff.** Three defects in this repository
survived careful reading and died the moment something was executed: a function
called but never defined, a gate that could not fail, a monitor that grepped
itself. Count what is left; do not conclude from what you changed.

**Translations are re-translated, not re-stamped.** `python3
tools/build_translations.py --check` fails when a watched passage moves. The fix
is to translate the new sentence in all eleven languages. Re-running the build
to clear the warning without touching the strings defeats the mechanism.

**A count is not a cause.** Report the arithmetic; state the explanation
separately, with whatever tests it. Two retractions inside thirty-six hours have
this one shape, and in both the counting was correct:

- [15](RETRACTIONS.md) — "four of nine discriminating probes fail the gate" was a
  true count. `p = 0.0035` beside it was computed over thirty-two rows that are
  nine prompt templates.
- [16](RETRACTIONS.md) — "seven of nine probes a second reader does not lose" was
  a true count. *"They measured the reader"* was an attribution, and a model with
  no reader-by-probe term at all fits the same data at `p = 0.229`.

The tell is a sentence where a number is followed by *because*, *so*, or
*which means*. The count survives every later correction; the clause after it is
what gets struck. Before writing that clause, name the simplest model that
reproduces the count without it, and fit it. If it fits, you have a count.

**A comparison across parties must be like-for-like, and asymmetric effort is
the easy way to lose that.** Retraction 16's headline statistic put
`gpt-oss:120b`'s *minimum over four sender passes* against `qwen3.5:35b`'s
*single* pass. A minimum over more draws is smaller for free, so the comparison
manufactured its own result: six of seven at one pass each becomes two of seven.
Where two parties have had different amounts of measurement spent on them, say
so in the sentence that compares them, or equalise before comparing.

---

## Before you push

```bash
python3 metrics/tests/test_metrics.py          # must be green
python3 tools/test_tools.py                    # the checks below can still fail
python3 tools/check_counts.py                  # every stated count vs its source
python3 tools/check_retracted.py               # no withdrawn claim stated as live
python3 tools/check_links.py                   # every internal pointer resolves
python3 tools/check_experiments.py             # site status == the directory behind it
python3 tools/build_translations.py --check    # must say "current"
python3 tools/build_og.py --check              # the social card matches the version
python3 tools/build_wiki.py --check            # /wiki/ matches the sources it maps
python3 tools/build_journal.py                 # regenerate if sources moved
```

Then check the rendered page, not the source, for anything visual. A version
string once shipped as `V0.1` on the live site because it was verified by
re-reading HTML instead of by looking. The same rule applies to generated
images: both social cards said `v0.3` at v0.4, and one of them had its headline
running off the right edge with the bottom fifth blank, because `qlmanage`
scales an SVG by its viewBox *height* and clips the width. Nothing caught it —
a number rendered into pixels is invisible to `check_counts.py`. The card is now
built by `tools/build_og.py` from `CITATION.cff` and the `move` passage, so its
claims come from the same files everything else's do.

**To check whether a deploy landed, compare the live bytes with the built ones.**
Not a grep for a phrase you believe should be there. On 2026-08-06 a Pages deploy
genuinely timed out, and the diagnosis "the new content is not live" was then
drawn from grepping `/wiki/` for sentences that appear nowhere in the wiki build
— it indexes titles, not bodies. That grep returns zero on a perfectly current
site, so it could not have passed, which makes it the mirror of the gate that
cannot fail and just as worthless. The check that works is one line:

```bash
diff <(curl -s https://noophorics.org/wiki/) docs/wiki/index.html && echo current
```

---

## A note for agents that are also experimental subjects

`gpt-oss:120b`, `qwen3.5:35b`, `claude-*` and `codex` appear in this repository
both as tools and as **subjects of measurement**. An agent that has read
`theory/` or an experiment's hypotheses is contaminated as a subject of that
experiment: it has seen what it is supposed to be measured against.

If you are working in this repository, record that you did. An experiment that
later uses your model must either exclude you or declare the exposure. This is
not hypothetical — E-004's probe measure was deliberately *not* adjudicated by
the models E-004 measures, because filtering a measure with its own subjects
selects for probes those subjects agree on, and E-004's detector **is** their
disagreement.

---

*This document is licensed CC BY 4.0.*
