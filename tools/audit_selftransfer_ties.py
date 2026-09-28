#!/usr/bin/env python3
"""Enumerate modal-tie sensitivity in the saved RIVERSIDE self-transfer draws.

No model is called. Probe text, keys, and individual answer labels are read by
the existing arithmetic audit, but this tool emits none of them. It checks the
published deterministic result before considering alternative tied modes.
"""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import product
import json
from pathlib import Path

import audit_selftransfer as base


ROOT = Path(__file__).resolve().parents[1]
JSON_OUT = Path("research/selftransfer-tie-sensitivity.json")
MD_OUT = Path("research/2026-09-28-selftransfer-tie-sensitivity.md")
ROW_PAIRS = (("gptoss_self", "qwen_cross"), ("qwen_self", "gptoss_cross"))
BRIEFS = ("b0", "b1", "b2")
LIMIT = Fraction(3, 2)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def tied_modes(draws, recorded_mode):
    """Return co-modes in the original lexicographic order, without emitting labels."""
    require(bool(draws), "empty draw cell")
    counts = Counter(draws)
    highest = max(counts.values())
    choices = sorted(answer for answer, count in counts.items() if count == highest)
    require(recorded_mode == choices[0], "stored mode differs from raw draws")
    return choices


def analyze_raw_arms(raw_arms, row_pairs=ROW_PAIRS, briefs=BRIEFS):
    """Enumerate every co-mode choice; return only counts and choice indices."""
    fixed = {}
    ties = []
    probe_count = None
    for arm_id, arm in raw_arms.items():
        parties = arm["parties"]
        require(set(parties) == {"sender", *briefs}, "missing or extra party")
        reference_raw = parties["sender"]["raw"]
        reference_modes = parties["sender"]["modes"]
        require(len(reference_raw) == len(reference_modes) > 0,
                "reference count differs")
        if probe_count is None:
            probe_count = len(reference_raw)
        require(len(reference_raw) == probe_count, "arm probe count differs")
        for draws, recorded in zip(reference_raw, reference_modes):
            require(len(tied_modes(draws, recorded)) == 1,
                    "reference has a modal tie; fixed reference unavailable")
        fixed[arm_id] = {}
        for brief in briefs:
            receiver = parties[brief]
            require(len(receiver["raw"]) == len(receiver["modes"]) == probe_count,
                    "receiver probe count differs")
            fixed[arm_id][brief] = 0
            for index, (draws, recorded) in enumerate(
                    zip(receiver["raw"], receiver["modes"])):
                choices = tied_modes(draws, recorded)
                if len(choices) == 1:
                    fixed[arm_id][brief] += int(choices[0] != reference_modes[index])
                else:
                    ties.append({
                        "arm": arm_id, "brief": brief,
                        "probe_index_zero_based": index,
                        "co_mode_count": len(choices),
                        "choice_divergences": [int(choice != reference_modes[index])
                                               for choice in choices],
                        "reference_among_co_modes": reference_modes[index] in choices,
                        "published_choice_index": 0,
                    })
    require(all(a in fixed and b in fixed for a, b in row_pairs),
            "row arm missing")
    combination_count = 1
    for tie in ties:
        combination_count *= tie["co_mode_count"]
    require(combination_count <= 100000,
            "too many modal configurations for exhaustive enumeration")
    configurations = []
    for choice_indices in product(*(range(tie["co_mode_count"]) for tie in ties)):
        counts = {arm: dict(brief_counts) for arm, brief_counts in fixed.items()}
        for tie, choice_index in zip(ties, choice_indices):
            counts[tie["arm"]][tie["brief"]] += tie["choice_divergences"][choice_index]
        row_differences = [
            [counts[own][brief] - counts[cross][brief] for brief in briefs]
            for own, cross in row_pairs
        ]
        row_means = [Fraction(sum(row), len(briefs)) for row in row_differences]
        configurations.append({
            "tie_choice_indices": list(choice_indices),
            "row_differences": row_differences,
            "row_mean_numerators_over_three": [sum(row) for row in row_differences],
            "both_absolute_means_below_1_5": all(abs(mean) < LIMIT
                                                 for mean in row_means),
        })
    return {"probe_count": probe_count, "sender_probe_cells": len(raw_arms) * probe_count,
            "receiver_probe_cells": len(raw_arms) * len(briefs) * probe_count,
            "tie_count": len(ties), "ties": ties,
            "modal_configuration_count": len(configurations),
            "configurations": configurations}


