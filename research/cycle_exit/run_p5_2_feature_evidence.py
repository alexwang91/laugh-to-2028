from __future__ import annotations

import argparse
import hashlib
import json
import math
import time
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd
import requests

import p5_1_event_taxonomy as taxonomy
import p5_2_features as features


ROOT = Path(__file__).resolve().parents[2]
P5_DIR = Path(__file__).resolve().parent
CONTRACT_PATH = P5_DIR / "p5_2_feature_contract.json"
TAXONOMY_PATH = P5_DIR / "p5_1_event_taxonomy.json"
RESULT_DIR = ROOT / "research" / "results" / "p5_2_feature_evidence"

API_BASES = [
    "https://data-api.binance.vision/api/v3/klines",
    "https://api.binance.com/api/v3/klines",
]
SYMBOL_TO_ASSET = {
    "BTCUSDT": "BTC",
    "ETHUSDT": "ETH",
    "SOLUSDT": "SOL",
    "BNBUSDT": "BNB",
    "XRPUSDT": "XRP",
}
INTERVAL_MS = {"1d": 86_400_000, "4h": 14_400_000}


class P52Error(RuntimeError):
    pass


def _git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


def _load_contract() -> dict:
    payload = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    if payload.get("contract_id") != "P5.2-FEATURE-FAMILIES-V1":
        raise P52Error("unexpected P5.2 contract id")
    if payload.get("status") != "FROZEN_BEFORE_FIRST_FEATURE_EVIDENCE_RUN":
        raise P52Error("P5.2 contract is not frozen")
    if payload["research_integrity"].get("production_authorization") != "NONE":
        raise P52Error("P5.2 cannot authorize production")
    if not payload["run_once"].get("authorized_under_standing_research_authorization"):
        raise P52Error("one-time research run is not authorized")
    taxonomy_bytes = TAXONOMY_PATH.read_bytes()
    if _git_blob_sha(taxonomy_bytes) != payload.get("taxonomy_blob_sha"):
        raise P52Error("P5.1 taxonomy blob does not match frozen P5.2 contract")
    taxonomy.load_taxonomy(TAXONOMY_PATH)
    fmap = features.family_map(payload)
    if set(fmap) != set(features.AVAILABLE_FEATURES):
        raise P52Error("available feature list differs from frozen contract")
    return payload


def _utc_ms(day: str) -> int:
    return int(pd.Timestamp(day, tz="UTC").timestamp() * 1000)


def _fetch_klines(symbol: str, interval: str, start: str, end_exclusive: str) -> pd.DataFrame:
    if interval not in INTERVAL_MS:
        raise P52Error(f"unsupported interval: {interval}")
    cursor = _utc_ms(start)
    end_ms = _utc_ms(end_exclusive)
    rows: list[list] = []
    last_error: Exception | None = None
    while cursor < end_ms:
        payload = None
        for base in API_BASES:
            try:
                response = requests.get(
                    base,
                    params={
                        "symbol": symbol,
                        "interval": interval,
                        "startTime": cursor,
                        "endTime": end_ms - 1,
                        "limit": 1000,
                    },
                    timeout=30,
                )
                response.raise_for_status()
                payload = response.json()
                break
            except Exception as exc:  # pragma: no cover - network path
                last_error = exc
                time.sleep(0.5)
        if payload is None:
            raise P52Error(f"could not fetch {symbol} {interval}: {last_error}")
        if not payload:
            break
        rows.extend(payload)
        nxt = int(payload[-1][0]) + INTERVAL_MS[interval]
        if nxt <= cursor:
            raise P52Error(f"non-advancing Binance cursor for {symbol} {interval}")
        cursor = nxt
        time.sleep(0.05)

    if not rows:
        raise P52Error(f"no Binance rows for {symbol} {interval}")
    frame = pd.DataFrame(
        rows,
        columns=[
            "open_time",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "close_time",
            "quote_volume",
            "trades",
            "taker_base",
            "taker_quote",
            "ignore",
        ],
    )
    frame = frame.drop_duplicates("open_time").sort_values("open_time")
    frame["close"] = frame["close"].astype(float)
    return frame


