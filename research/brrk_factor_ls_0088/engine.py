from __future__ import annotations

from math import isfinite, sqrt
from random import Random
from statistics import median, stdev
from typing import Any, Mapping, Sequence

BOOTSTRAP_SEED = 880088
BOOTSTRAP_REPLICATES = 10_000
BOOTSTRAP_BLOCK = 8
MIN_WEEKS = 104
REFERENCE_NAV = 1_000_000.0

CLASSIFICATIONS = {
    "PASS_VALIDATED_FACTOR_LS",
    "FAIL_FACTOR_LS_GATES",
    "INCONCLUSIVE_INSUFFICIENT_SUPPORT",
}


class FactorLSExecutionError(RuntimeError):
    pass


def _quantile(values: list[float], q: float) -> float:
    if not values:
        raise FactorLSExecutionError("EMPTY_BOOTSTRAP")
    ordered = sorted(values)
    pos = (len(ordered) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    w = pos - lo
    return ordered[lo] * (1.0 - w) + ordered[hi] * w


def _moving_block_sample(values: list[float], rng: Random) -> list[float]:
    block = min(BOOTSTRAP_BLOCK, len(values))
    out: list[float] = []
    while len(out) < len(values):
        start = rng.randrange(0, len(values) - block + 1)
        out.extend(values[start : start + block])
    return out[: len(values)]


def _bootstrap_ci(values: list[float]) -> tuple[float, float]:
    rng = Random(BOOTSTRAP_SEED)
    means = []
    for _ in range(BOOTSTRAP_REPLICATES):
        sample = _moving_block_sample(values, rng)
        means.append(sum(sample) / len(sample))
    return _quantile(means, 0.025), _quantile(means, 0.975)


def _max_drawdown(returns: Sequence[float]) -> float:
    nav = 1.0
    peak = 1.0
    worst = 0.0
    for r in returns:
        nav *= 1.0 + r
        peak = max(peak, nav)
        dd = nav / peak - 1.0
        worst = min(worst, dd)
    return worst


def _four_blocks(values: list[float]) -> list[list[float]]:
    n = len(values)
    bounds = [round(i * n / 4) for i in range(5)]
    return [values[bounds[i] : bounds[i + 1]] for i in range(4)]


def _ensure_finite(value: Any, code: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise FactorLSExecutionError(code) from exc
    if not isfinite(out):
        raise FactorLSExecutionError(code)
    return out


def _transition_turnover(previous: Mapping[str, float], current: Mapping[str, float]) -> float:
    names = set(previous) | set(current)
    return sum(abs(current.get(name, 0.0) - previous.get(name, 0.0)) for name in names)


def _validate_target(target: Mapping[str, float]) -> None:
    if not target:
        raise FactorLSExecutionError("EMPTY_TARGET")
    weights = [_ensure_finite(v, "NONFINITE_WEIGHT") for v in target.values()]
    gross = sum(abs(v) for v in weights)
    net = sum(weights)
    if abs(gross - 2.0) > 1e-10:
        raise FactorLSExecutionError("GROSS_NOT_TWO")
    if abs(net) > 1e-10:
        raise FactorLSExecutionError("NET_NOT_ZERO")
    if max(abs(v) for v in weights) > 0.15 + 1e-12:
        raise FactorLSExecutionError("CONCENTRATION_BREACH")


def _capacity_ok(previous: Mapping[str, float], current: Mapping[str, float], med_quote_volume: Mapping[str, float]) -> tuple[bool, float]:
    max_util = 0.0
    for name in set(previous) | set(current):
        delta = abs(current.get(name, 0.0) - previous.get(name, 0.0))
        if delta == 0:
            continue
        denom = med_quote_volume.get(name)
        if denom is None:
            return False, float("nan")
        denom_f = _ensure_finite(denom, "NONFINITE_CAPACITY_DENOMINATOR")
        if denom_f <= 0:
            return False, float("nan")
        util = delta * REFERENCE_NAV / denom_f
        max_util = max(max_util, util)
        if util > 0.01 + 1e-12:
            return False, max_util
    return True, max_util


def analyze_weekly_records(records: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    previous: dict[str, float] = {}
    admitted: list[dict[str, Any]] = []

    for raw in records:
        day = str(raw.get("date", ""))
        support = bool(raw.get("support", True))
        target_raw = raw.get("target")
        if not isinstance(target_raw, Mapping):
            support = False
            target: dict[str, float] = {}
        else:
            target = {str(k): _ensure_finite(v, "NONFINITE_WEIGHT") for k, v in target_raw.items()}

        if support:
            try:
                _validate_target(target)
            except FactorLSExecutionError:
                support = False

        med_qv_raw = raw.get("median_quote_volume", {})
        med_qv = med_qv_raw if isinstance(med_qv_raw, Mapping) else {}
        if support:
            cap_ok, max_util = _capacity_ok(previous, target, med_qv)
            if not cap_ok:
                support = False
        else:
            max_util = float("nan")

        if not support:
            if admitted and previous:
                admitted.pop()
            previous = {}
            continue

        turnover = _transition_turnover(previous, target)
        price_returns = raw.get("asset_returns")
        if not isinstance(price_returns, Mapping):
            raise FactorLSExecutionError(f"MISSING_ASSET_RETURNS:{day}")
        price_pnl = 0.0
        for name, weight in target.items():
            if name not in price_returns:
                raise FactorLSExecutionError(f"MISSING_ASSET_RETURN:{day}:{name}")
            price_pnl += weight * _ensure_finite(price_returns[name], "NONFINITE_ASSET_RETURN")

        funding_pnl = _ensure_finite(raw.get("funding_pnl", 0.0), "NONFINITE_FUNDING")
        beta = _ensure_finite(raw.get("portfolio_beta", 0.0), "NONFINITE_BETA")
        btc_state = str(raw.get("btc_state", ""))
        if btc_state not in {"BTC_UP", "BTC_NONUP"}:
            raise FactorLSExecutionError("INVALID_BTC_STATE")

        c0 = price_pnl + funding_pnl
        c1 = c0 - turnover * 0.001
        c2 = c0 - turnover * 0.002
        admitted.append({
            "date": day,
            "year": day[:4],
            "btc_state": btc_state,
            "turnover": turnover,
            "c0": c0,
            "c1": c1,
            "c2": c2,
            "beta": beta,
            "max_capacity_utilization": max_util,
            "max_abs_weight": max(abs(v) for v in target.values()),
        })
        previous = dict(target)

    c2_values = [float(row["c2"]) for row in admitted]
    support = len(admitted) >= MIN_WEEKS
    by_year: dict[str, list[float]] = {}
    by_state: dict[str, list[float]] = {"BTC_UP": [], "BTC_NONUP": []}
    for row in admitted:
        by_year.setdefault(str(row["year"]), []).append(float(row["c2"]))
        by_state[str(row["btc_state"])].append(float(row["c2"]))
    qualifying_years = {year: vals for year, vals in by_year.items() if len(vals) >= 20}
    blocks = _four_blocks(c2_values) if c2_values else []
    support = support and len(blocks) == 4 and all(len(block) >= 20 for block in blocks)
    support = support and len(qualifying_years) >= 3
    support = support and all(len(by_state[state]) >= 30 for state in by_state)

    if not support:
        return {
            "classification": "INCONCLUSIVE_INSUFFICIENT_SUPPORT",
            "gates": {"G0_EXECUTION": True, "G1_SUPPORT": False},
            "observations": len(admitted),
        }

    ci_low, ci_high = _bootstrap_ci(c2_values)
    mean_c0 = sum(float(row["c0"]) for row in admitted) / len(admitted)
    mean_c1 = sum(float(row["c1"]) for row in admitted) / len(admitted)
    mean_c2 = sum(c2_values) / len(c2_values)
    sd = stdev(c2_values)
    sharpe = sqrt(52.0) * mean_c2 / sd if sd > 0 else float("inf")
    drawdown = _max_drawdown(c2_values)
    hit = sum(v > 0 for v in c2_values) / len(c2_values)
    block_means = [sum(block) / len(block) for block in blocks]
    year_means = {year: sum(vals) / len(vals) for year, vals in qualifying_years.items()}
    state_means = {state: sum(vals) / len(vals) for state, vals in by_state.items()}
    loyo = {}
    for year in qualifying_years:
        vals = [float(row["c2"]) for row in admitted if row["year"] != year]
        loyo[year] = sum(vals) / len(vals)

    abs_betas = sorted(abs(float(row["beta"])) for row in admitted)
    p90_beta = _quantile(abs_betas, 0.90)
    median_beta = median(abs_betas)
    max_weight = max(float(row["max_abs_weight"]) for row in admitted)
    max_capacity = max(float(row["max_capacity_utilization"]) for row in admitted)

    gates = {
        "G0_EXECUTION": True,
        "G1_SUPPORT": True,
        "G2_NET_RETURN": mean_c2 > 0 and ci_low > 0,
        "G3_SHARPE": sharpe >= 0.75,
        "G4_DRAWDOWN": drawdown >= -0.35,
        "G5_HIT_RATE": hit >= 0.52,
        "G6_CHRONOLOGY": sum(x > 0 for x in block_means) >= 3 and all(x > -0.0025 for x in block_means),
        "G7_CALENDAR": sum(x > 0 for x in year_means.values()) >= 3,
        "G8_STATE_AND_LOYO": all(x > 0 for x in state_means.values()) and all(x > 0 for x in loyo.values()),
        "G9_IMPLEMENTATION": mean_c0 >= mean_c1 >= mean_c2 and max_weight <= 0.15 and max_capacity <= 0.01 and median_beta <= 0.20 and p90_beta <= 0.50,
    }
    classification = "PASS_VALIDATED_FACTOR_LS" if all(gates.values()) else "FAIL_FACTOR_LS_GATES"
    return {
        "classification": classification,
        "gates": gates,
        "observations": len(admitted),
        "mean_c0": mean_c0,
        "mean_c1": mean_c1,
        "mean_c2": mean_c2,
        "bootstrap_95_ci": [ci_low, ci_high],
        "annualized_sharpe": sharpe,
        "max_drawdown": drawdown,
        "positive_week_fraction": hit,
        "chronological_block_means": block_means,
        "calendar_year_means": year_means,
        "btc_state_means": state_means,
        "leave_one_year_out_means": loyo,
        "median_abs_beta": median_beta,
        "p90_abs_beta": p90_beta,
        "max_capacity_utilization": max_capacity,
        "max_abs_target_weight": max_weight,
    }


class FactorLS0088Engine:
    """Source-qualified post-marker engine. The common runner owns reads/persistence."""

    def validate_source_keys(self, source_keys: Sequence[str]) -> None:
        from .source_adapter import validate_source_keys
        validate_source_keys(source_keys)

    def execute(self, context: Any) -> Mapping[str, Any]:
        from .construction import build_weekly_records
        from .source_adapter import normalize_controlled_sources
        panel, funding = normalize_controlled_sources(context.sources)
        return analyze_weekly_records(build_weekly_records(panel, funding))