def fraction_text(value):
    return str(value.numerator) if value.denominator == 1 else str(value)


def summarize(a, enumeration):
    configurations = enumeration["configurations"]
    published = next((c for c in configurations
                      if all(index == 0 for index in c["tie_choice_indices"])), None)
    require(published is not None, "published modal configuration missing")
    require(published["row_differences"] ==
            [row["self_minus_cross"] for row in a["rows"]],
            "published tie choices do not reproduce audited row differences")
    rows = []
    for i, original in enumerate(a["rows"]):
        all_differences = [c["row_differences"][i] for c in configurations]
        all_means = [Fraction(sum(diff), len(diff)) for diff in all_differences]
        rows.append({
            "composer": original["composer"],
            "published_differences": original["self_minus_cross"],
            "published_mean_fraction": fraction_text(Fraction(
                sum(original["self_minus_cross"]), len(BRIEFS))),
            "possible_differences_by_brief": [sorted({diff[j] for diff in all_differences})
                                              for j in range(len(BRIEFS))],
            "possible_mean_fractions": sorted({fraction_text(mean) for mean in all_means},
                                               key=lambda x: Fraction(x)),
            "minimum_mean_fraction": fraction_text(min(all_means)),
            "maximum_mean_fraction": fraction_text(max(all_means)),
            "strictly_positive_in_every_configuration": all(mean > 0
                                                              for mean in all_means),
            "negative_in_any_configuration": any(mean < 0 for mean in all_means),
            "absolute_mean_below_1_5_in_every_configuration": all(abs(mean) < LIMIT
                                                                   for mean in all_means),
        })
    return {
        "date": "2026-09-28",
        "status": "retrospective sensitivity draft for human review; no new experiment or formal correction",
        "analysis": "exhaustive choices among raw-draw modal ties with sender modes fixed",
        "measure": a["measure"]["qualified_id"],
        "source_sha256": a["source_sha256"],
        "raw_draws_and_published_arithmetic_checked": a["published_arithmetic_matches"],
        "published_tie_rule": "lexicographically first co-mode",
        **enumeration,
        "rows": rows,
        "both_absolute_row_means_below_1_5_in_every_configuration": all(
            c["both_absolute_means_below_1_5"] for c in configurations),
        "new_model_calls": 0,
    }


