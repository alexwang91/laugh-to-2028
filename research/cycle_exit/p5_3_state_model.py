from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "research" / "cycle_exit" / "p5_3_state_model_contract.json"
P52_FEATURE_PANEL = ROOT / "research" / "results" / "p5_2_feature_evidence" / "feature_panel.csv"

DIAGNOSTIC_DATA_INSUFFICIENT = "DATA_INSUFFICIENT"
DIAGNOSTIC_DATA_MISSING_HOLD = "DATA_MISSING_HOLD"


class P53Error(RuntimeError):
    pass


@dataclass(frozen=True)
class AtomState:
    mature_texture: bool
    rotation: bool
    exhaustion: bool
    strong_exhaustion: bool
    damage: bool
    strong_damage: bool
    divergence_subchannel: bool
    momentum_failure_subchannel: bool
    breadth_transition_subchannel: bool


@dataclass
class TransitionMemory:
    current_state: str | None = None
    escalation_raw_indices: list[int] | None = None
    deescalation_count: int = 0

    def __post_init__(self) -> None:
        if self.escalation_raw_indices is None:
            self.escalation_raw_indices = []

    def reset_counters(self) -> None:
        self.escalation_raw_indices = []
        self.deescalation_count = 0


def load_contract(path: Path = CONTRACT_PATH) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("contract_id") != "P5.3-STATE-MODEL-STRUCTURE-V1":
        raise P53Error("unexpected P5.3 contract id")
    if payload.get("status") != "FROZEN_BEFORE_STATE_PATH_EVALUATION":
        raise P53Error("P5.3 contract is not frozen")
    if payload.get("severity_order") != payload.get("states"):
        raise P53Error("severity order differs from state vocabulary")
    if payload["research_integrity"].get("production_authorization") != "NONE":
        raise P53Error("P5.3 cannot authorize production")
    return payload


def load_feature_panel(path: Path = P52_FEATURE_PANEL) -> pd.DataFrame:
    frame = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    if frame.index.has_duplicates:
        raise P53Error("duplicate feature-panel dates")
    return frame.astype(float)


def runtime_features(contract: dict) -> tuple[list[str], list[str]]:
    used = sorted({f for group in contract["runtime_feature_inputs"].values() for f in group})
    raw = sorted(contract.get("raw_fraction_inputs", {}).keys())
    continuous = sorted(set(used) - set(raw))
    return continuous, raw


def _average_rank_percentile(values: pd.Series) -> float:
    clean = values.dropna().astype(float)
    n = len(clean)
    if n < 2:
        return float("nan")
    ranks = clean.rank(method="average")
    return float((ranks.iloc[-1] - 1.0) / (n - 1.0))


