from __future__ import annotations

from dataclasses import dataclass
from math import erf, exp, log, sqrt
from typing import Any, Mapping, Sequence

import numpy as np

RID = "BRRK-SOL-LONG-SIDEWAYS-CONTROLLER-INTEGRATION-0071"
PASS = "PASS_LOCKED_P02_ECONOMIC_CONTROLLER_INTEGRATION"
FAIL = "FAIL_NO_ROBUST_LOCKED_P02_ECONOMIC_CONTROLLER_VALUE"
INCONCLUSIVE = "MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_ECONOMIC_SUPPORT"
INVALID = "INVALID_EXECUTION"

CANDIDATES = (
    "C01_BINARY_RISK_OFF",
    "C02_LINEAR_DERISK",
    "C03_PIECEWISE_DERISK",
    "C04_VOL_ADJUSTED",
    "C05_DRAWDOWN_AWARE",
    "C06_HYSTERESIS",
)
CONTROLS = ("M01_SIGNAL_OFF_VOL_ONLY", "M02_SIGNAL_OFF_DRAWDOWN_ONLY")
BENCHMARK = "B00_FULLY_INVESTED_SOL"
COST_BPS = {"C0_THEORETICAL": 0.0, "C1_REALISTIC": 10.0, "C2_STRESSED": 30.0}
MIN_ROWS = 252
BOOTSTRAP_REPS = 4000
BOOTSTRAP_BLOCK = 20
BOOTSTRAP_SEED = 710071
DSR_TRIALS = 6
DSR_GATE = 0.95
TOL = 1e-12


@dataclass(frozen=True)
class SeriesMetrics:
    cagr: float
    annualized_volatility: float
    sharpe: float
    sortino: float
    max_drawdown: float
    calmar: float
    downside_deviation: float
    worst_1: float
    worst_5: float
    worst_10: float
    worst_20: float
    average_exposure: float
    time_in_cash: float
    switch_count: int
    turnover_sum: float
    terminal_nav: float
    recovery_time: int | None


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + erf(x / sqrt(2.0)))


def _as_float(x: Any) -> float:
    return float(np.asarray(x).item())


def _validate_inputs(scores: Sequence[float], sol_returns: Sequence[float], cash_returns: Sequence[float], lag20: Sequence[Sequence[float]], lagged_drawdown: Sequence[float]) -> None:
    n = len(scores)
    if n == 0 or any(len(x) != n for x in (sol_returns, cash_returns, lag20, lagged_drawdown)):
        raise ValueError("common-support length mismatch")
    if any(len(row) != 20 for row in lag20):
        raise ValueError("volatility overlay requires exactly 20 lagged returns")
    a = np.asarray(scores, dtype=float)
    if np.any(~np.isfinite(a)) or np.any((a < 0.0) | (a > 1.0)):
        raise ValueError("P02 score outside [0,1] or nonfinite")


def controller_exposures(scores: Sequence[float], lag20: Sequence[Sequence[float]], lagged_drawdown: Sequence[float]) -> dict[str, np.ndarray]:
    s = np.asarray(scores, dtype=float)
    vols = np.asarray([np.std(np.asarray(row, dtype=float), ddof=1) * sqrt(365.0) for row in lag20], dtype=float)
    vol_overlay = np.where(vols > 0.0, np.clip(0.60 / vols, 0.0, 1.0), 1.0)
    dd = np.asarray(lagged_drawdown, dtype=float)
    dd_overlay = np.select(
        [dd > -0.10, dd > -0.20, dd > -0.30],
        [1.0, 0.75, 0.50],
        default=0.25,
    ).astype(float)

    hyst = np.empty(len(s), dtype=float)
    state = 1.0
    for i, score in enumerate(s):
        if score >= 0.60:
            state = 0.0
        elif score <= 0.40:
            state = 1.0
        hyst[i] = state

    out = {
        BENCHMARK: np.ones(len(s), dtype=float),
        "C01_BINARY_RISK_OFF": np.where(s < 0.50, 1.0, 0.0),
        "C02_LINEAR_DERISK": np.clip(1.0 - s, 0.0, 1.0),
        "C03_PIECEWISE_DERISK": np.where(s < 0.40, 1.0, np.where(s < 0.60, 0.50, 0.0)),
        "C04_VOL_ADJUSTED": np.clip(1.0 - s, 0.0, 1.0) * vol_overlay,
        "C05_DRAWDOWN_AWARE": np.clip(1.0 - s, 0.0, 1.0) * dd_overlay,
        "C06_HYSTERESIS": hyst,
        "M01_SIGNAL_OFF_VOL_ONLY": vol_overlay,
        "M02_SIGNAL_OFF_DRAWDOWN_ONLY": dd_overlay,
    }
    for key, value in out.items():
        if np.any((value < -TOL) | (value > 1.0 + TOL)):
            raise ValueError(f"exposure bound drift {key}")
    return out


