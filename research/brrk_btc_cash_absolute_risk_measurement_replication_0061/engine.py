from __future__ import annotations

import importlib.util
import math
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd

RESEARCH_ID = "BRRK-BTC-CASH-ABSOLUTE-RISK-MEASUREMENT-REPLICATION-0061"
UPSTREAM_RESEARCH_ID = "BRRK-BTC-CASH-ABSOLUTE-RISK-DIAGNOSTIC-0060"
UPSTREAM_ENGINE_GIT_BLOB_SHA = "b901774b6849c9bcf6fbbf9887022142bf74a42d"
DATASET_SLICE_REF = "BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1"
EXPECTED_PAYLOAD_SHA256 = "d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193"
HORIZONS: Tuple[int, ...] = (20, 60, 120, 240)
TARGET_KEYS = tuple([f"terminal_loss_{h}" for h in HORIZONS] + [f"adverse_excursion_{h}" for h in HORIZONS])
MIN_SHARED_ORIGINS = 1440
BOOTSTRAP_BLOCK = 240
BOOTSTRAP_REPS = 10000
BOOTSTRAP_SEED = 1844716895
SPEARMAN_EQUIVALENCE_TOL = 1e-12

CLASS_INVALID = "INVALID_EXECUTION"
CLASS_SUPPORT = "FAIL_INSUFFICIENT_CAUSAL_SUPPORT"
CLASS_INFO = "FAIL_NO_JOINT_DOWNSIDE_INFORMATION"
CLASS_TEMPORAL = "FAIL_TEMPORAL_INSTABILITY"
CLASS_DEP = "FAIL_DEPENDENCE_AWARE_ROBUSTNESS"
CLASS_PASS = "PASS_ABSOLUTE_RISK_INFORMATION_STAGE_ELIGIBLE"


class MeasurementProtocolError(RuntimeError):
    pass


def _load_upstream_module():
    path = Path(__file__).resolve().parent.parent / "brrk_btc_cash_absolute_risk_diagnostic_0060" / "engine.py"
    spec = importlib.util.spec_from_file_location("brrk0060_immutable_engine", path)
    if spec is None or spec.loader is None:
        raise MeasurementProtocolError("unable to load immutable 0060 engine dependency")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    required = {
        "RESEARCH_ID": UPSTREAM_RESEARCH_ID,
        "EXPECTED_PAYLOAD_SHA256": EXPECTED_PAYLOAD_SHA256,
        "MIN_SHARED_ORIGINS": MIN_SHARED_ORIGINS,
        "BOOTSTRAP_BLOCK": BOOTSTRAP_BLOCK,
        "BOOTSTRAP_REPS": BOOTSTRAP_REPS,
        "BOOTSTRAP_SEED": BOOTSTRAP_SEED,
    }
    for name, expected in required.items():
        if getattr(mod, name, None) != expected:
            raise MeasurementProtocolError(f"immutable 0060 dependency mismatch: {name}")
    if tuple(getattr(mod, "TARGET_KEYS", ())) != TARGET_KEYS:
        raise MeasurementProtocolError("immutable 0060 target-key mismatch")
    return mod


_UPSTREAM = _load_upstream_module()


def validate_payload_identity(payload_sha256: str) -> None:
    if payload_sha256 != EXPECTED_PAYLOAD_SHA256:
        raise MeasurementProtocolError("0061 immutable payload SHA256 mismatch")


def build_shared_panel(frame: pd.DataFrame, require_frozen_calendar: bool = True) -> pd.DataFrame:
    """Delegate state, targets, complete-case origins and block ids byte-for-mechanism to 0060."""
    return _UPSTREAM.build_shared_panel(frame, require_frozen_calendar=require_frozen_calendar)


def ordinary_spearman(x: np.ndarray, y: np.ndarray) -> float:
    return float(_UPSTREAM.spearman(np.asarray(x, dtype=float), np.asarray(y, dtype=float)))


def _null_target_map() -> Dict[str, None]:
    return {k: None for k in TARGET_KEYS}


def _finite_or_none(value):
    try:
        x = float(value)
    except (TypeError, ValueError):
        return None
    return x if math.isfinite(x) else None


def _finite_map(values: Dict[str, float]) -> Dict[str, float | None]:
    return {k: _finite_or_none(values.get(k)) for k in TARGET_KEYS}


def _rho_map(panel: pd.DataFrame, state_col: str = "S") -> Dict[str, float]:
    x = panel[state_col].to_numpy(dtype=float)
    return {k: ordinary_spearman(x, panel[k].to_numpy(dtype=float)) for k in TARGET_KEYS}


def _standardized_full_midrank(values: np.ndarray) -> np.ndarray | None:
    x = np.asarray(values, dtype=float)
    if x.ndim != 1 or len(x) < 2 or not np.isfinite(x).all():
        return None
    rank = pd.Series(x).rank(method="average").to_numpy(dtype=float)
    centered = rank - float(rank.mean())
    rms = float(np.sqrt(np.mean(centered * centered)))
    if not math.isfinite(rms) or rms <= 0:
        return None
    score = centered / rms
    return score if np.isfinite(score).all() else None


