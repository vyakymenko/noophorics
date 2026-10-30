#!/usr/bin/env python3
"""Do real model draws persist from one draw to the next?

Runs the audit registered in research/2026-10-30-draw-dependence-plan.md,
committed before this file. Every answer-draw sequence in the experiments'
sample caches is tested, per model, for repeats of the immediately preceding
answer beyond what its own counts imply, against permutations of each sequence.

    python3 tools/audit_draw_dependence.py --out research/draw-dependence.json
    python3 tools/audit_draw_dependence.py --write-tables
    python3 tools/audit_draw_dependence.py --check

Nothing here prints or records an answer, a probe or a condition's text: the
record holds counts and statistics only, so the agent that runs the audit sees
aggregates. ``--check`` recomputes every observed quantity from the caches and
rescores the predictions from the record; the permutation and simulation
quantities are reproduced by a full run, which is seeded.

Details the plan does not fix, settled here before any run: a sequence's
answers are compared as values (a non-string value by its JSON form); a model
named ``a/b`` in a condition is ``b``; permutations run in 20 chunks of 500 with
seeds fixed per chunk, so the result does not depend on the number of
processes; the null's 95th percentile is its ``ceil(0.95 N)``-th smallest value.

Standard library only.
"""

from __future__ import annotations

import argparse
import bisect
import concurrent.futures
import glob
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict
from typing import Dict, List, NamedTuple, Optional, Sequence, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAN = "research/2026-10-30-draw-dependence-plan.md"
RECORD = "research/draw-dependence.json"
NOTE = "research/2026-10-30-draw-dependence-results.md"
START, END = "<!-- tables:start -->", "<!-- tables:end -->"

FAMILIES = ("gpt-oss:120b", "qwen3.5:35b", "claude-opus-4-8")
EXCLUDED = ("pred-", "claim-")
PERMUTATIONS = 10_000
CHUNKS = 20
PERM_SEED = 20_261_030
GRID = tuple(round(0.01 * i, 2) for i in range(51))
DATASETS = 500
SIM_SEED = 30_102_026
POWER_AT = (0.05, 0.1, 0.3)
ALPHA = 0.05
GROUPED_FLAG = 0.001


class Seq(NamedTuple):
    source: str
    family: str
    condition: str
    probe: str
    answers: Tuple[int, ...]


# --------------------------------------------------------------------------
# reading the caches


def parse_condition(cond: str) -> Optional[Tuple[str, str]]:
    """(name, model) for an answer-draw condition; None for anything else."""
    name, sep, model = cond.split("#", 1)[0].partition("@")
    if not sep or name.startswith(EXCLUDED):
        return None
    return name, model.split("/")[-1]


def _value(v) -> str:
    return v if isinstance(v, str) else json.dumps(v, sort_keys=True)


def _encode(values: Sequence) -> Tuple[int, ...]:
    """Answers as small integers by first appearance; the statistics need no more."""
    seen: Dict[str, int] = {}
    return tuple(seen.setdefault(_value(v), len(seen)) for v in values)


def experiment_id(path: str) -> str:
    parts = os.path.basename(os.path.dirname(path)).split("-")
    return "-".join(parts[:2])


def load(root: str = ROOT) -> Tuple[List[Tuple[str, str, str, str, tuple]], List[str]]:
    """Every answer-draw sequence on disk, raw, and the caches read."""
    paths = sorted(glob.glob(os.path.join(root, "experiments", "*", "sample-cache.json")))
    rows = []
    for path in paths:
        with open(path, encoding="utf-8") as fh:
            data = json.load(fh)
        source = experiment_id(path)
        for cond in sorted(data):
            parsed = parse_condition(cond)
            if parsed is None or not isinstance(data[cond], dict):
                continue
            for probe in sorted(data[cond]):
                seq = data[cond][probe]
                if isinstance(seq, list) and len(seq) >= 2:
                    rows.append((source, parsed[1], cond, probe, tuple(_value(v) for v in seq)))
    return rows, [os.path.relpath(p, root) for p in paths]


def dedupe(rows) -> Tuple[List[Seq], int]:
    """Drop a sequence equal to or a prefix of another for the same condition and probe."""
    groups = defaultdict(list)
    for r in rows:
        groups[(r[2], r[3])].append(r)
    kept, dropped = [], 0
    for key in sorted(groups):
        mine: List[tuple] = []
        for r in sorted(groups[key], key=lambda r: (-len(r[4]), r[0])):
            if any(k[4][:len(r[4])] == r[4] for k in mine):
                dropped += 1
                continue
            mine.append(r)
        kept.extend(Seq(r[0], r[1], r[2], r[3], _encode(r[4])) for r in mine)
    return kept, dropped


