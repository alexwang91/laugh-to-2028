from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
sys.path.insert(0, str(RESEARCH))

import crypto_rotation_backtest as bt
from pit_universe.run_archive_discovery import DATA_API, archive_symbols
from pit_universe.run_dynamic_dispersion import load_panel, ordinary_symbol

EXPERIMENT_ID = "PIT-ALPHA-0016-DYNAMIC-ROTATION"
EVAL_START = pd.Timestamp("2021-05-01")
EVAL_END = pd.Timestamp("2026-08-02")
QVOL_FLOOR = 25_000_000.0
MIN_DAYS = 240
COST_BPS = 5.0
BAND = 0.05
ALT_SLEEVE = 0.50
ALT_CAP = 0.35
HORIZONS = (20, 60, 120, 240)
TREND_WEIGHTS = (0.15, 0.25, 0.30, 0.30)
PLACEBO_SEEDS = tuple(range(2026080400, 2026080500))
EXPLICIT_DUPLICATES = {"WBTC", "WETH", "WBETH", "BETH", "BTCB", "BTCST", "ETHW"}
CORE_MAP = {"BTCUSDT": "BTC", "ETHUSDT": "ETH", "SOLUSDT": "SOL", "BNBUSDT": "BNB"}


def alpha_symbol(symbol: str) -> bool:
    if not ordinary_symbol(symbol):
        return False
    return symbol[:-4] not in EXPLICIT_DUPLICATES


def trend_matrix(prices: pd.DataFrame) -> pd.DataFrame:
    logp = np.log(prices)
    lr = logp.diff()
    out = pd.DataFrame(0.0, index=prices.index, columns=prices.columns)
    valid = pd.DataFrame(True, index=prices.index, columns=prices.columns)
    for horizon, weight in zip(HORIZONS, TREND_WEIGHTS):
        momentum = logp - logp.shift(horizon)
        scale = lr.rolling(horizon).std() * math.sqrt(horizon)
        component = np.tanh(momentum / scale.replace(0.0, np.nan))
        out = out + weight * component
        valid &= component.notna()
    return out.where(valid)


def rv30_matrix(prices: pd.DataFrame) -> pd.DataFrame:
    return np.log(prices).diff().rolling(30).std() * math.sqrt(365.0)


def deterministic_priority(symbols: list[str], seed: int) -> np.ndarray:
    values = []
    for symbol in symbols:
        digest = hashlib.sha256(f"{seed}:{symbol}".encode("utf-8")).digest()
        values.append(int.from_bytes(digest[:8], "big") / 2**64)
    return np.asarray(values, dtype=float)


def build_dynamic_target(
    btc_idx: int,
    beta_budget: np.ndarray,
    btc_trend: np.ndarray,
    eligible: np.ndarray,
    rank_score: np.ndarray,
    top_n: int | None,
    equal_weight_all: bool = False,
    fixed_priority: np.ndarray | None = None,
) -> np.ndarray:
    n_dates, n_assets = eligible.shape
    target = np.zeros((n_dates, n_assets), dtype=float)

    for i in range(n_dates):
        budget = beta_budget[i]
        trend = btc_trend[i]
        if not np.isfinite(budget) or not np.isfinite(trend) or budget <= 0:
            continue
        budget = min(float(budget), 1.0)
        if trend < 0:
            target[i, btc_idx] = budget
            continue

        candidates = np.flatnonzero(eligible[i])
        if len(candidates) == 0:
            target[i, btc_idx] = budget
            continue

        if equal_weight_all:
            selected = candidates
            raw = np.ones(len(selected), dtype=float)
        else:
            order_values = rank_score[i, candidates] if fixed_priority is None else fixed_priority[candidates]
            finite = np.isfinite(order_values)
            candidates = candidates[finite]
            order_values = order_values[finite]
            if len(candidates) == 0:
                target[i, btc_idx] = budget
                continue
            order = np.argsort(-order_values, kind="stable")
            take = min(int(top_n or len(order)), len(order))
            selected = candidates[order[:take]]
            raw = rank_score[i, selected]

        raw = np.where(np.isfinite(raw) & (raw > 0), raw, 0.0)
        if raw.sum() <= 0:
            target[i, btc_idx] = budget
            continue

        target[i, btc_idx] = (1.0 - ALT_SLEEVE) * budget
        alt_weights = ALT_SLEEVE * budget * raw / raw.sum()
        cap = ALT_CAP * budget
        capped = np.minimum(alt_weights, cap)
        target[i, selected] = capped
        target[i, btc_idx] += float(alt_weights.sum() - capped.sum())

    return target


