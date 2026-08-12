from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

RESEARCH_ID = "BRRK-BETA-BTC-CONTINUATION-PARAMETER-GEOMETRY-0058"
EXPECTED_PAYLOAD_SHA256 = "d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193"

SOURCE_START = pd.Timestamp("2020-08-11")
FIRST_ORIGIN = pd.Timestamp("2021-04-08")
LAST_ORIGIN = pd.Timestamp("2026-08-01")
TERMINAL_CLOSE = pd.Timestamp("2026-08-02")
SOURCE_ROWS = 2183
ORIGIN_OFFSET = 240
HELD_PERIODS = 1942
ANNUALIZATION_DAYS = 365.25

ASSETS = ("BTC", "ETH", "SOL")
BENCHMARKS = ("B0_STATIC_BTC", "B1_STATIC_BETA", "B2_STATIC_BTC_BETA")
L_VALUES = tuple(range(20, 241, 20))
KAPPA_VALUES = tuple(float(x) for x in np.arange(0.0, 2.0000001, 0.25))
COST_BPS = (5.0, 10.0, 20.0)
PRIMARY_COST_BPS = 5.0
STRESS_COST_BPS = (10.0, 20.0)

GRADIENT_THRESHOLD = math.log(1.05)
HESSIAN_THRESHOLD = math.log(1.10)
MIN_COMPONENT_CELLS = 9
MIN_DISTINCT_L = 3
MIN_DISTINCT_KAPPA = 3
PRIMARY_MARGIN_LOG_WEALTH = math.log(1.05)
STRICT_TOL = 1e-12

TEMPORAL_BLOCK_SIZES = (486, 486, 485, 485)
TEMPORAL_REQUIRED_WINS = 3

BOOTSTRAP_BLOCK_LENGTH = 60
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 1_844_716_895
BOOTSTRAP_BLOCKS_PER_REPLICATE = 33
BOOTSTRAP_QUANTILE = 0.95

CLASSIFICATION_PRECEDENCE = (
    "INVALID_EXECUTION",
    "FAIL_NO_STABLE_PARAMETER_PLATEAU",
    "FAIL_STABLE_PLATEAU_NOT_COST_ROBUST",
    "FAIL_STABLE_PLATEAU_NOT_ECONOMICALLY_RELEVANT",
    "FAIL_STABLE_PLATEAU_NOT_TEMPORALLY_OR_DEPENDENCE_ROBUST",
    "PASS_PARAMETER_FREEZE_ELIGIBLE",
)


class ParameterGeometryProtocolError(RuntimeError):
    pass


@dataclass(frozen=True)
class PortfolioPath:
    name: str
    cost_bps: float
    nav: np.ndarray
    period_factors: np.ndarray
    executed_l1_turnover: np.ndarray
    states: tuple[str, ...] | None
    pre_trade_nav: np.ndarray
    transaction_cost: np.ndarray
    post_trade_nav: np.ndarray

    @property
    def terminal_wealth(self) -> float:
        return float(self.nav[-1])

    @property
    def cagr(self) -> float:
        return float(self.terminal_wealth ** (ANNUALIZATION_DAYS / HELD_PERIODS) - 1.0)

    @property
    def drawdown(self) -> np.ndarray:
        running = np.maximum.accumulate(self.nav)
        return self.nav / running - 1.0

    @property
    def maximum_drawdown(self) -> float:
        return float(np.min(self.drawdown))

    @property
    def total_turnover(self) -> float:
        return float(np.sum(self.executed_l1_turnover))

    @property
    def switch_count(self) -> int:
        if self.states is None:
            return 0
        return int(sum(a != b for a, b in zip(self.states[:-1], self.states[1:])))

    @property
    def beta_holding_fraction(self) -> float:
        if self.states is None:
            return float("nan")
        if not self.states:
            return 0.0
        return float(sum(state == "BETA" for state in self.states) / len(self.states))