def _fetch_daily_panel(contract: dict) -> pd.DataFrame:
    cfg = contract["canonical_price_data"]
    start = cfg["fetch_start"]
    end = cfg["fetch_end"]
    end_exclusive = (pd.Timestamp(end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    series: dict[str, pd.Series] = {}
    for symbol in cfg["daily_symbols"]:
        frame = _fetch_klines(symbol, "1d", start, end_exclusive)
        idx = pd.to_datetime(frame["open_time"], unit="ms", utc=True).dt.tz_localize(None)
        s = pd.Series(frame["close"].to_numpy(), index=idx, name=SYMBOL_TO_ASSET[symbol])
        series[SYMBOL_TO_ASSET[symbol]] = s
    panel = pd.concat(series.values(), axis=1).loc[:, list(features.DAILY_ASSETS)]
    expected = pd.date_range(start, end, freq="D")
    panel = panel.reindex(expected)
    if panel.isna().any().any():
        missing = panel.isna().sum().to_dict()
        raise P52Error(f"missing canonical daily price data: {missing}")
    return panel.astype(float)


def _fetch_btc_4h(contract: dict) -> pd.Series:
    cfg = contract["canonical_price_data"]
    start = cfg["fetch_start"]
    # Need the bar completing at 2025-12-31 00:00, not bars opening afterward.
    end_boundary = pd.Timestamp(cfg["fetch_end"])
    end_exclusive = (end_boundary + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    frame = _fetch_klines("BTCUSDT", "4h", start, end_exclusive)
    open_idx = pd.to_datetime(frame["open_time"], unit="ms", utc=True).dt.tz_localize(None)
    completion_idx = open_idx + pd.Timedelta(hours=4)
    s = pd.Series(frame["close"].to_numpy(), index=completion_idx, name="BTC_4H_CLOSE")
    s = s[~s.index.duplicated(keep="first")].sort_index()
    s = s.loc[:end_boundary]
    expected = pd.date_range(pd.Timestamp(start) + pd.Timedelta(hours=4), end_boundary, freq="4h")
    s = s.reindex(expected)
    if s.isna().any():
        raise P52Error(f"missing BTC 4h completed bars: {int(s.isna().sum())}")
    return s.astype(float)


def _preflight(contract: dict) -> None:
    # Connectivity/schema check only. Avoid required event windows and do not
    # calculate P5.2 features during preflight.
    for symbol in contract["canonical_price_data"]["daily_symbols"]:
        sample = _fetch_klines(symbol, "1d", "2020-10-01", "2020-10-04")
        if len(sample) < 2:
            raise P52Error(f"insufficient Binance preflight rows for {symbol}")
    sample4h = _fetch_klines("BTCUSDT", "4h", "2020-10-01", "2020-10-03")
    if len(sample4h) < 6:
        raise P52Error("insufficient BTC 4h preflight rows")
    if RESULT_DIR.exists():
        raise P52Error("P5.2 result directory already exists during preflight")
    print("P5.2 blinded data-access preflight PASS")


def _bucket_dates(anchor: pd.Timestamp, bounds: list[int]) -> tuple[pd.Timestamp, pd.Timestamp]:
    return anchor + pd.Timedelta(days=bounds[0]), anchor + pd.Timedelta(days=bounds[1])


def _event_bucket_observations(
    panel: pd.DataFrame, event: taxonomy.ResolvedEvent, bucket_bounds: list[int]
) -> pd.DataFrame:
    anchor = pd.Timestamp(event.anchor_date)
    start, end = _bucket_dates(anchor, bucket_bounds)
    return panel.loc[start:end]


def _mad(values: pd.Series) -> float:
    clean = values.dropna().astype(float)
    if clean.empty:
        return float("nan")
    med = float(clean.median())
    return float((clean - med).abs().median())


def _summary_rows(
    feature_panel: pd.DataFrame,
    resolved: list[taxonomy.ResolvedEvent],
    taxonomy_payload: dict,
    contract: dict,
) -> pd.DataFrame:
    fmap = features.family_map(contract)
    bucket_defs = taxonomy_payload["evaluation_buckets_relative_to_anchor_calendar_days"]

    controls = [e for e in resolved if e.event_class == "HIGH_VOLATILITY_NON_TOP_CONTROL"]
    control_stats: dict[tuple[str, str], tuple[float, float]] = {}
    for bucket, bounds in bucket_defs.items():
        for feature in feature_panel.columns:
            chunks = [
                _event_bucket_observations(feature_panel[[feature]], event, bounds)[feature]
                for event in controls
            ]
            pooled = pd.concat(chunks).dropna() if chunks else pd.Series(dtype=float)
            control_stats[(bucket, feature)] = (
                float(pooled.median()) if len(pooled) else float("nan"),
                _mad(pooled),
            )

    rows: list[dict] = []
    for event in resolved:
        for bucket, bounds in bucket_defs.items():
            observations = _event_bucket_observations(feature_panel, event, bounds)
            for feature in feature_panel.columns:
                values = observations[feature].dropna().astype(float)
                control_median, control_mad = control_stats[(bucket, feature)]
                median = float(values.median()) if len(values) else float("nan")
                robust_z = float("nan")
                if np.isfinite(control_mad) and control_mad > 0 and np.isfinite(median):
                    robust_z = (median - control_median) / (1.4826 * control_mad)
                rows.append(
                    {
                        "event_id": event.event_id,
                        "event_class": event.event_class,
                        "terminal_label": event.terminal_label,
                        "anchor_date": event.anchor_date.isoformat(),
                        "bucket": bucket,
                        "feature": feature,
                        "family": fmap[feature],
                        "count": int(len(values)),
                        "mean": float(values.mean()) if len(values) else float("nan"),
                        "median": median,
                        "min": float(values.min()) if len(values) else float("nan"),
                        "max": float(values.max()) if len(values) else float("nan"),
                        "first": float(values.iloc[0]) if len(values) else float("nan"),
                        "last": float(values.iloc[-1]) if len(values) else float("nan"),
                        "delta_last_minus_first": float(values.iloc[-1] - values.iloc[0]) if len(values) else float("nan"),
                        "control_median": control_median,
                        "control_mad": control_mad,
                        "robust_z_vs_controls": robust_z,
                    }
                )
    return pd.DataFrame(rows)


def _coverage_rows(
    feature_panel: pd.DataFrame,
    resolved: list[taxonomy.ResolvedEvent],
    taxonomy_payload: dict,
    contract: dict,
) -> pd.DataFrame:
    fmap = features.family_map(contract)
    bucket_defs = taxonomy_payload["evaluation_buckets_relative_to_anchor_calendar_days"]
    index_parts: list[pd.DatetimeIndex] = []
    for event in resolved:
        anchor = pd.Timestamp(event.anchor_date)
        for bounds in bucket_defs.values():
            start, end = _bucket_dates(anchor, bounds)
            index_parts.append(pd.date_range(start, end, freq="D"))
    required_index = pd.DatetimeIndex(sorted(set().union(*[set(idx) for idx in index_parts])))
    observed = feature_panel.reindex(required_index)
    threshold = float(contract["coverage_rule"]["available_feature_min_nonmissing_fraction"])
    rows = []
    for feature in feature_panel.columns:
        fraction = float(observed[feature].notna().mean())
        rows.append(
            {
                "feature": feature,
                "family": fmap[feature],
                "nonmissing_fraction": fraction,
                "status": "PASS" if fraction >= threshold else "COVERAGE_FAIL",
            }
        )
    return pd.DataFrame(rows)


def _pending_rows(contract: dict) -> pd.DataFrame:
    rows: list[dict] = []
    for family, payload in contract["feature_families"].items():
        for item in payload.get("pending", []):
            rows.append(
                {
                    "family": family,
                    "feature": item["id"],
                    "status": item["status"],
                    "reason": item["reason"],
                }
            )
    return pd.DataFrame(rows)


def _write_csv(frame: pd.DataFrame, path: Path, *, index: bool = False) -> str:
    frame.to_csv(path, index=index, lineterminator="\n", float_format="%.12g")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_results(contract: dict) -> dict:
    taxonomy_payload = taxonomy.load_taxonomy(TAXONOMY_PATH)
    daily = _fetch_daily_panel(contract)
    btc4h = _fetch_btc_4h(contract)
    resolved = taxonomy.resolve_event_anchors(
        taxonomy_payload,
        {idx.date(): float(value) for idx, value in daily["BTC"].items()},
    )
    feature_panel = features.build_feature_panel(daily, btc4h)
    summary_rows = _summary_rows(feature_panel, resolved, taxonomy_payload, contract)
    coverage = _coverage_rows(feature_panel, resolved, taxonomy_payload, contract)
    pending = _pending_rows(contract)

    failed_coverage = coverage.loc[coverage["status"] != "PASS", "feature"].tolist()
    if failed_coverage:
        raise P52Error(f"frozen AVAILABLE_V1 feature coverage failed: {failed_coverage}")

    if RESULT_DIR.exists():
        raise P52Error("P5.2 result directory already exists")
    RESULT_DIR.mkdir(parents=True)

    hashes: dict[str, str] = {}
    hashes["daily_close_panel.csv"] = _write_csv(daily.reset_index(names="date"), RESULT_DIR / "daily_close_panel.csv")
    hashes["btc_4h_close.csv"] = _write_csv(btc4h.rename("close").reset_index(names="completion_boundary"), RESULT_DIR / "btc_4h_close.csv")
    hashes["feature_panel.csv"] = _write_csv(feature_panel.reset_index(names="date"), RESULT_DIR / "feature_panel.csv")

    resolved_frame = pd.DataFrame(
        [
            {
                "event_id": event.event_id,
                "event_class": event.event_class,
                "terminal_label": event.terminal_label,
                "anchor_date": event.anchor_date.isoformat(),
                "search_window_start": event.search_window_start.isoformat(),
                "search_window_end": event.search_window_end.isoformat(),
                "outcome_window_end": event.outcome_window_end.isoformat(),
            }
            for event in resolved
        ]
    )
    hashes["resolved_events.csv"] = _write_csv(resolved_frame, RESULT_DIR / "resolved_events.csv")
    hashes["event_feature_summary.csv"] = _write_csv(summary_rows, RESULT_DIR / "event_feature_summary.csv")
    hashes["feature_coverage.csv"] = _write_csv(coverage, RESULT_DIR / "feature_coverage.csv")
    hashes["pending_features.csv"] = _write_csv(pending, RESULT_DIR / "pending_features.csv")

    family_counts = summary_rows.groupby("family")["feature"].nunique().to_dict()
    payload = {
        "study_id": "P5.2-FEATURE-FAMILIES-V1",
        "status": "ONE_TIME_FROZEN_FEATURE_EVIDENCE_COMPLETE",
        "production_authorized": False,
        "taxonomy_contract": taxonomy_payload["contract_id"],
        "taxonomy_blob_sha": contract["taxonomy_blob_sha"],
        "feature_contract": contract["contract_id"],
        "data_window": [contract["canonical_price_data"]["fetch_start"], contract["canonical_price_data"]["fetch_end"]],
        "available_feature_count": int(len(feature_panel.columns)),
        "family_feature_counts": {str(k): int(v) for k, v in family_counts.items()},
        "resolved_event_count": int(len(resolved)),
        "control_event_count": int(sum(e.event_class == "HIGH_VOLATILITY_NON_TOP_CONTROL" for e in resolved)),
        "coverage_all_pass": bool((coverage["status"] == "PASS").all()),
        "pending_feature_count": int(len(pending)),
        "selection": {
            "feature_set_selected": False,
            "state_thresholds_selected": False,
            "status": "DESCRIPTIVE_EVIDENCE_ONLY"
        },
        "artifact_sha256": hashes,
    }
    summary_path = RESULT_DIR / "summary.json"
    summary_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    digest = hashlib.sha256(summary_path.read_bytes()).hexdigest()
    (RESULT_DIR / "summary.sha256").write_text(digest + "\n", encoding="utf-8")
    print(f"P5.2 feature evidence complete summary_sha256={digest}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preflight-only", action="store_true")
    args = parser.parse_args()
    contract = _load_contract()
    if args.preflight_only:
        _preflight(contract)
        return
    _write_results(contract)


if __name__ == "__main__":
    main()
