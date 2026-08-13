from __future__ import annotations

import math
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd

RESEARCH_ID = "BRRK-BTC-CASH-ABSOLUTE-RISK-DIAGNOSTIC-0060"
DATASET_SLICE_REF = "BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1"
EXPECTED_PAYLOAD_SHA256 = "d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193"
HORIZONS: Tuple[int, ...] = (20, 60, 120, 240)
FAST_WEIGHTS = (0.15, 0.25, 0.30, 0.30)
SLOW_WEIGHTS = (0.10, 0.20, 0.30, 0.40)
TARGET_KEYS = tuple([f"terminal_loss_{h}" for h in HORIZONS] + [f"adverse_excursion_{h}" for h in HORIZONS])
MIN_SHARED_ORIGINS = 1440
BOOTSTRAP_BLOCK = 240
BOOTSTRAP_REPS = 10000
BOOTSTRAP_SEED = 1844716895

CLASS_INVALID = "INVALID_EXECUTION"
CLASS_SUPPORT = "FAIL_INSUFFICIENT_CAUSAL_SUPPORT"
CLASS_INFO = "FAIL_NO_JOINT_DOWNSIDE_INFORMATION"
CLASS_TEMPORAL = "FAIL_TEMPORAL_INSTABILITY"
CLASS_DEP = "FAIL_DEPENDENCE_AWARE_ROBUSTNESS"
CLASS_PASS = "PASS_ABSOLUTE_RISK_INFORMATION_STAGE_ELIGIBLE"


def validate_payload_identity(payload_sha256: str) -> None:
    if payload_sha256 != EXPECTED_PAYLOAD_SHA256:
        raise ValueError("0060 immutable payload SHA256 mismatch")


def validate_price_frame(frame: pd.DataFrame, require_frozen_calendar: bool = True) -> pd.Series:
    if not isinstance(frame, pd.DataFrame) or "close" not in frame.columns:
        raise ValueError("price frame must be a DataFrame containing close")
    if not isinstance(frame.index, pd.DatetimeIndex):
        raise ValueError("price index must be DatetimeIndex")
    if frame.index.tz is not None:
        raise ValueError("frozen source representation is UTC-normalized tz-naive")
    if frame.index.has_duplicates or not frame.index.is_monotonic_increasing:
        raise ValueError("price index must be unique and increasing")
    if require_frozen_calendar:
        if len(frame) != 2183 or frame.index[0] != pd.Timestamp("2020-08-11") or frame.index[-1] != pd.Timestamp("2026-08-02"):
            raise ValueError("frozen calendar mismatch")
        expected = pd.date_range("2020-08-11", "2026-08-02", freq="D")
        if not frame.index.equals(expected):
            raise ValueError("frozen calendar must be contiguous UTC daily labels")
    p = pd.to_numeric(frame["close"], errors="coerce").astype(float)
    if p.isna().any() or not np.isfinite(p.to_numpy()).all() or (p <= 0).any():
        raise ValueError("close values must be finite and strictly positive")
    return p


def _trend_component(price: pd.Series, h: int) -> pd.Series:
    lr = np.log(price).diff()
    vol = lr.rolling(h, min_periods=h).std(ddof=1)
    denom = vol * math.sqrt(h)
    x = np.log(price / price.shift(h)) / denom
    x = x.where(denom > 0)
    return np.tanh(x)


def _weighted_trend(price: pd.Series, weights: Iterable[float]) -> pd.Series:
    comps = pd.concat([_trend_component(price, h) for h in HORIZONS], axis=1)
    w = np.asarray(tuple(weights), dtype=float)
    out = comps.mul(w, axis=1).sum(axis=1, min_count=len(HORIZONS))
    return out


