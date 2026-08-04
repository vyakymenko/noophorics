#!/usr/bin/env python3
"""Where does each of the four registers put its shortest message?

E-001c voided because cell A's realised minimum over 40 attempts was 229 words
against a band ceiling of 231 -- the fluent register's floor sits on the band's
ceiling. That was measured on one cell of the four, twice, by a run that was
trying to do something else.

This measures it on purpose, on all four, with the instruction the band was
calibrated on (imported, not copied -- DEFECT-001) and the band the
pre-registration registers. It answers one question: what is the shortest
message each cell produces, and does the answer differ by register.

INSTRUMENT DATA. Not E-001c's data, on the same footing as the feasibility
messages: E-001c is void and closed, and nothing here can revive it. The output
exists to characterise the obstacle a successor has to design around.

No register judgment is made here. That needs two paid raters per message and
the question asked is about length, not register. Cell A's register acceptance
is already measured live at 16/40 and 17/40 by the two voided runs.

    python3 floor_by_register.py --n 12
"""
import argparse
import json
import os
import statistics
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(REPO, "metrics"))
sys.path.insert(0, os.path.join(REPO, "experiments", "E-001b-fluency-factorial"))
sys.path.insert(0, HERE)

from noophorics.ollama_agent import OllamaAgent, ollama_available  # noqa: E402
from prompts import CELLS, CELL_AXES, _OUTPUT  # noqa: E402
from feasibility import two_sided_output  # noqa: E402

WORD_TARGET = 207          # PREREGISTRATION section 3
WORD_TOLERANCE = 0.12      # band 182-231


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--n", type=int, default=12, help="compositions per cell")
    ap.add_argument("--model", default="gpt-oss:120b")
    ap.add_argument("--out", default=os.path.join(HERE, "floor-by-register.json"))
    args = ap.parse_args()

    if not ollama_available():
        print("ollama is not reachable", file=sys.stderr)
        return 2

    low = int(WORD_TARGET * (1 - WORD_TOLERANCE))
    high = int(WORD_TARGET * (1 + WORD_TOLERANCE))
    spec = open(os.path.join(REPO, "experiments", "E-001-fluency-cost",
                             "source-spec.md"), encoding="utf-8").read()
    agent = OllamaAgent("composer", spec, model=args.model,
                        think="medium", temperature=0.7)

    record = {
        "experiment": "E-001c-instrument",
        "purpose": ("the realised length floor of each of the four registers, "
                    "under the calibrated instruction at the registered band"),
        "not_experimental_data": True,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": args.model, "n_per_cell": args.n,
        "band": [low, high], "instruction": two_sided_output(low, high),
        "cells": {},
    }
    print("floor by register: %d per cell, band %d-%d words\n" % (args.n, low, high))

    for cell in sorted(CELLS):
        prompt = CELLS[cell].replace(_OUTPUT, two_sided_output(low, high))
        assert "{budget}" not in prompt, "the token ceiling survived the replace"
        rows = []
        for i in range(args.n):
            text = agent.compose(prompt)
            w = len(text.split())
            rows.append({"words": w, "in_band": low <= w <= high,
                         "cost_tokens": int(agent.cost_of(text)), "text": text})
            print("  %s (%s)  %2d/%d  %4d words  %s"
                  % (cell, "/".join(CELL_AXES[cell]), i + 1, args.n, w,
                     "in band" if low <= w <= high else "OUT"), flush=True)
            # Written every draw: this runs for hours and a partial measurement
            # is worth keeping, unlike a partial experiment.
            record["cells"][cell] = rows
            with open(args.out, "w", encoding="utf-8") as fh:
                json.dump(record, fh, indent=1, sort_keys=True)
        ws = [r["words"] for r in rows]
        print("  -> %s floor=%d median=%.0f max=%d  in band %d/%d\n"
              % (cell, min(ws), statistics.median(ws), max(ws),
                 sum(r["in_band"] for r in rows), len(ws)), flush=True)

    print("\ncell  register              floor  median   max   in band")
    for cell in sorted(record["cells"]):
        ws = [r["words"] for r in record["cells"][cell]]
        print("  %s   %-20s  %4d  %6.0f  %4d   %d/%d"
              % (cell, "/".join(CELL_AXES[cell]), min(ws),
                 statistics.median(ws), max(ws),
                 sum(1 for w in ws if low <= w <= high), len(ws)))
    print("\nband ceiling is %d. A register whose floor exceeds it cannot be "
          "composed inside the band at all." % high)
    print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
