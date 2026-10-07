#!/usr/bin/env python3
"""Trace which array each reported interval and p-value was computed from.

Problem 13 (theory/open-problems.md): three times a claim in this repository
carried an interval computed from one quantity and a p-value computed from
another. E-002b's H4 had a paired interval and an unpaired test. E-002c's H3
had a slope-difference interval and a p-value from a difference of claim
*levels*. E-002c's H1 could not print as supported, because the terminal
summary gated the verdict on a p-value the hypothesis is registered not to
have. Two were found by the person who wrote them, re-reading after
publication; one by executing the path.

A results file cannot show the defect. It holds numbers, not the arrays they
came from, and a CI excluding zero beside a large p is only *sometimes* the
symptom -- E-002c's H3 was coherent on its face. So this traces provenance at
run time instead:

1. Load a runner -- the working tree's, or any revision's from git -- without
   running ``main``, against the current ``metrics`` library.
2. Replace ``bootstrap_ci``, ``permutation_diff`` and ``paired_permutation`` in
   the runner's namespace with wrappers that record every call's input arrays
   and keep the returned objects.
3. Run its pure ``analyse()`` on synthetic draws. No model is called and no
   repository data is read.
4. Bind each effect's ``ci95`` and ``p_value`` to the call that produced them
   by **object identity**: the floats in the effect dict are the very objects a
   wrapped call returned, so the binding is exact and perturbs no value.

Then, per effect:

- **R1, same quantity.** The test's observed statistic equals the reported
  value -- exactly, or as the mean of per-unit terms whose sum is the value
  (a sign-flip p-value is scale-invariant, so that is the same test). Any
  other relation is a test of a different quantity: E-002c H3's defect. The
  interval's own point estimate must equal the value too (**R1b**), with no
  sum allowance: a bootstrap's point is on its statistic's own scale.
- **R2, same units and pairing.** The interval and the test resample the same
  units the same way. A bootstrap over paired differences ``a_i - b_i`` beside
  a two-sample permutation of ``a`` against ``b`` discards the pairing in the
  test only: E-002b H4's defect. A permutation of ``x`` against a vector of
  zeros is a one-sample question asked with a two-sample test; it is reported
  as its own class, ``one-sample-as-two-sample``, not as a pairing defect.
- **R3, traced.** An interval or p-value no wrapped call produced was computed
  inline. It is reported as untraced -- not as wrong -- because an inline
  estimator can be correct and this tool cannot see inside it.
- **R4, summary renders the record.** For registered hypotheses (``H<n>_``),
  the runner's own ``main()`` is executed with ``run()`` replaced by the traced
  result, and its terminal table is read back: an effect the record calls
  supported that the summary does not mark, or the reverse, or omits, is
  E-002c H1's defect. Whether the two disagree depends on the draws -- a
  record decided by an interval and a summary that also asks for a corrected
  p-value part only near a boundary -- so R4 is read over many synthetic
  seeds, and a FAIL names the first seed that shows it.

**This is a report, not a gate.** Which of these relations a registration
*requires* is a decision for the person who owns the analysis plan --
E-001c's pre-registration (section 6, item 6) registers a stricter "same
array" rule than R1 -- and a gate that turns registered hypotheses red at HEAD
before anyone has decided what it should require teaches its reader to ignore
it. ``--fixtures`` is the check that the tool sees what it
exists to see: red on each incident's revision, green on the commit that
fixed it.

    python3 tools/audit_estimand.py                    # working-tree runners
    python3 tools/audit_estimand.py --rev a62d2d6      # a revision; absent runners skipped
    python3 tools/audit_estimand.py --fixtures         # the three incidents
    python3 tools/audit_estimand.py --json report.json
    python3 tools/audit_estimand.py --check-record research/estimand-audit.json
"""

from __future__ import annotations

