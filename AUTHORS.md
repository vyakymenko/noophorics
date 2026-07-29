# Authorship and contributions

Noophorics was founded on 2026-07-28 by **Valentyn Yakymenko**.

This file records who did what, in roles rather than in adjectives. A programme
whose subject is the transfer of understanding between humans and machines
cannot be vague about which understanding came from where — the attribution is
itself a noophoric record, and a fuzzy one would be the field's own central
pathology applied to its own history.

---

## Valentyn Yakymenko — founder, principal investigator

[github.com/vyakymenko](https://github.com/vyakymenko) · [noophorics.org](https://noophorics.org)

Using the [CRediT](https://credit.niso.org/) taxonomy:

- **Conceptualization.** The programme exists because he asked for a science to
  be founded from zero, and specified that it should concern the connection
  between minds — human to machine, machine to machine.
- **Supervision.** Every directional decision is his: open source from day one,
  the dual Apache-2.0 / CC BY 4.0 split, the domain, the sequencing of repairs
  after the reviews, the choice to stop spending rather than push a compromised
  run to completion.
- **Resources.** Domains, API budget, and the hardware the experiments run on.
- **Validation.** He commissioned the adversarial review, and relayed the first
  one himself.

That last item deserves to be stated plainly rather than buried in a list.

**Every major finding in this repository came from outside the work, and he is
the reason the outside was let in.** The inflated noise floor, the refutation of
axiom A3, the discovery that `F*` rewards replicating the sender's errors, the
tautological form of L2, the ill-typed form of L4, the underpowered design —
none of these were found by the author of the code. They were found because the
founder insisted the programme be handed to reviewers who were free to break
it, and then accepted the results when they did.

Setting up the conditions under which your own work can be falsified, and then
funding the falsification, is a scientific contribution. It is the one this
field would recognise as the founding act.

## Claude (Anthropic) — instrument and collaborator

Drafted the theory documents, the metrics implementation, the experimental
apparatus, the protocol, and this site, under the direction above. Also
authored several of the defects listed in the previous section, and the
retractions that followed.

Disclosed here rather than elided, for two reasons. Prevailing scholarly norms
require disclosure of substantial AI contribution and do not admit AI systems as
authors. And more particularly: this programme measures what survives transfer
between a human and a model. A repository that obscured which side produced
which artifact would be withholding its own primary data.

## Adversarial reviewers

Two independent reviews are load-bearing on the current state of the theory and
are cited in the documents they changed:

- The review that identified the noise-floor estimator defect, the
  answer-table refutation of A3, the pseudoreplication in E-001, and the
  runner's divergences from its own pre-registration.
- The review that identified error-replication in `F*` — verified against the
  cached draws before acceptance and now recorded in
  [FINDINGS](experiments/E-001-fluency-cost/FINDINGS.md) — along with the
  capacity estimator's winner's curse and the pre-registration's amendment
  loophole.

Blind prompt authorship for [E-001](experiments/E-001-fluency-cost/) and
[E-001b](experiments/E-001b-fluency-factorial/) was performed by agents kept
ignorant of the hypotheses, as recorded in the respective amendments.

---

## Contributing

Contributors are added here with their roles. See
[CONTRIBUTING.md](CONTRIBUTING.md); the pre-registration norm applies to
everyone, including the founder and including the drafting model.

## Citation

See [CITATION.cff](CITATION.cff).

---

*This document is licensed CC BY 4.0.*
