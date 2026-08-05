from __future__ import annotations

import io
import json
import math
import re
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
PIT = RESEARCH / "pit_universe"
FUNDING = RESEARCH / "funding_router"
for path in (RESEARCH, PIT, FUNDING, HERE):
    sys.path.insert(0, str(path))

from run_archive_discovery import S3_URL, s3_list
from run_funding_data_audit import detect_column, parse_timestamp

AUDIT_ID = "CARRY-DATA-0030"
ASSETS = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT")
SPOT_ROOT = "data/spot/monthly/klines/"
PERP_ROOT = "data/futures/um/monthly/klines/"
FUNDING_ROOT = "data/futures/um/monthly/fundingRate/"
OUTPUT = RESEARCH / "results" / "carry_data_0030"
MAX_WORKERS = 5
MIN_ALIGNMENT = 0.99


def download_key(key: str) -> bytes:
    url = f"{S3_URL}/{quote(key, safe='/')}"
    last_error: Exception | str | None = None
    for attempt in range(6):
        try:
            response = requests.get(url, timeout=60)
            if response.status_code in (418, 429) or response.status_code >= 500:
                last_error = f"HTTP {response.status_code}"
                time.sleep(min(8.0, 0.5 * (2 ** attempt)))
                continue
            response.raise_for_status()
            return response.content
        except Exception as exc:
            last_error = exc
            time.sleep(min(8.0, 0.5 * (2 ** attempt)))
    raise RuntimeError(f"download failed {key}: {last_error!r}")


def timestamp_unit(values: pd.Series) -> str:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    if numeric.empty:
        return "ms"
    magnitude = float(numeric.abs().median())
    if magnitude >= 1e17:
        return "ns"
    if magnitude >= 1e14:
        return "us"
    if magnitude >= 1e11:
        return "ms"
    return "s"


def parse_kline_payload(payload: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]
        if len(names) != 1:
            raise RuntimeError(f"unexpected ZIP members: {names}")
        with archive.open(names[0]) as handle:
            raw = pd.read_csv(handle, header=None)
    if raw.empty or raw.shape[1] < 8:
        raise RuntimeError(f"unexpected kline shape: {raw.shape}")
    open_time = pd.to_numeric(raw.iloc[:, 0], errors="coerce")
    close = pd.to_numeric(raw.iloc[:, 4], errors="coerce")
    quote_volume = pd.to_numeric(raw.iloc[:, 7], errors="coerce")
    valid = open_time.notna() & close.notna() & quote_volume.notna()
    if not valid.any():
        raise RuntimeError("no numeric kline rows")
    unit = timestamp_unit(open_time.loc[valid])
    dates = pd.to_datetime(open_time.loc[valid].astype("int64"), unit=unit, utc=True).dt.tz_localize(None).dt.normalize()
    frame = pd.DataFrame(
        {
            "close": close.loc[valid].to_numpy(float),
            "quote_volume": quote_volume.loc[valid].to_numpy(float),
        },
        index=pd.DatetimeIndex(dates),
    )
    return frame[~frame.index.duplicated(keep="last")].sort_index()


def parse_funding_payload(payload: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]
        if len(names) != 1:
            raise RuntimeError(f"unexpected funding ZIP members: {names}")
        with archive.open(names[0]) as handle:
            frame = pd.read_csv(handle)
    columns = [str(column) for column in frame.columns]
    time_col = detect_column(columns, ("calc_time", "fundingTime", "funding_time", "time", "timestamp"), "time")
    rate_col = detect_column(columns, ("last_funding_rate", "fundingRate", "funding_rate"), "funding")
    if time_col is None or rate_col is None:
        raise RuntimeError(f"funding fields not found: {columns}")
    ts = parse_timestamp(frame[time_col])
    rate = pd.to_numeric(frame[rate_col], errors="coerce")
    valid = ts.notna() & rate.notna()
    out = pd.DataFrame({"timestamp": ts.loc[valid], "rate": rate.loc[valid].to_numpy(float)})
    return out.drop_duplicates(subset=["timestamp"], keep="last").sort_values("timestamp")


def list_month_objects(root: str, symbol: str, kind: str) -> list[dict[str, Any]]:
    if kind in {"spot", "perp"}:
        prefix = f"{root}{symbol}/1d/"
        pattern = re.compile(rf"/{re.escape(symbol)}-1d-(\d{{4}}-\d{{2}})\.zip$")
    elif kind == "funding":
        prefix = f"{root}{symbol}/"
        pattern = re.compile(rf"/{re.escape(symbol)}-fundingRate-(\d{{4}}-\d{{2}})\.zip$")
    else:
        raise ValueError(kind)
    _, items = s3_list(prefix)
    rows: list[dict[str, Any]] = []
    for item in items:
        match = pattern.search(item["key"])
        if match:
            rows.append({"month": match.group(1), "key": item["key"], "size": item.get("size")})
    return sorted(rows, key=lambda row: row["month"])