import argparse
import contextlib
import inspect
import io
import json
import math
import os
import random
import re
import subprocess
import sys
import tempfile
import types
from typing import Any, Dict, List, Optional, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS = os.path.join(ROOT, "metrics")
if METRICS not in sys.path:
    sys.path.insert(0, METRICS)

RUNNERS = {
    "E-002b": "experiments/E-002b-phantom-agreement-ladder/runner.py",
    "E-002c": "experiments/E-002c-calibration-slope/runner.py",
}


TRACED = ("bootstrap_ci", "permutation_diff", "paired_permutation")
REL_TOL = 1e-9

# Speed only. Interval and test outcomes change with these; provenance does not.
FAST = {"PERMUTATIONS": 499, "BOOTSTRAP": 499, "BOOTSTRAP_BETA": 999,
        "FLOOR_PERMUTATIONS": 10}
# R4 reads the summary over this many synthetic draws by default.
R4_SEEDS = 40


# --------------------------------------------------------------------------
# loading


def runner_source(experiment: str, rev: Optional[str]) -> str:
    rel = RUNNERS[experiment]
    if rev is None:
        with open(os.path.join(ROOT, rel), "r", encoding="utf-8") as fh:
            return fh.read()
    return subprocess.run(["git", "show", "%s:%s" % (rev, rel)], cwd=ROOT,
                          check=True, capture_output=True, text=True).stdout


def load_runner(experiment: str, rev: Optional[str] = None) -> types.ModuleType:
    """Execute a runner's module body -- definitions only -- as a fresh module.

    ``__file__`` is the runner's real path so its own ``sys.path`` setup and
    default paths resolve as they would in place. ``main`` is never called
    here, and nothing at module level of these runners writes a file.
    """
    name = "_audit_%s_%s" % (experiment.replace("-", "_"), rev or "worktree")
    module = types.ModuleType(name)
    module.__file__ = os.path.join(ROOT, RUNNERS[experiment])
    code = compile(runner_source(experiment, rev), module.__file__, "exec")
    exec(code, module.__dict__)
    for knob, value in FAST.items():
        if knob in module.__dict__:
            setattr(module, knob, value)
    # The library's decompose() runs its own 300-permutation floor per brief,
    # which is nine-tenths of an analyse() call here and feeds no interval or
    # test this tool binds. Speed only, like FAST.
    if "decompose" in module.__dict__:
        original = module.decompose

        def fast_decompose(*args, **kwargs):
            kwargs.setdefault("permutations", FAST["FLOOR_PERMUTATIONS"])
            return original(*args, **kwargs)
        module.decompose = fast_decompose
    return module


# --------------------------------------------------------------------------
# tracing


class Call(object):
    __slots__ = ("fn", "arrays", "out")

    def __init__(self, fn: str, arrays: List[List[float]], out: Tuple[Any, ...]):
        self.fn, self.arrays, self.out = fn, arrays, out


ARRAY_PARAMS = {"bootstrap_ci": ("values",),
                "permutation_diff": ("group_a", "group_b"),
                "paired_permutation": ("differences",)}


def install_tracer(module: types.ModuleType) -> List[Call]:
    """Wrap the three helpers in ``module``'s namespace; return the call log.

    Arguments are bound by the helper's own signature, so positional and
    keyword calls are read alike, and each array is materialised *before* the
    helper runs and passed through as that list -- a generator would otherwise
    be exhausted by the helper and recorded as empty.
    """
    calls: List[Call] = []

    def wrap(fn_name, original):
        signature = inspect.signature(original)

        def traced(*args, **kwargs):
            bound = signature.bind(*args, **kwargs)
            arrays = []
            for param in ARRAY_PARAMS[fn_name]:
                values = [float(x) for x in bound.arguments[param]]
                bound.arguments[param] = values
                arrays.append(list(values))
            out = original(*bound.args, **bound.kwargs)
            calls.append(Call(fn_name, arrays, tuple(out)))
            return out
        return traced

    for fn_name in ARRAY_PARAMS:
        if fn_name in module.__dict__:
            setattr(module, fn_name, wrap(fn_name, module.__dict__[fn_name]))
    return calls


