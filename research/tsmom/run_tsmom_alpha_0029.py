from __future__ import annotations

import io
import json
import math
import sys
import time
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
ROOT = RESEARCH.parent
for path in (
    RESEARCH,
    RESEARCH / "regime_kelly",
    RESEARCH / "funding_router",
    RESEARCH / "asym_beta",
    HERE,
):
    sys.path.insert(0, str(path))

from features import trend_score
from run_tsmom_perp_universe_audit import KLINE_ROOT, classify, dated_1d_files, prefix_symbols
from run_tsmom_pit_eligibility import MIN_DAYS, QVOL_FLOOR, _timestamp_unit, eligibility_for_history
from run_funding_data_audit import (
    detect_column,
    parse_timestamp,
    parse_zip as parse_funding_zip,
    symbol_months as funding_symbol_months,
)
from run_asym_beta_0021 import expected_router_0005_equity_from_persisted_inputs

EXPERIMENT_ID = "TSMOM-ALPHA-0029"
DOWNLOAD_ROOT = "https://data.binance.vision"
PRICE_END = pd.Timestamp("2026-07-31")
# A target held on day d pays the 00:00 event on d+1 before the next rebalance.
# July archive cannot guarantee the 2026-08-01 00:00 event, so canonical funding PNL ends Jul 30.
FUNDING_END = pd.Timestamp("2026-07-30")
MAX_WORKERS = 20
VOL_WINDOW = 30
COSTS_BPS = (5.0, 10.0, 20.0)
CANONICAL_COST_BPS = 5.0
OUTPUT = RESEARCH / "results" / "tsmom_alpha_0029"
BRRK_EQUITY_PATH = RESEARCH / "results" / "pit_disp_0015" / "daily_equity.csv"
EPS = 1e-12


def download_bytes(url: str) -> bytes:
    last_error: Exception | None = None
    for attempt in range(6):
        try:
            response = requests.get(url, timeout=60)
            if response.status_code in (418, 429) or response.status_code >= 500:
                raise RuntimeError(f"HTTP {response.status_code}")
            response.raise_for_status()
            return response.content
        except Exception as exc:
            last_error = exc
            time.sleep(min(8.0, 0.5 * (2 ** attempt)))
    raise RuntimeError(f"download failed {url}: {last_error!r}")


def parse_kline_zip(payload: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]
        if not names:
            raise ValueError("empty kline zip")
        with archive.open(names[0]) as handle:
            raw = pd.read_csv(handle, header=None)
    if raw.empty or raw.shape[1] < 8:
        raise ValueError(f"unexpected kline shape {raw.shape}")
    open_time = pd.to_numeric(raw.iloc[:, 0], errors="coerce")
    close = pd.to_numeric(raw.iloc[:, 4], errors="coerce")
    quote_volume = pd.to_numeric(raw.iloc[:, 7], errors="coerce")
    valid = open_time.notna() & close.notna() & quote_volume.notna()
    if not valid.any():
        raise ValueError("no numeric kline rows")
    open_time = open_time.loc[valid]
    unit = _timestamp_unit(open_time)
    dates = pd.to_datetime(open_time.astype("int64"), unit=unit, utc=True).dt.tz_localize(None).dt.normalize()
    frame = pd.DataFrame(
        {
            "close": close.loc[valid].to_numpy(float),
            "quote_volume": quote_volume.loc[valid].to_numpy(float),
        },
        index=pd.DatetimeIndex(dates),
    )
    return frame[~frame.index.duplicated(keep="last")].sort_index()


def load_price_history(symbol: str) -> dict[str, Any]:
    listing = dated_1d_files(symbol)
    frames: list[pd.DataFrame] = []
    errors: list[str] = []
    for month in listing.get("months", []):
        url = f"{DOWNLOAD_ROOT}/{KLINE_ROOT}{symbol}/1d/{symbol}-1d-{month}.zip"
        try:
            frames.append(parse_kline_zip(download_bytes(url)))
        except Exception as exc:
            errors.append(f"{month}: {exc!r}")
    if not frames:
        return {"symbol": symbol, "history": pd.DataFrame(columns=["close", "quote_volume"]), "errors": errors}
    history = pd.concat(frames).sort_index()
    history = history[~history.index.duplicated(keep="last")].loc[:PRICE_END]
    return {"symbol": symbol, "history": history, "errors": errors}


