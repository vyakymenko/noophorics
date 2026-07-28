# Probe measures

A **probe measure** is the noophoric frame of reference. Per axiom
[A2](../PRINCIPIA.md#4-the-four-axioms), no quantity in this field is defined
without one: a fidelity number reported without its `P` is as meaningless as a
velocity reported without a frame.

This directory holds reusable probe measures. Experiment-specific ones live
next to their experiment.

---

## Format

```json
{
  "id": "KESTREL-34",
  "domain": "fictional-eligibility-rules",
  "description": "What this measure probes, and what it deliberately does not.",
  "weights": [1.0, 1.0],
  "probes": [
    {
      "id": "K01",
      "prompt": "A decidable case. What is the verdict?",
      "options": ["ELIGIBLE", "INELIGIBLE", "ADJUSTED"],
      "key": "ELIGIBLE",
      "tags": ["R1", "boundary"]
    }
  ]
}
```

| Field | Required | Notes |
|---|---|---|
| `id` | yes | Short, stable. Reported as `id@content_hash`. |
| `domain` | no | Free-text domain label. |
| `description` | no | Say what the measure covers **and what it excludes**. |
| `weights` | no | Probe measure density. Uniform if omitted. |
| `probes[].id` | yes | Unique within the measure. |
| `probes[].prompt` | yes | The case. Self-contained. |
| `probes[].options` | yes | **Finite, discrete, ≥2.** |
| `probes[].key` | no | Ground truth, where one exists. |
| `probes[].tags` | no | Which rules or interactions the probe discriminates. |

---

## Rules

**Probes must be decidable.** Finite, discrete answer space. This is a
methodological commitment, not a convenience: no divergence measure over free
text is stable under paraphrase. Free-form probes must be resolved into a
discrete space by a *stated* rubric before they enter a measurement. If you
cannot say what the possible answers are, you do not have a probe.

**Probes must discriminate.** A probe every agent answers identically
regardless of the transfer contributes nothing to the numerator and dilutes the
measure. Prefer boundary cases, rule interactions, overrides, and scope limits
— the places a reasonable receiver goes wrong.

**`key` is not a noophoric quantity.** Fidelity measures sender↔receiver
convergence, not correctness. The key exists so an experiment can report
*sender accuracy* as a gate: a sender that misunderstood the source material
makes the whole transfer measurement uninterpretable, and you want to find that
out before you interpret anything.

**Admissibility is checked at runtime.** A measure is admissible for a transfer
only if the parties actually disagree on it beforehand, by more than the noise
floor. Measuring fidelity where agreement already exists produces flattering
numbers from nothing.

---

## Content hash

`ProbeMeasure.content_hash` digests the probes' semantic content — id, prompt,
options, key — and nothing else. Editing a description does not change the
frame identity; editing a prompt does.

Always report the qualified id (`KESTREL-34@cadcf2faaf74`). A measure that
silently changed between two runs is the single easiest way to produce an
irreproducible result while believing you reproduced one.

---

## Loading

```python
from noophorics import load_probe_measure

measure = load_probe_measure("experiments/E-001-fluency-cost/probes.json")
print(measure.qualified_id)   # KESTREL-34@cadcf2faaf74
```

---

## Available measures

| Measure | Probes | Domain | Used by |
|---|---:|---|---|
| [`KESTREL-34`](../experiments/E-001-fluency-cost/probes.json) | 34 | Fictional eligibility rules | [E-001](../experiments/E-001-fluency-cost/) |

Fictional domains are preferred for transfer experiments: they guarantee the
receiver's baseline is a genuine zero-information prior rather than a recall of
training data.