# --------------------------------------------------------------------------
# synthetic inputs


def synthetic_inputs(module: types.ModuleType, seed: int = 1, n_probes: int = 33,
                     briefs_per_rung: int = 4, draws: int = 16, n_c: int = 9):
    """Draws, elicitations and brief metadata with the shapes ``analyse`` reads.

    Claims are drawn independently of what transferred, so calibration slopes
    sit near zero, every rung keeps between 4 and 12 diverged probes so the
    outcome gates pass, and the sender is unanimous on the key.
    """
    ProbeMeasure, Probe = module.ProbeMeasure, sys.modules["noophorics.probes"].Probe
    options = ["A", "B", "C"]
    probes = [Probe("S%02d" % i, "synthetic %d" % i, options, key="A")
              for i in range(n_probes)]
    measure = ProbeMeasure("synthetic-audit", probes)
    rng = random.Random(seed)

    def column(mode: str, strength: int) -> List[str]:
        rest = [o for o in options if o != mode]
        return [mode] * strength + [rng.choice(rest) for _ in range(draws - strength)]

    raw: Dict[str, List[List[str]]] = {
        "sender": [column("A", draws) for _ in probes],
        "PRIOR": [[rng.choice(options) for _ in range(draws)] for _ in probes],
        "CEILING": [column("A", draws - 1) for _ in probes],
    }
    preds: Dict[str, Dict[str, List[List[str]]]] = {}
    meta: Dict[str, Dict[str, Any]] = {}
    rungs = getattr(module, "RUNGS", (30, 70, 110, 150))
    for r_index, rung in enumerate(rungs):
        for b in range(briefs_per_rung):
            label = "r%d_%d" % (rung, b)
            diverged = set(rng.sample(range(n_probes), 12 - 2 * r_index - (b % 2)))
            raw[label] = [column("B" if i in diverged else "A", 11) for i in range(n_probes)]
            own_receiver = ["B" if i in diverged else "A" for i in range(n_probes)]
            preds[label] = {}
            for who, own in (("sender", ["A"] * n_probes), ("receiver", own_receiver)):
                rows = []
                for i in range(n_probes):
                    q = rng.uniform(0.45, 1.0)
                    other = "C" if own[i] != "C" else "A"
                    rows.append([own[i] if rng.random() < q else other
                                 for _ in range(n_c)])
                preds[label][who] = rows
            meta[label] = {"rung": rung, "words": rung, "cost": int(rung * 1.3)}
    return measure, raw, preds, meta


# --------------------------------------------------------------------------
# rules
#
# Every verdict is a string. "ok" passes; anything beginning "FAIL" is a
# defect of the class the rule exists for, and each FAIL branch has its own
# code so a test can tell which detector fired; other verdicts ("note",
# "one-sample-as-two-sample", "no-verdict") are reported and neither pass nor
# fail.

PAIRING = "FAIL:unpaired-test-of-paired-differences"
DIFFERENT_ARRAYS = "FAIL:different-arrays"
UNRECOGNISED = "FAIL:unrecognised-structure"


def _close(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=REL_TOL, abs_tol=1e-12)


def _same_array(a: List[float], b: List[float]) -> bool:
    return bool(a) and len(a) == len(b) and all(_close(x, y) for x, y in zip(a, b))


def _find(calls: List[Call], fns: Tuple[str, ...], index: int, obj: Any) -> Optional[Call]:
    for call in calls:
        if call.fn in fns and len(call.out) > index and call.out[index] is obj:
            return call
    return None


