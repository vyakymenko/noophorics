#!/usr/bin/env python3
"""Recompute the existing RIVERSIDE self-transfer result without model calls.

Uses only the standard library. Probe/brief content and individual answer labels
are read by the program but never emitted. Default: write the draft Markdown and
JSON. --check: verify both are current. --self-test: exercise synthetic defects.
This is a retrospective arithmetic audit, not a new experimental analysis plan.
"""

import argparse
from collections import Counter
import copy
import hashlib
import json
from math import comb, isclose
from pathlib import Path
import re
import statistics
import sys
import unittest


BASE = Path(__file__).resolve().parents[1]
SOURCE = Path("probes/riverside-30")
JSON_OUT = Path("research/selftransfer-audit.json")
MD_OUT = Path("research/2026-09-09-selftransfer-audit.md")
ARMS = (
    ("gptoss_self", "headroom.json", "briefs.json"),
    ("qwen_cross", "headroom-qwen.json", "briefs.json"),
    ("gptoss_cross", "cross-gptoss-on-qwenbriefs.json", "briefs-qwen.json"),
    ("qwen_self", "self-qwen-on-qwenbriefs.json", "briefs-qwen.json"),
)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest_bytes(data):
    return hashlib.sha256(data).hexdigest()


def digest_object(value):
    return digest_bytes(json.dumps(value, sort_keys=True, separators=(",", ":"))
                        .encode("utf-8"))


def qualified_measure(measure):
    """Mirror the documented semantic hash, independently of local imports."""
    probes = measure["probes"]
    weights = measure.get("weights")
    payload = {
        "probes": [[p["id"], p["prompt"], p["options"], p.get("key")]
                   for p in probes],
        "weights": list(weights) if weights is not None else [1.0] * len(probes),
        "holdout": sorted(set(measure.get("holdout") or [])),
    }
    encoded = json.dumps(payload, sort_keys=True, ensure_ascii=True).encode("utf-8")
    return "%s@%s" % (measure["id"], digest_bytes(encoded)[:12])


def draw_summary(raw, probes, draws, label):
    require(len(raw) == len(probes), label + ": wrong number of probes")
    modes, margins, ties = [], [], 0
    for row, probe in zip(raw, probes):
        require(len(row) == draws and draws > 0, label + ": wrong draw count")
        require(all(answer in probe["options"] for answer in row),
                label + ": answer outside declared option space")
        counts = Counter(row)
        # Original mode_of chooses the lexicographically first tied label.
        modes.append(max(sorted(counts), key=counts.get))
        ordered = sorted(counts.values(), reverse=True)
        margins.append(ordered[0] - (ordered[1] if len(ordered) > 1 else 0))
        ties += sum(n == ordered[0] for n in ordered) > 1
    return {"modes": modes, "margins": margins, "tied_probes": ties}


def audit_arm(arm, measure, briefs, label):
    probes = measure["probes"]
    ids = [p["id"] for p in probes]
    keys = [p.get("key") for p in probes]
    require(arm["probe_measure"] == qualified_measure(measure),
            label + ": measure hash differs from current probe content")
    require(arm["probe_ids"] == ids, label + ": probe order differs")
    require(arm["keys"] == keys, label + ": key vector differs")
    require(arm.get("composer", briefs["model"]) == briefs["model"],
            label + ": composer metadata differs")
    expected_briefs = [{"id": b["id"], "words": len(b["text"].split())}
                       for b in briefs["briefs"]]
    require(arm["briefs"] == expected_briefs, label + ": brief metadata differs")
    require(all(b["words"] == len(b["text"].split()) for b in briefs["briefs"]),
            label + ": current source brief word count differs")
    parties = arm["parties"]
    require(set(parties) == {"sender", *(b["id"] for b in expected_briefs)},
            label + ": unexpected/missing party")
    summaries = {}
    for party, data in parties.items():
        summary = draw_summary(data["raw"], probes, arm["draws"], label + "/" + party)
        require(summary["modes"] == data["modes"], label + ": stored modes differ")
        require(summary["margins"] == data["margins"], label + ": stored margins differ")
        summaries[party] = summary
    reference = summaries["sender"]["modes"]
    accuracy = sum(a == k for a, k in zip(reference, keys)) / len(probes)
    require(isclose(accuracy, arm["sender_accuracy"], abs_tol=1e-12),
            label + ": stored sender accuracy differs")
    counts = {}
    for brief in expected_briefs:
        party = brief["id"]
        data = parties[party]
        diverged = [pid for pid, a, b in zip(ids, reference, summaries[party]["modes"])
                    if a != b]
        require(data["diverged_probes"] == diverged, label + ": divergence list differs")
        require(data["diverged_count"] == len(diverged), label + ": divergence count differs")
        require(data["words"] == brief["words"], label + ": party word count differs")
        require(isclose(data["agreement_observed"], 1 - len(diverged) / len(probes),
                        abs_tol=1e-12), label + ": agreement differs")
        counts[party] = len(diverged)
    report = {
        "source": str(SOURCE / label),
        "reader": arm["model"],
        "composer": briefs["model"],
        "composer_explicit_in_arm": "composer" in arm,
        "timestamp_utc": arm["timestamp_utc"],
        "not_experimental_data": arm["not_experimental_data"],
        "draws_per_probe_per_party": arm["draws"],
        "reference_draws": len(probes) * arm["draws"],
        "receiver_draws": len(probes) * arm["draws"] * len(expected_briefs),
        "reference_kind": "reader's own full-specification sender condition",
        "reference_raw_sha256": digest_object(parties["sender"]["raw"]),
        "reference_modal_sha256": digest_object(reference),
        "diverged_counts": counts,
        "mean_diverged_count": statistics.mean(counts.values()),
        "tied_modal_probes": {p: s["tied_probes"] for p, s in summaries.items()},
        "word_counts": [b["words"] for b in expected_briefs],
        "stored_summaries_match_raw": True,
    }
    return report, reference


