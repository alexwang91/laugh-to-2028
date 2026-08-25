from __future__ import annotations

from collections import defaultdict
from math import erf, isfinite, log, sqrt
from random import Random
from typing import Any, Mapping, Sequence

BOOTSTRAP_SEED = 870087
BOOTSTRAP_REPLICATES = 4_000
BOOTSTRAP_BLOCK = 8
HAC_LAG = 8
MIN_TOTAL_WEEKS = 52
MIN_PER_UNDERLYING = 20
MIN_YEARS = 2
UNDERLYINGS = ("BTC", "ETH")
CLASSIFICATIONS = {
    "PASS_OPTIONS_VRP_STRUCTURE",
    "FAIL_NO_ROBUST_OPTIONS_VRP",
    "INCONCLUSIVE_INSUFFICIENT_OPTIONS_SUPPORT",
}


class OptionsVRPExecutionError(RuntimeError):
    pass


def _finite(value: Any, label: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError) as exc:
        raise OptionsVRPExecutionError(f"INVALID_{label}") from exc
    if not isfinite(out):
        raise OptionsVRPExecutionError(f"NONFINITE_{label}")
    return out


def select_atm_pair(chain: Sequence[Mapping[str, Any]], spot: float, dte: float) -> tuple[Mapping[str, Any], Mapping[str, Any]]:
    """Apply the frozen same-strike ATM selection to one already point-in-time expiry slice."""
    s = _finite(spot, "SPOT")
    expiry_dte = _finite(dte, "DTE")
    if s <= 0 or not 25 <= expiry_dte <= 35:
        raise OptionsVRPExecutionError("UNSUPPORTED_EXPIRY")
    by_strike: dict[float, dict[str, Mapping[str, Any]]] = defaultdict(dict)
    for row in chain:
        strike = _finite(row.get("strike"), "STRIKE")
        if strike <= 0:
            continue
        kind = str(row.get("kind", "")).upper()
        if kind not in {"C", "P", "CALL", "PUT"}:
            continue
        canonical = "C" if kind in {"C", "CALL"} else "P"
        bid = _finite(row.get("bid"), "BID")
        ask = _finite(row.get("ask"), "ASK")
        iv = _finite(row.get("iv"), "IV")
        if bid <= 0 or ask <= 0 or ask < bid or iv <= 0:
            continue
        mid = (bid + ask) / 2.0
        if (ask - bid) / mid > 0.20:
            continue
        if canonical in by_strike[strike]:
            raise OptionsVRPExecutionError("DUPLICATE_OPTION_LEG")
        by_strike[strike][canonical] = row
    valid = [(abs(log(k / s)), k, legs) for k, legs in by_strike.items() if set(legs) == {"C", "P"}]
    if not valid:
        raise OptionsVRPExecutionError("UNSUPPORTED_ATM_PAIR")
    _, _, legs = min(valid, key=lambda item: (item[0], item[1]))
    return legs["C"], legs["P"]


def realized_variance_30(closes: Sequence[float]) -> float:
    """Exactly 30 close-to-close log returns, annualized by 365."""
    if len(closes) != 31:
        raise OptionsVRPExecutionError("RV30_REQUIRES_31_CLOSES")
    values = [_finite(x, "INDEX_CLOSE") for x in closes]
    if any(x <= 0 for x in values):
        raise OptionsVRPExecutionError("NONPOSITIVE_INDEX_CLOSE")
    rets = [log(values[i] / values[i - 1]) for i in range(1, len(values))]
    return 365.0 * sum(r * r for r in rets) / 30.0


def atm_ivar30(call: Mapping[str, Any], put: Mapping[str, Any]) -> float:
    call_iv = _finite(call.get("iv"), "CALL_IV")
    put_iv = _finite(put.get("iv"), "PUT_IV")
    if call_iv <= 0 or put_iv <= 0:
        raise OptionsVRPExecutionError("NONPOSITIVE_IV")
    iv = (call_iv + put_iv) / 2.0
    return iv * iv


