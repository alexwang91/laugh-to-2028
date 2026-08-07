from __future__ import annotations

"""Pure LEVERAGE-0040 study mechanics frozen before the one-time historical run.

This module contains no network access and no strategy fitting.  It accepts already
frozen daily targets / returns and applies the preregistered P4 mechanics.

IMPORTANT: importing this module does not execute LEVERAGE-0040.
"""

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Mapping, Sequence

import numpy as np
import pandas as pd


ASSETS = ("BTC", "ETH", "SOL", "BNB")
CAPS = (1.0, 1.1, 1.2, 1.3)
REBALANCE_BAND = 0.05
OPERATING_BUDGETS = (0.35, 0.40, 0.45, 0.50)
BOOTSTRAP_BLOCKS = (7, 21, 63)
BOOTSTRAP_RESAMPLES = 10_000
BOOTSTRAP_BASE_SEED = 4040


class StudyContractError(ValueError):
    pass


@dataclass(frozen=True)
class PathResult:
    returns: pd.Series
    nav: pd.Series
    turnover: pd.Series
    gross_exposure: pd.Series
    held_weights: pd.DataFrame
    current_weights_before_decision: pd.DataFrame
    funding_return: pd.Series
    transaction_cost_return: pd.Series


def canonical_json_sha256(obj: object) -> str:
    payload = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _require_assets(frame: pd.DataFrame, name: str) -> pd.DataFrame:
    missing = [a for a in ASSETS if a not in frame.columns]
    extra = [c for c in frame.columns if c not in ASSETS]
    if missing or extra:
        raise StudyContractError(f"{name} must contain exactly {ASSETS}; missing={missing} extra={extra}")
    out = frame.loc[:, ASSETS].astype(float).copy()
    if not np.isfinite(out.to_numpy()).all():
        raise StudyContractError(f"{name} contains non-finite values")
    return out


def recover_defensive_scale(v1_targets: pd.DataFrame, brrk_targets: pd.DataFrame) -> pd.Series:
    v1 = _require_assets(v1_targets, "v1_targets")
    brrk = _require_assets(brrk_targets, "brrk_targets")
    if not v1.index.equals(brrk.index):
        raise StudyContractError("V1 and BRRK target indexes must match exactly")
    v1_gross = v1.abs().sum(axis=1)
    brrk_gross = brrk.abs().sum(axis=1)
    bad = (v1_gross <= 1e-15) & (brrk_gross > 1e-12)
    if bool(bad.any()):
        raise StudyContractError("cannot recover defensive scale when V1 gross is zero but BRRK gross is nonzero")
    scale = pd.Series(0.0, index=v1.index, dtype=float)
    nz = v1_gross > 1e-15
    scale.loc[nz] = brrk_gross.loc[nz] / v1_gross.loc[nz]
    if ((scale < -1e-12) | (scale > 1.0 + 1e-10)).any():
        raise StudyContractError("recovered defensive scale left frozen [0,1] range")
    return scale.clip(0.0, 1.0)


def multiplier_from_defensive_scale(defensive_scale: pd.Series | float, cap: float):
    cap = float(cap)
    if cap not in CAPS:
        raise StudyContractError(f"cap must be one of {CAPS}")
    if isinstance(defensive_scale, pd.Series):
        d = defensive_scale.astype(float)
        if ((d < 0.0) | (d > 1.0) | ~np.isfinite(d)).any():
            raise StudyContractError("defensive scale must remain finite in [0,1]")
        return 1.0 + (cap - 1.0) * d
    d = float(defensive_scale)
    if not math.isfinite(d) or not 0.0 <= d <= 1.0:
        raise StudyContractError("defensive scale must remain finite in [0,1]")
    return 1.0 + (cap - 1.0) * d


