from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import requests

HERE = Path(__file__).resolve().parent
AUDIT_ID = "TSMOM-DATA-0027-PIT-PERP-UNIVERSE"
S3_URL = "https://s3-ap-northeast-1.amazonaws.com/data.binance.vision"
KLINE_ROOT = "data/futures/um/monthly/klines/"
FUNDING_ROOT = "data/futures/um/monthly/fundingRate/"
CURRENT_ENDPOINTS = [
    "https://fapi.binance.com/fapi/v1/exchangeInfo",
    "https://fapi1.binance.com/fapi/v1/exchangeInfo",
    "https://fapi2.binance.com/fapi/v1/exchangeInfo",
]
STABLE_BASES = {"USDC", "BUSD", "TUSD", "FDUSD", "USDP", "DAI", "UST", "USTC", "PAX", "SUSD"}
LEVERAGED_SUFFIXES = ("UP", "DOWN", "BULL", "BEAR")


def s3_list(prefix: str, delimiter: str | None = None, max_keys: int = 1000) -> tuple[list[str], list[dict[str, Any]]]:
    items: list[dict[str, Any]] = []
    prefixes: list[str] = []
    token = None
    while True:
        params = {"list-type": "2", "prefix": prefix, "max-keys": str(max_keys)}
        if delimiter is not None:
            params["delimiter"] = delimiter
        if token:
            params["continuation-token"] = token
        response = requests.get(S3_URL, params=params, timeout=45)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        ns = "{http://s3.amazonaws.com/doc/2006-03-01/}"
        for cp in root.findall(f"{ns}CommonPrefixes"):
            el = cp.find(f"{ns}Prefix")
            if el is not None and el.text:
                prefixes.append(el.text)
        for content in root.findall(f"{ns}Contents"):
            key = content.find(f"{ns}Key")
            size = content.find(f"{ns}Size")
            if key is not None and key.text:
                items.append({"key": key.text, "size": int(size.text) if size is not None else None})
        truncated = root.find(f"{ns}IsTruncated")
        if truncated is None or truncated.text != "true":
            break
        nxt = root.find(f"{ns}NextContinuationToken")
        if nxt is None or not nxt.text:
            raise RuntimeError(f"S3 listing truncated without continuation token: {prefix}")
        token = nxt.text
    return sorted(set(prefixes)), items


def prefix_symbols(root_prefix: str) -> list[str]:
    prefixes, _ = s3_list(root_prefix, delimiter="/")
    return sorted({p[len(root_prefix):].strip("/") for p in prefixes if p.startswith(root_prefix) and p[len(root_prefix):].strip("/")})


def classify(symbol: str) -> str:
    if not symbol.endswith("USDT"):
        return "non_usdt"
    base = symbol[:-4]
    if base in STABLE_BASES:
        return "stable_base"
    if any(base.endswith(suffix) and len(base) > len(suffix) for suffix in LEVERAGED_SUFFIXES):
        return "leveraged_token_like"
    return "ordinary_usdt_candidate"


def dated_1d_files(symbol: str) -> dict[str, Any]:
    prefix = f"{KLINE_ROOT}{symbol}/1d/"
    _, items = s3_list(prefix)
    pattern = re.compile(rf"/{re.escape(symbol)}-1d-(\d{{4}}-\d{{2}})\.zip$")
    months = sorted({m.group(1) for item in items if (m := pattern.search(item["key"]))})
    return {
        "symbol": symbol,
        "monthly_1d_file_count": len(months),
        "first_month": months[0] if months else None,
        "last_month": months[-1] if months else None,
        "months": months,
    }


def current_perpetual_symbols() -> tuple[dict[str, dict[str, Any]], str | None, str | None]:
    errors = []
    for url in CURRENT_ENDPOINTS:
        try:
            response = requests.get(url, timeout=45)
            response.raise_for_status()
            data = response.json()
            rows = {}
            for row in data.get("symbols", []):
                if row.get("quoteAsset") != "USDT" or row.get("contractType") != "PERPETUAL":
                    continue
                rows[row["symbol"]] = {
                    "status": row.get("status"),
                    "baseAsset": row.get("baseAsset"),
                    "quoteAsset": row.get("quoteAsset"),
                    "contractType": row.get("contractType"),
                    "onboardDate": row.get("onboardDate"),
                    "deliveryDate": row.get("deliveryDate"),
                }
            return rows, url, None
        except Exception as exc:
            errors.append(f"{url}: {exc!r}")
    return {}, None, " | ".join(errors)


def month_number(value: str | None) -> int | None:
    if not value:
        return None
    year, month = map(int, value.split("-"))
    return year * 12 + month


