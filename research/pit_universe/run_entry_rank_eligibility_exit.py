from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RESEARCH))

import crypto_rotation_backtest as bt
import run_dynamic_alpha as alpha
import run_pit_alpha_attribution as audit
from pit_universe.run_archive_discovery import DATA_API, archive_symbols
from pit_universe.run_dynamic_dispersion import load_panel

EXPERIMENT_ID = "PIT-ALPHA-0018-ENTRY-RANK-ELIGIBILITY-EXIT"
EVAL_START = alpha.EVAL_START
EVAL_END = alpha.EVAL_END
OUTPUT = HERE / "pit_alpha_0018_outputs"
THRESHOLD = 1e-12


def build_entry_rank_eligibility_exit_target(
    btc_idx: int,
    beta_budget: np.ndarray,
    btc_trend: np.ndarray,
    eligible: np.ndarray,
    rank_score: np.ndarray,
    slots: int = 2,
    fixed_priority: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, pd.DataFrame]:
    """Build signal-date targets with Top-N used only to fill vacancies.

    Incumbents remain selected while `eligible` is true. Falling out of the
    daily Top-N is not an exit. The only exits are eligibility loss or BTC
    risk-off. Current rank scores continue to determine weights exactly as in
    PIT-ALPHA-0016; the experiment changes selection persistence only.
    """
    n_dates, n_assets = eligible.shape
    target = np.zeros((n_dates, n_assets), dtype=float)
    selected_mask = np.zeros((n_dates, n_assets), dtype=bool)
    mandatory_rebalance = np.zeros(n_dates, dtype=bool)
    event_rows: list[dict] = []

    incumbents: list[int] = []
    previous_risk_on = False

    for i in range(n_dates):
        previous = list(incumbents)
        budget = beta_budget[i]
        trend = btc_trend[i]
        valid_budget = np.isfinite(budget) and np.isfinite(trend) and budget > 0
        risk_on = bool(valid_budget and trend >= 0)

        exits: list[int] = []
        entries: list[int] = []

        if not risk_on:
            exits = previous
            incumbents = []
        else:
            retained = [asset for asset in previous if eligible[i, asset]]
            exits = [asset for asset in previous if asset not in retained]
            incumbents = retained

            vacancies = max(0, slots - len(incumbents))
            if vacancies:
                candidates = np.flatnonzero(eligible[i]).tolist()
                candidates = [asset for asset in candidates if asset not in incumbents]
                if candidates:
                    values = (
                        rank_score[i, candidates]
                        if fixed_priority is None
                        else fixed_priority[candidates]
                    )
                    finite = np.isfinite(values)
                    candidates = [asset for asset, keep in zip(candidates, finite) if keep]
                    values = np.asarray(values)[finite]
                    if candidates:
                        order = np.argsort(-values, kind="stable")
                        entries = [candidates[position] for position in order[:vacancies]]
                        incumbents.extend(entries)

        selected_changed = set(previous) != set(incumbents)
        regime_changed = risk_on != previous_risk_on
        mandatory_rebalance[i] = selected_changed or regime_changed
        previous_risk_on = risk_on

        if valid_budget:
            budget_value = min(float(budget), 1.0)
            if not risk_on or not incumbents:
                target[i, btc_idx] = budget_value
            else:
                scores = rank_score[i, incumbents]
                scores = np.where(np.isfinite(scores) & (scores > 0), scores, 0.0)
                if scores.sum() <= 0:
                    # This should not bind because eligibility requires rank availability,
                    # but a deterministic BTC fallback is safer than inventing weights.
                    target[i, btc_idx] = budget_value
                    exits.extend(incumbents)
                    incumbents = []
                    mandatory_rebalance[i] = True
                else:
                    target[i, btc_idx] = (1.0 - alpha.ALT_SLEEVE) * budget_value
                    alt_weights = alpha.ALT_SLEEVE * budget_value * scores / scores.sum()
                    cap = alpha.ALT_CAP * budget_value
                    capped = np.minimum(alt_weights, cap)
                    target[i, incumbents] = capped
                    target[i, btc_idx] += float(alt_weights.sum() - capped.sum())

        if incumbents:
            selected_mask[i, incumbents] = True

        for asset in exits:
            event_rows.append({"row": i, "event": "exit", "asset_index": int(asset)})
        for asset in entries:
            event_rows.append({"row": i, "event": "entry", "asset_index": int(asset)})
        if regime_changed:
            event_rows.append({
                "row": i,
                "event": "risk_on" if risk_on else "risk_off",
                "asset_index": None,
            })

    return target, selected_mask, mandatory_rebalance, pd.DataFrame(event_rows)


