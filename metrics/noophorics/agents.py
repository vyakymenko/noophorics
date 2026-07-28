"""Agents: systems that map probes to answer distributions.

The Agent interface is deliberately minimal -- an agent is defined entirely by
its answer distributions, so anything that can answer probes can be measured.
Human agents, ensembles, and retrieval systems all fit; only ``AnthropicAgent``
happens to be implemented here.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Sequence

from .divergence import AnswerDist, to_distribution
from .probes import Probe, ProbeMeasure

__all__ = ["Agent", "ScriptedAgent", "AnthropicAgent", "DEFAULT_MODEL"]

DEFAULT_MODEL = "claude-opus-5"

_ANSWER_INSTRUCTION = (
    "Answer with exactly one of the permitted options. "
    "Judge only from what you have been told. If the information you have does "
    "not settle the case, choose the option you consider most likely rather "
    "than refusing -- an abstention is not a measurable disposition."
)


class Agent(object):
    """A system that maps a probe to a distribution over answers."""

    name = "abstract-agent"

    def answer(self, probe: Probe, n_samples: int) -> AnswerDist:
        raise NotImplementedError

    def answer_all(
        self, measure: ProbeMeasure, n_samples: int
    ) -> List[AnswerDist]:
        return [self.answer(probe, n_samples) for probe in measure]

    def claim_agreement(self, measure: ProbeMeasure, counterpart: str) -> float:
        """Elicit this agent's claimed agreement rate with a counterpart.

        Must be asked in the same units as the observed agreement rate, or the
        phantom-agreement subtraction is meaningless. Returns a rate in [0, 1].
        """
        raise NotImplementedError


class ScriptedAgent(Agent):
    """An agent replaying fixed answers. For tests and for replaying logs."""

    def __init__(
        self,
        name: str,
        answers: Dict[str, Sequence[str]],
        claim: Optional[float] = None,
    ):
        self.name = name
        self._answers = {k: list(v) for k, v in answers.items()}
        self._claim = claim

    def answer(self, probe: Probe, n_samples: int) -> AnswerDist:
        if probe.id not in self._answers:
            raise KeyError("scripted agent %s has no answers for %s" % (self.name, probe.id))
        return to_distribution(self._answers[probe.id][:n_samples])

    def claim_agreement(self, measure: ProbeMeasure, counterpart: str) -> float:
        if self._claim is None:
            raise NotImplementedError("scripted agent %s has no claim" % self.name)
        return self._claim


class AnthropicAgent(Agent):
    """An agent backed by a Claude model.

    ``context`` is everything the agent knows about the domain -- the full
    source specification for a sender, a transferred message for a receiver,
    or nothing at all for a prior baseline. It is placed in the system prompt
    behind a cache breakpoint, so the repeated probe calls that make up one
    measurement read it at cache rates rather than paying for it every time.

    On sampling: current Claude models do not accept ``temperature``, so the
    per-probe distribution comes from the model's inherent nondeterminism
    rather than from a tunable knob. Distributions are therefore often
    degenerate, which shows up as a very low noise floor -- correct, and worth
    reporting rather than hiding, since it means the fidelity denominator is
    close to the raw prior gap.
    """

    def __init__(
        self,
        name: str,
        context: str = "",
        model: str = DEFAULT_MODEL,
        client: Any = None,
        effort: str = "low",
        max_tokens: int = 2048,
    ):
        try:
            import anthropic
        except ImportError:  # pragma: no cover - environment-dependent
            raise ImportError(
                "the anthropic SDK is required for AnthropicAgent: pip install anthropic"
            )
        self.name = name
        self.context = context
        self.model = model
        self.effort = effort
        self.max_tokens = max_tokens
        self._client = client if client is not None else anthropic.Anthropic()

    # -- internals ---------------------------------------------------------

    def _system_blocks(self) -> List[Dict[str, Any]]:
        blocks = [{"type": "text", "text": self._role_preamble()}]
        if self.context:
            blocks.append({"type": "text", "text": self.context})
        # Cache the whole stable prefix: it is re-sent once per probe sample.
        blocks[-1]["cache_control"] = {"type": "ephemeral"}
        return blocks

    def _role_preamble(self) -> str:
        if self.context:
            return (
                "You are deciding cases according to the rules you have been "
                "given below. " + _ANSWER_INSTRUCTION
            )
        return (
            "You are deciding cases in a domain whose rules you have not been "
            "told. " + _ANSWER_INSTRUCTION
        )

    def _call(self, prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        import json

        response = self._client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self._system_blocks(),
            output_config={"effort": self.effort, "format": {
                "type": "json_schema",
                "schema": schema,
            }},
            messages=[{"role": "user", "content": prompt}],
        )
        if response.stop_reason == "refusal":
            raise RuntimeError(
                "model declined the probe (category=%s); a refusal is not a "
                "disposition and must not be silently coerced into one"
                % getattr(response.stop_details, "category", None)
            )
        text = next(b.text for b in response.content if b.type == "text")
        return json.loads(text)

    # -- Agent interface ---------------------------------------------------

    def answer(self, probe: Probe, n_samples: int) -> AnswerDist:
        schema = {
            "type": "object",
            "properties": {"verdict": {"type": "string", "enum": probe.options}},
            "required": ["verdict"],
            "additionalProperties": False,
        }
        prompt = "%s\n\nPermitted answers: %s" % (
            probe.prompt,
            ", ".join(probe.options),
        )
        samples = [self._call(prompt, schema)["verdict"] for _ in range(n_samples)]
        return to_distribution(samples)

    def claim_agreement(self, measure: ProbeMeasure, counterpart: str) -> float:
        schema = {
            "type": "object",
            "properties": {
                "agreement_rate": {"type": "number"},
            },
            "required": ["agreement_rate"],
            "additionalProperties": False,
        }
        preview = "\n".join(
            "- %s" % p.prompt.strip().splitlines()[0][:160] for p in list(measure)[:5]
        )
        prompt = (
            "You are about to be compared against %s on %d decision cases from "
            "this domain. Five representative cases:\n\n%s\n\nEstimate the "
            "fraction of all %d cases on which your verdict would match theirs. "
            "Answer with a single number between 0 and 1. Do not hedge and do "
            "not explain -- an honest point estimate is what is being measured."
            % (counterpart, len(measure), preview, len(measure))
        )
        value = float(self._call(prompt, schema)["agreement_rate"])
        return max(0.0, min(1.0, value))

    # -- cost --------------------------------------------------------------

    def cost_of(self, message: str) -> int:
        """Token cost of a message, measured with *this* agent's tokenizer.

        Cost is always counted on the receiver: the receiver is who pays to
        read the artifact.
        """
        counted = self._client.messages.count_tokens(
            model=self.model,
            messages=[{"role": "user", "content": message}],
        )
        return counted.input_tokens


def api_key_present() -> bool:
    """Whether an Anthropic credential is resolvable from the environment."""
    return bool(
        os.environ.get("ANTHROPIC_API_KEY")
        or os.environ.get("ANTHROPIC_AUTH_TOKEN")
        or os.path.isdir(
            os.path.expanduser(
                os.environ.get("ANTHROPIC_CONFIG_DIR", "~/.config/anthropic")
            )
        )
    )
