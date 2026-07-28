"""An agent backed by the Codex CLI (OpenAI models, subscription auth).

Noophorics needs agents with genuinely different priors -- L2 (asymmetry),
L3 (prior overlap), and any estimate of capacity K or residual R are only
interesting across a real prior gap. Cross-provider pairs give the largest gap
obtainable: different data, different training, different tokenizer.

The Agent interface makes this cheap. ``answer_samples`` is the only primitive
an agent must supply, so a provider is a subprocess wrapper, not a redesign.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
from typing import Any, Dict, List, Optional, Sequence

from .agents import Agent, _ANSWER_INSTRUCTION
from .probes import Probe, ProbeMeasure

__all__ = ["CodexAgent", "codex_available"]

# Codex is an agentic harness, not a completion endpoint. These flags strip it
# back to something usable as a sampling instrument:
#   --ephemeral / --ignore-user-config  no session files, no user config
#   -C <empty dir> / --skip-git-repo-check   no project AGENTS.md or repo
#       context leaking into the probe -- without this the agent reads the
#       repository it is standing in, which for us contains the hypotheses
#   -s read-only                       the model may not act on the machine
#   model_reasoning_effort=low          without it a single probe can exceed
#       five minutes; with it, ~4 seconds
_BASE_FLAGS = [
    "--ephemeral",
    "--ignore-user-config",
    "--skip-git-repo-check",
    "--color", "never",
    "-s", "read-only",
]


def codex_available() -> bool:
    return shutil.which("codex") is not None


class CodexAgent(Agent):
    """Probe-answering agent driven by ``codex exec``.

    Sampling regime note, to be reported with any measurement: this agent runs
    at low reasoning effort and is instructed to answer without analysis. That
    is *not* identical to the regime an ``AnthropicAgent`` runs in, and exact
    cross-provider matching is not achievable -- the reasoning architectures
    differ. Record the regime as a parameter rather than pretending it is
    controlled.
    """

    def __init__(
        self,
        name: str,
        context: str = "",
        model: Optional[str] = None,
        reasoning_effort: str = "low",
        timeout_s: int = 180,
    ):
        if not codex_available():
            raise RuntimeError("the codex CLI is not on PATH")
        self.name = name
        self.context = context
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.timeout_s = timeout_s

    # -- internals ---------------------------------------------------------

    def _flags(self, workdir: str) -> List[str]:
        flags = list(_BASE_FLAGS) + ["-C", workdir]
        flags += ["-c", "model_reasoning_effort=%s" % self.reasoning_effort]
        if self.model:
            flags += ["-m", self.model]
        return flags

    def _call(self, prompt: str, schema: Optional[Dict[str, Any]] = None) -> str:
        # An empty working directory: codex reads AGENTS.md and repository
        # context from wherever it stands, and this repository states the
        # hypotheses the agent is being used to test.
        workdir = tempfile.mkdtemp(prefix="noophorics-codex-")
        out_path = os.path.join(workdir, "last-message.txt")
        argv = ["codex", "exec"] + self._flags(workdir) + ["-o", out_path]
        if schema is not None:
            schema_path = os.path.join(workdir, "schema.json")
            with open(schema_path, "w", encoding="utf-8") as fh:
                json.dump(schema, fh)
            argv += ["--output-schema", schema_path]
        argv.append(prompt)
        try:
            subprocess.run(
                argv, capture_output=True, text=True, timeout=self.timeout_s, check=False
            )
            if not os.path.exists(out_path):
                raise RuntimeError("codex produced no final message")
            with open(out_path, "r", encoding="utf-8") as fh:
                return fh.read().strip()
        finally:
            shutil.rmtree(workdir, ignore_errors=True)

    # -- Agent interface ---------------------------------------------------

    def answer_samples(self, probe: Probe, n_samples: int) -> List[str]:
        preamble = (
            "Decide the case below using only the rules you have been given. "
            if self.context
            else "Decide the case below. You have not been told the governing rules. "
        )
        prompt = "%s%s\n\n---\n%s%s\n\n%s\n\nAnswer immediately with exactly one "
        prompt = prompt % (
            self.context,
            "\n" if self.context else "",
            preamble,
            _ANSWER_INSTRUCTION,
            probe.prompt,
        )
        prompt += "of: %s. No analysis." % ", ".join(probe.options)
        schema = {
            "type": "object",
            "properties": {"verdict": {"type": "string", "enum": list(probe.options)}},
            "required": ["verdict"],
            "additionalProperties": False,
        }
        samples: List[str] = []
        for _ in range(n_samples):  # draw order preserved: the floor depends on it
            raw = self._call(prompt, schema)
            samples.append(self._coerce(raw, probe.options))
        return samples

    @staticmethod
    def _coerce(raw: str, options: Sequence[str]) -> str:
        """Extract the verdict. Raises rather than guessing on an unusable reply.

        A reply that cannot be read is missing data, not a wrong answer.
        Coercing it into an option would fabricate a disposition.
        """
        text = raw.strip()
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict) and parsed.get("verdict") in options:
                return parsed["verdict"]
        except ValueError:
            pass
        hits = [o for o in options if o in text.upper()]
        if len(hits) == 1:
            return hits[0]
        raise RuntimeError("unreadable codex reply: %r" % text[:200])

    def claim_agreement(self, measure: ProbeMeasure, counterpart: str) -> float:
        schema = {
            "type": "object",
            "properties": {"agreement_rate": {"type": "number"}},
            "required": ["agreement_rate"],
            "additionalProperties": False,
        }
        preview = "\n".join(
            "- %s" % p.prompt.strip().splitlines()[0][:160] for p in list(measure)[:5]
        )
        prompt = (
            "%s\n\n---\nYou are about to be compared against %s on %d decision "
            "cases from this domain. Five representative cases:\n\n%s\n\nEstimate "
            "the fraction of all %d cases on which your verdict would match "
            "theirs. Answer with a single number between 0 and 1, nothing else."
            % (self.context, counterpart, len(measure), preview, len(measure))
        )
        raw = self._call(prompt, schema)
        try:
            value = float(json.loads(raw)["agreement_rate"])
        except (ValueError, KeyError, TypeError):
            value = float(raw.strip().split()[0])
        return max(0.0, min(1.0, value))

    def cost_of(self, message: str) -> int:
        """Approximate token cost.

        The Codex CLI exposes no token-counting endpoint, so this is a word
        count scaled by a rough English words-per-token factor. Costs measured
        this way are NOT comparable with costs measured by a real tokenizer --
        report the unit, and never mix the two in one efficiency comparison.
        """
        return max(1, int(round(len(message.split()) * 1.3)))
