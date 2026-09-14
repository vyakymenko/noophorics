# Domain instruments: methods-read supplement

**2026-09-14 · literature and engineering note, not a registration or result.**
This supplements the [September 9 domain-selection draft](2026-09-09-domain-selection.md)
with methods inspected beyond abstracts. No benchmark items were imported, no
probes or hypotheses were authored, and no model calls were made. “Reported”
describes the papers; “Implication” and the recommendation are our assessment.

## Spatial relations — SPARTQA

**Reported:** AUTO generates descriptions from structured image scenes using
grammars and context-sensitive rules. Question generation and answer generation
share stored entities/relations and the `Find-all-relations` procedure. It
checks unique object descriptions; relation inference uses transitivity,
symmetry, converse, inclusion and exclusion. Undetermined yes/no questions have
an explicit “Do not Know” answer. Splits inherit NLVR image splits. The separate
“unseen” evaluation changes vocabulary; consistency and contrast sets modify
questions with preserved or changed answers. These are distinct controls, not
reported disjoint reasoning-template banks.
[Mirzaee et al., §§3–4.1, pp. 4584–4586; Appendix C, p. 4594](https://aclanthology.org/2021.naacl-main.364.pdf).

**Implication:** retain latent scenes and verify exactly what the text entails;
do not answer from facts present only in the underlying scene. The shared
generator/answerer is not an independently implemented verification path.
Vocabulary perturbation can expose surface sensitivity without establishing
structural generalization. This method supports composition of spatial
relations; it does not establish the September draft's proposed reference-frame
transformation component. Ambiguous descriptions and quantifier scope remain
checks for our implementation.

## Formal causal inference — CLadder

**Reported:** the pipeline first constructs graph/query/data combinations whose
answers are identifiable, computes answers and intermediate explanations with a
causal inference engine, then verbalizes them through templates. Small binary
models limit calculation load. Incompatible, trivial or ill-defined graph/query
combinations are omitted. Common, counter-commonsense and invented-name stories
vary the verbal context. The balanced version distributes questions across
story/graph/query combinations and answer classes. Quality checks include
grammar software, sampled human readability and expert problem-solving; these
are not described as independent adjudication of every key. The inspected
methods do not specify a held-out structural-template bank.
[Jin et al., §§3.1–3.4, pp. 5–7; Appendix A.4, p. 20](https://papers.neurips.cc/paper_files/paper/2023/file/631bb9434d718ea309af82566347d607-Paper-Conference.pdf).

**Implication:** preserve the formal query, required information and derivation
alongside each rendering. The oracle is independent of subject responses, but a
separately implemented oracle is not established by these methods. Keep causal
levels distinct: observational association does not exercise intervention.
Formal identifiability alone does not verify that the wording supplies the
assumptions used by the solver.

## Deterministic execution — CRUXEval

**Reported:** a language model generates functions and inputs; Python execution
supplies outputs and scores answers. Filters address syntax, bounded runtime,
exceptions, expensive operations and, on a best-effort basis, nondeterminism and
side effects. Output prediction has a fixed target; input prediction accepts
any input producing the required output. Benchmark items are randomly selected
after filtering, and size selection examines stability of selected model
comparisons. Appendix C.7 distinguishes removing exact benchmark functions from
training from a deliberately overlapping experiment. Appendix D.2 documents
model-dependent prompts and response-format problems.
[Gu et al., §§3–4, Appendices C.7 and D.2](https://arxiv.org/html/2401.03065v1).

**Implication:** execution provides an answer check outside the generating
model, without demonstrating an independent second implementation. Preserve
program-family identity across splits; new inputs to an old function are not a
new structural holdout. Distinguish parse failures from wrong answers. The
paper's performance-informed size choice is not a prospective cutoff for our
study.

## First engineering prototype

**Recommendation, not a crossover prediction:** start with a restricted
deterministic **output-execution** instrument. A pinned runtime and bounded
language subset make exact expected answers, execution traces and deliberately
broken fixtures straightforward to check offline. An independent trace/checker
can then be compared with runtime execution, followed by review of the presented
program and answer mapping. This is an engineering judgment about testability,
not evidence that this family will separate the current readers or measure
their priors.

The useful first deliverable is an offline verifier and manifest format, with
synthetic fixtures, rejection reasons and provenance fields. It need not choose
a model pair, sample size or scientific decision rule. Keep prototype fixtures
outside a later confirmation bank. The September draft's independent
adjudication and confirmation design remain our proposed research practices;
the papers do not supply them automatically. No published item should be called
an untouched holdout merely because it was newly downloaded.

**Exposure:** the Codex reviewer read the cited methods and illustrative paper
items. Together with previously declared repository-hypothesis exposure, this
precludes treating this working context as naive. No repository probe, key,
brief or individual answer content was printed during this supplement.

---

*This document is licensed CC BY 4.0.*
