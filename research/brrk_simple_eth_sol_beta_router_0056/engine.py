from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np
import pandas as pd

RESEARCH_ID = "BRRK-SIMPLE-ETH-SOL-BETA-ROUTER-0056"
EXPECTED_PAYLOAD_SHA256 = "d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193"

LOOKBACK_DAYS = 60
FROZEN_START = pd.Timestamp("2020-08-11T00:00:00Z")
FIRST_ORIGIN = pd.Timestamp("2020-10-10T00:00:00Z")
LAST_ORIGIN = pd.Timestamp("2026-08-01T00:00:00Z")
TERMINAL_CLOSE = pd.Timestamp("2026-08-02T00:00:00Z")
SOURCE_ROWS = 2183
HELD_PERIODS = 2122
ANNUALIZATION_DAYS = 365.25

ASSETS = ("ETH", "SOL")
BENCHMARKS = ("B0_STATIC_ETH", "B1_STATIC_SOL", "B2_STATIC_50_50")
COST_BPS = (5.0, 10.0, 20.0)
PRIMARY_COST_BPS = 5.0
STRESS_COST_BPS = (10.0, 20.0)
STRICT_TOL = 1e-12

TEMPORAL_BLOCK_SIZES = (531, 531, 530, 530)
TEMPORAL_REQUIRED_WINS = 3

BOOTSTRAP_BLOCK_LENGTH = 60
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_SEED = 1_844_716_895
BOOTSTRAP_BLOCKS_PER_REPLICATE = 36
BOOTSTRAP_QUANTILE = 0.95

ALLOWED_CLASSIFICATIONS = (
    "INVALID_EXECUTION",
    "FAIL_NO_SIMPLE_BETA_ROUTER_ECONOMIC_UPLIFT",
    "FAIL_SIMPLE_BETA_ROUTER_COST_FRAGILE",
    "FAIL_SIMPLE_BETA_ROUTER_TEMPORALLY_CONCENTRATED",
    "FAIL_SIMPLE_BETA_ROUTER_ECONOMIC_UPLIFT_NOT_DEPENDENCE_ROBUST",
    "PASS_SIMPLE_BETA_ROUTER_ECONOMIC_ELIGIBILITY",
)


class RouterProtocolError(RuntimeError):
    pass


@dataclass(frozen=True)
class ArmPath:
    name: str
    cost_bps: float
    nav: np.ndarray
    period_factors: np.ndarray
    executed_l1_turnover: np.ndarray
    targets: tuple[str, ...] | None

    @property
    def terminal_wealth(self) -> float:
        return float(self.nav[-1])

    @property
    def cagr(self) -> float:
        return float(self.terminal_wealth ** (ANNUALIZATION_DAYS / HELD_PERIODS) - 1.0)

    @property
    def maximum_drawdown(self) -> float:
        running = np.maximum.accumulate(self.nav)
        return float(np.min(self.nav / running - 1.0))

    @property
    def total_turnover(self) -> float:
        return float(np.sum(self.executed_l1_turnover))


def _finite_positive(values: Any, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=np.float64)
    if arr.ndim != 1 or arr.size == 0:
        raise RouterProtocolError(f"{name} must be a non-empty 1D array")
    if not np.isfinite(arr).all() or np.any(arr <= 0.0):
        raise RouterProtocolError(f"{name} must be finite and strictly positive")
    return arr


def validate_payload_identity(payload_sha256: str) -> None:
    if str(payload_sha256).lower() != EXPECTED_PAYLOAD_SHA256:
        raise RouterProtocolError("0056 payload SHA256 does not match frozen preregistration")


