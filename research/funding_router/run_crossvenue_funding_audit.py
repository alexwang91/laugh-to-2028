from __future__ import annotations

import json
import math
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parent
PIT = RESEARCH / "pit_universe"
for path in (HERE, RESEARCH, PIT):
    sys.path.insert(0, str(path))

from run_funding_data_audit import (
    HYPERLIQUID_INFO,
    parse_timestamp,
    parse_zip,
    symbol_months,
)

AUDIT_ID = "FUNDING-CROSSVENUE-0002-OVERLAP-AUDIT"
ASSETS = ("BTC", "ETH", "SOL", "BNB", "XRP")
SYMBOLS = {asset: f"{asset}USDT" for asset in ASSETS}
START = pd.Timestamp("2023-05-01 00:00:00", tz="UTC")
END = pd.Timestamp("2026-07-31 23:59:59.999", tz="UTC")
QUERY_DAYS = 14
OUTPUT = HERE / "funding_crossvenue_0002_outputs"
MAX_BINANCE_WORKERS = 8

LEVEL_MIN_BLOCKS = 500
LEVEL_MIN_PEARSON = 0.50
LEVEL_MIN_SPEARMAN = 0.50
LEVEL_MIN_SIGN = 0.65
LEVEL_MAX_BIAS_RATIO = 0.50
LEVEL_MIN_YEAR_SIGN = 0.55
REGIME_MIN_ASSETS = 4
REGIME_MIN_BLOCKS = 500
REGIME_MIN_SIGN = 0.55
REGIME_MIN_CORRELATION = 0.25


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


def load_one_binance_object(asset: str, row: dict) -> pd.DataFrame:
    frame, _ = parse_zip(row["key"])
    timestamp = parse_timestamp(frame["calc_time"])
    rate = pd.to_numeric(frame["last_funding_rate"], errors="coerce")
    interval = pd.to_numeric(frame.get("funding_interval_hours"), errors="coerce")
    out = pd.DataFrame({
        "asset": asset,
        "venue": "binance",
        "timestamp": timestamp,
        "rate": rate,
        "reported_interval_hours": interval,
    })
    return out.dropna(subset=["timestamp", "rate"])


def load_binance_events() -> tuple[pd.DataFrame, dict]:
    jobs = []
    coverage = {}
    for asset, symbol in SYMBOLS.items():
        months, objects = symbol_months(symbol)
        chosen = [
            row for row in objects
            if pd.Period(row["month"], freq="M")
            >= pd.Period(START.strftime("%Y-%m"), freq="M")
            and pd.Period(row["month"], freq="M")
            <= pd.Period(END.strftime("%Y-%m"), freq="M")
        ]
        coverage[asset] = {
            "symbol": symbol,
            "archive_months_total": len(months),
            "selected_months": len(chosen),
            "first_selected_month": chosen[0]["month"] if chosen else None,
            "last_selected_month": chosen[-1]["month"] if chosen else None,
        }
        jobs.extend((asset, row) for row in chosen)

    frames = []
    with ThreadPoolExecutor(max_workers=MAX_BINANCE_WORKERS) as executor:
        futures = {
            executor.submit(load_one_binance_object, asset, row): (asset, row["month"])
            for asset, row in jobs
        }
        completed = 0
        for future in as_completed(futures):
            asset, month = futures[future]
            frames.append(future.result())
            completed += 1
            if completed % 25 == 0 or completed == len(futures):
                print(f"binance_progress {completed}/{len(futures)}", flush=True)

    events = pd.concat(frames, ignore_index=True)
    events = events[(events["timestamp"] >= START) & (events["timestamp"] <= END)]
    events = events.drop_duplicates(["asset", "timestamp"], keep="last")
    return events.sort_values(["asset", "timestamp"]), coverage


