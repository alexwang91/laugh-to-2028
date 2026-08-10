from __future__ import annotations

"""Execute the single frozen BRRK-WINNER-ROBUSTNESS-0002 panel exactly once.

The 40/60 candidate is imported from the already-closed BRRK-WINNER-0001 runner.
This module aborts before any robustness result file is written unless the merged
5 bps canonical and candidate primary result reproduces within the preregistered
tolerance. It does not search allocations, windows, costs, bands, signals or caps.
"""

import argparse
import json
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd

from research.brrk_winner_0001 import run_once as primary


RESEARCH_ID = "BRRK-WINNER-ROBUSTNESS-0002"
RUN_INTERFACE_ID = "BRRK-WINNER-ROBUSTNESS-0002-RUN-ONCE-V1"
ROOT = Path(__file__).resolve().parents[2]
PREREG_PATH = ROOT / "research/brrk_winner_robustness_0002/PREREGISTRATION.json"
INTERFACE_PATH = ROOT / "research/brrk_winner_robustness_0002/RUN_INTERFACE.json"
SOURCE_RESULT_PATH = ROOT / "research/brrk_winner_0001/PRIMARY_RESULT.json"
REPRO_TOL = 5e-10
PRIMARY_COST_BPS = 5.0
COST_STRESSES = (10.0, 20.0)
BLOCKS = (
    ("T1", pd.Timestamp("2022-12-10"), pd.Timestamp("2024-02-26"), 444),
    ("T2", pd.Timestamp("2024-02-27"), pd.Timestamp("2025-05-15"), 444),
    ("T3", pd.Timestamp("2025-05-16"), pd.Timestamp("2026-08-02"), 444),
)

fusion = primary.fusion
core = fusion.core
ASSETS = tuple(primary.ASSETS)


class RobustnessRunError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _assert_frozen_contract() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    prereg = _load_json(PREREG_PATH)
    interface = _load_json(INTERFACE_PATH)
    source = _load_json(SOURCE_RESULT_PATH)

    if prereg.get("research_id") != RESEARCH_ID or prereg.get("status") != "PREREGISTERED_NOT_RUN":
        raise RobustnessRunError("formal preregistration is missing or no longer pre-result")
    candidate = prereg["candidate"]
    if float(candidate["single_alt_btc_share"]) != 0.40 or float(candidate["single_alt_winner_share"]) != 0.60:
        raise RobustnessRunError("frozen 40/60 candidate drifted")
    if bool(candidate["alternative_splits_permitted"]):
        raise RobustnessRunError("alternative split unexpectedly permitted")
    if float(candidate["p3_3_l1_band"]) != 0.05 or float(candidate["gross_cap"]) != 1.0:
        raise RobustnessRunError("frozen P3.3 band or gross cap drifted")
    if list(candidate["universe"]) != list(ASSETS):
        raise RobustnessRunError("frozen universe drifted")

    formal_blocks = prereg["temporal_panel"]["blocks"]
    expected_blocks = [
        {"id": block_id, "start": str(start.date()), "end": str(end.date()), "sessions": sessions}
        for block_id, start, end, sessions in BLOCKS
    ]
    if formal_blocks != expected_blocks:
        raise RobustnessRunError("frozen temporal panel drifted")
    if [float(x) for x in prereg["cost_stress_panel"]["cost_bps"]] != list(COST_STRESSES):
        raise RobustnessRunError("frozen cost stress panel drifted")

    if interface.get("run_interface_id") != RUN_INTERFACE_ID or int(interface["variant_count"]) != 1:
        raise RobustnessRunError("run interface identity or variant count drifted")
    if bool(interface["same_id_retuning_forbidden"]) is not True or bool(interface["second_run_permitted"]) is not False:
        raise RobustnessRunError("one-shot governance drifted")
    if interface["temporal_panel"]["simulation_semantics"] != "SIMULATE_FULL_CONTINUOUS_5BPS_PATH_ONCE_THEN_SLICE_REALIZED_SESSION_RETURNS_WITHOUT_POSITION_RESET":
        raise RobustnessRunError("temporal simulation semantics drifted")
    if interface["cost_stress_panel"]["cost_bps"] != [10.0, 20.0]:
        raise RobustnessRunError("run-interface cost stresses drifted")

    if source.get("research_id") != "BRRK-WINNER-0001" or source.get("result_status") != "PASS_ROBUSTNESS_STAGE_ELIGIBLE":
        raise RobustnessRunError("source primary result is not the closed BRRK-WINNER-0001 PASS")
    return prereg, interface, source