def _quantile(values: Sequence[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        raise OptionsVRPExecutionError("EMPTY_QUANTILE")
    pos = (len(ordered) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    weight = pos - lo
    return ordered[lo] * (1.0 - weight) + ordered[hi] * weight


def _moving_block_draw(values: Sequence[float], rng: Random) -> list[float]:
    n = len(values)
    if n == 0:
        raise OptionsVRPExecutionError("EMPTY_BOOTSTRAP")
    block = min(BOOTSTRAP_BLOCK, n)
    out: list[float] = []
    while len(out) < n:
        start = rng.randrange(0, n - block + 1)
        out.extend(values[start : start + block])
    return out[:n]


def moving_block_ci(values: Sequence[float]) -> tuple[float, float]:
    vals = [_finite(x, "BOOTSTRAP_VALUE") for x in values]
    rng = Random(BOOTSTRAP_SEED)
    means = [sum(draw := _moving_block_draw(vals, rng)) / len(draw) for _ in range(BOOTSTRAP_REPLICATES)]
    return _quantile(means, 0.025), _quantile(means, 0.975)


def _normal_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def hac_mean_test(values: Sequence[float], lag: int = HAC_LAG) -> tuple[float, float]:
    vals = [_finite(x, "HAC_VALUE") for x in values]
    n = len(vals)
    if n < 3:
        raise OptionsVRPExecutionError("INSUFFICIENT_HAC_SUPPORT")
    mean = sum(vals) / n
    centered = [x - mean for x in vals]
    gamma0 = sum(x * x for x in centered) / n
    long_run = gamma0
    max_lag = min(lag, n - 1)
    for k in range(1, max_lag + 1):
        gamma = sum(centered[t] * centered[t - k] for t in range(k, n)) / n
        long_run += 2.0 * (1.0 - k / (lag + 1.0)) * gamma
    variance_mean = max(long_run, 0.0) / n
    if variance_mean <= 0:
        if mean == 0:
            return 0.0, 1.0
        return (float("inf") if mean > 0 else float("-inf")), 0.0
    t_stat = mean / sqrt(variance_mean)
    p_value = 2.0 * (1.0 - _normal_cdf(abs(t_stat)))
    return t_stat, min(max(p_value, 0.0), 1.0)


def _chronological_means(values: Sequence[float]) -> list[float]:
    vals = list(values)
    n = len(vals)
    if n < 4:
        raise OptionsVRPExecutionError("INSUFFICIENT_BLOCK_SUPPORT")
    bounds = [round(i * n / 4) for i in range(5)]
    out: list[float] = []
    for i in range(4):
        block = vals[bounds[i] : bounds[i + 1]]
        if not block:
            raise OptionsVRPExecutionError("EMPTY_CHRONOLOGICAL_BLOCK")
        out.append(sum(block) / len(block))
    return out


def analyze_weekly_observations(rows: Sequence[Mapping[str, Any]]) -> Mapping[str, Any]:
    """Adjudicate the frozen G1-G8 family from normalized weekly observations.

    BUILD tests this function only with synthetic rows. ARM must bind the exact
    source schema and construct these rows without changing this adjudication.
    """
    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for raw in rows:
        underlying = str(raw.get("underlying", "")).upper()
        week = str(raw.get("week", ""))
        year = str(raw.get("year", week[:4]))
        if underlying not in UNDERLYINGS or len(week) < 10 or not year.isdigit():
            raise OptionsVRPExecutionError("INVALID_WEEK_IDENTITY")
        identity = (underlying, week)
        if identity in seen:
            raise OptionsVRPExecutionError("DUPLICATE_UNDERLYING_WEEK")
        seen.add(identity)
        normalized.append(
            {
                "underlying": underlying,
                "week": week,
                "year": int(year),
                "vrp30": _finite(raw.get("vrp30"), "VRP30"),
                "pnl_c1": _finite(raw.get("pnl_c1"), "PNL_C1"),
                "pnl_c2": _finite(raw.get("pnl_c2"), "PNL_C2"),
            }
        )
    normalized.sort(key=lambda row: (row["week"], row["underlying"]))

    by_week: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in normalized:
        by_week[row["week"]].append(row)
    counts = {u: sum(r["underlying"] == u for r in normalized) for u in UNDERLYINGS}
    years = sorted({r["year"] for r in normalized})
    support = {
        "total_weeks": len(by_week),
        "BTC": counts["BTC"],
        "ETH": counts["ETH"],
        "calendar_years": years,
    }
    if len(by_week) < MIN_TOTAL_WEEKS or any(counts[u] < MIN_PER_UNDERLYING for u in UNDERLYINGS) or len(years) < MIN_YEARS:
        return {
            "classification": "INCONCLUSIVE_INSUFFICIENT_OPTIONS_SUPPORT",
            "execution_valid": True,
            "candidate_count": 1,
            "support": support,
        }

    weekly: list[dict[str, float | str]] = []
    for week in sorted(by_week):
        group = by_week[week]
        weekly.append(
            {
                "week": week,
                "vrp30": sum(r["vrp30"] for r in group) / len(group),
                "pnl_c1": sum(r["pnl_c1"] for r in group) / len(group),
                "pnl_c2": sum(r["pnl_c2"] for r in group) / len(group),
            }
        )
    vrp = [float(r["vrp30"]) for r in weekly]
    pnl_c1 = [float(r["pnl_c1"]) for r in weekly]
    pnl_c2 = [float(r["pnl_c2"]) for r in weekly]

    mean_vrp = sum(vrp) / len(vrp)
    t_stat, p_value = hac_mean_test(vrp)
    ci = moving_block_ci(vrp)
    btc_mean = sum(r["vrp30"] for r in normalized if r["underlying"] == "BTC") / counts["BTC"]
    eth_mean = sum(r["vrp30"] for r in normalized if r["underlying"] == "ETH") / counts["ETH"]
    vrp_blocks = _chronological_means(vrp)
    pnl_blocks = _chronological_means(pnl_c1)
    mean_c1 = sum(pnl_c1) / len(pnl_c1)
    mean_c2 = sum(pnl_c2) / len(pnl_c2)

    gates = {
        "G1_MEAN_VRP_POSITIVE": mean_vrp > 0,
        "G2_HAC_P_LT_0_05": p_value < 0.05,
        "G3_BOOTSTRAP_CI_POSITIVE": ci[0] > 0,
        "G4_BTC_ETH_MEANS_POSITIVE": btc_mean > 0 and eth_mean > 0,
        "G5_VRP_CHRONOLOGY": sum(x > 0 for x in vrp_blocks) >= 3,
        "G6_C1_MEAN_PNL_POSITIVE": mean_c1 > 0,
        "G7_C2_MEAN_PNL_NONNEGATIVE": mean_c2 >= 0,
        "G8_C1_CHRONOLOGY": sum(x > 0 for x in pnl_blocks) >= 3,
    }
    classification = "PASS_OPTIONS_VRP_STRUCTURE" if all(gates.values()) else "FAIL_NO_ROBUST_OPTIONS_VRP"
    return {
        "classification": classification,
        "execution_valid": True,
        "candidate_count": 1,
        "support": support,
        "weekly_observations": len(weekly),
        "mean_vrp30": mean_vrp,
        "hac_lag8_tstat": t_stat,
        "hac_two_sided_p_value": p_value,
        "bootstrap_95_ci": list(ci),
        "underlying_mean_vrp30": {"BTC": btc_mean, "ETH": eth_mean},
        "vrp_chronological_block_means": vrp_blocks,
        "mean_pnl_c1": mean_c1,
        "mean_pnl_c2": mean_c2,
        "pnl_c1_chronological_block_means": pnl_blocks,
        "gates": gates,
        "bootstrap": {"method": "moving-block", "block_weeks": 8, "replicates": 4_000, "seed": 870087},
        "hac_lag": 8,
    }