def construct_candidate_targets(
    brrk_targets: pd.DataFrame,
    defensive_scale: pd.Series,
    cap: float,
) -> pd.DataFrame:
    base = _require_assets(brrk_targets, "brrk_targets")
    if not base.index.equals(defensive_scale.index):
        raise StudyContractError("target and defensive-scale indexes must match")
    if (base < -1e-12).any().any():
        raise StudyContractError("LEVERAGE-0040 cannot create short targets")
    if (base.abs().sum(axis=1) > 1.0 + 1e-9).any():
        raise StudyContractError("frozen BRRK target gross must remain <=1")
    mult = multiplier_from_defensive_scale(defensive_scale, cap)
    out = base.mul(mult, axis=0)
    if (out.abs().sum(axis=1) > float(cap) + 1e-9).any():
        raise StudyContractError("candidate target gross exceeded preregistered cap")
    return out


def legacy_apply_band(target_weights: pd.DataFrame, band: float = REBALANCE_BAND) -> pd.DataFrame:
    targets = _require_assets(target_weights, "target_weights")
    held = pd.Series(0.0, index=ASSETS, dtype=float)
    out = pd.DataFrame(0.0, index=targets.index, columns=ASSETS)
    for dt, row in targets.iterrows():
        if float((row - held).abs().sum()) >= float(band):
            held = row.copy()
        out.loc[dt] = held
    return out


def simulate_legacy_path(
    target_weights: pd.DataFrame,
    close_prices: pd.DataFrame,
    *,
    start: str | pd.Timestamp,
    end: str | pd.Timestamp,
    cost_bps: float,
) -> PathResult:
    """Replicate the frozen legacy research band/timing for comparator continuity."""
    targets = legacy_apply_band(target_weights)
    prices = _require_assets(close_prices, "close_prices")
    rets = prices.pct_change()
    held = targets.shift(1).fillna(0.0)
    dates = prices.loc[pd.Timestamp(start):pd.Timestamp(end)].index
    held = held.reindex(dates).fillna(0.0)
    rets = rets.reindex(dates).fillna(0.0)
    turnover = held.diff().abs().sum(axis=1)
    if len(turnover):
        turnover.iloc[0] = held.iloc[0].abs().sum()
    price_ret = (held * rets).sum(axis=1)
    cost = turnover * float(cost_bps) / 10_000.0
    net = price_ret - cost
    nav = (1.0 + net).cumprod()
    zero = pd.Series(0.0, index=dates)
    return PathResult(
        returns=net,
        nav=nav,
        turnover=turnover,
        gross_exposure=held.abs().sum(axis=1),
        held_weights=held,
        current_weights_before_decision=pd.DataFrame(np.nan, index=dates, columns=ASSETS),
        funding_return=zero,
        transaction_cost_return=cost,
    )


def routed_perp_weights(
    candidate_held: Mapping[str, float],
    matched_cap1_held: Mapping[str, float] | None,
    *,
    all_perp: bool = False,
) -> dict[str, float]:
    c = {a: float(candidate_held[a]) for a in ASSETS}
    if any((not math.isfinite(v)) or v < -1e-12 for v in c.values()):
        raise StudyContractError("candidate held weights must be finite long-only")
    if all_perp:
        return {a: max(0.0, c[a]) for a in ASSETS}
    if matched_cap1_held is None:
        raise StudyContractError("primary routing requires matched cap1 held weights")
    b = {a: float(matched_cap1_held[a]) for a in ASSETS}
    if any((not math.isfinite(v)) or v < -1e-12 for v in b.values()):
        raise StudyContractError("matched cap1 held weights must be finite long-only")
    btc_spot = min(max(c["BTC"], 0.0), max(b["BTC"], 0.0))
    return {
        "BTC": max(c["BTC"] - btc_spot, 0.0),
        "ETH": max(c["ETH"], 0.0),
        "SOL": max(c["SOL"], 0.0),
        "BNB": max(c["BNB"], 0.0),
    }