# --------------------------------------------------------------------------
# per-sequence statistics


def repeats(a: Sequence[int]) -> int:
    return sum(1 for x, y in zip(a, a[1:]) if x == y)


def expected_repeats(a: Sequence[int]) -> float:
    """E[R] over all orderings of a's answers: sum c(c - 1) / n."""
    return sum(c * (c - 1) for c in Counter(a).values()) / len(a)


def drift(a: Sequence[int]) -> int:
    h = len(a) // 2
    first, second = Counter(a[:h]), Counter(a[h:])
    return sum((first[k] - second[k]) ** 2 for k in set(a))


def grouped(a: Sequence[int]) -> bool:
    return 1 + sum(1 for x, y in zip(a, a[1:]) if x != y) == len(set(a))


def informative(a: Sequence[int]) -> bool:
    return len(set(a)) > 1


# --------------------------------------------------------------------------
# permutations


def _groups(seqs: Sequence[Seq]) -> List[Tuple[str, str]]:
    return sorted({(s.family, s.source) for s in seqs if informative(s.answers)})


def _perm_chunk(args) -> List[List[Tuple[int, int, int]]]:
    """For each permutation, per (family, source): sums of R, D and grouped."""
    chunk, size, by_group = args
    rng = random.Random(PERM_SEED + chunk)
    out = []
    for _ in range(size):
        row = []
        for seqs in by_group:
            r = d = g = 0
            for a in seqs:
                b = list(a)
                rng.shuffle(b)
                r += repeats(b)
                d += drift(b)
                g += grouped(b)
            row.append((r, d, g))
        out.append(row)
    return out


def permute(seqs: Sequence[Seq], workers: int, n: int = PERMUTATIONS):
    keys = _groups(seqs)
    by_group = [[s.answers for s in seqs if (s.family, s.source) == k and informative(s.answers)]
                for k in keys]
    size = n // CHUNKS
    jobs = [(c, size, by_group) for c in range(CHUNKS)]
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        rows = [row for part in pool.map(_perm_chunk, jobs) for row in part]
    return keys, rows


# --------------------------------------------------------------------------
# simulation under persistence


def persistent(rng: random.Random, n: int, cum: Sequence[float], rho: float) -> List[int]:
    top = len(cum) - 1
    pick = lambda: min(bisect.bisect_right(cum, rng.random()), top)
    out = [pick()]
    for _ in range(n - 1):
        out.append(out[-1] if rho > 0.0 and rng.random() < rho else pick())
    return out


def _cumulative(a: Sequence[int]) -> List[float]:
    counts = Counter(a)
    acc, out = 0.0, []
    for k in sorted(counts):
        acc += counts[k] / len(a)
        out.append(acc)
    return out


def _sim_task(args) -> List[float]:
    family_index, rho_index, shapes = args
    rng = random.Random(SIM_SEED + 1000 * family_index + rho_index)
    rho = GRID[rho_index]
    out = []
    for _ in range(DATASETS):
        t = 0.0
        for n, cum in shapes:
            b = persistent(rng, n, cum, rho)
            t += repeats(b) - expected_repeats(b)
        out.append(t)
    return out


def simulate(seqs: Sequence[Seq], family: str, workers: int) -> List[List[float]]:
    shapes = [(len(s.answers), _cumulative(s.answers)) for s in seqs
              if s.family == family and informative(s.answers)]
    index = sorted({s.family for s in seqs}).index(family)
    jobs = [(index, i, shapes) for i in range(len(GRID))]
    with concurrent.futures.ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(_sim_task, jobs))


# --------------------------------------------------------------------------
# the audit


def observed(seqs: Sequence[Seq]) -> Dict[Tuple[str, str], Dict]:
    """Every observed quantity per (family, source); cheap, so --check redoes it."""
    out: Dict[Tuple[str, str], Dict] = {}
    for s in seqs:
        o = out.setdefault((s.family, s.source), {
            "sequences": 0, "informative": 0, "draws": 0, "repeats": 0,
            "expected_repeats": 0.0, "room": 0.0, "drift": 0, "grouped": 0})
        o["sequences"] += 1
        o["draws"] += len(s.answers)
        if not informative(s.answers):
            continue
        e0 = expected_repeats(s.answers)
        o["informative"] += 1
        o["repeats"] += repeats(s.answers)
        o["expected_repeats"] += e0
        o["room"] += len(s.answers) - 1 - e0
        o["drift"] += drift(s.answers)
        o["grouped"] += grouped(s.answers)
    return out


