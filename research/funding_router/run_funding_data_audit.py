from __future__ import annotations

import io
import json
import re
import sys
import time
import zipfile
from pathlib import Path
from urllib.parse import quote

import numpy as np
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
ROOT = RESEARCH.parent
PIT = RESEARCH / "pit_universe"
for path in (HERE, RESEARCH, PIT):
    sys.path.insert(0, str(path))

from run_archive_discovery import S3_URL, s3_list

AUDIT_ID = "FUNDING-DATA-0001-SOURCE-AUDIT"
BINANCE_PREFIX = "data/futures/um/monthly/fundingRate/"
BINANCE_SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT", "BNBUSDT", "XRPUSDT")
HYPERLIQUID_COINS = ("BTC", "ETH", "SOL", "BNB", "XRP")
HYPERLIQUID_INFO = "https://api.hyperliquid.xyz/info"
RECENT_START = pd.Timestamp("2026-07-25", tz="UTC")
RECENT_END = pd.Timestamp("2026-08-03 23:59:59.999", tz="UTC")
EARLY_START = pd.Timestamp("2023-05-01", tz="UTC")
EARLY_END = pd.Timestamp("2023-06-01", tz="UTC")
OUTPUT = HERE / "funding_data_0001_outputs"


def json_value(value):
    if value is None:
        return None
    if isinstance(value, (pd.Timestamp, pd.Period)):
        return str(value)
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def records(frame: pd.DataFrame, limit: int = 5) -> list[dict]:
    rows = []
    for row in frame.head(limit).to_dict(orient="records"):
        rows.append({str(key): json_value(value) for key, value in row.items()})
    return rows


def archive_symbols() -> list[str]:
    prefixes, _ = s3_list(BINANCE_PREFIX, delimiter="/")
    symbols = []
    for prefix in prefixes:
        symbol = prefix[len(BINANCE_PREFIX):].strip("/")
        if symbol:
            symbols.append(symbol)
    return sorted(set(symbols))


def symbol_months(symbol: str) -> tuple[list[str], list[dict]]:
    prefix = f"{BINANCE_PREFIX}{symbol}/"
    _, items = s3_list(prefix)
    pattern = re.compile(
        rf"/{re.escape(symbol)}-fundingRate-(\d{{4}}-\d{{2}})\.zip$"
    )
    rows = []
    for item in items:
        match = pattern.search(item["key"])
        if match:
            rows.append({
                "symbol": symbol,
                "month": match.group(1),
                "key": item["key"],
                "size": item.get("size"),
            })
    rows.sort(key=lambda row: row["month"])
    return [row["month"] for row in rows], rows


def download_key(key: str) -> bytes:
    url = f"{S3_URL}/{quote(key, safe='/')}"
    last_error = None
    for attempt in range(6):
        try:
            response = requests.get(url, timeout=60)
            if response.status_code in (418, 429) or response.status_code >= 500:
                last_error = f"HTTP {response.status_code}: {response.text[:160]}"
                time.sleep(min(15.0, 1.5 ** attempt))
                continue
            response.raise_for_status()
            return response.content
        except Exception as exc:
            last_error = repr(exc)
            time.sleep(min(15.0, 1.5 ** attempt))
    raise RuntimeError(f"Failed to download {key}: {last_error}")


def parse_zip(key: str) -> tuple[pd.DataFrame, dict]:
    payload = download_key(key)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]
        if len(names) != 1:
            raise RuntimeError(f"Unexpected ZIP members for {key}: {names}")
        member = names[0]
        with archive.open(member) as handle:
            frame = pd.read_csv(handle)
    return frame, {
        "key": key,
        "zip_bytes": len(payload),
        "member": member,
        "columns": [str(column) for column in frame.columns],
        "rows": int(len(frame)),
    }


def detect_column(columns: list[str], candidates: tuple[str, ...], contains: str) -> str | None:
    normalized = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate.lower() in normalized:
            return normalized[candidate.lower()]
    for column in columns:
        if contains in column.lower():
            return column
    return None


def parse_timestamp(series: pd.Series) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().mean() >= 0.90:
        magnitude = float(numeric.dropna().abs().median()) if numeric.notna().any() else 0.0
        if magnitude >= 1e17:
            unit = "ns"
        elif magnitude >= 1e14:
            unit = "us"
        elif magnitude >= 1e11:
            unit = "ms"
        else:
            unit = "s"
        return pd.to_datetime(numeric, unit=unit, utc=True, errors="coerce")
    return pd.to_datetime(series, utc=True, errors="coerce")