def funding_return_from_blocks(
    perp_weights: Mapping[str, float],
    block_rates: Sequence[Mapping[str, float]] | None,
    *,
    adverse_spike_multiplier: float = 1.0,
) -> float:
    """Compound exact same-day 8h funding blocks for fixed daily held weights."""
    if not block_rates:
        return 0.0
    factor = 1.0
    for block in block_rates:
        debit = 0.0
        for asset in ASSETS:
            rate = float(block.get(asset, 0.0))
            if not math.isfinite(rate):
                raise StudyContractError("non-finite funding rate")
            if rate > 0.0:
                rate *= float(adverse_spike_multiplier)
            debit += float(perp_weights[asset]) * rate
        block_factor = 1.0 - debit
        if not math.isfinite(block_factor) or block_factor <= 0.0:
            raise StudyContractError("funding block factor became non-positive")
        factor *= block_factor
    return float(factor - 1.0)


def simulate_p3_3_economic_path(
    target_weights: pd.DataFrame,
    close_prices: pd.DataFrame,
    *,
    start: str | pd.Timestamp,
    end: str | pd.Timestamp,
    cost_bps: float,
    band: float = REBALANCE_BAND,
    fill_fraction: float = 1.0,
    transaction_cost_multiplier: float = 1.0,
    funding_blocks_by_session: Mapping[pd.Timestamp, Sequence[Mapping[str, float]]] | None = None,
    adverse_funding_spike_multiplier: float = 1.0,
    matched_cap1_held: pd.DataFrame | None = None,
    all_perp: bool = False,
    base_btc_fully_spot: bool = False,
) -> PathResult:
    """Simulate P3.3 L1 control using actual drifted economic weights.

    Decision target dated t is compared with economic current weights at t, then
    held over the next daily price return.  Costs/funding change account equity
    and therefore the next decision's economic weights.
    """
    targets = _require_assets(target_weights, "target_weights")
    prices = _require_assets(close_prices, "close_prices")
    if not targets.index.is_monotonic_increasing or not prices.index.is_monotonic_increasing:
        raise StudyContractError("indexes must be monotonic")
    if not (0.0 < float(fill_fraction) <= 1.0):
        raise StudyContractError("fill_fraction must be in (0,1]")
    if float(cost_bps) < 0.0 or float(transaction_cost_multiplier) < 0.0:
        raise StudyContractError("cost inputs must be non-negative")

    common = targets.index.intersection(prices.index).sort_values()
    start_ts, end_ts = pd.Timestamp(start), pd.Timestamp(end)
    common = common[(common >= start_ts) & (common <= end_ts)]
    if len(common) < 2:
        raise StudyContractError("need at least two aligned daily observations")

    px = prices.reindex(common)
    if px.isna().any().any():
        raise StudyContractError("missing prices inside simulation window")
    next_returns = px.pct_change()

    current = pd.Series(0.0, index=ASSETS, dtype=float)
    records = []
    before_records = []
    session_dates = []

    for i in range(1, len(common)):
        decision_date = common[i - 1]
        session_date = common[i]
        target = targets.loc[decision_date].astype(float)
        if (target < -1e-12).any():
            raise StudyContractError("short target encountered")
        if float(target.abs().sum()) > 1.300000001:
            raise StudyContractError("target gross exceeded LEVERAGE-0040 maximum")

        if (current < -1e-12).any():
            raise StudyContractError("current economic weights became short")
        before = current.copy()
        gap = float((target - current).abs().sum())
        if gap >= float(band):
            accepted = current + float(fill_fraction) * (target - current)
        else:
            accepted = current.copy()

        executed_turnover = float((accepted - current).abs().sum())
        cost_ret = executed_turnover * float(cost_bps) / 10_000.0 * float(transaction_cost_multiplier)
        r = next_returns.loc[session_date].fillna(0.0).astype(float)
        price_ret = float((accepted * r).sum())

        if all_perp:
            perp = routed_perp_weights(accepted.to_dict(), None, all_perp=True)
        elif funding_blocks_by_session is None:
            perp = {a: 0.0 for a in ASSETS}
        elif base_btc_fully_spot:
            perp = {
                "BTC": 0.0,
                "ETH": max(float(accepted["ETH"]), 0.0),
                "SOL": max(float(accepted["SOL"]), 0.0),
                "BNB": max(float(accepted["BNB"]), 0.0),
            }
        else:
            if matched_cap1_held is None:
                raise StudyContractError("funding study requires matched cap1 held weights")
            if session_date not in matched_cap1_held.index:
                raise StudyContractError("missing matched cap1 routing reference")
            perp = routed_perp_weights(
                accepted.to_dict(),
                matched_cap1_held.loc[session_date].to_dict(),
                all_perp=False,
            )

        funding_ret = funding_return_from_blocks(
            perp,
            None if funding_blocks_by_session is None else funding_blocks_by_session.get(session_date),
            adverse_spike_multiplier=adverse_funding_spike_multiplier,
        )
        net_ret = price_ret - cost_ret + funding_ret
        factor = 1.0 + net_ret
        if not math.isfinite(factor) or factor <= 0.0:
            raise StudyContractError("path equity became non-positive")

        current = accepted.mul(1.0 + r) / factor

        session_dates.append(session_date)
        before_records.append(before.to_dict())
        records.append(
            {
                "return": net_ret,
                "turnover": executed_turnover,
                "gross_exposure": float(accepted.abs().sum()),
                "funding_return": funding_ret,
                "transaction_cost_return": cost_ret,
                **{f"held__{a}": float(accepted[a]) for a in ASSETS},
            }
        )

    idx = pd.DatetimeIndex(session_dates)
    rec = pd.DataFrame(records, index=idx)
    held = rec[[f"held__{a}" for a in ASSETS]].copy()
    held.columns = list(ASSETS)
    before_df = pd.DataFrame(before_records, index=idx).loc[:, ASSETS]
    nav = (1.0 + rec["return"]).cumprod()
    return PathResult(
        returns=rec["return"],
        nav=nav,
        turnover=rec["turnover"],
        gross_exposure=rec["gross_exposure"],
        held_weights=held,
        current_weights_before_decision=before_df,
        funding_return=rec["funding_return"],
        transaction_cost_return=rec["transaction_cost_return"],
    )


