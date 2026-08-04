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
from urllib.parse import quote

import numpy as np
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
RESULTS = RESEARCH / "results"
sys.path.insert(0, str(HERE))

from run_tsmom_perp_universe_audit import KLINE_ROOT, classify, dated_1d_files, prefix_symbols

AUDIT_ID = "TSMOM-PIT-0028-DAILY-ELIGIBILITY"
DATA_BASE = "https://data.binance.vision/"
DATA_START = pd.Timestamp("2020-09-01")
EVAL_START = pd.Timestamp("2021-05-01")
EVAL_END = pd.Timestamp("2026-07-31")
MIN_DAYS = 240
QVOL_FLOOR = 25_000_000.0
MAX_WORKERS = 16
MAX_FAILURE_FRACTION = 0.01
SNAPSHOTS = (
    "2022-01-01",
    "2023-01-01",
    "2024-01-01",
    "2025-01-01",
    "2026-01-01",
    "2026-07-31",
)
OUTPUT = HERE / "tsmom_pit_0028_outputs"


def month_in_range(month: str) -> bool:
    start = pd.Period(DATA_START, freq="M")
    end = pd.Period(EVAL_END, freq="M")
    p = pd.Period(month, freq="M")
    return start <= p <= end


def parse_archive_csv(payload: bytes, symbol: str, month: str) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        names = [name for name in zf.namelist() if not name.endswith("/")]
        if len(names) != 1:
            raise RuntimeError(f"{symbol} {month}: expected one file in zip, found {names}")
        with zf.open(names[0]) as handle:
            frame = pd.read_csv(handle, header=None)
    if frame.empty:
        return pd.DataFrame(columns=["close", "quote_volume"])
    # Some archive families may include a textual header row. Remove it mechanically.
    first = str(frame.iloc[0, 0]).lower()
    if "open" in first and "time" in first:
        frame = frame.iloc[1:].copy()
    if frame.shape[1] < 8:
        raise RuntimeError(f"{symbol} {month}: unexpected kline column count={frame.shape[1]}")
    open_time = pd.to_numeric(frame.iloc[:, 0], errors="coerce")
    close = pd.to_numeric(frame.iloc[:, 4], errors="coerce")
    quote_volume = pd.to_numeric(frame.iloc[:, 7], errors="coerce")
    valid = open_time.notna() & close.notna() & quote_volume.notna()
    open_time = open_time[valid].astype("int64")
    close = close[valid].astype(float)
    quote_volume = quote_volume[valid].astype(float)
    if open_time.empty:
        return pd.DataFrame(columns=["close", "quote_volume"])
    # Binance public-data timestamps can be millisecond or microsecond precision.
    unit = "us" if int(open_time.median()) >= 100_000_000_000_000 else "ms"
    dt = pd.to_datetime(open_time, unit=unit, utc=True).dt.tz_localize(None).dt.normalize()
    out = pd.DataFrame({
        "close": close.to_numpy(float),
        "quote_volume": quote_volume.to_numpy(float),
    }, index=pd.DatetimeIndex(dt))
    out = out[~out.index.duplicated(keep="last")].sort_index()
    return out.loc[(out.index >= DATA_START) & (out.index <= EVAL_END)]


def archive_url(symbol: str, month: str) -> str:
    key = f"{KLINE_ROOT}{symbol}/1d/{symbol}-1d-{month}.zip"
    return DATA_BASE + quote(key, safe="/._-")


def download_month(session: requests.Session, symbol: str, month: str) -> pd.DataFrame:
    url = archive_url(symbol, month)
    last_error: Exception | str | None = None
    for attempt in range(7):
        try:
            response = session.get(url, timeout=45)
            if response.status_code in (418, 429) or response.status_code >= 500:
                last_error = f"HTTP {response.status_code}: {response.text[:120]}"
                time.sleep(min(30.0, 1.5 * (2 ** attempt)))
                continue
            response.raise_for_status()
            return parse_archive_csv(response.content, symbol, month)
        except Exception as exc:
            last_error = exc
            time.sleep(min(20.0, 1.25 * (2 ** attempt)))
    raise RuntimeError(f"{symbol} {month} failed: {last_error!r}")