def sign_arithmetic(differences):
    """Reproduce the published binomial sign calculation; do not validate i.i.d."""
    positive = sum(d > 0 for d in differences)
    negative = sum(d < 0 for d in differences)
    n = positive + negative
    numerator = 2 * sum(comb(n, k) for k in range(min(positive, negative) + 1))
    denominator = 2 ** n
    return {"positive": positive, "negative": negative,
            "zero": len(differences) - n, "nonzero_n": n,
            "two_sided_p": min(1, numerator / denominator),
            "doubled_tail_numerator": numerator,
            "binomial_denominator": denominator,
            "assumption": "independent fair signs under the null, after excluding zeros",
            "scope": "reproduction of reported arithmetic; population validity not established"}


def number(text):
    return float(text.replace("−", "-"))


def check_published_arithmetic(result_text, rows, differences, sign):
    """Check source values as well as the newly generated report."""
    flat = result_text.replace("**", "").replace("`", "")
    for row, composer in zip(rows, ("gpt-oss", "qwen")):
        match = re.search(r"\| composed by " + re.escape(composer)
                          + r" \| ([\d.]+).*?\| ([\d.]+)", flat)
        require(match is not None, "published 2x2 table could not be parsed")
        expected = ((row["self_mean"], row["cross_mean"]) if composer == "gpt-oss"
                    else (row["cross_mean"], row["self_mean"]))
        require(all(isclose(number(v), round(e, 2), abs_tol=1e-12)
                    for v, e in zip(match.groups(), expected)),
                "published 2x2 means differ")
    match = re.search(r"All six: ([^\n]+), mean ([+−\d.]+), sd (\d+(?:\.\d+)?)", flat)
    require(match is not None, "published pooled descriptive summary could not be parsed")
    reported = [number(v.strip()) for v in match[1].split(",")]
    require(reported == differences, "published paired differences differ")
    require(isclose(number(match[2]), round(statistics.mean(differences), 3), abs_tol=1e-12),
            "published descriptive mean differs")
    require(isclose(number(match[3]), round(statistics.pstdev(differences), 2), abs_tol=1e-12),
            "published descriptive population SD differs")
    match = re.search(r"Sign test (\d+) positive,\s*(\d+) negative, (\d+) zero.*?p = (\d+(?:\.\d+)?)",
                      flat, re.S)
    require(match is not None, "published sign calculation could not be parsed")
    require([int(match[i]) for i in (1, 2, 3)]
            == [sign[k] for k in ("positive", "negative", "zero")],
            "published sign counts differ")
    require(isclose(number(match[4]), sign["two_sided_p"], abs_tol=1e-12),
            "published sign p differs")


