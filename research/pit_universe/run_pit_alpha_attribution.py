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
ROOT = RESEARCH.parent
RESULTS = RESEARCH / "results" / "pit_alpha_0016"
OUTPUT = HERE / "audit_0017_outputs"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(RESEARCH))

import run_dynamic_alpha as alpha
from pit_universe.run_archive_discovery import DATA_API, archive_symbols
from pit_universe.run_dynamic_dispersion import load_panel

AUDIT_ID = "AUDIT-0017-PIT-ALPHA-ATTRIBUTION"
STRATEGY = "PIT_ALPHA_TOP2_PRIMARY"
EVAL_START = pd.Timestamp("2021-05-01")
EVAL_END = pd.Timestamp("2026-08-02")
THRESHOLD = 1e-12
HORIZONS = (1, 3, 7, 14, 30)
FIXED_ALTS = ("ETHUSDT", "SOLUSDT", "BNBUSDT")
COST_RATE = 5.0 / 10_000.0


def safe_float(value):
    if value is None or not np.isfinite(value):
        return None
    return float(value)


def set_churn(mask: pd.DataFrame) -> pd.DataFrame:
    arr = mask.to_numpy(bool)
    previous = np.vstack([np.zeros((1, arr.shape[1]), dtype=bool), arr[:-1]])
    intersection = (arr & previous).sum(axis=1)
    union = (arr | previous).sum(axis=1)
    additions = (arr & ~previous).sum(axis=1)
    removals = (~arr & previous).sum(axis=1)
    jaccard = np.divide(intersection, union, out=np.ones(len(arr), dtype=float), where=union > 0)
    return pd.DataFrame({
        "jaccard": jaccard,
        "additions": additions,
        "removals": removals,
        "set_size": arr.sum(axis=1),
    }, index=mask.index)