def validate_price_frames(
    frames: Mapping[str, pd.DataFrame],
    *,
    require_frozen_calendar: bool = True,
) -> pd.DataFrame:
    if set(frames) != set(ASSETS):
        raise RouterProtocolError(f"frames must contain exactly {ASSETS}")
    indexes = [frames[a].index for a in ASSETS]
    if not all(indexes[0].equals(idx) for idx in indexes[1:]):
        raise RouterProtocolError("ETH/SOL indexes must be identical")
    index = indexes[0]
    if not isinstance(index, pd.DatetimeIndex):
        raise RouterProtocolError("price index must be a DatetimeIndex")
    if index.tz is None or str(index.tz) != "UTC":
        raise RouterProtocolError("price index timezone must be UTC")
    if index.has_duplicates or not index.is_monotonic_increasing:
        raise RouterProtocolError("price index must be unique and strictly increasing")
    if len(index) < LOOKBACK_DAYS + 2:
        raise RouterProtocolError("price history is too short for one causal held period")
    prices = pd.DataFrame(index=index)
    for asset in ASSETS:
        if "close" not in frames[asset].columns:
            raise RouterProtocolError(f"missing {asset} close")
        prices[asset] = _finite_positive(frames[asset]["close"].to_numpy(), f"{asset} close")
    if require_frozen_calendar:
        expected = pd.date_range(FROZEN_START, TERMINAL_CLOSE, freq="D")
        if len(index) != SOURCE_ROWS or not index.equals(expected):
            raise RouterProtocolError("frozen 0056 daily calendar mismatch")
        if index[LOOKBACK_DAYS] != FIRST_ORIGIN or index[-2] != LAST_ORIGIN or index[-1] != TERMINAL_CLOSE:
            raise RouterProtocolError("frozen 0056 evaluation boundary mismatch")
    return prices


def router_targets_from_prices(prices: pd.DataFrame) -> tuple[np.ndarray, tuple[str, ...]]:
    if not {"ETH", "SOL"}.issubset(prices.columns):
        raise RouterProtocolError("prices must contain ETH and SOL")
    eth = _finite_positive(prices["ETH"].to_numpy(), "ETH close")
    sol = _finite_positive(prices["SOL"].to_numpy(), "SOL close")
    if eth.shape != sol.shape:
        raise RouterProtocolError("ETH/SOL close arrays must have equal length")
    z = np.log(sol) - np.log(eth)
    rms: list[float] = []
    targets: list[str] = []
    prior: str | None = None
    for pos in range(LOOKBACK_DAYS, len(z) - 1):
        rm = float(z[pos] - z[pos - LOOKBACK_DAYS])
        if rm > 0.0:
            target = "SOL"
        elif rm < 0.0:
            target = "ETH"
        else:
            target = prior if prior is not None else "ETH"
        rms.append(rm)
        targets.append(target)
        prior = target
    return np.asarray(rms, dtype=np.float64), tuple(targets)


def _period_ratios(prices: pd.DataFrame, target: str) -> np.ndarray:
    values = _finite_positive(prices[target].to_numpy(), f"{target} close")
    origins = values[LOOKBACK_DAYS:-1]
    next_values = values[LOOKBACK_DAYS + 1 :]
    ratios = next_values / origins
    if not np.isfinite(ratios).all() or np.any(ratios <= 0.0):
        raise RouterProtocolError("invalid close-to-close ratios")
    return ratios.astype(np.float64, copy=False)


def _validate_cost(cost_bps: float) -> float:
    value = float(cost_bps)
    if not math.isfinite(value) or value < 0.0:
        raise RouterProtocolError("cost bps must be finite and non-negative")
    return value


def simulate_router(prices: pd.DataFrame, targets: Sequence[str], cost_bps: float) -> ArmPath:
    cost_bps = _validate_cost(cost_bps)
    targets = tuple(str(x) for x in targets)
    n = len(prices) - LOOKBACK_DAYS - 1
    if len(targets) != n:
        raise RouterProtocolError("router target count mismatch")
    if any(t not in ASSETS for t in targets):
        raise RouterProtocolError("router targets must be ETH or SOL")
    ratios = {asset: _period_ratios(prices, asset) for asset in ASSETS}
    nav = np.empty(n + 1, dtype=np.float64)
    nav[0] = 1.0
    factors = np.empty(n, dtype=np.float64)
    turnover = np.empty(n, dtype=np.float64)
    prior: str | None = None
    rate = cost_bps / 10000.0
    for i, target in enumerate(targets):
        l1 = 1.0 if prior is None else (2.0 if target != prior else 0.0)
        post_cost = nav[i] - nav[i] * l1 * rate
        if not math.isfinite(post_cost) or post_cost <= 0.0:
            raise RouterProtocolError("transaction cost exhausted router NAV")
        nav[i + 1] = post_cost * ratios[target][i]
        if not math.isfinite(nav[i + 1]) or nav[i + 1] <= 0.0:
            raise RouterProtocolError("router NAV became invalid")
        factors[i] = nav[i + 1] / nav[i]
        turnover[i] = l1
        prior = target
    return ArmPath("ROUTER", cost_bps, nav, factors, turnover, targets)


