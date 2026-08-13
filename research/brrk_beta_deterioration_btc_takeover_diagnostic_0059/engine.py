from __future__ import annotations

import math
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd
from scipy.stats import rankdata

RESEARCH_ID = "BRRK-BETA-DETERIORATION-BTC-TAKEOVER-DIAGNOSTIC-0059"
DATASET_SLICE_ID = "BRRK-LEADERSHIP-ROTATION-0048-EXPOSED-HIST-V1"
EXPECTED_PAYLOAD_SHA256 = "d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193"

ASSETS = ("BTC", "ETH", "SOL")
SOURCE_START = pd.Timestamp("2020-08-11")
SOURCE_END = pd.Timestamp("2026-08-02")
SOURCE_ROWS = 2183

HORIZONS = (20, 60, 120, 240)
FAST_WEIGHTS = (0.15, 0.25, 0.30, 0.30)
SLOW_WEIGHTS = (0.10, 0.20, 0.30, 0.40)
D2_HIGH_WINDOW = 60
CAUSAL_Z_WINDOW = 252
CAUSAL_Z_MIN_PERIODS = 60
CAUSAL_Z_CLIP = 3.0

MIN_SHARED_ORIGINS = 1440
TEMPORAL_BLOCK_COUNT = 4

BOOTSTRAP_BLOCK_LENGTH = 240
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 1_844_716_895
BOOTSTRAP_QUANTILE = 0.95

CLASSIFICATION_PRECEDENCE = (
    "INVALID_EXECUTION",
    "FAIL_INSUFFICIENT_CAUSAL_SUPPORT",
    "FAIL_NO_MONOTONE_CONTINUATION_INFORMATION",
    "FAIL_TEMPORAL_INSTABILITY",
    "FAIL_DEPENDENCE_AWARE_ROBUSTNESS",
    "PASS_MECHANISM_INFORMATION_STAGE_ELIGIBLE",
)

ORIGIN_PANEL_FIELDS = (
    "origin_date",
    "b_log_beta",
    "z_log_beta_over_btc",
    "D1_raw",
    "D2_raw",
    "D3_raw",
    "D1_z",
    "D2_z",
    "D3_z",
    "S",
    "WBTC_20",
    "WBETA_20",
    "Y_20",
    "WBTC_60",
    "WBETA_60",
    "Y_60",
    "WBTC_120",
    "WBETA_120",
    "Y_120",
    "WBTC_240",
    "WBETA_240",
    "Y_240",
    "chronological_block_id",
)


class DiagnosticProtocolError(RuntimeError):
    pass