def _finite_positive(values: Any, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    if arr.ndim != 1 or arr.size == 0:
        raise ParameterGeometryProtocolError(f"{name} must be a non-empty 1D array")
    if not np.isfinite(arr).all() or np.any(arr <= 0.0):
        raise ParameterGeometryProtocolError(f"{name} must be finite and strictly positive")
    return arr


def _validate_cost(cost_bps: float) -> float:
    value = float(cost_bps)
    if not math.isfinite(value) or value < 0.0:
        raise ParameterGeometryProtocolError("cost_bps must be finite and non-negative")
    return value


def validate_payload_identity(payload_sha256: str) -> None:
    if str(payload_sha256).lower() != EXPECTED_PAYLOAD_SHA256:
        raise ParameterGeometryProtocolError("0058 payload SHA256 does not match frozen preregistration")


def validate_price_frames(
    frames: Mapping[str, pd.DataFrame],
    *,
    require_frozen_calendar: bool = True,
) -> pd.DataFrame:
    if set(frames) != set(ASSETS):
        raise ParameterGeometryProtocolError(f"frames must contain exactly {ASSETS}")

    indexes = [frames[a].index for a in ASSETS]
    if not all(indexes[0].equals(idx) for idx in indexes[1:]):
        raise ParameterGeometryProtocolError("BTC/ETH/SOL indexes must be identical")

    index = indexes[0]
    if not isinstance(index, pd.DatetimeIndex):
        raise ParameterGeometryProtocolError("price index must be a DatetimeIndex")
    if index.tz is not None:
        raise ParameterGeometryProtocolError("0058 source index must remain tz-naive UTC-normalized daily labels")
    if index.has_duplicates or not index.is_monotonic_increasing:
        raise ParameterGeometryProtocolError("price index must be unique and strictly increasing")
    if not index.equals(index.normalize()):
        raise ParameterGeometryProtocolError("price index must be midnight-normalized")
    if len(index) < ORIGIN_OFFSET + 2:
        raise ParameterGeometryProtocolError("price history is too short for one common causal held period")

    prices = pd.DataFrame(index=index)
    for asset in ASSETS:
        if "close" not in frames[asset].columns:
            raise ParameterGeometryProtocolError(f"missing {asset} close")
        prices[asset] = _finite_positive(frames[asset]["close"].to_numpy(), f"{asset} close")

    if require_frozen_calendar:
        expected = pd.date_range(SOURCE_START, TERMINAL_CLOSE, freq="D")
        if len(index) != SOURCE_ROWS or not index.equals(expected):
            raise ParameterGeometryProtocolError("frozen 0058 daily calendar mismatch")
        if index[ORIGIN_OFFSET] != FIRST_ORIGIN or index[-2] != LAST_ORIGIN or index[-1] != TERMINAL_CLOSE:
            raise ParameterGeometryProtocolError("frozen 0058 evaluation boundary mismatch")

    return prices


def relative_log_state(prices: pd.DataFrame) -> np.ndarray:
    for asset in ASSETS:
        if asset not in prices.columns:
            raise ParameterGeometryProtocolError(f"prices missing {asset}")
    btc = _finite_positive(prices["BTC"].to_numpy(), "BTC close")
    eth = _finite_positive(prices["ETH"].to_numpy(), "ETH close")
    sol = _finite_positive(prices["SOL"].to_numpy(), "SOL close")
    if not (btc.shape == eth.shape == sol.shape):
        raise ParameterGeometryProtocolError("close arrays must align")
    return 0.5 * (np.log(eth) - np.log(btc)) + 0.5 * (np.log(sol) - np.log(btc))


def sigma240_from_z(z: Sequence[float]) -> np.ndarray:
    z_arr = np.asarray(z, dtype=np.float64)
    if z_arr.ndim != 1 or len(z_arr) < ORIGIN_OFFSET + 2 or not np.isfinite(z_arr).all():
        raise ParameterGeometryProtocolError("z must be finite 1D with sufficient history")
    d = np.diff(z_arr)
    sigmas = np.empty(len(z_arr), dtype=np.float64)
    sigmas[:] = np.nan
    for pos in range(ORIGIN_OFFSET, len(z_arr)):
        window = d[pos - ORIGIN_OFFSET : pos]
        if len(window) != ORIGIN_OFFSET:
            raise ParameterGeometryProtocolError("sigma240 window length mismatch")
        sigma = float(np.std(window, ddof=1))
        if not math.isfinite(sigma) or sigma < 0.0:
            raise ParameterGeometryProtocolError("sigma240 became invalid")
        sigmas[pos] = sigma
    return sigmas


def score_series(prices: pd.DataFrame, L: int) -> np.ndarray:
    if int(L) not in L_VALUES:
        raise ParameterGeometryProtocolError("L is outside frozen lattice")
    z = relative_log_state(prices)
    sigma = sigma240_from_z(z)
    origins = range(ORIGIN_OFFSET, len(z) - 1)
    out = np.empty(len(z) - ORIGIN_OFFSET - 1, dtype=np.float64)
    for i, pos in enumerate(origins):
        denom = (sigma[pos] + STRICT_TOL) * math.sqrt(int(L))
        value = (z[pos] - z[pos - int(L)]) / denom
        if not math.isfinite(value):
            raise ParameterGeometryProtocolError("score became non-finite")
        out[i] = value
    return out


def states_from_scores(scores: Sequence[float], kappa: float) -> tuple[str, ...]:
    k = float(kappa)
    if k not in KAPPA_VALUES:
        raise ParameterGeometryProtocolError("kappa is outside frozen lattice")
    arr = np.asarray(scores, dtype=np.float64)
    if arr.ndim != 1 or not np.isfinite(arr).all():
        raise ParameterGeometryProtocolError("scores must be finite 1D")
    return tuple("BETA" if float(x) > k else "BTC" for x in arr)


def target_states(prices: pd.DataFrame, L: int, kappa: float) -> tuple[str, ...]:
    states = states_from_scores(score_series(prices, L), kappa)
    expected = len(prices) - ORIGIN_OFFSET - 1
    if len(states) != expected:
        raise ParameterGeometryProtocolError("state count mismatch")
    return states


def _period_ratios(prices: pd.DataFrame) -> dict[str, np.ndarray]:
    out: dict[str, np.ndarray] = {}
    for asset in ASSETS:
        values = _finite_positive(prices[asset].to_numpy(), f"{asset} close")
        ratios = values[ORIGIN_OFFSET + 1 :] / values[ORIGIN_OFFSET:-1]
        if not np.isfinite(ratios).all() or np.any(ratios <= 0.0):
            raise ParameterGeometryProtocolError("invalid close-to-close ratios")
        out[asset] = ratios.astype(np.float64, copy=False)
    return out


def simulate_candidate(prices: pd.DataFrame, states: Sequence[str], cost_bps: float) -> PortfolioPath:
    cost_bps = _validate_cost(cost_bps)
    states = tuple(str(x) for x in states)
    n = len(prices) - ORIGIN_OFFSET - 1
    if len(states) != n:
        raise ParameterGeometryProtocolError("candidate state count mismatch")
    if any(state not in ("BTC", "BETA") for state in states):
        raise ParameterGeometryProtocolError("candidate states must be BTC or BETA")

    ratios = _period_ratios(prices)
    nav = np.empty(n + 1, dtype=np.float64)
    nav[0] = 1.0
    factors = np.empty(n, dtype=np.float64)
    turnover = np.empty(n, dtype=np.float64)
    pre_trade_nav = np.empty(n, dtype=np.float64)
    transaction_cost = np.empty(n, dtype=np.float64)
    post_trade_nav = np.empty(n, dtype=np.float64)

    btc_value = 0.0
    eth_value = 0.0
    sol_value = 0.0
    prior_state: str | None = None
    rate = cost_bps / 10000.0

    for i, state in enumerate(states):
        pre = float(nav[i])
        pre_trade_nav[i] = pre
        l1 = 1.0 if prior_state is None else (2.0 if state != prior_state else 0.0)
        cost = pre * l1 * rate
        post = pre - cost
        if not math.isfinite(post) or post <= 0.0:
            raise ParameterGeometryProtocolError("transaction cost exhausted candidate NAV")
        turnover[i] = l1
        transaction_cost[i] = cost
        post_trade_nav[i] = post

        if prior_state is None or state != prior_state:
            if state == "BTC":
                btc_value, eth_value, sol_value = post, 0.0, 0.0
            else:
                btc_value, eth_value, sol_value = 0.0, 0.5 * post, 0.5 * post
        else:
            total = btc_value + eth_value + sol_value
            if not math.isclose(total, pre, rel_tol=1e-12, abs_tol=1e-12):
                raise ParameterGeometryProtocolError("component NAV failed pre-trade identity")
            if l1 != 0.0 or cost != 0.0:
                raise ParameterGeometryProtocolError("unchanged state must have zero turnover/cost")

        btc_value *= float(ratios["BTC"][i])
        eth_value *= float(ratios["ETH"][i])
        sol_value *= float(ratios["SOL"][i])
        next_nav = btc_value + eth_value + sol_value
        if not math.isfinite(next_nav) or next_nav <= 0.0:
            raise ParameterGeometryProtocolError("candidate NAV became invalid")
        nav[i + 1] = next_nav
        factors[i] = next_nav / pre
        prior_state = state

    return PortfolioPath(
        "CANDIDATE", cost_bps, nav, factors, turnover, states,
        pre_trade_nav, transaction_cost, post_trade_nav,
    )


def _simulate_static_weights(
    prices: pd.DataFrame,
    weights: Mapping[str, float],
    name: str,
    cost_bps: float,
) -> PortfolioPath:
    cost_bps = _validate_cost(cost_bps)
    if set(weights) != set(ASSETS):
        raise ParameterGeometryProtocolError("static weights must contain BTC/ETH/SOL")
    w = {asset: float(weights[asset]) for asset in ASSETS}
    if any((not math.isfinite(x) or x < 0.0) for x in w.values()):
        raise ParameterGeometryProtocolError("static weights must be finite non-negative")
    if not math.isclose(sum(w.values()), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ParameterGeometryProtocolError("static weights must sum to one")

    ratios = _period_ratios(prices)
    n = len(prices) - ORIGIN_OFFSET - 1
    nav = np.empty(n + 1, dtype=np.float64)
    nav[0] = 1.0
    factors = np.empty(n, dtype=np.float64)
    turnover = np.zeros(n, dtype=np.float64)
    turnover[0] = 1.0
    pre_trade_nav = np.empty(n, dtype=np.float64)
    transaction_cost = np.zeros(n, dtype=np.float64)
    post_trade_nav = np.empty(n, dtype=np.float64)

    rate = cost_bps / 10000.0
    entry_cost = rate
    post_entry = 1.0 - entry_cost
    if post_entry <= 0.0:
        raise ParameterGeometryProtocolError("transaction cost exhausted static NAV")
    values = {asset: w[asset] * post_entry for asset in ASSETS}

    for i in range(n):
        pre_trade_nav[i] = nav[i]
        if i == 0:
            transaction_cost[i] = entry_cost
            post_trade_nav[i] = post_entry
        else:
            post_trade_nav[i] = nav[i]
        for asset in ASSETS:
            values[asset] *= float(ratios[asset][i])
        next_nav = sum(values.values())
        if not math.isfinite(next_nav) or next_nav <= 0.0:
            raise ParameterGeometryProtocolError("static NAV became invalid")
        nav[i + 1] = next_nav
        factors[i] = next_nav / nav[i]

    return PortfolioPath(
        name, cost_bps, nav, factors, turnover, None,
        pre_trade_nav, transaction_cost, post_trade_nav,
    )


def simulate_benchmarks(prices: pd.DataFrame, cost_bps: float) -> dict[str, PortfolioPath]:
    return {
        "B0_STATIC_BTC": _simulate_static_weights(
            prices, {"BTC": 1.0, "ETH": 0.0, "SOL": 0.0}, "B0_STATIC_BTC", cost_bps
        ),
        "B1_STATIC_BETA": _simulate_static_weights(
            prices, {"BTC": 0.0, "ETH": 0.5, "SOL": 0.5}, "B1_STATIC_BETA", cost_bps
        ),
        "B2_STATIC_BTC_BETA": _simulate_static_weights(
            prices, {"BTC": 0.5, "ETH": 0.25, "SOL": 0.25}, "B2_STATIC_BTC_BETA", cost_bps
        ),
    }


def select_best_static(benchmarks: Mapping[str, PortfolioPath]) -> str:
    if set(benchmarks) != set(BENCHMARKS):
        raise ParameterGeometryProtocolError("benchmark set mismatch")
    best = BENCHMARKS[0]
    best_w = benchmarks[best].terminal_wealth
    for name in BENCHMARKS[1:]:
        w = benchmarks[name].terminal_wealth
        if w > best_w:
            best = name
            best_w = w
    return best


def _surface_summary(path: PortfolioPath, L: int, kappa: float) -> dict[str, Any]:
    return {
        "L": int(L),
        "kappa": float(kappa),
        "cost_bps": float(path.cost_bps),
        "terminal_wealth": float(path.terminal_wealth),
        "cagr": float(path.cagr),
        "mdd": float(path.maximum_drawdown),
        "executed_l1_turnover": float(path.total_turnover),
        "state_switch_count": int(path.switch_count),
        "beta_holding_fraction": float(path.beta_holding_fraction),
    }


def evaluate_surface(
    prices: pd.DataFrame,
) -> tuple[
    dict[float, dict[tuple[int, float], PortfolioPath]],
    list[dict[str, Any]],
    dict[int, np.ndarray],
]:
    scores_by_L = {L: score_series(prices, L) for L in L_VALUES}
    states_by_cell: dict[tuple[int, float], tuple[str, ...]] = {}
    for L in L_VALUES:
        for kappa in KAPPA_VALUES:
            states_by_cell[(L, kappa)] = states_from_scores(scores_by_L[L], kappa)

    panel: dict[float, dict[tuple[int, float], PortfolioPath]] = {}
    rows: list[dict[str, Any]] = []
    for cost in COST_BPS:
        cell_paths: dict[tuple[int, float], PortfolioPath] = {}
        for L in L_VALUES:
            for kappa in KAPPA_VALUES:
                path = simulate_candidate(prices, states_by_cell[(L, kappa)], cost)
                cell_paths[(L, kappa)] = path
                rows.append(_surface_summary(path, L, kappa))
        panel[cost] = cell_paths
    return panel, rows, scores_by_L


def geometry_for_cost(
    cell_paths: Mapping[tuple[int, float], PortfolioPath],
    cost_bps: float,
) -> tuple[list[dict[str, Any]], np.ndarray]:
    J = np.empty((len(L_VALUES), len(KAPPA_VALUES)), dtype=np.float64)
    for i, L in enumerate(L_VALUES):
        for j, kappa in enumerate(KAPPA_VALUES):
            path = cell_paths[(L, kappa)]
            value = math.log(path.terminal_wealth)
            if not math.isfinite(value):
                raise ParameterGeometryProtocolError("non-finite surface objective")
            J[i, j] = value

    stable = np.zeros_like(J, dtype=bool)
    rows: list[dict[str, Any]] = []
    for i in range(1, len(L_VALUES) - 1):
        for j in range(1, len(KAPPA_VALUES) - 1):
            dL = float((J[i + 1, j] - J[i - 1, j]) / 2.0)
            dk = float((J[i, j + 1] - J[i, j - 1]) / 2.0)
            dLL = float(J[i + 1, j] - 2.0 * J[i, j] + J[i - 1, j])
            dkk = float(J[i, j + 1] - 2.0 * J[i, j] + J[i, j - 1])
            dLk = float(
                (J[i + 1, j + 1] - J[i + 1, j - 1] - J[i - 1, j + 1] + J[i - 1, j - 1])
                / 4.0
            )
            grad = float(math.sqrt(dL * dL + dk * dk))
            eigvals = np.linalg.eigvalsh(np.array([[dLL, dLk], [dLk, dkk]], dtype=np.float64))
            hnorm = float(np.max(np.abs(eigvals)))
            is_stable = bool(grad <= GRADIENT_THRESHOLD and hnorm <= HESSIAN_THRESHOLD)
            stable[i, j] = is_stable
            rows.append(
                {
                    "L": int(L_VALUES[i]),
                    "kappa": float(KAPPA_VALUES[j]),
                    "cost_bps": float(cost_bps),
                    "D_L": dL,
                    "D_kappa": dk,
                    "gradient_norm": grad,
                    "D_LL": dLL,
                    "D_kk": dkk,
                    "D_Lk": dLk,
                    "hessian_spectral_norm": hnorm,
                    "stable_cell": is_stable,
                }
            )
    return rows, stable


def connected_components(mask: np.ndarray) -> list[tuple[tuple[int, int], ...]]:
    arr = np.asarray(mask, dtype=bool)
    if arr.shape != (len(L_VALUES), len(KAPPA_VALUES)):
        raise ParameterGeometryProtocolError("stable mask shape mismatch")
    visited = np.zeros_like(arr, dtype=bool)
    components: list[tuple[tuple[int, int], ...]] = []
    for i in range(1, arr.shape[0] - 1):
        for j in range(1, arr.shape[1] - 1):
            if not arr[i, j] or visited[i, j]:
                continue
            stack = [(i, j)]
            visited[i, j] = True
            cells: list[tuple[int, int]] = []
            while stack:
                ci, cj = stack.pop()
                cells.append((ci, cj))
                for ni, nj in ((ci - 1, cj), (ci + 1, cj), (ci, cj - 1), (ci, cj + 1)):
                    if (
                        1 <= ni < arr.shape[0] - 1
                        and 1 <= nj < arr.shape[1] - 1
                        and arr[ni, nj]
                        and not visited[ni, nj]
                    ):
                        visited[ni, nj] = True
                        stack.append((ni, nj))
            components.append(tuple(sorted(cells)))
    return components


def _component_admissible(cells: Sequence[tuple[int, int]]) -> bool:
    cells = tuple(cells)
    return (
        len(cells) >= MIN_COMPONENT_CELLS
        and len({i for i, _ in cells}) >= MIN_DISTINCT_L
        and len({j for _, j in cells}) >= MIN_DISTINCT_KAPPA
    )


def admissible_components(mask: np.ndarray) -> list[tuple[tuple[int, int], ...]]:
    return [c for c in connected_components(mask) if _component_admissible(c)]


def _component_trace(
    components: Sequence[Sequence[tuple[int, int]]],
    prefix: str,
) -> list[dict[str, Any]]:
    out = []
    for n, cells in enumerate(components, start=1):
        cells = tuple(sorted(cells))
        out.append(
            {
                "component_id": f"{prefix}_{n:03d}",
                "cell_count": int(len(cells)),
                "distinct_L_levels": int(len({i for i, _ in cells})),
                "distinct_kappa_levels": int(len({j for _, j in cells})),
                "min_L_index": int(min(i for i, _ in cells)),
                "min_kappa_index": int(min(j for _, j in cells)),
                "cells": [
                    {
                        "L_index": int(i),
                        "kappa_index": int(j),
                        "L": int(L_VALUES[i]),
                        "kappa": float(KAPPA_VALUES[j]),
                    }
                    for i, j in cells
                ],
            }
        )
    return out


def select_component(
    components: Sequence[Sequence[tuple[int, int]]],
) -> tuple[tuple[int, int], ...] | None:
    comps = [tuple(sorted(c)) for c in components]
    if not comps:
        return None
    return min(
        comps,
        key=lambda c: (
            -len(c),
            min(i for i, _ in c),
            min(j for _, j in c),
        ),
    )


def medoid_of_component(
    cells: Sequence[tuple[int, int]],
) -> tuple[tuple[int, int], float]:
    cells = tuple(sorted(cells))
    if not cells:
        raise ParameterGeometryProtocolError("medoid requires non-empty component")
    best_cell: tuple[int, int] | None = None
    best_sum: float | None = None
    for candidate in cells:
        ci, cj = candidate
        distance_sum = float(sum((ci - i) ** 2 + (cj - j) ** 2 for i, j in cells))
        if best_sum is None or distance_sum < best_sum:
            best_cell = candidate
            best_sum = distance_sum
        elif distance_sum == best_sum and candidate < best_cell:
            best_cell = candidate
            best_sum = distance_sum
    assert best_cell is not None and best_sum is not None
    return best_cell, best_sum


def historical_argmax(cell_paths: Mapping[tuple[int, float], PortfolioPath]) -> tuple[int, float]:
    best: tuple[int, float] | None = None
    best_w = -math.inf
    for L in L_VALUES:
        for kappa in KAPPA_VALUES:
            key = (L, kappa)
            w = cell_paths[key].terminal_wealth
            if w > best_w:
                best = key
                best_w = w
            elif w == best_w and best is not None and key < best:
                best = key
    if best is None:
        raise ParameterGeometryProtocolError("historical argmax unavailable")
    return best


def temporal_block_relative_log_growth(
    candidate: PortfolioPath,
    benchmark: PortfolioPath,
) -> tuple[float, ...]:
    if len(candidate.period_factors) != HELD_PERIODS or len(benchmark.period_factors) != HELD_PERIODS:
        raise ParameterGeometryProtocolError("temporal gate requires frozen 1942 held periods")
    out: list[float] = []
    start = 0
    for size in TEMPORAL_BLOCK_SIZES:
        end = start + size
        cg = candidate.nav[end] / candidate.nav[start]
        bg = benchmark.nav[end] / benchmark.nav[start]
        out.append(float(math.log(cg / bg)))
        start = end
    if start != HELD_PERIODS:
        raise ParameterGeometryProtocolError("temporal blocks do not cover frozen window")
    return tuple(out)


def moving_block_indices(
    n: int,
    rng: np.random.Generator,
    block_length: int = BOOTSTRAP_BLOCK_LENGTH,
) -> np.ndarray:
    if n < block_length:
        raise ParameterGeometryProtocolError("moving-block bootstrap requires a full block")
    starts = np.arange(0, n - block_length + 1, dtype=int)
    pieces: list[np.ndarray] = []
    total = 0
    while total < n:
        start = int(rng.choice(starts))
        pieces.append(np.arange(start, start + block_length, dtype=int))
        total += block_length
    return np.concatenate(pieces)[:n]


def _bootstrap_from_differentials(
    differentials: np.ndarray,
    *,
    replicates: int,
    seed: int,
) -> dict[str, Any]:
    d = np.asarray(differentials, dtype=np.float64)
    if d.ndim != 2 or d.shape[1] != 3 or not np.isfinite(d).all():
        raise ParameterGeometryProtocolError("bootstrap differentials must be finite Nx3")
    if d.shape[0] < BOOTSTRAP_BLOCK_LENGTH:
        raise ParameterGeometryProtocolError("insufficient bootstrap rows")
    if int(replicates) <= 0:
        raise ParameterGeometryProtocolError("bootstrap replicates must be positive")
    mu = np.mean(d, axis=0)
    rng = np.random.default_rng(int(seed))
    tstars = np.empty(int(replicates), dtype=np.float64)
    for r in range(int(replicates)):
        idx = moving_block_indices(d.shape[0], rng)
        mu_star = np.mean(d[idx], axis=0)
        tstars[r] = float(np.max(mu - mu_star))
    q95 = float(np.quantile(tstars, BOOTSTRAP_QUANTILE, method="linear"))
    lcb = mu - q95
    return {
        "means": tuple(float(x) for x in mu),
        "q95": q95,
        "lcbs": tuple(float(x) for x in lcb),
    }


def dependence_aware_bootstrap(
    selected: PortfolioPath,
    benchmarks: Mapping[str, PortfolioPath],
) -> dict[str, Any]:
    columns = []
    for name in BENCHMARKS:
        benchmark = benchmarks[name]
        if len(selected.period_factors) != HELD_PERIODS or len(benchmark.period_factors) != HELD_PERIODS:
            raise ParameterGeometryProtocolError("bootstrap requires frozen 1942 held periods")
        columns.append(np.log(selected.period_factors) - np.log(benchmark.period_factors))
    matrix = np.column_stack(columns)
    out = _bootstrap_from_differentials(
        matrix, replicates=BOOTSTRAP_REPLICATES, seed=BOOTSTRAP_SEED
    )
    out.update(
        {
            "benchmarks": BENCHMARKS,
            "replicates": BOOTSTRAP_REPLICATES,
            "block_length": BOOTSTRAP_BLOCK_LENGTH,
            "blocks_per_replicate_before_truncation": BOOTSTRAP_BLOCKS_PER_REPLICATE,
            "seed": BOOTSTRAP_SEED,
        }
    )
    return out


def holding_spells(states: Sequence[str]) -> tuple[int, ...]:
    states = tuple(states)
    if not states:
        return tuple()
    if any(x not in ("BTC", "BETA") for x in states):
        raise ParameterGeometryProtocolError("invalid state")
    spells: list[int] = []
    current = states[0]
    count = 1
    for state in states[1:]:
        if state == current:
            count += 1
        else:
            spells.append(count)
            current = state
            count = 1
    spells.append(count)
    return tuple(spells)


def calendar_year_returns(path: PortfolioPath, origin_index: pd.DatetimeIndex) -> dict[str, float]:
    if len(origin_index) != len(path.period_factors):
        raise ParameterGeometryProtocolError("calendar-year origin alignment mismatch")
    years = origin_index.year
    out: dict[str, float] = {}
    for year in sorted(set(int(x) for x in years)):
        mask = years == year
        out[str(year)] = float(np.prod(path.period_factors[mask]) - 1.0)
    return out


def longest_underperformance_interval_days(candidate: PortfolioPath, benchmark: PortfolioPath) -> int:
    if candidate.nav.shape != benchmark.nav.shape:
        raise ParameterGeometryProtocolError("relative NAV alignment mismatch")
    relative = candidate.nav / benchmark.nav
    below = relative < (1.0 - STRICT_TOL)
    longest = 0
    current = 0
    for flag in below:
        if bool(flag):
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return int(longest)


def _daily_path_rows(
    path: PortfolioPath,
    prices: pd.DataFrame,
    *,
    include_candidate_fields: bool,
) -> list[dict[str, Any]]:
    terminal_dates = prices.index[ORIGIN_OFFSET + 1 :]
    if len(terminal_dates) != len(path.period_factors):
        raise ParameterGeometryProtocolError("daily path date alignment mismatch")
    dd = path.drawdown
    rows: list[dict[str, Any]] = []
    for i, date in enumerate(terminal_dates):
        row = {
            "date": pd.Timestamp(date).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "nav": float(path.nav[i + 1]),
            "drawdown": float(dd[i + 1]),
            "held_period_growth": float(path.period_factors[i]),
        }
        if include_candidate_fields:
            if path.states is None:
                raise ParameterGeometryProtocolError("candidate daily path requires states")
            row.update(
                {
                    "state": path.states[i],
                    "pre_trade_nav": float(path.pre_trade_nav[i]),
                    "executed_l1_turnover": float(path.executed_l1_turnover[i]),
                    "transaction_cost": float(path.transaction_cost[i]),
                    "post_trade_nav": float(path.post_trade_nav[i]),
                }
            )
        else:
            row["benchmark"] = path.name
        rows.append(row)
    return rows


def classification_from_gates(
    *,
    g1: bool,
    g2: bool | None,
    g3: bool | None,
    g4: bool | None,
    g5: bool | None,
) -> str:
    if not g1:
        return "FAIL_NO_STABLE_PARAMETER_PLATEAU"
    if g2 is not True:
        return "FAIL_STABLE_PLATEAU_NOT_COST_ROBUST"
    if g3 is not True:
        return "FAIL_STABLE_PLATEAU_NOT_ECONOMICALLY_RELEVANT"
    if g4 is not True or g5 is not True:
        return "FAIL_STABLE_PLATEAU_NOT_TEMPORALLY_OR_DEPENDENCE_ROBUST"
    return "PASS_PARAMETER_FREEZE_ELIGIBLE"


def evaluate_frozen_contract(
    frames: Mapping[str, pd.DataFrame],
    payload_sha256: str,
) -> dict[str, Any]:
    validate_payload_identity(payload_sha256)
    prices = validate_price_frames(frames, require_frozen_calendar=True)
    panel, surface_rows, _ = evaluate_surface(prices)

    geometry_rows: list[dict[str, Any]] = []
    stable_by_cost: dict[float, np.ndarray] = {}
    for cost in COST_BPS:
        rows, mask = geometry_for_cost(panel[cost], cost)
        geometry_rows.extend(rows)
        stable_by_cost[cost] = mask

    primary_components = admissible_components(stable_by_cost[PRIMARY_COST_BPS])
    coherent_mask = stable_by_cost[5.0] & stable_by_cost[10.0] & stable_by_cost[20.0]
    coherent_components = admissible_components(coherent_mask)
    selected_component = select_component(coherent_components)

    primary_trace = _component_trace(primary_components, "P5")
    coherent_trace = _component_trace(coherent_components, "CC")

    primary_argmax = historical_argmax(panel[PRIMARY_COST_BPS])
    argmax_path = panel[PRIMARY_COST_BPS][primary_argmax]

    selected_key: tuple[int, float] | None = None
    selected_component_id: str | None = None
    selected_cells: list[dict[str, Any]] = []
    medoid_distance_sum: float | None = None

    if selected_component is not None:
        medoid_idx, medoid_distance_sum = medoid_of_component(selected_component)
        selected_key = (L_VALUES[medoid_idx[0]], KAPPA_VALUES[medoid_idx[1]])
        chosen_ordinal = next(
            ordinal
            for ordinal, comp in enumerate(coherent_components, start=1)
            if tuple(sorted(comp)) == tuple(sorted(selected_component))
        )
        selected_component_id = f"CC_{chosen_ordinal:03d}"
        selected_cells = [
            {
                "L_index": int(i),
                "kappa_index": int(j),
                "L": int(L_VALUES[i]),
                "kappa": float(KAPPA_VALUES[j]),
            }
            for i, j in selected_component
        ]

    benchmarks_by_cost = {cost: simulate_benchmarks(prices, cost) for cost in COST_BPS}
    best_static_by_cost = {cost: select_best_static(benchmarks_by_cost[cost]) for cost in COST_BPS}

    g1 = bool(primary_components)
    g2: bool | None = None
    g3: bool | None = None
    g4: bool | None = None
    g5: bool | None = None
    temporal_stats: tuple[float, ...] | None = None
    bootstrap: dict[str, Any] | None = None

    selected_paths: dict[float, PortfolioPath] = {}
    if selected_key is not None:
        selected_paths = {cost: panel[cost][selected_key] for cost in COST_BPS}
        stress_ok = True
        for cost in STRESS_COST_BPS:
            best = benchmarks_by_cost[cost][best_static_by_cost[cost]]
            advantage = math.log(selected_paths[cost].terminal_wealth / best.terminal_wealth)
            stress_ok = stress_ok and advantage > STRICT_TOL
        g2 = bool(stress_ok)
        if g2:
            best_primary = benchmarks_by_cost[PRIMARY_COST_BPS][best_static_by_cost[PRIMARY_COST_BPS]]
            primary_advantage = math.log(
                selected_paths[PRIMARY_COST_BPS].terminal_wealth / best_primary.terminal_wealth
            )
            g3 = bool(primary_advantage > PRIMARY_MARGIN_LOG_WEALTH)

            b_star = best_static_by_cost[PRIMARY_COST_BPS]
            temporal_stats = temporal_block_relative_log_growth(
                selected_paths[PRIMARY_COST_BPS],
                benchmarks_by_cost[PRIMARY_COST_BPS][b_star],
            )
            g4 = bool(sum(x > STRICT_TOL for x in temporal_stats) >= TEMPORAL_REQUIRED_WINS)

            bootstrap = dependence_aware_bootstrap(
                selected_paths[PRIMARY_COST_BPS],
                benchmarks_by_cost[PRIMARY_COST_BPS],
            )
            g5 = bool(min(bootstrap["lcbs"]) > 0.0)
    else:
        g2 = False

    classification = classification_from_gates(g1=g1, g2=g2, g3=g3, g4=g4, g5=g5)

    ranking_trace = []
    for rank, comp in enumerate(
        sorted(
            coherent_components,
            key=lambda c: (-len(c), min(i for i, _ in c), min(j for _, j in c)),
        ),
        start=1,
    ):
        ranking_trace.append(
            {
                "rank": int(rank),
                "cell_count": int(len(comp)),
                "min_L_index": int(min(i for i, _ in comp)),
                "min_kappa_index": int(min(j for _, j in comp)),
            }
        )

    plateau_trace = {
        "primary_5bps_components": primary_trace,
        "cost_coherent_components": coherent_trace,
        "selected_component_id": selected_component_id,
        "selected_component_cells": selected_cells,
        "component_ranking_trace": ranking_trace,
        "selected_representative": (
            None if selected_key is None else {"L": int(selected_key[0]), "kappa": float(selected_key[1])}
        ),
        "medoid_distance_sum": medoid_distance_sum,
        "historical_argmax_descriptive_only": {
            "L": int(primary_argmax[0]),
            "kappa": float(primary_argmax[1]),
            "terminal_wealth": float(argmax_path.terminal_wealth),
        },
    }

    selected_daily_path: list[dict[str, Any]] = []
    benchmark_daily_paths: list[dict[str, Any]] = []
    diagnostics: dict[str, Any]

    if selected_key is not None:
        selected_primary = selected_paths[PRIMARY_COST_BPS]
        selected_daily_path = _daily_path_rows(selected_primary, prices, include_candidate_fields=True)
        for name in BENCHMARKS:
            benchmark_daily_paths.extend(
                _daily_path_rows(
                    benchmarks_by_cost[PRIMARY_COST_BPS][name],
                    prices,
                    include_candidate_fields=False,
                )
            )
        spells = holding_spells(selected_primary.states or ())
        origin_index = prices.index[ORIGIN_OFFSET:-1]
        b_star_name = best_static_by_cost[PRIMARY_COST_BPS]
        diagnostics = {
            "selected_L": int(selected_key[0]),
            "selected_kappa": float(selected_key[1]),
            "selected_component_size": int(len(selected_component or ())),
            "selected_component_L_span": int(len({i for i, _ in selected_component or ()})),
            "selected_component_kappa_span": int(len({j for _, j in selected_component or ()})),
            "historical_argmax_L": int(primary_argmax[0]),
            "historical_argmax_kappa": float(primary_argmax[1]),
            "historical_argmax_terminal_wealth": float(argmax_path.terminal_wealth),
            "selected_terminal_wealth_by_cost": {
                str(int(cost)): float(selected_paths[cost].terminal_wealth) for cost in COST_BPS
            },
            "selected_cagr_by_cost": {
                str(int(cost)): float(selected_paths[cost].cagr) for cost in COST_BPS
            },
            "selected_mdd_by_cost": {
                str(int(cost)): float(selected_paths[cost].maximum_drawdown) for cost in COST_BPS
            },
            "selected_total_l1_turnover": float(selected_primary.total_turnover),
            "selected_switch_count": int(selected_primary.switch_count),
            "selected_beta_holding_fraction": float(selected_primary.beta_holding_fraction),
            "average_state_spell_days": float(np.mean(spells)) if spells else None,
            "median_state_spell_days": float(np.median(spells)) if spells else None,
            "longest_underperformance_interval_vs_5bps_B_STAR": longest_underperformance_interval_days(
                selected_primary, benchmarks_by_cost[PRIMARY_COST_BPS][b_star_name]
            ),
            "calendar_year_returns_2021_partial_through_2026_partial": calendar_year_returns(
                selected_primary, origin_index
            ),
        }
    else:
        diagnostics = {
            "selected_L": None,
            "selected_kappa": None,
            "selected_component_size": None,
            "selected_component_L_span": None,
            "selected_component_kappa_span": None,
            "historical_argmax_L": int(primary_argmax[0]),
            "historical_argmax_kappa": float(primary_argmax[1]),
            "historical_argmax_terminal_wealth": float(argmax_path.terminal_wealth),
            "selected_terminal_wealth_by_cost": {},
            "selected_cagr_by_cost": {},
            "selected_mdd_by_cost": {},
            "selected_total_l1_turnover": None,
            "selected_switch_count": None,
            "selected_beta_holding_fraction": None,
            "average_state_spell_days": None,
            "median_state_spell_days": None,
            "longest_underperformance_interval_vs_5bps_B_STAR": None,
            "calendar_year_returns_2021_partial_through_2026_partial": {},
        }

    robustness = {
        "four_block_statistics": None if temporal_stats is None else [float(x) for x in temporal_stats],
        "bootstrap_means": None if bootstrap is None else list(bootstrap["means"]),
        "bootstrap_q95": None if bootstrap is None else float(bootstrap["q95"]),
        "bootstrap_lcbs": None if bootstrap is None else list(bootstrap["lcbs"]),
    }

    return {
        "research_id": RESEARCH_ID,
        "classification": classification,
        "gates": {
            "G0_INTEGRITY": True,
            "G1_PRIMARY_PLATEAU": g1,
            "G2_COST_ROBUSTNESS": g2,
            "G3_ECONOMIC_RELEVANCE": g3,
            "G4_TEMPORAL_ROBUSTNESS": g4,
            "G5_DEPENDENCE_AWARE_ROBUSTNESS": g5,
        },
        "surface_table_every_cell_every_cost": surface_rows,
        "geometry_every_interior_cell_every_cost": geometry_rows,
        "plateau_trace": plateau_trace,
        "selected_representative_daily_path": selected_daily_path,
        "benchmark_daily_paths": benchmark_daily_paths,
        "robustness": robustness,
        "best_static_by_cost_bps": {str(int(cost)): best_static_by_cost[cost] for cost in COST_BPS},
        "diagnostics": diagnostics,
        "actual_variants_evaluated": len(L_VALUES) * len(KAPPA_VALUES),
        "authority": {
            "canonical_strategy_changed": False,
            "phase6_changed": False,
            "production_authorized_components": [],
            "production_authorized": False,
            "signature_authorized": False,
            "order_submission_authorized": False,
        },
        "path_date_semantics": "date is held-period terminal close; state and trade fields refer to the decision immediately after the preceding origin close",
    }