def simulate_static_single(prices: pd.DataFrame, asset: str, cost_bps: float) -> ArmPath:
    if asset not in ASSETS:
        raise RouterProtocolError("static asset must be ETH or SOL")
    cost_bps = _validate_cost(cost_bps)
    ratio = _period_ratios(prices, asset)
    n = len(ratio)
    nav = np.empty(n + 1, dtype=np.float64)
    nav[0] = 1.0
    turnover = np.zeros(n, dtype=np.float64)
    turnover[0] = 1.0
    factors = np.empty(n, dtype=np.float64)
    rate = cost_bps / 10000.0
    for i in range(n):
        post = nav[i] * (1.0 - rate) if i == 0 else nav[i]
        if post <= 0.0:
            raise RouterProtocolError("transaction cost exhausted static NAV")
        nav[i + 1] = post * ratio[i]
        factors[i] = nav[i + 1] / nav[i]
    name = "B0_STATIC_ETH" if asset == "ETH" else "B1_STATIC_SOL"
    return ArmPath(name, cost_bps, nav, factors, turnover, tuple([asset] * n))


def simulate_static_50_50(prices: pd.DataFrame, cost_bps: float) -> ArmPath:
    cost_bps = _validate_cost(cost_bps)
    re = _period_ratios(prices, "ETH")
    rs = _period_ratios(prices, "SOL")
    if re.shape != rs.shape:
        raise RouterProtocolError("B2 ratio alignment mismatch")
    n = len(re)
    nav = np.empty(n + 1, dtype=np.float64)
    nav[0] = 1.0
    turnover = np.zeros(n, dtype=np.float64)
    turnover[0] = 1.0
    factors = np.empty(n, dtype=np.float64)
    post_entry = 1.0 - cost_bps / 10000.0
    if post_entry <= 0.0:
        raise RouterProtocolError("transaction cost exhausted B2 NAV")
    eth_component = 0.5 * post_entry
    sol_component = 0.5 * post_entry
    for i in range(n):
        eth_component *= re[i]
        sol_component *= rs[i]
        nav[i + 1] = eth_component + sol_component
        if not math.isfinite(nav[i + 1]) or nav[i + 1] <= 0.0:
            raise RouterProtocolError("B2 NAV became invalid")
        factors[i] = nav[i + 1] / nav[i]
    return ArmPath("B2_STATIC_50_50", cost_bps, nav, factors, turnover, None)


def evaluate_cost_panel(prices: pd.DataFrame, targets: Sequence[str]) -> dict[float, dict[str, ArmPath]]:
    panel: dict[float, dict[str, ArmPath]] = {}
    for bps in COST_BPS:
        panel[bps] = {
            "ROUTER": simulate_router(prices, targets, bps),
            "B0_STATIC_ETH": simulate_static_single(prices, "ETH", bps),
            "B1_STATIC_SOL": simulate_static_single(prices, "SOL", bps),
            "B2_STATIC_50_50": simulate_static_50_50(prices, bps),
        }
    return panel


def _strict_log_advantage(router: ArmPath, benchmark: ArmPath) -> float:
    value = math.log(router.terminal_wealth / benchmark.terminal_wealth)
    if not math.isfinite(value):
        raise RouterProtocolError("non-finite terminal log advantage")
    return float(value)


def select_best_static(arms: Mapping[str, ArmPath]) -> str:
    best = BENCHMARKS[0]
    best_w = arms[best].terminal_wealth
    for name in BENCHMARKS[1:]:
        w = arms[name].terminal_wealth
        if w > best_w:
            best = name
            best_w = w
    return best


def temporal_block_relative_log_growth(router: ArmPath, benchmark: ArmPath) -> tuple[float, ...]:
    if len(router.period_factors) != HELD_PERIODS or len(benchmark.period_factors) != HELD_PERIODS:
        raise RouterProtocolError("temporal gate requires frozen 2122 held periods")
    out: list[float] = []
    start = 0
    for size in TEMPORAL_BLOCK_SIZES:
        end = start + size
        rg = router.nav[end] / router.nav[start]
        bg = benchmark.nav[end] / benchmark.nav[start]
        out.append(float(math.log(rg / bg)))
        start = end
    if start != HELD_PERIODS:
        raise RouterProtocolError("temporal block sizes do not cover frozen window")
    return tuple(out)