def relate(effect: Dict[str, Any], calls: List[Call]) -> Dict[str, Any]:
    ci = effect.get("ci95")
    ci_call = None
    if isinstance(ci, (list, tuple)) and len(ci) == 2:
        ci_call = _find(calls, ("bootstrap_ci",), 1, ci[0])
        if ci_call is not None and ci_call.out[2] is not ci[1]:
            ci_call = None
    p = effect.get("p_value")
    p_call = (_find(calls, ("permutation_diff", "paired_permutation"), 1, p)
              if p is not None else None)
    value = effect.get("value")
    numeric = isinstance(value, (int, float)) and not isinstance(value, bool)
    report: Dict[str, Any] = {
        "has_ci": ci is not None, "has_p": p is not None,
        "ci_source": (None if ci is None else
                      "untraced" if ci_call is None else
                      "bootstrap_ci over %d units" % len(ci_call.arrays[0])),
        "p_source": (None if p is None else
                     "untraced" if p_call is None else
                     "%s over %s units" % (p_call.fn, "+".join(
                         str(len(a)) for a in p_call.arrays))),
        "findings": [],
    }
    if ci is not None and ci_call is None:
        report["findings"].append(("R3", "note", "interval computed inline; untraced"))
    if p is not None and p_call is None:
        report["findings"].append(("R3", "note", "p-value computed inline; untraced"))

    if p_call is not None and numeric:
        observed = p_call.out[0]
        units = len(p_call.arrays[0])
        if _close(observed, value):
            report["findings"].append(("R1", "ok", "test statistic is the reported value"))
        elif p_call.fn == "paired_permutation" and _close(observed * units, value):
            report["findings"].append(
                ("R1", "ok", "test statistic is the mean of %d per-unit terms whose "
                             "sum is the reported value" % units))
        else:
            report["findings"].append(
                ("R1", "FAIL:different-quantity",
                 "test statistic %.6g is not the reported value %.6g: the p-value "
                 "tests a different quantity" % (observed, value)))

    if ci_call is not None and numeric:
        if _close(ci_call.out[0], value):
            report["findings"].append(("R1b", "ok", "interval's point estimate is "
                                                    "the reported value"))
        else:
            report["findings"].append(
                ("R1b", "FAIL:interval-of-another-quantity",
                 "interval's point estimate %.6g is not the reported value %.6g"
                 % (ci_call.out[0], value)))

    if ci_call is not None and p_call is not None:
        a = ci_call.arrays[0]
        if p_call.fn == "paired_permutation":
            if _same_array(a, p_call.arrays[0]):
                report["findings"].append(("R2", "ok", "interval and test share one "
                                                      "array of %d units" % len(a)))
            else:
                report["findings"].append(("R2", DIFFERENT_ARRAYS, "interval and paired "
                                                                 "test use different arrays"))
        else:
            g1, g2 = p_call.arrays
            if g2 and all(x == 0.0 for x in g2) and len(g1) == len(g2):
                if _same_array(a, g1):
                    report["findings"].append(
                        ("R2", "one-sample-as-two-sample",
                         "two-sample permutation of %d units against %d zeros"
                         % (len(g1), len(g2))))
                else:
                    report["findings"].append(
                        ("R2", DIFFERENT_ARRAYS, "test against zeros uses a different "
                                                 "array from the interval"))
            elif (a and len(a) == len(g1) == len(g2)
                  and all(_close(x, y - z) for x, y, z in zip(a, g1, g2))):
                report["findings"].append(
                    ("R2", PAIRING, "interval over %d paired differences, test an "
                                    "unpaired two-sample permutation of the same %d "
                                    "pairs" % (len(a), len(a))))
            else:
                report["findings"].append(("R2", UNRECOGNISED, "interval and two-sample "
                                                               "test share no recognised "
                                                               "structure"))
    return report


SUMMARY_LINE = re.compile(r"^\s{2}(H\d\w*)\s")


def _marked(line: str) -> bool:
    """A row is marked when its last token is exactly SUPPORTED, not NOT SUPPORTED."""
    tokens = line.split()
    return (bool(tokens) and tokens[-1] == "SUPPORTED"
            and (len(tokens) < 2 or tokens[-2] != "NOT"))