def _sum(parts: Sequence[Dict]) -> Dict:
    keys = ("sequences", "informative", "draws", "repeats", "expected_repeats", "room",
            "drift", "grouped")
    return {k: sum(p[k] for p in parts) for k in keys}


def _excess(o: Dict) -> float:
    return o["repeats"] - o["expected_repeats"]


def _upper_p(stat: float, null: Sequence[float]) -> float:
    return (1 + sum(1 for x in null if x >= stat - 1e-9)) / (1 + len(null))


def holm(ps: Dict[str, float]) -> Dict[str, float]:
    order = sorted(ps, key=lambda k: (ps[k], k))
    m, running, out = len(order), 0.0, {}
    for j, k in enumerate(order):
        running = max(running, min(1.0, (m - j) * ps[k]))
        out[k] = running
    return out


def rho_upper(t_obs: float, sims: Sequence[Sequence[float]]) -> Dict:
    ok = [i for i, ts in enumerate(sims) if sum(1 for t in ts if t <= t_obs) / len(ts) >= 0.05]
    if not ok:
        return {"kind": "below_grid", "value": None}
    if ok[-1] == len(GRID) - 1:
        return {"kind": "above_grid", "value": None}
    return {"kind": "bound", "value": GRID[ok[-1]]}


def _below(bound: Dict, x: float) -> bool:
    return bound["kind"] == "below_grid" or (bound["kind"] == "bound" and bound["value"] < x)


def score(families: Dict[str, Dict]) -> Dict:
    def fam(name, cap):
        f = families.get(name)
        if f is None:
            return {"holds": False, "reason": "no sequences"}
        return {"holds": f["p_holm"] > ALPHA and _below(f["rho_upper"], cap),
                "p_holm": f["p_holm"], "rho_upper": f["rho_upper"], "cap": cap}
    drifting = {k: f["p_drift"] for k, f in families.items() if f["p_drift"] < ALPHA}
    return {"P1": fam("gpt-oss:120b", 0.10), "P2": fam("qwen3.5:35b", 0.30),
            "P3": fam("claude-opus-4-8", 0.30),
            "P4": {"holds": not drifting, "families_with_drift": drifting}}


def audit(root: str = ROOT, workers: int = 4, permutations: int = PERMUTATIONS) -> Dict:
    rows, paths = load(root)
    seqs, dropped = dedupe(rows)
    obs = observed(seqs)
    keys, perms = permute(seqs, workers, permutations)
    col = {k: i for i, k in enumerate(keys)}
    expected_r = {k: obs[k]["expected_repeats"] for k in keys}

    def null_of(ks, which):
        idx = [col[k] for k in ks]
        if which == "excess":
            base = sum(expected_r[k] for k in ks)
            return [sum(row[i][0] for i in idx) - base for row in perms]
        j = {"drift": 1, "grouped": 2}[which]
        return [sum(row[i][j] for i in idx) for row in perms]

    by_source, flagged = [], defaultdict(list)
    for k in sorted(obs):
        o = obs[k]
        rec = {"family": k[0], "source": k[1], **{x: o[x] for x in ("sequences", "informative", "draws")},
               "excess_repeats": _excess(o),
               "rho_hat": _excess(o) / o["room"] if o["room"] > 0 else None}
        if k in col:
            ex, dr, gr = null_of([k], "excess"), null_of([k], "drift"), null_of([k], "grouped")
            rec.update({"p_persistence": _upper_p(rec["excess_repeats"], ex),
                        "drift": o["drift"], "drift_null_mean": sum(dr) / len(dr),
                        "p_drift": _upper_p(o["drift"], dr),
                        "grouped": o["grouped"], "grouped_null_mean": sum(gr) / len(gr),
                        "p_grouped": _upper_p(o["grouped"], gr)})
            if rec["p_grouped"] < GROUPED_FLAG:
                flagged[k[0]].append(k[1])
        by_source.append(rec)

    families, raw_p = {}, {}
    for fam in sorted({k[0] for k in obs}):
        ks = [k for k in keys if k[0] == fam]
        o = _sum([obs[k] for k in obs if k[0] == fam])
        t = _excess(o)
        ex, dr = null_of(ks, "excess"), null_of(ks, "drift")
        c95 = sorted(ex)[math.ceil(0.95 * len(ex)) - 1]
        sims = simulate(seqs, fam, workers)
        f = {**{x: o[x] for x in ("sequences", "informative", "draws")},
             "excess_repeats": t, "rho_hat": t / o["room"] if o["room"] > 0 else None,
             "p": _upper_p(t, ex), "null_p95": c95,
             "drift": o["drift"], "drift_null_mean": sum(dr) / len(dr), "p_drift": _upper_p(o["drift"], dr),
             "rho_upper": rho_upper(t, sims),
             "power": {str(r): sum(1 for x in sims[GRID.index(r)] if x > c95) / DATASETS for r in POWER_AT},
             "share_at_or_below_observed": {str(GRID[i]): sum(1 for x in s if x <= t) / DATASETS
                                            for i, s in enumerate(sims)}}
        if flagged.get(fam):
            keep = [k for k in ks if k[1] not in flagged[fam]]
            o2 = _sum([obs[k] for k in obs if k[0] == fam and k[1] not in flagged[fam]])
            f["without_flagged"] = {"excluded": flagged[fam], "excess_repeats": _excess(o2),
                                    "rho_hat": _excess(o2) / o2["room"] if o2["room"] > 0 else None,
                                    "p": _upper_p(_excess(o2), null_of(keep, "excess")) if keep else None}
        families[fam] = f
        raw_p[fam] = f["p"]
    for fam, p in holm(raw_p).items():
        families[fam]["p_holm"] = p
    return {"plan": PLAN, "caches": paths,
            "settings": {"permutations": permutations, "chunks": CHUNKS, "perm_seed": PERM_SEED,
                         "grid": [GRID[0], GRID[-1], len(GRID)], "datasets": DATASETS,
                         "sim_seed": SIM_SEED, "alpha": ALPHA, "grouped_flag": GROUPED_FLAG},
            "dedupe": {"read": len(rows), "dropped": dropped, "kept": len(seqs)},
            "families": families, "by_source": by_source,
            "predictions": score(families)}