def _disagreement_persistence(fast: pd.Series, slow: pd.Series) -> pd.Series:
    vals = []
    count = 0
    for f, s in zip(fast.to_numpy(), slow.to_numpy()):
        if not np.isfinite(f) or not np.isfinite(s):
            count = 0
            vals.append(np.nan)
        elif f < s:
            count += 1
            vals.append(float(count))
        else:
            count = 0
            vals.append(0.0)
    return pd.Series(vals, index=fast.index, dtype=float)


def causal_z(s: pd.Series) -> pd.Series:
    mean = s.rolling(252, min_periods=60).mean()
    std = s.rolling(252, min_periods=60).std(ddof=1)
    z = (s - mean) / std
    z = z.where(std > 0)
    return z.clip(-3.0, 3.0)


def _recent_high_age(x: np.ndarray) -> float:
    if len(x) != 60 or not np.isfinite(x).all():
        return np.nan
    m = np.max(x)
    positions = np.flatnonzero(x == m)
    return float(len(x) - 1 - positions[-1])


def _semivol_log_ratio(x: np.ndarray) -> float:
    if len(x) != 20 or not np.isfinite(x).all():
        return np.nan
    neg = x[x < 0]
    pos = x[x > 0]
    if len(neg) == 0 or len(pos) == 0:
        return np.nan
    down = math.sqrt(float(np.mean(neg * neg)))
    up = math.sqrt(float(np.mean(pos * pos)))
    if down <= 0 or up <= 0:
        return np.nan
    return math.log(down / up)


def build_state_panel(frame: pd.DataFrame, require_frozen_calendar: bool = True) -> pd.DataFrame:
    p = validate_price_frame(frame, require_frozen_calendar=require_frozen_calendar)
    logp = np.log(p)
    r = logp.diff()

    fast = _weighted_trend(p, FAST_WEIGHTS)
    slow = _weighted_trend(p, SLOW_WEIGHTS)
    a1a = slow - fast
    a1b = _disagreement_persistence(fast, slow)

    high60 = p.rolling(60, min_periods=60).max()
    a2a = np.log(high60 / p)
    a2b = p.rolling(60, min_periods=60).apply(_recent_high_age, raw=True)
    ma20 = p.rolling(20, min_periods=20).mean()
    a2c = -np.log(ma20 / ma20.shift(10))

    rv10 = r.rolling(10, min_periods=10).std(ddof=1)
    rv30 = r.rolling(30, min_periods=30).std(ddof=1)
    a3a = np.log(rv10 / rv30).where((rv10 > 0) & (rv30 > 0))
    a3b = r.rolling(20, min_periods=20).apply(_semivol_log_ratio, raw=True)
    a3c = r.rolling(20, min_periods=20).apply(lambda x: float(np.sum(x < 0)) / 20.0 if np.isfinite(x).all() else np.nan, raw=True)

    raw = {
        "A1a_raw": a1a,
        "A1b_raw": a1b,
        "A2a_raw": a2a,
        "A2b_raw": a2b,
        "A2c_raw": a2c,
        "A3a_raw": a3a,
        "A3b_raw": a3b,
        "A3c_raw": a3c,
    }
    out = pd.DataFrame(raw, index=p.index)
    zcols = []
    for name, series in raw.items():
        zname = name.replace("_raw", "_z")
        out[zname] = causal_z(series)
        zcols.append(zname)

    def strict_mean(names):
        x = out[names]
        return x.mean(axis=1).where(x.notna().all(axis=1))

    out["A1"] = strict_mean(["A1a_z", "A1b_z"])
    out["A2"] = strict_mean(["A2a_z", "A2b_z", "A2c_z"])
    out["A3"] = strict_mean(["A3a_z", "A3b_z", "A3c_z"])
    out["S"] = strict_mean(["A1", "A2", "A3"])
    return out


