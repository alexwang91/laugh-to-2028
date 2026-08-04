from __future__ import annotations

import csv
import io
import json
import re
import time
import zipfile
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import requests

from run_tsmom_perp_universe_audit import (
    KLINE_ROOT,
    S3_URL,
    classify,
    dated_1d_files,
    month_number,
    prefix_symbols,
)

AUDIT_ID = "TSMOM-DATA-0028-PIT-ELIGIBILITY"
MIN_DAYS = 240
QVOL_FLOOR = 25_000_000.0
MAX_WORKERS = 20
OUTPUT = Path(__file__).resolve().parent / "tsmom_data_0028_outputs"
DOWNLOAD_ROOT = "https://data.binance.vision"
SNAPSHOT_DATES = (
    "2021-01-01",
    "2022-01-01",
    "2023-01-01",
    "2024-01-01",
    "2025-01-01",
    "2026-01-01",
    "2026-07-31",
)


def _timestamp_unit(values: pd.Series) -> str:
    finite = pd.to_numeric(values, errors="coerce").dropna()
    if finite.empty:
        raise ValueError("no numeric open_time values")
    # Binance public data changed some timestamps to microseconds in newer archives.
    return "us" if float(finite.median()) > 1e14 else "ms"


def parse_month_zip(content: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]
        if not names:
            raise ValueError("empty zip archive")
        with archive.open(names[0]) as handle:
            raw = pd.read_csv(handle, header=None)
    if raw.empty or raw.shape[1] < 8:
        raise ValueError(f"unexpected kline CSV shape {raw.shape}")

    open_time = pd.to_numeric(raw.iloc[:, 0], errors="coerce")
    qvol = pd.to_numeric(raw.iloc[:, 7], errors="coerce")
    valid = open_time.notna() & qvol.notna()
    if not valid.any():
        raise ValueError("no numeric kline rows")
    open_time = open_time.loc[valid]
    qvol = qvol.loc[valid]
    unit = _timestamp_unit(open_time)
    dates = pd.to_datetime(open_time.astype("int64"), unit=unit, utc=True).dt.tz_localize(None).dt.normalize()
    frame = pd.DataFrame({"quote_volume": qvol.to_numpy(float)}, index=pd.DatetimeIndex(dates))
    frame = frame[~frame.index.duplicated(keep="last")].sort_index()
    return frame


def download_month(symbol: str, month: str) -> pd.DataFrame:
    url = f"{DOWNLOAD_ROOT}/{KLINE_ROOT}{symbol}/1d/{symbol}-1d-{month}.zip"
    last_error: Exception | None = None
    for attempt in range(6):
        try:
            response = requests.get(url, timeout=45)
            if response.status_code in (418, 429) or response.status_code >= 500:
                raise RuntimeError(f"HTTP {response.status_code}")
            response.raise_for_status()
            return parse_month_zip(response.content)
        except Exception as exc:
            last_error = exc
            time.sleep(min(8.0, 0.5 * (2 ** attempt)))
    raise RuntimeError(f"{symbol} {month} failed after retries: {last_error!r}")


def contiguous_run_length(index: pd.DatetimeIndex) -> pd.Series:
    index = pd.DatetimeIndex(index).sort_values()
    if len(index) == 0:
        return pd.Series(dtype=int)
    dates = pd.Series(index, index=index)
    new_run = dates.diff().dt.days.ne(1)
    groups = new_run.cumsum()
    return dates.groupby(groups).cumcount().add(1).astype(int)


def eligibility_for_history(history: pd.DataFrame) -> pd.DataFrame:
    history = history.sort_index().copy()
    run_length = contiguous_run_length(history.index)
    out = history.copy()
    out["contiguous_days"] = run_length.reindex(out.index).astype(int)
    out["eligible"] = (out["contiguous_days"] >= MIN_DAYS) & (out["quote_volume"] >= QVOL_FLOOR)
    out["effective_date"] = out.index + pd.Timedelta(days=1)
    return out


def eligible_spells(symbol: str, eligible_dates: pd.DatetimeIndex) -> list[dict[str, Any]]:
    dates = pd.DatetimeIndex(eligible_dates).sort_values()
    if len(dates) == 0:
        return []
    series = pd.Series(dates, index=dates)
    new_spell = series.diff().dt.days.ne(1)
    groups = new_spell.cumsum()
    rows: list[dict[str, Any]] = []
    for _, group in series.groupby(groups):
        start = pd.Timestamp(group.iloc[0])
        end = pd.Timestamp(group.iloc[-1])
        rows.append({
            "symbol": symbol,
            "eligible_start": str(start.date()),
            "eligible_end": str(end.date()),
            "effective_start": str((start + pd.Timedelta(days=1)).date()),
            "effective_end_inclusive": str((end + pd.Timedelta(days=1)).date()),
            "eligible_days": int(len(group)),
        })
    return rows


