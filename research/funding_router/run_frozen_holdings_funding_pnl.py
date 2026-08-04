from __future__ import annotations

import json
import math
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
ROOT = RESEARCH.parent
for path in (HERE, RESEARCH):
    sys.path.insert(0, str(path))

from run_funding_data_audit import parse_timestamp, parse_zip, symbol_months

EXPERIMENT_ID = "FUNDING-PNL-0003-FROZEN-HOLDINGS"
ASSETS = ("BTC", "ETH", "SOL", "BNB", "XRP")
SYMBOLS = {asset: f"{asset}USDT" for asset in ASSETS}
WEIGHT_COLUMNS = {asset: f"BRRK0011_BASELINE__{asset}" for asset in ASSETS}
WEIGHTS_PATH = ROOT / "research/results/pit_disp_0015/daily_weights.csv"
EQUITY_PATH = ROOT / "research/results/pit_disp_0015/daily_equity.csv"
PAIRED_PATH = ROOT / "research/results/funding_crossvenue_0002/paired_8h_blocks.csv"
OUTPUT = HERE / "funding_pnl_0003_outputs"
BINANCE_START = pd.Timestamp("2022-12-10 00:00:00", tz="UTC")
BINANCE_END = pd.Timestamp("2026-07-31 23:59:59.999", tz="UTC")
COMMON_START = pd.Timestamp("2023-06-18 00:00:00", tz="UTC")
COMMON_END = BINANCE_END
MAX_WORKERS = 8
STARTING_NAV = 10_000.0


def load_strategy_inputs() -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    weights = pd.read_csv(WEIGHTS_PATH, parse_dates=["date"]).set_index("date")
    weights = weights[[WEIGHT_COLUMNS[asset] for asset in ASSETS]].rename(
        columns={WEIGHT_COLUMNS[asset]: asset for asset in ASSETS}
    )
    weights.index = pd.DatetimeIndex(weights.index).normalize()

    equity_frame = pd.read_csv(EQUITY_PATH, parse_dates=["date"]).set_index("date")
    equity = equity_frame["BRRK0011_BASELINE"].astype(float)
    equity.index = pd.DatetimeIndex(equity.index).normalize()
    price_return = equity.pct_change(fill_method=None)
    price_return.iloc[0] = equity.iloc[0] / STARTING_NAV - 1.0
    return weights.astype(float), equity, price_return.astype(float)


def load_binance_month(asset: str, row: dict) -> pd.DataFrame:
    frame, _ = parse_zip(row["key"])
    timestamp = parse_timestamp(frame["calc_time"])
    rate = pd.to_numeric(frame["last_funding_rate"], errors="coerce")
    interval = pd.to_numeric(frame.get("funding_interval_hours"), errors="coerce")
    result = pd.DataFrame({
        "asset": asset,
        "timestamp": timestamp,
        "rate": rate,
        "reported_interval_hours": interval,
    }).dropna(subset=["timestamp", "rate"])
    return result


def load_binance_full_blocks() -> tuple[pd.DataFrame, dict]:
    jobs = []
    source_coverage = {}
    start_month = pd.Period(BINANCE_START.strftime("%Y-%m"), freq="M")
    end_month = pd.Period(BINANCE_END.strftime("%Y-%m"), freq="M")
    for asset, symbol in SYMBOLS.items():
        months, objects = symbol_months(symbol)
        selected = [
            row for row in objects
            if start_month <= pd.Period(row["month"], freq="M") <= end_month
        ]
        source_coverage[asset] = {
            "symbol": symbol,
            "selected_months": len(selected),
            "first_month": selected[0]["month"] if selected else None,
            "last_month": selected[-1]["month"] if selected else None,
            "archive_months_total": len(months),
        }
        jobs.extend((asset, row) for row in selected)

    frames = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(load_binance_month, asset, row): (asset, row["month"])
            for asset, row in jobs
        }
        completed = 0
        for future in as_completed(futures):
            frames.append(future.result())
            completed += 1
            if completed % 25 == 0 or completed == len(futures):
                print(f"binance_funding_progress {completed}/{len(futures)}", flush=True)

    events = pd.concat(frames, ignore_index=True)
    events = events[(events["timestamp"] >= BINANCE_START) & (events["timestamp"] <= BINANCE_END)]
    events = events.drop_duplicates(["asset", "timestamp"], keep="last")
    events["block"] = events["timestamp"].dt.floor("8h")
    grouped = events.groupby(["asset", "block"], sort=True)
    blocks = grouped.agg(
        additive_rate=("rate", "sum"),
        event_count=("rate", "count"),
        first_event=("timestamp", "min"),
        last_event=("timestamp", "max"),
    ).reset_index()
    blocks["compounded_rate"] = grouped["rate"].apply(
        lambda values: float(np.prod(1.0 + values.to_numpy(float)) - 1.0)
    ).to_numpy()
    return blocks.sort_values(["block", "asset"]), source_coverage