def main() -> None:
    archive_symbols = prefix_symbols(KLINE_ROOT)
    funding_symbols = set(prefix_symbols(FUNDING_ROOT))
    archive_usdt = sorted(s for s in archive_symbols if s.endswith("USDT"))
    ordinary = sorted(s for s in archive_usdt if classify(s) == "ordinary_usdt_candidate")

    rows: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    with ThreadPoolExecutor(max_workers=20) as pool:
        futures = {pool.submit(dated_1d_files, symbol): symbol for symbol in ordinary}
        for i, future in enumerate(as_completed(futures), start=1):
            symbol = futures[future]
            try:
                row = future.result()
                row["has_funding_archive_prefix"] = symbol in funding_symbols
                rows.append(row)
            except Exception as exc:
                errors.append({"symbol": symbol, "error": repr(exc)})
            if i % 50 == 0:
                print("resolved", i, "of", len(futures), flush=True)
    rows = sorted(rows, key=lambda x: x["symbol"])

    valid_rows = [r for r in rows if r["monthly_1d_file_count"] > 0]
    latest_month = max((r["last_month"] for r in valid_rows if r["last_month"]), default=None)
    latest_n = month_number(latest_month)
    for row in rows:
        last_n = month_number(row.get("last_month"))
        row["months_behind_latest"] = (latest_n - last_n) if latest_n is not None and last_n is not None else None
        row["ended_at_least_2_months_before_latest"] = bool(row["months_behind_latest"] is not None and row["months_behind_latest"] >= 2)

    current, current_source, current_error = current_perpetual_symbols()
    current_set = set(current)
    archive_set = set(ordinary)
    archive_only = sorted(archive_set - current_set) if current else []
    common_current = sorted(archive_set & current_set) if current else []

    ended_early = sorted(r["symbol"] for r in rows if r["ended_at_least_2_months_before_latest"])
    confirmed_archive_only = sorted(set(archive_only) & set(ended_early)) if current else []
    funding_count = sum(bool(r["has_funding_archive_prefix"]) for r in rows)

    class_counts: dict[str, int] = {}
    for symbol in archive_usdt:
        c = classify(symbol)
        class_counts[c] = class_counts.get(c, 0) + 1

    output = HERE / "tsmom_data_0027_outputs"
    output.mkdir(parents=True, exist_ok=True)
    import csv
    fieldnames = [
        "symbol", "monthly_1d_file_count", "first_month", "last_month",
        "has_funding_archive_prefix", "months_behind_latest", "ended_at_least_2_months_before_latest"
    ]
    with (output / "historical_perp_contracts.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fieldnames})

    report = {
        "audit_id": AUDIT_ID,
        "trading_changes": False,
        "strategy_pnl": False,
        "sources": {
            "s3": S3_URL,
            "kline_root": KLINE_ROOT,
            "funding_root": FUNDING_ROOT,
            "current_exchangeinfo_source": current_source,
            "current_exchangeinfo_error": current_error,
        },
        "counts": {
            "archive_symbol_count_all_quotes": len(archive_symbols),
            "archive_usdt_symbol_count": len(archive_usdt),
            "ordinary_archive_usdt_candidates": len(ordinary),
            "ordinary_with_1d_archives": len(valid_rows),
            "ordinary_with_funding_archive_prefix": funding_count,
            "current_usdt_perpetual_count": len(current),
            "ordinary_common_with_current": len(common_current),
            "ordinary_archive_only_vs_current": len(archive_only),
            "ordinary_ended_at_least_2_months_before_latest": len(ended_early),
            "confirmed_archive_only_and_ended_early": len(confirmed_archive_only),
            "per_symbol_listing_errors": len(errors),
        },
        "latest_archive_month": latest_month,
        "archive_usdt_classification_counts": class_counts,
        "archive_only_symbols": archive_only,
        "ended_early_symbols": ended_early,
        "confirmed_archive_only_and_ended_early_symbols": confirmed_archive_only,
        "errors": errors,
        "sample_contracts": rows[:10] + rows[-10:] if len(rows) >= 20 else rows,
        "success_gate": {
            "archive_symbols_nonempty": len(archive_symbols) > 0,
            "ordinary_historical_candidates_nonempty": len(ordinary) > 0,
            "dated_1d_archives_resolvable": len(valid_rows) > 0 and len(errors) == 0,
            "historical_contracts_that_ended_before_latest_found": len(ended_early) > 0,
            "confirmed_archive_only_contracts_found_when_current_api_available": (len(confirmed_archive_only) > 0) if current else None,
        },
        "interpretation": "This audit establishes historical USD-M perpetual contract existence from official archive structure only. It does not yet define daily TSMOM eligibility, signal, risk sizing or PNL. A future point-in-time construction must use completed-day archive availability/age/liquidity and must not substitute current survivors."
    }
    (output / "summary.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("=== TSMOM_DATA_0027_REPORT ===")
    print(json.dumps({k: v for k, v in report.items() if k not in {"archive_only_symbols", "ended_early_symbols", "confirmed_archive_only_and_ended_early_symbols", "sample_contracts"}}, indent=2))
    print("archive_only_examples", archive_only[:30])
    print("ended_early_examples", ended_early[:30])
    print("=== END ===")


if __name__ == "__main__":
    main()