def sample_diagnostics(frame: pd.DataFrame, metadata: dict) -> dict:
    columns = [str(column) for column in frame.columns]
    time_column = detect_column(
        columns,
        ("calc_time", "fundingTime", "funding_time", "time", "timestamp"),
        "time",
    )
    rate_column = detect_column(
        columns,
        ("last_funding_rate", "fundingRate", "funding_rate"),
        "funding",
    )
    if time_column is None or rate_column is None:
        raise RuntimeError(
            f"Could not identify funding fields in {metadata['key']}: {columns}"
        )
    timestamp = parse_timestamp(frame[time_column])
    rate = pd.to_numeric(frame[rate_column], errors="coerce")
    valid_time = timestamp.dropna().sort_values()
    intervals = valid_time.diff().dt.total_seconds().div(3600.0).dropna()
    result = dict(metadata)
    result.update({
        "time_column": time_column,
        "rate_column": rate_column,
        "first_timestamp": str(valid_time.iloc[0]) if len(valid_time) else None,
        "last_timestamp": str(valid_time.iloc[-1]) if len(valid_time) else None,
        "median_interval_hours": float(intervals.median()) if len(intervals) else None,
        "minimum_interval_hours": float(intervals.min()) if len(intervals) else None,
        "maximum_interval_hours": float(intervals.max()) if len(intervals) else None,
        "valid_rate_rows": int(rate.notna().sum()),
        "positive_rate_rows": int((rate > 0).sum()),
        "zero_rate_rows": int((rate == 0).sum()),
        "negative_rate_rows": int((rate < 0).sum()),
        "mean_rate_per_event": float(rate.mean()) if rate.notna().any() else None,
        "median_rate_per_event": float(rate.median()) if rate.notna().any() else None,
        "minimum_rate": float(rate.min()) if rate.notna().any() else None,
        "maximum_rate": float(rate.max()) if rate.notna().any() else None,
        "sample_rows": records(frame),
    })
    return result


def month_gaps(months: list[str]) -> list[str]:
    if not months:
        return []
    periods = pd.PeriodIndex(months, freq="M")
    expected = pd.period_range(periods.min(), periods.max(), freq="M")
    return [str(period) for period in expected.difference(periods)]


