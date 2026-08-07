#!/usr/bin/env python3
"""Is there any outcome variation left at the length the fluent register lives at?

[Problem 15](../../theory/open-problems.md) says `Phi` has almost no belief
component on this instrument, and that observed agreement climbs toward its
ceiling with message length: +0.203 per 100 words across E-002c's ladder, which
tops out at 182 words. The fluent register's measured floor in this generator is
229-232 words. Nobody has ever measured the outcome variable out there, because
all three experiments in the E-001 line voided during composition and the sweep
never ran.

This runs it, on messages that ALREADY EXIST on disk, so nothing is composed and
no instruction is involved:

  - three fluent cell-A messages from the void run of 2026-08-04. Each passed
    BOTH blind register raters and failed only the word band, which is a
    constraint no successor is obliged to inherit.
  - three terse cell-C messages from floor-by-register.json.

One number decides the line. If observed agreement is at ceiling in both
registers, there is no experiment on this probe measure at any register, and the
successor is a harder frame rather than a different prompt.

DRAWS ONLY. No elicitation, so no `Phi` is computed here. That is deliberate:
saturation kills the design on its own, and the belief half costs another 2000
calls to measure something that would not matter if this stage comes back at
ceiling. Fail fast, in the stage that is cheap.

INSTRUMENT DATA. E-001c is void and closed; nothing here can revive it, and no
hypothesis is touched.

    python3 headroom_check.py --draws 10
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

from noophorics.probes import ProbeMeasure  # noqa: E402
from noophorics.divergence import (agreement_rate, mean_divergence,  # noqa: E402
                                   to_distribution)


def mode_of(rows):
    """Copied in shape from E-002c's runner, ties broken by label sort order.

    Not imported, because it lives in that runner rather than in the library --
    which is itself the drift hazard DEFECT-001 records. Written out here so the
    tie rule is visible rather than assumed.
    """
    return [max(sorted(to_distribution(row)), key=lambda k: to_distribution(row)[k])
            for row in rows]
from noophorics.ollama_agent import OllamaAgent, ollama_available  # noqa: E402

VOID_RUN = os.path.join(HERE, "results", "E-001c-20260804T094831Z.json")
FLOOR = os.path.join(HERE, "floor-by-register.json")
PROBES = os.path.join(REPO, "experiments", "E-001-fluency-cost", "probes.json")
SPEC = os.path.join(REPO, "experiments", "E-001-fluency-cost", "source-spec.md")


AXES = {"A": ("fluent", "declarative"), "B": ("fluent", "contrastive"),
        "C": ("terse", "declarative"), "D": ("terse", "contrastive")}


def pick_messages(k: int) -> list:
    """Deterministic, so the selection is not a degree of freedom.

    Fluent: cell-A messages the two blind raters BOTH called prose, shortest
    first -- the ones closest to the band, which is the least favourable choice
    for the saturation hypothesis and therefore the right one.
    Terse: cell-C, longest first, for the same reason in the other direction.
    """
    void = json.load(open(VOID_RUN, encoding="utf-8"))
    fluent = [r for r in void["rejected"]["A"]
              if all(v == "A" for v in r["verdicts"])]
    fluent.sort(key=lambda r: r["words"])
    floor = json.load(open(FLOOR, encoding="utf-8"))
    terse = sorted(floor["cells"]["C"], key=lambda r: -r["words"])
    out = []
    for i, r in enumerate(fluent[:k]):
        out.append({"id": "fluent%d" % i, "register": "fluent",
                    "words": r["words"], "text": r["text"]})
    for i, r in enumerate(terse[:k]):
        out.append({"id": "terse%d" % i, "register": "terse",
                    "words": r["words"], "text": r["text"]})
    return out


def pick_all_cells(k: int) -> list:
    """All four cells, from the floor measurement, longest first.

    The six-message run covered A and C only, and its divergence rate rested on
    eleven events. This widens it to the whole 2x2 so the contrastiveness axis is
    measured rather than assumed, and so the rate a successor design would be
    costed against has more than eleven events under it.

    These messages carry NO register verdicts -- floor_by_register.py composed
    them to measure length and did not rate them. So this arm establishes what
    the probe measure does at these lengths; it does not establish that cell B
    reads as fluent prose. Where the two arms disagree, the rated one wins.
    """
    floor = json.load(open(FLOOR, encoding="utf-8"))
    out = []
    for cell in sorted(floor["cells"]):
        rows = sorted(floor["cells"][cell], key=lambda r: -r["words"])[:k]
        for i, r in enumerate(rows):
            out.append({"id": "%s%d" % (cell.lower(), i),
                        "register": AXES[cell][0], "selection": AXES[cell][1],
                        "cell": cell, "rated": False,
                        "words": r["words"], "text": r["text"]})
    return out


def reuse_sender(path: str):
    """The sender's draws from a previous run of this script, if compatible.

    Same model, same spec, same probe measure, same draw count -- so re-drawing
    would only add sampling noise between the two batches on a party that is not
    what either batch is about. Reused rather than recomputed, and the run
    records that it did.
    """
    if not os.path.exists(path):
        return None
    prev = json.load(open(path, encoding="utf-8"))
    s = prev.get("parties", {}).get("sender")
    if not s or prev.get("draws") is None:
        return None
    return {"modes": s["modes"], "margins": s["margins"],
            "draws": prev["draws"], "measure": prev.get("probe_measure")}


def checkpoint(rec: dict, path: str) -> None:
    """Write the record so far, atomically, and never take the run down with it.

    The qwen run of 2026-08-06 died on its seventeenth hour because a single
    incremental write returned EPERM -- a transient macOS refusal on a file that
    was writable a second earlier and a second later. It had just finished a
    message; that message never reached the file, and the two after it were
    never drawn. A checkpoint that kills the run when it fails is worse than no
    checkpoint at all.

    Temp file plus rename, so a crash mid-write cannot leave a truncated record
    either.
    """
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, indent=1, sort_keys=True)
        os.replace(tmp, path)
    except OSError as exc:
        print("  ! checkpoint failed (%s: %s) -- continuing; the run is worth "
              "more than the snapshot" % (type(exc).__name__, exc), flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--draws", type=int, default=10)
    ap.add_argument("--per-register", type=int, default=3)
    ap.add_argument("--all-cells", action="store_true",
                    help="all four cells from floor-by-register.json instead of "
                         "the two rated ones. Widens the divergence rate past "
                         "the eleven events the six-message run rested on.")
    ap.add_argument("--reuse-sender", default=None,
                    help="a previous output file whose sender draws to reuse. "
                         "Refused unless model, measure and n match.")
    ap.add_argument("--model", default="gpt-oss:120b")
    ap.add_argument("--out", default=os.path.join(HERE, "headroom.json"))
    args = ap.parse_args()

    if not ollama_available():
        print("ollama is not reachable", file=sys.stderr)
        return 2

    measure = ProbeMeasure.from_dict(json.load(open(PROBES, encoding="utf-8")))
    spec = open(SPEC, encoding="utf-8").read()
    msgs = (pick_all_cells(args.per_register) if args.all_cells
            else pick_messages(args.per_register))

    print("headroom check: %s, %d probes, n=%d draws%s"
          % (measure.qualified_id, len(measure), args.draws,
             "  [all four cells]" if args.all_cells else ""))
    print("messages: %s\n" % ", ".join("%s(%dw)" % (m["id"], m["words"]) for m in msgs))

    rec = {
        "purpose": ("outcome variation at the fluent register's operating "
                    "length, on messages already on disk"),
        "not_experimental_data": True,
        "problem": "theory/open-problems.md#15",
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": args.model, "draws": args.draws,
        "probe_measure": measure.qualified_id,
        "messages": [{k: v for k, v in m.items() if k != "text"} for m in msgs],
        "parties": {},
    }

    def draw(name: str, context: str) -> dict:
        agent = OllamaAgent(name, context=context, model=args.model,
                            think="medium", temperature=0.7)
        raw = []
        for i, probe in enumerate(measure):
            raw.append(agent.answer_samples(probe, args.draws))
            print("  %-9s %2d/%d" % (name, i + 1, len(measure)), end="\r", flush=True)
        modes = mode_of(raw)
        # Margins recorded because Problem 14 is open: a modal answer whose
        # lead is one draw is not the same observable as a unanimous one, and
        # a saturation claim resting on coin-flips would be worth nothing.
        margins = []
        for col in raw:
            counts = sorted((col.count(a) for a in set(col)), reverse=True)
            margins.append(counts[0] - (counts[1] if len(counts) > 1 else 0))
        print("  %-9s done, %d probes, median margin %d/%d"
              % (name, len(measure), statistics.median(margins), args.draws))
        return {"raw": raw, "modes": modes, "margins": margins,
                "dists": [to_distribution(c) for c in raw]}

    prev = reuse_sender(args.reuse_sender) if args.reuse_sender else None
    if prev and prev["draws"] == args.draws and prev["measure"] == measure.qualified_id:
        print("  sender    reused from %s (same model, spec, measure and n)"
              % os.path.basename(args.reuse_sender))
        # agreement_rate reads modal answers off distributions, so a point mass
        # on the recorded mode reproduces it exactly. Only the modes were
        # persisted; the raw draws were not, and inventing a spread would be
        # worse than admitting the point mass.
        sender = {"modes": prev["modes"], "margins": prev["margins"],
                  "dists": [{m: 1.0} for m in prev["modes"]]}
        rec["sender_reused_from"] = os.path.basename(args.reuse_sender)
    elif args.reuse_sender and prev:
        raise SystemExit("refusing to reuse a sender drawn at n=%s on %s against "
                         "n=%d on %s" % (prev["draws"], prev["measure"],
                                         args.draws, measure.qualified_id))
    else:
        sender = draw("sender", spec)
    rec["parties"]["sender"] = {"modes": sender["modes"],
                                "margins": sender["margins"],
                                "raw": sender.get("raw")}
    checkpoint(rec, args.out)

    for m in msgs:
        r = draw(m["id"], m["text"])
        a_hat = agreement_rate(sender["dists"], r["dists"], measure.weights)
        # Reported beside the agreement rate, not instead of it. The agreement
        # rate is a modal statistic and Problem 14 governs it; mean divergence
        # reads the whole distribution and does not need a mode at all. Whether
        # the two saturate together is the open question.
        # Refused when the sender was reused: only its modes were persisted, so
        # its "distributions" are point masses, and a Jensen-Shannon divergence
        # against a point mass measures the reconstruction rather than the party.
        d_post = (None if rec.get("sender_reused_from")
                  else mean_divergence(sender["dists"], r["dists"], measure.weights))
        diverged = [p.id for p, s, o in zip(measure, sender["modes"], r["modes"])
                    if s != o]
        rec["parties"][m["id"]] = {
            "register": m["register"], "words": m["words"],
            # Copied through because the per-cell summary groups on them and
            # silently found nothing when they were left behind -- the table
            # printed empty rather than wrong, which is the friendlier failure
            # but still a failure.
            "cell": m.get("cell"), "selection": m.get("selection"),
            # The raw draws, not only the modes. The first two runs persisted
            # modes and margins and threw the draws away, and the very next
            # question -- whether Jensen-Shannon divergence over the full
            # distributions saturates where the modal agreement rate does --
            # could not be answered without re-running 4080 calls. A summary
            # statistic is a decision about which later questions are askable.
            "raw": r["raw"],
            "agreement_observed": a_hat,
            "mean_divergence": d_post,
            "diverged_probes": diverged,
            "diverged_count": len(diverged),
            "modes": r["modes"], "margins": r["margins"],
        }
        print("    -> %s  A_hat = %.3f   JSD = %s   diverged %d of %d"
              % (m["id"], a_hat, ("%.4f" % d_post) if d_post is not None else "n/a",
                 len(diverged), len(measure)))
        checkpoint(rec, args.out)

    done = [v for v in rec["parties"].values()
            if isinstance(v, dict) and "agreement_observed" in v]
    if args.all_cells:
        print("\ncell  register/selection      n  mean A_hat   diverged of %d" % len(measure))
        for cell in sorted(AXES):
            g = [v for v in done if v.get("cell") == cell]
            if g:
                print("  %s   %-22s %d   %.3f        %s"
                      % (cell, "/".join(AXES[cell]), len(g),
                         statistics.mean(v["agreement_observed"] for v in g),
                         ", ".join(str(v["diverged_count"]) for v in g)))
    print("\nregister   n  mean A_hat   diverged probes of %d" % len(measure))
    for reg in ("fluent", "terse"):
        g = [v for v in done if v.get("register") == reg]
        if g:
            print("  %-8s %d   %.3f        %s"
                  % (reg, len(g), statistics.mean(v["agreement_observed"] for v in g),
                     ", ".join(str(v["diverged_count"]) for v in g)))
    events = sum(v["diverged_count"] for v in done)
    print("\ndivergence events: %d over %d probe-message pairs"
          % (events, len(done) * len(measure)))
    print("\nE-002c's outcome-variation gate wanted at least 3 diverged probes.")
    print("wrote %s" % args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
