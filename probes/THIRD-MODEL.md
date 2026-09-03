# Choosing a third model, and what it is for

**Written 2026-09-03, while the weights download and before any measurement.**
The choice of instrument is a claim in this repository, so it is argued here
rather than in a commit message after the fact.

## What three blockers have in common

Three separate lines are stalled, and all three want the same thing:

1. **E-003 / [L2](../theory/laws.md#l2).** Its sharper form needs a model pair
   whose **domain prior and general capability disagree**. `gpt-oss:120b` and
   `qwen3.5:35b` cannot supply one — `qwen` is stronger or level on both domains
   this repository owns. Measuring only that *some* asymmetry exists is
   [retraction 5](../RETRACTIONS.md), withdrawn as tautological.
2. **The D-study, obstacle 3** ([D-STUDY](meridian-ix16/D-STUDY.md)). A rater
   facet with two levels has no variance to estimate. Brennan's theorem is
   blunt: with every facet fixed, error variance is zero *by construction*. Two
   readers can show a structure survives; they cannot say how much of it is
   reader.
3. **E-001c's register filter.** [Retraction 18](../RETRACTIONS.md) showed the
   fluent length floor was `gpt-oss`'s, not the register's — but that measured
   only the band half of E-001c's gate. Rating the other half needs a rater that
   is **not the composer**, and `blind_rating.py` says so in its own docstring.
   With two local models and one of them the composer, there is exactly one
   clean rater. That is below the standard the original rating met.

## Why `llama3.3:70b`

**Lineage, not size.** [`ollama_agent.py`](../metrics/noophorics/ollama_agent.py)
states the reason local open weights were adopted at all: they give *"the largest
prior gap available for L2 and L3 — different data, different training,
different tokenizer."* `gpt-oss:120b` and `qwen3.5:35b` are OpenAI-lineage and
Alibaba-lineage. A Meta model is a third training corpus and a third tokenizer,
which is the axis that matters for a prior gap and for rater independence.

Size was **not** the criterion, and a larger model would have been the wrong
instinct. The binding practical constraint this programme keeps hitting is
throughput: `gpt-oss` runs at 5.8 s/call and `qwen` at 72 s/call, and that
factor of twelve is why the qwen arms cost twenty-eight and twenty-two hours
while the gpt-oss arms cost one and a half. 70B at 42 GB sits between them on
128 GB of unified memory. A frontier-scale local model would have bought
capability this task does not need and cost days per arm.

**What would have been wrong:** picking the model most likely to be *weak* on
MERIDIAN in order to manufacture a crossover. The crossover has to be found, not
arranged, and the prediction below is recorded before the first draw for exactly
that reason.

## What it must clear before it counts

Sender accuracy on the source specification, the same gate every model here has
faced: a model that cannot recover the keys from the full text is not a subject,
it is a defect. `gpt-oss` scores 29/30 on `RIVERSIDE-30` and `qwen` 30/30; E-004
set the bar at 0.9.

If `llama3.3` fails that, it is not a third reader and this file records a
download rather than a measurement.

## Exposure

`llama3.3:70b` has read nothing in this repository. It is clean for every measure
here, including `MERIDIAN-IX32`, which `claude-opus-5` authored and is
[recorded as contaminated for](../EXPOSURE.md). The scripts load probe items; the
agent driving them does not print them, and this file does not quote any.

---

*This document is licensed CC BY 4.0.*