def path_metrics(path: PathResult, annualization: float = 365.25) -> dict[str, float]:
    r = path.returns.astype(float)
    nav = path.nav.astype(float)
    if len(r) == 0:
        raise StudyContractError("empty path")
    years = len(r) / float(annualization)
    cagr = float(nav.iloc[-1] ** (1.0 / years) - 1.0)
    dd = nav / nav.cummax() - 1.0
    std = float(r.std())
    sharpe = float(r.mean() / std * math.sqrt(365.0)) if std > 0 else float("nan")
    mdd = float(dd.min())
    return {
        "end_multiple": float(nav.iloc[-1]),
        "cagr": cagr,
        "max_drawdown": mdd,
        "sharpe": sharpe,
        "calmar": float(cagr / abs(mdd)) if mdd < 0 else float("nan"),
        "turnover": float(path.turnover.sum()),
        "avg_gross_exposure": float(path.gross_exposure.mean()),
    }


def buy_and_hold_returns(close_prices: pd.DataFrame, weights: Mapping[str, float]) -> pd.Series:
    prices = _require_assets(close_prices, "close_prices")
    w = pd.Series({a: float(weights.get(a, 0.0)) for a in ASSETS})
    if (w < -1e-12).any() or float(w.sum()) > 1.0 + 1e-12:
        raise StudyContractError("buy-and-hold weights invalid")
    units = w / prices.iloc[0]
    equity = prices.mul(units, axis=1).sum(axis=1) + (1.0 - float(w.sum()))
    return equity.pct_change().fillna(0.0)