def summary_marks(module: types.ModuleType, result: Dict[str, Any]) -> Dict[str, Any]:
    """Run the runner's own ``main()`` on ``result`` and read back its table.

    ``run`` is replaced so no model, cache or brief file is touched, and
    ``--out`` points at a temporary directory. Returns ``marks`` -- registered
    effects printed, and whether each was marked -- with ``wrote_inside_temp``,
    which is True only if the results file ``main()`` reported writing lies in
    that directory, and ``error`` if ``main()`` raised.
    """
    if "main" not in module.__dict__:
        return {"marks": None, "error": "runner has no main()", "wrote_inside_temp": None}
    payload = dict(result)
    payload.setdefault("gates", {})
    payload.setdefault("dry_run", True)
    saved_run, saved_argv = module.__dict__.get("run"), sys.argv
    module.run = lambda args: payload
    out = io.StringIO()
    error, wrote_inside = None, None
    try:
        with tempfile.TemporaryDirectory() as tmp:
            sys.argv = ["runner.py", "--out", tmp]
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                module.main()
            written = re.findall(r"^wrote (.+)$", out.getvalue(), re.M)
            wrote_inside = bool(written) and all(
                os.path.realpath(w).startswith(os.path.realpath(tmp) + os.sep)
                for w in written)
    except (SystemExit, Exception) as exc:   # reported, never swallowed silently
        error = "%s: %s" % (type(exc).__name__, exc)
    finally:
        module.run, sys.argv = saved_run, saved_argv
    marks: Dict[str, bool] = {}
    for line in out.getvalue().splitlines():
        m = SUMMARY_LINE.match(line)
        if m and m.group(1) in result.get("effects", {}):
            marks[m.group(1)] = _marked(line)
    return {"marks": None if error else marks, "error": error,
            "wrote_inside_temp": wrote_inside}


def _r4(name: str, effect: Dict[str, Any], summary: Dict[str, Any]):
    """R4 for one registered effect on one draw."""
    raw = effect.get("supported")
    if summary["marks"] is None:
        return ("FAIL:summary-raised" if summary["error"] else "note",
                "summary not executable: %s" % summary["error"])
    if raw is None:
        return ("no-verdict", "the record carries no supported verdict")
    if name not in summary["marks"]:
        return ("FAIL:omitted" if raw else "note",
                "summary omits it; record says supported=%r" % raw)
    printed = summary["marks"][name]
    return ("ok" if printed == bool(raw) else "FAIL:mark-disagrees",
            "summary %s it; record says supported=%r"
            % ("marks" if printed else "does not mark", raw))


def _analyse(module: types.ModuleType, seed: int) -> Dict[str, Any]:
    measure, raw, preds, meta = synthetic_inputs(module, seed)
    return module.analyse(measure, raw, preds, meta, module.EPSILON)


