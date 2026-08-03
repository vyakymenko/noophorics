#!/usr/bin/env python3
"""Blind rating: did the register manipulation survive being pinned to a length?

E-001c cannot be registered until this question is answered. Its
[feasibility check](FEASIBILITY.md) established cost parity and showed the two
registers still differ on structural markers -- sentence length, connective
density -- and then said of those markers, correctly:

> These are proxies, not a validity check. They distinguish prose from notes;
> they do not establish that the *intended* style distinction is what survived.
> Establishing that needs independent blind rating, and it is a precondition of
> E-001c's registration.

This is that rating. It is an **instrument check**, not an experiment: no
hypothesis is tested and none may be read off it.

## What is being asked

The two register instructions differ in one thing. Fluent cells are told to
write *"considered, connected prose ... with the relationships between points
spelled out in the words"*; terse cells are told to write *"bare declarative
statements, one item per line, no bridging or linking phrases"*. The rating
question operationalises that and nothing else.

## How the blinding works

- Raters see **two passages and nothing else** -- no spec, no prompts, no cell
  labels, no mention of an experiment, no indication that other pairs exist.
- Every cross pair of one fluent and one terse message is rated, and **which
  one is shown first is randomised per pair** and recorded, so position bias is
  measurable rather than assumed away.
- Each rating is an independent process call. Nothing carries between pairs.
- **No rater is the composer.** The messages come from `gpt-oss:120b`; the
  raters are `codex` and `qwen3.5:35b`, and optionally `claude-opus-4-8`, which
  puts at least two different providers on the question. Cross-provider
  independence is the thing E-004's third arm was supposed to supply and this
  measure gets for free.

The rating prompt does state that one passage is of each kind. Without that the
forced choice is ill-posed. It does not say which, in what proportion, or that
anything is being tested.

## What the numbers mean

Accuracy against the true labels; chance is 0.5. The interval that governs is a
**bootstrap over messages, not over pairs** -- the design crosses every fluent
message with every terse one, so each message appears in eight pairs and 64
ratings rest on 16 independent units. An exact binomial interval over the pairs
would be too narrow, in exactly the direction that makes a weak separation look
established, so it is reported alongside and labelled. Agreement between raters is reported separately, because two raters who
agree with each other and not with the labels would mean the passages differ
reliably along *some* axis that is not the intended one -- which is a different
finding and a worse one.

## Whether the design can answer at all

Powered before running, because a rating that comes back ambiguous is worth
nothing and costs the same as one that does not. Simulating a rater that
recovers the separation reliably on a fraction `q` of messages and guesses on
the rest, and asking how often the cluster interval clears 0.5:

```
messages per side    q = 0.80    q = 0.90    q = 1.00
        8              0.78        0.95        1.00
       12              0.97        0.99        1.00
```

Eight per side -- `k = 4` per cell -- is adequate if the separation is strong and
marginal if it is patchy. The structural markers say it is strong (fluent
sentences 1.77x longer, connectives 2.5x denser), so eight is the starting point
and `k = 6` is the remedy if the interval comes back straddling chance. Stating
that now means the remedy is not a decision made after seeing the answer.

    python3 blind_rating.py --raters codex,qwen3.5:35b
    python3 blind_rating.py --raters codex --limit 16      # a cheap smoke run
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from typing import Any, Dict, List

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "metrics"))

SEED = 20260803

QUESTION = """You are shown two short passages, PASSAGE 1 and PASSAGE 2. They \
describe the same subject and are about the same length.

One of them was written as connected prose: complete sentences that follow from \
one another, with the relationships between the points spelled out in words.

The other was written as bare declarative statements, with no bridging or \
linking phrases between them.

Which is the connected prose?

PASSAGE 1
---------
%s

PASSAGE 2
---------
%s

Answer with exactly one word: either "1" or "2"."""


# The absolute question, asked of one passage at a time.
#
# The forced choice below cannot answer the question this check exists for. It
# asks which of two passages is the connected prose, so a rater must name one
# even when neither is -- and it will name the wordier one, which correlates
# perfectly with the label. A perfect score therefore establishes only that the
# two registers are distinguishable, which the structural markers already said.
#
# Reading the messages is what showed it. Both registers produced a labelled
# list of ten rules; the fluent one writes each item as a complete sentence and
# the terse one abbreviates. Neither spells out the relationships *between*
# items, which is what the fluent instruction actually asked for.
#
# So each passage is also judged on its own, against the instruction's own
# words, with an option that lets the honest answer be "neither".
ABSOLUTE = """Read the passage below and classify how it is written.

A. CONNECTED PROSE -- complete sentences that follow from one another, where the
   relationships between the points are spelled out in words.
B. A LIST -- separate items stated one after another, with no wording that
   relates them to each other, whether or not the items are full sentences.

