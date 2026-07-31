#!/usr/bin/env python3
"""Fail if a claim this repository has withdrawn is stated somewhere as live.

`check_counts.py` verifies that stated *numbers* match their source. This
checks the other half: that stated *claims* match theirs. Both exist because
the two halves fail independently, and on 2026-07-31 the second half failed
nine times at once -- an audit found that `docs/index.html` still published
axiom A3, laws L2/L4/L6, the noise-floor definition, the efficiency claim and
two falsification criteria in exactly the wording the repository had struck
through months of commits earlier. Every one had been corrected at its source
and never re-derived on the page.

Nothing would have caught it. The retraction machinery lives in markdown
(`~~struck~~`) and the site is HTML (`<s>struck</s>`), so a correction to one
was invisible to the other. That gap is now this file.

**How it works.** Every `~~...~~` span in the markdown sources is a claim this
repository has withdrawn. Each is normalised to a word sequence and its
`--ngram`-word shingles are indexed. These are *struck spans*, not the eleven
numbered entries in `RETRACTIONS.md` -- one withdrawal is often struck in
several files, so the two counts differ on purpose and are named differently. Then every HTML page is read with `<s>`
regions removed -- what is left is text the site asserts *as true*. Any shingle
of a withdrawn claim appearing in that remainder is a live restatement of a
dead claim, and is reported with both locations.

A withdrawn claim may still be legitimately *quoted* -- a findings page has to
say what it broke. The repository's own norm decides which is which: never
delete a refuted claim, and never state one without its correction. So a
restatement passes exactly when the withdrawal is acknowledged within
`CONTEXT_WORDS` of it. That is mechanical, and unlike a file allowlist it
cannot silently start covering newly added text.

Struck text is not deleted from the site; it stays in place. So the check is
specifically "does this appear OUTSIDE an `<s>`", not "does this appear".

    python3 tools/check_retracted.py            # 0 = clean, 1 = restatements
    python3 tools/check_retracted.py --list     # show the indexed claims
    python3 tools/check_retracted.py --ngram 6  # stricter (more sensitive)

Exit status is what CI reads.
"""

from __future__ import annotations

import argparse
import html
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Sources of retracted claims: markdown carrying ~~...~~ spans.
SOURCES = [
    "PRINCIPIA.md",
    "lexicon.md",
    "RETRACTIONS.md",
    "theory/laws.md",
    "theory/definitions.md",
    "theory/open-problems.md",
    "theory/prior-art.md",
]

# Where a live restatement would be published. docs/journal/** is generated
# from the same markdown and renders ~~x~~ as <s>x</s>, so it is covered by
# the <s>-stripping rather than excluded.
# The sources are targets too. A document can withdraw a claim in one section
# and go on asserting it in another -- PRINCIPIA did exactly that, striking the
# noise-floor definition in section 3 and restating it as live in section 8,
# where it survived every reading for four versions.
TARGETS = ["docs/index.html", "README.md", "AGENTS.md", "CONTRIBUTING.md"] + SOURCES
TARGET_GLOBS = ["docs/journal/**/*.html", "docs/*/index.html"]

DEFAULT_NGRAM = 6

# A withdrawn claim may legitimately be *quoted* -- RETRACTIONS.md is nothing
# but withdrawn claims, and every findings page describes what it broke. The
# repository's own norm decides which is which: never delete a refuted claim,
# and never state one without its correction. So a restatement is legitimate
# exactly when the withdrawal is acknowledged next to it. That is mechanical,
# and unlike a file allowlist it cannot silently start covering new text.
WITHDRAWAL_VOCAB = {
    "retracted", "retraction", "retractions", "withdrawn", "withdrew",
    "withdrawal", "refuted", "refutation", "amended", "amendment", "struck",
    "superseded", "corrected", "correction", "invalid", "deprecated",
    "obsolete", "restated", "killed", "kills",
}
CONTEXT_WORDS = 40

# The vocabulary above has to be *perfective*: it must mark this text as
# already withdrawn, not merely discuss withdrawal. That distinction is not
# pedantic here. A first version included "wrong" and "defect" and treated any
# "refuted" as acknowledgment, and it silently suppressed two of the real
# defects it was built to catch -- because every law card ends "Refuted if:"
# and the falsifier list opens "Noophorics is wrong if:". Both are conditions
# for a *future* refutation, sitting a few words from claims that had already
# been refuted in the past. The conditional forms are excluded by bigram.
CONDITIONAL = {("refuted", "if"), ("wrong", "if"), ("falsified", "if"),
               ("refuted", "when"), ("killed", "if")}

# The retraction index is the one document whose entire content is withdrawn
# claims, quoted in a column headed "Claim" under a title that says so. The
# withdrawal is carried by the table's structure, which a word-window cannot
# see -- row 11's "Killed by" cell reads "the primacy word does not" and
# contains no withdrawal vocabulary at all. Scanning the index for the claims
# it indexes would report every row forever, so it is not a target. This is
# narrow and it has a cost worth naming: a claim asserted as live *inside*
# RETRACTIONS.md is not checked by this file. Nothing else is skipped.
NOT_A_TARGET = {"docs/journal/retractions/index.html", "RETRACTIONS.md"}

# Phrases too generic to carry a claim: a shingle made only of these is noise.
# Kept deliberately short -- a long stopword list would hide real hits.
STOP = {
    "the", "a", "an", "of", "to", "in", "is", "it", "and", "or", "that",
    "this", "for", "on", "at", "as", "by", "with", "not", "be", "are", "was",
}