def render_markdown(report):
    """Fixed interpretation is deliberately guarded against changed source data."""
    require(report["measure"] == "RIVERSIDE-30@2e6afe2f3c92"
            and report["probe_count"] == 30
            and report["sender_probe_cells"] == 120
            and report["receiver_probe_cells"] == 360
            and report["tie_count"] == 3
            and report["modal_configuration_count"] == 8,
            "reviewed measure/tie dimensions changed; review prose")
    expected_ties = [
        ("gptoss_self", "b2", 23),
        ("gptoss_cross", "b0", 29),
        ("qwen_self", "b2", 21),
    ]
    require([(t["arm"], t["brief"], t["probe_index_zero_based"])
             for t in report["ties"]] == expected_ties
            and all(t["co_mode_count"] == 2 and t["reference_among_co_modes"]
                    and t["choice_divergences"][0] == 1
                    and sorted(t["choice_divergences"]) == [0, 1]
                    for t in report["ties"]),
            "reviewed tie identities or effects changed; review prose")
    gpt, qwen = report["rows"]
    require((gpt["composer"], gpt["published_differences"],
             gpt["minimum_mean_fraction"], gpt["maximum_mean_fraction"]) ==
            ("gpt-oss:120b", [-1, 1, 1], "0", "1/3")
            and (qwen["composer"], qwen["published_differences"],
                 qwen["minimum_mean_fraction"], qwen["maximum_mean_fraction"]) ==
            ("qwen3.5:35b", [0, 1, 2], "2/3", "4/3")
            and not gpt["strictly_positive_in_every_configuration"]
            and qwen["strictly_positive_in_every_configuration"]
            and not any(row["negative_in_any_configuration"] for row in report["rows"])
            and report["both_absolute_row_means_below_1_5_in_every_configuration"],
            "reviewed row ranges or threshold result changed; review prose")
    return f"""# Draft sensitivity audit: modal ties in RIVERSIDE-30 self-transfer

**2026-09-28 — retrospective check for human review.** This note analyzes the
saved draws behind the [self-transfer result](../probes/riverside-30/RESULTS-selftransfer.md)
and its [arithmetic audit](2026-09-09-selftransfer-audit.md). It adds no model
responses, changes no registered prediction, and makes no formal correction.
The four saved arms are labelled instrument data in their source files.

The published runner chooses the lexicographically first answer when modal
counts tie. That rule is deterministic and remains the published calculation.
Across **{report['receiver_probe_cells']} receiver probe cells**, three have a
two-way modal tie; none of the **{report['sender_probe_cells']} sender probe cells**
has one. The sender modal reference therefore stays fixed. For each of
the three receiver ties, one co-mode matches that reference and the published
choice does not. The tied answer labels and probe content are not reproduced
here.

Choosing either co-mode in each tied cell yields exactly
**{report['modal_configuration_count']} modal configurations**. These are
alternative scoring resolutions of the **same saved draws**, not repeated
samples or equally likely outcomes.

| Composer row | Published self − cross differences (b0, b1, b2) | Published row mean | Possible row mean with any tied co-mode |
|---|---|---:|---:|
| `gpt-oss:120b` | {', '.join(str(v) if v == 0 else f'{v:+d}' for v in gpt['published_differences'])} | {gpt['published_mean_fraction']} | {gpt['minimum_mean_fraction']} to {gpt['maximum_mean_fraction']} |
| `qwen3.5:35b` | {', '.join(str(v) if v == 0 else f'{v:+d}' for v in qwen['published_differences'])} | {qwen['published_mean_fraction']} | {qwen['minimum_mean_fraction']} to {qwen['maximum_mean_fraction']} |

One tied `gpt-oss` self-reader cell can lower its b2 difference from +1 to 0,
making that row mean **0** instead of **+1/3**. In the qwen-composed row, a
tied cross-reader b0 cell can raise the difference from 0 to +1, while a tied
self-reader b2 cell can lower it from +2 to +1. That row mean ranges from
**+2/3 to +4/3**. No admissible tie choice produces a negative row mean.

**Every configuration keeps both absolute row means below the published
1.5-probe descriptive threshold.** The strictly positive sign of the
`gpt-oss`-composed row is sensitive to the tie rule; under another admissible
choice it becomes zero. The qwen-composed row remains positive. This check
does not establish equivalence, absence of a self-transfer effect, a cause for
the differences, or any population result. There is no new significance test.

The [machine summary](selftransfer-tie-sensitivity.json) lists all eight
configurations as co-mode **indices and divergence counts**, without answer
labels. It records source hashes and the exact threshold outcome for each
configuration. The tool first runs the existing raw-draw arithmetic audit and
requires its published modal result to reproduce before enumerating alternatives.

Recompute from the repository root without model calls:

```bash
python3 tools/audit_selftransfer_ties.py --check
python3 tools/test_audit_selftransfer_ties.py
```

**Exposure:** this Codex audit read the research index, register instrument
plan/readout, self-transfer audit, domain drafts and analysis code, including
selected prediction wording. The original prediction, result, measure, briefs
and raw answer arrays were also processed programmatically; probe text, keys,
individual answers and brief text were not printed into the agent context.
This working context should not be treated as a naive experimental subject.
The session belongs in [EXPOSURE.md](../EXPOSURE.md).

---

*Prose: CC BY 4.0. Audit code: Apache-2.0.*
"""


def build(root=ROOT):
    audit = base.build_audit(root)
    # The existing auditor has guarded prose for this exact result. This call
    # checks its reviewed outcome identities without writing the old report.
    base.render_markdown(audit)
    raw = {arm_id: json.loads((root / base.SOURCE / filename).read_text(encoding="utf-8"))
           for arm_id, filename, _ in base.ARMS}
    return summarize(audit, analyze_raw_arms(raw))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="verify saved report and JSON against raw draws")
    args = parser.parse_args()
    report = build()
    markdown = render_markdown(report)
    machine = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        require((ROOT / MD_OUT).read_text(encoding="utf-8") == markdown,
                "saved tie-sensitivity note differs from raw-derived report")
        require((ROOT / JSON_OUT).read_text(encoding="utf-8") == machine,
                "saved tie-sensitivity JSON differs from raw-derived report")
        print("self-transfer tie sensitivity current; all modal choices enumerated")
    else:
        (ROOT / MD_OUT).write_text(markdown, encoding="utf-8")
        (ROOT / JSON_OUT).write_text(machine, encoding="utf-8")
        print("wrote tie-sensitivity note and machine summary")


if __name__ == "__main__":
    main()