def moving_block_indices(n: int, rng: np.random.Generator, block_length: int = BOOTSTRAP_BLOCK_LENGTH) -> np.ndarray:
    if n < block_length:
        raise RouterProtocolError("moving-block bootstrap requires at least one full block")
    starts = np.arange(0, n - block_length + 1, dtype=int)
    pieces: list[np.ndarray] = []
    total = 0
    while total < n:
        start = int(rng.choice(starts))
        pieces.append(np.arange(start, start + block_length, dtype=int))
        total += block_length
    return np.concatenate(pieces)[:n]


def _bootstrap_from_differentials(differentials: np.ndarray, *, replicates: int, seed: int) -> dict[str, Any]:
    d = np.asarray(differentials, dtype=np.float64)
    if d.ndim != 2 or d.shape[1] != 3 or not np.isfinite(d).all():
        raise RouterProtocolError("bootstrap differentials must be finite Nx3")
    n = d.shape[0]
    if n < BOOTSTRAP_BLOCK_LENGTH:
        raise RouterProtocolError("insufficient bootstrap rows")
    if int(replicates) <= 0:
        raise RouterProtocolError("bootstrap replicates must be positive")
    mu = np.mean(d, axis=0)
    rng = np.random.default_rng(int(seed))
    tstars = np.empty(int(replicates), dtype=np.float64)
    for r in range(int(replicates)):
        idx = moving_block_indices(n, rng)
        mu_star = np.mean(d[idx], axis=0)
        tstars[r] = float(np.max(mu - mu_star))
    q95 = float(np.quantile(tstars, BOOTSTRAP_QUANTILE, method="linear"))
    lcb = mu - q95
    return {"means": tuple(float(x) for x in mu), "q95": q95, "lcbs": tuple(float(x) for x in lcb)}


def dependence_aware_bootstrap(primary_arms: Mapping[str, ArmPath]) -> dict[str, Any]:
    router = primary_arms["ROUTER"]
    columns = []
    for b in BENCHMARKS:
        bench = primary_arms[b]
        if len(router.period_factors) != HELD_PERIODS or len(bench.period_factors) != HELD_PERIODS:
            raise RouterProtocolError("bootstrap requires frozen 2122 held periods")
        columns.append(np.log(router.period_factors) - np.log(bench.period_factors))
    matrix = np.column_stack(columns)
    out = _bootstrap_from_differentials(matrix, replicates=BOOTSTRAP_REPLICATES, seed=BOOTSTRAP_SEED)
    out["benchmarks"] = BENCHMARKS
    out["replicates"] = BOOTSTRAP_REPLICATES
    out["block_length"] = BOOTSTRAP_BLOCK_LENGTH
    out["blocks_per_replicate_before_truncation"] = BOOTSTRAP_BLOCKS_PER_REPLICATE
    out["seed"] = BOOTSTRAP_SEED
    return out


def holding_spells(targets: Sequence[str]) -> tuple[int, ...]:
    targets = tuple(targets)
    if not targets:
        return tuple()
    if any(t not in ASSETS for t in targets):
        raise RouterProtocolError("invalid holding target")
    spells: list[int] = []
    current = targets[0]
    count = 1
    for target in targets[1:]:
        if target == current:
            count += 1
        else:
            spells.append(count)
            current = target
            count = 1
    spells.append(count)
    return tuple(spells)


def calendar_year_returns(path: ArmPath, origin_index: pd.DatetimeIndex) -> dict[str, float]:
    if len(origin_index) != len(path.period_factors):
        raise RouterProtocolError("calendar-year origin alignment mismatch")
    out: dict[str, float] = {}
    years = origin_index.year
    for year in sorted(set(int(x) for x in years)):
        mask = years == year
        out[str(year)] = float(np.prod(path.period_factors[mask]) - 1.0)
    return out


def longest_underperformance_interval_days(router: ArmPath, benchmark: ArmPath) -> int:
    if router.nav.shape != benchmark.nav.shape:
        raise RouterProtocolError("relative NAV alignment mismatch")
    relative = router.nav / benchmark.nav
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


def classification_from_gates(g0: bool, g1: bool, g2: bool, g3: bool, g4: bool) -> str:
    if not g0:
        return "INVALID_EXECUTION"
    if not g1:
        return "FAIL_NO_SIMPLE_BETA_ROUTER_ECONOMIC_UPLIFT"
    if not g2:
        return "FAIL_SIMPLE_BETA_ROUTER_COST_FRAGILE"
    if not g3:
        return "FAIL_SIMPLE_BETA_ROUTER_TEMPORALLY_CONCENTRATED"
    if not g4:
        return "FAIL_SIMPLE_BETA_ROUTER_ECONOMIC_UPLIFT_NOT_DEPENDENCE_ROBUST"
    return "PASS_SIMPLE_BETA_ROUTER_ECONOMIC_ELIGIBILITY"