def build_audit(root):
    source = root / SOURCE
    read = lambda name: json.loads((source / name).read_text(encoding="utf-8"))
    measure = read("probes.json")
    arms, references = {}, {}
    for arm_id, filename, brief_file in ARMS:
        arms[arm_id], references[arm_id] = audit_arm(read(filename), measure,
                                                   read(brief_file), filename)
    rows = []
    for self_id, cross_id in (("gptoss_self", "qwen_cross"), ("qwen_self", "gptoss_cross")):
        own, other = arms[self_id], arms[cross_id]
        require(own["draws_per_probe_per_party"] == other["draws_per_probe_per_party"],
                "asymmetric within-row sampling effort")
        require(own["word_counts"] == other["word_counts"], "within-row lengths differ")
        deltas = [own["diverged_counts"][b] - other["diverged_counts"][b]
                  for b in own["diverged_counts"]]
        rows.append({"composer": own["composer"], "self_arm": self_id, "cross_arm": cross_id,
                     "self_mean": own["mean_diverged_count"],
                     "cross_mean": other["mean_diverged_count"],
                     "self_minus_cross": deltas, "mean_difference": statistics.mean(deltas),
                     "absolute_row_mean_below_1_5": abs(statistics.mean(deltas)) < 1.5})
    differences = [d for row in rows for d in row["self_minus_cross"]]
    sign = sign_arithmetic(differences)
    results = (source / "RESULTS-selftransfer.md").read_text(encoding="utf-8")
    check_published_arithmetic(results, rows, differences, sign)
    prediction = (source / "PREDICTION-selftransfer.md").read_text(encoding="utf-8")
    require("the sign is not consistently in self's favour" in prediction
            and "both rows within 1.5, signs inconsistent" in prediction,
            "reviewed prediction wording changed; revisit interpretation before regenerating")
    require("what is established is the absence of the naive" in results,
            "reviewed absence claim changed; revisit interpretation before regenerating")
    source_paths = [SOURCE / name for name in (
        "probes.json", "briefs.json", "briefs-qwen.json", "PREDICTION-selftransfer.md",
        "RESULTS-selftransfer.md", "headroom_riverside.py", *(arm[1] for arm in ARMS))]
    source_paths += [Path("metrics/noophorics/probes.py"),
                     Path("metrics/noophorics/divergence.py")]
    reference_comparisons = []
    for a, b in (("gptoss_self", "gptoss_cross"), ("qwen_cross", "qwen_self"),
                 ("gptoss_self", "qwen_cross"), ("gptoss_cross", "qwen_self")):
        reference_comparisons.append({"arms": [a, b],
            "same_reader": arms[a]["reader"] == arms[b]["reader"],
            "raw_draws_identical": arms[a]["reference_raw_sha256"] == arms[b]["reference_raw_sha256"],
            "modal_reference_mismatches": sum(x != y for x, y in zip(references[a], references[b]))})
    return {
        "audit_date": "2026-09-09", "status": "draft for human review; no formal retraction",
        "analysis": "retrospective reconstruction of existing descriptive statistics",
        "measure": {"qualified_id": qualified_measure(measure), "probe_count": len(measure["probes"]),
                    "all_arms_match_current_semantic_hash": True},
        "source_sha256": {str(p): digest_bytes((root / p).read_bytes()) for p in source_paths},
        "current_brief_text_sha256": {name: {b["id"]: digest_bytes(b["text"].encode("utf-8"))
                                                    for b in read(name)["briefs"]}
                                       for name in ("briefs.json", "briefs-qwen.json")},
        "brief_provenance_limit": "arm JSON stores brief IDs and word counts, not consumed-text hashes",
        "arms": arms, "reference_comparisons": reference_comparisons, "rows": rows,
        "six_pairs_descriptive_only": {"differences": differences,
            "mean_difference": statistics.mean(differences),
            "population_sd": statistics.pstdev(differences),
            "sample_sd": statistics.stdev(differences),
            "absolute_per_brief_difference_at_least_1_5": sum(abs(d) >= 1.5 for d in differences)},
        "reported_sign_calculation": sign,
        "prediction_wording": {
            "both_absolute_row_means_below_1_5": all(r["absolute_row_mean_below_1_5"] for r in rows),
            "sign_not_consistently_in_self_favour": not all(r["mean_difference"] < 0 for r in rows),
            "row_signs_inconsistent": len({(r["mean_difference"] > 0) - (r["mean_difference"] < 0)
                                           for r in rows}) > 1,
            "equivalence_established": False,
        },
        "published_arithmetic_matches": True,
        "new_model_calls": 0,
    }


