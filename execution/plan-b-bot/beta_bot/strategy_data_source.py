from __future__ import annotations

import time
from typing import Any

import requests

from .data_contract import DAY_MS, DataContractPolicy


def build_binance_daily_request(
    *,
    policy: DataContractPolicy,
    symbol: str,
    start_ms: int,
    end_ms: int,
    limit: int = 1000,
) -> dict[str, Any]:
    if start_ms < 0 or end_ms < start_ms:
        raise ValueError("Invalid Binance daily request range")
    if limit <= 0 or limit > 1000:
        raise ValueError("Binance kline limit must be between 1 and 1000")
    return {
        "symbol": symbol.upper(),
        "interval": policy.strategy_interval,
        "startTime": int(start_ms),
        "endTime": int(end_ms),
        "timeZone": policy.strategy_time_zone,
        "limit": int(limit),
    }


def fetch_binance_daily_rows(
    *,
    policy: DataContractPolicy,
    symbol: str,
    start_ms: int,
    end_ms: int,
    timeout: float,
) -> list[list[Any]]:
    """Fetch the contract-defined Binance UTC daily source with endpoint fallback.

    This function deliberately returns raw exchange rows. `data_contract.py` owns
    all canonical filtering, completeness checks and decision-boundary semantics.
    """
    cursor = int(start_ms)
    rows: list[list[Any]] = []
    while cursor <= end_ms:
        params = build_binance_daily_request(
            policy=policy,
            symbol=symbol,
            start_ms=cursor,
            end_ms=end_ms,
        )
        payload = None
        last_error: Exception | None = None
        for endpoint in policy.strategy_endpoints:
            try:
                response = requests.get(endpoint, params=params, timeout=timeout)
                response.raise_for_status()
                candidate = response.json()
                if not isinstance(candidate, list):
                    raise RuntimeError("Unexpected Binance kline response shape")
                payload = candidate
                break
            except Exception as exc:  # endpoint fallback is explicit policy
                last_error = exc
        if payload is None:
            raise RuntimeError(f"Could not fetch canonical Binance daily data: {last_error}")
        if not payload:
            break
        for row in payload:
            if not isinstance(row, list):
                raise RuntimeError("Unexpected Binance kline row shape")
            rows.append(row)
        try:
            last_open = int(payload[-1][0])
        except (IndexError, TypeError, ValueError) as exc:
            raise RuntimeError("Malformed Binance kline pagination key") from exc
        next_cursor = last_open + DAY_MS
        if next_cursor <= cursor:
            raise RuntimeError("Binance kline pagination did not advance")
        cursor = next_cursor
        if len(payload) < 1000:
            break
        time.sleep(0.05)
    return rows