def evaluate_frozen_contract(frames: Mapping[str, pd.DataFrame], payload_sha256: str) -> dict[str, Any]:
    validate_payload_identity(payload_sha256)
    prices = validate_price_frames(frames, require_frozen_calendar=True)
    rm60, targets = router_targets_from_prices(prices)
    if len(targets) != HELD_PERIODS:
        raise RouterProtocolError("frozen target count mismatch")
    panel = evaluate_cost_panel(prices, targets)
    primary = panel[PRIMARY_COST_BPS]
    router_primary = primary["ROUTER"]

    log_advantages: dict[str, dict[str, float]] = {}
    for bps in COST_BPS:
        router = panel[bps]["ROUTER"]
        log_advantages[str(int(bps))] = {b: _strict_log_advantage(router, panel[bps][b]) for b in BENCHMARKS}

    g1 = all(v > STRICT_TOL for v in log_advantages["5"].values())
    g2 = all(all(v > STRICT_TOL for v in log_advantages[str(int(bps))].values()) for bps in STRESS_COST_BPS)

    b_star = select_best_static(primary)
    block_stats = temporal_block_relative_log_growth(router_primary, primary[b_star])
    g3 = sum(x > STRICT_TOL for x in block_stats) >= TEMPORAL_REQUIRED_WINS

    bootstrap = dependence_aware_bootstrap(primary)
    g4 = min(bootstrap["lcbs"]) > 0.0
    gates = {
        "G0_INTEGRITY": True,
        "G1_PRIMARY_ECONOMIC_DOMINANCE_5BPS": bool(g1),
        "G2_COST_SURVIVAL": bool(g2),
        "G3_TEMPORAL_ROBUSTNESS": bool(g3),
        "G4_DEPENDENCE_AWARE_ROBUSTNESS": bool(g4),
    }
    classification = classification_from_gates(True, g1, g2, g3, g4)

    spells = holding_spells(targets)
    origin_index = prices.index[LOOKBACK_DAYS:-1]
    diagnostics = {
        "maximum_drawdown_5bps": {name: float(path.maximum_drawdown) for name, path in primary.items()},
        "router_total_executed_l1_turnover_5bps": float(router_primary.total_turnover),
        "router_switch_count": int(np.sum(router_primary.executed_l1_turnover[1:] == 2.0)),
        "router_average_holding_duration_days": float(np.mean(spells)),
        "router_median_holding_duration_days": float(np.median(spells)),
        "router_holding_spell_count": int(len(spells)),
        "longest_underperformance_interval_days_vs_b_star_5bps": longest_underperformance_interval_days(router_primary, primary[b_star]),
        "calendar_year_returns_5bps": {name: calendar_year_returns(path, origin_index) for name, path in primary.items()},
    }

    metrics: dict[str, dict[str, dict[str, float]]] = {}
    for bps in COST_BPS:
        key = str(int(bps))
        metrics[key] = {
            name: {
                "terminal_wealth": float(path.terminal_wealth),
                "cagr": float(path.cagr),
                "maximum_drawdown": float(path.maximum_drawdown),
                "total_executed_l1_turnover": float(path.total_turnover),
            }
            for name, path in panel[bps].items()
        }

    return {
        "research_id": RESEARCH_ID,
        "classification": classification,
        "gates": gates,
        "rm60_origin_count": int(len(rm60)),
        "target_count": int(len(targets)),
        "targets": targets,
        "metrics_by_cost_bps": metrics,
        "log_terminal_advantage_by_cost_bps": log_advantages,
        "best_static_5bps": b_star,
        "temporal_block_relative_log_growth_vs_best_static_5bps": block_stats,
        "temporal_positive_block_count": int(sum(x > STRICT_TOL for x in block_stats)),
        "bootstrap_5bps": bootstrap,
        "diagnostics": diagnostics,
        "actual_variants_evaluated": 1,
        "authority": {
            "canonical_strategy_changed": False,
            "phase6_changed": False,
            "production_authorized": False,
            "production_authorized_components": [],
            "signature_authorized": False,
            "order_submission_authorized": False,
        },
    }