def audit(experiment: str, rev: Optional[str] = None, seed: int = 1,
          r4_seeds: int = R4_SEEDS) -> Dict[str, Any]:
    """R1-R3 on one synthetic draw, R4 over ``r4_seeds`` of them.

    R1-R3 are properties of which arrays the code passes where, and one draw
    exercises them; R4 depends on where a draw falls relative to two decision
    rules, so it is read over many and its first disagreement is kept.
    """
    module = load_runner(experiment, rev)
    calls = install_tracer(module)
    result = _analyse(module, seed)
    traced = len(calls)
    if result.get("void"):
        raise RuntimeError("%s@%s voided on synthetic inputs: %s"
                           % (experiment, rev or "worktree", result.get("void_reason")))
    effects: Dict[str, Any] = {}
    for name, effect in sorted(result.get("effects", {}).items()):
        if isinstance(effect, dict) and "value" in effect:
            effects[name] = relate(effect, calls)

    registered = [n for n in effects if re.match(r"^H\d", n)]
    r4: Dict[str, Tuple[str, str, int]] = {}
    wrote_inside: List[Optional[bool]] = []
    for s in range(seed, seed + max(1, r4_seeds)):
        res = result if s == seed else _analyse(module, s)
        if res.get("void"):
            continue
        summary = summary_marks(module, res)
        wrote_inside.append(summary["wrote_inside_temp"])
        for name in registered:
            effect = res.get("effects", {}).get(name)
            if not isinstance(effect, dict):
                continue
            verdict, text = _r4(name, effect, summary)
            if name not in r4 or (not r4[name][0].startswith("FAIL")
                                  and verdict.startswith("FAIL")):
                r4[name] = (verdict, text, s)
    for name in registered:
        if name in r4:
            verdict, text, s = r4[name]
            effects[name]["findings"].append(
                ("R4", verdict, "%s (synthetic seed %d)" % (text, s)
                 if verdict.startswith("FAIL") else text))
    return {"experiment": experiment, "revision": rev or "worktree",
            "synthetic_seed": seed, "r4_seeds": r4_seeds,
            "traced_calls": traced,
            "summary_wrote_only_to_temp": (all(w is True for w in wrote_inside)
                                           if wrote_inside else None),
            "effects": effects}


def status(rep: Dict[str, Any], rule: str) -> Optional[str]:
    for r, verdict, _ in rep["findings"]:
        if r == rule:
            return verdict
    return None


# Each incident: the revision that carried it, the commit that fixed it, the
# effect, the rule, and the exact verdict the defect must produce -- so a red
# result shows the detector for *this* defect fired, not some catch-all.
FIXTURES = [
    {"incident": "E-002b H4: paired interval, unpaired test",
     "experiment": "E-002b", "effect": "H4_sender_worse_than_receiver",
     "rule": "R2", "expected_fail": PAIRING,
     "defect_rev": "a62d2d6", "fixed_rev": "df0305b"},
    {"incident": "E-002c H3: slope-difference interval, level-difference test",
     "experiment": "E-002c", "effect": "H3_sender_less_responsive",
     "rule": "R1", "expected_fail": "FAIL:different-quantity",
     "defect_rev": "cea9243", "fixed_rev": "c97005b"},
    {"incident": "E-002c H1: summary gated on a p-value H1 has by design none of",
     "experiment": "E-002c", "effect": "H1_beta_below_half",
     "rule": "R4", "expected_fail": "FAIL:mark-disagrees",
     "defect_rev": "549ff54", "fixed_rev": "cea9243"},
]


def run_fixtures(r4_seeds: int = 8) -> List[Dict[str, Any]]:
    rows = []
    for fx in FIXTURES:
        before = audit(fx["experiment"], fx["defect_rev"], r4_seeds=r4_seeds)
        after = audit(fx["experiment"], fx["fixed_rev"], r4_seeds=r4_seeds)
        b = before["effects"].get(fx["effect"])
        a = after["effects"].get(fx["effect"])
        rows.append(dict(
            fx,
            defect_status=b and status(b, fx["rule"]),
            fixed_status=a and status(a, fx["rule"]),
            red_on_defect=b is not None and status(b, fx["rule"]) == fx["expected_fail"],
            green_on_fix=a is not None and status(a, fx["rule"]) == "ok",
            wrote_only_to_temp=(before["summary_wrote_only_to_temp"] is True
                                and after["summary_wrote_only_to_temp"] is True)))
    return rows


def render(report: Dict[str, Any]) -> str:
    lines = ["%s @ %s  (%d traced calls on synthetic seed %d; R4 over %d seeds)"
             % (report["experiment"], report["revision"], report["traced_calls"],
                report["synthetic_seed"], report["r4_seeds"])]
    for name, rep in report["effects"].items():
        lines.append("  %s" % name)
        lines.append("      interval: %s;  p-value: %s" % (rep["ci_source"], rep["p_source"]))
        for rule, verdict, text in rep["findings"]:
            lines.append("      %-4s %-40s %s" % (rule, verdict, text))
    return "\n".join(lines)


