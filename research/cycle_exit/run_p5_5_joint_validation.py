from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CYCLE = ROOT / "research" / "cycle_exit"
L0040 = ROOT / "research" / "leverage_0040"
for p in (ROOT, CYCLE, L0040):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import run_leverage_0040_once_r1 as authority  # noqa: E402
import study_core as core  # noqa: E402
from research.cycle_exit.p5_4_behavior_mapping import apply_candidate_to_targets, load_contract as load_p54  # noqa: E402
from research.cycle_exit.p5_5_validation import (  # noqa: E402
    add_broad_policy_pass,
    economic_gate_checks,
    event_behavior_pass,
    event_behavior_table,
    held_out_relative_cagr,
    load_contracts,
    robustness_pass,
    select_candidate,
)

RESULT_DIR = ROOT / "research" / "results" / "p5_5_joint_validation"
V2_DIR = ROOT / "research" / "results" / "p5_3_v2_market_state"
P52_DIR = ROOT / "research" / "results" / "p5_2_feature_evidence"
TAXONOMY_PATH = CYCLE / "p5_1_event_taxonomy.json"
CONTRACT_PATH = CYCLE / "p5_5_validation_contract.json"
R1_PATH = CYCLE / "p5_5_validation_contract_r1.json"
P54_CONTRACT_PATH = CYCLE / "p5_4_behavior_mapping_contract.json"
P54_ENGINE_PATH = CYCLE / "p5_4_behavior_mapping.py"


class P55RunError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()


def frame_sha256(frame: pd.DataFrame) -> str:
    payload = frame.to_csv(index=True, float_format="%.12f", lineterminator="\n").encode()
    return hashlib.sha256(payload).hexdigest()


def write_csv(frame: pd.DataFrame, path: Path) -> str:
    frame.to_csv(path, index=False, lineterminator="\n", float_format="%.12g")
    return sha256_file(path)


def verify_frozen_dependencies(contract: dict, r1: dict) -> None:
    if RESULT_DIR.exists():
        raise P55RunError("P5.5 result directory already exists")
    if git_blob_sha(CONTRACT_PATH) != "96a923189fce1682d2cee2dd0b34afdb3e3bd3a7":
        raise P55RunError("P5.5 contract hash drift")
    if git_blob_sha(R1_PATH) != "98f651811b7edcb1f0b4c3047b87d95bffed087a":
        raise P55RunError("P5.5 R1 hash drift")
    if (V2_DIR / "summary.sha256").read_text().strip() != contract["upstream"]["p5_3_v2_result_summary_sha256"]:
        raise P55RunError("P5.3 V2 digest drift")
    if (P52_DIR / "summary.sha256").read_text().strip() != contract["upstream"]["p5_2_summary_sha256"]:
        raise P55RunError("P5.2 digest drift")
    if git_blob_sha(P54_CONTRACT_PATH) != contract["upstream"]["p5_4_contract_git_blob_sha"]:
        raise P55RunError("P5.4 contract drift")
    if git_blob_sha(P54_ENGINE_PATH) != contract["upstream"]["p5_4_mapping_engine_git_blob_sha"]:
        raise P55RunError("P5.4 engine drift")
    if r1.get("result_observed_before_amendment") is not False:
        raise P55RunError("R1 pre-result evidence invalid")


def simulate(targets: pd.DataFrame, prices: pd.DataFrame, session_start: str, end: str, cost_bps: float):
    decision_start = pd.Timestamp(session_start) - pd.Timedelta(days=1)
    path = core.simulate_p3_3_economic_path(
        targets,
        prices,
        start=decision_start,
        end=pd.Timestamp(end),
        cost_bps=float(cost_bps),
        band=0.05,
        fill_fraction=1.0,
        transaction_cost_multiplier=1.0,
        funding_blocks_by_session=None,
    )
    if len(path.returns) == 0 or pd.Timestamp(path.returns.index[0]) != pd.Timestamp(session_start):
        raise P55RunError(f"session timing drift for start={session_start}")
    return path


