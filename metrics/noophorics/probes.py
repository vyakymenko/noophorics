"""Probes and probe measures.

Reference implementation of theory/definitions.md sections 1.2 and 1.3.

A probe measure is the noophoric frame of reference. Its identity matters:
every reported measurement must name the probe measure it was taken against,
so ProbeMeasure carries a content hash that survives serialization.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Dict, List, Optional, Sequence

__all__ = ["Probe", "ProbeMeasure", "load_probe_measure"]


class Probe(object):
    """A decidable decision whose answer depends on the transferred understanding.

    ``options`` is the finite answer space. Decidability is a methodological
    commitment, not a convenience: free-text answers admit no divergence
    measure that is stable across paraphrase. Free-form probes must be resolved
    into a discrete space by a stated rubric before they enter a measurement.

    ``key`` is the ground-truth answer where one exists. It is *not* used to
    compute any noophoric quantity -- fidelity measures sender/receiver
    convergence, not correctness -- but it lets an experiment report accuracy
    alongside fidelity as a sanity check on the sender.
    """

    __slots__ = ("id", "prompt", "options", "key", "tags")

    def __init__(
        self,
        id: str,
        prompt: str,
        options: Sequence[str],
        key: Optional[str] = None,
        tags: Optional[Sequence[str]] = None,
    ):
        if len(options) < 2:
            raise ValueError("probe %s: an answer space needs at least 2 options" % id)
        if len(set(options)) != len(options):
            raise ValueError("probe %s: duplicate options" % id)
        if key is not None and key not in options:
            raise ValueError("probe %s: key %r is not among the options" % (id, key))
        self.id = id
        self.prompt = prompt
        self.options = list(options)
        self.key = key
        self.tags = list(tags or [])

    def to_dict(self) -> Dict[str, Any]:
        out = {"id": self.id, "prompt": self.prompt, "options": self.options}
        if self.key is not None:
            out["key"] = self.key
        if self.tags:
            out["tags"] = self.tags
        return out

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Probe":
        return cls(
            id=data["id"],
            prompt=data["prompt"],
            options=data["options"],
            key=data.get("key"),
            tags=data.get("tags"),
        )

    def __repr__(self) -> str:
        return "Probe(%s, %d options)" % (self.id, len(self.options))


class ProbeMeasure(object):
    """A distribution over probes -- the noophoric frame of reference.

    Weights default to uniform. The content hash is over the probes' semantic
    content only (id, prompt, options, key), so cosmetic edits to metadata do
    not silently change the frame identity, and edits to a probe's text do.
    """

    __slots__ = ("id", "description", "probes", "weights", "domain")

    def __init__(
        self,
        id: str,
        probes: Sequence[Probe],
        description: str = "",
        weights: Optional[Sequence[float]] = None,
        domain: str = "",
    ):
        if not probes:
            raise ValueError("probe measure %s: empty" % id)
        ids = [p.id for p in probes]
        if len(set(ids)) != len(ids):
            raise ValueError("probe measure %s: duplicate probe ids" % id)
        if weights is not None and len(weights) != len(probes):
            raise ValueError("probe measure %s: weights length mismatch" % id)
        self.id = id
        self.description = description
        self.probes = list(probes)
        self.weights = list(weights) if weights is not None else [1.0] * len(probes)
        self.domain = domain

    def __len__(self) -> int:
        return len(self.probes)

    def __iter__(self):
        return iter(self.probes)

    @property
    def content_hash(self) -> str:
        """Stable 12-hex-char digest of the measure's semantic content."""
        payload = json.dumps(
            [
                [p.id, p.prompt, p.options, p.key]
                for p in self.probes
            ],
            sort_keys=True,
            ensure_ascii=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:12]

    @property
    def qualified_id(self) -> str:
        """The identifier that belongs in a report: id plus content hash."""
        return "%s@%s" % (self.id, self.content_hash)

    def accuracy(self, answers: Sequence[str]) -> Optional[float]:
        """Fraction of modal answers matching the key, or None if unkeyed.

        Not a noophoric quantity. A sanity check on whether the sender
        actually understood the source material -- a sender who did not
        understand it makes the whole transfer measurement uninterpretable.
        """
        keyed = [(p, a) for p, a in zip(self.probes, answers) if p.key is not None]
        if not keyed:
            return None
        return sum(1 for p, a in keyed if a == p.key) / len(keyed)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "description": self.description,
            "domain": self.domain,
            "weights": self.weights,
            "probes": [p.to_dict() for p in self.probes],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProbeMeasure":
        return cls(
            id=data["id"],
            probes=[Probe.from_dict(d) for d in data["probes"]],
            description=data.get("description", ""),
            weights=data.get("weights"),
            domain=data.get("domain", ""),
        )

    def __repr__(self) -> str:
        return "ProbeMeasure(%s, %d probes)" % (self.qualified_id, len(self.probes))


def load_probe_measure(path: str) -> ProbeMeasure:
    """Load a probe measure from a JSON file."""
    with open(path, "r", encoding="utf-8") as handle:
        return ProbeMeasure.from_dict(json.load(handle))