def load_common_blocks() -> tuple[pd.DataFrame, pd.DataFrame]:
    paired = pd.read_csv(PAIRED_PATH, parse_dates=["block"])
    if paired["block"].dt.tz is None:
        paired["block"] = paired["block"].dt.tz_localize("UTC")
    paired = paired[(paired["block"] >= COMMON_START) & (paired["block"] <= COMMON_END)]

    binance = paired[["asset", "block", "binance_additive", "binance_compounded", "binance_event_count"]].rename(
        columns={
            "binance_additive": "additive_rate",
            "binance_compounded": "compounded_rate",
            "binance_event_count": "event_count",
        }
    )
    hyperliquid = paired[["asset", "block", "hyperliquid_additive", "hyperliquid_compounded", "hyperliquid_event_count"]].rename(
        columns={
            "hyperliquid_additive": "additive_rate",
            "hyperliquid_compounded": "compounded_rate",
            "hyperliquid_event_count": "event_count",
        }
    )
    return binance.sort_values(["block", "asset"]), hyperliquid.sort_values(["block", "asset"])


def validate_complete_blocks(blocks: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp, label: str) -> dict:
    expected_blocks = pd.date_range(start.floor("8h"), end.floor("8h"), freq="8h")
    pivot = blocks.pivot_table(index="block", columns="asset", values="additive_rate", aggfunc="sum")
    missing_assets = {
        asset: int(pivot[asset].isna().sum()) if asset in pivot else len(pivot)
        for asset in ASSETS
    }
    missing_clock_blocks = expected_blocks.difference(pivot.index)
    incomplete_rows = int(pivot[list(ASSETS)].isna().any(axis=1).sum()) if set(ASSETS).issubset(pivot.columns) else len(pivot)
    if len(missing_clock_blocks) or incomplete_rows:
        raise RuntimeError(
            f"{label} incomplete: missing clock blocks={len(missing_clock_blocks)}, "
            f"incomplete rows={incomplete_rows}, missing assets={missing_assets}"
        )
    return {
        "label": label,
        "expected_blocks": int(len(expected_blocks)),
        "observed_blocks": int(len(pivot)),
        "missing_clock_blocks": int(len(missing_clock_blocks)),
        "incomplete_asset_blocks": incomplete_rows,
        "missing_asset_cells": missing_assets,
    }


def weight_for_block(weights: pd.DataFrame, blocks: pd.Series) -> pd.DataFrame:
    dates = pd.DatetimeIndex(blocks.dt.tz_convert("UTC").dt.tz_localize(None).dt.normalize())
    missing = dates.difference(weights.index)
    if len(missing):
        raise RuntimeError(f"Funding blocks map to dates absent from held weights: {missing[:5].tolist()}")
    selected = weights.loc[dates, list(ASSETS)].copy()
    selected.index = blocks.index
    return selected


