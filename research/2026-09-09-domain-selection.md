# E-003 domain selection: a protocol draft

**2026-09-09 · design proposal, not a pre-registration or a result.** No new
probe text, key, model response or experiment is produced by this document. Its
numbers below are proposed budgets and decision rules, not measurements.

The next useful E-003 step is an exploratory screen of **different reasoning
operations**, followed by an untouched confirmation set. Trying another model
on the existing two rule-application tasks does not resolve the remaining
construct problem: full-specification accuracy measures performance with the
information supplied, while L2's sharper form requires an independently
specified direction of domain prior.

## What the existing record permits

[L2](../theory/laws.md#l2) states its sharper form for a shared,
sender-independent reference, and depends on [Problem
2](../theory/open-problems.md): measuring prior overlap without using the
transfer outcome to define it. The [crossover
reanalysis](../probes/riverside-30/RESULTS-crossover.md) distinguishes a ceiling
tie, a comparison confounded by inference settings, and a model failing the
adopted sender gate. No useful crossover has been found. That is neither proof
that one does not exist nor evidence that a particular new task will supply it.

[THIRD-MODEL.md](../probes/THIRD-MODEL.md) and the [llama
result](../probes/RESULTS-llama-crossover.md) also show why model lineage cannot
stand in for task competence or compatible inference settings. The following
families are candidates for different operations, **not predictions of which
model will win**.

## Three candidate families

| Candidate | Proposed source and finite query type | What changes from the existing tasks | Independent route to a key | Main alternative explanation |
|---|---|---|---|---|
| **Spatial scene reconstruction** | A textual scene with explicitly defined coordinates, object relations and a reference frame; queries classify a spatial relation from a fixed vocabulary. | Composing relations and transforming a reference frame, rather than deciding eligibility from a numbered policy. | A geometric representation plus a separately implemented relation checker; independently check that the text describes that representation. | Reference-frame ambiguity, linguistic parsing and working-memory demands. |
| **Causal intervention** | A small, fully specified acyclic causal model with finite variables; queries concern a distribution or outcome after an intervention. Keep observational, interventional and counterfactual questions in separately identified strata. | Replacing a generating mechanism and evaluating its consequences, rather than applying a decision policy to a record. | Exhaustive enumeration of the finite model plus an independent calculation. Exclude unidentifiable or underspecified questions before models answer. | Formal causal reasoning ability, arithmetic load and representation of the graph. |
| **Program semantics** | A short deterministic, terminating program and input under a pinned language/runtime; queries classify its output or state from a fixed answer vocabulary. | Tracking computation and state, rather than following a prose policy. | Execution in the pinned runtime plus a separate interpreter or independent trace. Restrict the language to a small, explicitly specified subset. | Familiarity with syntax, tokenization, algorithmic skill and runtime-specific semantics. |

These distinctions are design intentions. A causal or code task is still a
formal task; merely replacing numbered rules with code or a graph would not
establish a different prior. A structural audit must verify that each family
requires the operation named above. The pilot must then show whether these
operations produce usable measurements on the chosen models.

There is primary precedent for each task type. **SPARTQA** studies spatial
question answering over text and generates scene descriptions with associated
questions; it supports the spatial task family, not any present model ordering.
[Mirzaee et al., NAACL 2021](https://aclanthology.org/2021.naacl-main.364/).
**CLadder** constructs questions at observational, interventional and
counterfactual levels with an oracle causal inference engine; it supports the
causal family and a route to independent ground truth.
[Jin et al., NeurIPS 2023](https://papers.neurips.cc/paper_files/paper/2023/hash/631bb9434d718ea309af82566347d607-Abstract-Conference.html).
**CRUXEval** separates code input/output prediction from code generation; it
supports execution reasoning as a distinct operational target.
[Gu et al., 2024](https://arxiv.org/abs/2401.03065).

Only these papers' abstracts and publication metadata were inspected for this
draft. Published benchmark items are not proposed as a clean holdout, and no
items were imported. Newly generated instances would reduce direct item reuse;
they would not prove that their patterns were absent from training.

## Three quantities that must remain separate

**Full-specification competence:** accuracy when all information needed to
answer is supplied. This determines whether the model can perform the task at
the proposed operating point. It is not a direct measurement of a latent prior.

**Pre-transfer disposition:** the answer distribution under a frozen baseline
context, without the source or brief. This is the receiver's operational
baseline for that particular measure. Random hidden coordinates, arbitrary
causal parameters or a withheld program cannot be recovered from domain
knowledge alone; high agreement in this condition can instead be shared bias.
The baseline context and class distribution must therefore be specified, not
treated as a neutral absence of information.

**Domain prior:** the explanatory construct in L2. It needs an independent
operationalization fixed without the transfer outcomes. Two possible research
routes remain open:

- An **observational route** measures domain competence on a separate task bank
  and compares it with a separately frozen general-capability battery. That can
  identify opposing *performance orderings*. Calling the domain score a prior
  would still require justification; a domain-specific solver can reproduce
  that ordering without the proposed prior explanation.
- An **assigned-familiarization route** randomizes access to domain background
  in fresh model contexts, using equally long control material and target
  instances absent from the background. This would test an explicitly supplied
  background intervention. It would not establish a claim about differences in
  pretraining priors, and persistent background could also change attention or
  instruction following.

The screen below supports the first route only as exploratory instrument work.
Choosing between these routes is a remaining scientific decision. A contrast
between conventional and renamed symbols could diagnose representation
sensitivity, but renaming also changes parsing and tokenization; it is not by
itself an intervention on prior knowledge.

**No causal attribution to prior is licensed by an observed crossover alone.**
Before making that attribution, name and fit a model that has general ability,
task difficulty, task-specific competence and representation effects but no
prior mechanism. A successful predictive contrast on a holdout can improve the
evidence; it does not remove an unmeasured alternative mechanism.

## Proposed bounded exploratory pilot

This is a proposal for a later prospective plan. **Nothing in this section is
authorization to run it or a claim that its numerical cutoffs are validated.**

1. **Freeze a design manifest before subject calls.** Name two initial readers
   (`gpt-oss:120b` and `qwen3.5:35b` are practical candidates already in the
   programme), their exact weight/runtime identities, prompt/schema versions,
   inference settings, seeds, failure rules, scenario families and the selection
   rule. Do not add readers or change prompts after seeing which gives a
   crossover.
2. **Build 12 distinct structural templates per family**, one scenario and one
   scored query per template: 36 queries. Balance answer classes and three
   author-declared difficulty strata where possible before subject responses.
   Declare dependencies between templates; relabeled copies do not count as
   independent templates. All authoring and key adjudication precede sampling.
3. **Prepare three contexts for every query:** full source; a canonical brief;
   and the frozen baseline. Use the same context text for both readers. The
   brief follows a fixed, source-based compression recipe, established before
   outcomes and without choosing omissions by their expected answers. Record
   the retained facts, length and missing facts. This is a headroom diagnostic,
   not a sender-to-receiver transfer experiment or a test of L2.
4. **Draw two equal batches of five responses** for every reader × query ×
   context cell. Retain all categorical draws, exact prompts and batch identity.
   Report modal answers with ties and winning margins; do not hide uncertain
   distributions behind a single mode. No repeated drawing until a desired
   modal answer appears.
5. **Use a separate capability anchor:** 16 items from a fixed battery outside
   these candidate families, the same two batches of five for both readers.
   The battery, weighting and provenance must be chosen before the pilot.
   Sixteen items can flag a gross reversal; they cannot establish an invariant
   general-capability ranking. If its ranking is uncertain, report that and
   leave the L2 pair-selection condition unresolved.
6. **Publish every family and every gate outcome.** Do not publish only the
   candidate with the largest model difference. Freeze at most one candidate
   for later confirmation under the rule below; permit the outcome “none”.

| Proposed budget item | Calls |
|---|---:|
| 3 families × 12 queries × 2 readers × 3 contexts × 2 batches × 5 draws | 2,160 |
| 16 separate anchor items × 2 readers × 2 batches × 5 draws | 320 |
| Maximum non-experimental compatibility calls | 16 |
| Reserved transport retries; never a second chance after a valid answer | 104 |
| **Hard ceiling, including all attempted calls** | **2,600** |

The first two rows contain 2,480 planned experimental responses; the other rows
reserve capacity rather than promising it will be used. Stop at the ceiling,
retain incomplete cells and report an incomplete pilot. No generation or rater
calls are hidden in that budget: authorship and independent key adjudication
must be arranged separately before this plan can run. Wall time is not forecast
from the old rule probes, because new task complexity and reasoning lengths can
change it materially.

### Proposed selection rule, to be fixed before sampling

First assess **feasibility**, not the desirable direction of a model gap:

- Every source/key pair passes independent adjudication and the runner's
  positive and deliberately failing checks.
- In each full-source batch, each reader has at least 11 correct modal answers
  among the 12 queries, with no modal tie. This is a proposed engineering
  screen; it is not E-004's gate, and passing 12 items does not establish a
  population accuracy bound.
- The canonical brief produces at least three queries per reader whose modal
  answer differs from that reader's full-source modal answer in **both**
  batches. Record whether those changes help or hurt correctness. This is a
  proposed minimum count of observable changes, not a power calculation.
- Complete answer distributions, error counts, batch changes and class-prior
  baselines remain in the report. These criteria never authorize deleting
  inconvenient queries after outcomes.

Among feasible candidates, select the first in the prospectively frozen order
**spatial, causal, code** that shows an exploratory reader ordering opposite to
the separately anchored capability ordering in both batches. Specify the domain
ordering as mean per-draw correctness under the canonical brief, with equal
weight for each template. A tie or an uncertain anchor is not an opposing
ordering. This ordering is a screen for a later hypothesis; it is not the
independent prior measure needed for L2 and cannot serve as its confirmation.
The family order is a proposed administrative choice, not a belief about the
likely result, and may be changed only before the prospective plan is fixed.

If no family meets these conditions, report that the bounded screen supplied no
candidate. Do not widen cutoffs, change the anchor, remove difficult templates or
add another family inside the same analysis. A subsequent screen requires a new
prospective design and must carry this one forward in its evidence inventory.

## Confirmation requires a different set and a fuller protocol

Define the selection/confirmation split at the **structural-template level**.
Reserve a separate template bank for confirmation before inspecting selection
outcomes; random renaming of the same template is not an untouched holdout.
Record generator versions, seeds, manifests and hashes. Keep confirmation
items, keys and model outcomes outside the selecting agent's context. A hash
records identity; access separation supplies blinding.

After selecting a family, write a new E-003 registration before opening that
holdout. It must fix the independent prior operationalization, the capability
ordering and its uncertainty, both message directions, the composer sampling
budget, content/length controls, and all outcome definitions. The canonical
screening brief does not substitute for independently sampled messages in each
direction. Include every selected pair, including a confirmation failure.

**Reference:** for the eventual criterion experiment, `R` is the same
independently validated key distribution for both directions, a point mass on
the correct outcome in the proposed finite deterministic tasks. Report the
measure hash, source and key provenance, answer vocabulary, baseline contexts
and sender/receiver identities. Any `F*_R` needs its admissibility checks and
decomposition against that declared reference. The screen itself reports raw
correctness and answer distributions; it does not compute normalized fidelity
or label sender replication as understanding.

The key author, key adjudicator and measured subjects must be separate roles.
Agreement between a generator and its own checker is insufficient. Have an
independent adjudicator verify the text-to-world or text-to-program mapping,
answer uniqueness and implementation, blind to model responses and candidate
rankings. Record disagreements and repairs before subject calls. Current
planning agents have read L2 and must be recorded as exposed; they cannot be
reintroduced as independent hypothesis-blind judges.

In the eventual analysis, the repeated draws are measurements within an item,
and repeated items can share a template. Estimate uncertainty at the independent
template/message unit specified by the design, preserving all pairing and
nesting. Fit the simpler capability/difficulty explanation before attributing
anything to a prior. Do not select using a discovery p-value and then reuse it
as confirmation. Freeze primary contrasts and multiplicity handling, calculate
the required holdout size from relevant pilot variation, and permit a result
that is too imprecise to decide. A count of twelve templates is not a claim of
adequate power.

## Inference effort and remaining decisions

Equal numbers of calls are necessary for like-for-like sampling; they do not
equalize reasoning effort. Record each model's supported settings, actual token
use, truncation/refusal rates and latency. Verify schema compatibility on
non-experimental inputs before fixing the run. Equal names such as `medium`, or
omitting the same parameter, do not establish equal compute across models.
Under default settings, the estimand is model-plus-serving-regime performance.
No cross-provider comparison should silently inherit a baseline from another
regime.

The concrete decisions still needed before a prospective plan can be finalized
are:

1. Choose the claim: observational domain-competence prediction, or a separate
   randomized familiarization study with its narrower interpretation.
2. Name the independent author/adjudicator and decide how the untouched template
   bank will be held out from selection.
3. Fix the capability anchor, exact model/runtime regimes, representation and
   compression recipes, and confirm or replace the proposed screen cutoffs.
4. Allocate the proposed 2,600-call ceiling and the separate instrument-building
   work; decide the later confirmation budget after the exploratory evidence
   and a prospective power analysis exist.

These are design choices to resolve, not missing measurements that can be
filled by treating the existing sender-accuracy table as a measure of prior.

---

*This document is licensed CC BY 4.0.*