def fetch_symbol(symbol: str) -> tuple[str, pd.DataFrame, dict[str, Any]]:
    metadata = dated_1d_files(symbol)
    months = [m for m in metadata.get("months", []) if month_in_range(m)]
    session = requests.Session()
    parts: list[pd.DataFrame] = []
    month_errors: list[dict[str, str]] = []
    for month in months:
        try:
            part = download_month(session, symbol, month)
            if not part.empty:
                parts.append(part)
        except Exception as exc:
            month_errors.append({"month": month, "error": repr(exc)})
    if month_errors:
        raise RuntimeError(f"{symbol} month_errors={month_errors[:5]} total={len(month_errors)}")
    if not parts:
        frame = pd.DataFrame(columns=["close", "quote_volume"])
    else:
        frame = pd.concat(parts).sort_index()
        frame = frame[~frame.index.duplicated(keep="last")]
        frame = frame.loc[(frame.index >= DATA_START) & (frame.index <= EVAL_END)]
    diag = {
        "archive_first_month": metadata.get("first_month"),
        "archive_last_month": metadata.get("last_month"),
        "archive_month_count": metadata.get("monthly_1d_file_count", 0),
        "downloaded_month_count": len(months),
        "first_data_date": str(frame.index.min().date()) if len(frame) else None,
        "last_data_date": str(frame.index.max().date()) if len(frame) else None,
        "row_count": int(len(frame)),
    }
    return symbol, frame, diag


