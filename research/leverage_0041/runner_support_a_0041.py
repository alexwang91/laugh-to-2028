from __future__ import annotations

"""One-time LEVERAGE-0041 sweet-spot study runner.

Inert unless explicitly executed. All economic and selection semantics are
frozen in LEVERAGE-0041.json and LEVERAGE-0041-STUDY-IMPLEMENTATION-V1.json
before RUN_ONCE. Candidate economic metrics are written to immutable artifacts
and are intentionally not printed to stdout.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
from typing import Mapping

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research"
L0040 = RESEARCH / "leverage_0040"
L0041 = RESEARCH / "leverage_0041"
CORE = RESEARCH / "core"
HYBRID = RESEARCH / "hybrid_meta"
REGIME = RESEARCH / "regime_kelly"
DISPERSION = RESEARCH / "dispersion_overlay"
for p in (ROOT, RESEARCH, CORE, HYBRID, REGIME, DISPERSION, L0040, L0041):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import run_leverage_0040_once as old  # noqa: E402
import run_leverage_0040_once_r1 as authority  # noqa: E402
from liquidation_model import (  # noqa: E402
    LiquidationModelError,
    evaluate_cross_margin_state,
    load_frozen_snapshot,
    uniform_long_down_liquidation_distance,
)
import study_core_0041 as core  # noqa: E402

PREREG_PATH = L0041 / "LEVERAGE-0041.json"
CONTRACT_PATH = L0041 / "LEVERAGE-0041-STUDY-IMPLEMENTATION-V1.json"
RESULT_DIR = RESEARCH / "results" / "leverage_0041"
FUNDING_PATH = RESEARCH / "results" / "funding_crossvenue_0002" / "paired_8h_blocks.csv"
OLD_RESULT_DIR = RESEARCH / "results" / "leverage_0040"
OLD_SUMMARY = OLD_RESULT_DIR / "summary.json"
OLD_DIGEST = OLD_RESULT_DIR / "summary.sha256"
MARGIN_SNAPSHOT = RESEARCH / "leverage_0039" / "hyperliquid_margin_snapshot.json"

FULL_START = pd.Timestamp("2022-12-10")
FULL_END = pd.Timestamp("2026-08-02")
COMMON_FUNDING_START = pd.Timestamp("2023-06-18")
COMMON_FUNDING_END = pd.Timestamp("2026-07-31")
FUNDING_SPIKES = (1.0, 2.0, 3.0, 5.0)
VOL_MULTIPLIERS = (1.5, 2.0, 3.0)
START_DATES = ("2022-12-10", "2023-03-01", "2023-06-01", "2024-01-01")
GAP_SCENARIOS = {
    "UNIFORM_-10": {a: -0.10 for a in core.ASSETS},
    "UNIFORM_-20": {a: -0.20 for a in core.ASSETS},
    "UNIFORM_-30": {a: -0.30 for a in core.ASSETS},
    "UNIFORM_-40": {a: -0.40 for a in core.ASSETS},
    "UNIFORM_-50": {a: -0.50 for a in core.ASSETS},
    "ALT_CRASH": {"BTC": -0.25, "ETH": -0.35, "SOL": -0.50, "BNB": -0.40},
    "BTC_LED_CRASH": {"BTC": -0.40, "ETH": -0.25, "SOL": -0.30, "BNB": -0.25},
}
HISTORICAL_WINDOWS = {
    "2021_SPRING_CRASH_PROXY": ("2021-05-01", "2021-07-31", "PROXY"),
    "2021_BEAR_TRANSITION_PROXY": ("2021-11-01", "2022-03-31", "PROXY"),
    "2022_SEVERE_DRAWDOWN_PROXY": ("2022-05-01", "2022-12-31", "PROXY"),
    "2024_STRESS": ("2024-03-01", "2024-05-15", "FULL_BRRK"),
    "2025_FULL_YEAR": ("2025-01-01", "2025-12-31", "FULL_BRRK"),
    "2026_RECENT": ("2026-01-01", "2026-08-02", "FULL_BRRK"),
}


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _dataframe_sha256(frame: pd.DataFrame) -> str:
    payload = frame.to_csv(
        index=True, float_format="%.12f", lineterminator="\n"
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _json_safe(value):
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, (pd.Timestamp, np.datetime64)):
        return pd.Timestamp(value).isoformat()
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        x = float(value)
        return None if math.isnan(x) or math.isinf(x) else x
    return value


def _validate_pre_run_contract():
    prereg = _read_json(PREREG_PATH)
    contract = _read_json(CONTRACT_PATH)
    if prereg.get("experiment_id") != "LEVERAGE-0041":
        raise RuntimeError("wrong preregistration identity")
    if prereg.get("status") != "PREREGISTERED_BEFORE_FIRST_RUN":
        raise RuntimeError("LEVERAGE-0041 is not preregistered")
    if prereg.get("production_authorized") is not False:
        raise RuntimeError("preregistration unexpectedly authorizes production")
    if contract.get("status") != "FROZEN_BEFORE_FIRST_ECONOMIC_RUN":
        raise RuntimeError("implementation contract is not frozen pre-result")
    if contract.get("result_observed_before_freeze") is not False:
        raise RuntimeError("implementation contract is not a clean pre-result freeze")
    if contract.get("owner_run_once_authorized") is not True:
        raise RuntimeError("owner RUN_ONCE authorization not recorded")
    if contract.get("production_authorized") is not False:
        raise RuntimeError("implementation contract unexpectedly authorizes production")
    if (RESULT_DIR / "summary.json").exists():
        raise RuntimeError("LEVERAGE-0041 result already exists; one-time run cannot repeat")
    if not OLD_SUMMARY.exists() or not OLD_DIGEST.exists():
        raise RuntimeError("immutable LEVERAGE-0040 comparator evidence missing")
    expected_old = OLD_DIGEST.read_text(encoding="utf-8").strip()
    if _sha256(OLD_SUMMARY) != expected_old:
        raise RuntimeError("immutable LEVERAGE-0040 comparator digest mismatch")
    if expected_old != "3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0":
        raise RuntimeError("unexpected LEVERAGE-0040 immutable digest")
    return prereg, contract


def _load_authoritative_inputs():
    prices = authority._fetch_prices_corrected()
    v1, brrk, defensive = authority._load_frozen_targets_corrected()
    if authority._target_authority_meta.get("published_banded_weights_used_for_scale") is not False:
        raise RuntimeError("banded holdings were incorrectly used as target authority")
    if FULL_END not in prices.index:
        raise RuntimeError("price frame does not reach frozen end")
    cap1 = core.construct_requested_targets(brrk, 1.0)
    if not np.allclose(cap1.to_numpy(), brrk.to_numpy(), rtol=0.0, atol=1e-12):
        raise RuntimeError("cap=1 requested-target parity failed")
    return prices, v1, brrk, defensive, cap1


def _funding_maps():
    native, proxy = old._funding_block_maps()
    return native, proxy


def _capacity_floor_by_route(artifact_dir: Path):
    files = list(Path(artifact_dir).rglob("vwap_slippage.csv"))
    if len(files) != 1:
        raise RuntimeError(f"expected one vwap_slippage.csv, found {len(files)}")
    path = files[0]
    frame = pd.read_csv(path)
    required = [
        ("BTC", "spot"),
        ("BTC", "perp"),
        ("ETH", "spot"),
        ("ETH", "perp"),
        ("SOL", "spot"),
        ("SOL", "perp"),
        ("BNB", "perp"),
    ]
    floor: dict[tuple[str, str], float] = {}
    classification: dict[str, list[str]] = {}
    for asset, market in required:
        sub = frame[
            (frame["target"].astype(str) == asset)
            & (frame["market_type"].astype(str) == market)
        ]
        good: list[float] = []
        for notional, group in sub.groupby("target_notional"):
            sides = set(group["side"].astype(str))
            fill = (
                group["fully_fillable_in_returned_book"]
                .astype(str)
                .str.lower()
                .isin(["true", "1"])
            )
            if {"buy", "sell"}.issubset(sides) and bool(fill.all()):
                good.append(float(notional))
        if not good:
            raise RuntimeError(f"no two-sided fillable capacity for {asset} {market}")
        floor[(asset, market)] = max(good)
        classification[f"{asset}:{market}"] = sorted(
            set(str(x) for x in sub.get("classification", pd.Series(dtype=str)).dropna())
        )
    return floor, path, _sha256(path), classification


def _route_market_weights(path: core.Path0041) -> dict[tuple[str, str], pd.Series]:
    out: dict[tuple[str, str], pd.Series] = {}
    for asset in ("BTC", "ETH", "SOL"):
        out[(asset, "spot")] = path.routed_spot_weights[asset].astype(float)
    for asset in core.ASSETS:
        out[(asset, "perp")] = path.routed_perp_weights[asset].astype(float)
    return out


def _capacity_check(path: core.Path0041, floors, depth_fraction: float):
    route_series = _route_market_weights(path)
    max_trade = {}
    failures = []
    for key, series in route_series.items():
        prev = 0.0
        max_seen = 0.0
        cap_usd = float(floors[key]) * float(depth_fraction)
        for dt, weight in series.items():
            trade = abs(float(weight) - prev) * core.REFERENCE_EQUITY
            max_seen = max(max_seen, trade)
            if trade > cap_usd + 1e-9:
                failures.append(
                    {
                        "date": pd.Timestamp(dt).strftime("%Y-%m-%d"),
                        "route": f"{key[0]}:{key[1]}",
                        "trade_usd": trade,
                        "capacity_usd": cap_usd,
                    }
                )
            prev = float(weight)
        max_trade[f"{key[0]}:{key[1]}"] = max_seen
    return {
        "pass": not failures,
        "max_trade_usd_by_route": max_trade,
        "capacity_usd_by_route": {
            f"{a}:{m}": float(v) * float(depth_fraction)
            for (a, m), v in floors.items()
        },
        "failures": failures[:25],
    }


def _liquidation_distance(path: core.Path0041):
    snapshot = load_frozen_snapshot()
    minimum = float("inf")
    worst_date = None
    any_perp = False
    starting_liquidatable = False
    for dt, row in path.routed_perp_weights.iterrows():
        notionals = {
            a: float(row[a]) * core.REFERENCE_EQUITY
            for a in core.ASSETS
            if float(row[a]) > 1e-15
        }
        if not notionals:
            continue
        any_perp = True
        try:
            dist = uniform_long_down_liquidation_distance(
                current_cross_account_equity_usd=core.CASH_RESERVE * core.REFERENCE_EQUITY,
                current_long_perp_notionals_usd=notionals,
                snapshot=snapshot,
            )
            d = (
                float("inf")
                if not dist.liquidates_within_domain
                else float(dist.uniform_down_move_fraction)
            )
        except LiquidationModelError as exc:
            if "already liquidatable" in str(exc):
                d = 0.0
                starting_liquidatable = True
            else:
                raise
        if d < minimum:
            minimum = d
            worst_date = pd.Timestamp(dt)
    if not any_perp:
        return {
            "pass": True,
            "minimum_uniform_down_move": None,
            "worst_date": None,
            "starting_liquidatable_state_seen": False,
            "cross_margin_equity_usd": core.CASH_RESERVE * core.REFERENCE_EQUITY,
        }
    value = None if math.isinf(minimum) else minimum
    return {
        "pass": bool(minimum > core.LIQUIDATION_MIN_DISTANCE),
        "minimum_uniform_down_move": value,
        "worst_date": None if worst_date is None else worst_date.strftime("%Y-%m-%d"),
        "starting_liquidatable_state_seen": bool(starting_liquidatable),
        "cross_margin_equity_usd": core.CASH_RESERVE * core.REFERENCE_EQUITY,
    }


def _gap_stress(path: core.Path0041):
    snapshot = load_frozen_snapshot()
    out = {}
    for name, gaps in GAP_SCENARIOS.items():
        worst_return = float("inf")
        worst_date = None
        any_liquidatable = False
        first_liq_date = None
        for dt in path.held_weights.index:
            held = path.held_weights.loc[dt]
            ret = float(sum(float(held[a]) * float(gaps[a]) for a in core.ASSETS))
            perp_row = path.routed_perp_weights.loc[dt]
            notionals = {
                a: float(perp_row[a]) * core.REFERENCE_EQUITY
                for a in core.ASSETS
                if float(perp_row[a]) > 1e-15
            }
            liquidatable = False
            if notionals:
                state = evaluate_cross_margin_state(
                    current_cross_account_equity_usd=core.CASH_RESERVE * core.REFERENCE_EQUITY,
                    current_long_perp_notionals_usd=notionals,
                    relative_mark_returns={a: float(gaps[a]) for a in notionals},
                    snapshot=snapshot,
                )
                liquidatable = bool(state.liquidatable)
            if ret < worst_return:
                worst_return = ret
                worst_date = pd.Timestamp(dt)
            if liquidatable:
                any_liquidatable = True
                if first_liq_date is None:
                    first_liq_date = pd.Timestamp(dt)
        out[name] = {
            "worst_portfolio_return": worst_return,
            "worst_date": None if worst_date is None else worst_date.strftime("%Y-%m-%d"),
            "liquidatable": any_liquidatable,
            "first_liquidatable_date": (
                None if first_liq_date is None else first_liq_date.strftime("%Y-%m-%d")
            ),
            "catastrophe_pass": bool(worst_return > -0.70),
            "liquidation_pass": not any_liquidatable,
            "pass": bool(worst_return > -0.70 and not any_liquidatable),
        }
    return out



__all__ = [n for n in globals() if not n.startswith('__')]