def _simulate_at_cost(targets: pd.DataFrame, prices: pd.DataFrame, cost_bps: float):
    decision_start = fusion.EVALUATION_SESSION_START - pd.Timedelta(days=1)
    path = core.simulate_p3_3_economic_path(
        targets,
        prices,
        start=decision_start,
        end=fusion.EVALUATION_SESSION_END,
        cost_bps=float(cost_bps),
        band=fusion.BAND,
        fill_fraction=1.0,
        transaction_cost_multiplier=1.0,
        funding_blocks_by_session=None,
    )
    if len(path.returns) != 1332:
        raise RobustnessRunError(f"unexpected full-path session count at {cost_bps} bps: {len(path.returns)}")
    if pd.Timestamp(path.returns.index[0]) != fusion.EVALUATION_SESSION_START or pd.Timestamp(path.returns.index[-1]) != fusion.EVALUATION_SESSION_END:
        raise RobustnessRunError(f"full-path session boundary mismatch at {cost_bps} bps")
    return path


def _metric_payload(path) -> dict[str, float]:
    return fusion.metric_payload(path)


def _slice_path(path, start: pd.Timestamp, end: pd.Timestamp, expected_sessions: int):
    returns = path.returns.loc[start:end].astype(float).copy()
    if len(returns) != expected_sessions:
        raise RobustnessRunError(
            f"temporal block {start.date()}..{end.date()} expected {expected_sessions} sessions, found {len(returns)}"
        )
    idx = returns.index
    nav = (1.0 + returns).cumprod()
    return core.PathResult(
        returns=returns,
        nav=nav,
        turnover=path.turnover.loc[idx].astype(float).copy(),
        gross_exposure=path.gross_exposure.loc[idx].astype(float).copy(),
        held_weights=path.held_weights.loc[idx, list(ASSETS)].astype(float).copy(),
        current_weights_before_decision=path.current_weights_before_decision.loc[idx, list(ASSETS)].astype(float).copy(),
        funding_return=path.funding_return.loc[idx].astype(float).copy(),
        transaction_cost_return=path.transaction_cost_return.loc[idx].astype(float).copy(),
    )


def _assert_metric_reproduction(label: str, actual: dict[str, float], expected: dict[str, object]) -> None:
    if set(actual) != set(expected):
        raise RobustnessRunError(f"{label} metric key mismatch: actual={sorted(actual)} expected={sorted(expected)}")
    for key, value in actual.items():
        exp = float(expected[key])
        if not math.isclose(float(value), exp, rel_tol=0.0, abs_tol=REPRO_TOL):
            raise RobustnessRunError(
                f"{label} reproduction failed for {key}: expected={exp:.15g} actual={float(value):.15g}"
            )


def _reproduce_primary(
    base_targets: pd.DataFrame,
    candidate_targets: pd.DataFrame,
    base_path,
    candidate_path,
    source: dict[str, object],
) -> dict[str, object]:
    base_metrics = _metric_payload(base_path)
    candidate_metrics = _metric_payload(candidate_path)

    # Preserve the older independent canonical assertion as an additional fail-closed check.
    fusion.assert_baseline_reproduction(base_metrics)
    _assert_metric_reproduction("canonical", base_metrics, source["baseline"])
    _assert_metric_reproduction("candidate", candidate_metrics, source["candidate"])

    base_hash = fusion.frame_sha256(base_targets)
    candidate_hash = fusion.frame_sha256(candidate_targets)
    if base_hash != source["input_evidence"]["canonical_brrk_target_frame_sha256"]:
        raise RobustnessRunError("canonical target frame hash failed reproduction")
    if candidate_hash != source["input_evidence"]["candidate_target_frame_sha256"]:
        raise RobustnessRunError("candidate target frame hash failed reproduction")

    return {
        "passed": True,
        "absolute_tolerance": REPRO_TOL,
        "canonical_metrics": base_metrics,
        "candidate_metrics": candidate_metrics,
        "canonical_target_frame_sha256": base_hash,
        "candidate_target_frame_sha256": candidate_hash,
        "source_primary_result": "research/brrk_winner_0001/PRIMARY_RESULT.json",
    }


def _mdd_deterioration_pp(base: dict[str, float], candidate: dict[str, float]) -> float:
    return float(max(0.0, (base["max_drawdown"] - candidate["max_drawdown"]) * 100.0))


def _metric_delta(base: dict[str, float], candidate: dict[str, float]) -> dict[str, float]:
    return {key: float(candidate[key] - base[key]) for key in base}