def build_eligibility(close: pd.DataFrame, qvol: pd.DataFrame) -> pd.DataFrame:
    full_index = pd.date_range(DATA_START, EVAL_END, freq="D")
    close = close.reindex(full_index)
    qvol = qvol.reindex(full_index)
    available = close.notna()
    full_recent_history = available.rolling(MIN_DAYS, min_periods=MIN_DAYS).sum() >= MIN_DAYS
    eligible = full_recent_history & available & qvol.ge(QVOL_FLOOR)
    return eligible.loc[EVAL_START:EVAL_END]


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    all_symbols = prefix_symbols(KLINE_ROOT)
    candidates = sorted(s for s in all_symbols if classify(s) == "ordinary_usdt_candidate")
    print(f"candidate_symbols={len(candidates)}", flush=True)

    data: dict[str, pd.DataFrame] = {}
    diagnostics: dict[str, dict[str, Any]] = {}
    errors: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(fetch_symbol, symbol): symbol for symbol in candidates}
        for i, future in enumerate(as_completed(futures), start=1):
            symbol = futures[future]
            try:
                sym, frame, diag = future.result()
                data[sym] = frame
                diagnostics[sym] = diag
            except Exception as exc:
                errors[symbol] = repr(exc)
            if i % 25 == 0 or i == len(futures):
                print(f"symbol_progress {i}/{len(futures)} errors={len(errors)}", flush=True)

    failure_fraction = len(errors) / max(len(candidates), 1)
    if failure_fraction > MAX_FAILURE_FRACTION:
        raise RuntimeError(f"Too many symbol download failures: {len(errors)}/{len(candidates)} = {failure_fraction:.4%}")
    usable = {s: df for s, df in data.items() if not df.empty}
    if not usable:
        raise RuntimeError("No usable futures daily history")

    close = pd.concat({s: df["close"] for s, df in usable.items()}, axis=1).sort_index()
    qvol = pd.concat({s: df["quote_volume"] for s, df in usable.items()}, axis=1).sort_index()
    columns = sorted(set(close.columns) & set(qvol.columns))
    close = close[columns]
    qvol = qvol[columns]
    eligible = build_eligibility(close, qvol)
    if int(eligible.to_numpy(bool).sum()) == 0:
        raise RuntimeError("Daily PIT eligibility is empty")

    daily_count = eligible.sum(axis=1).astype(int)
    daily = pd.DataFrame({"eligible_contracts": daily_count})
    daily.to_csv(OUTPUT / "daily_eligible_count.csv", index_label="date")
    eligible.astype("uint8").to_csv(OUTPUT / "eligibility_matrix.csv.gz", compression="gzip", index_label="date")

    symbol_rows: list[dict[str, Any]] = []
    latest_month = pd.Period(EVAL_END, freq="M")
    ended_ever_eligible: list[str] = []
    for symbol in columns:
        df = usable[symbol]
        e = eligible[symbol]
        eligible_dates = e.index[e]
        archive_last_month = diagnostics[symbol].get("archive_last_month")
        months_behind = None
        if archive_last_month:
            months_behind = latest_month.ordinal - pd.Period(archive_last_month, freq="M").ordinal
        ended_early = bool(months_behind is not None and months_behind >= 2)
        ever = bool(e.any())
        if ended_early and ever:
            ended_ever_eligible.append(symbol)
        symbol_rows.append({
            "symbol": symbol,
            **diagnostics[symbol],
            "months_behind_latest": months_behind,
            "ended_at_least_2_months_before_latest": ended_early,
            "eligible_days": int(e.sum()),
            "ever_eligible": ever,
            "first_eligible_date": str(eligible_dates[0].date()) if len(eligible_dates) else None,
            "last_eligible_date": str(eligible_dates[-1].date()) if len(eligible_dates) else None,
            "max_completed_day_quote_volume": float(qvol[symbol].max(skipna=True)) if qvol[symbol].notna().any() else None,
        })
    symbol_summary = pd.DataFrame(symbol_rows).sort_values("symbol")
    symbol_summary.to_csv(OUTPUT / "symbol_eligibility_summary.csv", index=False)

    snapshots: dict[str, dict[str, Any]] = {}
    for raw in SNAPSHOTS:
        dt = pd.Timestamp(raw)
        if dt not in eligible.index:
            snapshots[raw] = {"eligible_count": 0, "symbols": []}
            continue
        syms = sorted(eligible.columns[eligible.loc[dt].to_numpy(bool)].tolist())
        snapshots[raw] = {"eligible_count": len(syms), "symbols": syms}

    eval_counts = daily_count.loc[EVAL_START:EVAL_END]
    report = {
        "audit_id": AUDIT_ID,
        "status": "FIRST_RUN_COMPLETE",
        "trading_changes": False,
        "strategy_pnl": False,
        "parameters": {
            "data_start": str(DATA_START.date()),
            "evaluation_start": str(EVAL_START.date()),
            "evaluation_end": str(EVAL_END.date()),
            "continuous_history_days": MIN_DAYS,
            "completed_day_quote_volume_floor_usd": QVOL_FLOOR,
            "information_timing": "completed date-t kline only; future strategy execution must be t->t+1",
        },
        "coverage": {
            "archive_candidates": len(candidates),
            "usable_symbol_histories": len(columns),
            "symbol_failures": len(errors),
            "symbol_failure_fraction": failure_fraction,
            "panel_first_date": str(close.index.min().date()),
            "panel_last_date": str(close.index.max().date()),
            "evaluation_days": int(len(eval_counts)),
        },
        "eligibility": {
            "ever_eligible_symbols": int((symbol_summary["eligible_days"] > 0).sum()),
            "total_eligible_symbol_days": int(eligible.to_numpy(np.int64).sum()),
            "daily_count_min": int(eval_counts.min()),
            "daily_count_median": float(eval_counts.median()),
            "daily_count_mean": float(eval_counts.mean()),
            "daily_count_max": int(eval_counts.max()),
            "ended_early_contracts_ever_eligible_count": len(ended_ever_eligible),
            "ended_early_contracts_ever_eligible": sorted(ended_ever_eligible),
        },
        "snapshots": snapshots,
        "errors": errors,
        "success_gate": {
            "historical_panel_nonempty": len(columns) > 0,
            "daily_eligibility_nonempty": int(eligible.to_numpy(bool).sum()) > 0,
            "later_ended_contracts_historically_eligible": len(ended_ever_eligible) > 0,
            "symbol_download_failure_fraction_within_limit": failure_fraction <= MAX_FAILURE_FRACTION,
        },
        "interpretation": "This audit freezes completed-information daily perpetual eligibility only. It does not calculate a trend signal, position, return, Sharpe or correlation. Today's surviving universe is not used as a historical eligibility condition."
    }
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== TSMOM_PIT_0028_REPORT ===")
    printable = dict(report)
    printable["snapshots"] = {k: {"eligible_count": v["eligible_count"], "symbols_sample": v["symbols"][:20]} for k, v in snapshots.items()}
    print(json.dumps(printable, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