def build_target_panel(frame: pd.DataFrame, require_frozen_calendar: bool = True) -> pd.DataFrame:
    p = validate_price_frame(frame, require_frozen_calendar=require_frozen_calendar)
    out = pd.DataFrame(index=p.index)
    for h in HORIZONS:
        terminal = -np.log(p.shift(-h) / p)
        out[f"terminal_loss_{h}"] = terminal.clip(lower=0.0)
        future_losses = pd.concat([(-np.log(p.shift(-u) / p)).clip(lower=0.0) for u in range(1, h + 1)], axis=1)
        ae = future_losses.max(axis=1, skipna=False)
        out[f"adverse_excursion_{h}"] = ae
    return out


def _assign_blocks(n: int) -> np.ndarray:
    q, r = divmod(n, 4)
    ids = []
    for b in range(4):
        ids.extend([b + 1] * (q + (1 if b < r else 0)))
    return np.asarray(ids, dtype=int)


def build_shared_panel(frame: pd.DataFrame, require_frozen_calendar: bool = True) -> pd.DataFrame:
    state = build_state_panel(frame, require_frozen_calendar=require_frozen_calendar)
    target = build_target_panel(frame, require_frozen_calendar=require_frozen_calendar)
    cols = list(state.columns) + list(TARGET_KEYS)
    panel = pd.concat([state, target], axis=1)[cols].dropna().copy()
    panel.insert(0, "origin_date", panel.index.strftime("%Y-%m-%d"))
    panel["chronological_block_id"] = _assign_blocks(len(panel))
    return panel.reset_index(drop=True)


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, dtype=float)
    y = np.asarray(y, dtype=float)
    mask = np.isfinite(x) & np.isfinite(y)
    x, y = x[mask], y[mask]
    if len(x) < 2 or np.all(x == x[0]) or np.all(y == y[0]):
        return float("nan")
    rx = pd.Series(x).rank(method="average").to_numpy(dtype=float)
    ry = pd.Series(y).rank(method="average").to_numpy(dtype=float)
    return float(np.corrcoef(rx, ry)[0, 1])


def _rho_map(panel: pd.DataFrame, state_col: str = "S") -> Dict[str, float]:
    x = panel[state_col].to_numpy(float)
    return {k: spearman(x, panel[k].to_numpy(float)) for k in TARGET_KEYS}


def _effective_rank(corr: np.ndarray) -> Tuple[list, float]:
    eig = np.linalg.eigvalsh(corr)
    eig = np.maximum(eig, 0.0)
    total = eig.sum()
    if total <= 0:
        return eig.tolist(), float("nan")
    p = eig / total
    p = p[p > 0]
    er = float(np.exp(-np.sum(p * np.log(p))))
    return eig.tolist(), er


def _mbb_indices(n: int, block: int, rng: np.random.Generator) -> np.ndarray:
    if n < block:
        raise ValueError("sample shorter than bootstrap block")
    chunks = []
    need = n
    while need > 0:
        start = int(rng.integers(0, n - block + 1))
        take = min(block, need)
        chunks.append(np.arange(start, start + take, dtype=int))
        need -= take
    return np.concatenate(chunks)


def simultaneous_bootstrap(panel: pd.DataFrame, observed: Dict[str, float], reps: int = BOOTSTRAP_REPS, seed: int = BOOTSTRAP_SEED, block: int = BOOTSTRAP_BLOCK) -> Tuple[float, Dict[str, float]]:
    if any(not np.isfinite(observed[k]) for k in TARGET_KEYS):
        return float("nan"), {k: float("nan") for k in TARGET_KEYS}
    rng = np.random.default_rng(seed)
    n = len(panel)
    s = panel["S"].to_numpy(float)
    ys = {k: panel[k].to_numpy(float) for k in TARGET_KEYS}
    errors = np.empty(reps, dtype=float)
    for b in range(reps):
        idx = _mbb_indices(n, block, rng)
        boot = [spearman(s[idx], ys[k][idx]) for k in TARGET_KEYS]
        if any(not np.isfinite(v) for v in boot):
            errors[b] = np.nan
        else:
            errors[b] = max(observed[k] - v for k, v in zip(TARGET_KEYS, boot))
    if not np.isfinite(errors).all():
        return float("nan"), {k: float("nan") for k in TARGET_KEYS}
    q95 = float(np.quantile(errors, 0.95, method="linear"))
    return q95, {k: float(observed[k] - q95) for k in TARGET_KEYS}