def check_reviewed_outcomes(a, ties):
    """Fail closed when fixed narrative would need another scientific review.

    This report reconstructs one saved result; it is not a general-purpose
    result interpreter. In particular, its suggested wording, binomial formula
    and identified exceptions must not silently survive changed outcomes.
    """
    rows = a["rows"]
    require(len(rows) == 2 and [r["composer"] for r in rows]
            == ["gpt-oss:120b", "qwen3.5:35b"],
            "composer rows changed; revisit narrative")
    for row, reviewed_mean in zip(rows, (1 / 3, 1.0)):
        require(len(row["self_minus_cross"]) == 3
                and isclose(row["mean_difference"], statistics.mean(row["self_minus_cross"]),
                            abs_tol=1e-12)
                and isclose(row["mean_difference"], reviewed_mean, abs_tol=1e-12)
                and row["absolute_row_mean_below_1_5"] is True
                and abs(row["mean_difference"]) < 1.5,
                "reviewed row mean/threshold changed; revisit narrative")
    require(a["prediction_wording"] == {
        "both_absolute_row_means_below_1_5": True,
        "sign_not_consistently_in_self_favour": True,
        "row_signs_inconsistent": False,
        "equivalence_established": False,
    }, "prediction sign/threshold interpretation changed; revisit narrative")
    differences = [d for row in rows for d in row["self_minus_cross"]]
    desc = a["six_pairs_descriptive_only"]
    exceedances = [(row["composer"], "b%d" % i, d)
                   for row in rows for i, d in enumerate(row["self_minus_cross"])
                   if abs(d) >= 1.5]
    require(desc["differences"] == differences
            and desc["absolute_per_brief_difference_at_least_1_5"] == 1
            and exceedances == [("qwen3.5:35b", "b2", 2)],
            "identified per-brief threshold exception changed; revisit narrative")
    sign = a["reported_sign_calculation"]
    require(sign == sign_arithmetic(differences)
            and [sign[k] for k in ("positive", "negative", "zero", "nonzero_n",
                                   "doubled_tail_numerator", "binomial_denominator")]
            == [4, 1, 1, 5, 12, 32],
            "reviewed binomial terms changed; revisit narrative")
    require(sorted(ties) == sorted([
        ("gptoss_self", "b2"), ("gptoss_cross", "b0"), ("qwen_self", "b2"),
    ]), "identified modal ties changed; revisit narrative")


