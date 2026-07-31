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
it. A file containing only survivors tells a flattering lie about how the field
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

**Run the check, do not re-read the diff.** Three defects in this repository
survived careful reading and died the moment something was executed: a function
called but never defined, a gate that could not fail, a monitor that grepped
itself. Count what is left; do not conclude from what you changed.

**Translations are re-translated, not re-stamped.** `python3
tools/build_translations.py --check` fails when a watched passage moves. The fix
is to translate the new sentence in all eleven languages. Re-running the build
to clear the warning without touching the strings defeats the mechanism.

---

## Before you push

```bash
python3 metrics/tests/test_metrics.py          # must be green
python3 tools/build_translations.py --check    # must say "current"
python3 tools/build_journal.py                 # regenerate if sources moved
```

Then check the rendered page, not the source, for anything visual. A version
string once shipped as `V0.1` on the live site because it was verified by
re-reading HTML instead of by looking.

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