def turnover(exposure: Sequence[float]) -> np.ndarray:
    x = np.asarray(exposure, dtype=float)
    prev = np.concatenate(([0.0], x[:-1]))
    return np.abs(x - prev)


def net_returns(exposure: Sequence[float], sol_returns: Sequence[float], cash_returns: Sequence[float], cost_bps: float) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(exposure, dtype=float)
    r = np.asarray(sol_returns, dtype=float)
    c = np.asarray(cash_returns, dtype=float)
    if len(x) != len(r) or len(x) != len(c):
        raise ValueError("economic series length mismatch")
    idle = np.clip(1.0 - x, 0.0, 1.0)
    t = turnover(x)
    gross = x * r + idle * c
    return gross - t * (float(cost_bps) / 10000.0), t


def nav_from_returns(returns: Sequence[float]) -> np.ndarray:
    rr = np.asarray(returns, dtype=float)
    if np.any(rr <= -1.0):
        raise ValueError("return <= -100% invalid")
    return np.cumprod(1.0 + rr)


def _rolling_worst(rr: np.ndarray, window: int) -> float:
    if len(rr) < window:
        return float("nan")
    vals = [float(np.prod(1.0 + rr[i:i + window]) - 1.0) for i in range(len(rr) - window + 1)]
    return min(vals)


def _recovery_time(nav: np.ndarray) -> int | None:
    running = np.maximum.accumulate(nav)
    max_wait = 0
    open_start: int | None = None
    unrecovered = False
    for i, (n, h) in enumerate(zip(nav, running)):
        if n < h - 1e-15 and open_start is None:
            open_start = i - 1 if i > 0 else 0
        if open_start is not None and n >= h - 1e-15:
            max_wait = max(max_wait, i - open_start)
            open_start = None
    if open_start is not None:
        unrecovered = True
    return None if unrecovered else int(max_wait)


def metrics(returns: Sequence[float], exposure: Sequence[float], dates: Sequence[Any] | None = None) -> SeriesMetrics:
    rr = np.asarray(returns, dtype=float)
    x = np.asarray(exposure, dtype=float)
    if len(rr) < 2 or len(rr) != len(x):
        raise ValueError("metrics support invalid")
    nav = nav_from_returns(rr)
    if dates is not None and len(dates) == len(rr):
        d0 = np.datetime64(dates[0], "D")
        d1 = np.datetime64(dates[-1], "D")
        elapsed_days = max(int((d1 - d0).astype(int)), 1)
    else:
        elapsed_days = max(len(rr) - 1, 1)
    cagr = float(nav[-1] ** (365.0 / elapsed_days) - 1.0)
    vol = float(np.std(rr, ddof=1) * sqrt(365.0))
    sharpe = float(np.mean(rr) * 365.0 / vol) if vol > 0 else float("nan")
    downside = np.minimum(rr, 0.0)
    ddev = float(np.std(downside, ddof=1) * sqrt(365.0))
    sortino = float(np.mean(rr) * 365.0 / ddev) if ddev > 0 else float("nan")
    drawdowns = nav / np.maximum.accumulate(nav) - 1.0
    mdd = float(np.min(drawdowns))
    calmar = float(cagr / abs(mdd)) if mdd < 0 else float("nan")
    t = turnover(x)
    return SeriesMetrics(
        cagr=cagr,
        annualized_volatility=vol,
        sharpe=sharpe,
        sortino=sortino,
        max_drawdown=mdd,
        calmar=calmar,
        downside_deviation=ddev,
        worst_1=float(np.min(rr)),
        worst_5=_rolling_worst(rr, 5),
        worst_10=_rolling_worst(rr, 10),
        worst_20=_rolling_worst(rr, 20),
        average_exposure=float(np.mean(x)),
        time_in_cash=float(np.mean((1.0 - x) > 1e-12)),
        switch_count=int(np.sum(t > 1e-12)),
        turnover_sum=float(np.sum(t)),
        terminal_nav=float(nav[-1]),
        recovery_time=_recovery_time(nav),
    )


