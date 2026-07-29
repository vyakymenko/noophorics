"""The four cell prompts for E-001b.

Written by an independent agent, blind to the hypotheses, the laws, the
metrics, and which cell anyone expected to win. It was given only the source
spec and the two style axes, told the four prompts feed an A/B comparison and
that a weak one invalidates it, and instructed not to read files. It made zero
tool calls, so the blinding could not have failed even by accident.

Structure, which is the point: every prompt is five blocks in the same order --
framing, what-to-include, how-to-write, precision, output. Only blocks 2 and 3
vary, and each has exactly two variants appearing VERBATIM in the two cells
that share them. So the difference between any two cells is textually exact.

Each varying block carries a firewall clause, because the two axes want to
collapse into each other:

    content blocks end "This is a decision about what goes in, not about how
    it is written."

    style blocks insist the constraint applies to wording only and must
    neither buy nor cost content.

The independent author flagged where the design is most at risk, and it is
recorded here rather than discovered later: boundary material is intrinsically
list-shaped and invites clipped output even when prose is demanded (threatening
cell B), while a terse register invites shedding whole areas rather than words
(threatening cell C). A secondary risk is the fixed budget itself -- terse notes
fit more content per token, so the LOW-polish cells may look better covered for
reasons unrelated to what was selected.
"""

from __future__ import annotations

__all__ = ["CELLS", "CELL_AXES"]

_FRAMING = """You are holding a set of submission-handling rules. A colleague \
who has never seen those rules, and never will, has to decide real cases with \
them. The note you are about to write is the only thing they will have: they \
cannot ask you anything afterwards, they cannot look at the source, and the \
verdicts they issue are final and affect real submitters. Whatever you leave \
out, they will be guessing at."""

_BROAD = """Your note must represent the material as a whole. Convey what the \
scheme is for, what each of its parts requires, and how those parts assemble \
into one working system, so that the reader ends up holding a faithful \
miniature of the source rather than a handful of pieces of it. Coverage is the \
priority: no part of the source should be missing entirely from the picture the \
reader forms, and where you must compress, compress evenly rather than dropping \
whole areas. This is a decision about what goes in, not about how it is \
written."""

_NARROW = """Your note must stay at the edges of the material. Spend the space \
on exact cut-offs and which side of each one falls inside and which outside; on \
what is excluded and what lifts an exclusion; on what a given provision reaches \
and what it pointedly does not; on which provision gives way to which where two \
of them meet; and on cases that resemble each other closely but come out \
differently. Leave out orientation, purpose, and any general account of what \
the scheme is, along with anything a reader would land on correctly without \
being told. This is a decision about what goes in, not about how it is \
written."""

_HIGH_POLISH = """Write it as considered, connected prose: complete sentences \
that follow from one another, with the relationships between points spelled out \
in the wording rather than left to the reader to infer. Give the note a shape, \
an order that carries a reader from the first line to the last, and work the \
sentences over so the result reads smoothly and can be understood on a single \
pass. Reading well must not cost you content, though: if a sentence sounds good \
and carries nothing, cut it and spend the space on substance."""

_LOW_POLISH = """Write it stripped down: bare declarative statements, one item \
per line, no opening, no closing, no bridging or linking phrases, nothing whose \
job is to introduce or round off other lines. Use the fewest words that still \
carry the item, dropping articles and connectives wherever the meaning survives \
without them. Do not work the wording over and do not make it agreeable to \
read; raw notes are the target. Cutting applies to words only, never to \
content: strip the phrasing hard and put every token you save back into what \
the note actually says."""

_PRECISION = """Precision decides this. Every number, comparison and condition \
you carry across must be exactly as the source has it; a detail transferred \
loosely will hurt your colleague more than a detail you never mentioned."""

_OUTPUT = """Stay within {budget} tokens. Output the note and nothing else: no \
preamble, no account of what you decided to include, no sign-off."""


def _assemble(content: str, style: str) -> str:
    return "\n\n".join([_FRAMING, content, style, _PRECISION, _OUTPUT])


# cell -> (polish, selection). The axes are what the hypotheses are stated on;
# the cell letters are only labels.
CELL_AXES = {
    "A": ("fluent", "declarative"),
    "B": ("fluent", "contrastive"),
    "C": ("terse", "declarative"),
    "D": ("terse", "contrastive"),
}

CELLS = {
    "A": _assemble(_BROAD, _HIGH_POLISH),
    "B": _assemble(_NARROW, _HIGH_POLISH),
    "C": _assemble(_BROAD, _LOW_POLISH),
    "D": _assemble(_NARROW, _LOW_POLISH),
}


def _check_shared_blocks() -> None:
    """The design's validity rests on the shared blocks being byte-identical."""
    for block in (_FRAMING, _PRECISION, _OUTPUT):
        assert all(block in text for text in CELLS.values()), "shared block drifted"
    assert _BROAD in CELLS["A"] and _BROAD in CELLS["C"]
    assert _NARROW in CELLS["B"] and _NARROW in CELLS["D"]
    assert _HIGH_POLISH in CELLS["A"] and _HIGH_POLISH in CELLS["B"]
    assert _LOW_POLISH in CELLS["C"] and _LOW_POLISH in CELLS["D"]


_check_shared_blocks()