def load_price_panel() -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Any]]:
    candidates = sorted(
        symbol for symbol in prefix_symbols(KLINE_ROOT)
        if classify(symbol) == "ordinary_usdt_candidate"
    )
    rows: list[dict[str, Any]] = []
    top_errors: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(load_price_history, symbol): symbol for symbol in candidates}
        for completed, future in enumerate(as_completed(futures), start=1):
            symbol = futures[future]
            try:
                rows.append(future.result())
            except Exception as exc:
                top_errors.append({"symbol": symbol, "error": repr(exc)})
            if completed % 25 == 0 or completed == len(futures):
                month_errors = sum(len(row.get("errors", [])) for row in rows)
                print(
                    f"price_progress {completed}/{len(futures)} top_errors={len(top_errors)} month_errors={month_errors}",
                    flush=True,
                )
    rows.sort(key=lambda row: row["symbol"])
    month_errors = [(row["symbol"], err) for row in rows for err in row.get("errors", [])]
    if top_errors or month_errors:
        raise RuntimeError(
            f"Price archive incomplete: top_errors={top_errors[:5]} month_errors={month_errors[:5]} "
            f"counts={len(top_errors)}/{len(month_errors)}"
        )
    histories = {row["symbol"]: row["history"] for row in rows if not row["history"].empty}
    close = pd.concat({symbol: frame["close"] for symbol, frame in histories.items()}, axis=1).sort_index()
    qvol = pd.concat({symbol: frame["quote_volume"] for symbol, frame in histories.items()}, axis=1).sort_index()
    return close, qvol, {
        "candidates": len(candidates),
        "nonempty_histories": len(histories),
        "top_level_errors": 0,
        "month_errors": 0,
    }


