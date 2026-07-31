# The public page was still publishing v0.1

**2026-07-31.** A four-lens consistency audit over the repository returned
twenty findings, all claim-bearing, all verified against source. They
deduplicate to nine places. Eight of the nine are on `docs/index.html`, and
every one is the same defect: a claim corrected at its source and never
re-derived on the page.

The page was stating, as live and unqualified:

| | site said | source says |
|---|---|---|
| **A3** | dispositions untransferable at any message length | refuted — a 113-token lookup table reaches `F* = 1`; restated for held-out probes at bounded cost |
| **D_floor** | the irreducible divergence from the parties' stochasticity | there is none — it is finite-sample estimator bias at a stated `n` |
| **η** | the quantity engineering should optimise | a ratio with a signed numerator is not an ordering |
| **L2** | `F*(A→B) ≠ F*(B→A)` | withdrawn as tautological |
| **L4** | fidelity is multiplicative along a chain, an invariant core survives arbitrarily many hops | withdrawn as ill-typed; the existence claim dropped as unfalsifiable |
| **L6** | the field's first engineering prescription | refuted — I-PASS, 2014 |
| **falsifier 2** | `Φ ≈ 0` refutes the programme | invalid — that scores a maximally pathological party as the refutation |
| **falsifier 3** | `K ≈ 1` in practice | would have fired from search size alone |

The ninth was in `PRINCIPIA.md` itself: §3 struck the noise-floor definition,
and §8 went on asserting it. Every other correction in that file is struck in
place. That one was written in a different section and never revisited.

## Why nothing caught it

The retraction machinery lives in markdown, as `~~struck~~`. The site is HTML,
where the same thing is `<s>struck</s>`. A correction to one was invisible to
the other, and `tools/check_counts.py` — which does verify every stated number
against its source — checks counts, not claim text.

So the page passed every check the repository had while contradicting itself
across four sections. It said *"Axiom A3 was false as first stated"* in the
refuted-work section and stated A3 in the refuted form 589 lines above. It
carried the v0.4 heading **"Understanding is measured by behavioural
convergence toward a declared reference"** directly above a pull-quote, cited
to `Principia Noophorica §3`, giving the v0.1 sentence that §3 struck.

## The check that now exists

[`tools/check_retracted.py`](../tools/check_retracted.py) indexes every
`~~span~~` in the markdown sources as word shingles, then reads every published
page with `<s>` and `~~` regions removed — what remains is text asserted as
true. A shingle of a withdrawn claim appearing in that remainder is reported
with both locations.

A withdrawn claim may still be legitimately quoted; a findings page has to say
what it broke. Rather than an allowlist of files to skip, the check uses the
repository's own norm — *never delete a refuted claim, never state one without
its correction* — and passes a restatement when the withdrawal is acknowledged
within forty words. An allowlist would have silently started covering newly
added text; this cannot.

## Three things the check found about itself

**Its first version suppressed two of the defects it was built to catch.** The
acknowledgment vocabulary included `wrong` and treated any `refuted` as a
withdrawal marker. Every law card on the site ends **"Refuted if:"** and the
falsifier list opens **"Noophorics is wrong if:"** — conditions for a *future*
refutation, sitting a few words from claims already refuted in the past. The
vocabulary had to become perfective, and the conditional forms are now excluded
by bigram.

**It saw exactly as much as the striking discipline gave it.** L2's headline
and falsifier 3's old wording had been corrected in *prose* rather than struck,
so nothing indexed them and no shingle length would have found them. Both are
now struck at source, which is the repository conforming to its own rule rather
than a change to the tool.

**One claim was hidden by a spelling.** The site writes `optimise`, the
markdown `optimize`. That single letter split one claim into two and hid the
efficiency retraction at every shingle length above five. Both sides are now
folded the same way.

## What it found that the audit did not

With the sources conforming, the check reproduces every site defect the
twenty-finding audit reported — and adds two the audit did not.

The first is the pull-quote above: the operational definition of understanding,
the sentence the whole programme rests on, stated in its v0.1 form in the two
most-read files in the repository, `README.md` and the landing page. Both cite
the section that struck it.

The second is in `theory/laws.md` itself. L2's section blockquote — the
headline statement of the law, the first thing under the heading — gave the
withdrawn form, while the paragraph twenty lines below explained why it was
withdrawn. Twenty-five agents read that file and none reported it. A word
comparison did, because it does not get tired at line 60 and satisfied by line
79.

That is the honest ranking: the audit found what needed reading and judgment,
and it missed two things that needed only patience. The two instruments are not
substitutes.

## The uncomfortable part

The audit ran against a repository whose founding document says *"a claim here
is worth what its check is worth"*, and whose front page has said since v0.1
that nothing is established and eleven claims are withdrawn. The withdrawals
were real, made in public, dated, indexed and linked.

They were made in the files, and the page kept selling the old version.

Every one of these corrections had already been paid for — argued, verified,
committed. The failure was not of honesty and not of rigour. It was that a
correction was treated as finished when the source changed, and the site is
where the claim is actually made to a reader.

---

*This document is licensed CC BY 4.0.*
