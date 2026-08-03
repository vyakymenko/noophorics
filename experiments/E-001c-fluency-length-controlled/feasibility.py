#!/usr/bin/env python3
"""Can the four E-001b styles be produced at a common length at all?

E-001b was voided by its cost parity gate (../E-001b-fluency-factorial/VOID.md).
Its budget instruction was a CEILING -- "stay within 350 tokens" -- which is a
one-sided constraint used to enforce a two-sided requirement. It cannot produce
parity even when obeyed, and it was not obeyed: every cell exceeded it, the
fluent cells by 76%.

Worse, the realised costs of the two style families were DISJOINT: fluent
[559, 716] tokens, terse [365, 441], with 118 tokens of clear air between them.
So the repair first proposed in VOID.md -- rejection sampling into a shared
band -- has acceptance zero for every possible band. It is not expensive, it is
impossible.

That leaves one question, and E-001c does not exist until it is answered:

    Under a TWO-SIDED word target, do the four cells converge in realised cost,
    and does the style manipulation survive being pinned?

Both halves matter. Convergence without surviving styles is a null experiment
with extra steps: if "fluent" at 220 words is indistinguishable from "terse" at
220 words, there is no manipulation left to test L5 or L6 against.

This is instrument work and reports no hypothesis. It is the analogue of
E-001b's PARAMETERS.md: a measurement made before registration, so the
registration can be written knowing whether its design is buildable.

    python3 feasibility.py --targets 200,300 --k 3
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
import time
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "metrics"))
sys.path.insert(0, os.path.join(REPO, "experiments", "E-001b-fluency-factorial"))

from noophorics.ollama_agent import OllamaAgent, ollama_available  # noqa: E402
from prompts import CELLS, CELL_AXES, _OUTPUT  # noqa: E402

PARITY_THRESHOLD = 1.30
TOLERANCE = 0.10  # +/- of the word target that counts as compliance


def two_sided_output(low: int, high: int) -> str:
    """Replace the ceiling with a band, changing nothing else.

    Word count rather than token count: a model cannot observe its own
    tokenizer, and E-001b is direct evidence that it does not honour a token
    ceiling. Words it can at least approximately count.
    """
    return (
        "Write between %d and %d words. Not fewer, not more -- a note outside "
        "that range is unusable to your colleague regardless of its quality. "
        "Output the note and nothing else: no preamble, no account of what you "
        "decided to include, no sign-off." % (low, high)
    )


def style_markers(text: str) -> Dict[str, float]:
    """Cheap structural proxies for register. NOT a validity check.

    These distinguish prose from notes; they do not establish that the intended
    style distinction survived. That needs independent blind rating, and this
    script does not pretend otherwise -- it exists to catch the loud failure
    mode where pinning the length collapses the two registers into one.
    """
    words = text.split()
    sentences = [s for s in re.split(r"[.!?]+", text) if s.strip()]
    lines = [l for l in text.splitlines() if l.strip()]
    bullets = sum(1 for l in lines if re.match(r"^\s*(?:[-*•]|\d+[.)])\s", l))
    connectives = sum(
        1 for w in words
        if w.lower().strip(",.;:") in {
            "because", "however", "therefore", "although", "whereas", "since",
            "thus", "while", "but", "so", "unless", "whether"}
    )
    return {
        "words": float(len(words)),
        "mean_sentence_words": (len(words) / len(sentences)) if sentences else 0.0,
        "bullet_fraction": (bullets / len(lines)) if lines else 0.0,
        "connectives_per_100w": 100.0 * connectives / max(1, len(words)),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="E-001c length-control feasibility")
    ap.add_argument("--targets", default="200,300",
                    help="comma-separated word-count centres to try")
    ap.add_argument("--k", type=int, default=3, help="compositions per cell per target")
    ap.add_argument("--model", default="gpt-oss:120b")
    ap.add_argument("--spec", default=os.path.join(
        REPO, "experiments", "E-001-fluency-cost", "source-spec.md"))
    ap.add_argument("--out", default=os.path.join(HERE, "feasibility.json"))
    args = ap.parse_args()

    if not ollama_available():
        print("ollama is not reachable", file=sys.stderr)
        return 2
    with open(args.spec, "r", encoding="utf-8") as fh:
        spec = fh.read()

    agent = OllamaAgent("composer", spec, model=args.model, think="medium",
                        temperature=0.7)
    record: Dict[str, Any] = {
        "experiment": "E-001c-feasibility",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": args.model, "k": args.k,
        "parity_threshold": PARITY_THRESHOLD,
        "purpose": ("instrument check before registration: does a two-sided "
                    "word target produce cost parity, and does the style "
                    "manipulation survive being pinned"),
        "targets": {},
    }

    for target in [int(t) for t in args.targets.split(",")]:
        low, high = int(target * (1 - TOLERANCE)), int(target * (1 + TOLERANCE))
        cells: Dict[str, List[Dict[str, Any]]] = {}
        print("\n=== target %d words (band %d-%d) ===" % (target, low, high))
        for cell in sorted(CELLS):
            cells[cell] = []
            prompt = CELLS[cell].replace(_OUTPUT, two_sided_output(low, high))
            assert "{budget}" not in prompt, "ceiling instruction survived"
            for i in range(args.k):
                text = agent.compose(prompt, seed=i)
                m = style_markers(text)
                m["cost_tokens"] = float(agent.cost_of(text))
                m["in_band"] = bool(low <= m["words"] <= high)
                # Keep the message, not only its measurements.
                #
                # This script's own conclusion is that the structural markers
                # are "proxies, not a validity check", and that establishing
                # the intended style distinction survived "needs independent
                # blind rating ... a precondition of E-001c's registration".
                # It then discarded every message it had composed, so that
                # precondition could not be met from its own output: nothing
                # remained to rate. Measuring an artifact and throwing the
                # artifact away is a strange thing for an instrument check to
                # do, and it cost a recomposition to notice.
                m["text"] = text
                m["seed"] = i
                cells[cell].append(m)
                # flush=True, because a redirected run is otherwise silent
                # until it exits. Sixteen compositions at about a minute each
                # produced no output for a quarter of an hour, and the only way
                # to tell working from wedged was to watch the model's CPU time
                # from outside. A progress line nobody can read during the run
                # is not progress reporting.
                print("  %s%d  %4d words  %4.0f tok  %s"
                      % (cell, i, m["words"], m["cost_tokens"],
                         "in band" if m["in_band"] else "OUT"), flush=True)

        costs = [x["cost_tokens"] for v in cells.values() for x in v]
        means = [statistics.mean([x["cost_tokens"] for x in v]) for v in cells.values()]
        fluent = [x for c, v in cells.items() for x in v if CELL_AXES[c][0] == "fluent"]
        terse = [x for c, v in cells.items() for x in v if CELL_AXES[c][0] == "terse"]
        summary = {
            "band": [low, high],
            "compliance_rate": sum(1 for v in cells.values() for x in v
                                   if x["in_band"]) / max(1, len(costs)),
            "parity_across_messages": max(costs) / min(costs),
            "parity_across_cell_means": max(means) / min(means),
            "fluent_cost_range": [min(x["cost_tokens"] for x in fluent),
                                  max(x["cost_tokens"] for x in fluent)],
            "terse_cost_range": [min(x["cost_tokens"] for x in terse),
                                 max(x["cost_tokens"] for x in terse)],
            "style_separation": {
                k: {"fluent": statistics.mean([x[k] for x in fluent]),
                    "terse": statistics.mean([x[k] for x in terse])}
                for k in ("mean_sentence_words", "bullet_fraction",
                          "connectives_per_100w")
            },
            "cells": cells,
        }
        summary["parity_passes"] = bool(
            summary["parity_across_messages"] <= PARITY_THRESHOLD
            and summary["parity_across_cell_means"] <= PARITY_THRESHOLD)
        record["targets"][str(target)] = summary

        print("  ---")
        print("  compliance with the band : %.0f%%" % (100 * summary["compliance_rate"]))
        print("  parity across messages   : %.3f" % summary["parity_across_messages"])
        print("  parity across cell means : %.3f  -> %s"
              % (summary["parity_across_cell_means"],
                 "PASS" if summary["parity_passes"] else "FAIL"))
        for k, v in summary["style_separation"].items():
            print("  %-24s fluent %7.2f   terse %7.2f" % (k, v["fluent"], v["terse"]))

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=1, sort_keys=True)
    print("\nwrote %s" % args.out)
    print("Instrument check. No hypothesis is tested and none may be read off this.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