def fixed_score_setup(panel: pd.DataFrame) -> tuple[np.ndarray | None, Dict[str, np.ndarray] | None, Dict[str, float] | None, float | None]:
    u = _standardized_full_midrank(panel["S"].to_numpy(dtype=float))
    if u is None:
        return None, None, None, None
    vs: Dict[str, np.ndarray] = {}
    observed: Dict[str, float] = {}
    max_error = 0.0
    for k in TARGET_KEYS:
        v = _standardized_full_midrank(panel[k].to_numpy(dtype=float))
        if v is None:
            return None, None, None, None
        a = float(np.mean(u * v))
        rho = ordinary_spearman(panel["S"].to_numpy(dtype=float), panel[k].to_numpy(dtype=float))
        if not math.isfinite(a) or not math.isfinite(rho):
            raise MeasurementProtocolError("nonfinite full-panel fixed-score/Spearman identity")
        err = abs(a - rho)
        max_error = max(max_error, err)
        vs[k] = v
        observed[k] = a
    if max_error > SPEARMAN_EQUIVALENCE_TOL:
        raise MeasurementProtocolError(
            f"fixed-score observed statistic drifted from ordinary Spearman: {max_error} > {SPEARMAN_EQUIVALENCE_TOL}"
        )
    return u, vs, observed, float(max_error)


def _mbb_indices(n: int, block: int, rng: np.random.Generator) -> np.ndarray:
    if n < block or block <= 0:
        raise MeasurementProtocolError("sample shorter than frozen bootstrap block")
    chunks = []
    need = n
    while need > 0:
        start = int(rng.integers(0, n - block + 1))
        take = min(block, need)
        chunks.append(np.arange(start, start + take, dtype=int))
        need -= take
    return np.concatenate(chunks)


def fixed_score_bootstrap(
    u: np.ndarray,
    vs: Dict[str, np.ndarray],
    observed: Dict[str, float],
    reps: int = BOOTSTRAP_REPS,
    seed: int = BOOTSTRAP_SEED,
    block: int = BOOTSTRAP_BLOCK,
) -> tuple[float, Dict[str, float]]:
    n = len(u)
    if reps <= 0:
        raise MeasurementProtocolError("bootstrap replicate count must be positive")
    if not np.isfinite(u).all() or any(not np.isfinite(v).all() or len(v) != n for v in vs.values()):
        raise MeasurementProtocolError("fixed-score bootstrap received invalid full-panel scores")
    if any(k not in observed or not math.isfinite(float(observed[k])) for k in TARGET_KEYS):
        raise MeasurementProtocolError("fixed-score bootstrap missing finite observed association")
    rng = np.random.default_rng(seed)
    errors = np.empty(reps, dtype=float)
    products = {k: u * vs[k] for k in TARGET_KEYS}
    for b in range(reps):
        idx = _mbb_indices(n, block, rng)
        boot = {k: float(np.mean(products[k][idx])) for k in TARGET_KEYS}
        if any(not math.isfinite(v) for v in boot.values()):
            raise MeasurementProtocolError("fixed-score replicate unexpectedly nonfinite")
        errors[b] = max(float(observed[k]) - boot[k] for k in TARGET_KEYS)
    if not np.isfinite(errors).all():
        raise MeasurementProtocolError("fixed-score simultaneous-error vector nonfinite")
    q95 = float(np.quantile(errors, 0.95, method="linear"))
    lcbs = {k: float(observed[k] - q95) for k in TARGET_KEYS}
    if not math.isfinite(q95) or any(not math.isfinite(v) for v in lcbs.values()):
        raise MeasurementProtocolError("fixed-score simultaneous lower bounds nonfinite")
    return q95, lcbs


def _temporal_results(panel: pd.DataFrame) -> tuple[dict, int]:
    temporal = {}
    positive = 0
    for b in range(1, 5):
        sub = panel[panel["chronological_block_id"] == b]
        rhos = _rho_map(sub)
        temporal[str(b)] = _finite_map(rhos)
        if all(math.isfinite(rhos[k]) and rhos[k] > 0 for k in TARGET_KEYS):
            positive += 1
    return temporal, positive


def _axis_diagnostics(panel: pd.DataFrame) -> tuple[dict, list, list, float | None, dict]:
    axis_target = {}
    for axis in ("A1", "A2", "A3"):
        axis_target[axis] = _finite_map(_rho_map(panel, axis))
    corr = panel[["A1", "A2", "A3"]].corr(method="spearman").to_numpy(dtype=float)
    corr_out = [[_finite_or_none(x) for x in row] for row in corr]
    eig_out = []
    erank = None
    if np.isfinite(corr).all():
        eig = np.maximum(np.linalg.eigvalsh(corr), 0.0)
        eig_out = [float(x) for x in eig]
        total = float(eig.sum())
        if total > 0:
            p = eig / total
            p = p[p > 0]
            erank = float(np.exp(-np.sum(p * np.log(p))))
    terminal_pos = {str(h): float((panel[f"terminal_loss_{h}"] > 0).mean()) for h in HORIZONS}
    return axis_target, corr_out, eig_out, erank, terminal_pos


