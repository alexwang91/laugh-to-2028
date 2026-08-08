from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from research.cycle_exit.p5_3_state_model import (
    DIAGNOSTIC_DATA_INSUFFICIENT,
    DIAGNOSTIC_DATA_MISSING_HOLD,
    AtomState,
    P53Error,
    TransitionMemory,
    _hard_flat_inputs_present,
    causal_percentiles,
    evidence_atoms,
    load_contract as load_v1_contract,
    load_feature_panel,
    raw_candidate,
    runtime_features,
)

ROOT = Path(__file__).resolve().parents[2]
V2_CONTRACT_PATH = ROOT / "research" / "cycle_exit" / "p5_3_v2_architecture_contract.json"


class P53V2Error(RuntimeError):
    pass


def load_v2_contract(path: Path = V2_CONTRACT_PATH) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("contract_id") != "P5.3-MARKET-STATE-PERMISSION-SEPARATION-V2":
        raise P53V2Error("unexpected P5.3 V2 contract id")
    if payload.get("status") != "FROZEN_BEFORE_V2_STATE_PATH_EVALUATION":
        raise P53V2Error("P5.3 V2 contract is not frozen")
    market = payload["architecture_layers"]["MARKET_STATE"]
    if market["state_vocabulary"] != market["severity_order"]:
        raise P53V2Error("V2 market-state severity differs from vocabulary")
    if market.get("flat_absorbing") is not False:
        raise P53V2Error("V2 MARKET_STATE must be non-absorbing")
    permission = payload["architecture_layers"]["RISK_PERMISSION_LOCK"]
    if permission.get("automatic_unlock_forbidden") is not True:
        raise P53V2Error("operational permission must remain human-gated")
    if permission.get("market_state_has_unlock_authority") is not False:
        raise P53V2Error("MARKET_STATE cannot unlock operational permission")
    return payload


def inherited_v1_contract(v2_contract: dict | None = None) -> dict:
    v2 = v2_contract or load_v2_contract()
    v1 = load_v1_contract()
    if v2["profiles"] != v1["profiles"]:
        raise P53V2Error("V2 profile parameters differ from frozen V1")
    if v2["architecture_layers"]["MARKET_STATE"]["severity_order"] != v1["severity_order"]:
        raise P53V2Error("V2 severity order differs from frozen V1")
    return v1


def market_state_transition_step(
    memory: TransitionMemory,
    raw_state: str,
    profile: dict,
    severity_order: list[str],
    *,
    ordinary_inputs_complete: bool,
    hard_flat_proven: bool = False,
) -> str:
    """V2 transition engine.

    This is intentionally the V1 R2 transition algorithm with one architecture
    change only: current MARKET_STATE=FLAT is allowed to enter the ordinary
    de-escalation path instead of being permanently absorbing.
    """

    if memory.current_state is None:
        if not ordinary_inputs_complete:
            return DIAGNOSTIC_DATA_INSUFFICIENT
        memory.current_state = "FLAT" if raw_state == "FLAT" else "NORMAL_BULL"
        memory.reset_counters()
        return memory.current_state

    if not ordinary_inputs_complete:
        memory.reset_counters()
        if hard_flat_proven:
            memory.current_state = "FLAT"
        return memory.current_state

    if raw_state == "FLAT":
        memory.current_state = "FLAT"
        memory.reset_counters()
        return memory.current_state

    index = {state: i for i, state in enumerate(severity_order)}
    current_i = index[memory.current_state]
    raw_i = index[raw_state]

    if raw_i > current_i:
        memory.deescalation_count = 0
        memory.escalation_raw_indices.append(raw_i)
        needed = int(profile["escalation_persistence_days"])
        if len(memory.escalation_raw_indices) >= needed:
            window = memory.escalation_raw_indices[-needed:]
            target_i = min(window)
            if target_i > current_i:
                memory.current_state = severity_order[target_i]
                memory.reset_counters()
        return memory.current_state

    if raw_i < current_i:
        memory.escalation_raw_indices = []
        memory.deescalation_count += 1
        needed = int(profile["deescalation_clear_days"])
        if memory.deescalation_count >= needed:
            memory.current_state = severity_order[current_i - 1]
            memory.reset_counters()
        return memory.current_state

    memory.reset_counters()
    return memory.current_state