def apply_band_with_forced_exit(target: np.ndarray, available: np.ndarray, band: float = BAND) -> np.ndarray:
    held = np.zeros(target.shape[1], dtype=float)
    out = np.zeros_like(target)
    for i in range(len(target)):
        force_exit = bool(np.any((held > 1e-12) & ~available[i]))
        if force_exit or float(np.abs(target[i] - held).sum()) >= band:
            held = target[i].copy()
        out[i] = held
    return out


def evaluate_array(
    prices: pd.DataFrame,
    target: np.ndarray,
    evaluation_index: pd.Index,
    cost_bps: float = COST_BPS,
    missing_haircut: float = 0.0,
) -> dict:
    available = prices.notna().to_numpy(bool)
    banded = apply_band_with_forced_exit(target, available, BAND)
    held = np.vstack([np.zeros((1, banded.shape[1])), banded[:-1]])

    returns = prices.pct_change(fill_method=None).to_numpy(float)
    first_missing = prices.shift(1).notna().to_numpy(bool) & ~available
    stressed = np.nan_to_num(returns, nan=0.0, posinf=0.0, neginf=0.0)
    if missing_haircut != 0.0:
        haircut_mask = first_missing & (held > 1e-12)
        stressed[haircut_mask] = missing_haircut

    turnover = np.abs(np.diff(held, axis=0, prepend=np.zeros((1, held.shape[1])))).sum(axis=1)
    gross_contrib = held * stressed
    gross_return = gross_contrib.sum(axis=1)
    net_return = gross_return - turnover * cost_bps / 10_000.0
    gross_exposure = np.abs(held).sum(axis=1)

    loc = prices.index.get_indexer(evaluation_index)
    return {
        "return": pd.Series(net_return[loc], index=evaluation_index),
        "turnover": pd.Series(turnover[loc], index=evaluation_index),
        "gross": pd.Series(gross_exposure[loc], index=evaluation_index),
        "held": held[loc],
        "gross_contrib": gross_contrib[loc],
    }


def metrics(result: dict) -> dict:
    ret = result["return"].dropna()
    nav = (1.0 + ret).cumprod()
    years = len(ret) / 365.25
    cagr = float(nav.iloc[-1] ** (1.0 / years) - 1.0)
    drawdown = nav / nav.cummax() - 1.0
    vol = float(ret.std() * math.sqrt(365.0))
    sharpe = float(ret.mean() / ret.std() * math.sqrt(365.0)) if ret.std() > 0 else float("nan")
    return {
        "end_multiple": float(nav.iloc[-1]),
        "final_10k": float(nav.iloc[-1] * 10_000.0),
        "cagr": cagr,
        "max_drawdown": float(drawdown.min()),
        "ann_vol": vol,
        "sharpe": sharpe,
        "calmar": float(cagr / abs(drawdown.min())) if drawdown.min() < 0 else float("nan"),
        "turnover": float(result["turnover"].sum()),
        "avg_gross_exposure": float(result["gross"].mean()),
    }


def annual_returns(ret: pd.Series) -> dict:
    return {str(int(year)): float((1.0 + values).prod() - 1.0) for year, values in ret.groupby(ret.index.year)}