def funding_accounting(
    blocks: pd.DataFrame,
    weights: pd.DataFrame,
    rate_column: str,
    label: str,
) -> dict:
    frame = blocks[["asset", "block", rate_column]].rename(columns={rate_column: "rate"}).copy()
    wide = frame.pivot(index="block", columns="asset", values="rate").sort_index()
    if not set(ASSETS).issubset(wide.columns):
        raise RuntimeError(f"{label}: missing assets in rate matrix")
    wide = wide[list(ASSETS)]
    block_weights = weight_for_block(weights, wide.index.to_series())
    block_weights.index = wide.index

    contribution = -block_weights * wide
    block_return = contribution.sum(axis=1)
    if (1.0 + block_return <= 0).any():
        raise RuntimeError(f"{label}: impossible funding block return <= -100%")

    date_index = pd.DatetimeIndex(wide.index.tz_convert("UTC").tz_localize(None).normalize())
    daily_factor = (1.0 + block_return).groupby(date_index).prod()
    daily_additive = block_return.groupby(date_index).sum()
    asset_daily = contribution.groupby(date_index).sum()
    asset_daily.columns = list(ASSETS)

    long = contribution.stack().rename("contribution").reset_index()
    long.columns = ["block", "asset", "contribution"]
    rate_long = wide.stack().rename("rate").reset_index()
    rate_long.columns = ["block", "asset", "rate"]
    weight_long = block_weights.stack().rename("held_weight").reset_index()
    weight_long.columns = ["block", "asset", "held_weight"]
    long = long.merge(rate_long, on=["block", "asset"], validate="one_to_one")
    long = long.merge(weight_long, on=["block", "asset"], validate="one_to_one")
    long["date"] = pd.DatetimeIndex(long["block"].dt.tz_convert("UTC").dt.tz_localize(None).dt.normalize())
    long["rate_sign"] = np.select(
        [long["rate"] > 0, long["rate"] < 0],
        ["positive_long_pays", "negative_long_receives"],
        default="zero",
    )

    diagnostics = {
        "label": label,
        "block_count": int(len(wide)),
        "date_count": int(len(daily_factor)),
        "first_block": str(wide.index.min()),
        "last_block": str(wide.index.max()),
        "nonzero_exposure_blocks": int((block_weights.abs().sum(axis=1) > 0).sum()),
        "mean_gross_held_exposure_on_blocks": float(block_weights.abs().sum(axis=1).mean()),
        "minimum_block_funding_return": float(block_return.min()),
        "maximum_block_funding_return": float(block_return.max()),
        "total_additive_funding_return": float(block_return.sum()),
        "total_compounded_funding_factor": float((1.0 + block_return).prod()),
    }
    return {
        "daily_factor": daily_factor,
        "daily_additive": daily_additive,
        "asset_daily": asset_daily,
        "block_return": block_return,
        "block_detail": long,
        "diagnostics": diagnostics,
    }


def price_returns_for_window(price_return: pd.Series, start: pd.Timestamp, end: pd.Timestamp) -> pd.Series:
    start_date = start.tz_convert("UTC").tz_localize(None).normalize()
    end_date = end.tz_convert("UTC").tz_localize(None).normalize()
    result = price_return.loc[start_date:end_date].copy()
    if result.empty:
        raise RuntimeError(f"No price returns in {start_date}..{end_date}")
    return result


def combine_price_and_funding(price_return: pd.Series, funding_factor: pd.Series) -> pd.Series:
    aligned_factor = funding_factor.reindex(price_return.index)
    if aligned_factor.isna().any():
        missing = aligned_factor.index[aligned_factor.isna()]
        raise RuntimeError(f"Missing daily funding factor for {missing[:5].tolist()}")
    return (1.0 + price_return) * aligned_factor - 1.0