def evaluate_profile_v2(
    feature_panel: pd.DataFrame,
    percentiles: pd.DataFrame,
    counts: pd.DataFrame,
    min_depth: pd.Series,
    v1_contract: dict,
    v2_contract: dict,
    profile_name: str,
) -> pd.DataFrame:
    profile = v2_contract["profiles"][profile_name]
    severity = list(v2_contract["architecture_layers"]["MARKET_STATE"]["severity_order"])
    continuous, raw_names = runtime_features(v1_contract)
    memory = TransitionMemory()
    rows: list[dict] = []

    for dt in feature_panel.index:
        p = percentiles.loc[dt]
        raw = feature_panel.loc[dt]
        ordinary_complete = bool(p[continuous].notna().all() and raw[raw_names].notna().all())

        atoms: AtomState | None = None
        candidate = DIAGNOSTIC_DATA_INSUFFICIENT if memory.current_state is None else DIAGNOSTIC_DATA_MISSING_HOLD
        hard_flat_proven = False

        if ordinary_complete:
            atoms = evidence_atoms(p, raw, profile)
            candidate = raw_candidate(atoms)
        elif memory.current_state is not None and _hard_flat_inputs_present(p):
            safe_raw = raw.copy()
            if (
                "canonical5_outperformance_breadth_20d" not in safe_raw.index
                or pd.isna(safe_raw["canonical5_outperformance_breadth_20d"])
            ):
                safe_raw["canonical5_outperformance_breadth_20d"] = 0.0
            atoms = evidence_atoms(p, safe_raw, profile)
            hard_flat_proven = bool(atoms.strong_damage and atoms.strong_exhaustion)

        state = market_state_transition_step(
            memory,
            candidate if candidate in severity else "NORMAL_BULL",
            profile,
            severity,
            ordinary_inputs_complete=ordinary_complete,
            hard_flat_proven=hard_flat_proven,
        )

        rows.append(
            {
                "date": dt,
                "profile": profile_name,
                "market_state": state,
                "raw_candidate_state": candidate,
                "ordinary_inputs_complete": ordinary_complete,
                "minimum_calibration_depth": int(min_depth.loc[dt]),
                "mature_texture": bool(atoms.mature_texture) if atoms else False,
                "rotation": bool(atoms.rotation) if atoms else False,
                "exhaustion": bool(atoms.exhaustion) if atoms else False,
                "strong_exhaustion": bool(atoms.strong_exhaustion) if atoms else False,
                "damage": bool(atoms.damage) if atoms else False,
                "strong_damage": bool(atoms.strong_damage) if atoms else False,
                "divergence_subchannel": bool(atoms.divergence_subchannel) if atoms else False,
                "momentum_failure_subchannel": bool(atoms.momentum_failure_subchannel) if atoms else False,
                "breadth_transition_subchannel": bool(atoms.breadth_transition_subchannel) if atoms else False,
            }
        )

    return pd.DataFrame(rows).set_index("date")


def evaluate_all_profiles_v2(
    feature_panel: pd.DataFrame | None = None,
    v2_contract: dict | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    v2 = v2_contract or load_v2_contract()
    v1 = inherited_v1_contract(v2)
    feature_panel = feature_panel if feature_panel is not None else load_feature_panel()
    pct, counts, min_depth = causal_percentiles(feature_panel, v1)
    paths = [
        evaluate_profile_v2(feature_panel, pct, counts, min_depth, v1, v2, name)
        for name in v2["profiles"]
    ]
    return pd.concat(paths).sort_index(), pct, counts


def evaluate_signal_only(
    feature_panel: pd.DataFrame | None = None,
    v2_contract: dict | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Evaluate inherited V1 signal evidence without computing V2 MARKET_STATE.

    Used by pre-run parity CI so the full historical V2 state path remains
    unobserved until implementation gates are green.
    """

    v2 = v2_contract or load_v2_contract()
    v1 = inherited_v1_contract(v2)
    feature_panel = feature_panel if feature_panel is not None else load_feature_panel()
    pct, counts, min_depth = causal_percentiles(feature_panel, v1)
    continuous, raw_names = runtime_features(v1)
    rows: list[dict] = []

    for profile_name, profile in v2["profiles"].items():
        for dt in feature_panel.index:
            p = pct.loc[dt]
            raw = feature_panel.loc[dt]
            ordinary_complete = bool(p[continuous].notna().all() and raw[raw_names].notna().all())
            atoms: AtomState | None = None
            candidate = DIAGNOSTIC_DATA_INSUFFICIENT
            if ordinary_complete:
                atoms = evidence_atoms(p, raw, profile)
                candidate = raw_candidate(atoms)
            rows.append(
                {
                    "date": dt,
                    "profile": profile_name,
                    "raw_candidate_state": candidate,
                    "ordinary_inputs_complete": ordinary_complete,
                    "minimum_calibration_depth": int(min_depth.loc[dt]),
                    "mature_texture": bool(atoms.mature_texture) if atoms else False,
                    "rotation": bool(atoms.rotation) if atoms else False,
                    "exhaustion": bool(atoms.exhaustion) if atoms else False,
                    "strong_exhaustion": bool(atoms.strong_exhaustion) if atoms else False,
                    "damage": bool(atoms.damage) if atoms else False,
                    "strong_damage": bool(atoms.strong_damage) if atoms else False,
                    "divergence_subchannel": bool(atoms.divergence_subchannel) if atoms else False,
                    "momentum_failure_subchannel": bool(atoms.momentum_failure_subchannel) if atoms else False,
                    "breadth_transition_subchannel": bool(atoms.breadth_transition_subchannel) if atoms else False,
                }
            )

    return pd.DataFrame(rows).set_index(["date", "profile"]).sort_index(), pct, counts