def normalise(text: str) -> list[str]:
    """Text -> comparable word sequence, across markdown/HTML/entity spelling."""
    text = html.unescape(text)
    text = unicodedata.normalize("NFKD", text)
    # Dashes, quotes and non-breaking spaces differ between the two lanes;
    # they never carry the claim, so flatten them all to whitespace.
    text = re.sub(r"[‐-―‘’“” −]", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)          # any surviving markup
    text = re.sub(r"[`*_>#\[\]()|]", " ", text)   # markdown punctuation
    text = text.lower()
    # The site is written in British spelling and the markdown in American, so
    # "optimise"/"optimize" split one claim into two and hid the efficiency
    # retraction from every shingle length above five. Both sides are folded
    # the same way; over-folding a word like "promise" is harmless precisely
    # because it happens on both sides.
    text = re.sub(r"is(e|ed|es|ing|ation)\b", r"iz\1", text)
    return re.findall(r"[a-z0-9]+", text)


def shingles(words: list[str], n: int) -> set[tuple[str, ...]]:
    if len(words) < n:
        return set()
    out = set()
    for i in range(len(words) - n + 1):
        gram = tuple(words[i:i + n])
        if all(w in STOP for w in gram):
            continue
        # Symbol-dense runs carry no claim: `F*(A→B) ≠ F*(B→A)` normalises to
        # "f a b f b a", which would match any other formula on the page.
        if sum(len(w) == 1 for w in gram) * 2 >= n:
            continue
        out.add(gram)
    return out


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def collect_retracted(n: int):
    """Every ~~...~~ span in the sources, as (shingle) -> (file, line, text)."""
    index: dict[tuple[str, ...], tuple[str, int, str]] = {}
    claims = []
    for rel in SOURCES:
        path = ROOT / rel
        if not path.exists():
            continue
        raw = path.read_text(encoding="utf-8")
        # Spans may wrap lines and, in blockquotes, carry "> " continuations.
        for m in re.finditer(r"~~(.+?)~~", raw, re.S):
            body = re.sub(r"\n\s*>?\s*", " ", m.group(1))
            words = normalise(body)
            grams = shingles(words, n)
            if not grams:
                continue
            where = (rel, line_of(raw, m.start()), " ".join(body.split()))
            claims.append((where, len(grams)))
            for g in grams:
                index.setdefault(g, where)
    return index, claims


def strip_struck(markup: str) -> str:
    """Remove <s>...</s> and ~~...~~ -- what remains is asserted as true."""
    markup = re.sub(r"<s\b[^>]*>.*?</s>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"<del\b[^>]*>.*?</del>", " ", markup, flags=re.S | re.I)
    markup = re.sub(r"~~.+?~~", " ", markup, flags=re.S)
    return markup


def targets() -> list[Path]:
    seen, out = set(), []
    for rel in TARGETS:
        p = ROOT / rel
        if p.exists() and p not in seen:
            seen.add(p)
            out.append(p)
    for pattern in TARGET_GLOBS:
        for p in sorted(ROOT.glob(pattern)):
            if p not in seen:
                seen.add(p)
                out.append(p)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ngram", type=int, default=DEFAULT_NGRAM,
                    help="shingle length in words (lower = stricter)")
    ap.add_argument("--list", action="store_true",
                    help="print the indexed retracted claims and exit")
    args = ap.parse_args()

    index, claims = collect_retracted(args.ngram)

    if args.list:
        for (rel, line, text), count in claims:
            print("%-26s :%-5d %3d grams  %s" % (rel, line, count, text[:90]))
        print("\n%d struck spans, %d shingles" % (len(claims), len(index)))
        return 0

    if not index:
        print("check_retracted: no struck spans found -- is the source list right?")
        return 1

    hits, acknowledged = [], 0
    for path in targets():
        rel = path.relative_to(ROOT).as_posix()
        if rel in NOT_A_TARGET:
            continue
        raw = path.read_text(encoding="utf-8")
        live = strip_struck(raw)
        words = normalise(live)
        for i in range(max(0, len(words) - args.ngram + 1)):
            gram = tuple(words[i:i + args.ngram])
            src = index.get(gram)
            if not src:
                continue
            lo = max(0, i - CONTEXT_WORDS)
            hi = min(len(words), i + args.ngram + CONTEXT_WORDS)
            context = words[lo:hi]
            marked = False
            for j, w in enumerate(context):
                if (w, context[j + 1] if j + 1 < len(context) else "") in CONDITIONAL:
                    continue
                if w in WITHDRAWAL_VOCAB or (w == "v0" and j + 1 < len(context)):
                    marked = True
                    break
            if marked:
                acknowledged += 1
                continue
            hits.append((rel, " ".join(gram), src))

    # One report per (target file, source claim) -- a long restatement matches
    # on many overlapping shingles and is one defect, not thirty.
    grouped: dict[tuple[str, tuple], str] = {}
    for rel, gram, src in hits:
        grouped.setdefault((rel, src), gram)

    if not grouped:
        print("check_retracted: %d struck spans, none restated as live "
              "across %d files (n=%d); %d quoted with the withdrawal acknowledged"
              % (len(claims), len(targets()), args.ngram, acknowledged))
        return 0

    print("check_retracted: %d struck span(s) stated as live, with no "
          "withdrawal acknowledged within %d words\n" % (len(grouped), CONTEXT_WORDS))
    for (rel, src), gram in sorted(grouped.items()):
        src_file, src_line, src_text = src
        print("  %s" % rel)
        print("    restates: ...%s..." % gram)
        print("    withdrawn at %s:%d" % (src_file, src_line))
        print("    struck text: %s" % src_text[:150])
        print("    fix: state the correction, or strike it in place with <s>...</s>")
        print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