def binance_audit() -> tuple[dict, pd.DataFrame, pd.DataFrame]:
    available_symbols = archive_symbols()
    coverage_rows = []
    sample_rows = []
    for symbol in BINANCE_SYMBOLS:
        months, objects = symbol_months(symbol)
        gaps = month_gaps(months)
        coverage_rows.append({
            "symbol": symbol,
            "present_in_archive_root": symbol in available_symbols,
            "month_count": len(months),
            "first_month": months[0] if months else None,
            "last_month": months[-1] if months else None,
            "internal_gap_count": len(gaps),
            "internal_gaps": ",".join(gaps),
        })
        if not objects:
            continue
        positions = sorted(set([0, len(objects) // 2, len(objects) - 1]))
        for position in positions:
            row = objects[position]
            frame, metadata = parse_zip(row["key"])
            diagnostic = sample_diagnostics(frame, metadata)
            diagnostic.update({"symbol": symbol, "month": row["month"]})
            sample_rows.append(diagnostic)

    coverage = pd.DataFrame(coverage_rows)
    samples = pd.DataFrame(sample_rows)
    report = {
        "archive_root_prefix": BINANCE_PREFIX,
        "archive_symbol_count": len(available_symbols),
        "target_symbol_count": len(BINANCE_SYMBOLS),
        "all_targets_present": bool(coverage["present_in_archive_root"].all()),
        "all_targets_have_months": bool((coverage["month_count"] > 0).all()),
        "total_internal_missing_months": int(coverage["internal_gap_count"].sum()),
        "coverage": coverage.to_dict(orient="records"),
        "samples": sample_rows,
    }
    return report, coverage, samples


def hyperliquid_history(coin: str, start: pd.Timestamp, end: pd.Timestamp) -> list[dict]:
    body = {
        "type": "fundingHistory",
        "coin": coin,
        "startTime": int(start.timestamp() * 1000),
        "endTime": int(end.timestamp() * 1000),
    }
    last_error = None
    for attempt in range(6):
        try:
            response = requests.post(HYPERLIQUID_INFO, json=body, timeout=45)
            if response.status_code == 429 or response.status_code >= 500:
                last_error = f"HTTP {response.status_code}: {response.text[:160]}"
                time.sleep(min(15.0, 1.5 ** attempt))
                continue
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list):
                raise RuntimeError(f"Unexpected Hyperliquid payload: {payload}")
            return payload
        except Exception as exc:
            last_error = repr(exc)
            time.sleep(min(15.0, 1.5 ** attempt))
    raise RuntimeError(f"Hyperliquid fundingHistory failed for {coin}: {last_error}")


def hyperliquid_diagnostics(coin: str, label: str, rows: list[dict]) -> dict:
    frame = pd.DataFrame(rows)
    result = {
        "coin": coin,
        "window": label,
        "rows": int(len(frame)),
        "columns": [str(column) for column in frame.columns],
        "sample_rows": records(frame),
    }
    if frame.empty:
        result.update({
            "first_timestamp": None,
            "last_timestamp": None,
            "median_interval_hours": None,
            "positive_rate_rows": 0,
            "zero_rate_rows": 0,
            "negative_rate_rows": 0,
        })
        return result
    time_column = detect_column(
        [str(column) for column in frame.columns],
        ("time", "fundingTime", "funding_time"),
        "time",
    )
    rate_column = detect_column(
        [str(column) for column in frame.columns],
        ("fundingRate", "funding_rate", "rate"),
        "funding",
    )
    if time_column is None or rate_column is None:
        raise RuntimeError(
            f"Could not identify Hyperliquid fields for {coin}/{label}: {frame.columns.tolist()}"
        )
    timestamp = parse_timestamp(frame[time_column])
    rate = pd.to_numeric(frame[rate_column], errors="coerce")
    valid_time = timestamp.dropna().sort_values()
    intervals = valid_time.diff().dt.total_seconds().div(3600.0).dropna()
    result.update({
        "time_column": time_column,
        "rate_column": rate_column,
        "first_timestamp": str(valid_time.iloc[0]) if len(valid_time) else None,
        "last_timestamp": str(valid_time.iloc[-1]) if len(valid_time) else None,
        "median_interval_hours": float(intervals.median()) if len(intervals) else None,
        "minimum_interval_hours": float(intervals.min()) if len(intervals) else None,
        "maximum_interval_hours": float(intervals.max()) if len(intervals) else None,
        "positive_rate_rows": int((rate > 0).sum()),
        "zero_rate_rows": int((rate == 0).sum()),
        "negative_rate_rows": int((rate < 0).sum()),
        "mean_rate_per_event": float(rate.mean()) if rate.notna().any() else None,
        "minimum_rate": float(rate.min()) if rate.notna().any() else None,
        "maximum_rate": float(rate.max()) if rate.notna().any() else None,
    })
    return result


def hyperliquid_audit() -> tuple[dict, pd.DataFrame]:
    diagnostics = []
    for coin in HYPERLIQUID_COINS:
        early = hyperliquid_history(coin, EARLY_START, EARLY_END)
        diagnostics.append(hyperliquid_diagnostics(coin, "early", early))
        recent = hyperliquid_history(coin, RECENT_START, RECENT_END)
        diagnostics.append(hyperliquid_diagnostics(coin, "recent", recent))
    frame = pd.DataFrame(diagnostics)
    recent = frame[frame["window"] == "recent"]
    report = {
        "endpoint": HYPERLIQUID_INFO,
        "request_type": "fundingHistory",
        "early_probe": [str(EARLY_START), str(EARLY_END)],
        "recent_probe": [str(RECENT_START), str(RECENT_END)],
        "all_recent_targets_parseable": bool((recent["rows"] > 0).all()),
        "diagnostics": diagnostics,
    }
    return report, frame


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    binance, coverage, binance_samples = binance_audit()
    hyperliquid, hyperliquid_rows = hyperliquid_audit()

    success = {
        "binance_all_targets_present": bool(binance["all_targets_present"]),
        "binance_all_targets_have_parseable_samples": bool(
            set(binance_samples["symbol"]) == set(BINANCE_SYMBOLS)
        ),
        "hyperliquid_all_recent_targets_parseable": bool(
            hyperliquid["all_recent_targets_parseable"]
        ),
    }
    report = {
        "audit_id": AUDIT_ID,
        "trading_changes": False,
        "binance": binance,
        "hyperliquid": hyperliquid,
        "success": success,
        "decision_rule": "No PNL or routing rule is authorized by this audit. A later experiment may use Binance as a clearly labeled long-history proxy and Hyperliquid as the native venue source only after coverage, sign and interval evidence are reviewed.",
    }

    coverage.to_csv(OUTPUT / "binance_monthly_coverage.csv", index=False)
    binance_samples.to_json(
        OUTPUT / "binance_sample_diagnostics.json", orient="records", indent=2
    )
    hyperliquid_rows.to_json(
        OUTPUT / "hyperliquid_probe_diagnostics.json", orient="records", indent=2
    )
    (OUTPUT / "funding_data_0001_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    print("=== FUNDING_DATA_0001_REPORT ===")
    print(json.dumps(report, indent=2))
    print("=== END ===")


if __name__ == "__main__":
    main()