def _temporal_panel(base_path, candidate_path) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    cagr_not_below_count = 0
    all_mdd_safe = True
    for block_id, start, end, sessions in BLOCKS:
        base = _metric_payload(_slice_path(base_path, start, end, sessions))
        candidate = _metric_payload(_slice_path(candidate_path, start, end, sessions))
        cagr_pass = bool(candidate["cagr"] >= base["cagr"] - 1e-12)
        mdd_deterioration = _mdd_deterioration_pp(base, candidate)
        mdd_pass = bool(mdd_deterioration <= 4.0 + 1e-12)
        cagr_not_below_count += int(cagr_pass)
        all_mdd_safe = all_mdd_safe and mdd_pass
        rows.append(
            {
                "block_id": block_id,
                "session_start": str(start.date()),
                "session_end": str(end.date()),
                "sessions": sessions,
                "cost_bps": PRIMARY_COST_BPS,
                "baseline": base,
                "candidate": candidate,
                "delta": _metric_delta(base, candidate),
                "gates": {
                    "candidate_cagr_not_below_canonical": {"pass": cagr_pass},
                    "max_drawdown_deterioration_pp_max_4": {
                        "value": mdd_deterioration,
                        "threshold": 4.0,
                        "pass": mdd_pass,
                    },
                },
            }
        )
    aggregate = {
        "candidate_cagr_not_below_canonical_block_count": {
            "value": cagr_not_below_count,
            "threshold": 2,
            "pass": cagr_not_below_count >= 2,
        },
        "max_drawdown_deterioration_safe_in_every_block": {"pass": all_mdd_safe},
    }
    return rows, aggregate