PASSAGE
-------
%s

Answer with exactly one letter: either "A" or "B"."""


def load_messages(path: str):
    """(fluent, terse) message texts, from a feasibility run that kept them."""
    with open(path, "r", encoding="utf-8") as fh:
        record = json.load(fh)
    sys.path.insert(0, os.path.join(ROOT, "experiments", "E-001b-fluency-factorial"))
    from prompts import CELL_AXES  # noqa: E402

    fluent, terse = [], []
    for target, summary in sorted(record["targets"].items()):
        for cell, items in sorted(summary["cells"].items()):
            for m in items:
                if "text" not in m:
                    raise SystemExit(
                        "%s has no message texts. It was written by a version of "
                        "feasibility.py that measured the messages and discarded "
                        "them; re-run that script to produce a file this can "
                        "rate." % path)
                row = {"cell": cell, "target": target, "seed": m.get("seed"),
                       "text": m["text"], "words": m.get("words")}
                (fluent if CELL_AXES[cell][0] == "fluent" else terse).append(row)
    return fluent, terse


def make_pairs(fluent, terse, limit: int = 0):
    rng = random.Random(SEED)
    pairs = []
    for i, f in enumerate(fluent):
        for j, t in enumerate(terse):
            first_is_fluent = rng.random() < 0.5
            pairs.append({
                "id": "F%d-T%d" % (i, j),
                "fluent_cell": f["cell"], "terse_cell": t["cell"],
                "first_is_fluent": first_is_fluent,
                "p1": f["text"] if first_is_fluent else t["text"],
                "p2": t["text"] if first_is_fluent else f["text"],
            })
    rng.shuffle(pairs)
    return pairs[:limit] if limit else pairs


def make_rater(name: str):
    """A rater with no context. The empty context is the blinding."""
    if name.startswith("codex"):
        from noophorics.codex_agent import CodexAgent
        return CodexAgent("rater", context="",
                          model=None if name == "codex" else name.split(":", 1)[1],
                          reasoning_effort="low")
    if name.startswith("claude"):
        from noophorics.agents import AnthropicAgent
        return AnthropicAgent(name, "", model=name)
    from noophorics.ollama_agent import OllamaAgent
    return OllamaAgent("rater", "", model=name, think="medium", temperature=0.7)


def ask(agent, pair) -> str:
    from noophorics.probes import Probe
    probe = Probe(id=pair["id"], prompt=QUESTION % (pair["p1"], pair["p2"]),
                  options=("1", "2"))
    return agent.answer_samples(probe, 1)[0]


def ask_absolute(agent, text: str) -> str:
    from noophorics.probes import Probe
    return agent.answer_samples(
        Probe(id="abs", prompt=ABSOLUTE % text, options=("A", "B")), 1)[0]


def cluster_ci(answers, fluent_n, terse_n, resamples: int = 20000):
    """Bootstrap over MESSAGES, because the pairs are not independent.

    The design crosses every fluent message with every terse one, so each
    message appears in `terse_n` (or `fluent_n`) pairs and the ratings are
    clustered by message. A binomial interval over the pairs treats 64
    observations as 64 independent trials when the design has 16 independent
    units, and it is therefore too narrow -- anticonservative in exactly the
    direction that would make a weak separation look established.

    Resampling the messages with replacement and recomputing accuracy over the
    pairs they induce respects the clustering. Both intervals are reported; this
    is the one that governs.
    """
    import random as _r
    by_pair = {a["pair"]: a["correct"] for a in answers}
    rng = _r.Random(SEED + 7)
    accs = []
    for _ in range(resamples):
        fi = [rng.randrange(fluent_n) for _ in range(fluent_n)]
        ti = [rng.randrange(terse_n) for _ in range(terse_n)]
        hits = [by_pair["F%d-T%d" % (i, j)] for i in fi for j in ti
                if "F%d-T%d" % (i, j) in by_pair]
        if hits:
            accs.append(sum(hits) / len(hits))
    accs.sort()
    if not accs:
        return (0.0, 1.0)
    return (accs[int(0.025 * len(accs))], accs[int(0.975 * len(accs))])


def binom_ci(k: int, n: int):
    """Exact Clopper-Pearson, by bisection on the beta quantile. No SciPy here."""
    if n == 0:
        return (0.0, 1.0)
    from math import comb

    def cdf_ge(p, k, n):                       # P(X >= k) under Binom(n, p)
        return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k, n + 1))

    def solve(target, lo, hi, fn):
        for _ in range(80):
            mid = (lo + hi) / 2
            if fn(mid) < target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    low = 0.0 if k == 0 else solve(0.025, 0.0, 1.0, lambda p: cdf_ge(p, k, n))
    high = 1.0 if k == n else solve(0.975, 0.0, 1.0,
                                    lambda p: cdf_ge(p, k + 1, n))
    return (low, high)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--messages",
                    default=os.path.join(HERE, "feasibility-messages.json"))
    ap.add_argument("--raters", default="codex,qwen3.5:35b")
    ap.add_argument("--limit", type=int, default=0,
                    help="rate only the first N pairs; 0 = all")
    ap.add_argument("--out", default=os.path.join(HERE, "blind-rating.json"))
    ap.add_argument("--absolute-only", action="store_true",
                    help="skip the forced choice and run only the per-passage "
                         "judgment, which is the arm that can say the "
                         "manipulation failed")
    args = ap.parse_args()

    fluent, terse = load_messages(args.messages)
    pairs = make_pairs(fluent, terse, args.limit)
    print("  %d fluent x %d terse -> %d pairs rated" % (len(fluent), len(terse), len(pairs)))

    results: Dict[str, Any] = {}
    for name in ([] if args.absolute_only
                 else [r.strip() for r in args.raters.split(",") if r.strip()]):
        agent = make_rater(name)
        answers, correct, chose_first = [], 0, 0
        for n, pair in enumerate(pairs, 1):
            try:
                a = ask(agent, pair).strip()
            except Exception as exc:                       # noqa: BLE001
                a = "ERROR:%s" % type(exc).__name__
            picked_first = a == "1"
            right = picked_first == pair["first_is_fluent"]
            correct += bool(right and not a.startswith("ERROR"))
            chose_first += bool(picked_first)
            answers.append({"pair": pair["id"], "answer": a,
                            "first_is_fluent": pair["first_is_fluent"],
                            "correct": bool(right)})
            sys.stderr.write("\r  %-16s %d/%d  correct %d" % (name, n, len(pairs), correct))
            sys.stderr.flush()
        sys.stderr.write("\n")
        lo, hi = binom_ci(correct, len(pairs))
        clo, chi = cluster_ci(answers, len(fluent), len(terse))
        results[name] = {
            "n": len(pairs), "correct": correct,
            "independent_units": {"fluent": len(fluent), "terse": len(terse)},
            "accuracy": correct / len(pairs) if pairs else 0.0,
            "ci95_cluster_bootstrap": [clo, chi],
            "ci95_binomial_anticonservative": [lo, hi],
            "chose_first_rate": chose_first / len(pairs) if pairs else 0.0,
            "answers": answers,
        }
        print("  %-16s %d/%d = %.3f  cluster CI [%.3f, %.3f]  "
              "(binomial [%.3f, %.3f], too narrow)  chose-first %.2f"
              % (name, correct, len(pairs), results[name]["accuracy"],
                 clo, chi, lo, hi, results[name]["chose_first_rate"]))

    # The absolute pass: every message judged on its own, 16 calls per rater.
    # This is the one that can say the manipulation failed.
    for name in [r.strip() for r in args.raters.split(",") if r.strip()]:
        agent = make_rater(name)
        verdicts = {}
        for label, group in (("fluent", fluent), ("terse", terse)):
            got = []
            for n_i, m in enumerate(group, 1):
                try:
                    got.append(ask_absolute(agent, m["text"]).strip())
                except Exception as exc:                   # noqa: BLE001
                    got.append("ERROR:%s" % type(exc).__name__)
                sys.stderr.write("\r  %-16s absolute %s %d/%d" % (name, label, n_i, len(group)))
                sys.stderr.flush()
            verdicts[label] = got
        sys.stderr.write("\n")
        prose = {k: sum(1 for x in v if x == "A") for k, v in verdicts.items()}
        results.setdefault(name, {})["absolute"] = {"verdicts": verdicts,
                                                    "called_prose": prose}
        print("  %-16s called CONNECTED PROSE: fluent %d/%d, terse %d/%d"
              % (name, prose["fluent"], len(fluent), prose["terse"], len(terse)))

    names = [k for k in results if not k.startswith("_") and "answers" in results[k]]
    if len(names) >= 2:
        a, b = results[names[0]]["answers"], results[names[1]]["answers"]
        agree = sum(1 for x, y in zip(a, b) if x["answer"] == y["answer"])
        print("  agreement %s vs %s: %d/%d = %.3f"
              % (names[0], names[1], agree, len(a), agree / len(a)))
        results["_agreement"] = {"pair": names[:2], "agree": agree, "n": len(a)}

    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump({"seed": SEED, "question": QUESTION,
                   "composer": "gpt-oss:120b", "raters": results}, fh,
                  indent=1, sort_keys=True)
    print("  wrote %s" % args.out)
    print("\n  Instrument check. No hypothesis is tested here and none may be "
          "read off it.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