def render_markdown(a):
    arms = a["arms"]
    require(set(arms) == {arm_id for arm_id, _, _ in ARMS}
            and a["measure"]["probe_count"] == 30
            and all(list(arm["diverged_counts"]) == ["b0", "b1", "b2"]
                    for arm in arms.values()),
            "report dimensions/brief order changed; revisit narrative")
    row0, row1 = a["rows"]
    desc = a["six_pairs_descriptive_only"]
    sign = a["reported_sign_calculation"]
    probe_n = a["measure"]["probe_count"]
    draws_n = arms["gptoss_self"]["draws_per_probe_per_party"]
    require(all(arm["draws_per_probe_per_party"] == draws_n for arm in arms.values()),
            "report expects equal sampling effort across all arms")
    references_n = sum(arm["reference_draws"] for arm in arms.values())
    answers_n = references_n + sum(arm["receiver_draws"] for arm in arms.values())
    ties = [(arm_id, party) for arm_id, arm in arms.items()
            for party, n in arm["tied_modal_probes"].items() for _ in range(n)
            if party != "sender"]
    check_reviewed_outcomes(a, ties)
    reference_ties = sum(arm["tied_modal_probes"]["sender"] for arm in arms.values())
    same_reader = [c for c in a["reference_comparisons"] if c["same_reader"]]
    other_reader = [c for c in a["reference_comparisons"] if not c["same_reader"]]
    require(len({arm["reference_raw_sha256"] for arm in arms.values()}) == len(arms)
            and all(c["modal_reference_mismatches"] == 0 for c in same_reader)
            and len({c["modal_reference_mismatches"] for c in other_reader}) == 1,
            "reference pattern changed; review narrative before regenerating")
    reference_difference = other_reader[0]["modal_reference_mismatches"]
    require(reference_ties == 0, "reference modal ties appeared; revisit narrative")
    require(all(arm["not_experimental_data"] is True for arm in arms.values()),
            "instrument-data label changed; revisit narrative")
    tie_labels = {"gptoss_self": "gpt-oss self", "qwen_cross": "qwen cross",
                  "gptoss_cross": "gpt-oss cross on qwen", "qwen_self": "qwen self"}
    tie_text = ", ".join(tie_labels[arm] + " " + party for arm, party in ties)
    gpt_words = "/".join(map(str, arms["gptoss_self"]["word_counts"]))
    qwen_words = "/".join(map(str, arms["qwen_self"]["word_counts"]))
    table = []
    for arm_id, _, _ in ARMS:
        arm = arms[arm_id]
        counts = arm["diverged_counts"]
        table.append("| %s | %s | %s | %s | %s | %.2f |" % (
            arm["composer"], arm["reader"], counts["b0"], counts["b1"], counts["b2"],
            arm["mean_diverged_count"]))
    return f"""# Draft audit: RIVERSIDE-30 self-transfer arithmetic and claim scope

**2026-09-09 — draft for human review.** This audit adds no experimental result,
changes no prediction, and makes no formal retraction. It reconstructs the
[existing result](../probes/riverside-30/RESULTS-selftransfer.md) from its saved
draws and reviews the wording against the
[existing prediction](../probes/riverside-30/PREDICTION-selftransfer.md).

The arithmetic reproduces. The statement that the absence of a self-transfer
advantage is established exceeds the evidence. Both observed row means favour
the cross reader, and both satisfy the descriptive 1.5-probe criterion; this
does not establish equivalence or absence beyond these observations.

## Mechanically reconstructed measurement

Measure: **`{a['measure']['qualified_id']}`**, with {a['measure']['probe_count']} probes.
All arm identifiers match a fresh semantic hash computed from the current
measure's IDs, prompts, options, keys, weights and holdout. The program reads
those fields without emitting their contents. All stored modes, modal margins,
divergence lists/counts, agreements, and sender accuracies match their raw draws.

The outcome is a count of unequal modal answers against **each reader's own
full-specification sender condition**. It is not `F*`, criterion accuracy, or a
measurement of understanding. Every party has **{draws_n} draws per probe**. Each arm
contains **{arms['gptoss_self']['reference_draws']} reference draws and {arms['gptoss_self']['receiver_draws']} receiver draws**; four arms therefore
contain **{answers_n:,} stored answers**, including **{references_n:,} reference answers**. All
four artifacts label themselves `not_experimental_data: true`; their existing
status is instrument data.

| Composer | Reader | b0 | b1 | b2 | Mean diverged of 30 |
|---|---|---:|---:|---:|---:|
{chr(10).join(table)}

For each composer, subtract the cross-reader count from the self-reader count.
A positive value means self has more modal divergence:

| Composer | b0 | b1 | b2 | Mean self − cross | Absolute mean < 1.5 |
|---|---:|---:|---:|---:|---|
| gpt-oss:120b | {row0['self_minus_cross'][0]:+d} | {row0['self_minus_cross'][1]:+d} | {row0['self_minus_cross'][2]:+d} | {row0['mean_difference']:+.3f} | Yes |
| qwen3.5:35b | {row1['self_minus_cross'][0]:+d} | {row1['self_minus_cross'][1]:+d} | {row1['self_minus_cross'][2]:+d} | {row1['mean_difference']:+.3f} | Yes |

The six paired differences are **{', '.join(f'{d:+d}' for d in desc['differences'])}**.
Their descriptive mean is **{desc['mean_difference']:+.6f}** probes. The source's
reported SD of {desc['population_sd']:.2f} is the **population SD** of these six observed numbers
({desc['population_sd']:.6f}, denominator {len(desc['differences'])}); the sample SD would be
{desc['sample_sd']:.6f} (denominator {len(desc['differences']) - 1}). Neither is an uncertainty interval.
**{desc['absolute_per_brief_difference_at_least_1_5']}** per-brief absolute difference
reaches or exceeds 1.5, the qwen-composed b2 pair at +2.

The reported sign calculation also reproduces: **{sign['positive']} positive,
{sign['negative']} negative, {sign['zero']} zero**. Excluding the zero leaves
{sign['nonzero_n']} signs; the two-sided fair-binomial arithmetic is
`2 × (C(5,0) + C(5,1)) / 2^5 = {sign['doubled_tail_numerator']}/{sign['binomial_denominator']} = {sign['two_sided_p']:.3f}`.
This is a reconstruction of the published calculation, not a new confirmatory
test or an endorsement of independence across the six pairs.

The lexicographically first label wins a modal tie, matching the runner.
There are **{len(ties)} receiver probe cells with tied modes**: {tie_text}.
No reference probe has a modal tie.
The result is consequently conditional on this declared deterministic rule.

## References and identity limits

Each arm has its own saved sender draws; none of the four sender raw arrays
are identical. Within each reader model, however, its sender modal vector is
identical across composers. Across the two reader models, the sender modal
vectors differ on **{reference_difference} of {probe_n} probes** in each composer row. Thus the reference
*kind* is matched, while the reference answer vector differs by reader. The
comparison is relative to the respective readers' references; it does not
compare both readers against one common criterion vector.

The present source briefs have **{gpt_words} words** for gpt-oss and
**{qwen_words}** for qwen. Their stored word counts match a fresh whitespace
count, and the two arms in each composer row have matching brief IDs/lengths
and equal sampling effort. The arm files omit consumed-text hashes, prompt
bytes, model digests, decoding settings and per-draw seed metadata. Current
brief-text hashes and whole-file SHA-256 values are in the
[machine audit](selftransfer-audit.json); these fingerprint present files and
do not independently prove which exact text or model version a past call used.
The first two arms omit an explicit composer field; their composer is taken
from the current `briefs.json` metadata and the documented design.

## Review issues, without changing the scientific record

**Absence is not established by the reported p-value.** The measured row means
show no observed self advantage. A non-significant sign test does not establish
the absence of a population effect; a large p-value alone is insufficient
evidence for a null hypothesis. This follows the
[ASA statement on p-values](https://doi.org/10.1080/00031305.2016.1154108).
The 1.5 threshold is an observed row-mean rule here. Neither the prediction nor
this audit supplies a registered equivalence test and uncertainty calculation
that would turn satisfying that rule into evidence of equivalence.
The prediction explicitly records that the gpt-oss-composed row was already
observed before it was written; only the qwen-composed arms were still to be
drawn. The six-pair sign test is not specified in that prediction document.
It should not be described as a fully prospective confirmatory test of all
four arms.

**The prediction has two different sign conditions.** Its main sentence says
the sign is not consistently in self's favour; both positive row means satisfy
that wording. Its first outcome-table row instead requires “signs inconsistent”;
both positive row means fail that stronger condition. The table also lists
“self clearly worse in both rows” without defining “clearly.” The correct audit
result is that the numerical threshold and the main sentence's weaker sign
condition are met, while the table's inconsistent-sign condition is not met.
This ambiguity should be acknowledged in human review, not resolved by
rewriting the prediction after the data.

**The design limits the inferential unit.** The six pairs use two composers,
two reader models, one probe set, and the same sender reference within each
arm's three brief comparisons. Each paired comparison deliberately reuses one
brief across readers. The record does not establish six independent draws
from a population of composers, readers, tasks, or references. The sign test's
usual independent-sign assumption therefore cannot be treated as verified
population evidence. The +0.667 value is retained solely as the published
descriptive average; it is not a between-composer comparison or a newly pooled
effect estimate. No confidence interval, bootstrap, causal model, or new
confirmatory test is added by this audit.

The causal claim that the probes carry the signal is outside this arithmetic
audit. Reproducing the self-transfer counts does not supply an independent
test of probe attribution. This audit also supplies no measurement of `Φ`
and does not measure a system before and after its own compaction.

**Suggested wording for review:** “On these saved draws, self has 0.33 and
1.00 more diverged probes than cross in the two composer rows. Both absolute
row means satisfy the predicted 1.5-probe threshold. The descriptive means
show no self advantage; they establish neither equivalence nor the absence
of a self-transfer advantage beyond this design.” This is a proposal, not an
applied correction.

## Reproduction and exposure

Run `python3 tools/audit_selftransfer.py` to regenerate this draft and its JSON.
Run `python3 tools/audit_selftransfer.py --check` to compare both generated
artifacts byte-for-byte with a new computation. Run
`python3 tools/audit_selftransfer.py --self-test` for synthetic red/green checks
of the audit. These commands make no model calls. Every quantitative statement
above is derived from, or explicitly checked against, the linked source files;
the source result's means, six differences, SD and sign arithmetic are checked
independently of its stored summaries.

The Codex audit agent read `AGENTS.md`, `CONTRIBUTING.md`, the self-transfer
prediction and result, and selected analysis/metadata excerpts from
`headroom_riverside.py`, `metrics/noophorics/probes.py` and
`metrics/noophorics/divergence.py`. The latter excerpts include methodological
comments, so this is exposure to the experimental hypotheses and measurement
design. Probe texts, key values, individual answer labels and brief text were
processed programmatically for hashing and reconstruction without entering the
agent's visible context. No source specification, adjudication, other probe
content, or full `theory/` file was read for this audit. The agent must be
excluded as a naive subject of this self-transfer experiment or its exposure
declared. The parent task records the session in the repository exposure log.

---

*Prose: CC BY 4.0. Audit code: Apache-2.0.*
"""