def query_hyperliquid(asset: str, start: pd.Timestamp, end: pd.Timestamp) -> list[dict]:
    body = {
        "type": "fundingHistory",
        "coin": asset,
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
                raise RuntimeError(f"Unexpected payload {payload}")
            return payload
        except Exception as exc:
            last_error = repr(exc)
            time.sleep(min(15.0, 1.5 ** attempt))
    raise RuntimeError(f"Hyperliquid query failed {asset}: {last_error}")


def load_hyperliquid_events() -> tuple[pd.DataFrame, dict]:
    rows = []
    coverage = {}
    for asset in ASSETS:
        cursor = START
        calls = 0
        asset_rows = []
        while cursor <= END:
            block_end = min(cursor + pd.Timedelta(days=QUERY_DAYS) - pd.Timedelta(milliseconds=1), END)
            payload = query_hyperliquid(asset, cursor, block_end)
            asset_rows.extend(payload)
            calls += 1
            cursor = block_end + pd.Timedelta(milliseconds=1)
        frame = pd.DataFrame(asset_rows)
        if frame.empty:
            coverage[asset] = {"calls": calls, "events": 0, "first": None, "last": None}
            continue
        timestamp = parse_timestamp(frame["time"])
        rate = pd.to_numeric(frame["fundingRate"], errors="coerce")
        premium = pd.to_numeric(frame.get("premium"), errors="coerce")
        out = pd.DataFrame({
            "asset": asset,
            "venue": "hyperliquid",
            "timestamp": timestamp,
            "rate": rate,
            "premium": premium,
        }).dropna(subset=["timestamp", "rate"])
        out = out[(out["timestamp"] >= START) & (out["timestamp"] <= END)]
        out = out.drop_duplicates(["asset", "timestamp"], keep="last")
        rows.append(out)
        coverage[asset] = {
            "calls": calls,
            "events": int(len(out)),
            "first": str(out["timestamp"].min()) if len(out) else None,
            "last": str(out["timestamp"].max()) if len(out) else None,
        }
        print(f"hyperliquid_progress {asset} calls={calls} events={len(out)}", flush=True)
    events = pd.concat(rows, ignore_index=True)
    return events.sort_values(["asset", "timestamp"]), coverage


def compound_rates(series: pd.Series) -> float:
    values = pd.to_numeric(series, errors="coerce").dropna().to_numpy(float)
    return float(np.prod(1.0 + values) - 1.0) if len(values) else np.nan


def to_blocks(events: pd.DataFrame) -> pd.DataFrame:
    frame = events.copy()
    frame["block"] = frame["timestamp"].dt.floor("8h")
    grouped = frame.groupby(["asset", "venue", "block"], sort=True)
    blocks = grouped.agg(
        additive_rate=("rate", "sum"),
        event_count=("rate", "count"),
        first_event=("timestamp", "min"),
        last_event=("timestamp", "max"),
    ).reset_index()
    compounded = grouped["rate"].apply(compound_rates).rename("compounded_rate").reset_index()
    return blocks.merge(compounded, on=["asset", "venue", "block"], how="left")


def safe_corr(left: pd.Series, right: pd.Series, method: str) -> float | None:
    if len(left) < 3 or left.nunique() < 2 or right.nunique() < 2:
        return None
    value = left.corr(right, method=method)
    return float(value) if pd.notna(value) else None


def sign_agreement(left: pd.Series, right: pd.Series) -> float:
    return float((np.sign(left.to_numpy(float)) == np.sign(right.to_numpy(float))).mean())


def comparison_metrics(frame: pd.DataFrame) -> dict:
    b = frame["binance_additive"]
    h = frame["hyperliquid_additive"]
    difference = h - b
    mean_abs_hl = float(h.abs().mean())
    result = {
        "paired_blocks": int(len(frame)),
        "pearson": safe_corr(b, h, "pearson"),
        "spearman": safe_corr(b, h, "spearman"),
        "sign_agreement": sign_agreement(b, h),
        "mean_binance": float(b.mean()),
        "mean_hyperliquid": float(h.mean()),
        "mean_bias_hl_minus_binance": float(difference.mean()),
        "median_bias_hl_minus_binance": float(difference.median()),
        "mean_absolute_hyperliquid": mean_abs_hl,
        "absolute_mean_bias_ratio": (
            float(abs(difference.mean()) / mean_abs_hl) if mean_abs_hl > 0 else None
        ),
        "mae": float(difference.abs().mean()),
        "rmse": float(np.sqrt(np.mean(np.square(difference)))),
        "cumulative_additive_binance": float(b.sum()),
        "cumulative_additive_hyperliquid": float(h.sum()),
        "cumulative_additive_difference": float(difference.sum()),
        "cumulative_compounded_binance": float(np.prod(1.0 + frame["binance_compounded"]) - 1.0),
        "cumulative_compounded_hyperliquid": float(np.prod(1.0 + frame["hyperliquid_compounded"]) - 1.0),
        "mean_abs_additive_compound_difference_binance": float(
            (frame["binance_additive"] - frame["binance_compounded"]).abs().mean()
        ),
        "mean_abs_additive_compound_difference_hyperliquid": float(
            (frame["hyperliquid_additive"] - frame["hyperliquid_compounded"]).abs().mean()
        ),
    }
    return result


def build_paired(blocks: pd.DataFrame) -> pd.DataFrame:
    fields = ["additive_rate", "compounded_rate", "event_count"]
    wide = blocks.pivot(index=["asset", "block"], columns="venue", values=fields)
    wide.columns = [f"{venue}_{field}" for field, venue in wide.columns]
    wide = wide.reset_index()
    rename = {
        "binance_additive_rate": "binance_additive",
        "hyperliquid_additive_rate": "hyperliquid_additive",
        "binance_compounded_rate": "binance_compounded",
        "hyperliquid_compounded_rate": "hyperliquid_compounded",
        "binance_event_count": "binance_event_count",
        "hyperliquid_event_count": "hyperliquid_event_count",
    }
    wide = wide.rename(columns=rename)
    required = [
        "binance_additive", "hyperliquid_additive",
        "binance_compounded", "hyperliquid_compounded",
    ]
    return wide.dropna(subset=required).sort_values(["asset", "block"])


def classify(asset_metrics: dict, annual_metrics: dict) -> tuple[str, dict]:
    level_checks = {}
    for asset in ASSETS:
        metrics = asset_metrics[asset]
        years = [row for row in annual_metrics if row["asset"] == asset]
        minimum_year_sign = min((row["sign_agreement"] for row in years), default=0.0)
        level_checks[asset] = bool(
            metrics["paired_blocks"] >= LEVEL_MIN_BLOCKS
            and (metrics["pearson"] is not None and metrics["pearson"] >= LEVEL_MIN_PEARSON)
            and (metrics["spearman"] is not None and metrics["spearman"] >= LEVEL_MIN_SPEARMAN)
            and metrics["sign_agreement"] >= LEVEL_MIN_SIGN
            and (metrics["absolute_mean_bias_ratio"] is not None and metrics["absolute_mean_bias_ratio"] <= LEVEL_MAX_BIAS_RATIO)
            and minimum_year_sign >= LEVEL_MIN_YEAR_SIGN
        )
    if all(level_checks.values()):
        return "level_proxy", {"level_checks": level_checks, "regime_checks": {}}

    regime_checks = {}
    for asset in ASSETS:
        metrics = asset_metrics[asset]
        correlations = [value for value in (metrics["pearson"], metrics["spearman"]) if value is not None]
        regime_checks[asset] = bool(
            metrics["paired_blocks"] >= REGIME_MIN_BLOCKS
            and metrics["sign_agreement"] >= REGIME_MIN_SIGN
            and correlations
            and max(correlations) >= REGIME_MIN_CORRELATION
        )
    if sum(regime_checks.values()) >= REGIME_MIN_ASSETS:
        return "sign_regime_proxy", {"level_checks": level_checks, "regime_checks": regime_checks}
    return "stress_source_only", {"level_checks": level_checks, "regime_checks": regime_checks}


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    binance_events, binance_coverage = load_binance_events()
    hyperliquid_events, hyperliquid_coverage = load_hyperliquid_events()
    events = pd.concat([binance_events, hyperliquid_events], ignore_index=True)
    blocks = to_blocks(events)
    paired = build_paired(blocks)

    asset_metrics = {}
    annual_rows = []
    coverage_rows = []
    for asset in ASSETS:
        asset_blocks = blocks[blocks["asset"] == asset]
        pair = paired[paired["asset"] == asset].copy()
        if pair.empty:
            raise RuntimeError(f"No paired blocks for {asset}")
        asset_metrics[asset] = comparison_metrics(pair)
        for year, group in pair.groupby(pair["block"].dt.year):
            annual_rows.append({"asset": asset, "year": int(year), **comparison_metrics(group)})

        first = max(
            asset_blocks.loc[asset_blocks["venue"] == "binance", "block"].min(),
            asset_blocks.loc[asset_blocks["venue"] == "hyperliquid", "block"].min(),
        )
        last = min(
            asset_blocks.loc[asset_blocks["venue"] == "binance", "block"].max(),
            asset_blocks.loc[asset_blocks["venue"] == "hyperliquid", "block"].max(),
        )
        expected = len(pd.date_range(first, last, freq="8h")) if pd.notna(first) and pd.notna(last) else 0
        binance_count = int(asset_blocks[(asset_blocks["venue"] == "binance") & asset_blocks["block"].between(first, last)]["block"].nunique())
        hyperliquid_count = int(asset_blocks[(asset_blocks["venue"] == "hyperliquid") & asset_blocks["block"].between(first, last)]["block"].nunique())
        coverage_rows.append({
            "asset": asset,
            "common_first_block": str(first),
            "common_last_block": str(last),
            "expected_8h_blocks": expected,
            "binance_blocks": binance_count,
            "hyperliquid_blocks": hyperliquid_count,
            "paired_blocks": int(len(pair)),
            "binance_coverage_fraction": float(binance_count / expected) if expected else None,
            "hyperliquid_coverage_fraction": float(hyperliquid_count / expected) if expected else None,
            "paired_coverage_fraction": float(len(pair) / expected) if expected else None,
        })

    classification, classification_checks = classify(asset_metrics, annual_rows)
    hl_event_distribution = (
        blocks[blocks["venue"] == "hyperliquid"]
        .groupby(["asset", "event_count"]).size()
        .rename("block_count").reset_index()
    )

    report = {
        "audit_id": AUDIT_ID,
        "trading_changes": False,
        "window": {"start": str(START), "end": str(END)},
        "alignment": {
            "block": "UTC floor to eight hours",
            "primary": "arithmetic sum of event rates inside block",
            "secondary": "compound product of one plus event rate minus one",
            "interpolation": False,
        },
        "source_coverage": {
            "binance": binance_coverage,
            "hyperliquid": hyperliquid_coverage,
            "paired": coverage_rows,
        },
        "asset_metrics": asset_metrics,
        "annual_metrics": annual_rows,
        "hyperliquid_event_count_distribution": hl_event_distribution.to_dict(orient="records"),
        "proxy_classification": classification,
        "classification_checks": classification_checks,
        "decision_rule": "This classification cannot alter positions. A later frozen-holdings funding attribution must use Binance only in the role assigned here and must retain Hyperliquid native overlap results as a separate scenario.",
    }

    paired.to_csv(OUTPUT / "paired_8h_blocks.csv", index=False, float_format="%.12f")
    pd.DataFrame(coverage_rows).to_csv(OUTPUT / "coverage.csv", index=False)
    pd.DataFrame(annual_rows).to_csv(OUTPUT / "annual_metrics.csv", index=False, float_format="%.12f")
    hl_event_distribution.to_csv(OUTPUT / "hyperliquid_event_count_distribution.csv", index=False)
    binance_events.to_csv(OUTPUT / "binance_events.csv", index=False, float_format="%.12f")
    hyperliquid_events.to_csv(OUTPUT / "hyperliquid_events.csv", index=False, float_format="%.12f")
    (OUTPUT / "funding_crossvenue_0002_report.json").write_text(
        json.dumps(report, indent=2, default=json_value), encoding="utf-8"
    )

    print("=== FUNDING_CROSSVENUE_0002_REPORT ===")
    print(json.dumps(report, indent=2, default=json_value))
    print("=== END ===")


if __name__ == "__main__":
    main()
