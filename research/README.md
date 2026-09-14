# Research continuation — September 2026

These materials separate a new instrument readout, an audit of existing data,
and proposals for later work.

| Material | What it supplies | Status |
|---|---|---|
| [Qwen register readout](2026-09-14-register-feasibility.md) | Direct length-and-register counts from blind ratings of archived compositions, with raw requests and responses. | Instrument data; collection status is reported inside. |
| [Self-transfer audit](2026-09-09-selftransfer-audit.md) | Reconstruction from saved draws and proposed narrower wording for the existing result. | Retrospective audit and correction draft for human review. |
| [Domain-selection design](2026-09-09-domain-selection.md) | Candidate task families, a bounded exploratory screen, and separation of selection from confirmation. | Design draft; not registered or run. |
| [Methods supplement](2026-09-14-domain-methods.md) | Primary-source methods and limitations behind the proposed task families. | Literature review and engineering recommendation. |

The register check follows a [prospective plan](../probes/qwen-register/PLAN.md)
committed before ratings. Its source compositions already existed; their length
outcomes were known. It does not reopen E-001c or measure transfer fidelity.

The self-transfer audit reproduces the arithmetic while distinguishing observed
row means from evidence of equivalence. Its suggested correction has not been
applied to the original result, journal, theory, or retraction ledger. The
published prediction remains as written.

The next engineering step proposed by the methods review is an offline verifier
for a restricted program-output task. A new E-003 study also needs an explicit
operational definition of prior, an independent capability anchor, independently
adjudicated keys and an untouched confirmation set. The design draft names these
open choices; its proposed budget is not a completed experiment.

## Reproducing the evidence

The readout and audit each include their exact reproduction commands. Their
checks derive counts from raw records and compare generated reports with the
saved files. The corresponding tests deliberately inject incorrect counts,
missing responses, mismatched identities, and interrupted collection.

Agent and judge exposure is recorded in [EXPOSURE.md](../EXPOSURE.md). The
scientific workflow remains governed by [CONTRIBUTING.md](../CONTRIBUTING.md).

---

*This document is licensed CC BY 4.0.*