def month_gaps(months: list[str]) -> list[str]:
    if not months:
        return []
    periods = pd.PeriodIndex(months, freq="M")
    expected = pd.period_range(periods.min(), periods.max(), freq="M")
    return [str(period) for period in expected.difference(periods)]


def combine_klines(objects: list[dict[str, Any]], allowed_months: set[str]) -> pd.DataFrame:
    frames = []
    for row in objects:
        if row["month"] not in allowed_months:
            continue
        frames.append(parse_kline_payload(download_key(row["key"])))
    if not frames:
        return pd.DataFrame(columns=["close", "quote_volume"])
    out = pd.concat(frames).sort_index()
    return out[~out.index.duplicated(keep="last")]


def combine_funding(objects: list[dict[str, Any]], allowed_months: set[str]) -> pd.DataFrame:
    frames = []
    for row in objects:
        if row["month"] not in allowed_months:
            continue
        frames.append(parse_funding_payload(download_key(row["key"])))
    if not frames:
        return pd.DataFrame(columns=["timestamp", "rate"])
    return pd.concat(frames, ignore_index=True).drop_duplicates(subset=["timestamp"], keep="last").sort_values("timestamp")


def distribution(series: pd.Series) -> dict[str, float | None]:
    values = pd.to_numeric(series, errors="coerce").dropna().astype(float)
    if values.empty:
        return {"min": None, "p01": None, "p25": None, "median": None, "mean": None, "p75": None, "p99": None, "max": None}
    return {
        "min": float(values.min()),
        "p01": float(values.quantile(0.01)),
        "p25": float(values.quantile(0.25)),
        "median": float(values.median()),
        "mean": float(values.mean()),
        "p75": float(values.quantile(0.75)),
        "p99": float(values.quantile(0.99)),
        "max": float(values.max()),
    }


def audit_asset(symbol: str) -> dict[str, Any]:
    spot_objects = list_month_objects(SPOT_ROOT, symbol, "spot")
    perp_objects = list_month_objects(PERP_ROOT, symbol, "perp")
    funding_objects = list_month_objects(FUNDING_ROOT, symbol, "funding")
    spot_months = [row["month"] for row in spot_objects]
    perp_months = [row["month"] for row in perp_objects]
    funding_months = [row["month"] for row in funding_objects]
    common_months = sorted(set(spot_months) & set(perp_months) & set(funding_months))
    common_set = set(common_months)

    if not common_months:
        return {
            "symbol": symbol,
            "pass": False,
            "reason": "no common monthly spot/perp/funding coverage",
            "archive": {
                "spot": {"count": len(spot_months), "first": spot_months[0] if spot_months else None, "last": spot_months[-1] if spot_months else None, "internal_gaps": month_gaps(spot_months)},
                "perp": {"count": len(perp_months), "first": perp_months[0] if perp_months else None, "last": perp_months[-1] if perp_months else None, "internal_gaps": month_gaps(perp_months)},
                "funding": {"count": len(funding_months), "first": funding_months[0] if funding_months else None, "last": funding_months[-1] if funding_months else None, "internal_gaps": month_gaps(funding_months)},
            },
        }

    spot = combine_klines(spot_objects, common_set)
    perp = combine_klines(perp_objects, common_set)
    funding = combine_funding(funding_objects, common_set)

    spot_dates = pd.DatetimeIndex(spot.index)
    perp_dates = pd.DatetimeIndex(perp.index)
    shared_dates = spot_dates.intersection(perp_dates)
    denom = max(len(spot_dates), len(perp_dates), 1)
    alignment_ratio = float(len(shared_dates) / denom)

    aligned = pd.DataFrame({"spot": spot.reindex(shared_dates)["close"], "perp": perp.reindex(shared_dates)["close"]}).dropna()
    aligned["basis"] = aligned["perp"] / aligned["spot"] - 1.0

    if len(shared_dates):
        start = pd.Timestamp(shared_dates.min(), tz="UTC")
        end = pd.Timestamp(shared_dates.max() + pd.Timedelta(days=1), tz="UTC")
        funding_window = funding[(funding["timestamp"] >= start) & (funding["timestamp"] < end)].copy()
    else:
        funding_window = funding.iloc[0:0].copy()
    intervals = funding_window["timestamp"].diff().dt.total_seconds().div(3600.0).dropna() if len(funding_window) else pd.Series(dtype=float)
    rates = funding_window["rate"].astype(float) if len(funding_window) else pd.Series(dtype=float)

    passed = bool(len(aligned) > 0 and alignment_ratio >= MIN_ALIGNMENT and len(funding_window) > 0)
    return {
        "symbol": symbol,
        "pass": passed,
        "archive": {
            "spot": {"count": len(spot_months), "first": spot_months[0] if spot_months else None, "last": spot_months[-1] if spot_months else None, "internal_gap_count": len(month_gaps(spot_months)), "internal_gaps": month_gaps(spot_months)},
            "perp": {"count": len(perp_months), "first": perp_months[0] if perp_months else None, "last": perp_months[-1] if perp_months else None, "internal_gap_count": len(month_gaps(perp_months)), "internal_gaps": month_gaps(perp_months)},
            "funding": {"count": len(funding_months), "first": funding_months[0] if funding_months else None, "last": funding_months[-1] if funding_months else None, "internal_gap_count": len(month_gaps(funding_months)), "internal_gaps": month_gaps(funding_months)},
            "common_month_count": len(common_months),
            "common_first_month": common_months[0],
            "common_last_month": common_months[-1],
        },
        "daily_alignment": {
            "spot_days": int(len(spot_dates)),
            "perp_days": int(len(perp_dates)),
            "shared_days": int(len(shared_dates)),
            "ratio": alignment_ratio,
            "first_shared_day": str(shared_dates.min().date()) if len(shared_dates) else None,
            "last_shared_day": str(shared_dates.max().date()) if len(shared_dates) else None,
            "spot_only_days": [str(x.date()) for x in spot_dates.difference(perp_dates)[:20]],
            "perp_only_days": [str(x.date()) for x in perp_dates.difference(spot_dates)[:20]],
        },
        "basis": {
            "definition": "perp_close / spot_close - 1",
            "observations": int(len(aligned)),
            "distribution": distribution(aligned["basis"]),
        },
        "funding": {
            "event_count": int(len(funding_window)),
            "positive_events": int((rates > 0).sum()),
            "zero_events": int((rates == 0).sum()),
            "negative_events": int((rates < 0).sum()),
            "positive_event_share": float((rates > 0).mean()) if len(rates) else None,
            "rate_distribution": distribution(rates),
            "interval_hours": distribution(intervals),
            "first_event": str(funding_window["timestamp"].min()) if len(funding_window) else None,
            "last_event": str(funding_window["timestamp"].max()) if len(funding_window) else None,
        },
    }


