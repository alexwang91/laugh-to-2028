"""History-agnostic Stage4 integration for BRRK 0084.

This module joins the already-frozen trial manifest, family-wise Holm
adjustment, G0-G11 evaluation, terminal classification, exact execution
accounting, and deterministic result-bundle serialization. It performs no file
I/O, no network access, and no controlled historical reads.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from typing import Mapping, Sequence

from .engine import DECLARED_TRIALS, ExecutionAccounting, terminal_classification
from .execution_interface import TrialEvidence, evaluate_gates
from .orchestration import TrialKey, declared_trial_manifest, family_holm
from .persistence import ExecutionCounters, build_result_bundle


@dataclass(frozen=True)
class IntegratedTrialInput:
    key: TrialKey
    evidence: TrialEvidence
    raw_ic_p: float
    raw_spread_p: float


@dataclass(frozen=True)
class IntegratedResult:
    classification: str
    qualified_trials: tuple[TrialKey, ...]
    trial_results: tuple[dict[str, object], ...]
    gate_summary: Mapping[str, object]
    bundle: bytes
    bundle_sha256: str


def integrate_trial_evidence(
    *,
    trials: Sequence[IntegratedTrialInput],
    accounting: ExecutionAccounting,
    counters: ExecutionCounters,
    support_possible: bool,
    inference_defined: bool,
    provenance: Mapping[str, object],
) -> IntegratedResult:
    """Run the frozen post-statistics integration exactly once in memory.

    The caller must supply already-computed, already-staged trial evidence.
    This function neither opens source payloads nor computes alternative
    science. It requires the exact 64-trial manifest, applies Holm separately
    to IC and spread p-values within each frozen factor family, evaluates
    G0-G11, derives the frozen terminal classification, and builds the canonical
    create-only result payload.
    """
    manifest = declared_trial_manifest()
    if len(trials) != DECLARED_TRIALS:
        raise ValueError("integration requires exactly 64 declared trials")

    by_key = {trial.key: trial for trial in trials}
    if len(by_key) != DECLARED_TRIALS or set(by_key) != set(manifest):
        raise ValueError("integrated trial manifest mismatch")

    holm_ic = family_holm({key: float(by_key[key].raw_ic_p) for key in manifest})
    holm_spread = family_holm({key: float(by_key[key].raw_spread_p) for key in manifest})

    execution_valid = accounting.execution_valid()
    qualified: list[TrialKey] = []
    serialized: list[dict[str, object]] = []
    gate_rows: dict[str, Mapping[str, bool]] = {}

    for key in manifest:
        item = by_key[key]
        evidence = replace(
            item.evidence,
            holm_ic_p=float(holm_ic[key]),
            holm_spread_p=float(holm_spread[key]),
        )
        gates = evaluate_gates(evidence, execution_valid)
        if all(gates.values()):
            qualified.append(key)
        key_id = f"{key.family}|{key.factor}|{key.horizon}|{key.representation}"
        gate_rows[key_id] = gates
        serialized.append(
            {
                "family": key.family,
                "factor": key.factor,
                "horizon": key.horizon,
                "representation": key.representation,
                "raw_ic_p": float(item.raw_ic_p),
                "raw_spread_p": float(item.raw_spread_p),
                "holm_ic_p": float(holm_ic[key]),
                "holm_spread_p": float(holm_spread[key]),
                "evidence": asdict(evidence),
                "gates": dict(gates),
                "qualified": all(gates.values()),
            }
        )

    classification = terminal_classification(
        accounting=accounting,
        any_qualified=bool(qualified),
        support_possible=bool(support_possible),
        inference_defined=bool(inference_defined),
    )
    gate_summary: dict[str, object] = {
        "execution_valid": execution_valid,
        "qualified_trial_count": len(qualified),
        "trial_gates": gate_rows,
    }
    bundle, digest = build_result_bundle(
        classification=classification,
        counters=counters,
        trial_results=serialized,
        gate_summary=gate_summary,
        provenance=provenance,
    )
    return IntegratedResult(
        classification=classification,
        qualified_trials=tuple(qualified),
        trial_results=tuple(serialized),
        gate_summary=gate_summary,
        bundle=bundle,
        bundle_sha256=digest,
    )
