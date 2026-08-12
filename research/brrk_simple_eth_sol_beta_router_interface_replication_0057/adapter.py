from __future__ import annotations

from typing import Any, Mapping

import numpy as np
import pandas as pd

from research.brrk_simple_eth_sol_beta_router_0056 import engine as frozen_0056_engine

RESEARCH_ID = "BRRK-SIMPLE-ETH-SOL-BETA-ROUTER-INTERFACE-REPLICATION-0057"
BOUND_0056_RESEARCH_ID = "BRRK-SIMPLE-ETH-SOL-BETA-ROUTER-0056"
BOUND_0056_ENGINE_BLOB_SHA = "b0fc1ac267a66593e7e2c4687aff81491bfcdf5a"
EXPECTED_PAYLOAD_SHA256 = "d1cd28bc76f2cd8ee0486287fc50b49e5451355a3e75132a2de5b30c15af3193"
ASSETS = ("ETH", "SOL")


class InterfaceAdapterError(RuntimeError):
    pass


def _source_close(frame: pd.DataFrame, asset: str) -> np.ndarray:
    if not isinstance(frame, pd.DataFrame):
        raise InterfaceAdapterError(f"{asset} source must be a DataFrame")
    if "close" not in frame.columns:
        raise InterfaceAdapterError(f"missing {asset} close")
    values = frame["close"].to_numpy(dtype=np.float64, copy=True)
    if values.ndim != 1 or values.size == 0:
        raise InterfaceAdapterError(f"{asset} close must be a non-empty 1D array")
    if not np.isfinite(values).all() or np.any(values <= 0.0):
        raise InterfaceAdapterError(f"{asset} close must be finite and strictly positive")
    return values


def validate_tz_naive_source_frames(frames: Mapping[str, pd.DataFrame]) -> None:
    if set(frames) != set(ASSETS):
        raise InterfaceAdapterError(f"source frames must contain exactly {ASSETS}")
    indexes = [frames[a].index for a in ASSETS]
    if not all(isinstance(idx, pd.DatetimeIndex) for idx in indexes):
        raise InterfaceAdapterError("source indexes must be DatetimeIndex")
    if not indexes[0].equals(indexes[1]):
        raise InterfaceAdapterError("ETH/SOL source indexes must be identical")
    index = indexes[0]
    if index.tz is not None:
        raise InterfaceAdapterError("source index must be UTC-normalized tz-naive dates")
    if index.has_duplicates or not index.is_monotonic_increasing:
        raise InterfaceAdapterError("source index must be unique and strictly increasing")
    if (index.normalize() != index).any():
        raise InterfaceAdapterError("source index must contain midnight-normalized daily labels")
    _source_close(frames["ETH"], "ETH")
    _source_close(frames["SOL"], "SOL")


def adapt_source_frames(frames: Mapping[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Apply the sole preregistered representation correction without changing observations."""
    validate_tz_naive_source_frames(frames)
    source_index = frames["ETH"].index.copy()
    source_close = {asset: _source_close(frames[asset], asset) for asset in ASSETS}

    adapted: dict[str, pd.DataFrame] = {}
    for asset in ASSETS:
        out = frames[asset].copy(deep=True)
        out.index = out.index.tz_localize("UTC")
        adapted[asset] = out

    adapted_index = adapted["ETH"].index
    if str(adapted_index.tz) != "UTC":
        raise InterfaceAdapterError("adapted index must be timezone-aware UTC")
    if not adapted_index.equals(adapted["SOL"].index):
        raise InterfaceAdapterError("adapted ETH/SOL indexes diverged")
    if not adapted_index.tz_localize(None).equals(source_index):
        raise InterfaceAdapterError("adapter changed calendar labels or row order")
    if len(adapted_index) != len(source_index):
        raise InterfaceAdapterError("adapter changed row count")
    for asset in ASSETS:
        after = adapted[asset]["close"].to_numpy(dtype=np.float64, copy=True)
        if not np.array_equal(after, source_close[asset], equal_nan=False):
            raise InterfaceAdapterError(f"adapter changed {asset} close values")
        if frames[asset].index.tz is not None:
            raise InterfaceAdapterError("adapter mutated source frame index")
        before_again = frames[asset]["close"].to_numpy(dtype=np.float64, copy=True)
        if not np.array_equal(before_again, source_close[asset], equal_nan=False):
            raise InterfaceAdapterError(f"adapter mutated source {asset} close values")
    return adapted


def evaluate_frozen_contract(frames: Mapping[str, pd.DataFrame], payload_sha256: str) -> dict[str, Any]:
    """Delegate unchanged portfolio science to immutable 0056 after representation adaptation."""
    if str(payload_sha256).lower() != EXPECTED_PAYLOAD_SHA256:
        raise InterfaceAdapterError("0057 payload SHA256 does not match frozen preregistration")
    adapted = adapt_source_frames(frames)
    delegated = frozen_0056_engine.evaluate_frozen_contract(adapted, payload_sha256)
    if delegated.get("research_id") != BOUND_0056_RESEARCH_ID:
        raise InterfaceAdapterError("delegated result does not identify the bound 0056 engine")
    if delegated.get("actual_variants_evaluated") != 1:
        raise InterfaceAdapterError("delegated result variant count mismatch")

    result = dict(delegated)
    result["research_id"] = RESEARCH_ID
    result["delegated_scientific_engine"] = {
        "research_id": BOUND_0056_RESEARCH_ID,
        "git_blob_sha": BOUND_0056_ENGINE_BLOB_SHA,
        "portfolio_outputs_modified_by_0057_adapter": False,
    }
    result["source_interface_adapter"] = {
        "source_timezone_representation": "UTC_NORMALIZED_TZ_NAIVE_DAILY_DATES",
        "operation": "COPY_THEN_INDEX_TZ_LOCALIZE_UTC_ONLY",
        "calendar_order_rowcount_close_values_changed": False,
    }
    return result