class AuditChecks(unittest.TestCase):
    @staticmethod
    def reviewed_outcomes():
        differences = [-1, 1, 1, 0, 1, 2]
        report = {
            "rows": [
                {"composer": "gpt-oss:120b", "self_minus_cross": differences[:3],
                 "mean_difference": 1 / 3, "absolute_row_mean_below_1_5": True},
                {"composer": "qwen3.5:35b", "self_minus_cross": differences[3:],
                 "mean_difference": 1.0, "absolute_row_mean_below_1_5": True},
            ],
            "prediction_wording": {
                "both_absolute_row_means_below_1_5": True,
                "sign_not_consistently_in_self_favour": True,
                "row_signs_inconsistent": False,
                "equivalence_established": False,
            },
            "six_pairs_descriptive_only": {
                "differences": differences,
                "absolute_per_brief_difference_at_least_1_5": 1,
            },
            "reported_sign_calculation": sign_arithmetic(differences),
        }
        return report, [("gptoss_self", "b2"), ("gptoss_cross", "b0"), ("qwen_self", "b2")]

    def test_reviewed_narrative_accepts_current_outcomes(self):
        report, ties = self.reviewed_outcomes()
        check_reviewed_outcomes(report, list(reversed(ties)))

    def test_reviewed_narrative_rejects_changed_outcomes(self):
        for defect in ("mean", "threshold", "weak_sign", "strong_sign", "binomial",
                       "exception_identity", "tie_identity"):
            report, ties = self.reviewed_outcomes()
            if defect == "mean":
                report["rows"][0].update(self_minus_cross=[2, 2, 2], mean_difference=2.0,
                                          absolute_row_mean_below_1_5=False)
                report["prediction_wording"]["both_absolute_row_means_below_1_5"] = False
            elif defect == "threshold":
                report["rows"][0]["absolute_row_mean_below_1_5"] = False
            elif defect == "weak_sign":
                report["prediction_wording"]["sign_not_consistently_in_self_favour"] = False
            elif defect == "strong_sign":
                report["prediction_wording"]["row_signs_inconsistent"] = True
            elif defect == "binomial":
                # Same row means and exceedance, different fair-binomial terms.
                report["rows"][0]["self_minus_cross"] = [0, 0, 1]
                differences = [0, 0, 1, 0, 1, 2]
                report["six_pairs_descriptive_only"]["differences"] = differences
                report["reported_sign_calculation"] = sign_arithmetic(differences)
            elif defect == "exception_identity":
                # Same means and sign counts, but the +2 moved to another brief.
                report["rows"][1]["self_minus_cross"] = [2, 1, 0]
                report["six_pairs_descriptive_only"]["differences"] = [-1, 1, 1, 2, 1, 0]
            else:
                ties[0] = ("gptoss_self", "b0")
            with self.subTest(defect=defect), self.assertRaises(ValueError):
                check_reviewed_outcomes(report, ties)

    def test_tie_rule_is_order_independent(self):
        probes = [{"options": ["X", "Y"]}]
        for raw in ([["Y", "X"]], [["X", "Y"]]):
            self.assertEqual(draw_summary(raw, probes, 2, "synthetic"),
                             {"modes": ["X"], "margins": [0], "tied_probes": 1})

    def test_empty_draw_and_invalid_answer_rejected(self):
        probes = [{"options": ["X", "Y"]}]
        for raw in ([[]], [["Z"]]):
            with self.assertRaises(ValueError):
                draw_summary(raw, probes, 1, "synthetic")

    def test_sign_calculation(self):
        self.assertEqual(sign_arithmetic([-1, 1, 1, 0, 1, 2])["two_sided_p"], 0.375)
        self.assertEqual(sign_arithmetic([0, 0])["two_sided_p"], 1)
        self.assertEqual(sign_arithmetic([-1, 1])["two_sided_p"], 1)

    def test_published_summary_and_corruptions(self):
        rows = [{"self_mean": 10, "cross_mean": 29 / 3},
                {"self_mean": 34 / 3, "cross_mean": 31 / 3}]
        deltas = [-1, 1, 1, 0, 1, 2]
        sign = sign_arithmetic(deltas)
        text = (
            "| **composed by `gpt-oss`** | **10.00** *(self)* | 9.67 *(cross)* |\n"
            "| **composed by `qwen`** | 10.33 *(cross)* | **11.33** *(self)* |\n"
            "All six: `−1, +1, +1, 0, +1, +2`, mean **+0.667**, sd 0.94. "
            "Sign test 4 positive,\n1 negative, 1 zero — **two-sided `p = 0.375`**.\n")
        check_published_arithmetic(text, rows, deltas, sign)
        for before, after in (("9.67", "9.00"), ("+2`", "+3`"),
                              ("0.94.", "1.03."), ("4 positive", "3 positive"),
                              ("0.375", "0.500")):
            with self.subTest(defect=before), self.assertRaises(ValueError):
                check_published_arithmetic(text.replace(before, after), rows, deltas, sign)

    def test_semantic_hash_changes_only_for_watched_content(self):
        measure = {"id": "synthetic", "probes": [{"id": "p", "prompt": "synthetic",
                    "options": ["X", "Y"], "key": "X"}]}
        changed = copy.deepcopy(measure)
        changed["description"] = "cosmetic"
        self.assertEqual(qualified_measure(measure), qualified_measure(changed))
        changed["probes"][0]["prompt"] = "changed synthetic"
        self.assertNotEqual(qualified_measure(measure), qualified_measure(changed))

    def test_stale_summary_and_reference_are_rejected(self):
        measure = {"id": "synthetic", "probes": [{"id": "p", "prompt": "synthetic",
                    "options": ["X", "Y"], "key": "X"}]}
        briefs = {"model": "synthetic-model", "briefs": [{"id": "b0", "words": 1, "text": "synthetic"}]}
        arm = {"model": "synthetic-model", "draws": 2, "timestamp_utc": "synthetic",
            "not_experimental_data": True, "probe_measure": qualified_measure(measure),
            "probe_ids": ["p"], "keys": ["X"], "briefs": [{"id": "b0", "words": 1}],
            "sender_accuracy": 1.0, "parties": {
                "sender": {"raw": [["X", "X"]], "modes": ["X"], "margins": [2]},
                "b0": {"raw": [["Y", "X"]], "modes": ["X"], "margins": [0],
                       "diverged_probes": [], "diverged_count": 0,
                       "agreement_observed": 1.0, "words": 1}}}
        self.assertEqual(audit_arm(arm, measure, briefs, "synthetic")[0]["diverged_counts"], {"b0": 0})
        for defect in ("count", "mode", "hash", "reference"):
            changed = copy.deepcopy(arm)
            if defect == "count": changed["parties"]["b0"]["diverged_count"] = 1
            elif defect == "mode": changed["parties"]["b0"]["modes"] = ["Y"]
            elif defect == "hash": changed["probe_measure"] = "synthetic@bad"
            else: changed["parties"]["sender"]["raw"] = [["Y", "Y"]]
            with self.subTest(defect=defect), self.assertRaises(ValueError):
                audit_arm(changed, measure, briefs, "synthetic")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(AuditChecks))
        return 0 if result.wasSuccessful() else 1
    try:
        audit = build_audit(BASE)
        outputs = {JSON_OUT: json.dumps(audit, indent=2, ensure_ascii=False) + "\n",
                   MD_OUT: render_markdown(audit)}
        if args.check:
            for path, content in outputs.items():
                require((BASE / path).exists() and (BASE / path).read_text(encoding="utf-8") == content,
                        str(path) + ": absent or stale; regenerate with tools/audit_selftransfer.py")
            print("self-transfer audit current; raw-derived and published arithmetic agree")
        else:
            for path, content in outputs.items():
                (BASE / path).parent.mkdir(parents=True, exist_ok=True)
                (BASE / path).write_text(content, encoding="utf-8")
                print("wrote " + str(path))
        return 0
    except (ValueError, KeyError, OSError, TypeError) as error:
        print("self-transfer audit FAILED: " + str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
