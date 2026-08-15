from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

from research.brrk_btc_sol_path_event_early_warning_runtime_qualified_0067 import engine as e67

RID = "BRRK-BTC-SOL-PATH-EVENT-EXECUTION-EQUIVALENCE-0068"


def _canonical(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): _canonical(value[k]) for k in sorted(value, key=lambda x: str(x))}
    if isinstance(value, (list, tuple)):
        return [_canonical(x) for x in value]
    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(_canonical(value), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def work_unit_hash(unit: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(unit).encode("utf-8")).hexdigest()


def manifest_hash(work_units: list[dict[str, Any]]) -> str:
    payload = [{**u, "work_unit_hash": work_unit_hash(u)} for u in work_units]
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def build_downstream_manifest(
    selected_params: Mapping[tuple[str, str, str, int], Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Build the frozen downstream graph from validation-selected tracks.

    This function encodes existing 0067 eligibility semantics only. It does not
    inspect historical values, metrics, returns, controller outcomes, or model
    performance. `selected_params` is the already-frozen output of validation.
    """
    units: list[dict[str, Any]] = []
    seq = 0
    mdl = e67.mdl
    ee = e67.ee

    for asset in ee.ASSETS:
        for target in e67.TARGETS:
            for h in ee.WARNING_HORIZONS:
                for arch in mdl.BASE_ARCHITECTURES[:6]:
                    key = (arch, asset, target, h)
                    params = selected_params.get(key)
                    seq += 1
                    eligible = params is not None
                    units.append(
                        {
                            "stage": "economic_fit",
                            "sequence": seq,
                            "asset": asset,
                            "target": target,
                            "horizon": int(h),
                            "architecture": arch,
                            "canonical_params": _canonical(dict(params)) if eligible else None,
                            "eligibility_reason": "VALIDATION_SELECTED" if eligible else "NOT_VALIDATION_SELECTED",
                            "expected_action": "FIT" if eligible else "SKIP_NOT_ELIGIBLE",
                        }
                    )

            p7 = selected_params.get(("P07_DISCRETE_TIME_HAZARD_LOGIT", asset, target, 1))
            if p7 is None:
                for h in ee.WARNING_HORIZONS:
                    p7 = selected_params.get(("P07_DISCRETE_TIME_HAZARD_LOGIT", asset, target, h))
                    if p7 is not None:
                        break
            seq += 1
            units.append(
                {
                    "stage": "economic_fit",
                    "sequence": seq,
                    "asset": asset,
                    "target": target,
                    "horizon": None,
                    "architecture": "P07_DISCRETE_TIME_HAZARD_LOGIT",
                    "canonical_params": _canonical(dict(p7)) if p7 is not None else None,
                    "eligibility_reason": "ANY_P07_HORIZON_SELECTED" if p7 is not None else "NO_P07_HORIZON_SELECTED",
                    "expected_action": "FIT" if p7 is not None else "SKIP_NOT_ELIGIBLE",
                }
            )

    for asset in ee.ASSETS:
        for target in e67.TARGETS:
            for h in ee.WARNING_HORIZONS:
                key8 = ("P08_STACKED_PROBABILITY_ENSEMBLE", asset, target, h)
                params8 = selected_params.get(key8)
                seq += 1
                units.append(
                    {
                        "stage": "p08_nnls",
                        "sequence": seq,
                        "asset": asset,
                        "target": target,
                        "horizon": int(h),
                        "architecture": "P08_STACKED_PROBABILITY_ENSEMBLE",
                        "canonical_params": _canonical(dict(params8)) if params8 else None,
                        "eligibility_reason": "P08_SELECTED_FROM_AVAILABLE_BASES" if params8 else "NO_ELIGIBLE_BASE_PREDICTIONS",
                        "expected_action": "NNLS" if params8 else "SKIP_NOT_ELIGIBLE",
                    }
                )

    return units


def summarize_manifest(units: list[Mapping[str, Any]]) -> dict[str, int]:
    return {
        "economic_fit_units": sum(1 for u in units if u["stage"] == "economic_fit" and u["expected_action"] == "FIT"),
        "p08_nnls_units": sum(1 for u in units if u["stage"] == "p08_nnls" and u["expected_action"] == "NNLS"),
        "skipped_units": sum(1 for u in units if u["expected_action"] == "SKIP_NOT_ELIGIBLE"),
        "total_manifest_units": len(units),
    }


def terminal_trace_complete(units: list[Mapping[str, Any]], traces: list[Mapping[str, Any]]) -> bool:
    expected = {work_unit_hash(u) for u in units}
    observed = [str(t.get("work_unit_hash", "")) for t in traces]
    return len(observed) == len(expected) and len(set(observed)) == len(observed) and set(observed) == expected
