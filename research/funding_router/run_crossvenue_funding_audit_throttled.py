"""Rate-limit-safe runner for the frozen FUNDING-CROSSVENUE-0002 audit.

This wrapper changes no source, date, query-window, alignment, metric or proxy
classification rule. It only replaces HTTP retry pacing after the first valid
run reached Hyperliquid's 429 limit while downloading the preregistered sample.
"""

from __future__ import annotations

import time

import pandas as pd
import requests

import run_crossvenue_funding_audit as audit

SUCCESS_DELAY_SECONDS = 0.35
BETWEEN_ASSET_DELAY_SECONDS = 3.0
MAX_ATTEMPTS = 8
ORIGINAL_LOAD_HYPERLIQUID_EVENTS = audit.load_hyperliquid_events


def rate_limit_safe_query(asset, start, end):
    body = {
        "type": "fundingHistory",
        "coin": asset,
        "startTime": int(start.timestamp() * 1000),
        "endTime": int(end.timestamp() * 1000),
    }
    last_error = None
    for attempt in range(MAX_ATTEMPTS):
        try:
            response = requests.post(audit.HYPERLIQUID_INFO, json=body, timeout=45)
            if response.status_code == 429:
                retry_header = response.headers.get("Retry-After")
                header_delay = float(retry_header) if retry_header else 0.0
                delay = max(header_delay, min(120.0, 10.0 * (2 ** attempt)))
                last_error = f"HTTP 429: {response.text[:160]}; retry in {delay}s"
                time.sleep(delay)
                continue
            if response.status_code >= 500:
                delay = min(60.0, 2.0 * (2 ** attempt))
                last_error = f"HTTP {response.status_code}: {response.text[:160]}"
                time.sleep(delay)
                continue
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, list):
                raise RuntimeError(f"Unexpected payload {payload}")
            time.sleep(SUCCESS_DELAY_SECONDS)
            return payload
        except Exception as exc:
            last_error = repr(exc)
            time.sleep(min(60.0, 2.0 * (2 ** attempt)))
    raise RuntimeError(f"Hyperliquid query failed {asset}: {last_error}")


def load_hyperliquid_events_with_asset_pause():
    original_assets = audit.ASSETS
    frames = []
    coverage = {}
    try:
        for index, asset in enumerate(original_assets):
            audit.ASSETS = (asset,)
            frame, asset_coverage = ORIGINAL_LOAD_HYPERLIQUID_EVENTS()
            frames.append(frame)
            coverage.update(asset_coverage)
            if index + 1 < len(original_assets):
                time.sleep(BETWEEN_ASSET_DELAY_SECONDS)
    finally:
        audit.ASSETS = original_assets
    return pd.concat(frames, ignore_index=True).sort_values(["asset", "timestamp"]), coverage


def main():
    audit.query_hyperliquid = rate_limit_safe_query
    audit.load_hyperliquid_events = load_hyperliquid_events_with_asset_pause
    audit.main()


if __name__ == "__main__":
    main()
