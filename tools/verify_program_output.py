#!/usr/bin/env python3
"""Offline prototype for a bounded, synthetic program-output instrument.

This is an engineering fixture verifier, not an experiment runner or an
adjudicated probe measure. It never evaluates Python or calls a model.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import re
import sys


SCHEMA = "noophorics.offline_program_output.v1"
LANGUAGE = "two-register-arithmetic-v1"
REGISTERS = ("a", "b")
OPERATIONS = ("set", "add", "sub", "mul", "mod")
MAX_STEPS = 8
MAX_ITEMS = 16
MAX_ABS_STATE = 10_000
MAX_JSON_BYTES = 100_000
ANSWER_VOCABULARY = (0, 1, 2, 3)
ID_RE = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")
SHA_RE = re.compile(r"[0-9a-f]{64}\Z")
UTC_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")


class Rejection(ValueError):
    """A validation failure with a stable machine-readable reason."""

    def __init__(self, code: str, item_id: str | None = None):
        super().__init__(code)
        self.code = code
        self.item_id = item_id


def _reject(code: str, item_id: str | None = None) -> None:
    raise Rejection(code, item_id)


def _fields(value: object, names: set[str], code: str, item_id: str | None = None) -> dict:
    if not isinstance(value, dict) or set(value) != names:
        _reject(code, item_id)
    return value


def _integer(value: object, low: int, high: int, code: str, item_id: str | None = None) -> None:
    if type(value) is not int or not low <= value <= high:
        _reject(code, item_id)


def canonical_sha256(value: object) -> str:
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def instrument_sha256() -> str:
    return hashlib.sha256(Path(__file__).read_bytes()).hexdigest()


def _source_value(source: str | int, state: dict[str, int]) -> int:
    return state[source] if isinstance(source, str) else source


def validate_item(item: object) -> dict:
    if not isinstance(item, dict):
        _reject("ITEM_SHAPE")
    item_id = item.get("id") if isinstance(item.get("id"), str) else None
    _fields(item, {"id", "family_id", "template_id", "input", "program",
                   "output_register", "key", "spec_sha256"}, "ITEM_SHAPE", item_id)
    for field in ("id", "family_id", "template_id"):
        if not isinstance(item[field], str) or not ID_RE.fullmatch(item[field]):
            _reject("ITEM_ID", item_id)
    item_id = item["id"]
    spec = {key: item[key] for key in item if key not in ("key", "spec_sha256")}
    if not isinstance(item["spec_sha256"], str) or not SHA_RE.fullmatch(item["spec_sha256"]):
        _reject("SPEC_HASH_FORMAT", item_id)
    if canonical_sha256(spec) != item["spec_sha256"]:
        _reject("SPEC_HASH_MISMATCH", item_id)
    initial = _fields(item["input"], set(REGISTERS), "INPUT_SHAPE", item_id)
    for value in initial.values():
        _integer(value, -9, 9, "INPUT_RANGE", item_id)
    if item["output_register"] not in REGISTERS:
        _reject("OUTPUT_REGISTER", item_id)
    _integer(item["key"], 0, 3, "KEY_VOCABULARY", item_id)
    program = item["program"]
    if not isinstance(program, list) or not 1 <= len(program) <= MAX_STEPS:
        _reject("PROGRAM_LENGTH", item_id)
    for instruction in program:
        _fields(instruction, {"op", "dst", "src"}, "INSTRUCTION_SHAPE", item_id)
        if instruction["op"] not in OPERATIONS or instruction["dst"] not in REGISTERS:
            _reject("INSTRUCTION_NAME", item_id)
        source = instruction["src"]
        if isinstance(source, str):
            if source not in REGISTERS or instruction["op"] == "mod":
                _reject("OPERAND", item_id)
        elif type(source) is int:
            if instruction["op"] == "mod":
                if not 2 <= source <= 9:
                    _reject("MODULUS", item_id)
            elif not -9 <= source <= 9:
                _reject("OPERAND", item_id)
        else:
            _reject("OPERAND", item_id)
    if program[-1] != {"op": "mod", "dst": item["output_register"], "src": 4}:
        _reject("FINAL_NORMALIZATION", item_id)
    return item


def validate_manifest(manifest: object) -> list[dict]:
    manifest = _fields(manifest,
                       {"schema", "language", "runtime", "instrument_sha256",
                        "provenance", "items"}, "MANIFEST_SHAPE")
    if manifest["schema"] != SCHEMA or manifest["language"] != LANGUAGE:
        _reject("SCHEMA_VERSION")
    runtime = _fields(manifest["runtime"], {"implementation", "version"}, "RUNTIME_SHAPE")
    if (runtime["implementation"] != "CPython"
            or runtime["version"] != sys.version.split()[0]
            or sys.implementation.name != "cpython"):
        _reject("RUNTIME_MISMATCH")
    code_hash = manifest["instrument_sha256"]
    if not isinstance(code_hash, str) or not SHA_RE.fullmatch(code_hash):
        _reject("INSTRUMENT_HASH_FORMAT")
    if code_hash != instrument_sha256():
        _reject("INSTRUMENT_HASH_MISMATCH")
    provenance = _fields(manifest["provenance"],
                         {"created_utc", "author", "source", "purpose",
                          "holdout_eligible", "independent_key_adjudication"},
                         "PROVENANCE_SHAPE")
    if (not isinstance(provenance["created_utc"], str)
            or not UTC_RE.fullmatch(provenance["created_utc"])):
        _reject("PROVENANCE_DATE")
    try:
        datetime.fromisoformat(provenance["created_utc"].replace("Z", "+00:00"))
    except ValueError:
        _reject("PROVENANCE_DATE")
    if (not isinstance(provenance["author"], str) or not provenance["author"]
            or not isinstance(provenance["source"], str) or not provenance["source"]
            or provenance["purpose"] != "synthetic_fixture"
            or provenance["holdout_eligible"] is not False
            or provenance["independent_key_adjudication"] is not False):
        _reject("PROVENANCE_SCOPE")
    items = manifest["items"]
    if not isinstance(items, list) or not 1 <= len(items) <= MAX_ITEMS:
        _reject("ITEM_COUNT")
    seen = set()
    for item in items:
        validate_item(item)
        if item["id"] in seen:
            _reject("DUPLICATE_ITEM_ID", item["id"])
        seen.add(item["id"])
    return items


def execute_program(item: dict) -> tuple[list[dict], int]:
    """Runtime path: execute a validated, bounded instruction list."""
    state = dict(item["input"])
    trace = []
    for index, instruction in enumerate(item["program"]):
        before = state.copy()
        dst = instruction["dst"]
        value = _source_value(instruction["src"], state)
        operation = instruction["op"]
        if operation == "set":
            state[dst] = value
        elif operation == "add":
            state[dst] += value
        elif operation == "sub":
            state[dst] -= value
        elif operation == "mul":
            state[dst] *= value
        else:
            state[dst] %= value
        if abs(state[dst]) > MAX_ABS_STATE:
            _reject("STATE_LIMIT", item["id"])
        trace.append({"index": index, "before": before, "after": state.copy()})
    return trace, state[item["output_register"]]


def check_trace(item: dict, trace: object, output: object) -> None:
    """Independent path: audit each state transition, without execute_program."""
    item_id = item["id"]
    if not isinstance(trace, list) or len(trace) != len(item["program"]):
        _reject("TRACE_LENGTH", item_id)
    expected = dict(item["input"])
    for position, (step, instruction) in enumerate(zip(trace, item["program"])):
        _fields(step, {"index", "before", "after"}, "TRACE_SHAPE", item_id)
        if type(step["index"]) is not int or step["index"] != position:
            _reject("TRACE_INDEX", item_id)
        for state in (step["before"], step["after"]):
            _fields(state, set(REGISTERS), "TRACE_STATE", item_id)
            if any(type(value) is not int or abs(value) > MAX_ABS_STATE
                   for value in state.values()):
                _reject("TRACE_STATE", item_id)
        if step["before"] != expected:
            _reject("TRACE_BEFORE", item_id)
        dst, source = instruction["dst"], instruction["src"]
        operand = expected[source] if isinstance(source, str) else source
        current = expected[dst]
        operation = instruction["op"]
        # Deliberately separate from the runtime dispatch, including divmod
        # for modulus. Agreement alone is not external key adjudication.
        if operation == "set":
            next_value = operand
        elif operation == "add":
            next_value = sum((current, operand))
        elif operation == "sub":
            next_value = sum((current, -operand))
        elif operation == "mul":
            next_value = math.prod((current, operand))
        else:
            next_value = divmod(current, operand)[1]
        if abs(next_value) > MAX_ABS_STATE:
            _reject("STATE_LIMIT", item_id)
        expected = {**expected, dst: next_value}
        if step["after"] != expected:
            _reject("TRACE_TRANSITION", item_id)
    if type(output) is not int or output != expected[item["output_register"]]:
        _reject("TRACE_OUTPUT", item_id)
    if output not in ANSWER_VOCABULARY:
        _reject("OUTPUT_VOCABULARY", item_id)


def verify_manifest(manifest: object) -> list[dict]:
    items = validate_manifest(manifest)
    verified = []
    for item in items:
        trace, output = execute_program(item)
        check_trace(item, trace, output)
        if output != item["key"]:
            _reject("KEY_MISMATCH", item["id"])
        verified.append({"id": item["id"], "key": output,
                         "steps": len(trace), "trace_sha256": canonical_sha256(trace)})
    return verified


def self_check(manifest: dict) -> list[dict]:
    """Exercise distinct failure gates on copies of a valid synthetic fixture."""
    first = manifest["items"][0]
    cases = []

    def case(name: str, expected: str, mutate, trace_only: bool = False) -> None:
        copy = deepcopy(manifest)
        mutate(copy)
        try:
            if trace_only:
                item = copy["items"][0]
                trace, output = execute_program(item)
                trace[0]["after"]["a"] += 1
                check_trace(item, trace, output)
            else:
                verify_manifest(copy)
        except Rejection as rejection:
            observed = rejection.code
        else:
            observed = "ACCEPTED"
        cases.append({"case": name, "expected_rejection": expected,
                      "observed_rejection": observed, "passed": observed == expected})

    def rehash_first(copy: dict) -> None:
        item = copy["items"][0]
        item["spec_sha256"] = canonical_sha256(
            {key: value for key, value in item.items() if key not in ("key", "spec_sha256")})

    case("wrong-key", "KEY_MISMATCH",
         lambda copy: copy["items"][0].__setitem__("key", (first["key"] + 1) % 4))
    case("changed-source-hash", "SPEC_HASH_MISMATCH",
         lambda copy: copy["items"][0]["input"].__setitem__("a", first["input"]["a"] + 1))
    case("wrong-runtime", "RUNTIME_MISMATCH",
         lambda copy: copy["runtime"].__setitem__("version", "0.0.0"))
    case("unadjudicated-holdout", "PROVENANCE_SCOPE",
         lambda copy: copy["provenance"].__setitem__("holdout_eligible", True))
    case("corrupt-trace", "TRACE_TRANSITION", lambda copy: None, trace_only=True)

    def bad_operation(copy: dict) -> None:
        copy["items"][0]["program"][0]["op"] = "import"
        rehash_first(copy)

    case("unsupported-operation", "INSTRUCTION_NAME", bad_operation)

    def bad_final(copy: dict) -> None:
        copy["items"][0]["program"][-1] = {"op": "add", "dst": "a", "src": 1}
        rehash_first(copy)

    case("missing-final-normalization", "FINAL_NORMALIZATION", bad_final)

    def out_of_range(copy: dict) -> None:
        item = copy["items"][0]
        item["input"]["a"] = 9
        item["program"] = ([{"op": "mul", "dst": "a", "src": "a"}] * 3
                           + [{"op": "mod", "dst": "a", "src": 4}])
        rehash_first(copy)

    case("state-limit", "STATE_LIMIT", out_of_range)
    return cases


def _unique_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            _reject("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def load_manifest(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    if len(raw) > MAX_JSON_BYTES:
        _reject("MANIFEST_SIZE")
    try:
        manifest = json.loads(raw, object_pairs_hook=_unique_pairs)
    except (UnicodeDecodeError, json.JSONDecodeError):
        _reject("MANIFEST_JSON")
    return manifest, hashlib.sha256(raw).hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="synthetic fixture manifest JSON")
    parser.add_argument("--self-check", action="store_true",
                        help="run expected negative checks on copies of the fixtures")
    args = parser.parse_args(argv)
    try:
        manifest, manifest_sha = load_manifest(args.manifest)
        items = verify_manifest(manifest)
        negative_checks = self_check(manifest) if args.self_check else []
    except (OSError, Rejection) as exc:
        print(json.dumps({"status": "rejected", "code": exc.code if isinstance(exc, Rejection)
                          else "MANIFEST_IO", "item_id": getattr(exc, "item_id", None)}))
        return 1
    passed = all(check["passed"] for check in negative_checks)
    print(json.dumps({"status": "accepted" if passed else "self_check_failed",
                      "accepted_fixture_count": len(items),
                      "negative_check_count": len(negative_checks),
                      "negative_checks": negative_checks,
                      "manifest_sha256": manifest_sha,
                      "instrument_sha256": instrument_sha256(), "runtime": manifest["runtime"],
                      "provenance": manifest["provenance"], "items": items},
                     sort_keys=True, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