def _finite_positive(values: Any, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    if arr.ndim != 1 or arr.size == 0:
        raise DiagnosticProtocolError(f"{name} must be a non-empty 1D array")
    if not np.isfinite(arr).all() or np.any(arr <= 0.0):
        raise DiagnosticProtocolError(f"{name} must be finite and strictly positive")
    return arr


def validate_payload_identity(payload_sha256: str) -> None:
    if str(payload_sha256).lower() != EXPECTED_PAYLOAD_SHA256:
        raise DiagnosticProtocolError("0059 payload SHA256 does not match frozen preregistration")


def validate_price_frames(
    frames: Mapping[str, pd.DataFrame],
    *,
    require_frozen_calendar: bool = True,
) -> pd.DataFrame:
    if set(frames) != set(ASSETS):
        raise DiagnosticProtocolError(f"frames must contain exactly {ASSETS}")

    indexes = [frames[a].index for a in ASSETS]
    if not all(indexes[0].equals(idx) for idx in indexes[1:]):
        raise DiagnosticProtocolError("BTC/ETH/SOL indexes must be identical")

    index = indexes[0]
    if not isinstance(index, pd.DatetimeIndex):
        raise DiagnosticProtocolError("price index must be a DatetimeIndex")
    if index.tz is not None:
        raise DiagnosticProtocolError("0059 source index must remain tz-naive UTC-normalized daily labels")
    if index.has_duplicates or not index.is_monotonic_increasing:
        raise DiagnosticProtocolError("price index must be unique and strictly increasing")
    if not index.equals(index.normalize()):
        raise DiagnosticProtocolError("price index must be midnight-normalized")
    if len(index) < max(HORIZONS) + CAUSAL_Z_MIN_PERIODS + 2:
        raise DiagnosticProtocolError("price history is too short for frozen state/target contract")

    prices = pd.DataFrame(index=index)
    for asset in ASSETS:
        if "close" not in frames[asset].columns:
            raise DiagnosticProtocolError(f"missing {asset} close")
        prices[asset] = _finite_positive(frames[asset]["close"].to_numpy(), f"{asset} close")

    if require_frozen_calendar:
        expected = pd.date_range(SOURCE_START, SOURCE_END, freq="D")
        if len(index) != SOURCE_ROWS or not index.equals(expected):
            raise DiagnosticProtocolError("frozen 0059 daily calendar mismatch")

    return prices


def trend_score(price: pd.Series, weights: Sequence[float]) -> pd.Series:
    weights = tuple(float(x) for x in weights)
    if len(weights) != len(HORIZONS):
        raise DiagnosticProtocolError("trend weight length mismatch")
    values = _finite_positive(price.to_numpy(), "trend price")
    series = pd.Series(values, index=price.index, dtype=float)
    lr = np.log(series).diff()
    out = pd.Series(0.0, index=series.index, dtype=float)
    valid = pd.Series(True, index=series.index)
    for horizon, weight in zip(HORIZONS, weights):
        momentum = np.log(series / series.shift(horizon))
        scale = lr.rolling(horizon).std() * math.sqrt(horizon)
        component = np.tanh(momentum / scale)
        out = out + weight * component
        valid &= component.notna()
    return out.where(valid)


def causal_z(series: pd.Series) -> pd.Series:
    mean = series.rolling(CAUSAL_Z_WINDOW, min_periods=CAUSAL_Z_MIN_PERIODS).mean()
    std = (
        series.rolling(CAUSAL_Z_WINDOW, min_periods=CAUSAL_Z_MIN_PERIODS)
        .std()
        .replace(0.0, np.nan)
    )
    return ((series - mean) / std).clip(-CAUSAL_Z_CLIP, CAUSAL_Z_CLIP)


def build_state_panel(prices: pd.DataFrame) -> pd.DataFrame:
    if set(prices.columns) != set(ASSETS):
        raise DiagnosticProtocolError("prices must contain exactly BTC/ETH/SOL")
    if not isinstance(prices.index, pd.DatetimeIndex):
        raise DiagnosticProtocolError("prices index must be DatetimeIndex")

    btc = pd.Series(_finite_positive(prices["BTC"].to_numpy(), "BTC close"), index=prices.index)
    eth = pd.Series(_finite_positive(prices["ETH"].to_numpy(), "ETH close"), index=prices.index)
    sol = pd.Series(_finite_positive(prices["SOL"].to_numpy(), "SOL close"), index=prices.index)

    b = 0.5 * np.log(eth) + 0.5 * np.log(sol)
    B = np.exp(b)
    z = b - np.log(btc)
    R = np.exp(z)

    fast_B = trend_score(B, FAST_WEIGHTS)
    slow_B = trend_score(B, SLOW_WEIGHTS)
    fast_R = trend_score(R, FAST_WEIGHTS)
    slow_R = trend_score(R, SLOW_WEIGHTS)

    d1 = slow_B - fast_B
    high60 = B.rolling(D2_HIGH_WINDOW, min_periods=D2_HIGH_WINDOW).max()
    d2 = np.log(high60 / B)
    d3 = slow_R - fast_R

    panel = pd.DataFrame(index=prices.index)
    panel["b_log_beta"] = b
    panel["z_log_beta_over_btc"] = z
    panel["D1_raw"] = d1
    panel["D2_raw"] = d2
    panel["D3_raw"] = d3
    panel["D1_z"] = causal_z(d1)
    panel["D2_z"] = causal_z(d2)
    panel["D3_z"] = causal_z(d3)
    panel["S"] = panel[["D1_z", "D2_z", "D3_z"]].mean(axis=1, skipna=False)
    return panel


def build_target_panel(prices: pd.DataFrame) -> pd.DataFrame:
    if set(prices.columns) != set(ASSETS):
        raise DiagnosticProtocolError("prices must contain exactly BTC/ETH/SOL")
    out = pd.DataFrame(index=prices.index)
    for horizon in HORIZONS:
        wbtc = prices["BTC"].shift(-horizon) / prices["BTC"]
        wbeta = 0.5 * (prices["ETH"].shift(-horizon) / prices["ETH"]) + 0.5 * (
            prices["SOL"].shift(-horizon) / prices["SOL"]
        )
        out[f"WBTC_{horizon}"] = wbtc
        out[f"WBETA_{horizon}"] = wbeta
        out[f"Y_{horizon}"] = np.log(wbtc / wbeta)
    return out


def _block_ids(n: int) -> np.ndarray:
    if n < TEMPORAL_BLOCK_COUNT:
        raise DiagnosticProtocolError("not enough rows for four chronological blocks")
    q, r = divmod(int(n), TEMPORAL_BLOCK_COUNT)
    sizes = [q + 1 if i < r else q for i in range(TEMPORAL_BLOCK_COUNT)]
    return np.concatenate(
        [np.full(size, i + 1, dtype=np.int64) for i, size in enumerate(sizes)]
    )


def build_shared_origin_panel(prices: pd.DataFrame) -> pd.DataFrame:
    state = build_state_panel(prices)
    target = build_target_panel(prices)
    merged = pd.concat([state, target], axis=1)
    required = [
        "b_log_beta",
        "z_log_beta_over_btc",
        "D1_raw",
        "D2_raw",
        "D3_raw",
        "D1_z",
        "D2_z",
        "D3_z",
        "S",
    ]
    for horizon in HORIZONS:
        required.extend([f"WBTC_{horizon}", f"WBETA_{horizon}", f"Y_{horizon}"])
    shared = merged.dropna(subset=required).copy()
    if shared.empty:
        shared.insert(0, "origin_date", pd.Series(dtype="string"))
        shared["chronological_block_id"] = pd.Series(dtype="int64")
        return shared.loc[:, list(ORIGIN_PANEL_FIELDS)]
    if not np.isfinite(shared[required].to_numpy(dtype=float)).all():
        raise DiagnosticProtocolError("shared origin panel contains nonfinite values")
    shared.insert(0, "origin_date", shared.index.strftime("%Y-%m-%dT00:00:00Z"))
    shared["chronological_block_id"] = _block_ids(len(shared))
    return shared.loc[:, list(ORIGIN_PANEL_FIELDS)]


def _average_ranks(values: Sequence[float]) -> np.ndarray:
    x = np.asarray(values, dtype=np.float64)
    if x.ndim != 1 or x.size == 0 or not np.isfinite(x).all():
        raise DiagnosticProtocolError("rank input must be finite non-empty 1D")
    return np.asarray(rankdata(x, method="average"), dtype=np.float64)


def spearman_rho(x: Sequence[float], y: Sequence[float]) -> float:
    a = np.asarray(x, dtype=np.float64)
    b = np.asarray(y, dtype=np.float64)
    if a.ndim != 1 or b.ndim != 1 or len(a) != len(b) or len(a) < 2:
        raise DiagnosticProtocolError("Spearman inputs must be aligned 1D arrays with >=2 rows")
    if not np.isfinite(a).all() or not np.isfinite(b).all():
        raise DiagnosticProtocolError("Spearman inputs must be finite")
    ra = _average_ranks(a)
    rb = _average_ranks(b)
    da = ra - float(np.mean(ra))
    db = rb - float(np.mean(rb))
    denom = math.sqrt(float(np.dot(da, da)) * float(np.dot(db, db)))
    if denom == 0.0:
        return float("nan")
    return float(np.dot(da, db) / denom)


def _finite_or_none(value: float) -> float | None:
    return float(value) if math.isfinite(float(value)) else None


def full_sample_rhos(origin_panel: pd.DataFrame) -> dict[str, float | None]:
    return {
        str(h): _finite_or_none(
            spearman_rho(origin_panel["S"].to_numpy(), origin_panel[f"Y_{h}"].to_numpy())
        )
        for h in HORIZONS
    }


def temporal_block_rhos(origin_panel: pd.DataFrame) -> dict[str, dict[str, float | None]]:
    out: dict[str, dict[str, float | None]] = {}
    for block_id in range(1, TEMPORAL_BLOCK_COUNT + 1):
        block = origin_panel.loc[origin_panel["chronological_block_id"] == block_id]
        out[str(block_id)] = {
            str(h): _finite_or_none(
                spearman_rho(block["S"].to_numpy(), block[f"Y_{h}"].to_numpy())
            )
            for h in HORIZONS
        }
    return out


def component_target_spearman(origin_panel: pd.DataFrame) -> dict[str, dict[str, float | None]]:
    out: dict[str, dict[str, float | None]] = {}
    for axis in ("D1_z", "D2_z", "D3_z"):
        out[axis] = {
            str(h): _finite_or_none(
                spearman_rho(origin_panel[axis].to_numpy(), origin_panel[f"Y_{h}"].to_numpy())
            )
            for h in HORIZONS
        }
    return out


def component_redundancy(
    origin_panel: pd.DataFrame,
) -> tuple[list[list[float | None]], list[float] | None, float | None]:
    axes = ("D1_z", "D2_z", "D3_z")
    matrix = np.eye(3, dtype=np.float64)
    finite = True
    for i in range(3):
        for j in range(i + 1, 3):
            rho = spearman_rho(origin_panel[axes[i]].to_numpy(), origin_panel[axes[j]].to_numpy())
            if not math.isfinite(rho):
                finite = False
            matrix[i, j] = matrix[j, i] = rho
    rendered = [
        [_finite_or_none(float(matrix[i, j])) for j in range(3)]
        for i in range(3)
    ]
    if not finite:
        return rendered, None, None
    eigenvalues = np.linalg.eigvalsh(matrix)
    nonnegative = np.clip(eigenvalues, 0.0, None)
    total = float(nonnegative.sum())
    if total <= 0.0:
        effective_rank = 0.0
    else:
        p = nonnegative / total
        positive = p[p > 0.0]
        effective_rank = float(np.exp(-np.sum(positive * np.log(positive))))
    return rendered, [float(x) for x in eigenvalues], effective_rank


def _bootstrap_rhos(
    state: Sequence[float],
    targets: np.ndarray,
    *,
    block_length: int,
    replicates: int,
    seed: int,
) -> np.ndarray:
    s = np.asarray(state, dtype=np.float64)
    y = np.asarray(targets, dtype=np.float64)
    if s.ndim != 1 or y.ndim != 2 or y.shape != (len(s), len(HORIZONS)):
        raise DiagnosticProtocolError("bootstrap state/target shape mismatch")
    if not np.isfinite(s).all() or not np.isfinite(y).all():
        raise DiagnosticProtocolError("bootstrap inputs must be finite")
    n = len(s)
    L = int(block_length)
    reps = int(replicates)
    if L <= 0 or L > n or reps <= 0:
        raise DiagnosticProtocolError("invalid moving-block bootstrap dimensions")
    max_start = n - L
    blocks_per = int(math.ceil(n / L))
    rng = np.random.default_rng(int(seed))
    out = np.empty((reps, len(HORIZONS)), dtype=np.float64)
    offsets = np.arange(L, dtype=np.int64)
    for b in range(reps):
        starts = rng.integers(0, max_start + 1, size=blocks_per)
        idx = (starts[:, None] + offsets[None, :]).reshape(-1)[:n]
        ss = s[idx]
        for j in range(len(HORIZONS)):
            rho = spearman_rho(ss, y[idx, j])
            if not math.isfinite(rho):
                raise DiagnosticProtocolError("bootstrap replicate Spearman became undefined")
            out[b, j] = rho
    return out


def simultaneous_bootstrap_lcbs(
    origin_panel: pd.DataFrame,
) -> tuple[dict[str, float], float, dict[str, float]]:
    observed_maybe = full_sample_rhos(origin_panel)
    if any(observed_maybe[str(h)] is None for h in HORIZONS):
        raise DiagnosticProtocolError("observed Spearman is undefined")
    observed = {str(h): float(observed_maybe[str(h)]) for h in HORIZONS}
    obs = np.array([observed[str(h)] for h in HORIZONS], dtype=np.float64)
    targets = np.column_stack([origin_panel[f"Y_{h}"].to_numpy(dtype=float) for h in HORIZONS])
    boot = _bootstrap_rhos(
        origin_panel["S"].to_numpy(dtype=float),
        targets,
        block_length=BOOTSTRAP_BLOCK_LENGTH,
        replicates=BOOTSTRAP_REPLICATES,
        seed=BOOTSTRAP_SEED,
    )
    max_error = np.max(obs[None, :] - boot, axis=1)
    q95 = float(np.quantile(max_error, BOOTSTRAP_QUANTILE, method="linear"))
    lcbs = {str(h): float(obs[i] - q95) for i, h in enumerate(HORIZONS)}
    return observed, q95, lcbs


def classification_from_gates(
    *,
    g1: bool,
    g2: bool | None,
    g3: bool | None,
    g4: bool | None,
) -> str:
    if not g1:
        return "FAIL_INSUFFICIENT_CAUSAL_SUPPORT"
    if g2 is not True:
        return "FAIL_NO_MONOTONE_CONTINUATION_INFORMATION"
    if g3 is not True:
        return "FAIL_TEMPORAL_INSTABILITY"
    if g4 is not True:
        return "FAIL_DEPENDENCE_AWARE_ROBUSTNESS"
    return "PASS_MECHANISM_INFORMATION_STAGE_ELIGIBLE"


def evaluate_frozen_contract(
    frames: Mapping[str, pd.DataFrame],
    payload_sha256: str,
) -> dict[str, Any]:
    validate_payload_identity(payload_sha256)
    prices = validate_price_frames(frames, require_frozen_calendar=True)
    origin_panel = build_shared_origin_panel(prices)
    n = int(len(origin_panel))

    gates: dict[str, bool | None] = {
        "G0_INTEGRITY": True,
        "G1_SUPPORT": n >= MIN_SHARED_ORIGINS,
        "G2_MONOTONE_INFORMATION": None,
        "G3_TEMPORAL_RECURRENCE": None,
        "G4_DEPENDENCE_AWARE_ROBUSTNESS": None,
    }

    full_rho: dict[str, float | None] | None = None
    temporal: dict[str, dict[str, float | None]] | None = None
    bootstrap_q95: float | None = None
    lcbs: dict[str, float] | None = None
    component_target: dict[str, dict[str, float | None]] | None = None
    redundancy_matrix: list[list[float | None]] | None = None
    eigenvalues: list[float] | None = None
    effective_rank: float | None = None

    if gates["G1_SUPPORT"]:
        full_rho = full_sample_rhos(origin_panel)
        finite_full = all(x is not None for x in full_rho.values())
        gates["G2_MONOTONE_INFORMATION"] = finite_full and all(
            float(x) > 0.0 for x in full_rho.values() if x is not None
        )

        temporal = temporal_block_rhos(origin_panel)
        positive_blocks = 0
        for row in temporal.values():
            if all(x is not None and float(x) > 0.0 for x in row.values()):
                positive_blocks += 1
        gates["G3_TEMPORAL_RECURRENCE"] = positive_blocks >= 3

        component_target = component_target_spearman(origin_panel)
        redundancy_matrix, eigenvalues, effective_rank = component_redundancy(origin_panel)

        if finite_full:
            observed_again, bootstrap_q95, lcbs = simultaneous_bootstrap_lcbs(origin_panel)
            for h in HORIZONS:
                if not math.isclose(
                    observed_again[str(h)], float(full_rho[str(h)]), rel_tol=0.0, abs_tol=1e-15
                ):
                    raise DiagnosticProtocolError("bootstrap observed statistic drift")
            gates["G4_DEPENDENCE_AWARE_ROBUSTNESS"] = all(
                math.isfinite(x) and x > 0.0 for x in lcbs.values()
            )
        else:
            gates["G4_DEPENDENCE_AWARE_ROBUSTNESS"] = False

    classification = classification_from_gates(
        g1=bool(gates["G1_SUPPORT"]),
        g2=gates["G2_MONOTONE_INFORMATION"],
        g3=gates["G3_TEMPORAL_RECURRENCE"],
        g4=gates["G4_DEPENDENCE_AWARE_ROBUSTNESS"],
    )

    return {
        "research_id": RESEARCH_ID,
        "classification": classification,
        "gates": gates,
        "shared_origin_count": n,
        "shared_origin_start": None if n == 0 else str(origin_panel.iloc[0]["origin_date"]),
        "shared_origin_end": None if n == 0 else str(origin_panel.iloc[-1]["origin_date"]),
        "full_sample_rho_by_horizon": full_rho,
        "temporal_block_rho_by_horizon": temporal,
        "bootstrap_q95": bootstrap_q95,
        "simultaneous_lcb_by_horizon": lcbs,
        "component_target_spearman": component_target,
        "component_redundancy_matrix": redundancy_matrix,
        "component_eigenvalues": eigenvalues,
        "component_effective_rank": effective_rank,
        "actual_variants_evaluated": 1,
        "origin_panel": origin_panel.to_dict(orient="records"),
        "authority": {
            "development_not_independent_oos": True,
            "researcher_exposed_history": True,
            "canonical_strategy_changed": False,
            "phase6_changed": False,
            "production_authorized_components": [],
            "production_authorized": False,
            "signature_authorized": False,
            "order_submission_authorized": False,
        },
    }
