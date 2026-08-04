from __future__ import annotations

import io
import time
import zipfile
from typing import Any

import pandas as pd
import requests

DAILY_ROOT = "data/futures/um/daily/klines/"
DOWNLOAD_ROOT = "https://data.binance.vision"


def internal_missing_dates(history: pd.DataFrame) -> pd.DatetimeIndex:
    """Calendar dates strictly inside an observed 24/7 perp history but absent from monthly 1d bars."""
    if history.empty or len(history.index) < 2:
        return pd.DatetimeIndex([])
    index = pd.DatetimeIndex(history.index).normalize().sort_values().unique()
    expected = pd.date_range(index.min(), index.max(), freq="D")
    return expected.difference(index)


def _download_daily(url: str) -> bytes | None:
    last_error: Exception | None = None
    for attempt in range(6):
        try:
            response = requests.get(url, timeout=45)
            if response.status_code == 404:
                return None
            if response.status_code in (418, 429) or response.status_code >= 500:
                raise RuntimeError(f"HTTP {response.status_code}")
            response.raise_for_status()
            return response.content
        except Exception as exc:
            last_error = exc
            time.sleep(min(8.0, 0.5 * (2 ** attempt)))
    raise RuntimeError(f"daily fallback download failed {url}: {last_error!r}")


def repair_internal_gaps(
    symbol: str,
    history: pd.DataFrame,
    parse_kline_zip,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """
    Fill only monthly-archive internal date gaps from the official Binance daily 1d archive.
    No interpolation, forward fill, cross-market substitution or zero-return assumption is allowed.
    """
    missing = internal_missing_dates(history)
    repaired_rows: list[pd.DataFrame] = []
    repaired: list[str] = []
    unresolved: list[str] = []

    for date in missing:
        day = pd.Timestamp(date).strftime("%Y-%m-%d")
        url = f"{DOWNLOAD_ROOT}/{DAILY_ROOT}{symbol}/1d/{symbol}-1d-{day}.zip"
        payload = _download_daily(url)
        if payload is None:
            unresolved.append(day)
            continue
        frame = parse_kline_zip(payload)
        exact = frame.loc[frame.index == pd.Timestamp(date)]
        if len(exact) != 1:
            unresolved.append(day)
            continue
        if exact[["close", "quote_volume"]].isna().any(axis=None):
            unresolved.append(day)
            continue
        repaired_rows.append(exact)
        repaired.append(day)

    if repaired_rows:
        history = pd.concat([history, *repaired_rows]).sort_index()
        history = history[~history.index.duplicated(keep="last")]

    return history, {
        "symbol": symbol,
        "internal_monthly_gap_count": int(len(missing)),
        "daily_fallback_repaired_count": int(len(repaired)),
        "daily_fallback_unresolved_count": int(len(unresolved)),
        "repaired_dates": repaired,
        "unresolved_dates": unresolved,
    }