def build_record() -> Dict[str, Any]:
    """Fixtures and the working-tree report, as research/ quotes them.

    Deterministic: every draw is seeded, and the findings are text. The counts
    a note states about this report are read back from here by check_counts.
    """
    reports = [audit(e) for e in sorted(RUNNERS)]
    effects = [(r["experiment"], n, rep) for r in reports
               for n, rep in r["effects"].items()]
    registered = [x for x in effects if re.match(r"^H\d", x[1])]
    return {
        "fixtures": run_fixtures(),
        "worktree": reports,
        "counts": {
            "effects": len(effects),
            "untraced_intervals": sum(1 for _, _, rep in effects
                                      if rep["ci_source"] == "untraced"),
            "registered": len(registered),
            "registered_untraced_intervals": sum(
                1 for _, _, rep in registered if rep["ci_source"] == "untraced"),
            "r4_seeds": R4_SEEDS,
        },
    }


def _exists_at(experiment: str, rev: str) -> bool:
    return subprocess.run(["git", "cat-file", "-e", "%s:%s" % (rev, RUNNERS[experiment])],
                          cwd=ROOT, capture_output=True).returncode == 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--experiment", choices=sorted(RUNNERS), action="append")
    ap.add_argument("--rev", help="a git revision; default is the working tree")
    ap.add_argument("--seeds", type=int, default=R4_SEEDS,
                    help="synthetic draws R4 is read over (default %d)" % R4_SEEDS)
    ap.add_argument("--fixtures", action="store_true",
                    help="red on each incident's revision, green on its fix")
    ap.add_argument("--json", help="write the report here as JSON")
    ap.add_argument("--record", metavar="PATH",
                    help="write the saved record (fixtures and working-tree "
                         "report) that research/ quotes counts from")
    ap.add_argument("--check-record", metavar="PATH",
                    help="recompute the record and fail if PATH differs")
    args = ap.parse_args()

    if args.record or args.check_record:
        text = json.dumps(build_record(), indent=1, sort_keys=True) + "\n"
        if args.record:
            with open(args.record, "w", encoding="utf-8") as fh:
                fh.write(text)
            print("wrote %s" % args.record)
            return 0
        with open(args.check_record, "r", encoding="utf-8") as fh:
            saved = fh.read()
        if saved != text:
            print("audit_estimand: %s is stale -- the runners, the tool or the "
                  "library moved; regenerate with --record and review" % args.check_record)
            return 1
        print("audit_estimand: %s current" % args.check_record)
        return 0

    if args.fixtures:
        rows = run_fixtures()
        for row in rows:
            print("%-62s %-3s %s@%s=%s  %s@%s=%s" % (
                row["incident"], row["rule"],
                "red" if row["red_on_defect"] else "NOT RED", row["defect_rev"],
                row["defect_status"], "green" if row["green_on_fix"] else "NOT GREEN",
                row["fixed_rev"], row["fixed_status"]))
        ok = all(r["red_on_defect"] and r["green_on_fix"] and r["wrote_only_to_temp"]
                 for r in rows)
        print("\naudit_estimand fixtures: %s" % ("all three incidents seen"
                                               if ok else "an incident was NOT seen"))
        if args.json:
            with open(args.json, "w", encoding="utf-8") as fh:
                json.dump(rows, fh, indent=1)
        return 0 if ok else 1

    reports = []
    for experiment in (args.experiment or sorted(RUNNERS)):
        if args.rev and not _exists_at(experiment, args.rev):
            print("%s: no runner at %s; skipped\n" % (experiment, args.rev))
            continue
        reports.append(audit(experiment, args.rev, r4_seeds=args.seeds))
    print("\n\n".join(render(r) for r in reports))
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(reports, fh, indent=1)
    # A report, not a gate: findings at HEAD are for the owner of the analysis
    # plan to rule on. Exit non-zero only if the audit itself could not run.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