def metric_payload(candidate, baseline) -> dict[str, float]:
    cm = core.path_metrics(candidate)
    bm = core.path_metrics(baseline)
    bcalmar = float(bm["calmar"])
    bturn = float(bm["turnover"])
    dd_improvement = abs(float(bm["max_drawdown"])) - abs(float(cm["max_drawdown"]))
    return {
        "candidate_end_multiple": float(cm["end_multiple"]),
        "baseline_end_multiple": float(bm["end_multiple"]),
        "candidate_minus_baseline_end_multiple": float(cm["end_multiple"] - bm["end_multiple"]),
        "end_multiple_ratio_vs_baseline": float(cm["end_multiple"] / bm["end_multiple"]),
        "candidate_cagr": float(cm["cagr"]),
        "baseline_cagr": float(bm["cagr"]),
        "candidate_minus_baseline_cagr_pp": float(cm["cagr"] - bm["cagr"]),
        "candidate_max_drawdown": float(cm["max_drawdown"]),
        "baseline_max_drawdown": float(bm["max_drawdown"]),
        "candidate_minus_baseline_max_drawdown_pp": float(cm["max_drawdown"] - bm["max_drawdown"]),
        "max_drawdown_improvement_abs": float(dd_improvement),
        "max_drawdown_absolute_worsening": float(max(0.0, -dd_improvement)),
        "candidate_sharpe": float(cm["sharpe"]),
        "baseline_sharpe": float(bm["sharpe"]),
        "candidate_calmar": float(cm["calmar"]),
        "baseline_calmar": bcalmar,
        "calmar_ratio_vs_baseline": float(cm["calmar"] / bcalmar) if np.isfinite(bcalmar) and bcalmar > 0 else float("nan"),
        "candidate_turnover": float(cm["turnover"]),
        "baseline_turnover": bturn,
        "turnover_ratio_vs_baseline": float(cm["turnover"] / bturn) if bturn > 0 else float("nan"),
        "candidate_average_gross": float(cm["avg_gross_exposure"]),
        "baseline_average_gross": float(bm["avg_gross_exposure"]),
        "cycle_zero_exposure_days": int((candidate.gross_exposure.astype(float) <= 1e-12).sum()),
    }


def make_adjusted_targets(
    base_targets: pd.DataFrame,
    state_paths: pd.DataFrame,
    profile: str,
    behavior_map: str,
) -> tuple[pd.DataFrame, pd.Series]:
    p = state_paths.loc[state_paths["profile"] == profile, ["date", "market_state"]].copy()
    p["date"] = pd.to_datetime(p["date"])
    states = p.set_index("date")["market_state"].sort_index()
    states = states.reindex(base_targets.index)
    if states.isna().any():
        missing = [str(x.date()) for x in states.index[states.isna()][:5]]
        raise P55RunError(f"missing V2 market state on target dates profile={profile}: {missing}")
    adjusted, multipliers = apply_candidate_to_targets(base_targets, states, behavior_map, load_p54())
    return adjusted, multipliers


def economic_window(base_targets: pd.DataFrame, start_session: str, end_session: str) -> pd.DataFrame:
    decision_start = pd.Timestamp(start_session) - pd.Timedelta(days=1)
    end = pd.Timestamp(end_session)
    out = base_targets.loc[(base_targets.index >= decision_start) & (base_targets.index <= end)].copy()
    if decision_start not in out.index or end not in out.index:
        raise P55RunError("authoritative BRRK target window missing boundary")
    if out.isna().any().any():
        raise P55RunError("authoritative BRRK target contains NaN in economic window")
    return out