def metrics(returns: pd.Series) -> dict:
    returns = returns.dropna().astype(float)
    equity = (1.0 + returns).cumprod()
    elapsed_years = max((returns.index[-1] - returns.index[0]).days / 365.25, 1.0 / 365.25)
    final_multiple = float(equity.iloc[-1])
    cagr = final_multiple ** (1.0 / elapsed_years) - 1.0
    drawdown = equity / equity.cummax() - 1.0
    std = float(returns.std(ddof=1))
    ann_vol = std * math.sqrt(365.0)
    sharpe = float(returns.mean() / std * math.sqrt(365.0)) if std > 0 else None
    max_drawdown = float(drawdown.min())
    calmar = float(cagr / abs(max_drawdown)) if max_drawdown < 0 else None
    return {
        "start": str(returns.index[0].date()),
        "end": str(returns.index[-1].date()),
        "observations": int(len(returns)),
        "final_multiple": final_multiple,
        "final_10k": final_multiple * STARTING_NAV,
        "cagr": float(cagr),
        "max_drawdown": max_drawdown,
        "ann_vol": float(ann_vol),
        "sharpe": sharpe,
        "calmar": calmar,
    }


def annual_returns(returns: pd.Series) -> dict:
    return {
        str(int(year)): float((1.0 + group).prod() - 1.0)
        for year, group in returns.groupby(returns.index.year)
    }


def funding_summary(accounting: dict) -> dict:
    daily_factor = accounting["daily_factor"]
    daily_funding_return = daily_factor - 1.0
    additive = accounting["daily_additive"]
    detail = accounting["block_detail"]
    asset_total = detail.groupby("asset")["contribution"].sum().to_dict()
    asset_year = (
        detail.groupby(["asset", detail["date"].dt.year])["contribution"]
        .sum().rename_axis(["asset", "year"]).reset_index()
    )
    sign_total = detail.groupby("rate_sign")["contribution"].sum().to_dict()
    return {
        "diagnostics": accounting["diagnostics"],
        "total_compounded_funding_return": float(daily_factor.prod() - 1.0),
        "total_additive_funding_return": float(additive.sum()),
        "annual_compounded_funding_returns": annual_returns(daily_funding_return),
        "annual_additive_funding_returns": {
            str(int(year)): float(group.sum())
            for year, group in additive.groupby(additive.index.year)
        },
        "asset_additive_contribution": {asset: float(asset_total.get(asset, 0.0)) for asset in ASSETS},
        "asset_year_additive_contribution": asset_year.to_dict(orient="records"),
        "rate_sign_additive_contribution": {key: float(value) for key, value in sign_total.items()},
    }


def write_svg(equity: pd.DataFrame, path: Path) -> None:
    width, height = 1200, 650
    left, right, top, bottom = 105, 35, 75, 90
    plot_w, plot_h = width - left - right, height - top - bottom
    low = 0.0
    high = float(equity.max().max()) * 1.05
    colors = ["#111111", "#B13B2E", "#2457A7"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111}.grid{stroke:#dedede}.axis{stroke:#555;stroke-width:1.2}</style>',
        '<text x="105" y="30" font-size="22" font-weight="700">FUNDING-PNL-0003 exact daily NAV</text>',
        f'<text x="105" y="52" font-size="12">Frozen BRRK-0011 holdings · {equity.index[0].date()} to {equity.index[-1].date()} · event/block funding attribution</text>',
    ]
    for tick in np.linspace(low, high, 6):
        y = top + plot_h * (high - tick) / max(high - low, 1e-12)
        parts.append(f'<line class="grid" x1="{left}" y1="{y:.2f}" x2="{left + plot_w}" y2="{y:.2f}"/>')
        parts.append(f'<text x="{left - 12}" y="{y + 4:.2f}" font-size="11" text-anchor="end">${tick:,.0f}</text>')
    for year in sorted(set(equity.index.year)):
        loc = np.flatnonzero(equity.index.year == year)
        if len(loc):
            x = left + plot_w * loc[0] / max(len(equity) - 1, 1)
            parts.append(f'<line class="grid" x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{top + plot_h}"/>')
            parts.append(f'<text x="{x:.2f}" y="{top + plot_h + 24}" font-size="11" text-anchor="middle">{year}</text>')
    parts.append(f'<line class="axis" x1="{left}" y1="{top}" x2="{left}" y2="{top + plot_h}"/>')
    parts.append(f'<line class="axis" x1="{left}" y1="{top + plot_h}" x2="{left + plot_w}" y2="{top + plot_h}"/>')
    for position, name in enumerate(equity.columns):
        values = equity[name].ffill().to_numpy(float)
        coordinates = []
        for index, value in enumerate(values):
            x = left + plot_w * index / max(len(values) - 1, 1)
            y = top + plot_h * (high - value) / max(high - low, 1e-12)
            coordinates.append(f"{x:.2f} {y:.2f}")
        parts.append(f'<path d="M {" L ".join(coordinates)}" fill="none" stroke="{colors[position]}" stroke-width="2.5"/>')
        legend_y = height - 46 + position * 18
        parts.append(f'<line x1="{left}" y1="{legend_y - 4}" x2="{left + 30}" y2="{legend_y - 4}" stroke="{colors[position]}" stroke-width="3"/>')
        parts.append(f'<text x="{left + 40}" y="{legend_y}" font-size="11">{name} — ${values[-1]:,.0f}</text>')
    parts.append('</svg>')
    path.write_text("\n".join(parts), encoding="utf-8")