def flatten_rows(results: list[dict[str, Any]]) -> pd.DataFrame:
    rows = []
    for result in results:
        archive = result.get("archive", {})
        alignment = result.get("daily_alignment", {})
        funding = result.get("funding", {})
        basis = result.get("basis", {})
        rows.append({
            "symbol": result["symbol"],
            "pass": result.get("pass"),
            "common_first_month": archive.get("common_first_month"),
            "common_last_month": archive.get("common_last_month"),
            "common_month_count": archive.get("common_month_count"),
            "daily_alignment_ratio": alignment.get("ratio"),
            "shared_days": alignment.get("shared_days"),
            "funding_event_count": funding.get("event_count"),
            "funding_positive_event_share": funding.get("positive_event_share"),
            "basis_median": basis.get("distribution", {}).get("median"),
            "basis_p01": basis.get("distribution", {}).get("p01"),
            "basis_p99": basis.get("distribution", {}).get("p99"),
        })
    return pd.DataFrame(rows)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(audit_asset, symbol): symbol for symbol in ASSETS}
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                result = future.result()
                results.append(result)
                print(f"resolved {symbol} pass={result.get('pass')}", flush=True)
            except Exception as exc:
                errors.append({"symbol": symbol, "error": repr(exc)})
                print(f"failed {symbol}: {exc!r}", flush=True)
    results.sort(key=lambda row: ASSETS.index(row["symbol"]))
    summary_table = flatten_rows(results)
    summary_table.to_csv(OUTPUT / "asset_coverage.csv", index=False)

    overall_pass = bool(len(results) == len(ASSETS) and not errors and all(bool(row.get("pass")) for row in results))
    report = {
        "audit_id": AUDIT_ID,
        "status": "PASS" if overall_pass else "FAIL",
        "strategy_pnl": False,
        "trading_changes": False,
        "sources": {
            "s3": S3_URL,
            "spot_root": SPOT_ROOT,
            "perp_root": PERP_ROOT,
            "funding_root": FUNDING_ROOT,
        },
        "assets": results,
        "errors": errors,
        "pass_rule": {
            "target_assets": len(ASSETS),
            "resolved_assets": len(results),
            "all_without_errors": not errors,
            "minimum_daily_spot_perp_alignment": MIN_ALIGNMENT,
            "all_assets_pass": overall_pass,
        },
        "interpretation": (
            "This is a data-only qualification for same-venue delta-neutral spot-perpetual carry. "
            "It reports archive coverage, daily spot/perp alignment, contemporaneous basis diagnostics, and funding-event structure. "
            "It does not define entry/exit rules, funding thresholds, leverage, or strategy PNL. PASS only authorizes a separately preregistered naive carry PNL experiment."
        ),
    }
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== CARRY_DATA_0030_REPORT ===")
    print(json.dumps({
        "audit_id": AUDIT_ID,
        "status": report["status"],
        "pass_rule": report["pass_rule"],
        "table": summary_table.to_dict(orient="records"),
        "errors": errors,
    }, indent=2))
    print("=== END ===")
    if not overall_pass:
        raise RuntimeError("CARRY-DATA-0030 failed data qualification; see persisted summary.json")


if __name__ == "__main__":
    main()
