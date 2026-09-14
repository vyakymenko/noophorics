#!/usr/bin/env python3
"""Prospective, stateless register instrument. No inference or hypothesis test.

The SHA-bound plan fixes the source, question, controls, raters and call budget.
Each attempted HTTP call has an atomic, immutable reservation before sending;
an interrupted reservation is missing evidence and is never retried on resume.
Only standard-library modules are used. --dry-run and --summarize are offline.
"""
from __future__ import annotations

import argparse
import ast
import base64
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import random
import sys
import tempfile
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "experiments/E-001c-fluency-length-controlled/floor-by-register-qwen.json"
PROMPT_SOURCE = "experiments/E-001c-fluency-length-controlled/blind_rating.py"
SOURCE_SHA = "cfbd5d776cec1bb430f0bb9ec82b5d1a08f2c0a22c5dff43520a7f1fb8f5d0f9"
ENDPOINT = "http://localhost:11434"
PROMPT_SHA = "44571477c1c92e7ce9526c707a88fc08eda3075fa87459871153f1f7cdcb6590"
VERDICT_FORMAT = {"type": "object", "properties": {"verdict": {
    "type": "string", "enum": ["A", "B"]}}, "required": ["verdict"],
    "additionalProperties": False}


class CheckError(ValueError):
    """The frozen protocol or its recorded evidence does not match."""