def main() -> None:
    contract, r1, p54 = load_contracts()
    verify_frozen_dependencies(contract, r1)

    econ = contract["evaluation_layers"]["authoritative_brrk_economics"]
    start_session = econ["evaluation_session_start"]
    end_session = econ["evaluation_session_end"]
    costs = [float(x) for x in econ["cost_bps_per_abs_weight_change"]]

    prices = authority._fetch_prices_corrected()
    _, brrk_raw_all, defensive_scale = authority._load_frozen_targets_corrected()
    base_targets = economic_window(brrk_raw_all, start_session, end_session)
    prices = prices.loc[(prices.index >= base_targets.index.min()) & (prices.index <= base_targets.index.max()), list(core.ASSETS)].copy()
    if not base_targets.index.equals(prices.index):
        raise P55RunError("authoritative price/target daily index mismatch in P5.5 window")
    if authority._target_authority_meta.get("evaluation_start_session") != start_session:
        raise P55RunError("authoritative target start drift")

    state_paths = pd.read_csv(V2_DIR / "daily_market_state_paths.csv", parse_dates=["date"])
    flat_episodes = pd.read_csv(V2_DIR / "flat_episodes.csv")
    resolved = pd.read_csv(P52_DIR / "resolved_events.csv")
    taxonomy = json.loads(TAXONOMY_PATH.read_text())

    event_rows = event_behavior_table(state_paths, resolved, taxonomy, flat_episodes, contract, p54)

    baseline_paths: dict[float, object] = {}
    for cost in costs:
        baseline_paths[cost] = simulate(base_targets, prices, start_session, end_session, cost)

    adjusted_targets: dict[tuple[str, str], pd.DataFrame] = {}
    full_paths: dict[tuple[str, str, float], object] = {}
    metric_rows: list[dict[str, object]] = []
    profiles = contract["candidate_set"]["profiles"]
    maps = contract["candidate_set"]["behavior_maps"]
    for profile in profiles:
        for behavior_map in maps:
            adjusted, _ = make_adjusted_targets(base_targets, state_paths, profile, behavior_map)
            adjusted_targets[(profile, behavior_map)] = adjusted
            for cost in costs:
                path = simulate(adjusted, prices, start_session, end_session, cost)
                full_paths[(profile, behavior_map, cost)] = path
                row = {"profile": profile, "behavior_map": behavior_map, "cost_bps": cost}
                row.update(metric_payload(path, baseline_paths[cost]))
                metric_rows.append(row)
    metrics = pd.DataFrame(metric_rows)

    start_rows: list[dict[str, object]] = []
    for session_start in contract["start_date_robustness"]["starts"]:
        base_path = simulate(base_targets, prices, session_start, end_session, 5.0)
        for profile in profiles:
            for behavior_map in maps:
                cand_path = simulate(adjusted_targets[(profile, behavior_map)], prices, session_start, end_session, 5.0)
                cm, bm = core.path_metrics(cand_path), core.path_metrics(base_path)
                start_rows.append({
                    "profile": profile,
                    "behavior_map": behavior_map,
                    "start_session": session_start,
                    "candidate_cagr": float(cm["cagr"]),
                    "baseline_cagr": float(bm["cagr"]),
                    "relative_cagr_pp": float(cm["cagr"] - bm["cagr"]),
                })
    start_df = pd.DataFrame(start_rows)

    resolved_index = resolved.set_index("event_id")
    held_rows: list[dict[str, object]] = []
    for event_id in contract["event_held_out_robustness"]["economic_window_events"]:
        if event_id not in resolved_index.index:
            raise P55RunError(f"missing held-out event {event_id}")
        anchor = pd.Timestamp(resolved_index.loc[event_id, "anchor_date"])
        exclude_start = anchor - pd.Timedelta(days=14)
        exclude_end = anchor + pd.Timedelta(days=28)
        baseline_returns = baseline_paths[5.0].returns
        for profile in profiles:
            for behavior_map in maps:
                candidate_returns = full_paths[(profile, behavior_map, 5.0)].returns
                cc, bc, rel, kept = held_out_relative_cagr(
                    candidate_returns,
                    baseline_returns,
                    exclude_start=exclude_start,
                    exclude_end=exclude_end,
                )
                held_rows.append({
                    "profile": profile,
                    "behavior_map": behavior_map,
                    "event_id": event_id,
                    "anchor_date": anchor.date().isoformat(),
                    "excluded_start": exclude_start.date().isoformat(),
                    "excluded_end": exclude_end.date().isoformat(),
                    "kept_sessions": kept,
                    "candidate_cagr": cc,
                    "baseline_cagr": bc,
                    "relative_cagr_pp": rel,
                })
    held_df = pd.DataFrame(held_rows)

    gate_rows: list[dict[str, object]] = []
    for profile in profiles:
        for behavior_map in maps:
            event_pass, event_checks = event_behavior_pass(event_rows, profile, behavior_map, contract)
            econ_pass, econ_checks = economic_gate_checks(metrics, profile, behavior_map, contract, r1)
            robust_pass, robust_checks = robustness_pass(start_df, held_df, profile, behavior_map, contract)
            row: dict[str, object] = {
                "profile": profile,
                "behavior_map": behavior_map,
                "event_behavior_pass": event_pass,
                "economic_pass": econ_pass,
                "robustness_pass": robust_pass,
                "non_selection_pass": bool(event_pass and econ_pass and robust_pass),
            }
            row.update({f"event__{k}": v for k, v in event_checks.items()})
            row.update({f"economic__{k}": v for k, v in econ_checks.items()})
            row.update({f"robust__{k}": v for k, v in robust_checks.items()})
            gate_rows.append(row)
    gates = add_broad_policy_pass(pd.DataFrame(gate_rows), contract)
    selected = select_candidate(gates, metrics, contract)

    RESULT_DIR.mkdir(parents=True)
    artifact_hashes: dict[str, str] = {}
    artifact_hashes["candidate_metrics_by_cost.csv"] = write_csv(metrics, RESULT_DIR / "candidate_metrics_by_cost.csv")
    artifact_hashes["event_behavior.csv"] = write_csv(event_rows, RESULT_DIR / "event_behavior.csv")
    artifact_hashes["start_date_robustness.csv"] = write_csv(start_df, RESULT_DIR / "start_date_robustness.csv")
    artifact_hashes["event_held_out_robustness.csv"] = write_csv(held_df, RESULT_DIR / "event_held_out_robustness.csv")
    artifact_hashes["candidate_gate_matrix.csv"] = write_csv(gates, RESULT_DIR / "candidate_gate_matrix.csv")

    selected_path = RESULT_DIR / "selected_candidate.json"
    selected_path.write_text(json.dumps(selected, indent=2, sort_keys=True) + "\n")
    artifact_hashes["selected_candidate.json"] = sha256_file(selected_path)

    manifest = {
        "study_id": contract["contract_id"],
        "contract_git_blob_sha": git_blob_sha(CONTRACT_PATH),
        "r1_git_blob_sha": git_blob_sha(R1_PATH),
        "p5_4_contract_git_blob_sha": git_blob_sha(P54_CONTRACT_PATH),
        "p5_4_engine_git_blob_sha": git_blob_sha(P54_ENGINE_PATH),
        "p5_3_v2_summary_sha256": (V2_DIR / "summary.sha256").read_text().strip(),
        "p5_2_summary_sha256": (P52_DIR / "summary.sha256").read_text().strip(),
        "price_frame_sha256": frame_sha256(prices),
        "brrk_target_frame_sha256": frame_sha256(base_targets),
        "defensive_scale_sha256": hashlib.sha256(defensive_scale.to_csv(float_format="%.12f", lineterminator="\n").encode()).hexdigest(),
        "v2_state_paths_sha256": sha256_file(V2_DIR / "daily_market_state_paths.csv"),
        "resolved_events_sha256": sha256_file(P52_DIR / "resolved_events.csv"),
        "taxonomy_git_blob_sha": git_blob_sha(TAXONOMY_PATH),
        "target_authority_meta": authority._target_authority_meta,
        "evaluation_session_start": start_session,
        "evaluation_session_end": end_session,
        "decision_start": str((pd.Timestamp(start_session) - pd.Timedelta(days=1)).date()),
        "cost_bps": costs,
        "rebalance_band_l1": 0.05,
        "candidate_count": 12,
        "funding_in_primary_selection": False,
    }
    manifest_path = RESULT_DIR / "input_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, default=str) + "\n")
    artifact_hashes["input_manifest.json"] = sha256_file(manifest_path)

    eligible_count = int(gates["eligible"].astype(bool).sum())
    summary = {
        "study_id": contract["contract_id"],
        "status": "ONE_TIME_FROZEN_P5_5_VALIDATION_COMPLETE",
        "candidate_count": 12,
        "eligible_candidate_count": eligible_count,
        "selection_status": selected["status"],
        "profile_selected": selected.get("profile_selected"),
        "behavior_map_selected": selected.get("behavior_map_selected"),
        "p5_6_integration_eligible": bool(selected.get("profile_selected") is not None),
        "production_authorized": False,
        "risk_permission_unlock_authorized": False,
        "economic_start": start_session,
        "economic_end": end_session,
        "event_diagnostics_include_2021_without_fabricated_brrk_economics": True,
        "artifact_sha256": artifact_hashes,
    }
    summary_path = RESULT_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    digest = sha256_file(summary_path)
    (RESULT_DIR / "summary.sha256").write_text(digest + "\n")
    print(
        f"P5.5 immutable validation complete selection={selected['status']} "
        f"eligible={eligible_count} summary_sha256={digest}"
    )


if __name__ == "__main__":
    main()
