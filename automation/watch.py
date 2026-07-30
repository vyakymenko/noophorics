#!/usr/bin/env python3
"""Watch a running experiment and report state changes. Reports only.

    python3 automation/watch.py experiments/E-002b-phantom-agreement-ladder

Why this exists. Three experiments have voided in this repository, and in two of
them the void was discovered hours after it happened -- E-001b would have burned
thirty hours before crashing, and E-002 sat at a fired gate until someone looked.
A gate that fires into an empty room is only half a gate.

It reports transitions, not a stream: started, progress crossing a decile, the
process disappearing, a results file appearing, a void. Silence means nothing
changed, which is the property that makes a notifier bearable overnight.

Like everything under automation/, it reports facts and makes no judgements.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from notify import send  # noqa: E402


def cache_progress(exp: str) -> Dict[str, int]:
    path = os.path.join(exp, "sample-cache.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            d = json.load(fh)
    except (json.JSONDecodeError, OSError):
        # The runner writes atomically via rename, but a read can still land
        # mid-swap. A monitor must never crash on the thing it monitors.
        return {}
    draws = {c: v for c, v in d.items() if not c.startswith(("pred-", "claim-"))}
    elicit = {c: v for c, v in d.items() if c.startswith(("pred-", "claim-"))}
    return {"draw_conditions": len(draws),
            "draw_units": sum(len(v) for v in draws.values()),
            "elicit_conditions": len(elicit),
            "elicit_units": sum(len(v) for v in elicit.values())}


def newest_result(exp: str) -> Optional[str]:
    d = os.path.join(exp, "results")
    if not os.path.isdir(d):
        return None
    files = sorted(f for f in os.listdir(d) if f.endswith(".json"))
    return os.path.join(d, files[-1]) if files else None


def process_alive(pattern: str) -> bool:
    try:
        subprocess.check_output(["pgrep", "-f", pattern],
                                stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        return False


def describe(path: str) -> str:
    with open(path, "r", encoding="utf-8") as fh:
        r = json.load(fh)
    if r.get("void"):
        return ("■ VOID at %s\n  %s" % (r.get("voided_at", "?"),
                                        str(r.get("void_reason"))[:600]))
    lines = ["● results written: %s" % os.path.basename(path)]
    gates = r.get("gates", {})
    failed = [g for g, v in gates.items() if not v.get("passed")]
    lines.append("  gates: %d/%d passed%s"
                 % (len(gates) - len(failed), len(gates),
                    ("  FAILED: " + ", ".join(failed)) if failed else ""))
    for k, v in sorted((r.get("effects") or {}).items()):
        val = v.get("value")
        if val is not None:
            lines.append("  %s = %+.4f  p(holm)=%s"
                         % (k, val, v.get("p_value_holm")))
    for rung, v in sorted((r.get("rungs") or {}).items(),
                          key=lambda x: int(x[0])):
        lines.append("  rung %s: %.1f diverged -> %s"
                     % (rung, v.get("mean_diverged", 0),
                        "pass" if v.get("passed") else "DROPPED"))
    lines.append("  (values only; no interpretation is made here)")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="watch one experiment directory")
    ap.add_argument("experiment")
    ap.add_argument("--total", type=int, default=0,
                    help="expected draw units, for percentage reporting")
    ap.add_argument("--interval", type=int, default=300)
    ap.add_argument("--pattern", default="",
                    help="pgrep pattern for the runner; defaults to the dir name")
    ap.add_argument("--max-hours", type=float, default=24.0)
    args = ap.parse_args()

    exp = os.path.join(REPO, args.experiment) if not os.path.isabs(args.experiment) \
        else args.experiment
    if not os.path.isdir(exp):
        print("no such experiment directory: %s" % exp, file=sys.stderr)
        return 2
    pattern = args.pattern or os.path.basename(exp.rstrip("/"))

    seen_result = newest_result(exp)
    last_decile = -1
    began = time.time()
    send("◇ watching %s (reports transitions only; silence means no change)"
         % os.path.basename(exp))

    while time.time() - began < args.max_hours * 3600:
        time.sleep(args.interval)

        latest = newest_result(exp)
        if latest and latest != seen_result:
            send("%s\n%s" % (os.path.basename(exp), describe(latest)))
            return 0

        prog = cache_progress(exp)
        if args.total and prog.get("draw_units"):
            decile = int(10 * prog["draw_units"] / args.total)
            if decile > last_decile:
                last_decile = decile
                hours = (time.time() - began) / 3600.0
                send("· %s %d%%  (%d/%d draw units, %d elicitation conditions, "
                     "%.1fh elapsed)"
                     % (os.path.basename(exp), 10 * decile, prog["draw_units"],
                        args.total, prog.get("elicit_conditions", 0), hours))

        if not process_alive(pattern):
            latest = newest_result(exp)
            if latest and latest != seen_result:
                send("%s\n%s" % (os.path.basename(exp), describe(latest)))
            else:
                send("✖ %s: the runner is gone and no new results file appeared.\n"
                     "  Draws on disk: %s\n"
                     "  Check the log before assuming the data is lost -- the "
                     "sample cache is written incrementally and survives a crash."
                     % (os.path.basename(exp), prog.get("draw_units", "?")))
            return 0

    send("◇ %s: watch window of %.0fh elapsed; the run is still going."
         % (os.path.basename(exp), args.max_hours))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