def cost_break_even_bps(exposure: Sequence[float], sol_returns: Sequence[float], cash_returns: Sequence[float], benchmark_terminal_nav: float) -> float | str:
    def terminal(cost: float) -> float:
        rr, _ = net_returns(exposure, sol_returns, cash_returns, cost)
        return float(nav_from_returns(rr)[-1])
    lo, hi = 0.0, 1000.0
    f_lo = terminal(lo) - benchmark_terminal_nav
    f_hi = terminal(hi) - benchmark_terminal_nav
    if f_lo < 0:
        return 0.0
    if f_hi > 0:
        return "REPORT_GT_1000"
    for _ in range(80):
        mid = 0.5 * (lo + hi)
        if terminal(mid) - benchmark_terminal_nav >= 0:
            lo = mid
        else:
            hi = mid
    return float(0.5 * (lo + hi))


def deflated_sharpe_probability(returns: Sequence[float], observed_sharpe: float, trials: int = DSR_TRIALS) -> float:
    rr = np.asarray(returns, dtype=float)
    t = len(rr)
    if t < 3 or trials != 6 or not np.isfinite(observed_sharpe):
        return float("nan")
    centered = rr - np.mean(rr)
    sd = np.std(rr, ddof=1)
    if sd <= 0:
        return float("nan")
    skew = float(np.mean((centered / sd) ** 3))
    kurt = float(np.mean((centered / sd) ** 4))
    gamma = 0.5772156649015329
    z1 = _norm_ppf(1.0 - 1.0 / trials)
    z2 = _norm_ppf(1.0 - 1.0 / (trials * exp(1.0)))
    expected_max = (1.0 - gamma) * z1 + gamma * z2
    denom = sqrt(max((1.0 - skew * observed_sharpe + ((kurt - 1.0) / 4.0) * observed_sharpe ** 2) / max(t - 1, 1), 1e-18))
    return float(_norm_cdf((observed_sharpe - expected_max) / denom))


def _norm_ppf(p: float) -> float:
    # Acklam inverse-normal approximation; deterministic and dependency-free.
    if not 0.0 < p < 1.0:
        raise ValueError("p outside (0,1)")
    a = [-3.969683028665376e1, 2.209460984245205e2, -2.759285104469687e2, 1.383577518672690e2, -3.066479806614716e1, 2.506628277459239]
    b = [-5.447609879822406e1, 1.615858368580409e2, -1.556989798598866e2, 6.680131188771972e1, -1.328068155288572e1]
    c = [-7.784894002430293e-3, -3.223964580411365e-1, -2.400758277161838, -2.549732539343734, 4.374664141464968, 2.938163982698783]
    d = [7.784695709041462e-3, 3.224671290700398e-1, 2.445134137142996, 3.754408661907416]
    plow, phigh = 0.02425, 1.0 - 0.02425
    if p < plow:
        q = sqrt(-2.0 * log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)
    if p > phigh:
        q = sqrt(-2.0 * log(1.0-p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1.0)
    q = p - 0.5
    r = q*q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1.0)


def moving_block_indices(n: int, reps: int = BOOTSTRAP_REPS, block: int = BOOTSTRAP_BLOCK, seed: int = BOOTSTRAP_SEED) -> np.ndarray:
    if n < block:
        raise ValueError("insufficient bootstrap support")
    rng = np.random.default_rng(seed)
    blocks_needed = int(np.ceil(n / block))
    out = np.empty((reps, n), dtype=int)
    max_start = n - block
    for r in range(reps):
        starts = rng.integers(0, max_start + 1, size=blocks_needed)
        idx = np.concatenate([np.arange(s, s + block) for s in starts])[:n]
        out[r] = idx
    return out


def bootstrap_probabilities(candidate_returns: Sequence[float], benchmark_returns: Sequence[float], candidate_exposure: Sequence[float], benchmark_exposure: Sequence[float], dates: Sequence[Any] | None = None) -> dict[str, float]:
    cr = np.asarray(candidate_returns, dtype=float)
    br = np.asarray(benchmark_returns, dtype=float)
    cx = np.asarray(candidate_exposure, dtype=float)
    bx = np.asarray(benchmark_exposure, dtype=float)
    if not (len(cr) == len(br) == len(cx) == len(bx)):
        raise ValueError("bootstrap common support mismatch")
    idxs = moving_block_indices(len(cr))
    mdd_better = 0
    return_ok = 0
    valid = 0
    for idx in idxs:
        try:
            cm = metrics(cr[idx], cx[idx])
            bm = metrics(br[idx], bx[idx])
        except ValueError:
            continue
        valid += 1
        if abs(cm.max_drawdown) < abs(bm.max_drawdown):
            mdd_better += 1
        cond = (cm.cagr / bm.cagr >= 0.75) if bm.cagr > 0 else (cm.cagr >= bm.cagr)
        if cond:
            return_ok += 1
    if valid == 0:
        return {"valid_replicates": 0, "p_mdd_better": float("nan"), "p_return_gate": float("nan")}
    return {"valid_replicates": valid, "p_mdd_better": mdd_better / valid, "p_return_gate": return_ok / valid}