def causal_percentiles(
    feature_panel: pd.DataFrame,
    contract: dict,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    continuous, _ = runtime_features(contract)
    missing = sorted(set(continuous) - set(feature_panel.columns))
    if missing:
        raise P53Error(f"runtime feature(s) missing from P5.2 panel: {missing}")

    cfg = contract["causal_normalization"]
    lookback = int(cfg["lookback_completed_daily_dates"])
    minimum = int(cfg["minimum_nonmissing_feature_observations"])

    pct = pd.DataFrame(np.nan, index=feature_panel.index, columns=continuous, dtype=float)
    counts = pd.DataFrame(0, index=feature_panel.index, columns=continuous, dtype=int)

    for feature in continuous:
        series = feature_panel[feature]
        for i, dt in enumerate(series.index):
            start = max(0, i - lookback + 1)
            window = series.iloc[start : i + 1].dropna()
            counts.loc[dt, feature] = int(len(window))
            if len(window) < minimum or pd.isna(series.iloc[i]):
                continue
            pct.loc[dt, feature] = _average_rank_percentile(window)

    min_depth = counts.min(axis=1).astype(int)
    return pct, counts, min_depth


def _ge(value: float, threshold: float) -> bool:
    return bool(np.isfinite(value) and value >= threshold)


def _le(value: float, threshold: float) -> bool:
    return bool(np.isfinite(value) and value <= threshold)


def evidence_atoms(
    percentiles: pd.Series,
    raw_features: pd.Series,
    profile: dict,
) -> AtomState:
    mh = float(profile["moderate_high_percentile"])
    sh = float(profile["strong_high_percentile"])
    ml = float(profile["moderate_low_percentile"])
    sl = float(profile["strong_low_percentile"])

    mature_flags = [
        _le(percentiles["btc_rv20_ann"], ml),
        _le(percentiles["btc_rv20_to_rv60"], ml),
        _ge(percentiles["btc_distance_from_90d_high"], mh),
        _ge(percentiles["btc_kama_gap"], 0.50),
    ]
    mature_texture = sum(mature_flags) >= 2

    breadth_raw = float(raw_features["canonical5_outperformance_breadth_20d"])
    rotation = _ge(percentiles["eth_btc_log_return_20d"], mh) and (
        _ge(percentiles["eth_btc_log_return_40d"], mh)
        or _ge(percentiles["breadth_acceleration_10d"], mh)
        or (np.isfinite(breadth_raw) and breadth_raw >= 0.75)
    )

    divergence = _ge(percentiles["btc_price_rsi_rank_divergence_20d"], mh)
    momentum_failure = _ge(percentiles["btc_rsi14_failure_from_14d_max"], mh) or (
        _ge(percentiles["btc_4h_rsi14"], mh) and _ge(percentiles["btc_4h_rsi28"], mh)
    )
    breadth_transition = _ge(percentiles["breadth_contraction_from_10d_max"], mh) or _le(
        percentiles["breadth_acceleration_10d"], ml
    )
    exhaustion_subchannels = [divergence, momentum_failure, breadth_transition]
    exhaustion = sum(exhaustion_subchannels) >= 2

    divergence_strong = _ge(percentiles["btc_price_rsi_rank_divergence_20d"], sh)
    additional_exhaustion = int(momentum_failure) + int(breadth_transition) >= 1
    strong_exhaustion = (divergence_strong and additional_exhaustion) or sum(exhaustion_subchannels) >= 3

    damage_flags = [
        _le(percentiles["btc_kama_gap"], ml),
        _le(percentiles["btc_distance_from_90d_high"], ml),
        _le(percentiles["btc_log_return_20d"], ml),
        _le(percentiles["btc_log_return_40d"], ml),
    ]
    damage = sum(damage_flags) >= 2

    strong_damage_flags = {
        "btc_kama_gap": _le(percentiles["btc_kama_gap"], sl),
        "btc_distance_from_90d_high": _le(percentiles["btc_distance_from_90d_high"], sl),
        "btc_log_return_20d": _le(percentiles["btc_log_return_20d"], sl),
        "btc_log_return_40d": _le(percentiles["btc_log_return_40d"], sl),
    }
    strong_damage = (
        sum(strong_damage_flags.values()) >= 2
        and (strong_damage_flags["btc_kama_gap"] or strong_damage_flags["btc_distance_from_90d_high"])
    )

    return AtomState(
        mature_texture=mature_texture,
        rotation=rotation,
        exhaustion=exhaustion,
        strong_exhaustion=strong_exhaustion,
        damage=damage,
        strong_damage=strong_damage,
        divergence_subchannel=divergence,
        momentum_failure_subchannel=momentum_failure,
        breadth_transition_subchannel=breadth_transition,
    )


def raw_candidate(atoms: AtomState) -> str:
    if atoms.strong_damage and atoms.strong_exhaustion:
        return "FLAT"
    if (atoms.strong_damage and atoms.exhaustion) or (atoms.damage and atoms.strong_exhaustion):
        return "DE_RISK_2"
    if atoms.damage and atoms.exhaustion:
        return "DE_RISK_1"
    if atoms.exhaustion or atoms.strong_exhaustion:
        return "EXHAUSTION_WATCH"
    if atoms.rotation and not atoms.damage:
        return "LATE_BULL_ROTATION"
    if atoms.mature_texture and not atoms.damage:
        return "BTC_LEADERSHIP_MATURING"
    return "NORMAL_BULL"


def _hard_flat_inputs_present(percentiles: pd.Series) -> bool:
    required = {
        "btc_kama_gap",
        "btc_distance_from_90d_high",
        "btc_log_return_20d",
        "btc_log_return_40d",
        "btc_price_rsi_rank_divergence_20d",
        "btc_rsi14_failure_from_14d_max",
        "btc_4h_rsi14",
        "btc_4h_rsi28",
        "breadth_acceleration_10d",
        "breadth_contraction_from_10d_max",
    }
    return all(f in percentiles.index and np.isfinite(percentiles[f]) for f in required)


def transition_step(
    memory: TransitionMemory,
    raw_state: str,
    profile: dict,
    severity_order: list[str],
    *,
    ordinary_inputs_complete: bool,
    hard_flat_proven: bool = False,
) -> str:
    if memory.current_state == "FLAT":
        memory.reset_counters()
        return "FLAT"

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


def evaluate_profile(
    feature_panel: pd.DataFrame,
    percentiles: pd.DataFrame,
    counts: pd.DataFrame,
    min_depth: pd.Series,
    contract: dict,
    profile_name: str,
) -> pd.DataFrame:
    profile = contract["profiles"][profile_name]
    severity = list(contract["severity_order"])
    continuous, raw_names = runtime_features(contract)
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
            # The hard-FLAT proof does not depend on raw breadth/rotation inputs.
            safe_raw = raw.copy()
            if "canonical5_outperformance_breadth_20d" not in safe_raw.index or pd.isna(safe_raw["canonical5_outperformance_breadth_20d"]):
                safe_raw["canonical5_outperformance_breadth_20d"] = 0.0
            atoms = evidence_atoms(p, safe_raw, profile)
            hard_flat_proven = bool(atoms.strong_damage and atoms.strong_exhaustion)

        state = transition_step(
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
                "state": state,
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


def evaluate_all_profiles(
    feature_panel: pd.DataFrame | None = None,
    contract: dict | None = None,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    contract = contract or load_contract()
    feature_panel = feature_panel if feature_panel is not None else load_feature_panel()
    pct, counts, min_depth = causal_percentiles(feature_panel, contract)
    paths = [evaluate_profile(feature_panel, pct, counts, min_depth, contract, name) for name in contract["profiles"]]
    return pd.concat(paths).sort_index(), pct, counts