def require(ok, message):
    if not ok:
        raise CheckError(message)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def encoded(data):
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def atomic_json(path, value):
    """Replace one checkpoint only after its bytes have reached the filesystem."""
    path = Path(path)
    fd, temporary = tempfile.mkstemp(prefix=".checkpoint-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def absolute_question(path):
    """Read only a literal assignment, without executing the legacy module."""
    values = []
    for statement in ast.parse(Path(path).read_text(encoding="utf-8")).body:
        if isinstance(statement, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "ABSOLUTE"
                for target in statement.targets):
            values.append(ast.literal_eval(statement.value))
    require(len(values) == 1 and isinstance(values[0], str), "exactly one literal ABSOLUTE required")
    require(sha(values[0].encode()) == PROMPT_SHA, "ABSOLUTE question checksum changed")
    return values[0]


def digest(value):
    require(isinstance(value, str), "model digest must be a string")
    normalized = value.removeprefix("sha256:")
    require(len(normalized) == 64 and all(c in "0123456789abcdef" for c in normalized),
            "model digest must be a full SHA-256")
    return normalized


def load_protocol(plan_path, root=ROOT):
    """Validate all offline inputs before any service request or result write."""
    plan_path, root = Path(plan_path), Path(root)
    plan_bytes = plan_path.read_bytes()
    plan = json.loads(plan_bytes)
    require(plan.get("schema_version") == 1, "unsupported plan schema")
    source_spec, prompt_spec = plan["source"], plan["prompt"]
    require(source_spec["path"] == SOURCE and source_spec["sha256"] == SOURCE_SHA,
            "plan must bind the frozen qwen source")
    require(prompt_spec["path"] == PROMPT_SOURCE and prompt_spec["sha256"] == PROMPT_SHA,
            "plan must bind the original ABSOLUTE question")
    source_path, prompt_path = root / SOURCE, root / PROMPT_SOURCE
    source_bytes = source_path.read_bytes()
    require(sha(source_bytes) == SOURCE_SHA, "source file checksum mismatch")
    source = json.loads(source_bytes)
    require(prompt_spec["variable"] == "ABSOLUTE" and sha(prompt_path.read_bytes()) == prompt_spec["file_sha256"],
            "original prompt source checksum mismatch")
    question = absolute_question(prompt_path)
    require(source["model"] == source_spec["composer"] == "qwen3.5:35b", "composer mismatch")
    require(source["band"] == source_spec["band"] == [182, 231], "word band mismatch")
    require(source["n_per_cell"] == source_spec["n_per_cell"] == 12, "source cell size mismatch")
    require(set(source["cells"]) == {"A", "B", "C", "D"}, "source cells mismatch")
    rows = []
    for cell in "ABCD":
        require(len(source["cells"][cell]) == 12, "every source cell needs 12 rows")
        for index, original in enumerate(source["cells"][cell]):
            passage = original["text"]
            require(isinstance(passage, str) and bool(passage.strip()), "empty source passage")
            words = len(passage.split())
            in_band = 182 <= words <= 231
            require(type(original["words"]) is int and original["words"] == words,
                    f"{cell}/{index}: stored word count mismatch")
            require(type(original["in_band"]) is bool and original["in_band"] == in_band,
                    f"{cell}/{index}: stored band flag mismatch")
            rows.append({"id": f"source-{cell}-{index:02d}", "kind": "source", "cell": cell,
                         "source_index": index, "text": passage, "words": words,
                         "in_band": in_band, "expected": "A" if cell in "AB" else "B"})
    controls = plan["controls"]
    require(isinstance(controls, list) and len(controls) == 4, "exactly four calibration controls required")
    require({item["expected"] for item in controls} == {"A", "B"}, "controls must cover A and B")
    control_rows = []
    for control in controls:
        require(isinstance(control["id"], str) and control["id"].startswith("control-"),
                "control IDs must start with control-")
        require(isinstance(control["text"], str) and bool(control["text"].strip()), "empty control")
        control_rows.append(dict(control, kind="control"))
    require(len({c["id"] for c in control_rows}) == len(control_rows), "duplicate control ID")
    raters = plan["raters"]
    require([r["model"] for r in raters] == ["gpt-oss:120b", "llama3.3:70b"], "rater roster mismatch")
    require(raters[0].get("think") == "medium" and raters[1].get("think") is None,
            "think must be medium for gpt-oss and absent/null for llama")
    require(all(r.get("temperature") == 0.7 for r in raters), "rater temperature must be 0.7")
    require(source_spec["composer_digest"] is None, "historical composer digest was not recorded")
    require(all(r["model"] != source_spec["composer"] for r in raters), "composer cannot be a rater")
    all_digests = [digest(r["digest"]) for r in raters]
    require(len(set(all_digests)) == 2, "both raters must have distinct model digests")
    require(plan["expected_by_cell"] == {"A": "A", "B": "A", "C": "B", "D": "B"},
            "expected register mapping changed")
    execution = plan
    require(type(execution["seed"]) is int, "integer shuffle seed required")
    require(execution["timeout_seconds"] == 120, "timeout must be 120 seconds")
    require(execution["retries"] == 0, "exactly one attempt per item required")
    require(execution["max_requests"] == len(raters) * (len(rows) + len(controls)) == 104, "call budget mismatch")
    shuffled = list(rows)
    random.Random(execution["seed"]).shuffle(shuffled)
    schedule = []
    for rater in raters:
        for item in control_rows + shuffled:
            sequence = len(schedule)
            item_seed = int(sha(f'{execution["seed"]}:{rater["model"]}:{item["id"]}'.encode())[:8], 16)
            schedule.append({"sequence": sequence, "rater": rater, "item": item, "seed": item_seed})
    identity = {"plan_sha256": sha(plan_bytes), "source_sha256": sha(source_bytes),
                "script_sha256": sha(Path(__file__).read_bytes()), "prompt_sha256": sha(question.encode()),
                "prompt_source_sha256": sha(prompt_path.read_bytes()),
                "model_digests": {r["model"]: digest(r["digest"]) for r in raters},
                "composer": source_spec["composer"], "composer_digest": None}
    items = [{k: v for k, v in dict(row, text_sha256=sha(row["text"].encode())).items()
              if k != "text"} for row in control_rows + rows]
    return {"plan": plan, "question": question, "rows": rows, "controls": control_rows,
            "items": items,
            "schedule": schedule, "identity": identity}


def payload(protocol, call):
    """The rater sees only the exact one-passage question; no labels or history."""
    rater = call["rater"]
    body = {"model": rater["model"], "messages": [{"role": "user", "content":
            protocol["question"] % call["item"]["text"]}], "stream": False,
            "format": VERDICT_FORMAT, "options": {"temperature": rater["temperature"], "seed": call["seed"]}}
    if rater.get("think") is not None:
        body["think"] = rater["think"]
    return body


class HTTPTransport:
    def __init__(self, endpoint):
        self.endpoint = endpoint

    def __call__(self, method, path, body, timeout):
        request = urllib.request.Request(self.endpoint + path,
            data=body.encode("utf-8") if body is not None else None, method=method,
            headers={"Content-Type": "application/json"})
        try:
            response = urllib.request.urlopen(request, timeout=timeout)
        except urllib.error.HTTPError as error:
            response = error
        with response:
            raw = response.read()
            return {"status": response.status, "headers": list(response.headers.items()),
                    "body_base64": base64.b64encode(raw).decode("ascii"),
                    "body": raw.decode("utf-8", errors="replace"), "error": None}


def request_once(transport, method, path, body, timeout):
    try:
        return transport(method, path, body, timeout)
    except Exception as error:
        return {"status": None, "headers": [], "body_base64": "", "body": "",
                "error": {"type": type(error).__name__, "message": str(error)}}


def response_json(response):
    require(isinstance(response, dict), "missing raw HTTP response")
    raw = base64.b64decode(response["body_base64"], validate=True)
    require(raw.decode("utf-8", errors="replace") == response["body"], "raw response bytes/text mismatch")
    require(response.get("error") is None and response["status"] == 200, "HTTP or transport error")
    return json.loads(raw.decode("utf-8"))


def verdict(record):
    """Errors, incomplete generations and malformed outputs never mean B."""
    if record is None or record.get("state") != "complete":
        return None
    try:
        response = response_json(record["response"])
        require(isinstance(response, dict), "response must be an object")
        require(response.get("model") == record["rater"], "response model does not match the rater")
        require(response.get("done") is True, "generation not complete")
        require(not response.get("error"), "generation reports an error")
        message = response["message"]
        require(isinstance(message, dict), "message must be an object")
        require(message.get("role") == "assistant", "response is not an assistant message")
        parsed = json.loads(message["content"])
        require(isinstance(parsed, dict) and set(parsed) == {"verdict"}, "wrong verdict schema")
        require(parsed["verdict"] in ("A", "B"), "invalid verdict")
        return parsed["verdict"]
    except (CheckError, KeyError, TypeError, ValueError):
        return None


def verify_models(protocol, transport):
    response = request_once(transport, "GET", "/api/tags", None, 120)
    inventory = response_json(response)
    models = inventory["models"]
    for name, expected in protocol["identity"]["model_digests"].items():
        found = [model for model in models if model.get("name") == name]
        require(len(found) == 1 and digest(found[0]["digest"]) == expected, f"model digest mismatch: {name}")
    return response


def record_path(out, sequence):
    return Path(out) / "calls" / f"{sequence:04d}.json"


def load_records(protocol, out):
    records = {}
    expected = {f'{call["sequence"]:04d}.json': call for call in protocol["schedule"]}
    for path in sorted((Path(out) / "calls").glob("*")):
        # A hard crash can leave an unpublished atomic-write temporary. It is
        # not a final reservation and is never read as evidence or retried.
        if path.name.startswith(".checkpoint-"):
            continue
        require(path.name in expected, f"unexpected call artifact: {path.name}")
        call, record = expected[path.name], read_json(path)
        require(record["sequence"] == call["sequence"] and record["item_id"] == call["item"]["id"]
                and record["rater"] == call["rater"]["model"], "record identity mismatch")
        require(record["request"] == {"method": "POST", "path": "/api/chat", "body": encoded(payload(protocol, call))},
                "record request differs from frozen blinded payload")
        require(record.get("state") in ("reserved", "complete"), "invalid record state")
        require(record.get("state") != "complete" or isinstance(record.get("response"), dict), "missing raw response")
        records[call["sequence"]] = record
    # Records must be a prefix of the allowed schedule: a hole must not be retried.
    skipped = set()
    for rater in protocol["plan"]["raters"]:
        calls = [c for c in protocol["schedule"] if c["rater"] == rater]
        controls = [c for c in calls if c["item"]["kind"] == "control"]
        if all(c["sequence"] in records for c in controls) and not all(
                verdict(records[c["sequence"]]) == c["item"]["expected"] for c in controls):
            skipped.update(c["sequence"] for c in calls if c["item"]["kind"] == "source")
    permitted = [c["sequence"] for c in protocol["schedule"] if c["sequence"] not in skipped]
    require(sorted(records) == permitted[:len(records)], "call checkpoint has a gap or violates order")
    # A saved corpus call without successful prior controls is never admissible.
    for rater in protocol["plan"]["raters"]:
        calls = [c for c in protocol["schedule"] if c["rater"] == rater]
        controls = [c for c in calls if c["item"]["kind"] == "control"]
        if any(c["sequence"] in records for c in calls if c["item"]["kind"] == "source"):
            require(all(verdict(records.get(c["sequence"])) == c["item"]["expected"] for c in controls),
                    "corpus calls exist for an uncalibrated rater")
    return records


def summarize(protocol, records):
    answers, calibration = {}, {}
    for rater in protocol["plan"]["raters"]:
        name = rater["model"]
        calls = [c for c in protocol["schedule"] if c["rater"]["model"] == name]
        control_calls = [c for c in calls if c["item"]["kind"] == "control"]
        valid_controls = sum(verdict(records.get(c["sequence"])) is not None for c in control_calls)
        correct = sum(verdict(records.get(c["sequence"])) == c["item"]["expected"] for c in control_calls)
        all_attempted = all(c["sequence"] in records for c in control_calls)
        passed = correct == len(control_calls)
        calibration[name] = {"status": "passed" if passed else ("failed" if all_attempted else "incomplete"),
                             "planned": len(control_calls), "attempted": sum(c["sequence"] in records for c in control_calls),
                             "valid": valid_controls, "correct": correct}
        answers[name] = {c["item"]["id"]: verdict(records.get(c["sequence"])) if passed else None
                         for c in calls if c["item"]["kind"] == "source"}
    cells = {}
    all_calibrated = all(c["status"] == "passed" for c in calibration.values())
    names = [r["model"] for r in protocol["plan"]["raters"]]
    for cell in "ABCD":
        rows = [r for r in protocol["rows"] if r["cell"] == cell]
        both_valid = lambda row: all(answers[n][row["id"]] is not None for n in names)
        both_expected = lambda row: all(answers[n][row["id"]] == row["expected"] for n in names)
        cells[cell] = {"total": len(rows), "in_band": sum(r["in_band"] for r in rows),
                       "expected_verdict": "A" if cell in "AB" else "B",
                       "valid_ratings": {n: sum(answers[n][r["id"]] is not None for r in rows) for n in names},
                       "expected_register_by_rater": {n: sum(answers[n][r["id"]] == r["expected"] for r in rows) for n in names},
                       "both_valid": sum(both_valid(r) for r in rows),
                       "both_expected_register": sum(both_expected(r) for r in rows),
                       "observed_joint_acceptance": sum(r["in_band"] and both_expected(r) for r in rows) if all_calibrated else None,
                       "joint_acceptance": sum(r["in_band"] and both_expected(r) for r in rows)
                           if all_calibrated and all(both_valid(r) for r in rows) else None,
                       "joint_result_available": all_calibrated and all(both_valid(r) for r in rows),
                       "disagreement": sum(both_valid(r) and len({answers[n][r["id"]] for n in names}) > 1 for r in rows),
                       "missing_any_rating": sum(not both_valid(r) for r in rows)}
    expected_attempts = sum(len(protocol["controls"]) + (48 if calibration[n]["status"] == "passed" else 0) for n in names)
    all_valid = all(c["missing_any_rating"] == 0 for c in cells.values())
    finished = len(records) == expected_attempts and all(c["status"] != "incomplete" for c in calibration.values())
    return {"not_experimental_data": True, "analysis": "descriptive instrument counts only",
            "complete": finished, "usable": all_calibrated and all_valid and finished,
            "attempted_calls": len(records), "max_calls": protocol["plan"]["max_requests"],
            "invalid_or_indeterminate_attempts": sum(verdict(r) is None for r in records.values()),
            "calibration": calibration, "cells": cells}


def checked_results(protocol, out):
    manifest = read_json(Path(out) / "manifest.json")
    require(manifest.get("schema_version") == 1, "unsupported result schema")
    require(manifest["identity"] == protocol["identity"], "plan/source/script/model identity conflict")
    require(manifest["plan"] == protocol["plan"], "recorded plan differs from frozen plan")
    require(manifest["items"] == protocol["items"], "recorded item identities or text hashes differ")
    # Model evidence is checked offline as well as against live inventory on resume.
    verify_models(protocol, lambda *_: manifest["initial_model_inventory"])
    return load_records(protocol, out)


def run(protocol, out, *, resume=False, transport=None):
    out = Path(out)
    existed = out.exists()
    require(resume if existed else not resume, "existing output needs --resume; --resume requires existing output")
    if not existed:
        out.mkdir(parents=True)
    with (out / ".lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise CheckError("another process owns this result directory") from error
        records = checked_results(protocol, out) if resume else {}
        transport = transport or HTTPTransport(ENDPOINT)
        inventory = verify_models(protocol, transport)
        if not resume:
            (out / "calls").mkdir()
            atomic_json(out / "manifest.json", {"schema_version": 1, "started_at": now(),
                        "identity": protocol["identity"], "plan": protocol["plan"], "items": protocol["items"],
                        "initial_model_inventory": inventory})
        for call in protocol["schedule"]:
            sequence, item, name = call["sequence"], call["item"], call["rater"]["model"]
            if sequence in records:
                continue
            if item["kind"] == "source":
                controls = [c for c in protocol["schedule"] if c["rater"]["model"] == name and c["item"]["kind"] == "control"]
                if not all(verdict(records.get(c["sequence"])) == c["item"]["expected"] for c in controls):
                    continue
            require(len(records) < protocol["plan"]["max_requests"], "hard call budget exhausted")
            request = {"method": "POST", "path": "/api/chat", "body": encoded(payload(protocol, call))}
            record = {"sequence": sequence, "item_id": item["id"], "rater": name,
                      "state": "reserved", "reserved_at": now(), "request": request}
            path = record_path(out, sequence)
            require(not path.exists(), "refusing to overwrite an existing call")
            atomic_json(path, record)
            records[sequence] = record
            response = request_once(transport, request["method"], request["path"], request["body"], 120)
            record = dict(record, state="complete", completed_at=now(), response=response)
            atomic_json(path, record)
            records[sequence] = record
            atomic_json(out / "summary.json", summarize(protocol, records))
        summary = summarize(protocol, records)
        atomic_json(out / "summary.json", summary)
        return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=ROOT / "probes/qwen-register/plan.json")
    parser.add_argument("--out", type=Path)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument("--summarize", action="store_true")
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args(argv)
    try:
        require(not args.resume or not (args.dry_run or args.summarize), "--resume cannot be combined with offline modes")
        protocol = load_protocol(args.plan)
        if args.dry_run:
            report = {"dry_run": True, "live_calls": 0, "source_rows": len(protocol["rows"]),
                      "max_calls": len(protocol["schedule"]), "identity": protocol["identity"],
                      "cells": {cell: {"rows": 12, "in_band": sum(r["cell"] == cell and r["in_band"] for r in protocol["rows"])} for cell in "ABCD"}}
        else:
            require(args.out is not None, "--out is required for execution or --summarize")
            if args.summarize:
                report = summarize(protocol, checked_results(protocol, args.out))
            else:
                report = run(protocol, args.out, resume=args.resume)
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
        return 0 if args.dry_run or report["usable"] else 2
    except (CheckError, KeyError, ValueError, OSError) as error:
        print(f"rate_register: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
