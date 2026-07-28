# E-001 — Amendment 002: blind rewrite of the generation prompts

**Date:** 2026-07-28
**Amends:** the instrument only. Hypotheses, analysis plan, significance
criteria, and promotion gates in [PREREGISTRATION.md](PREREGISTRATION.md) are
**unchanged and unedited.**

---

## The problem this fixes

E-001 compares two message encodings produced by the same sender under the
same budget. The encodings are elicited by two prompts. Those prompts were
written by the experimenter, who holds [L5](../../theory/laws.md#l5) and
[L6](../../theory/laws.md#l6) and finds them satisfying.

This was declared as a limitation in
[PREREGISTRATION.md §4.1](PREREGISTRATION.md) and flagged in the
[founding journal entry](../../journal/2026-07-28-founding.md) as the most
likely way the experiment would mislead us. Declaring a confound does not
remove it.

## What the inspection found

It was not hypothetical. The original pair was asymmetric in the direction of
the hypothesis:

| | Original prompt |
|---|---|
| CONTRASTIVE | *"Write ONLY the boundaries: the edge cases, the exclusions, the places where a reasonable person would guess wrong, what does NOT follow from what, and which rules override which. No prose, no introduction... If a fact would not change anyone's verdict on any case, leave it out."* |
| NARRATIVE | *"Write it as fluent, well-organized explanatory prose. Use clear paragraphs and connective reasoning... Make it read well."* |

The contrastive prompt is a specification. The narrative prompt is an
aesthetic gesture. A quality gap between the resulting briefs would have been
partly attributable to prompt strength, and it would have favoured H1 and H3.

## Procedure

The two prompts were rewritten by an independent agent under blinding:

- It received the source spec and the two style descriptions, inline.
- It was **not** told the hypotheses, the laws, the field, the metrics, the
  existence of phantom agreement, or which condition anyone expected to win.
- It was instructed that both prompts would be used in an A/B comparison, that
  each must be the best possible prompt for its own style, and that a weak
  version of either would invalidate the comparison.
- It was instructed not to read files or explore the repository. It made
  **zero tool calls**, so the blinding held: it could not have discovered the
  hypotheses even by accident.

## What changed

The replacement pair shares, verbatim across both conditions:

- the same stakes framing (unreachable sender, real decisions, guesses become
  outcomes),
- the same anti-approximation warning ("approximate is worse than absent,
  because it is believed"),
- the same explicit triage instruction, so the budget forces prioritization
  rather than truncation,
- the same output-purity and hard-limit clauses.

They differ only in the mechanism each style uses to reach decision accuracy:
one paragraph on structural explanation for NARRATIVE, one paragraph
enumerating boundary categories for CONTRASTIVE. The two are within a few
lines of each other in length.

Both prompts are in [`runner.py`](runner.py). The rewriting agent's own
reasoning about why it considers them equally strong is preserved in the
commit that introduced them.

## What this does and does not buy

**Does:** removes a demonstrated asymmetry that favoured the experimenter's
hypothesis, and moves the prompt-authoring step outside the hypothesis-holder's
hands.

**Does not:** make E-001 unbiased. The experimenter still chose the two style
categories, the domain, the probe measure, the budget, and the metrics. An
independent prompt author constrains one degree of freedom out of several.
The honest description is *less biased*, not *blind*.

It also cannot rule out that the new pair is asymmetric in the *other*
direction. The rewriting agent judged them equal; that judgment is not
independently verified, and no procedure here measures prompt strength
directly. [Problem 4](../../theory/open-problems.md) — optimal encoding search
— is the eventual principled answer: search for the best encoding within each
family rather than hand-writing one representative of each.

## Standing

Committed before the replacement run produces any data.

---

*This document is licensed CC BY 4.0.*