def monthly_capture(ret: pd.Series, btc_ret: pd.Series) -> dict:
    strategy = (1.0 + ret).resample("ME").prod() - 1.0
    btc = (1.0 + btc_ret).resample("ME").prod() - 1.0
    frame = pd.concat([strategy.rename("s"), btc.rename("b")], axis=1).dropna()
    up = frame[frame.b > 0]
    down = frame[frame.b < 0]
    return {
        "upside_capture": float(up.s.sum() / up.b.sum()) if len(up) and up.b.sum() else float("nan"),
        "downside_capture": float(down.s.sum() / down.b.sum()) if len(down) and down.b.sum() else float("nan"),
        "up_months": int(len(up)),
        "down_months": int(len(down)),
    }


def subperiod_metrics(result: dict) -> dict:
    out = {}
    for start in ["2022-01-01", "2023-01-01", "2024-01-01", "2025-01-01", "2026-01-01"]:
        mask = result["return"].index >= pd.Timestamp(start)
        if not mask.any():
            continue
        sub = {
            "return": result["return"].loc[mask],
            "turnover": result["turnover"].loc[mask],
            "gross": result["gross"].loc[mask],
        }
        out[start] = metrics(sub)
    return out


def fixed_v1_target(prices: pd.DataFrame, columns: list[str]) -> np.ndarray:
    fixed = prices[list(CORE_MAP)].rename(columns=CORE_MAP).dropna()
    weights, _ = bt.build_rotation_weights(fixed)
    gross = weights.abs().sum(axis=1)
    scale = pd.Series(1.0, index=weights.index)
    over = gross > 1.0
    scale.loc[over] = 1.0 / gross.loc[over]
    weights = weights.mul(scale, axis=0)
    target = pd.DataFrame(0.0, index=prices.index, columns=columns)
    for symbol, asset in CORE_MAP.items():
        target.loc[weights.index, symbol] = weights[asset]
    return target.to_numpy(float)


def long_form_weights(index: pd.Index, columns: list[str], evaluated: dict[str, dict]) -> pd.DataFrame:
    frames = []
    symbol_array = np.asarray(columns, dtype=object)
    for strategy, result in evaluated.items():
        held = result["held"]
        rows, cols = np.nonzero(np.abs(held) > 1e-12)
        if len(rows) == 0:
            continue
        frames.append(pd.DataFrame({
            "date": index[rows].astype(str),
            "strategy": strategy,
            "symbol": symbol_array[cols],
            "weight": held[rows, cols],
        }))
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame(columns=["date", "strategy", "symbol", "weight"])


