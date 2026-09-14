#!/usr/bin/env python3
"""Render the fixed register instrument's checked evidence as offline Markdown.

Raw responses are parsed only by rate_register; no passage or reasoning text is
copied into this readout. --check compares bytes without modifying the report.
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
from pathlib import Path
import sys
from urllib.parse import quote

import rate_register as rr


PLAN = rr.ROOT / "probes/qwen-register/plan.json"
DEFAULT_REPORT = rr.ROOT / "research/2026-09-14-register-feasibility.md"
PLAN_COMMIT = "544e6fe"
RUNNER_COMMIT = "d0de1a3"
PLAN_SHA = "8709fb5c79ed1c7d306ef15dac4a42d2e860fdd34359fd0f8126922d5cdb4f6c"
RUNNER_SHA = "32a5120cb6c410fff2f0c9737fc71c353fd2348b4240d5722dabd954900757fe"


def link(label, path, report):
    relative = os.path.relpath(Path(path).resolve(), Path(report).resolve().parent)
    return f"[{label}]({quote(Path(relative).as_posix(), safe='/.-_')})"


def render(out, report):
    """Validate raw evidence and recompute every reported observation."""
    out, report = Path(out).resolve(), Path(report).resolve()
    protocol = rr.load_protocol(PLAN)
    rr.require(protocol["identity"]["plan_sha256"] == PLAN_SHA,
               "report is bound to plan commit " + PLAN_COMMIT)
    rr.require(protocol["identity"]["script_sha256"] == RUNNER_SHA,
               "report is bound to runner commit " + RUNNER_COMMIT)
    records = rr.checked_results(protocol, out)
    summary = rr.summarize(protocol, records)
    manifest = rr.read_json(out / "manifest.json")
    started = dt.datetime.fromisoformat(manifest["started_at"])
    rr.require(started.tzinfo is not None, "manifest start time must include its timezone")
    date = started.astimezone(dt.timezone.utc).date().isoformat()
    names = [r["model"] for r in protocol["plan"]["raters"]]
    calibration = summary["calibration"]
    cells = summary["cells"]
    total = sum(c["total"] for c in cells.values())
    missing = sum(c["missing_any_rating"] for c in cells.values())
    all_calibrated = all(calibration[n]["status"] == "passed" for n in names)
    status = "Collection complete" if summary["complete"] else "Partial collection — unfinished snapshot"
    usable = "available" if summary["usable"] else "unavailable"
    lines = [
        "# Qwen register feasibility: instrument readout",
        "",
        f"**{date} (UTC start date). {status}.**",
        "",
        f"The complete two-judge corpus result is **{usable}**. "
        f"Recorded HTTP rating attempts: **{summary['attempted_calls']} / {summary['max_calls']}** "
        f"(fixed cap); invalid or indeterminate attempted responses: "
        f"**{summary['invalid_or_indeterminate_attempts']}**. "
        f"Corpus messages missing at least one valid rating: **{missing} / {total}**.",
        "",
        (f"Direct joint acceptance across the archived corpus: **{sum(c['joint_acceptance'] for c in cells.values())} / {total}**. "
         f"The judges disagreed on **{sum(c['disagreement'] for c in cells.values())} / {total}** messages."
         if all(c["joint_result_available"] for c in cells.values()) else
         "The complete corpus acceptance count is unavailable while any cell lacks a valid joint result."),
        "",
        "These are descriptive counts for this finite archived corpus and these configured judges. "
        "This readout introduces no scientific hypothesis, law, significance test, or population acceptance estimate.",
        "",
        "## Calibration",
        "",
        "| Judge | Status | Controls attempted / planned | Valid responses | Correct controls |",
        "|---|---|---:|---:|---:|",
    ]
    for name in names:
        c = calibration[name]
        lines.append(f"| `{name}` | {c['status']} | {c['attempted']} / {c['planned']} | {c['valid']} | {c['correct']} |")
    lines.extend([
        "",
        "Every control must be correct before that judge's corpus calls are eligible. "
        "A failed or missing control excludes its corpus ratings; it does not authorize a replacement judge or retry. "
        "These procedural controls are not a validated benchmark, and passing them does not establish correctness on borderline passages.",
        "",
        "## Corpus counts",
        "",
        f"| Cell | Expected register | Messages | In word band | `{names[0]}` expected | `{names[1]}` expected | Both expected | Disagreements | Direct joint acceptance |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ])
    for cell, c in cells.items():
        expected = "connected prose" if c["expected_verdict"] == "A" else "list"
        counts = [c["expected_register_by_rater"][n] if calibration[n]["status"] == "passed"
                  else "unavailable" for n in names]
        both = c["both_expected_register"] if all_calibrated else "unavailable"
        disagreement = c["disagreement"] if all_calibrated else "unavailable"
        joint = c["joint_acceptance"] if c["joint_result_available"] else "unavailable"
        lines.append(f"| {cell} | {expected} | {c['total']} | {c['in_band']} | {counts[0]} | {counts[1]} | {both} | {disagreement} | {joint} |")
    low, high = protocol["plan"]["source"]["band"]
    lines.extend([
        "",
        f"The word band is {low}–{high} whitespace-separated words. Direct joint acceptance "
        "counts the same messages passing the band and both judges' expected register; it is the observed intersection, "
        "not a product or minimum of marginal counts. Expected-register counts use valid observed ratings. "
        "Both-expected and disagreement counts use only messages with two valid ratings. "
        "A complete joint count is unavailable for a cell with any missing rating, or if either judge fails calibration.",
        "",
        "### Missing data",
        "",
        f"| Cell | `{names[0]}` valid | `{names[0]}` missing | `{names[1]}` valid | `{names[1]}` missing | Two valid | Any missing |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ])
    for cell, c in cells.items():
        valid = [c["valid_ratings"][n] for n in names]
        lines.append(f"| {cell} | {valid[0]} | {c['total'] - valid[0]} | {valid[1]} | {c['total'] - valid[1]} | {c['both_valid']} | {c['missing_any_rating']} |")
    lower_bounds = [(cell, c["observed_joint_acceptance"]) for cell, c in cells.items()
                    if not c["joint_result_available"] and c["observed_joint_acceptance"] is not None]
    lines.append("")
    if lower_bounds:
        lines.append("For cells whose complete joint counts are unavailable, the observed joint acceptances are "
                     + "; ".join(f"{cell}: {value}" for cell, value in lower_bounds)
                     + ". Each is only a lower bound on its complete joint count; missing ratings have not been counted as rejections.")
        lines.append("")
    lines.extend([
        "Missing includes unattempted, skipped, invalid, and indeterminate corpus ratings. "
        "An invalid response never becomes a list verdict. A reserved call interrupted before a definitive response stays missing and is never resent.",
        "",
        "## Scope and provenance",
        "",
        f"All {total} archived compositions were fixed before the register outcomes were collected; "
        "their length outcomes already existed. Every composition is included, including those outside the word band. "
        "There is one draw per eligible message and judge, with no retries or replacement compositions.",
        "",
        "The configured regimes differ: `gpt-oss:120b` uses `think=medium`; `llama3.3:70b` omits the thinking field. "
        "Both use temperature 0.7. These are observations from these particular judges, not a controlled comparison of model ability. "
        "Different model lineages do not establish independent errors. The historical `qwen3.5:35b` composer digest is unknown.",
        "",
        "Register acceptance does not test factual accuracy, contrastiveness, transfer, fidelity, phantom agreement, or usefulness. "
        "E-001c remains void, and its pre-registration is unchanged. Scientific interpretation requires human review; this file is a mechanical instrument readout.",
        "",
        f"Collection started: `{manifest['started_at']}`. Plan committed before ratings: `{PLAN_COMMIT}`. "
        f"Frozen runner commit: `{RUNNER_COMMIT}`.",
        "",
        "| Pinned input | SHA-256 |",
        "|---|---|",
        f"| Archived source JSON | `{protocol['identity']['source_sha256']}` |",
        f"| Plan JSON | `{protocol['identity']['plan_sha256']}` |",
        f"| Runner | `{protocol['identity']['script_sha256']}` |",
        f"| Absolute question | `{protocol['identity']['prompt_sha256']}` |",
    ])
    for name in names:
        lines.append(f"| `{name}` weights | `{protocol['identity']['model_digests'][name]}` |")
    lines.extend([
        "",
        "Sources: " + ", ".join([
            link("prospective plan", PLAN.with_name("PLAN.md"), report),
            link("machine-readable plan", PLAN, report),
            link("archived source", rr.ROOT / protocol["plan"]["source"]["path"], report),
            link("result manifest and item identities", out / "manifest.json", report),
            link("saved summary", out / "summary.json", report),
            link("raw call records", out / "calls", report),
        ]) + ".",
        "",
        "Every count above is recomputed from checked raw call records, not copied from the saved summary. "
        "The manifest binds item identities and text hashes; the runner checks them alongside the source, question, plan, model, and runner identities.",
        "",
        "Recompute from the saved raw records, starting at the repository root:",
        "",
        "```bash",
        f"python3 tools/rate_register.py --out {shell_path(out)} --summarize",
        f"python3 tools/report_register.py --out {shell_path(out)} --report {shell_path(report)} --check",
        "```",
        "",
        "---",
        "",
        "*This document is licensed CC BY 4.0.*",
        "",
    ])
    return "\n".join(lines)


def shell_path(path):
    """Quote a repository-relative path for the displayed reproduction command."""
    import shlex
    return shlex.quote(os.path.relpath(Path(path).resolve(), rr.ROOT))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True, help="result directory to validate")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--check", action="store_true", help="compare Markdown without writing")
    args = parser.parse_args(argv)
    try:
        content = render(args.out, args.report)
        if args.check:
            rr.require(args.report.exists() and args.report.read_bytes() == content.encode("utf-8"),
                       "report missing or stale; regenerate it from the checked records")
            print(f"current: {args.report.resolve()}")
        else:
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(content, encoding="utf-8")
            print(f"wrote: {args.report.resolve()}")
        return 0
    except (rr.CheckError, KeyError, TypeError, ValueError, OSError) as error:
        print(f"report_register: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