def build_eligibility(close: pd.DataFrame, qvol: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(False, index=close.index, columns=close.columns)
    for symbol in close.columns:
        history = pd.DataFrame({"quote_volume": qvol[symbol].dropna()})
        audited = eligibility_for_history(history)
        out.loc[audited.index, symbol] = audited["eligible"].astype(bool)
    return out


def build_targets(close: pd.DataFrame, eligibility: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    logret = np.log(close / close.shift(1))
    vol = logret.rolling(VOL_WINDOW, min_periods=VOL_WINDOW).std() * math.sqrt(365.0)
    trend = pd.DataFrame(index=close.index, columns=close.columns, dtype=float)
    for symbol in close.columns:
        trend[symbol] = trend_score(close[symbol])
    direction = np.sign(trend)
    raw = direction.div(vol.where(vol > EPS))
    valid = eligibility & trend.notna() & vol.notna() & (vol > EPS)
    raw = raw.where(valid, 0.0).replace([np.inf, -np.inf], 0.0).fillna(0.0)
    denom = raw.abs().sum(axis=1)
    target = raw.div(denom.replace(0.0, np.nan), axis=0).fillna(0.0)
    return target.astype(float), trend.astype(float), vol.astype(float)


def price_returns_and_costs(
    close: pd.DataFrame,
    target: pd.DataFrame,
) -> tuple[pd.Series, pd.Series, pd.Series, pd.DataFrame, dict[float, pd.Series]]:
    held = target.shift(1).fillna(0.0)
    asset_ret = close.pct_change(fill_method=None)
    missing_held = (held.abs() > EPS) & asset_ret.isna()
    missing_count = int(missing_held.to_numpy().sum())
    if missing_count:
        locs = np.argwhere(missing_held.to_numpy())[:10]
        examples = [(str(missing_held.index[i].date()), missing_held.columns[j]) for i, j in locs]
        raise RuntimeError(f"Held positions without next-day perp return: count={missing_count} examples={examples}")
    gross_price = (held * asset_ret.fillna(0.0)).sum(axis=1).astype(float)
    turnover = held.diff().abs().sum(axis=1).astype(float)
    if len(turnover):
        turnover.iloc[0] = held.iloc[0].abs().sum()
    gross = held.abs().sum(axis=1).astype(float)
    by_cost = {
        float(cost): (gross_price - turnover * float(cost) / 10000.0).astype(float)
        for cost in COSTS_BPS
    }
    return gross_price, turnover, gross, held, by_cost


def _funding_object_rows(symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> list[dict[str, Any]]:
    _, objects = funding_symbol_months(symbol)
    start_period = (start - pd.Timedelta(days=2)).to_period("M")
    end_period = (end + pd.Timedelta(days=2)).to_period("M")
    return [row for row in objects if start_period <= pd.Period(row["month"], freq="M") <= end_period]


def load_symbol_funding(symbol: str, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    objects = _funding_object_rows(symbol, start, end)
    if not objects:
        raise RuntimeError(f"{symbol}: no funding objects in active window")
    for row in objects:
        frame, metadata = parse_funding_zip(row["key"])
        columns = [str(column) for column in frame.columns]
        time_col = detect_column(columns, ("calc_time", "fundingTime", "funding_time", "time", "timestamp"), "time")
        rate_col = detect_column(columns, ("last_funding_rate", "fundingRate", "funding_rate"), "funding")
        if time_col is None or rate_col is None:
            raise RuntimeError(f"{symbol} {metadata['key']}: funding fields not found: {columns}")
        ts = parse_timestamp(frame[time_col])
        rate = pd.to_numeric(frame[rate_col], errors="coerce")
        valid = ts.notna() & rate.notna()
        piece = pd.DataFrame({"timestamp": ts.loc[valid], "rate": rate.loc[valid].to_numpy(float)})
        frames.append(piece)
    out = pd.concat(frames, ignore_index=True).drop_duplicates(subset=["timestamp"], keep="last").sort_values("timestamp")
    lower = pd.Timestamp(start - pd.Timedelta(days=1), tz="UTC")
    upper = pd.Timestamp(end + pd.Timedelta(days=1, hours=1), tz="UTC")
    return out[(out["timestamp"] >= lower) & (out["timestamp"] <= upper)].copy()


def load_funding_panel(active_windows: dict[str, tuple[pd.Timestamp, pd.Timestamp]]) -> tuple[dict[str, pd.DataFrame], dict[str, Any]]:
    data: dict[str, pd.DataFrame] = {}
    errors: list[dict[str, str]] = []
    items = sorted(active_windows.items())
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {
            pool.submit(load_symbol_funding, symbol, window[0], window[1]): symbol
            for symbol, window in items
        }
        for completed, future in enumerate(as_completed(futures), start=1):
            symbol = futures[future]
            try:
                data[symbol] = future.result()
            except Exception as exc:
                errors.append({"symbol": symbol, "error": repr(exc)})
            if completed % 25 == 0 or completed == len(futures):
                print(f"funding_progress {completed}/{len(futures)} errors={len(errors)}", flush=True)
    if errors:
        raise RuntimeError(f"Funding archive errors: count={len(errors)} sample={errors[:10]}")
    return data, {"active_symbols": len(items), "funding_symbols_loaded": len(data), "errors": 0}


def event_pnl_date(timestamp: pd.Timestamp) -> pd.Timestamp:
    ts = pd.Timestamp(timestamp).tz_convert("UTC")
    day = ts.tz_localize(None).normalize()
    # New target is effective at 00:00:01. The exact 00:00 funding event belongs to the prior held day.
    if ts.hour == 0 and ts.minute == 0 and ts.second == 0:
        return day - pd.Timedelta(days=1)
    return day


def funding_accounting(
    held: pd.DataFrame,
    funding: dict[str, pd.DataFrame],
    index: pd.DatetimeIndex,
) -> tuple[pd.Series, pd.DataFrame, dict[str, Any]]:
    events: list[dict[str, Any]] = []
    symbol_rows: list[dict[str, Any]] = []
    active_without_funding: list[tuple[str, str]] = []

    for symbol in held.columns:
        active = held.index[(held[symbol].abs() > EPS) & held.index.isin(index)]
        if len(active) == 0:
            continue
        frame = funding.get(symbol)
        if frame is None or frame.empty:
            raise RuntimeError(f"{symbol}: active position but no funding events")
        covered_dates: set[pd.Timestamp] = set()
        long_contribution = 0.0
        short_contribution = 0.0
        event_count = 0
        for row in frame.itertuples(index=False):
            ts = pd.Timestamp(row.timestamp)
            pnl_date = event_pnl_date(ts)
            if pnl_date not in index or pnl_date not in held.index:
                continue
            weight = float(held.at[pnl_date, symbol])
            if abs(weight) <= EPS:
                continue
            rate = float(row.rate)
            contribution = -weight * rate
            covered_dates.add(pnl_date)
            event_count += 1
            if weight > 0:
                long_contribution += contribution
            else:
                short_contribution += contribution
            events.append({
                "timestamp": ts,
                "pnl_date": pnl_date,
                "symbol": symbol,
                "weight": weight,
                "rate": rate,
                "contribution": contribution,
            })
        missing_dates = [date for date in active if pd.Timestamp(date) not in covered_dates]
        active_without_funding.extend((symbol, str(pd.Timestamp(date).date())) for date in missing_dates)
        symbol_rows.append({
            "symbol": symbol,
            "active_days": int(len(active)),
            "funding_event_count": event_count,
            "long_additive_contribution": float(long_contribution),
            "short_additive_contribution": float(short_contribution),
            "net_additive_contribution": float(long_contribution + short_contribution),
            "active_days_without_funding_event": int(len(missing_dates)),
        })

    if active_without_funding:
        raise RuntimeError(
            f"Active symbol-days without funding event: count={len(active_without_funding)} sample={active_without_funding[:20]}"
        )

    event_frame = pd.DataFrame(events)
    factor = pd.Series(1.0, index=index, dtype=float)
    if not event_frame.empty:
        grouped_event = event_frame.groupby(["pnl_date", "timestamp"], sort=True)["contribution"].sum()
        if (1.0 + grouped_event <= 0).any():
            raise RuntimeError("Funding event portfolio return <= -100%")
        daily = (1.0 + grouped_event).groupby(level=0).prod()
        factor.loc[daily.index.intersection(factor.index)] = daily.reindex(factor.index).dropna()
    symbol_summary = pd.DataFrame(symbol_rows).sort_values("symbol")
    diag = {
        "event_rows_used": int(len(event_frame)),
        "active_symbol_days_without_funding_event": 0,
        "long_additive_contribution": float(symbol_summary["long_additive_contribution"].sum()) if len(symbol_summary) else 0.0,
        "short_additive_contribution": float(symbol_summary["short_additive_contribution"].sum()) if len(symbol_summary) else 0.0,
        "net_additive_contribution": float(symbol_summary["net_additive_contribution"].sum()) if len(symbol_summary) else 0.0,
    }
    return factor, symbol_summary, diag


def metrics(ret: pd.Series, turnover: pd.Series | None = None, gross: pd.Series | None = None) -> dict[str, Any]:
    ret = ret.dropna().astype(float)
    if ret.empty:
        raise ValueError("empty return series")
    nav = (1.0 + ret).cumprod()
    elapsed_years = max((ret.index[-1] - ret.index[0]).days / 365.25, 1.0 / 365.25)
    cagr = float(nav.iloc[-1] ** (1.0 / elapsed_years) - 1.0)
    dd = nav / nav.cummax() - 1.0
    std = float(ret.std(ddof=1))
    return {
        "start": str(ret.index[0].date()),
        "end": str(ret.index[-1].date()),
        "observations": int(len(ret)),
        "final_10k": float(nav.iloc[-1] * 10000.0),
        "cagr": cagr,
        "max_drawdown": float(dd.min()),
        "ann_vol": float(std * math.sqrt(365.0)),
        "sharpe": float(ret.mean() / std * math.sqrt(365.0)) if std > 0 else None,
        "calmar": float(cagr / abs(dd.min())) if dd.min() < 0 else None,
        "turnover": float(turnover.reindex(ret.index).fillna(0.0).sum()) if turnover is not None else None,
        "avg_gross": float(gross.reindex(ret.index).mean()) if gross is not None else None,
    }


def annual_returns(ret: pd.Series) -> dict[str, float]:
    return {str(int(year)): float((1.0 + group).prod() - 1.0) for year, group in ret.groupby(ret.index.year)}


def return_correlation(a: pd.Series, b: pd.Series) -> dict[str, Any]:
    x = pd.concat([a.rename("a"), b.rename("b")], axis=1).dropna()
    monthly = pd.concat([
        ((1.0 + x["a"]).resample("ME").prod() - 1.0).rename("a"),
        ((1.0 + x["b"]).resample("ME").prod() - 1.0).rename("b"),
    ], axis=1).dropna()
    return {
        "start": str(x.index.min().date()) if len(x) else None,
        "end": str(x.index.max().date()) if len(x) else None,
        "daily_observations": int(len(x)),
        "daily_correlation": float(x.corr().iloc[0, 1]) if len(x) > 2 else None,
        "monthly_observations": int(len(monthly)),
        "monthly_correlation": float(monthly.corr().iloc[0, 1]) if len(monthly) > 2 else None,
    }


def crisis_alpha(tsmom: pd.Series, brrk: pd.Series) -> dict[str, Any]:
    x = pd.concat([tsmom.rename("tsmom"), brrk.rename("brrk")], axis=1).dropna()
    cutoff = float(x["brrk"].quantile(0.10))
    tail = x[x["brrk"] <= cutoff]
    worst20 = x.nsmallest(min(20, len(x)), "brrk")
    monthly = pd.concat([
        ((1.0 + x["tsmom"]).resample("ME").prod() - 1.0).rename("tsmom"),
        ((1.0 + x["brrk"]).resample("ME").prod() - 1.0).rename("brrk"),
    ], axis=1).dropna()
    mcut = float(monthly["brrk"].quantile(0.10)) if len(monthly) else float("nan")
    mtail = monthly[monthly["brrk"] <= mcut] if len(monthly) else monthly
    return {
        "brrk_daily_10pct_cutoff": cutoff,
        "tail_day_count": int(len(tail)),
        "mean_tsmom_return_on_brrk_worst_decile_days": float(tail["tsmom"].mean()) if len(tail) else None,
        "compound_tsmom_return_on_brrk_worst_decile_days": float((1.0 + tail["tsmom"]).prod() - 1.0) if len(tail) else None,
        "worst20_brrk_days_mean_tsmom": float(worst20["tsmom"].mean()) if len(worst20) else None,
        "worst20_brrk_days_compound_tsmom": float((1.0 + worst20["tsmom"]).prod() - 1.0) if len(worst20) else None,
        "brrk_monthly_10pct_cutoff": mcut if np.isfinite(mcut) else None,
        "tail_month_count": int(len(mtail)),
        "mean_tsmom_return_on_brrk_worst_decile_months": float(mtail["tsmom"].mean()) if len(mtail) else None,
    }


def load_brrk_price_return() -> pd.Series:
    frame = pd.read_csv(BRRK_EQUITY_PATH, parse_dates=["date"]).set_index("date")
    equity = frame["BRRK0011_BASELINE"].astype(float)
    return equity.pct_change(fill_method=None).rename("BRRK0011_PRICE_ONLY")


def load_brrk_strict_return() -> pd.Series:
    equity = expected_router_0005_equity_from_persisted_inputs().astype(float)
    return equity.pct_change(fill_method=None).rename("BRRK0011_STRICT_ROUTER")


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    close, qvol, price_coverage = load_price_panel()
    eligibility = build_eligibility(close, qvol)
    target, trend, vol = build_targets(close, eligibility)
    gross_price, turnover, gross, held, price_by_cost = price_returns_and_costs(close, target)

    active_mask = held.abs() > EPS
    active_dates = gross.index[gross > EPS]
    if len(active_dates) == 0:
        raise RuntimeError("TSMOM produced no active positions")
    eval_start = pd.Timestamp(active_dates.min())
    price_index = gross.loc[eval_start:PRICE_END].index
    funding_index = gross.loc[eval_start:FUNDING_END].index

    active_windows: dict[str, tuple[pd.Timestamp, pd.Timestamp]] = {}
    for symbol in held.columns:
        dates = held.index[(held[symbol].abs() > EPS) & (held.index >= eval_start) & (held.index <= FUNDING_END)]
        if len(dates):
            active_windows[symbol] = (pd.Timestamp(dates.min()), pd.Timestamp(dates.max()))

    funding_data, funding_coverage = load_funding_panel(active_windows)
    funding_factor, funding_by_symbol, funding_diag = funding_accounting(held, funding_data, funding_index)

    canonical_price = price_by_cost[CANONICAL_COST_BPS].reindex(funding_index)
    funding_ret = ((1.0 + canonical_price) * funding_factor - 1.0).astype(float)

    # Exposure diagnostics are based on actually held positions.
    held_eval = held.reindex(price_index).fillna(0.0)
    long_gross = held_eval.clip(lower=0.0).sum(axis=1)
    short_gross = -held_eval.clip(upper=0.0).sum(axis=1)
    net = held_eval.sum(axis=1)
    active_count = (held_eval.abs() > EPS).sum(axis=1)
    max_name_weight = held_eval.abs().max(axis=1)

    # Post-hoc survivorship diagnostic only; future end dates never enter target construction.
    global_last = close.apply(lambda s: s.last_valid_index())
    ended_early = [symbol for symbol, date in global_last.items() if date is not None and pd.Timestamp(date) <= PRICE_END - pd.Timedelta(days=60)]
    ended_held = sorted(symbol for symbol in ended_early if symbol in held and bool((held[symbol].abs() > EPS).any()))

    brrk_price = load_brrk_price_return()
    brrk_strict = load_brrk_strict_return()
    canonical_for_corr = funding_ret
    corr_price = return_correlation(canonical_for_corr, brrk_price)
    corr_strict = return_correlation(canonical_for_corr, brrk_strict)
    crisis = crisis_alpha(canonical_for_corr, brrk_price)

    cost_stress = {}
    for cost, ret in price_by_cost.items():
        r = ret.reindex(price_index)
        cost_stress[str(int(cost))] = metrics(r, turnover.reindex(price_index), gross.reindex(price_index))

    price_metrics = metrics(
        price_by_cost[CANONICAL_COST_BPS].reindex(price_index),
        turnover.reindex(price_index),
        gross.reindex(price_index),
    )
    funding_metrics = metrics(
        funding_ret,
        turnover.reindex(funding_index),
        gross.reindex(funding_index),
    )

    funding_sharpe = funding_metrics["sharpe"]
    qualification = {
        "funding_aware_economics": bool(funding_metrics["cagr"] > 0 and funding_sharpe is not None and funding_sharpe > 0),
        "daily_correlation_below_0_50": bool(corr_price["daily_correlation"] is not None and corr_price["daily_correlation"] < 0.50),
        "nonnegative_brrk_worst_decile_day_alpha": bool(
            crisis["mean_tsmom_return_on_brrk_worst_decile_days"] is not None
            and crisis["mean_tsmom_return_on_brrk_worst_decile_days"] >= 0
        ),
    }
    qualification["qualified_for_stack_test"] = bool(all(qualification.values()))

    daily = pd.DataFrame(index=price_index)
    daily["price_only_5bps"] = price_by_cost[5.0].reindex(price_index)
    daily["price_only_10bps"] = price_by_cost[10.0].reindex(price_index)
    daily["price_only_20bps"] = price_by_cost[20.0].reindex(price_index)
    daily["funding_aware_5bps"] = funding_ret.reindex(price_index)
    daily["funding_factor"] = funding_factor.reindex(price_index)
    daily["turnover"] = turnover.reindex(price_index)
    daily["gross"] = gross.reindex(price_index)
    daily["long_gross"] = long_gross
    daily["short_gross"] = short_gross
    daily["net"] = net
    daily["active_contracts"] = active_count
    daily["max_single_name_abs_weight"] = max_name_weight
    daily.to_csv(OUTPUT / "daily_returns_exposure.csv", index_label="date")
    funding_by_symbol.to_csv(OUTPUT / "funding_by_symbol.csv", index=False)

    report = {
        "experiment_id": EXPERIMENT_ID,
        "status": "FIRST_VALID_RUN_COMPLETE",
        "promotion_evidence": False,
        "price_coverage": price_coverage,
        "funding_coverage": funding_coverage,
        "universe_diagnostics": {
            "symbols_ever_eligible": int((eligibility.sum(axis=0) > 0).sum()),
            "symbols_ever_held": int((active_mask.sum(axis=0) > 0).sum()),
            "later_ended_symbols_ever_held_count": len(ended_held),
            "later_ended_symbols_ever_held_examples": ended_held[:50],
        },
        "execution": {
            "first_held_date": str(eval_start.date()),
            "price_end": str(PRICE_END.date()),
            "funding_end": str(FUNDING_END.date()),
            "canonical_cost_bps": CANONICAL_COST_BPS,
            "funding_event_timing": "target t effective t+1 00:00:01; exact 00:00 funding event belongs to previous held day",
        },
        "price_only_5bps": price_metrics,
        "funding_aware_5bps": funding_metrics,
        "cost_stress_price_only": cost_stress,
        "annual_price_only_5bps": annual_returns(price_by_cost[5.0].reindex(price_index)),
        "annual_funding_aware_5bps": annual_returns(funding_ret),
        "exposure": {
            "avg_long_gross": float(long_gross.mean()),
            "avg_short_gross": float(short_gross.mean()),
            "avg_net": float(net.mean()),
            "min_net": float(net.min()),
            "max_net": float(net.max()),
            "avg_active_contracts": float(active_count.mean()),
            "max_active_contracts": int(active_count.max()),
            "avg_max_single_name_abs_weight": float(max_name_weight.mean()),
            "max_single_name_abs_weight": float(max_name_weight.max()),
        },
        "funding": funding_diag,
        "correlation_vs_brrk_price_only": corr_price,
        "correlation_vs_brrk_strict_router": corr_strict,
        "crisis_alpha_vs_brrk_price_only": crisis,
        "qualification": qualification,
        "stopping_rule": (
            "No parameter tuning after this first valid run. If qualification fails, retain rejected evidence and move to carry. "
            "If it passes, only a separately preregistered portfolio-stack experiment may combine TSMOM with BRRK."
        ),
    }
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== TSMOM_ALPHA_0029_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