def write_svg(equity: pd.DataFrame, path: Path) -> None:
    selected = ["BTC_HOLD", "FIXED_V1_GROSS_1_0", "PIT_ALPHA_TOP2_PRIMARY", "PIT_ALPHA_EQUAL_WEIGHT_ALL_ELIGIBLE"]
    selected = [name for name in selected if name in equity.columns]
    chart = equity[selected].dropna(how="all")
    width, height = 1200, 660
    left, right, top, bottom = 105, 35, 75, 95
    plot_w, plot_h = width - left - right, height - top - bottom
    low, high = 0.0, float(chart.max().max()) * 1.05
    colors = ["#777777", "#111111", "#B13B2E", "#2457A7"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111}.grid{stroke:#dedede}.axis{stroke:#555;stroke-width:1.2}</style>',
        '<text x="105" y="30" font-size="22" font-weight="700">PIT-ALPHA-0016 exact daily NAV</text>',
        f'<text x="105" y="52" font-size="12">$10,000 start · {chart.index[0].date()} to {chart.index[-1].date()} · gross≤1 · 5 bps · 0.05 L1 band</text>',
    ]
    for tick in np.linspace(low, high, 6):
        y = top + plot_h * (high - tick) / max(high - low, 1e-12)
        parts.append(f'<line class="grid" x1="{left}" y1="{y:.2f}" x2="{left + plot_w}" y2="{y:.2f}"/>')
        parts.append(f'<text x="{left - 12}" y="{y + 4:.2f}" font-size="11" text-anchor="end">${tick:,.0f}</text>')
    for year in sorted(set(chart.index.year)):
        positions = np.flatnonzero(chart.index.year == year)
        if len(positions):
            x = left + plot_w * positions[0] / max(len(chart) - 1, 1)
            parts.append(f'<line class="grid" x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top + plot_h}"/>')
            parts.append(f'<text x="{x:.2f}" y="{top + plot_h + 24}" font-size="11" text-anchor="middle">{year}</text>')
    parts.append(f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}"/>')
    parts.append(f'<line class="axis" x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}"/>')
    for position, name in enumerate(selected):
        values = chart[name].ffill().to_numpy(float)
        coordinates = []
        for i, value in enumerate(values):
            x = left + plot_w * i / max(len(values) - 1, 1)
            y = top + plot_h * (high - value) / max(high - low, 1e-12)
            coordinates.append(f"{x:.2f} {y:.2f}")
        parts.append(f'<path d="M {" L ".join(coordinates)}" fill="none" stroke="{colors[position]}" stroke-width="2.5"/>')
        legend_x = left + (position // 2) * 520
        legend_y = height - 58 + (position % 2) * 22
        parts.append(f'<line x1="{legend_x}" y1="{legend_y - 4}" x2="{legend_x + 30}" y2="{legend_y - 4}" stroke="{colors[position]}" stroke-width="3"/>')
        parts.append(f'<text x="{legend_x + 40}" y="{legend_y}" font-size="12">{name} — ${values[-1]:,.0f}</text>')
    parts.append('</svg>')
    path.write_text("\n".join(parts), encoding="utf-8")


def main() -> None:
    symbols = sorted(symbol for symbol in archive_symbols() if alpha_symbol(symbol))
    print(f"candidate_symbols={len(symbols)}", flush=True)
    close, qvol, errors, api_calls = load_panel(symbols)
    close = close.sort_index().loc[:EVAL_END]
    qvol = qvol.reindex(close.index)
    missing_core = [symbol for symbol in CORE_MAP if symbol not in close.columns]
    if missing_core:
        raise RuntimeError(f"Missing core symbols: {missing_core}")
    if len(errors) > max(10, int(0.05 * len(symbols))):
        raise RuntimeError(f"Too many data errors: {len(errors)}/{len(symbols)}")

    columns = list(close.columns)
    btc_idx = columns.index("BTCUSDT")
    btc = close["BTCUSDT"]
    btc_beta, btc_trend_series, _ = bt.btc_last_drop_beta(btc)
    beta_budget = btc_beta.clip(upper=1.0).to_numpy(float)
    btc_trend = btc_trend_series.to_numpy(float)

    own = trend_matrix(close)
    relative = trend_matrix(close.div(btc, axis=0))
    volatility = rv30_matrix(close)
    combined = 0.50 * own + 0.50 * relative
    rank = combined / volatility.replace(0.0, np.nan)

    full_history = close.notna().rolling(MIN_DAYS, min_periods=MIN_DAYS).sum() >= MIN_DAYS
    eligible = full_history & (qvol >= QVOL_FLOOR) & (own > 0) & (relative > 0) & rank.notna()
    eligible["BTCUSDT"] = False

    eligible_array = eligible.to_numpy(bool)
    rank_array = rank.to_numpy(float)

    targets = {
        "PIT_ALPHA_TOP1": build_dynamic_target(btc_idx, beta_budget, btc_trend, eligible_array, rank_array, top_n=1),
        "PIT_ALPHA_TOP2_PRIMARY": build_dynamic_target(btc_idx, beta_budget, btc_trend, eligible_array, rank_array, top_n=2),
        "PIT_ALPHA_TOP3": build_dynamic_target(btc_idx, beta_budget, btc_trend, eligible_array, rank_array, top_n=3),
        "PIT_ALPHA_EQUAL_WEIGHT_ALL_ELIGIBLE": build_dynamic_target(btc_idx, beta_budget, btc_trend, eligible_array, rank_array, top_n=None, equal_weight_all=True),
    }

    btc_hold = np.zeros_like(targets["PIT_ALPHA_TOP2_PRIMARY"])
    btc_hold[:, btc_idx] = 1.0
    btc_dynamic = np.zeros_like(btc_hold)
    btc_dynamic[:, btc_idx] = np.nan_to_num(beta_budget, nan=0.0)
    targets["BTC_HOLD"] = btc_hold
    targets["BTC_DYNAMIC_GROSS_1_0"] = btc_dynamic
    targets["FIXED_V1_GROSS_1_0"] = fixed_v1_target(close, columns)

    evaluation_index = close.index[(close.index >= EVAL_START) & (close.index <= EVAL_END)]
    evaluated = {name: evaluate_array(close, target, evaluation_index) for name, target in targets.items()}
    btc_daily = close["BTCUSDT"].pct_change(fill_method=None).reindex(evaluation_index).fillna(0.0)

    primary = evaluated["PIT_ALPHA_TOP2_PRIMARY"]
    primary_metrics = metrics(primary)

    placebo_rows = []
    for seed in PLACEBO_SEEDS:
        priority = deterministic_priority(columns, seed)
        target = build_dynamic_target(
            btc_idx, beta_budget, btc_trend, eligible_array, rank_array,
            top_n=2, fixed_priority=priority,
        )
        placebo_result = evaluate_array(close, target, evaluation_index)
        placebo_rows.append({"seed": seed, **metrics(placebo_result)})
    placebo = pd.DataFrame(placebo_rows)

    cost_stress = {}
    for cost in [5.0, 10.0, 20.0]:
        result = evaluate_array(close, targets["PIT_ALPHA_TOP2_PRIMARY"], evaluation_index, cost_bps=cost)
        cost_stress[str(int(cost))] = metrics(result)

    delisting_stress = {}
    for haircut in [0.0, -0.25, -0.50]:
        result = evaluate_array(close, targets["PIT_ALPHA_TOP2_PRIMARY"], evaluation_index, missing_haircut=haircut)
        delisting_stress[str(haircut)] = metrics(result)

    exchange_info = requests.get(f"{DATA_API}/api/v3/exchangeInfo", timeout=45).json()
    status_map = {item["symbol"]: item.get("status") for item in exchange_info.get("symbols", [])}
    contribution = pd.Series(primary["gross_contrib"].sum(axis=0), index=columns).sort_values(ascending=False)
    positive_contribution = contribution[contribution > 0]
    inactive_mask = pd.Series({symbol: status_map.get(symbol, "MISSING") != "TRADING" for symbol in columns})
    inactive_contribution = float(contribution[inactive_mask.reindex(contribution.index).fillna(True)].sum())
    contribution_rows = pd.DataFrame({
        "symbol": contribution.index,
        "arithmetic_gross_contribution": contribution.values,
        "current_status": [status_map.get(symbol, "MISSING") for symbol in contribution.index],
        "ever_eligible_days": [int(eligible[symbol].loc[evaluation_index].sum()) for symbol in contribution.index],
    })

    metrics_report = {name: metrics(result) for name, result in evaluated.items()}
    capture_report = {name: monthly_capture(result["return"], btc_daily) for name, result in evaluated.items()}
    annual_report = {name: annual_returns(result["return"]) for name, result in evaluated.items()}
    subperiod_report = {name: subperiod_metrics(result) for name, result in evaluated.items()}

    report = {
        "experiment_id": EXPERIMENT_ID,
        "data": {
            "candidate_symbols": len(symbols),
            "symbols_with_rows": int(close.notna().any().sum()),
            "fetch_error_count": len(errors),
            "fetch_errors": errors,
            "api_calls": api_calls,
            "panel_start": str(close.index.min().date()),
            "panel_end": str(close.index.max().date()),
            "evaluation_start": str(evaluation_index.min().date()),
            "evaluation_end": str(evaluation_index.max().date()),
            "evaluation_days": len(evaluation_index),
        },
        "methodology": {
            "minimum_consecutive_rows": MIN_DAYS,
            "quote_volume_floor": QVOL_FLOOR,
            "rank": "(0.5 own trend + 0.5 relative-to-BTC trend) / rv30",
            "eligibility": "own trend >0 and relative trend >0",
            "portfolio": "BTC 50% core / 50% alt sleeve; universal alt cap 35%; gross<=1",
            "band": BAND,
            "cost_bps": COST_BPS,
            "lookahead": "none; t target held over t+1",
        },
        "metrics": metrics_report,
        "capture": capture_report,
        "annual_returns": annual_report,
        "subperiods": subperiod_report,
        "universe_diagnostics": {
            "mean_liquid_age_eligible_count": float((full_history & (qvol >= QVOL_FLOOR)).sum(axis=1).loc[evaluation_index].mean()),
            "mean_positive_trend_eligible_count": float(eligible.sum(axis=1).loc[evaluation_index].mean()),
            "median_positive_trend_eligible_count": float(eligible.sum(axis=1).loc[evaluation_index].median()),
            "max_positive_trend_eligible_count": int(eligible.sum(axis=1).loc[evaluation_index].max()),
            "days_no_eligible_alt_fraction": float((eligible.sum(axis=1).loc[evaluation_index] == 0).mean()),
            "inactive_or_nontrading_symbols_ever_eligible": int(sum((status_map.get(symbol) != "TRADING") and bool(eligible[symbol].loc[evaluation_index].any()) for symbol in columns)),
        },
        "primary_contribution": {
            "top_20": contribution_rows.head(20).to_dict(orient="records"),
            "top_positive_contributor_share": float(positive_contribution.iloc[0] / positive_contribution.sum()) if len(positive_contribution) else None,
            "top_3_positive_contributor_share": float(positive_contribution.iloc[:3].sum() / positive_contribution.sum()) if len(positive_contribution) else None,
            "inactive_current_status_total_contribution": inactive_contribution,
            "transaction_cost_total": float(primary["turnover"].sum() * COST_BPS / 10_000.0),
        },
        "placebo": {
            "seeds": len(placebo),
            "primary_final_10k": primary_metrics["final_10k"],
            "primary_calmar": primary_metrics["calmar"],
            "final_10k_percentile": float((placebo["final_10k"] < primary_metrics["final_10k"]).mean()),
            "calmar_percentile": float((placebo["calmar"] < primary_metrics["calmar"]).mean()),
            "summary": placebo.drop(columns=["seed"]).quantile([0.05, 0.50, 0.95]).to_dict(),
        },
        "cost_stress": cost_stress,
        "delisting_stress": delisting_stress,
        "decision_rule": "No parameter changes after this report. Evaluate primary Top2 against placebo, concentration, subperiods, costs and delisting stress.",
    }

    output_dir = HERE / "pit_alpha_0016_outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "dynamic_alpha_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    placebo.to_csv(output_dir / "placebo_metrics.csv", index=False)
    contribution_rows.to_csv(output_dir / "asset_contribution.csv", index=False)

    counts = pd.DataFrame({
        "liquid_age_eligible_count": (full_history & (qvol >= QVOL_FLOOR)).sum(axis=1),
        "positive_trend_eligible_count": eligible.sum(axis=1),
    }).loc[evaluation_index]
    counts.index.name = "date"
    counts.to_csv(output_dir / "daily_universe_counts.csv")

    daily_equity = pd.DataFrame({
        name: 10_000.0 * (1.0 + result["return"]).cumprod()
        for name, result in evaluated.items()
    })
    daily_equity.index.name = "date"
    daily_equity.to_csv(output_dir / "daily_equity.csv", float_format="%.10f")

    weight_strategies = {
        name: evaluated[name]
        for name in ["PIT_ALPHA_TOP1", "PIT_ALPHA_TOP2_PRIMARY", "PIT_ALPHA_TOP3", "PIT_ALPHA_EQUAL_WEIGHT_ALL_ELIGIBLE"]
    }
    long_form_weights(evaluation_index, columns, weight_strategies).to_csv(
        output_dir / "daily_held_weights_long.csv", index=False, float_format="%.10f"
    )
    write_svg(daily_equity, output_dir / "pnl_daily.svg")

    print("=== PIT_ALPHA_0016_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
