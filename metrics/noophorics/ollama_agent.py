"""An agent backed by a local model served by ollama.

Why this provider matters beyond cost. Local open-weight models give the
largest prior gap available for L2 and L3 -- different data, different
training, different tokenizer -- and they remove two constraints that shaped
every run so far: no billing, and no safety classifier standing between the
instrument and the measurement.

Measured on MERIDIAN-34 before adoption (see the experiment's parameter note):

    gpt-oss:120b  think=low      accuracy 0.912   3 errors    2.2 s/probe
    gpt-oss:120b  think=medium   accuracy 1.000   0 errors    4.8 s/probe
    qwen3.5:35b   think=low      accuracy 1.000   0 errors   17.3 s/probe
    claude-opus-4-8              accuracy 0.882   4 errors

Both local models out-decided the hosted one on this task, and gpt-oss's three
errors at low effort were all interaction probes -- they vanish at medium.

TWO PARAMETERS THAT MUST BE REPORTED, NOT ASSUMED
-------------------------------------------------
``think`` -- reasoning depth. Not a free knob: at ``think=False`` gpt-oss
returns an EMPTY response, the same failure class Claude Opus 5 shows when
thinking is disabled. Turning reasoning off is a mode with its own pathologies,
not a neutral setting.

``temperature`` -- at 0 the model is deterministic, per-probe distributions
collapse to point masses, and the permutation floor is identically zero. That
would silently return the field to uncorrected fidelity. A temperature that
produces a non-degenerate floor is required BY the pre-registered analysis
plan, not added to it.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional, Sequence

from .agents import Agent, _ANSWER_INSTRUCTION
from .probes import Probe, ProbeMeasure

__all__ = ["OllamaAgent", "ollama_available", "DEFAULT_ENDPOINT"]

DEFAULT_ENDPOINT = "http://localhost:11434"


def ollama_available(endpoint: str = DEFAULT_ENDPOINT) -> bool:
    try:
        with urllib.request.urlopen(endpoint + "/api/tags", timeout=5):
            return True
    except Exception:
        return False


class OllamaAgent(Agent):
    """Probe-answering agent served by a local ollama instance."""

    def __init__(
        self,
        name: str,
        context: str = "",
        model: str = "gpt-oss:120b",
        think: str = "medium",
        temperature: float = 0.7,
        endpoint: str = DEFAULT_ENDPOINT,
        timeout_s: int = 900,
    ):
        self.name = name
        self.context = context
        self.model = model
        self.think = think
        self.temperature = temperature
        self.endpoint = endpoint
        self.timeout_s = timeout_s

    # -- internals ---------------------------------------------------------

    def _chat(
        self, prompt: str, schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
            "think": self.think,
            "options": {"temperature": self.temperature},
        }
        if schema is not None:
            body["format"] = schema
        request = urllib.request.Request(
            self.endpoint + "/api/chat",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
            payload = json.load(response)
        content = (payload.get("message") or {}).get("content", "")
        if not content.strip():
            # Empty content is missing data, not an answer. It is exactly what
            # think=False produces, and coercing it would fabricate a
            # disposition.
            raise RuntimeError(
                "%s returned an empty response (think=%s) -- treat as missing "
                "data, never as a verdict" % (self.model, self.think)
            )
        payload["_content"] = content
        return payload

    def _with_context(self, tail: str) -> str:
        if not self.context:
            return tail
        return "%s\n\n---\n%s" % (self.context, tail)

    # -- Agent interface ---------------------------------------------------

    def answer_samples(self, probe: Probe, n_samples: int) -> List[str]:
        schema = {
            "type": "object",
            "properties": {"verdict": {"type": "string", "enum": list(probe.options)}},
            "required": ["verdict"],
        }
        preamble = (
            "Decide the case below using only the rules you have been given. "
            if self.context
            else "Decide the case below. You have not been told the governing rules. "
        )
        prompt = self._with_context(
            "%s%s\n\n%s\n\nAnswer with exactly one of: %s."
            % (preamble, _ANSWER_INSTRUCTION, probe.prompt, ", ".join(probe.options))
        )
        # Draw order preserved: the permutation floor depends on it.
        out: List[str] = []
        for _ in range(n_samples):
            content = self._chat(prompt, schema)["_content"]
            out.append(json.loads(content)["verdict"])
        return out

    def claim_agreement(
        self,
        measure: ProbeMeasure,
        counterpart: str,
        artifact: Optional[str] = None,
        n_elicitations: int = 3,
        seed: int = 0,
    ) -> List[float]:
        schema = {
            "type": "object",
            "properties": {"agreement_rate": {"type": "number"}},
            "required": ["agreement_rate"],
        }
        probes = list(measure)
        step = max(1, len(probes) // 6)
        preview = "\n".join(
            "- %s" % p.prompt.strip().splitlines()[0][:160] for p in probes[::step][:6]
        )
        artifact_block = (
            "\n\nThis is the brief that carries the transfer:\n\n%s\n" % artifact
            if artifact is not None else ""
        )
        prompt = self._with_context(
            "You are about to be compared against %s on %d decision cases from "
            "this domain, sampled across its full range. Six of them:\n\n%s%s"
            "\n\nEstimate the fraction of all %d cases on which your verdict "
            "would match theirs. Answer with a single number between 0 and 1."
            % (counterpart, len(measure), preview, artifact_block, len(measure))
        )
        out = []
        for _ in range(n_elicitations):
            value = float(json.loads(self._chat(prompt, schema)["_content"])["agreement_rate"])
            out.append(max(0.0, min(1.0, value)))
        return out

    def claim_per_probe(
        self,
        probe: Probe,
        counterpart: str,
        artifact: Optional[str] = None,
        n_elicitations: int = 5,
    ) -> List[bool]:
        """Per-probe binary judgment: will the counterpart's verdict match mine?

        The v0.4 instrument, and the reason E-002 exists. ``claim_agreement``
        returns one global rate for the whole measure, which yields a mean
        difference -- a BIAS term -- and nothing else.

        Keysar & Henly (2002) did not do that. Their speakers made a per-trial
        forced choice about what the listener had understood, and the reported
        72%/61% are aggregates computed afterwards. Because the judgment is
        per-trial, each prediction pairs with THAT trial's outcome, which yields
        resolution (can the party tell WHICH cases diverged) and the conditional
        asymmetry that was their actual headline -- neither of which a global
        rate can produce.

        Returns the raw draws, unaggregated, in order. The caller averages.
        Nothing about the key, the counterpart's answers, or any outcome appears
        in the prompt: this is a prediction, and contaminating it would measure
        reading instead.
        """
        schema = {
            "type": "object",
            "properties": {"same_verdict": {"type": "boolean"}},
            "required": ["same_verdict"],
        }
        artifact_block = (
            "\n\nThis is the brief that carries the transfer:\n\n%s\n" % artifact
            if artifact is not None else ""
        )
        prompt = self._with_context(
            "%s\n\nHere is a case you have just decided:\n\n%s%s\n\n"
            "Will %s reach the same verdict as you on this specific case? "
            "Answer only about this case."
            % (_ANSWER_INSTRUCTION, probe.prompt, artifact_block, counterpart)
        )
        return [bool(json.loads(self._chat(prompt, schema)["_content"])["same_verdict"])
                for _ in range(n_elicitations)]

    def compose(self, prompt: str, seed: int = 0) -> str:
        """Generate an artifact. Fast here, unlike the Codex CLI (>7 min)."""
        text = self._chat(self._with_context(prompt))["_content"].strip()
        if not text:
            raise RuntimeError("empty brief from %s" % self.model)
        return text

    def cost_of(self, message: str) -> int:
        """Token cost from the model's OWN tokenizer.

        ollama reports ``prompt_eval_count`` for the prompt it actually
        tokenized, so this is a real count rather than the scaled word count the
        Codex provider is stuck with. Costs measured here are comparable within
        a run; they are still not comparable across providers, because the
        tokenizers differ.
        """
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": message}],
            "stream": False,
            "think": "low",
            "options": {"num_predict": 1, "temperature": 0},
        }
        request = urllib.request.Request(
            self.endpoint + "/api/chat",
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=self.timeout_s) as response:
            payload = json.load(response)
        count = payload.get("prompt_eval_count")
        if not count:
            raise RuntimeError("ollama did not report prompt_eval_count")
        return int(count)