def load_symbol(symbol: str) -> dict[str, Any]:
    listing = dated_1d_files(symbol)
    months = listing.get("months", [])
    frames: list[pd.DataFrame] = []
    errors: list[str] = []
    for month in months:
        try:
            frames.append(download_month(symbol, month))
        except Exception as exc:
            errors.append(f"{month}: {exc!r}")
    if not frames:
        return {
            "symbol": symbol,
            "listing": listing,
            "history": pd.DataFrame(columns=["quote_volume"]),
            "download_errors": errors,
        }
    history = pd.concat(frames).sort_index()
    history = history[~history.index.duplicated(keep="last")]
    return {"symbol": symbol, "listing": listing, "history": history, "download_errors": errors}


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key) for key in fieldnames})


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    archive_symbols = prefix_symbols(KLINE_ROOT)
    candidates = sorted(
        symbol for symbol in archive_symbols
        if classify(symbol) == "ordinary_usdt_candidate"
    )
    if not candidates:
        raise RuntimeError("No ordinary historical USDT perpetual candidates")

    results: list[dict[str, Any]] = []
    top_level_errors: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(load_symbol, symbol): symbol for symbol in candidates}
        for completed, future in enumerate(as_completed(futures), start=1):
            symbol = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                top_level_errors.append({"symbol": symbol, "error": repr(exc)})
            if completed % 25 == 0 or completed == len(futures):
                month_errors = sum(len(row.get("download_errors", [])) for row in results)
                print(
                    f"history_progress {completed}/{len(futures)} "
                    f"symbol_errors={len(top_level_errors)} month_errors={month_errors}",
                    flush=True,
                )

    results.sort(key=lambda row: row["symbol"])
    nonempty = [row for row in results if not row["history"].empty]
    if not nonempty:
        raise RuntimeError("All historical perp histories are empty")

    latest_date = max(row["history"].index.max() for row in nonempty)
    latest_month = max(
        (row["listing"].get("last_month") for row in nonempty if row["listing"].get("last_month")),
        default=None,
    )
    latest_month_n = month_number(latest_month)

    daily_count: Counter[pd.Timestamp] = Counter()
    daily_symbols: dict[pd.Timestamp, list[str]] = {}
    summary_rows: list[dict[str, Any]] = []
    spell_rows: list[dict[str, Any]] = []
    all_month_errors: list[dict[str, Any]] = []
    premature_eligibility_violations = 0

    for row in results:
        symbol = row["symbol"]
        history = row["history"]
        listing = row["listing"]
        month_errors = row.get("download_errors", [])
        for error in month_errors:
            all_month_errors.append({"symbol": symbol, "error": error})

        if history.empty:
            summary_rows.append({
                "symbol": symbol,
                "bar_days": 0,
                "first_bar": None,
                "last_bar": None,
                "max_contiguous_days": 0,
                "eligible_days": 0,
                "first_eligible": None,
                "last_eligible": None,
                "ended_at_least_2_months_before_latest": None,
                "ever_eligible": False,
                "download_error_count": len(month_errors),
            })
            continue

        audited = eligibility_for_history(history)
        invalid = audited["eligible"] & (audited["contiguous_days"] < MIN_DAYS)
        premature_eligibility_violations += int(invalid.sum())
        eligible_dates = pd.DatetimeIndex(audited.index[audited["eligible"]])
        for date in eligible_dates:
            ts = pd.Timestamp(date)
            daily_count[ts] += 1
            daily_symbols.setdefault(ts, []).append(symbol)
        spell_rows.extend(eligible_spells(symbol, eligible_dates))

        last_month_n = month_number(listing.get("last_month"))
        ended_early = bool(
            latest_month_n is not None
            and last_month_n is not None
            and latest_month_n - last_month_n >= 2
        )
        summary_rows.append({
            "symbol": symbol,
            "bar_days": int(len(audited)),
            "first_bar": str(audited.index.min().date()),
            "last_bar": str(audited.index.max().date()),
            "max_contiguous_days": int(audited["contiguous_days"].max()),
            "eligible_days": int(audited["eligible"].sum()),
            "first_eligible": str(eligible_dates.min().date()) if len(eligible_dates) else None,
            "last_eligible": str(eligible_dates.max().date()) if len(eligible_dates) else None,
            "ended_at_least_2_months_before_latest": ended_early,
            "ever_eligible": bool(len(eligible_dates)),
            "download_error_count": len(month_errors),
        })

    count_rows = [
        {"date": str(date.date()), "eligible_contracts": int(count)}
        for date, count in sorted(daily_count.items())
    ]
    eligible_counts = pd.Series({date: count for date, count in daily_count.items()}, dtype=float).sort_index()
    eligible_symbols_count = sum(bool(row["ever_eligible"]) for row in summary_rows)
    ended_eligible = sorted(
        row["symbol"] for row in summary_rows
        if row.get("ended_at_least_2_months_before_latest") and row.get("ever_eligible")
    )

    snapshots: dict[str, Any] = {}
    for value in SNAPSHOT_DATES:
        date = pd.Timestamp(value)
        symbols = sorted(daily_symbols.get(date, []))
        snapshots[value] = {
            "eligible_count": len(symbols),
            "symbols_sample": symbols[:50],
        }

    if len(eligible_counts):
        count_stats = {
            "first_eligible_date": str(eligible_counts.index.min().date()),
            "last_eligible_date": str(eligible_counts.index.max().date()),
            "eligible_calendar_days": int(len(eligible_counts)),
            "min_eligible_contracts_on_nonzero_days": int(eligible_counts.min()),
            "median_eligible_contracts_on_nonzero_days": float(eligible_counts.median()),
            "max_eligible_contracts": int(eligible_counts.max()),
            "date_of_max_count": str(eligible_counts.idxmax().date()),
        }
    else:
        count_stats = {
            "first_eligible_date": None,
            "last_eligible_date": None,
            "eligible_calendar_days": 0,
            "min_eligible_contracts_on_nonzero_days": 0,
            "median_eligible_contracts_on_nonzero_days": 0.0,
            "max_eligible_contracts": 0,
            "date_of_max_count": None,
        }

    _write_csv(
        OUTPUT / "symbol_eligibility_summary.csv",
        summary_rows,
        [
            "symbol", "bar_days", "first_bar", "last_bar", "max_contiguous_days",
            "eligible_days", "first_eligible", "last_eligible",
            "ended_at_least_2_months_before_latest", "ever_eligible", "download_error_count",
        ],
    )
    _write_csv(
        OUTPUT / "eligibility_spells.csv",
        spell_rows,
        ["symbol", "eligible_start", "eligible_end", "effective_start", "effective_end_inclusive", "eligible_days"],
    )
    _write_csv(OUTPUT / "daily_eligible_counts.csv", count_rows, ["date", "eligible_contracts"])

    successful_symbols = len(results) - len(top_level_errors)
    symbols_with_month_errors = sum(bool(row.get("download_errors")) for row in results)
    report = {
        "audit_id": AUDIT_ID,
        "trading_changes": False,
        "strategy_pnl": False,
        "rule": {
            "minimum_contiguous_completed_daily_bars": MIN_DAYS,
            "completed_day_quote_volume_floor_usd": QVOL_FLOOR,
            "effective_lag_days": 1,
            "parameter_source": "exact PIT-DISP-0015 eligibility thresholds; not TSMOM-PNL selected",
        },
        "source": {
            "s3": S3_URL,
            "kline_root": KLINE_ROOT,
            "latest_archive_date_observed": str(pd.Timestamp(latest_date).date()),
            "latest_archive_month_observed": latest_month,
        },
        "coverage": {
            "candidate_symbols": len(candidates),
            "symbol_jobs_returned": len(results),
            "successful_symbol_jobs": successful_symbols,
            "top_level_symbol_errors": len(top_level_errors),
            "symbols_with_month_download_errors": symbols_with_month_errors,
            "month_download_errors": len(all_month_errors),
            "nonempty_histories": len(nonempty),
        },
        "eligibility": {
            "symbols_ever_eligible": eligible_symbols_count,
            "ended_early_symbols_ever_eligible": len(ended_eligible),
            "ended_early_ever_eligible_examples": ended_eligible[:50],
            "premature_eligibility_violations": premature_eligibility_violations,
            **count_stats,
        },
        "snapshots": snapshots,
        "errors": {
            "top_level": top_level_errors,
            "month_download_sample": all_month_errors[:100],
        },
        "success_gate": {
            "candidate_universe_nonempty": len(candidates) > 0,
            "at_least_98pct_symbol_jobs_returned": len(results) >= int(np.ceil(0.98 * len(candidates))),
            "nontrivial_eligible_universe": eligible_symbols_count >= 10 and count_stats["max_eligible_contracts"] >= 5,
            "later_ended_contract_previously_eligible": len(ended_eligible) > 0,
            "no_premature_eligibility": premature_eligibility_violations == 0,
        },
        "interpretation": (
            "Eligibility on completed UTC day t uses only that contract's archive history through t and quote volume on t; "
            "it is usable no earlier than t+1. Current survivor status and future delisting are not inputs. No TSMOM "
            "signal, rank, long/short position, return or PNL is computed in this audit."
        ),
    }
    report["passed"] = bool(all(value for value in report["success_gate"].values()))
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("=== TSMOM_DATA_0028_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