def _gate_return(candidate: SeriesMetrics, benchmark: SeriesMetrics, ratio: float) -> bool:
    return candidate.cagr / benchmark.cagr >= ratio if benchmark.cagr > 0 else candidate.cagr >= benchmark.cagr


def matched_attribution(candidate: SeriesMetrics, control: SeriesMetrics) -> bool:
    return_gate = candidate.cagr >= (0.95 * control.cagr) if control.cagr > 0 else candidate.cagr >= control.cagr
    checks = [
        candidate.sharpe >= control.sharpe + 0.05,
        abs(candidate.max_drawdown) <= 0.95 * abs(control.max_drawdown),
        candidate.worst_20 >= control.worst_20 + 0.05 * abs(control.worst_20) if control.worst_20 < 0 else candidate.worst_20 >= control.worst_20,
    ]
    return bool(return_gate and sum(bool(x) for x in checks) >= 2)


def evaluate(*, scores: Sequence[float], sol_returns: Sequence[float], cash_returns: Sequence[float], lag20: Sequence[Sequence[float]], lagged_drawdown: Sequence[float], dates: Sequence[Any] | None = None, identity_ok: bool = True, reproduction_ok: bool = True, read_counts_ok: bool = True, cash_accounting_ok: bool = True) -> dict[str, Any]:
    try:
        _validate_inputs(scores, sol_returns, cash_returns, lag20, lagged_drawdown)
    except ValueError as exc:
        return _terminal(INVALID, False, str(exc))
    if not all((identity_ok, reproduction_ok, read_counts_ok, cash_accounting_ok)):
        return _terminal(INVALID, False, "identity/reproduction/read/cash gate failed")
    n = len(scores)
    if n < MIN_ROWS:
        return _terminal(INCONCLUSIVE, True, "common support below 252", common_rows=n)

    try:
        expo = controller_exposures(scores, lag20, lagged_drawdown)
        if tuple(k for k in expo if k in CANDIDATES) != CANDIDATES or sum(k in expo for k in CONTROLS) != 2:
            return _terminal(INVALID, False, "candidate/control count drift")
        results: dict[str, Any] = {}
        for key, x in expo.items():
            by_cost: dict[str, Any] = {}
            for cost_name, bps in COST_BPS.items():
                rr, t = net_returns(x, sol_returns, cash_returns, bps)
                by_cost[cost_name] = {"returns": rr, "turnover": t, "metrics": metrics(rr, x, dates)}
            results[key] = by_cost
    except Exception as exc:
        return _terminal(INVALID, False, f"economic computation invalid: {exc}")

    b_c1 = results[BENCHMARK]["C1_REALISTIC"]
    b_c2 = results[BENCHMARK]["C2_STRESSED"]
    b_m = b_c1["metrics"]
    passing: list[str] = []
    candidate_evidence: dict[str, Any] = {}

    for cid in CANDIDATES:
        c1 = results[cid]["C1_REALISTIC"]
        c2 = results[cid]["C2_STRESSED"]
        c0 = results[cid]["C0_THEORETICAL"]
        m1 = c1["metrics"]
        m2 = c2["metrics"]
        dsr = deflated_sharpe_probability(c1["returns"], m1.sharpe, DSR_TRIALS)
        be = cost_break_even_bps(expo[cid], sol_returns, cash_returns, b_m.terminal_nav)
        boot = bootstrap_probabilities(c1["returns"], b_c1["returns"], expo[cid], expo[BENCHMARK])

        # Concentration stress: remove best candidate C1 calendar month; synthetic fallback uses 30-session buckets.
        rr_c = np.asarray(c1["returns"], dtype=float)
        rr_b = np.asarray(b_c1["returns"], dtype=float)
        if dates is not None and len(dates) == n:
            months = np.asarray([str(np.datetime64(d, "M")) for d in dates], dtype=object)
        else:
            months = np.asarray([f"B{i//30:04d}" for i in range(n)], dtype=object)
        unique_months = list(dict.fromkeys(months.tolist()))
        month_pnl = {m: float(np.prod(1.0 + rr_c[months == m]) - 1.0) for m in unique_months}
        best_month = max(unique_months, key=lambda m: month_pnl[m])
        keep = months != best_month
        conc_defined = int(np.sum(keep)) >= 2
        if conc_defined:
            cm = metrics(rr_c[keep], np.asarray(expo[cid])[keep])
            bm = metrics(rr_b[keep], np.asarray(expo[BENCHMARK])[keep])
            g8 = _gate_return(cm, bm, 0.70) and abs(cm.max_drawdown) <= 0.90 * abs(bm.max_drawdown)
        else:
            g8 = False

        gates = {
            "G0": True,
            "G1": True,
            "G2": _gate_return(m1, b_m, 0.75),
            "G3": abs(m1.max_drawdown) <= 0.80 * abs(b_m.max_drawdown),
            "G4": m1.worst_20 >= b_m.worst_20 + 0.10 * abs(b_m.worst_20) if b_m.worst_20 < 0 else m1.worst_20 >= b_m.worst_20,
            "G5": m1.sharpe >= b_m.sharpe and np.isfinite(dsr) and dsr >= DSR_GATE,
            "G6": (be == "REPORT_GT_1000") or (isinstance(be, float) and be >= 30.0),
            "G7": _gate_return(m2, b_c2["metrics"], 0.70) and abs(m2.max_drawdown) <= 0.85 * abs(b_c2["metrics"].max_drawdown) and (m2.worst_20 >= b_c2["metrics"].worst_20 + 0.05 * abs(b_c2["metrics"].worst_20) if b_c2["metrics"].worst_20 < 0 else m2.worst_20 >= b_c2["metrics"].worst_20),
            "G8": bool(g8),
            "G9": boot["valid_replicates"] > 0 and boot["p_mdd_better"] >= 0.95 and boot["p_return_gate"] >= 0.90,
            "G10": True,
        }
        if cid == "C04_VOL_ADJUSTED":
            gates["G10"] = matched_attribution(m1, results["M01_SIGNAL_OFF_VOL_ONLY"]["C1_REALISTIC"]["metrics"])
        elif cid == "C05_DRAWDOWN_AWARE":
            gates["G10"] = matched_attribution(m1, results["M02_SIGNAL_OFF_DRAWDOWN_ONLY"]["C1_REALISTIC"]["metrics"])

        passed = all(gates.values())
        if passed:
            passing.append(cid)
        candidate_evidence[cid] = {
            "passed": passed,
            "gates": gates,
            "DSR": dsr,
            "cost_break_even_bps": be,
            "bootstrap": boot,
            "best_month_removed": str(best_month),
            "C0_metrics": _metric_dict(c0["metrics"]),
            "C1_metrics": _metric_dict(m1),
            "C2_metrics": _metric_dict(m2),
        }

    representative = None
    if passing:
        representative = sorted(
            passing,
            key=lambda cid: (
                abs(results[cid]["C1_REALISTIC"]["metrics"].max_drawdown),
                results[cid]["C1_REALISTIC"]["metrics"].turnover_sum,
                cid,
            ),
        )[0]
    classification = PASS if representative is not None else FAIL
    return {
        "research_id": RID,
        "classification": classification,
        "execution_valid": True,
        "common_rows": n,
        "benchmark": _all_cost_metrics(results[BENCHMARK]),
        "controls": {cid: _all_cost_metrics(results[cid]) for cid in CONTROLS},
        "candidates": candidate_evidence,
        "passing_candidates": passing,
        "representative_candidate": representative,
        "candidate_count": 6,
        "matched_control_count": 2,
        "bootstrap_replicates": BOOTSTRAP_REPS,
        "bootstrap_block_length": BOOTSTRAP_BLOCK,
        "bootstrap_seed": BOOTSTRAP_SEED,
        "DSR_trials": 6,
        "PBO": "DIAGNOSTIC_IMPLEMENTED_SEPARATELY_OR_NOT_SUPPORTED",
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }


def _metric_dict(m: SeriesMetrics) -> dict[str, Any]:
    return {k: getattr(m, k) for k in m.__dataclass_fields__}


def _all_cost_metrics(d: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    return {k: _metric_dict(v["metrics"]) for k, v in d.items()}


def _terminal(classification: str, execution_valid: bool, reason: str, common_rows: int | None = None) -> dict[str, Any]:
    return {
        "research_id": RID,
        "classification": classification,
        "execution_valid": execution_valid,
        "common_rows": common_rows,
        "reason": reason,
        "production_authorized": False,
        "signature_authorized": False,
        "order_submission_authorized": False,
    }