def apply_band_with_mandatory_rebalance(
    target: np.ndarray,
    available: np.ndarray,
    mandatory_rebalance: np.ndarray,
    band: float = alpha.BAND,
) -> np.ndarray:
    held = np.zeros(target.shape[1], dtype=float)
    out = np.zeros_like(target)
    for i in range(len(target)):
        unavailable_exit = bool(np.any((held > THRESHOLD) & ~available[i]))
        l1_change = float(np.abs(target[i] - held).sum())
        if bool(mandatory_rebalance[i]) or unavailable_exit or l1_change >= band:
            held = target[i].copy()
        out[i] = held
    return out


def evaluate_stateful(
    prices: pd.DataFrame,
    target: np.ndarray,
    mandatory_rebalance: np.ndarray,
    evaluation_index: pd.Index,
    cost_bps: float = alpha.COST_BPS,
) -> dict:
    available = prices.notna().to_numpy(bool)
    banded = apply_band_with_mandatory_rebalance(
        target, available, mandatory_rebalance, alpha.BAND
    )
    held_full = np.vstack([np.zeros((1, banded.shape[1])), banded[:-1]])
    returns = prices.pct_change(fill_method=None).to_numpy(float)
    returns = np.nan_to_num(returns, nan=0.0, posinf=0.0, neginf=0.0)

    turnover_full = np.abs(
        np.diff(held_full, axis=0, prepend=np.zeros((1, held_full.shape[1])))
    ).sum(axis=1)
    gross_contrib_full = held_full * returns
    gross_return_full = gross_contrib_full.sum(axis=1)
    net_return_full = gross_return_full - turnover_full * cost_bps / 10_000.0
    gross_exposure_full = np.abs(held_full).sum(axis=1)

    locations = prices.index.get_indexer(evaluation_index)
    return {
        "return": pd.Series(net_return_full[locations], index=evaluation_index),
        "turnover": pd.Series(turnover_full[locations], index=evaluation_index),
        "gross": pd.Series(gross_exposure_full[locations], index=evaluation_index),
        "held": held_full[locations],
        "gross_contrib": gross_contrib_full[locations],
        "banded_target_full": banded,
    }


def exact_held_frame(result: dict, index: pd.Index, columns: list[str]) -> pd.DataFrame:
    return pd.DataFrame(result["held"], index=index, columns=columns)


def contribution_report(
    result: dict,
    columns: list[str],
    status_map: dict[str, str],
    eligible: pd.DataFrame,
    evaluation_index: pd.Index,
) -> tuple[pd.DataFrame, dict]:
    contribution = pd.Series(
        result["gross_contrib"].sum(axis=0), index=columns
    ).sort_values(ascending=False)
    rows = pd.DataFrame({
        "symbol": contribution.index,
        "arithmetic_gross_contribution": contribution.values,
        "current_status": [status_map.get(symbol, "MISSING") for symbol in contribution.index],
        "ever_eligible_days": [
            int(eligible[symbol].loc[evaluation_index].sum()) for symbol in contribution.index
        ],
    })
    positive = contribution[contribution > 0]
    inactive = pd.Series(
        {symbol: status_map.get(symbol, "MISSING") != "TRADING" for symbol in columns}
    )
    summary = {
        "largest_positive_contributor_share": (
            float(positive.iloc[0] / positive.sum()) if len(positive) else None
        ),
        "top_3_positive_contributor_share": (
            float(positive.iloc[:3].sum() / positive.sum()) if len(positive) else None
        ),
        "inactive_current_status_total_contribution": float(
            contribution[inactive.reindex(contribution.index).fillna(True)].sum()
        ),
        "positive_contributor_count": int(len(positive)),
    }
    return rows, summary


