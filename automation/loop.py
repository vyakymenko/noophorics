#!/usr/bin/env python3
"""Run pre-registered experiments from a committed queue. Report. Never decide.

    python3 automation/loop.py --dry-run     # show the plan, run nothing
    python3 automation/loop.py

WHAT THIS MAY DO, AND WHY THE LINE IS WHERE IT IS
-------------------------------------------------
CONTRIBUTING's automation table splits the research cycle in half: execution may
be automated, interpretation may not. This loop is the execution half and
nothing else.

    it runs a command that was already written and committed
    it collects data and commits raw results
    it reports gate values, void reasons and progress

    it does not choose what to run       -- queue.json is human-authored
    it does not write FINDINGS           -- no interpretation is emitted
    it does not edit a pre-registration  -- refuses if the tree is dirty there
    it does not promote a law            -- it has no opinion about laws

An agent that generates a hypothesis, designs the test, runs it and rules on
whether it passed is a machine for confirming its own priors at speed. It does
not violate the pre-registration norm -- every hypothesis is still committed
before its data -- which is exactly why the norm alone does not protect against
it. The commit order stays honest while the independence that made the order
meaningful quietly disappears.

THE SECOND REASON, SPECIFIC TO THIS FIELD
-----------------------------------------
A long-running loop is a chain of self-transfers: each iteration hands its
understanding to the next through the narrow channel of a queue entry and a
commit message. That is Problem 9, and L5 predicts self-transfer should show
*maximal* phantom agreement -- an agent has every reason to believe its own
summary preserved what mattered.

So the loop is instrumented as an instance of its own subject. Each iteration
records what it believed it was doing and what the run actually produced, in
``automation/self-transfer.jsonl``. The loop does not compute Phi from it and
does not act on it; computing it is a measurement, and measurements are made by
people here.

HARD LIMITS, all pre-set and none of them time-based
----------------------------------------------------
A cap on runs, not an interval: runs cost compute and an interval-bounded loop
has no bounded cost. Every run is committed including failures and voids -- a
sweep that silently drops its failures is worse than no sweep. And the queue is
read once at start, so editing it mid-flight cannot redirect a running loop.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from typing import Any, Dict, List, Optional

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from notify import send  # noqa: E402

QUEUE = os.path.join(HERE, "queue.json")
LEDGER = os.path.join(HERE, "self-transfer.jsonl")
MAX_RUNS_DEFAULT = 4
# Paths the loop must never modify. Checked before and after every run: a loop
# that edits a pre-registration has broken the only rule that matters.
PROTECTED = ("PREREGISTRATION.md", "PRINCIPIA.md", "theory/", "RETRACTIONS.md")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO,
                                   stderr=subprocess.DEVNULL).decode()


def protected_dirty() -> List[str]:
    """Protected paths with uncommitted changes. A tripwire, checked twice."""
    out = []
    for line in git("status", "--porcelain").splitlines():
        path = line[3:].strip()
        if any(p in path for p in PROTECTED):
            out.append(path)
    return out


def load_queue() -> List[Dict[str, Any]]:
    with open(QUEUE, "r", encoding="utf-8") as fh:
        q = json.load(fh)
    entries = q.get("runs", [])
    for e in entries:
        for field in ("id", "preregistration", "command", "expect"):
            if field not in e:
                raise ValueError("queue entry %r missing %r"
                                 % (e.get("id", "?"), field))
        prereg = os.path.join(REPO, e["preregistration"])
        if not os.path.exists(prereg):
            raise ValueError("%s: no pre-registration at %s"
                             % (e["id"], e["preregistration"]))
        # The command must be a list, never a shell string. A shell string in a
        # committed queue is an injection surface for anyone who can open a PR.
        if not isinstance(e["command"], list):
            raise ValueError("%s: command must be a list of argv tokens" % e["id"])
    return entries


def record(entry: Dict[str, Any], stage: str, payload: Dict[str, Any]) -> None:
    """Append to the self-transfer ledger. Facts only; no Phi is computed."""
    row = {"utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "id": entry["id"], "stage": stage,
           "expected": entry.get("expect"), **payload}
    with open(LEDGER, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, sort_keys=True) + "\n")


def summarise(entry: Dict[str, Any]) -> Dict[str, Any]:
    """Read the newest results file for an entry. Reports; does not judge."""
    d = os.path.join(REPO, entry["results_dir"]) if entry.get("results_dir") else None
    if not d or not os.path.isdir(d):
        return {"results": "none"}
    files = sorted(f for f in os.listdir(d) if f.endswith(".json"))
    if not files:
        return {"results": "none"}
    with open(os.path.join(d, files[-1]), "r", encoding="utf-8") as fh:
        r = json.load(fh)
    out: Dict[str, Any] = {"results_file": files[-1]}
    if r.get("void"):
        out["void"] = True
        out["void_reason"] = str(r.get("void_reason"))[:400]
        out["voided_at"] = r.get("voided_at")
        return out
    gates = r.get("gates", {})
    out["gates_failed"] = [g for g, v in gates.items() if not v.get("passed")]
    out["gates_total"] = len(gates)
    # Effect values are reported verbatim, with no verdict attached.
    out["effects"] = {k: {"value": v.get("value"), "p_holm": v.get("p_value_holm")}
                      for k, v in (r.get("effects") or {}).items()}
    return out


def run_one(entry: Dict[str, Any], dry: bool) -> Dict[str, Any]:
    cmd = entry["command"]
    record(entry, "start", {"command": cmd})
    send("▶ %s starting\n  prereg: %s\n  expecting: %s"
         % (entry["id"], entry["preregistration"], entry.get("expect")))
    if dry:
        return {"skipped": "dry run"}

    began = time.time()
    proc = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
    mins = (time.time() - began) / 60.0
    tail = (proc.stdout or "")[-1200:]

    result = summarise(entry)
    result.update({"exit_code": proc.returncode, "minutes": round(mins, 1)})
    record(entry, "end", result)

    if result.get("void"):
        send("■ %s VOID after %.0f min\n  at: %s\n  %s"
             % (entry["id"], mins, result.get("voided_at"),
                result.get("void_reason")))
    elif proc.returncode != 0:
        send("✖ %s exited %d after %.0f min\n%s"
             % (entry["id"], proc.returncode, mins,
                (proc.stderr or tail)[-800:]))
    else:
        failed = result.get("gates_failed") or []
        lines = ["● %s finished in %.0f min" % (entry["id"], mins),
                 "  gates: %d/%d passed"
                 % (result.get("gates_total", 0) - len(failed),
                    result.get("gates_total", 0))]
        if failed:
            lines.append("  FAILED: " + ", ".join(failed))
        for k, v in sorted((result.get("effects") or {}).items()):
            if v.get("value") is not None:
                lines.append("  %s = %+.4f  p=%s" % (k, v["value"], v.get("p_holm")))
        lines.append("  (values only; no interpretation is made here)")
        send("\n".join(lines))
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description="run the committed experiment queue")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--max-runs", type=int, default=MAX_RUNS_DEFAULT)
    args = ap.parse_args()

    dirty = protected_dirty()
    if dirty:
        msg = ("refusing to start: uncommitted changes under protected paths\n  "
               + "\n  ".join(dirty))
        print(msg, file=sys.stderr)
        send("✖ loop refused to start\n" + msg)
        return 2

    entries = load_queue()[:args.max_runs]
    if not entries:
        print("queue is empty")
        return 0

    send("◆ loop starting: %d run(s), cap %d\n%s"
         % (len(entries), args.max_runs,
            "\n".join("  %d. %s" % (i + 1, e["id"]) for i, e in enumerate(entries))))

    for entry in entries:
        run_one(entry, args.dry_run)
        after = protected_dirty()
        if after:
            # A run that touched a pre-registration is a stop condition, not a
            # warning. The loop cannot judge whether the edit was innocent.
            msg = ("STOPPING: %s left protected paths modified\n  " % entry["id"]
                   + "\n  ".join(after))
            print(msg, file=sys.stderr)
            send("■ " + msg)
            return 3

    send("◆ loop finished: %d run(s). Nothing was interpreted; read the results."
         % len(entries))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