def _origin_panel(panel: pd.DataFrame) -> list[dict]:
    fields = [
        "origin_date", "A1a_raw", "A1b_raw", "A2a_raw", "A2b_raw", "A2c_raw", "A3a_raw", "A3b_raw", "A3c_raw",
        "A1a_z", "A1b_z", "A2a_z", "A2b_z", "A2c_z", "A3a_z", "A3b_z", "A3c_z", "A1", "A2", "A3", "S",
        *TARGET_KEYS, "chronological_block_id",
    ]
    return panel[fields].to_dict(orient="records")


def _fixed_score_panel(panel: pd.DataFrame, u: np.ndarray, vs: Dict[str, np.ndarray]) -> list[dict]:
    out = pd.DataFrame({"origin_date": panel["origin_date"].astype(str), "U_S": u})
    for k in TARGET_KEYS:
        out[f"V_{k}"] = vs[k]
    return out.to_dict(orient="records")


def evaluate(
    frame: pd.DataFrame,
    payload_sha256: str,
    require_frozen_calendar: bool = True,
    bootstrap_reps: int = BOOTSTRAP_REPS,
) -> dict:
    validate_payload_identity(payload_sha256)
    panel = build_shared_panel(frame, require_frozen_calendar=require_frozen_calendar)
    n = len(panel)
    axis_target, axis_corr, eig, erank, terminal_pos = _axis_diagnostics(panel) if n >= 2 else ({}, [], [], None, {})

    full_out: Dict[str, float | None] = _null_target_map()
    temporal_out = {str(b): _null_target_map() for b in range(1, 5)}
    temporal_positive = None
    fixed_observed: Dict[str, float | None] = _null_target_map()
    eq_error = None
    q95 = None
    lcbs: Dict[str, float | None] = _null_target_map()
    fixed_panel = None
    reason = None

    gates = {"G0": True, "G1": n >= MIN_SHARED_ORIGINS, "G2": None, "G3": None, "G4": None}
    if not gates["G1"]:
        classification = CLASS_SUPPORT
        reason = "G2_G3_G4_NOT_EVALUATED_DUE_TO_G1_SUPPORT_FAILURE"
    else:
        full = _rho_map(panel)
        full_out = _finite_map(full)
        gates["G2"] = all(math.isfinite(full[k]) and full[k] > 0 for k in TARGET_KEYS)
        if not gates["G2"]:
            classification = CLASS_INFO
            reason = "G3_G4_NOT_EVALUATED_DUE_TO_G2_NO_JOINT_DOWNSIDE_INFORMATION"
        else:
            temporal_out, temporal_positive = _temporal_results(panel)
            gates["G3"] = temporal_positive >= 3
            if not gates["G3"]:
                classification = CLASS_TEMPORAL
                reason = "G4_NOT_EVALUATED_DUE_TO_G3_TEMPORAL_INSTABILITY"
            else:
                u, vs, observed, eq_error = fixed_score_setup(panel)
                if u is None or vs is None or observed is None:
                    raise MeasurementProtocolError("G2 passed but full-panel fixed scores are undefined")
                fixed_observed = {k: float(observed[k]) for k in TARGET_KEYS}
                q95, lcb_raw = fixed_score_bootstrap(u, vs, observed, reps=bootstrap_reps)
                lcbs = {k: float(lcb_raw[k]) for k in TARGET_KEYS}
                gates["G4"] = all(lcbs[k] > 0 for k in TARGET_KEYS)
                classification = CLASS_PASS if gates["G4"] else CLASS_DEP
                fixed_panel = _fixed_score_panel(panel, u, vs)

    return {
        "schema_version": 1,
        "research_id": RESEARCH_ID,
        "upstream_research_id": UPSTREAM_RESEARCH_ID,
        "dataset_slice_ref": DATASET_SLICE_REF,
        "payload_sha256": payload_sha256,
        "classification": classification,
        "gates": gates,
        "shared_origin_count": int(n),
        "shared_origin_start": panel["origin_date"].iloc[0] if n else None,
        "shared_origin_end": panel["origin_date"].iloc[-1] if n else None,
        "full_sample_rho_by_target": full_out,
        "temporal_block_rho_by_target": temporal_out,
        "temporal_positive_block_count": temporal_positive,
        "fixed_score_observed_by_target": fixed_observed,
        "spearman_equivalence_max_abs_error": eq_error,
        "bootstrap_q95": q95,
        "simultaneous_lcb_by_target": lcbs,
        "downstream_not_evaluated_reason": reason,
        "axis_target_spearman": axis_target,
        "axis_redundancy_matrix": axis_corr,
        "axis_eigenvalues": eig,
        "axis_effective_rank": erank,
        "terminal_positive_rate_by_horizon": terminal_pos,
        "origin_panel": _origin_panel(panel) if n else [],
        "fixed_score_panel": fixed_panel,
        "actual_variants_evaluated": 1,
        "portfolio_economics_executed": False,
        "btc_cash_gross_map_executed": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