def run_window(
    label: str,
    price_return: pd.Series,
    price_start: pd.Timestamp,
    price_end: pd.Timestamp,
    scenarios: dict[str, dict],
) -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    price = price_returns_for_window(price_return, price_start, price_end)
    returns = {"PRICE_ONLY": price}
    funding_daily_columns = {}
    summaries = {}
    for scenario_name, accounting in scenarios.items():
        combined = combine_price_and_funding(price, accounting["daily_factor"])
        returns[scenario_name] = combined
        funding_daily_columns[f"{scenario_name}__funding_factor"] = accounting["daily_factor"].reindex(price.index)
        funding_daily_columns[f"{scenario_name}__additive"] = accounting["daily_additive"].reindex(price.index)
        summaries[scenario_name] = funding_summary(accounting)

    return_frame = pd.DataFrame(returns)
    equity = STARTING_NAV * (1.0 + return_frame).cumprod()
    daily_funding = pd.DataFrame(funding_daily_columns)
    report = {
        "label": label,
        "metrics": {name: metrics(series) for name, series in return_frame.items()},
        "annual_returns": {name: annual_returns(series) for name, series in return_frame.items()},
        "funding": summaries,
    }
    return report, equity, daily_funding


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    weights, canonical_equity, canonical_price_return = load_strategy_inputs()

    binance_full_blocks, binance_source_coverage = load_binance_full_blocks()
    binance_common_blocks, hyperliquid_common_blocks = load_common_blocks()

    coverage = {
        "binance_full": validate_complete_blocks(binance_full_blocks, BINANCE_START, BINANCE_END, "binance_full"),
        "binance_common": validate_complete_blocks(binance_common_blocks, COMMON_START, COMMON_END, "binance_common"),
        "hyperliquid_common": validate_complete_blocks(hyperliquid_common_blocks, COMMON_START, COMMON_END, "hyperliquid_common"),
    }

    binance_full_add = funding_accounting(binance_full_blocks, weights, "additive_rate", "BINANCE_FULL_ADDITIVE")
    binance_full_comp = funding_accounting(binance_full_blocks, weights, "compounded_rate", "BINANCE_FULL_COMPOUNDED")
    binance_common_add = funding_accounting(binance_common_blocks, weights, "additive_rate", "BINANCE_COMMON_ADDITIVE")
    binance_common_comp = funding_accounting(binance_common_blocks, weights, "compounded_rate", "BINANCE_COMMON_COMPOUNDED")
    hl_common_add = funding_accounting(hyperliquid_common_blocks, weights, "additive_rate", "HYPERLIQUID_COMMON_ADDITIVE")
    hl_common_comp = funding_accounting(hyperliquid_common_blocks, weights, "compounded_rate", "HYPERLIQUID_COMMON_COMPOUNDED")

    full_report, full_equity, full_daily = run_window(
        "BINANCE_FULL_HISTORY_PROXY_WINDOW",
        canonical_price_return,
        BINANCE_START,
        BINANCE_END,
        {
            "BINANCE_ALL_PERP_PROXY": binance_full_add,
            "BINANCE_ALL_PERP_PROXY_COMPOUNDED_SENSITIVITY": binance_full_comp,
        },
    )
    common_report, common_equity, common_daily = run_window(
        "ALL_FIVE_ASSET_COMMON_OVERLAP",
        canonical_price_return,
        COMMON_START,
        COMMON_END,
        {
            "BINANCE_ALL_PERP_COMMON": binance_common_add,
            "HYPERLIQUID_ALL_PERP_NATIVE": hl_common_add,
            "BINANCE_COMMON_COMPOUNDED_SENSITIVITY": binance_common_comp,
            "HYPERLIQUID_COMMON_COMPOUNDED_SENSITIVITY": hl_common_comp,
        },
    )

    common_difference = {
        "final_10k_hyperliquid_minus_binance": float(
            common_report["metrics"]["HYPERLIQUID_ALL_PERP_NATIVE"]["final_10k"]
            - common_report["metrics"]["BINANCE_ALL_PERP_COMMON"]["final_10k"]
        ),
        "cagr_hyperliquid_minus_binance": float(
            common_report["metrics"]["HYPERLIQUID_ALL_PERP_NATIVE"]["cagr"]
            - common_report["metrics"]["BINANCE_ALL_PERP_COMMON"]["cagr"]
        ),
        "total_compounded_funding_return_hyperliquid_minus_binance": float(
            common_report["funding"]["HYPERLIQUID_ALL_PERP_NATIVE"]["total_compounded_funding_return"]
            - common_report["funding"]["BINANCE_ALL_PERP_COMMON"]["total_compounded_funding_return"]
        ),
    }

    report = {
        "experiment_id": EXPERIMENT_ID,
        "trading_changes": False,
        "strategy": {
            "weights_source": str(WEIGHTS_PATH.relative_to(ROOT)),
            "equity_source": str(EQUITY_PATH.relative_to(ROOT)),
            "held_weight_columns": WEIGHT_COLUMNS,
            "daily_held_notional_approximation": True,
            "positive_rate_long_pays": True,
        },
        "coverage": coverage,
        "binance_source_coverage": binance_source_coverage,
        "full_history_proxy_window": full_report,
        "common_overlap_window": common_report,
        "common_source_difference": common_difference,
        "theoretical_zero_funding_spot_upper_bound": "PRICE_ONLY in each matching window; excludes basis, spot availability, borrow, execution and venue differences",
        "decision_rule": "No position or routing change is authorized. Binance is a sign/regime/stress proxy; Hyperliquid common-history results are the venue-specific estimate. A later router must separately model spot availability, basis, fees and execution.",
    }

    full_equity.index.name = "date"
    common_equity.index.name = "date"
    full_daily.index.name = "date"
    common_daily.index.name = "date"
    full_equity.to_csv(OUTPUT / "full_window_daily_equity.csv", float_format="%.10f")
    common_equity.to_csv(OUTPUT / "common_window_daily_equity.csv", float_format="%.10f")
    full_daily.to_csv(OUTPUT / "full_window_daily_funding.csv", float_format="%.12f")
    common_daily.to_csv(OUTPUT / "common_window_daily_funding.csv", float_format="%.12f")

    attribution_frames = []
    for source_name, accounting in {
        "BINANCE_FULL": binance_full_add,
        "BINANCE_COMMON": binance_common_add,
        "HYPERLIQUID_COMMON": hl_common_add,
    }.items():
        detail = accounting["block_detail"].copy()
        detail.insert(0, "source", source_name)
        attribution_frames.append(detail)
    pd.concat(attribution_frames, ignore_index=True).to_csv(
        OUTPUT / "block_asset_funding_attribution.csv", index=False, float_format="%.12f"
    )

    write_svg(
        common_equity[["PRICE_ONLY", "BINANCE_ALL_PERP_COMMON", "HYPERLIQUID_ALL_PERP_NATIVE"]],
        OUTPUT / "common_window_pnl.svg",
    )
    (OUTPUT / "funding_pnl_0003_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    print("=== FUNDING_PNL_0003_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