# --------------------------------------------------------------------------
# tables and checks


def _f(x, fmt="%.4f"):
    return "–" if x is None else fmt % x


def _bound(b: Dict) -> str:
    return {"bound": lambda: "%.2f" % b["value"], "above_grid": lambda: "> 0.50",
            "below_grid": lambda: "< 0 (below the grid)"}[b["kind"]]()


def render(record: Dict) -> str:
    fams, p = record["families"], record["predictions"]
    out = ["**Table 1 — the predictions, scored as registered.**\n",
           "| prediction | held? | the numbers it turned on |", "|---|---|---|"]
    for key, label in (("P1", "gpt-oss:120b: Holm p > 0.05 and `ρ_upper` < 0.10"),
                       ("P2", "qwen3.5:35b: Holm p > 0.05 and `ρ_upper` < 0.30"),
                       ("P3", "claude-opus-4-8: Holm p > 0.05 and `ρ_upper` < 0.30")):
        x = p[key]
        nums = ("Holm p %s, `ρ_upper` %s" % (_f(x["p_holm"]), _bound(x["rho_upper"]))
                if "p_holm" in x else x.get("reason", ""))
        out.append("| %s: %s | **%s** | %s |" % (key, label, "yes" if x["holds"] else "no", nums))
    out.append("| P4: no family drifts at p < 0.05 | **%s** | drift p %s |" % (
        "yes" if p["P4"]["holds"] else "no",
        ", ".join("%s %s" % (k, _f(f["p_drift"])) for k, f in sorted(fams.items()))))
    out += ["", "**Table 2 — each model's draws.** Sequences after removing duplicates; those "
            "with more than one answer (informative); the excess of adjacent repeats over their "
            "expectation given each sequence's counts; `ρ̂`; the one-sided permutation p-value, "
            "raw and Holm-adjusted; the simulated upper bound on persistence; and the power "
            "against `ρ` = 0.05, 0.1 and 0.3.\n",
            "| model | sequences | informative | draws | excess repeats | `ρ̂` | p | Holm p | "
            "`ρ_upper` | power 0.05 | power 0.1 | power 0.3 | drift p |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for name, f in sorted(fams.items()):
        out.append("| %s | %d | %d | %d | %+.2f | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            name, f["sequences"], f["informative"], f["draws"], f["excess_repeats"],
            _f(f["rho_hat"], "%+.4f"), _f(f["p"]), _f(f["p_holm"]), _bound(f["rho_upper"]),
            _f(f["power"]["0.05"], "%.3f"), _f(f["power"]["0.1"], "%.3f"),
            _f(f["power"]["0.3"], "%.3f"), _f(f["p_drift"])))
    out += ["", "**Table 3 — by source, as a description.** The same quantities for each "
            "experiment's cache, and the diagnostic for sequences rebuilt from a distribution: "
            "fully grouped informative sequences against their mean under permutation.\n",
            "| model | source | sequences | informative | excess repeats | `ρ̂` | p | drift p | "
            "grouped | grouped, null mean | grouped p |",
            "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in record["by_source"]:
        out.append("| %s | %s | %d | %d | %+.2f | %s | %s | %s | %s | %s | %s |" % (
            r["family"], r["source"], r["sequences"], r["informative"], r["excess_repeats"],
            _f(r["rho_hat"], "%+.4f"), _f(r.get("p_persistence")), _f(r.get("p_drift")),
            _f(r.get("grouped"), "%d"), _f(r.get("grouped_null_mean"), "%.2f"),
            _f(r.get("p_grouped"))))
    d = record["dedupe"]
    out += ["", "Sequences read: %d; dropped as duplicates of a longer or equal sequence: %d; "
            "kept: %d." % (d["read"], d["dropped"], d["kept"])]
    flagged = {k: f["without_flagged"] for k, f in fams.items() if "without_flagged" in f}
    if flagged:
        out += ["", "**Table 4 — without the sources the diagnostic flags.**\n",
                "| model | excluded | excess repeats | `ρ̂` | p |", "|---|---|---|---|---|"]
        for k, w in sorted(flagged.items()):
            out.append("| %s | %s | %+.2f | %s | %s |" % (k, ", ".join(w["excluded"]),
                       w["excess_repeats"], _f(w["rho_hat"], "%+.4f"), _f(w["p"])))
    return "\n".join(out) + "\n"


def check(root: str = ROOT) -> List[str]:
    """Problems with the saved record against the caches and the scoring."""
    problems = []
    with open(os.path.join(root, RECORD), encoding="utf-8") as fh:
        record = json.load(fh)
    rows, paths = load(root)
    seqs, dropped = dedupe(rows)
    if record["caches"] != paths:
        problems.append("the caches read differ")
    if record["dedupe"] != {"read": len(rows), "dropped": dropped, "kept": len(seqs)}:
        problems.append("dedupe counts differ")
    obs = observed(seqs)
    saved = {(r["family"], r["source"]): r for r in record["by_source"]}
    if set(saved) != set(obs):
        problems.append("the (model, source) groups differ")
    for k, o in obs.items():
        r = saved.get(k)
        if r is None:
            continue
        for field, value in (("sequences", o["sequences"]), ("informative", o["informative"]),
                             ("draws", o["draws"]), ("excess_repeats", _excess(o))):
            if abs(r[field] - value) > 1e-9:
                problems.append("%s/%s %s differs" % (k[0], k[1], field))
        if "drift" in r and r["drift"] != o["drift"]:
            problems.append("%s/%s drift differs" % k)
        if "grouped" in r and r["grouped"] != o["grouped"]:
            problems.append("%s/%s grouped differs" % k)
    for fam, f in record["families"].items():
        o = _sum([obs[k] for k in obs if k[0] == fam])
        if abs(f["excess_repeats"] - _excess(o)) > 1e-9 or f["informative"] != o["informative"]:
            problems.append("%s family totals differ" % fam)
    if json.loads(json.dumps(score(record["families"]))) != record["predictions"]:
        problems.append("predictions differ from score(families)")
    note = os.path.join(root, NOTE)
    if os.path.exists(note):
        with open(note, encoding="utf-8") as fh:
            text = fh.read()
        i, j = text.index(START) + len(START), text.index(END)
        if text[i:j] != "\n" + render(record):
            problems.append("the note's tables differ from the record")
    return problems


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--out", help="run the audit and write the record here")
    mode.add_argument("--write-tables", action="store_true")
    mode.add_argument("--check", action="store_true")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 2))
    args = ap.parse_args()
    if args.out:
        record = audit(ROOT, args.workers)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(json.dumps(record, indent=1, sort_keys=True) + "\n")
        print("wrote %s" % args.out)
        return 0
    if args.write_tables:
        with open(os.path.join(ROOT, RECORD), encoding="utf-8") as fh:
            tables = render(json.load(fh))
        path = os.path.join(ROOT, NOTE)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        i, j = text.index(START) + len(START), text.index(END)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text[:i] + "\n" + tables + text[j:])
        print("wrote tables into %s" % NOTE)
        return 0
    problems = check(ROOT)
    if problems:
        print("audit_draw_dependence: " + "; ".join(problems))
        return 1
    print("audit_draw_dependence: record current against the caches; predictions rescored")
    return 0


if __name__ == "__main__":
    sys.exit(main())
