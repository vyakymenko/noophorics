#!/usr/bin/env python3
"""Does RIVERSIDE-30 have headroom at the operating point?

[INSTRUMENT-LIMITS](../INSTRUMENT-LIMITS.md) concluded that `RIVERSIDE-30` is the
measure E-003 and E-007 should use: 25 of its 30 probes are independent against
MERIDIAN's nine of thirty-odd, and it is the only measure here whose keys were
adjudicated by readers who did not write them. That recommendation was published
on independence alone.

Independence is worth nothing if the measure saturates. `MERIDIAN-34` is
independent enough and saturates at 230 words, which is why `MERIDIAN-IX32`
exists. Nobody has ever run `RIVERSIDE-30` against a brief -- E-004 gave both
models the full specification, where they score 0.967 and 1.000, which is the
sender condition and says nothing about transfer.

    python3 headroom_riverside.py --compose     # write the briefs, then stop
    python3 headroom_riverside.py --draws 10    # sender + receivers

INSTRUMENT DATA. No hypothesis in `theory/` is touched.
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

from noophorics.probes import ProbeMeasure                      # noqa: E402
from noophorics.divergence import to_distribution               # noqa: E402
from noophorics.ollama_agent import OllamaAgent, ollama_available  # noqa: E402

SPEC = os.path.join(HERE, "source-spec.md")
PROBES = os.path.join(HERE, "probes.json")
BRIEFS = os.path.join(HERE, "briefs.json")

# The same budget every message in this programme has been measured at, so the
# number is comparable with MERIDIAN's. Not chosen for this run.
TARGET_WORDS = 230
N_BRIEFS = 3

COMPOSE_PROMPT = (
    "Write a briefing note of about %d words for a colleague who must apply "
    "these rules and will not see the specification. Write only the briefing "
    "note."
)


def mode_of(rows):
    return [max(sorted(to_distribution(r)), key=lambda k: to_distribution(r)[k])
            for r in rows]


def margins_of(rows):
    out = []
    for col in rows:
        c = sorted((col.count(a) for a in set(col)), reverse=True)
        out.append(c[0] - (c[1] if len(c) > 1 else 0))
    return out


def compose(model: str, n: int) -> list:
    """Composition is separated from measurement on purpose.

    E-001 died because the sender refused to compose at roughly nine attempts in
    ten, and the refusal was silent, asymmetric and shaped like a result. Writing
    the briefs to disk first means a refusal is visible as a missing file rather
    than as a short run.
    """
    spec = open(SPEC, encoding="utf-8").read()
    # context=spec, matching how E-001c's floor_by_register.py composed: the
    # specification is the composer's context, and the prompt is the instruction.
    agent = OllamaAgent("composer", spec, model=model,
                        think="medium", temperature=0.7)
    out = []
    for i in range(n):
        text = agent.compose(COMPOSE_PROMPT % TARGET_WORDS, seed=i)
        words = len(text.split())
        print("  brief %d: %d words" % (i, words), flush=True)
        out.append({"id": "b%d" % i, "words": words, "text": text})
    json.dump({"model": model, "target_words": TARGET_WORDS, "briefs": out},
              open(BRIEFS, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--draws", type=int, default=10)
    ap.add_argument("--model", default="gpt-oss:120b")
    ap.add_argument("--compose", action="store_true")
    ap.add_argument("--out", default=os.path.join(HERE, "headroom.json"))
    args = ap.parse_args()

    if not ollama_available():
        print("ollama is not reachable", file=sys.stderr)
        return 2

    if args.compose:
        compose(args.model, N_BRIEFS)
        print("wrote %s" % BRIEFS)
        return 0

    if not os.path.exists(BRIEFS):
        raise SystemExit("no briefs: run --compose first")
    briefs = json.load(open(BRIEFS, encoding="utf-8"))["briefs"]
    measure = ProbeMeasure.from_dict(json.load(open(PROBES, encoding="utf-8")))
    spec = open(SPEC, encoding="utf-8").read()

    rec = {
        "purpose": "does RIVERSIDE-30 have outcome variation at 230 words?",
        "not_experimental_data": True,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": args.model, "draws": args.draws,
        "probe_measure": measure.qualified_id,
        "target_words": TARGET_WORDS,
        "briefs": [{"id": b["id"], "words": b["words"]} for b in briefs],
        "parties": {},
    }
    print("RIVERSIDE-30 headroom: %s, %d probes, n=%d"
          % (measure.qualified_id, len(measure), args.draws))

    def draw(name, context):
        agent = OllamaAgent(name, context=context, model=args.model,
                            think="medium", temperature=0.7)
        raw = []
        for i, probe in enumerate(measure):
            raw.append(agent.answer_samples(probe, args.draws))
            print("  %-8s %2d/%d" % (name, i + 1, len(measure)), end="\r", flush=True)
        m = margins_of(raw)
        print("  %-8s done, median margin %d/%d" % (name, statistics.median(m), args.draws))
        return {"raw": raw, "modes": mode_of(raw), "margins": m}

    keys = [p.key for p in measure]
    ids = [p.id for p in measure]
    rec["keys"], rec["probe_ids"] = keys, ids

    sender = draw("sender", spec)
    acc = sum(1 for a, k in zip(sender["modes"], keys) if a == k) / len(keys)
    print("    sender accuracy against the key: %.3f" % acc)
    rec["parties"]["sender"] = sender
    rec["sender_accuracy"] = acc
    json.dump(rec, open(args.out, "w", encoding="utf-8"), indent=1, sort_keys=True)

    for b in briefs:
        r = draw(b["id"], b["text"])
        diverged = [i for i, s, o in zip(ids, sender["modes"], r["modes"]) if s != o]
        r["words"] = b["words"]
        r["diverged_probes"] = diverged
        r["diverged_count"] = len(diverged)
        r["agreement_observed"] = 1 - len(diverged) / len(ids)
        rec["parties"][b["id"]] = r
        print("    -> %s  diverged %d of %d   agreement %.3f"
              % (b["id"], len(diverged), len(ids), r["agreement_observed"]))
        json.dump(rec, open(args.out, "w", encoding="utf-8"), indent=1, sort_keys=True)

    got = [v["diverged_count"] for k, v in rec["parties"].items() if k != "sender"]
    print("\nmean diverged per message: %.2f   (E-002c's gate is 3)"
          % statistics.mean(got))
    print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