def holding_summary(spells: pd.DataFrame) -> dict:
    if spells.empty:
        return {
            "spell_count": 0,
            "symbols_held": 0,
            "duration": {},
            "positive_contribution_fraction": None,
            "median_reentries_per_symbol": None,
            "max_reentries_symbol": None,
            "max_reentries": 0,
        }
    reentries = spells.groupby("symbol").size()
    return {
        "spell_count": int(len(spells)),
        "symbols_held": int(spells["symbol"].nunique()),
        "duration": audit.quantile_dict(spells["duration_days"]),
        "positive_contribution_fraction": float(spells["positive_contribution"].mean()),
        "median_reentries_per_symbol": float(reentries.median()),
        "max_reentries_symbol": str(reentries.idxmax()),
        "max_reentries": int(reentries.max()),
        "top_10_spells_by_contribution": spells.nlargest(
            10, "arithmetic_gross_contribution"
        ).to_dict(orient="records"),
    }


def write_svg(equity: pd.DataFrame, path: Path) -> None:
    selected = [
        "PIT_ALPHA_0016_DAILY_TOP2",
        "PIT_ALPHA_0018_ELIGIBILITY_EXIT",
        "BTC_DYNAMIC_GROSS_1_0",
        "FIXED_V1_GROSS_1_0",
    ]
    chart = equity[[name for name in selected if name in equity.columns]].dropna(how="all")
    width, height = 1200, 660
    left, right, top, bottom = 105, 35, 75, 95
    plot_w, plot_h = width - left - right, height - top - bottom
    low, high = 0.0, float(chart.max().max()) * 1.05
    colors = ["#B13B2E", "#2457A7", "#777777", "#111111"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111}.grid{stroke:#dedede}.axis{stroke:#555;stroke-width:1.2}</style>',
        '<text x="105" y="30" font-size="22" font-weight="700">PIT-ALPHA-0018 exact daily NAV</text>',
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
    for position, name in enumerate(chart.columns):
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
    symbols = sorted(symbol for symbol in archive_symbols() if alpha.alpha_symbol(symbol))
    print(f"candidate_symbols={len(symbols)}", flush=True)
    close, qvol, errors, api_calls = load_panel(symbols)
    close = close.sort_index().sort_index(axis=1).loc[:EVAL_END]
    qvol = qvol.reindex(index=close.index, columns=close.columns)
    if errors:
        raise RuntimeError(f"Data fetch errors: {len(errors)}")
    missing_core = [symbol for symbol in alpha.CORE_MAP if symbol not in close.columns]
    if missing_core:
        raise RuntimeError(f"Missing core symbols: {missing_core}")

    columns = list(close.columns)
    btc_idx = columns.index("BTCUSDT")
    btc = close["BTCUSDT"]
    btc_beta, btc_trend_series, _ = bt.btc_last_drop_beta(btc)
    beta_budget = btc_beta.clip(upper=1.0).to_numpy(float)
    btc_trend = btc_trend_series.to_numpy(float)

    own = alpha.trend_matrix(close)
    relative = alpha.trend_matrix(close.div(btc, axis=0))
    volatility = alpha.rv30_matrix(close)
    rank = (0.50 * own + 0.50 * relative) / volatility.replace(0.0, np.nan)
    full_history = close.notna().rolling(alpha.MIN_DAYS, min_periods=alpha.MIN_DAYS).sum() >= alpha.MIN_DAYS
    eligible = (
        full_history
        & (qvol >= alpha.QVOL_FLOOR)
        & (own > 0)
        & (relative > 0)
        & rank.notna()
    )
    eligible["BTCUSDT"] = False

    eligible_array = eligible.to_numpy(bool)
    rank_array = rank.to_numpy(float)
    target_0018, selected_0018, force_0018, events = build_entry_rank_eligibility_exit_target(
        btc_idx,
        beta_budget,
        btc_trend,
        eligible_array,
        rank_array,
        slots=2,
    )

    target_0016 = alpha.build_dynamic_target(
        btc_idx,
        beta_budget,
        btc_trend,
        eligible_array,
        rank_array,
        top_n=2,
    )
    btc_dynamic = np.zeros_like(target_0018)
    btc_dynamic[:, btc_idx] = np.nan_to_num(beta_budget, nan=0.0)
    fixed_v1 = alpha.fixed_v1_target(close, columns)

    evaluation_index = close.index[(close.index >= EVAL_START) & (close.index <= EVAL_END)]
    result_0018 = evaluate_stateful(close, target_0018, force_0018, evaluation_index)
    evaluated = {
        "PIT_ALPHA_0018_ELIGIBILITY_EXIT": result_0018,
        "PIT_ALPHA_0016_DAILY_TOP2": alpha.evaluate_array(close, target_0016, evaluation_index),
        "BTC_DYNAMIC_GROSS_1_0": alpha.evaluate_array(close, btc_dynamic, evaluation_index),
        "FIXED_V1_GROSS_1_0": alpha.evaluate_array(close, fixed_v1, evaluation_index),
    }

    placebo_rows = []
    for seed in alpha.PLACEBO_SEEDS:
        priority = alpha.deterministic_priority(columns, seed)
        target, _, force, _ = build_entry_rank_eligibility_exit_target(
            btc_idx,
            beta_budget,
            btc_trend,
            eligible_array,
            rank_array,
            slots=2,
            fixed_priority=priority,
        )
        result = evaluate_stateful(close, target, force, evaluation_index)
        placebo_rows.append({"seed": seed, **alpha.metrics(result)})
    placebo = pd.DataFrame(placebo_rows)

    cost_stress = {}
    for cost in [5.0, 10.0, 20.0]:
        result = evaluate_stateful(
            close, target_0018, force_0018, evaluation_index, cost_bps=cost
        )
        cost_stress[str(int(cost))] = alpha.metrics(result)

    exchange_info = requests.get(f"{DATA_API}/api/v3/exchangeInfo", timeout=45).json()
    status_map = {
        item["symbol"]: item.get("status") for item in exchange_info.get("symbols", [])
    }

    held_0018 = exact_held_frame(result_0018, evaluation_index, columns)
    asset_returns = close.reindex(evaluation_index).pct_change(fill_method=None).fillna(0.0)
    spells = audit.holding_spells(held_0018, asset_returns)
    turnover = audit.turnover_decomposition(held_0018)
    contribution_rows, contribution_summary = contribution_report(
        result_0018, columns, status_map, eligible, evaluation_index
    )

    primary_metrics = alpha.metrics(result_0018)
    metrics_report = {name: alpha.metrics(result) for name, result in evaluated.items()}
    annual_report = {name: alpha.annual_returns(result["return"]) for name, result in evaluated.items()}
    subperiod_report = {name: alpha.subperiod_metrics(result) for name, result in evaluated.items()}
    btc_daily = close["BTCUSDT"].pct_change(fill_method=None).reindex(evaluation_index).fillna(0.0)
    capture_report = {name: alpha.monthly_capture(result["return"], btc_daily) for name, result in evaluated.items()}

    turnover_summary = {
        "total_turnover": float(turnover["total_turnover"].sum()),
        "btc_weight_turnover": float(turnover["btc_weight_turnover"].sum()),
        "alt_sleeve_size_turnover": float(turnover["alt_sleeve_size_turnover"].sum()),
        "within_alt_name_switch_turnover": float(turnover["within_alt_name_switch_turnover"].sum()),
        "btc_turnover_share": float(turnover["btc_weight_turnover"].sum() / turnover["total_turnover"].sum()),
        "alt_sleeve_size_share": float(turnover["alt_sleeve_size_turnover"].sum() / turnover["total_turnover"].sum()),
        "name_switch_share": float(turnover["within_alt_name_switch_turnover"].sum() / turnover["total_turnover"].sum()),
        "total_transaction_cost_at_5bps": float(turnover["total_cost"].sum()),
    }

    selected_frame = pd.DataFrame(selected_0018, index=close.index, columns=columns).loc[evaluation_index]
    event_frame = events.copy()
    if not event_frame.empty:
        event_frame["signal_date"] = [str(close.index[int(row)].date()) for row in event_frame["row"]]
        event_frame["symbol"] = [
            columns[int(value)] if pd.notna(value) else None for value in event_frame["asset_index"]
        ]

    report = {
        "experiment_id": EXPERIMENT_ID,
        "data": {
            "candidate_symbols": len(symbols),
            "symbols_with_rows": int(close.notna().any().sum()),
            "fetch_error_count": len(errors),
            "api_calls": api_calls,
            "evaluation_start": str(evaluation_index.min().date()),
            "evaluation_end": str(evaluation_index.max().date()),
            "evaluation_days": int(len(evaluation_index)),
            "inactive_or_nontrading_symbols_ever_eligible": int(sum(
                (status_map.get(symbol) != "TRADING")
                and bool(eligible[symbol].loc[evaluation_index].any())
                for symbol in columns
            )),
        },
        "methodology": {
            "entry": "validated current Top-2 rank fills vacancies only",
            "exit": "own/relative/history/liquidity/rank eligibility loss or BTC risk-off",
            "falling_out_of_top2_is_exit": False,
            "portfolio": "unchanged 50% BTC core / 50% alt sleeve; 35% single-alt cap; gross<=1",
            "band": alpha.BAND,
            "mandatory_rebalance": "selected-name set or BTC risk regime changes",
            "cost_bps": alpha.COST_BPS,
            "lookahead": "none; completed t target held over t+1",
        },
        "metrics": metrics_report,
        "capture": capture_report,
        "annual_returns": annual_report,
        "subperiods": subperiod_report,
        "cost_stress": cost_stress,
        "turnover_decomposition": turnover_summary,
        "holding_spells": holding_summary(spells),
        "contribution": contribution_summary,
        "placebo": {
            "seeds": int(len(placebo)),
            "primary_final_10k": primary_metrics["final_10k"],
            "primary_calmar": primary_metrics["calmar"],
            "final_10k_percentile": float((placebo["final_10k"] < primary_metrics["final_10k"]).mean()),
            "calmar_percentile": float((placebo["calmar"] < primary_metrics["calmar"]).mean()),
            "summary": placebo.drop(columns=["seed"]).quantile([0.05, 0.50, 0.95]).to_dict(),
        },
        "state_machine": {
            "entry_events": int((event_frame["event"] == "entry").sum()) if not event_frame.empty else 0,
            "exit_events": int((event_frame["event"] == "exit").sum()) if not event_frame.empty else 0,
            "risk_on_events": int((event_frame["event"] == "risk_on").sum()) if not event_frame.empty else 0,
            "risk_off_events": int((event_frame["event"] == "risk_off").sum()) if not event_frame.empty else 0,
            "mean_selected_alts": float(selected_frame.sum(axis=1).mean()),
            "days_with_two_alts_fraction": float((selected_frame.sum(axis=1) == 2).mean()),
        },
        "decision_rule": "No parameter changes after this first valid report. Promotion requires lower turnover and longer holding, same-state-machine placebo edge, improved drawdown/cost robustness, non-negative 2025+ economics and no single-winner dependency.",
    }

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "pit_alpha_0018_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    placebo.to_csv(OUTPUT / "placebo_metrics.csv", index=False, float_format="%.10f")
    contribution_rows.to_csv(OUTPUT / "asset_contribution.csv", index=False, float_format="%.10f")
    spells.to_csv(OUTPUT / "holding_spells.csv", index=False, float_format="%.10f")
    turnover.to_csv(OUTPUT / "daily_turnover_decomposition.csv", float_format="%.10f")
    event_frame.to_csv(OUTPUT / "state_machine_events.csv", index=False)

    daily_equity = pd.DataFrame({
        name: 10_000.0 * (1.0 + result["return"]).cumprod()
        for name, result in evaluated.items()
    })
    daily_equity.index.name = "date"
    daily_equity.to_csv(OUTPUT / "daily_equity.csv", float_format="%.10f")

    alpha.long_form_weights(
        evaluation_index,
        columns,
        {"PIT_ALPHA_0018_ELIGIBILITY_EXIT": result_0018},
    ).to_csv(OUTPUT / "daily_held_weights_long.csv", index=False, float_format="%.10f")

    selected_long = selected_frame.stack()
    selected_long = selected_long[selected_long].reset_index()
    selected_long.columns = ["date", "symbol", "selected"]
    selected_long.to_csv(OUTPUT / "daily_selected_names.csv", index=False)
    write_svg(daily_equity, OUTPUT / "pnl_daily.svg")

    print("=== PIT_ALPHA_0018_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