def _cost_stress_panel(
    base_targets: pd.DataFrame,
    candidate_targets: pd.DataFrame,
    prices: pd.DataFrame,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    rows: list[dict[str, object]] = []
    all_cagr = True
    all_mdd = True
    all_calmar = True
    for cost_bps in COST_STRESSES:
        base_path = _simulate_at_cost(base_targets, prices, cost_bps)
        candidate_path = _simulate_at_cost(candidate_targets, prices, cost_bps)
        base = _metric_payload(base_path)
        candidate = _metric_payload(candidate_path)
        cagr_pass = bool(candidate["cagr"] > base["cagr"])
        mdd_deterioration = _mdd_deterioration_pp(base, candidate)
        mdd_pass = bool(mdd_deterioration <= 4.0 + 1e-12)
        calmar_pass = bool(candidate["calmar"] >= base["calmar"] - 1e-12)
        all_cagr = all_cagr and cagr_pass
        all_mdd = all_mdd and mdd_pass
        all_calmar = all_calmar and calmar_pass
        rows.append(
            {
                "cost_bps": cost_bps,
                "sessions": 1332,
                "baseline": base,
                "candidate": candidate,
                "delta": _metric_delta(base, candidate),
                "gates": {
                    "candidate_cagr_strictly_above_canonical": {"pass": cagr_pass},
                    "max_drawdown_deterioration_pp_max_4": {
                        "value": mdd_deterioration,
                        "threshold": 4.0,
                        "pass": mdd_pass,
                    },
                    "calmar_not_below_canonical": {"pass": calmar_pass},
                },
            }
        )
    aggregate = {
        "candidate_cagr_strictly_above_canonical_all_cost_stresses": {"pass": all_cagr},
        "max_drawdown_deterioration_safe_all_cost_stresses": {"pass": all_mdd},
        "calmar_not_below_canonical_all_cost_stresses": {"pass": all_calmar},
    }
    return rows, aggregate


def run() -> dict[str, object]:
    _, interface, source = _assert_frozen_contract()
    prices, v1, base_targets, defensive_scale = primary._slice_authority()
    candidate_targets, single_mask, winner_counts = primary._candidate_targets(v1, base_targets)

    # Reproduction is deliberately completed before any robustness panel is computed.
    base_5bps_path = _simulate_at_cost(base_targets, prices, PRIMARY_COST_BPS)
    candidate_5bps_path = _simulate_at_cost(candidate_targets, prices, PRIMARY_COST_BPS)
    reproduction = _reproduce_primary(
        base_targets,
        candidate_targets,
        base_5bps_path,
        candidate_5bps_path,
        source,
    )

    temporal_rows, temporal_gates = _temporal_panel(base_5bps_path, candidate_5bps_path)
    cost_rows, cost_gates = _cost_stress_panel(base_targets, candidate_targets, prices)

    capture, top20_dates, base_log, candidate_log = primary._top20_capture(
        base_5bps_path.returns.astype(float), candidate_5bps_path.returns.astype(float)
    )
    primary_base = reproduction["canonical_metrics"]
    primary_candidate = reproduction["candidate_metrics"]
    turnover_ratio = float(primary_candidate["turnover"] / primary_base["turnover"])
    target_gross = candidate_targets.sum(axis=1)
    target_gross_max = float(target_gross.max())
    target_min_weight = float(candidate_targets.min().min())

    inherited_gates = {
        "canonical_best20_log_growth_capture_min_0_98": {
            "value": capture,
            "threshold": 0.98,
            "pass": capture >= 0.98 - 1e-12,
        },
        "turnover_ratio_max_1_25": {
            "value": turnover_ratio,
            "threshold": 1.25,
            "pass": turnover_ratio <= 1.25 + 1e-12,
        },
        "long_only": {
            "value": target_min_weight,
            "threshold": 0.0,
            "pass": target_min_weight >= -primary.EPS,
        },
        "gross_max_1": {
            "value": target_gross_max,
            "threshold": 1.0,
            "pass": target_gross_max <= 1.0 + 1e-9,
        },
    }

    gate_groups = [temporal_gates, cost_gates, inherited_gates]
    all_pass = all(bool(item["pass"]) for group in gate_groups for item in group.values())
    result_status = (
        "PASS_FUTURE_ONLY_VALIDATION_STAGE_ELIGIBLE"
        if all_pass
        else "FAIL_NO_FUTURE_VALIDATION_ELIGIBILITY"
    )

    return {
        "schema_version": 1,
        "research_id": RESEARCH_ID,
        "run_interface_id": RUN_INTERFACE_ID,
        "result_status": result_status,
        "baseline_reproduced_before_robustness_release": True,
        "robustness_metrics_released_after_reproduction": True,
        "variant_budget": 1,
        "actual_variants_evaluated": 1,
        "retuning_performed": False,
        "candidate_definition": {
            "single_alt_btc_share": 0.40,
            "single_alt_winner_share": 0.60,
            "single_alt_decision_rows": int(single_mask.sum()),
            "single_alt_winner_counts": winner_counts,
            "other_decision_rows_unchanged": int((~single_mask).sum()),
            "same_defensive_gross": True,
        },
        "evaluation": {
            "session_start": str(fusion.EVALUATION_SESSION_START.date()),
            "session_end": str(fusion.EVALUATION_SESSION_END.date()),
            "sessions": 1332,
            "primary_cost_bps": PRIMARY_COST_BPS,
            "cost_stress_bps": list(COST_STRESSES),
            "p3_3_l1_band": fusion.BAND,
            "temporal_semantics": interface["temporal_panel"]["simulation_semantics"],
            "cost_stress_semantics": interface["cost_stress_panel"]["simulation_semantics"],
        },
        "input_evidence": {
            "target_authority": fusion.authority._target_authority_meta,
            "canonical_brrk_target_frame_sha256": fusion.frame_sha256(base_targets),
            "candidate_target_frame_sha256": fusion.frame_sha256(candidate_targets),
            "defensive_scale_min": float(defensive_scale.min()),
            "defensive_scale_max": float(defensive_scale.max()),
            "historical_role": "RESULT_INFORMED_RESEARCHER_EXPOSED_DEVELOPMENT_ROBUSTNESS",
            "development_dataset_ref": "BRRK-WINNER-0001-CANONICAL-HIST-V1",
        },
        "reproduction": reproduction,
        "temporal_panel": {
            "blocks": temporal_rows,
            "aggregate_gates": temporal_gates,
        },
        "cost_stress_panel": {
            "rows": cost_rows,
            "aggregate_gates": cost_gates,
        },
        "right_tail": {
            "canonical_best20_dates": top20_dates,
            "canonical_best20_log_growth": base_log,
            "candidate_log_growth_on_same_dates": candidate_log,
            "capture_ratio": capture,
        },
        "inherited_gates": inherited_gates,
        "all_hard_gates_pass": all_pass,
        "execution_evidence": {
            "github_run_id": os.getenv("GITHUB_RUN_ID"),
            "github_run_attempt": os.getenv("GITHUB_RUN_ATTEMPT"),
            "workflow_sha": os.getenv("GITHUB_SHA"),
            "head_ref": os.getenv("GITHUB_REF_NAME"),
        },
        "promotion_authority": (
            "FUTURE_ONLY_VALIDATION_STAGE_ELIGIBILITY_ONLY" if all_pass else "NONE"
        ),
        "canonical_brrk_changed": False,
        "phase6_observation_changed": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