def classify(n: int, full_rho: Dict[str, float], temporal_positive_blocks: int, lcbs: Dict[str, float]) -> Tuple[str, dict]:
    g0 = True
    g1 = n >= MIN_SHARED_ORIGINS
    g2 = g1 and all(np.isfinite(full_rho[k]) and full_rho[k] > 0 for k in TARGET_KEYS)
    g3 = g2 and temporal_positive_blocks >= 3
    g4 = g3 and all(np.isfinite(lcbs[k]) and lcbs[k] > 0 for k in TARGET_KEYS)
    if not g1:
        c = CLASS_SUPPORT
    elif not g2:
        c = CLASS_INFO
    elif not g3:
        c = CLASS_TEMPORAL
    elif not g4:
        c = CLASS_DEP
    else:
        c = CLASS_PASS
    return c, {"G0": g0, "G1": g1, "G2": g2, "G3": g3, "G4": g4}


def evaluate(frame: pd.DataFrame, payload_sha256: str, require_frozen_calendar: bool = True, bootstrap_reps: int = BOOTSTRAP_REPS) -> dict:
    validate_payload_identity(payload_sha256)
    panel = build_shared_panel(frame, require_frozen_calendar=require_frozen_calendar)
    n = len(panel)
    full = _rho_map(panel)

    temporal = {}
    pos_blocks = 0
    for b in range(1, 5):
        sub = panel[panel["chronological_block_id"] == b]
        rhos = _rho_map(sub)
        temporal[str(b)] = rhos
        if all(np.isfinite(rhos[k]) and rhos[k] > 0 for k in TARGET_KEYS):
            pos_blocks += 1

    axis_target = {axis: _rho_map(panel, axis) for axis in ("A1", "A2", "A3")}
    axis_corr = panel[["A1", "A2", "A3"]].corr(method="spearman").to_numpy(float)
    eig, erank = _effective_rank(axis_corr)
    terminal_pos = {str(h): float((panel[f"terminal_loss_{h}"] > 0).mean()) for h in HORIZONS}

    q95, lcbs = simultaneous_bootstrap(panel, full, reps=bootstrap_reps)
    classification, gates = classify(n, full, pos_blocks, lcbs)

    origin_fields = [
        "origin_date", "A1a_raw", "A1b_raw", "A2a_raw", "A2b_raw", "A2c_raw", "A3a_raw", "A3b_raw", "A3c_raw",
        "A1a_z", "A1b_z", "A2a_z", "A2b_z", "A2c_z", "A3a_z", "A3b_z", "A3c_z", "A1", "A2", "A3", "S",
        *TARGET_KEYS, "chronological_block_id",
    ]
    clean_panel = panel[origin_fields].replace({np.nan: None}).to_dict(orient="records")
    return {
        "research_id": RESEARCH_ID,
        "classification": classification,
        "gates": gates,
        "shared_origin_count": n,
        "shared_origin_start": panel.iloc[0]["origin_date"] if n else None,
        "shared_origin_end": panel.iloc[-1]["origin_date"] if n else None,
        "full_sample_rho_by_target": full,
        "temporal_block_rho_by_target": temporal,
        "temporal_positive_all_eight_blocks": pos_blocks,
        "bootstrap_q95": q95,
        "simultaneous_lcb_by_target": lcbs,
        "axis_target_spearman": axis_target,
        "axis_redundancy_matrix": axis_corr.tolist(),
        "axis_eigenvalues": eig,
        "axis_effective_rank": erank,
        "terminal_positive_rate_by_horizon": terminal_pos,
        "actual_variants_evaluated": 1,
        "data_budget": "DEVELOPMENT",
        "independent_oos": False,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
        "origin_panel": clean_panel,
    }
