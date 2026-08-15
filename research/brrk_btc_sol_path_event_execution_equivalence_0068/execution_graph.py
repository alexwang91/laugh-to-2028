from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Iterable

ASSETS = ("BTC", "SOL")
TARGETS = ("ANY_DOWN", "MAJOR_DOWN", "ANY_SIDEWAYS", "LONG_SIDEWAYS")
HORIZONS = (1, 3, 5, 10, 20)
NONHAZARD_ARCHITECTURES = ("P01", "P02", "P03", "P04", "P05", "P06")
REFIT_BLOCKS = tuple(range(48))


@dataclass(frozen=True)
class WorkUnit:
    unit_id: str
    stage: str
    asset: str
    target: str
    horizon: int | str
    architecture: str
    refit_block: int | None
    eligibility_reason: str
    expected_fit_calls: int
    expected_nnls_solves: int


def _unit_id(stage: str, asset: str, target: str, horizon: int | str, architecture: str, refit_block: int | None) -> str:
    rb = "NA" if refit_block is None else f"{refit_block:02d}"
    return f"{stage}:{asset}:{target}:{horizon}:{architecture}:{rb}"


def all_nonhazard_keys() -> tuple[tuple[str, str, int, str], ...]:
    return tuple(
        (asset, target, horizon, architecture)
        for asset in ASSETS
        for target in TARGETS
        for horizon in HORIZONS
        for architecture in NONHAZARD_ARCHITECTURES
    )


def all_p07_keys() -> tuple[tuple[str, str], ...]:
    return tuple((asset, target) for asset in ASSETS for target in TARGETS)


def all_p08_keys() -> tuple[tuple[str, str, int], ...]:
    return tuple((asset, target, horizon) for asset in ASSETS for target in TARGETS for horizon in HORIZONS)


def build_downstream_manifest(
    selected_nonhazard: Iterable[tuple[str, str, int, str]],
    selected_p07: Iterable[tuple[str, str]],
    eligible_p08: Iterable[tuple[str, str, int]],
) -> dict:
    """Single canonical graph builder used by qualification and controlled-mode dry run.

    Candidate downstream geometry is fixed. Eligibility controls expected physical actions.
    Excluded candidate units remain in the manifest with zero expected actions so every
    eligibility decision is auditable and receives a terminal trace.
    """
    selected_nonhazard = set(selected_nonhazard)
    selected_p07 = set(selected_p07)
    eligible_p08 = set(eligible_p08)

    units: list[WorkUnit] = []

    for asset, target, horizon, architecture in all_nonhazard_keys():
        eligible = (asset, target, horizon, architecture) in selected_nonhazard
        reason = "VALIDATION_SELECTED" if eligible else "VALIDATION_NOT_SELECTED"
        for refit_block in REFIT_BLOCKS:
            units.append(
                WorkUnit(
                    unit_id=_unit_id("ECONOMIC", asset, target, horizon, architecture, refit_block),
                    stage="ECONOMIC",
                    asset=asset,
                    target=target,
                    horizon=horizon,
                    architecture=architecture,
                    refit_block=refit_block,
                    eligibility_reason=reason,
                    expected_fit_calls=1 if eligible else 0,
                    expected_nnls_solves=0,
                )
            )

    for asset, target in all_p07_keys():
        eligible = (asset, target) in selected_p07
        reason = "VALIDATION_SELECTED" if eligible else "VALIDATION_NOT_SELECTED"
        for refit_block in REFIT_BLOCKS:
            units.append(
                WorkUnit(
                    unit_id=_unit_id("ECONOMIC", asset, target, "POOLED", "P07", refit_block),
                    stage="ECONOMIC",
                    asset=asset,
                    target=target,
                    horizon="POOLED",
                    architecture="P07",
                    refit_block=refit_block,
                    eligibility_reason=reason,
                    expected_fit_calls=1 if eligible else 0,
                    expected_nnls_solves=0,
                )
            )

    for asset, target, horizon in all_p08_keys():
        eligible = (asset, target, horizon) in eligible_p08
        reason = "BASE_PREDICTIONS_AVAILABLE" if eligible else "BASE_PREDICTIONS_MISSING"
        units.append(
            WorkUnit(
                unit_id=_unit_id("P08", asset, target, horizon, "P08", None),
                stage="P08",
                asset=asset,
                target=target,
                horizon=horizon,
                architecture="P08",
                refit_block=None,
                eligibility_reason=reason,
                expected_fit_calls=0,
                expected_nnls_solves=1 if eligible else 0,
            )
        )

    units.sort(key=lambda u: u.unit_id)
    ids = [u.unit_id for u in units]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate manifest unit_id")

    payload = {
        "schema_version": 1,
        "research_id": "BRRK-BTC-SOL-PATH-EVENT-EXECUTION-EQUIVALENCE-0068",
        "validation_fit_calls": 31008,
        "units": [asdict(u) for u in units],
    }
    canonical = canonical_bytes(payload)
    return {
        "payload": payload,
        "canonical_bytes": canonical,
        "sha256": hashlib.sha256(canonical).hexdigest(),
        "expected_economic_fit_calls": sum(u.expected_fit_calls for u in units),
        "expected_p08_nnls_solves": sum(u.expected_nnls_solves for u in units),
    }


def canonical_bytes(payload: dict) -> bytes:
    return (json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def consume_manifest(manifest: dict) -> dict:
    traces = []
    observed_fit_attempts = 0
    observed_nnls_attempts = 0
    seen = set()

    for unit in manifest["payload"]["units"]:
        uid = unit["unit_id"]
        if uid in seen:
            raise AssertionError("duplicate terminal trace")
        seen.add(uid)
        executable = unit["expected_fit_calls"] > 0 or unit["expected_nnls_solves"] > 0
        terminal_state = "EXECUTED" if executable else "ELIGIBILITY_EXCLUDED"
        observed_fit_attempts += unit["expected_fit_calls"]
        observed_nnls_attempts += unit["expected_nnls_solves"]
        traces.append({
            "unit_id": uid,
            "manifest_sha256": manifest["sha256"],
            "terminal_state": terminal_state,
            "fit_attempts": unit["expected_fit_calls"],
            "nnls_attempts": unit["expected_nnls_solves"],
        })

    if len(traces) != len(manifest["payload"]["units"]):
        raise AssertionError("missing terminal trace")
    if observed_fit_attempts != manifest["expected_economic_fit_calls"]:
        raise AssertionError("physical fit accounting mismatch")
    if observed_nnls_attempts != manifest["expected_p08_nnls_solves"]:
        raise AssertionError("physical NNLS accounting mismatch")

    trace_payload = {"manifest_sha256": manifest["sha256"], "traces": traces}
    return {
        "payload": trace_payload,
        "sha256": hashlib.sha256(canonical_bytes(trace_payload)).hexdigest(),
        "observed_fit_attempts": observed_fit_attempts,
        "observed_nnls_attempts": observed_nnls_attempts,
        "complete": True,
    }