def synthetic_gap_return(held_weights: Mapping[str, float], gaps: Mapping[str, float]) -> float:
    return float(sum(float(held_weights[a]) * float(gaps[a]) for a in ASSETS))


def stressed_log_returns(asset_returns: pd.DataFrame, multiplier: float) -> pd.DataFrame:
    r = _require_assets(asset_returns, "asset_returns")
    if (r <= -1.0).any().any():
        raise StudyContractError("log-return stress requires returns > -100%")
    return np.expm1(np.log1p(r) * float(multiplier))


def select_operating_budget(max_drawdowns: Sequence[float]) -> float | None:
    worst = max(abs(float(x)) for x in max_drawdowns) if max_drawdowns else 0.0
    for budget in OPERATING_BUDGETS:
        if worst <= budget + 1e-12:
            return budget
    return None


def broad_region_eligible(pass_by_cap: Mapping[float, bool], cap: float) -> bool:
    cap = round(float(cap), 2)
    if cap <= 1.0 or not bool(pass_by_cap.get(cap, False)):
        return False
    adjacency = {1.10: (1.20,), 1.20: (1.10, 1.30), 1.30: (1.20,)}
    return any(bool(pass_by_cap.get(n, False)) for n in adjacency[cap])


def stationary_bootstrap_indices(
    n: int,
    mean_block_days: int,
    *,
    resamples: int = BOOTSTRAP_RESAMPLES,
    base_seed: int = BOOTSTRAP_BASE_SEED,
) -> np.ndarray:
    if n <= 0 or mean_block_days <= 0 or resamples <= 0:
        raise StudyContractError("bootstrap dimensions must be positive")
    rng = np.random.default_rng(int(base_seed) + int(mean_block_days))
    p = 1.0 / float(mean_block_days)
    out = np.empty((int(resamples), int(n)), dtype=np.int32)
    out[:, 0] = rng.integers(0, n, size=int(resamples), dtype=np.int32)
    for t in range(1, int(n)):
        restart = rng.random(int(resamples)) < p
        fresh = rng.integers(0, n, size=int(resamples), dtype=np.int32)
        continued = (out[:, t - 1] + 1) % n
        out[:, t] = np.where(restart, fresh, continued)
    return out


def paired_bootstrap_stats(
    candidate_returns: pd.Series,
    comparator_returns: pd.Series,
    mean_block_days: int,
    *,
    resamples: int = BOOTSTRAP_RESAMPLES,
    base_seed: int = BOOTSTRAP_BASE_SEED,
) -> dict[str, float]:
    x = pd.concat(
        [candidate_returns.rename("candidate"), comparator_returns.rename("comparator")],
        axis=1,
        join="inner",
    ).dropna()
    if len(x) < 2:
        raise StudyContractError("insufficient paired returns")
    idx = stationary_bootstrap_indices(
        len(x),
        mean_block_days,
        resamples=resamples,
        base_seed=base_seed,
    )
    c = x["candidate"].to_numpy(dtype=float)
    b = x["comparator"].to_numpy(dtype=float)
    logc = np.log1p(c)
    logb = np.log1p(b)
    c_log_terminal = logc[idx].sum(axis=1)
    b_log_terminal = logb[idx].sum(axis=1)
    prob = float(np.mean(c_log_terminal > b_log_terminal))
    annual_scale = 365.25 / float(len(x))
    c_ann = np.expm1(c_log_terminal * annual_scale)
    b_ann = np.expm1(b_log_terminal * annual_scale)
    diff = c_ann - b_ann
    return {
        "terminal_outperformance_probability": prob,
        "annualized_return_difference_p05": float(np.quantile(diff, 0.05)),
        "annualized_return_difference_median": float(np.quantile(diff, 0.50)),
    }


def result_digest(payload: Mapping[str, object]) -> str:
    return canonical_json_sha256(payload)