def monthly_set_similarity(mask: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for period, group in mask.groupby(mask.index.to_period("M")):
        first = group.iloc[0].to_numpy(bool)
        last = group.iloc[-1].to_numpy(bool)
        union = int((first | last).sum())
        intersection = int((first & last).sum())
        rows.append({
            "month": str(period),
            "first_size": int(first.sum()),
            "last_size": int(last.sum()),
            "jaccard_first_last": intersection / union if union else 1.0,
            "additions": int((last & ~first).sum()),
            "removals": int((~last & first).sum()),
        })
    return pd.DataFrame(rows)


def holding_spells(held: pd.DataFrame, returns: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for symbol in held.columns:
        if symbol == "BTCUSDT":
            continue
        active = held[symbol].abs() > THRESHOLD
        starts = active & ~active.shift(1, fill_value=False)
        ends = active & ~active.shift(-1, fill_value=False)
        start_dates = list(active.index[starts])
        end_dates = list(active.index[ends])
        for spell_number, (start, end) in enumerate(zip(start_dates, end_dates), start=1):
            idx = held.loc[start:end].index
            weights = held.loc[idx, symbol]
            asset_returns = returns.loc[idx, symbol].fillna(0.0)
            contribution = weights * asset_returns
            rows.append({
                "symbol": symbol,
                "spell_number": spell_number,
                "start": str(start.date()),
                "end": str(end.date()),
                "duration_days": int(len(idx)),
                "mean_weight": float(weights.mean()),
                "max_weight": float(weights.max()),
                "arithmetic_gross_contribution": float(contribution.sum()),
                "asset_compound_return_during_spell": float((1.0 + asset_returns).prod() - 1.0),
                "positive_contribution": bool(contribution.sum() > 0),
            })
    return pd.DataFrame(rows)


def turnover_decomposition(held: pd.DataFrame) -> pd.DataFrame:
    previous = held.shift(1).fillna(0.0)
    delta = held - previous
    btc_turnover = delta.get("BTCUSDT", pd.Series(0.0, index=held.index)).abs()
    alt_columns = [column for column in held.columns if column != "BTCUSDT"]
    alt_l1 = delta[alt_columns].abs().sum(axis=1)
    alt_total_change = (held[alt_columns].sum(axis=1) - previous[alt_columns].sum(axis=1)).abs()
    name_switch = (alt_l1 - alt_total_change).clip(lower=0.0)
    total = btc_turnover + alt_l1
    return pd.DataFrame({
        "btc_weight_turnover": btc_turnover,
        "alt_sleeve_size_turnover": alt_total_change,
        "within_alt_name_switch_turnover": name_switch,
        "alt_total_turnover": alt_l1,
        "total_turnover": total,
        "btc_cost": btc_turnover * COST_RATE,
        "alt_sleeve_size_cost": alt_total_change * COST_RATE,
        "name_switch_cost": name_switch * COST_RATE,
        "total_cost": total * COST_RATE,
    }, index=held.index)


def drawdown_episodes(net_returns: pd.Series, gross_returns: pd.Series, costs: pd.Series, contributions: pd.DataFrame) -> pd.DataFrame:
    nav = (1.0 + net_returns).cumprod()
    peak = nav.cummax()
    underwater = nav < peak - 1e-12
    rows = []
    start = None
    for i, date in enumerate(nav.index):
        if underwater.iloc[i] and start is None:
            start = date
        is_last = i == len(nav) - 1
        recovered = start is not None and (not underwater.iloc[i] or is_last)
        if recovered:
            end = date if not underwater.iloc[i] else nav.index[-1]
            segment = nav.loc[start:end]
            trough = segment.idxmin()
            prior_dates = nav.index[nav.index < start]
            peak_date = prior_dates[-1] if len(prior_dates) else nav.index[0]
            idx = nav.loc[start:end].index
            asset_sum = contributions.loc[idx].sum().sort_values()
            rows.append({
                "peak_date": str(peak_date.date()),
                "start": str(start.date()),
                "trough": str(trough.date()),
                "end_or_last": str(end.date()),
                "max_drawdown": float(nav.loc[trough] / peak.loc[trough] - 1.0),
                "calendar_days_to_trough": int((trough - start).days + 1),
                "episode_net_compound_return": float((1.0 + net_returns.loc[idx]).prod() - 1.0),
                "episode_gross_additive_return": float(gross_returns.loc[idx].sum()),
                "episode_cost": float(costs.loc[idx].sum()),
                "worst_asset": asset_sum.index[0] if len(asset_sum) else None,
                "worst_asset_contribution": float(asset_sum.iloc[0]) if len(asset_sum) else None,
            })
            start = None
    frame = pd.DataFrame(rows)
    return frame.sort_values("max_drawdown").reset_index(drop=True) if not frame.empty else frame


def entry_rank_table(
    held: pd.DataFrame,
    close: pd.DataFrame,
    qvol: pd.DataFrame,
    eligible: pd.DataFrame,
    rank_score: pd.DataFrame,
    rank_position: pd.DataFrame,
    status_map: dict[str, str],
) -> pd.DataFrame:
    rows = []
    index = held.index
    close_first = {symbol: close[symbol].first_valid_index() for symbol in close.columns}
    for symbol in held.columns:
        if symbol == "BTCUSDT":
            continue
        active = held[symbol].abs() > THRESHOLD
        entries = active & ~active.shift(1, fill_value=False)
        for entry_date in index[entries]:
            entry_pos = index.get_loc(entry_date)
            if entry_pos == 0:
                continue
            signal_date = index[entry_pos - 1]
            first = close_first.get(symbol)
            row = {
                "symbol": symbol,
                "entry_date": str(entry_date.date()),
                "signal_date": str(signal_date.date()),
                "entry_weight": float(held.loc[entry_date, symbol]),
                "entry_rank_position": safe_float(rank_position.loc[signal_date, symbol]),
                "entry_rank_score": safe_float(rank_score.loc[signal_date, symbol]),
                "entry_quote_volume": safe_float(qvol.loc[signal_date, symbol]),
                "listing_age_days": int((signal_date - first).days + 1) if first is not None else None,
                "current_status": status_map.get(symbol, "MISSING"),
            }
            signal_pos = index.get_loc(signal_date)
            base_price = close.loc[signal_date, symbol]
            base_score = rank_score.loc[signal_date, symbol]
            for horizon in HORIZONS:
                future_pos = signal_pos + horizon
                if future_pos >= len(index):
                    row[f"eligible_h{horizon}"] = None
                    row[f"top2_h{horizon}"] = None
                    row[f"score_change_h{horizon}"] = None
                    row[f"forward_return_h{horizon}"] = None
                    continue
                future = index[future_pos]
                future_score = rank_score.loc[future, symbol]
                future_price = close.loc[future, symbol]
                row[f"eligible_h{horizon}"] = bool(eligible.loc[future, symbol])
                position = rank_position.loc[future, symbol]
                row[f"top2_h{horizon}"] = bool(np.isfinite(position) and position <= 2.0)
                row[f"score_change_h{horizon}"] = safe_float(future_score - base_score)
                row[f"forward_return_h{horizon}"] = safe_float(future_price / base_price - 1.0) if pd.notna(base_price) and pd.notna(future_price) else None
            rows.append(row)
    return pd.DataFrame(rows)


def cohort_label(value: float, boundaries: tuple[float, ...], labels: tuple[str, ...]) -> str:
    for boundary, label in zip(boundaries, labels):
        if value < boundary:
            return label
    return labels[-1]


def year_summary(
    net_returns: pd.Series,
    gross_returns: pd.Series,
    turnover: pd.DataFrame,
    eligible_churn: pd.DataFrame,
    held_churn: pd.DataFrame,
    spells: pd.DataFrame,
    contributions: pd.DataFrame,
    overlap: pd.Series,
) -> pd.DataFrame:
    rows = []
    for year in sorted(set(net_returns.index.year)):
        idx = net_returns.index[net_returns.index.year == year]
        spell_year = spells[pd.to_datetime(spells["start"]).dt.year == year] if not spells.empty else spells
        contrib = contributions.loc[idx].sum().sort_values(ascending=False)
        rows.append({
            "year": int(year),
            "net_compound_return": float((1.0 + net_returns.loc[idx]).prod() - 1.0),
            "gross_additive_return": float(gross_returns.loc[idx].sum()),
            "transaction_cost": float(turnover.loc[idx, "total_cost"].sum()),
            "total_turnover": float(turnover.loc[idx, "total_turnover"].sum()),
            "btc_turnover": float(turnover.loc[idx, "btc_weight_turnover"].sum()),
            "alt_sleeve_size_turnover": float(turnover.loc[idx, "alt_sleeve_size_turnover"].sum()),
            "name_switch_turnover": float(turnover.loc[idx, "within_alt_name_switch_turnover"].sum()),
            "mean_eligible_jaccard": float(eligible_churn.loc[idx, "jaccard"].mean()),
            "mean_held_jaccard": float(held_churn.loc[idx, "jaccard"].mean()),
            "new_holding_spells": int(len(spell_year)),
            "median_holding_days": safe_float(spell_year["duration_days"].median()) if len(spell_year) else None,
            "fixed_v1_overlap_day_fraction": float(overlap.loc[idx].mean()),
            "top_contributor": contrib.index[0] if len(contrib) else None,
            "top_contribution": float(contrib.iloc[0]) if len(contrib) else None,
            "bottom_contributor": contrib.index[-1] if len(contrib) else None,
            "bottom_contribution": float(contrib.iloc[-1]) if len(contrib) else None,
        })
    return pd.DataFrame(rows)


def quantile_dict(series: pd.Series) -> dict:
    clean = series.dropna()
    if clean.empty:
        return {}
    return {
        "count": int(len(clean)),
        "mean": float(clean.mean()),
        "median": float(clean.median()),
        "p05": float(clean.quantile(0.05)),
        "p25": float(clean.quantile(0.25)),
        "p75": float(clean.quantile(0.75)),
        "p95": float(clean.quantile(0.95)),
        "p99": float(clean.quantile(0.99)),
        "max": float(clean.max()),
    }


def main() -> None:
    equity = pd.read_csv(RESULTS / "daily_equity.csv", parse_dates=["date"]).set_index("date")
    weights_long = pd.read_csv(RESULTS / "daily_held_weights_long.csv", parse_dates=["date"])
    weights_long = weights_long[weights_long["strategy"] == STRATEGY].copy()
    evaluation_index = equity.index[(equity.index >= EVAL_START) & (equity.index <= EVAL_END)]

    symbols = sorted(symbol for symbol in archive_symbols() if alpha.alpha_symbol(symbol))
    close, qvol, errors, api_calls = load_panel(symbols)
    close = close.sort_index().sort_index(axis=1).loc[:EVAL_END]
    qvol = qvol.reindex(index=close.index, columns=close.columns)
    if errors:
        raise RuntimeError(f"Audit data fetch errors: {len(errors)}")

    columns = list(close.columns)
    held = weights_long.pivot_table(index="date", columns="symbol", values="weight", aggfunc="last")
    held = held.reindex(index=evaluation_index, columns=columns, fill_value=0.0).fillna(0.0)
    close_eval = close.reindex(index=evaluation_index, columns=columns)
    qvol_eval = qvol.reindex(index=evaluation_index, columns=columns)
    returns = close_eval.pct_change(fill_method=None).fillna(0.0)

    own = alpha.trend_matrix(close).reindex(evaluation_index)
    btc = close["BTCUSDT"]
    relative = alpha.trend_matrix(close.div(btc, axis=0)).reindex(evaluation_index)
    volatility = alpha.rv30_matrix(close).reindex(evaluation_index)
    rank_score = (0.5 * own + 0.5 * relative) / volatility.replace(0.0, np.nan)
    full_history = close.notna().rolling(alpha.MIN_DAYS, min_periods=alpha.MIN_DAYS).sum() >= alpha.MIN_DAYS
    eligible = (
        full_history.reindex(evaluation_index)
        & (qvol_eval >= alpha.QVOL_FLOOR)
        & (own > 0)
        & (relative > 0)
        & rank_score.notna()
    )
    eligible["BTCUSDT"] = False
    rank_position = rank_score.where(eligible).rank(axis=1, ascending=False, method="min")

    exchange_info = requests.get(f"{DATA_API}/api/v3/exchangeInfo", timeout=45).json()
    status_map = {item["symbol"]: item.get("status") for item in exchange_info.get("symbols", [])}

    held_alt_mask = held.drop(columns=["BTCUSDT"], errors="ignore").abs() > THRESHOLD
    eligible_churn = set_churn(eligible.drop(columns=["BTCUSDT"], errors="ignore"))
    held_churn = set_churn(held_alt_mask)
    monthly_eligible = monthly_set_similarity(eligible.drop(columns=["BTCUSDT"], errors="ignore"))
    monthly_held = monthly_set_similarity(held_alt_mask)

    spells = holding_spells(held, returns)
    turnover = turnover_decomposition(held)
    contributions = held * returns
    gross_returns = contributions.sum(axis=1)
    net_returns = equity[STRATEGY].pct_change(fill_method=None).fillna(equity[STRATEGY].iloc[0] / 10_000.0 - 1.0)

    fixed_target = alpha.fixed_v1_target(close, columns)
    fixed_banded = alpha.apply_band_with_forced_exit(fixed_target, close.notna().to_numpy(bool), alpha.BAND)
    fixed_held_full = np.vstack([np.zeros((1, fixed_banded.shape[1])), fixed_banded[:-1]])
    locations = close.index.get_indexer(evaluation_index)
    fixed_held = pd.DataFrame(fixed_held_full[locations], index=evaluation_index, columns=columns)
    fixed_active = fixed_held[list(FIXED_ALTS)].abs() > THRESHOLD
    pit_fixed_exposure = pd.Series(0.0, index=evaluation_index)
    for symbol in FIXED_ALTS:
        if symbol in held.columns:
            pit_fixed_exposure += held[symbol].where(fixed_active[symbol], 0.0)
    pit_alt_exposure = held.drop(columns=["BTCUSDT"], errors="ignore").sum(axis=1)
    overlap_exposure_fraction = (pit_fixed_exposure / pit_alt_exposure.replace(0.0, np.nan)).fillna(0.0)
    overlap_day = pit_fixed_exposure > THRESHOLD

    entries = entry_rank_table(held, close_eval, qvol_eval, eligible, rank_score, rank_position, status_map)
    if not entries.empty:
        entries["listing_age_cohort"] = entries["listing_age_days"].apply(
            lambda value: cohort_label(value, (365, 730, 1460), ("240-364d", "365-729d", "730-1459d", "1460d+"))
        )
        entries["quote_volume_cohort"] = entries["entry_quote_volume"].apply(
            lambda value: cohort_label(value, (100e6, 500e6, 2e9), ("25-100m", "100-500m", "500m-2b", "2b+"))
        )

    drawdowns = drawdown_episodes(net_returns, gross_returns, turnover["total_cost"], contributions)
    worst_days = pd.DataFrame({
        "net_return": net_returns,
        "gross_return": gross_returns,
        "transaction_cost": turnover["total_cost"],
        "turnover": turnover["total_turnover"],
    }).nsmallest(25, "net_return")
    worst_asset = []
    worst_asset_contribution = []
    for date in worst_days.index:
        row = contributions.loc[date].sort_values()
        worst_asset.append(row.index[0])
        worst_asset_contribution.append(float(row.iloc[0]))
    worst_days["worst_asset"] = worst_asset
    worst_days["worst_asset_contribution"] = worst_asset_contribution
    worst_days = worst_days.reset_index().rename(columns={"date": "date"})
    worst_days["date"] = worst_days["date"].dt.strftime("%Y-%m-%d")

    yearly = year_summary(net_returns, gross_returns, turnover, eligible_churn, held_churn, spells, contributions, overlap_day)

    capacity_rows = []
    signal_qvol = qvol_eval.shift(1)
    for nav in (100_000.0, 1_000_000.0):
        participation = held.drop(columns=["BTCUSDT"], errors="ignore").abs() * nav / signal_qvol.drop(columns=["BTCUSDT"], errors="ignore")
        stacked = participation.where(held.drop(columns=["BTCUSDT"], errors="ignore").abs() > THRESHOLD).stack()
        stats = quantile_dict(stacked)
        stats["hypothetical_nav"] = nav
        capacity_rows.append(stats)
    capacity = pd.DataFrame(capacity_rows)

    rank_persistence = {}
    for horizon in HORIZONS:
        eligible_col = entries[f"eligible_h{horizon}"].dropna() if not entries.empty else pd.Series(dtype=float)
        top2_col = entries[f"top2_h{horizon}"].dropna() if not entries.empty else pd.Series(dtype=float)
        score_col = entries[f"score_change_h{horizon}"].dropna() if not entries.empty else pd.Series(dtype=float)
        return_col = entries[f"forward_return_h{horizon}"].dropna() if not entries.empty else pd.Series(dtype=float)
        rank_persistence[str(horizon)] = {
            "entries_with_observation": int(len(eligible_col)),
            "remain_eligible_probability": safe_float(eligible_col.astype(float).mean()) if len(eligible_col) else None,
            "remain_top2_probability": safe_float(top2_col.astype(float).mean()) if len(top2_col) else None,
            "mean_score_change": safe_float(score_col.mean()) if len(score_col) else None,
            "median_forward_return": safe_float(return_col.median()) if len(return_col) else None,
            "mean_forward_return": safe_float(return_col.mean()) if len(return_col) else None,
        }

    spell_stats = {
        "spell_count": int(len(spells)),
        "symbols_held": int(spells["symbol"].nunique()) if not spells.empty else 0,
        "duration": quantile_dict(spells["duration_days"]) if not spells.empty else {},
        "positive_contribution_fraction": safe_float(spells["positive_contribution"].mean()) if not spells.empty else None,
        "median_reentries_per_symbol": safe_float(spells.groupby("symbol").size().median()) if not spells.empty else None,
        "max_reentries_symbol": spells.groupby("symbol").size().idxmax() if not spells.empty else None,
        "max_reentries": int(spells.groupby("symbol").size().max()) if not spells.empty else 0,
    }

    overlap_summary = {
        "mean_fraction_of_pit_alt_exposure_in_active_fixed_v1_alts": float(overlap_exposure_fraction.mean()),
        "days_with_any_overlap_fraction": float(overlap_day.mean()),
        "mean_net_return_overlap_days": float(net_returns[overlap_day].mean()) if overlap_day.any() else None,
        "mean_net_return_nonoverlap_days": float(net_returns[~overlap_day].mean()) if (~overlap_day).any() else None,
        "compound_return_overlap_days": float((1.0 + net_returns[overlap_day]).prod() - 1.0) if overlap_day.any() else None,
        "compound_return_nonoverlap_days": float((1.0 + net_returns[~overlap_day]).prod() - 1.0) if (~overlap_day).any() else None,
    }

    turnover_summary = {
        "total_turnover": float(turnover["total_turnover"].sum()),
        "btc_weight_turnover": float(turnover["btc_weight_turnover"].sum()),
        "alt_sleeve_size_turnover": float(turnover["alt_sleeve_size_turnover"].sum()),
        "within_alt_name_switch_turnover": float(turnover["within_alt_name_switch_turnover"].sum()),
        "btc_turnover_share": float(turnover["btc_weight_turnover"].sum() / turnover["total_turnover"].sum()),
        "alt_sleeve_size_share": float(turnover["alt_sleeve_size_turnover"].sum() / turnover["total_turnover"].sum()),
        "name_switch_share": float(turnover["within_alt_name_switch_turnover"].sum() / turnover["total_turnover"].sum()),
        "total_transaction_cost": float(turnover["total_cost"].sum()),
    }

    report = {
        "audit_id": AUDIT_ID,
        "trading_changes": False,
        "data": {
            "candidate_symbols": len(symbols),
            "symbols_with_rows": int(close.notna().any().sum()),
            "api_calls": api_calls,
            "fetch_errors": len(errors),
            "evaluation_start": str(evaluation_index.min().date()),
            "evaluation_end": str(evaluation_index.max().date()),
            "evaluation_days": len(evaluation_index),
        },
        "eligible_universe_churn": {
            "daily_jaccard": quantile_dict(eligible_churn["jaccard"]),
            "mean_daily_additions": float(eligible_churn["additions"].mean()),
            "mean_daily_removals": float(eligible_churn["removals"].mean()),
            "monthly_first_last_jaccard": quantile_dict(monthly_eligible["jaccard_first_last"]),
        },
        "held_name_churn": {
            "daily_jaccard": quantile_dict(held_churn["jaccard"]),
            "mean_daily_additions": float(held_churn["additions"].mean()),
            "mean_daily_removals": float(held_churn["removals"].mean()),
            "monthly_first_last_jaccard": quantile_dict(monthly_held["jaccard_first_last"]),
            "holding_spells": spell_stats,
        },
        "turnover_decomposition": turnover_summary,
        "rank_persistence": rank_persistence,
        "fixed_v1_overlap": overlap_summary,
        "tail_loss": {
            "worst_10_days": worst_days.head(10).to_dict(orient="records"),
            "top_5_drawdown_episodes": drawdowns.head(5).to_dict(orient="records") if not drawdowns.empty else [],
        },
        "year_summary": yearly.to_dict(orient="records"),
        "capacity_proxy": capacity.to_dict(orient="records"),
        "entry_cohorts": {
            "listing_age": entries.groupby("listing_age_cohort").agg(
                entries=("symbol", "size"),
                median_forward_30d=("forward_return_h30", "median"),
                mean_forward_30d=("forward_return_h30", "mean"),
                remain_top2_7d=("top2_h7", "mean"),
            ).reset_index().to_dict(orient="records") if not entries.empty else [],
            "quote_volume": entries.groupby("quote_volume_cohort").agg(
                entries=("symbol", "size"),
                median_forward_30d=("forward_return_h30", "median"),
                mean_forward_30d=("forward_return_h30", "mean"),
                remain_top2_7d=("top2_h7", "mean"),
            ).reset_index().to_dict(orient="records") if not entries.empty else [],
            "current_status": entries.groupby("current_status").agg(
                entries=("symbol", "size"),
                median_forward_30d=("forward_return_h30", "median"),
                mean_forward_30d=("forward_return_h30", "mean"),
                remain_top2_7d=("top2_h7", "mean"),
            ).reset_index().to_dict(orient="records") if not entries.empty else [],
        },
        "interpretation_rule": "No target or parameter changes. Use attribution to choose at most one causal hypothesis for a separately preregistered future experiment.",
    }

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "audit_0017_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    eligible_churn.to_csv(OUTPUT / "daily_eligible_churn.csv", float_format="%.10f")
    held_churn.to_csv(OUTPUT / "daily_held_churn.csv", float_format="%.10f")
    monthly_eligible.to_csv(OUTPUT / "monthly_eligible_similarity.csv", index=False, float_format="%.10f")
    monthly_held.to_csv(OUTPUT / "monthly_held_similarity.csv", index=False, float_format="%.10f")
    turnover.to_csv(OUTPUT / "daily_turnover_decomposition.csv", float_format="%.10f")
    spells.to_csv(OUTPUT / "holding_spells.csv", index=False, float_format="%.10f")
    entries.to_csv(OUTPUT / "entry_rank_persistence.csv", index=False, float_format="%.10f")
    worst_days.to_csv(OUTPUT / "worst_days.csv", index=False, float_format="%.10f")
    drawdowns.to_csv(OUTPUT / "drawdown_episodes.csv", index=False, float_format="%.10f")
    yearly.to_csv(OUTPUT / "year_summary.csv", index=False, float_format="%.10f")
    capacity.to_csv(OUTPUT / "capacity_proxy.csv", index=False, float_format="%.10f")

    print("=== AUDIT_0017_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
