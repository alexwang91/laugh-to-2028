from __future__ import annotations

"""Independent research/live parity gate for the P3.2 BRRK target engine.

The P3.1 candle canonicalizer is intentionally shared.  After that boundary the
reference calculation uses the frozen research modules, while the live side uses
``beta_bot.target_engine``.  This prevents a tautological test where both sides
call the same target implementation.
"""

import json
import math
import sys
import time
from pathlib import Path
from typing import Sequence

import numpy as np
import pandas as pd
import requests


REPO_ROOT = Path(__file__).resolve().parents[2]
EXECUTION_ROOT = REPO_ROOT / "execution" / "plan-b-bot"
RESEARCH = REPO_ROOT / "research"
REGIME = RESEARCH / "regime_kelly"
HYBRID = RESEARCH / "hybrid_meta"
RISKFIX = RESEARCH / "risk_metric_fix"

if str(EXECUTION_ROOT) not in sys.path:
    sys.path.insert(0, str(EXECUTION_ROOT))

from beta_bot.product_config import load_product_config  # noqa: E402
from beta_bot.target_engine import calculate_target  # noqa: E402
from beta_bot.target_math import build_v1_raw as product_build_v1_raw  # noqa: E402
from p3_1_data_contract_adapter import canonicalize_research_daily_history  # noqa: E402

for path in (RESEARCH, REGIME, HYBRID, RISKFIX):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import crypto_rotation_backtest as research_bt  # noqa: E402
from config import RegimeKellyConfig  # noqa: E402
from corrected_risk import choose_scale_corrected  # noqa: E402
from features_no_dominance import build_features_no_dominance  # noqa: E402
from regime_model_vb_nd import fit_variational_regime_model_nd  # noqa: E402
from walkforward_v1_meta import (  # noqa: E402
    RISK_BUDGET,
    build_benchmark_v1,
    fit_state_v1_distribution,
    portfolio_returns_full,
    sample_v1_paths,
)


ASSETS = ("BTC", "ETH", "SOL", "BNB", "XRP")
TARGET_ASSETS = ("BTC", "ETH", "SOL", "BNB")
API_BASES = (
    "https://data-api.binance.vision/api/v3/klines",
    "https://api.binance.com/api/v3/klines",
)
RAW_START = "2020-08-01T00:00:00Z"
V1_ONLY_DECISIONS = (
    "2021-05-20T00:00:00Z",
    "2021-09-08T00:00:00Z",
)
FULL_BRRK_DECISIONS = (
    "2022-12-15T00:00:00Z",
    "2023-10-25T00:00:00Z",
    "2024-08-06T00:00:00Z",
    "2025-04-10T00:00:00Z",
    "2025-11-15T00:00:00Z",
    "2026-08-03T00:00:00Z",
)


def _ms(value: str | pd.Timestamp) -> int:
    timestamp = pd.Timestamp(value)
    if timestamp.tzinfo is None:
        timestamp = timestamp.tz_localize("UTC")
    else:
        timestamp = timestamp.tz_convert("UTC")
    return int(timestamp.timestamp() * 1000)


def fetch_daily_rows(symbol: str, start_ms: int, end_exclusive_ms: int) -> list[list[object]]:
    cursor = int(start_ms)
    rows: list[list[object]] = []
    last_error: Exception | None = None
    while cursor < end_exclusive_ms:
        payload = None
        for base in API_BASES:
            try:
                response = requests.get(
                    base,
                    params={
                        "symbol": symbol,
                        "interval": "1d",
                        "timeZone": "0",
                        "startTime": cursor,
                        "endTime": end_exclusive_ms - 1,
                        "limit": 1000,
                    },
                    timeout=30,
                )
                response.raise_for_status()
                payload = response.json()
                break
            except Exception as exc:  # pragma: no cover - exercised by CI/network only
                last_error = exc
                time.sleep(0.5)
        if payload is None:
            raise RuntimeError(f"Could not fetch {symbol}: {last_error}")
        if not payload:
            break
        rows.extend(payload)
        next_cursor = int(payload[-1][0]) + 86_400_000
        if next_cursor <= cursor:
            raise RuntimeError(f"Non-advancing Binance cursor for {symbol}")
        cursor = next_cursor
        time.sleep(0.04)
    if not rows:
        raise RuntimeError(f"No Binance rows for {symbol}")
    return rows


def fetch_source_batches() -> dict[str, Sequence[tuple[str, Sequence[Sequence[object]]]]]:
    max_decision = max(pd.Timestamp(value) for value in FULL_BRRK_DECISIONS)
    start_ms = _ms(RAW_START)
    end_exclusive_ms = int(max_decision.timestamp() * 1000)
    batches = {}
    for asset in ASSETS:
        symbol = f"{asset}USDT"
        rows = fetch_daily_rows(symbol, start_ms, end_exclusive_ms)
        batches[asset] = [(symbol, rows)]
        print(f"fetched {asset}: {len(rows)} rows", flush=True)
    return batches


def dataset_prices(dataset) -> pd.DataFrame:
    columns = {}
    for asset in ASSETS:
        rows = dataset.closes_by_asset[asset]
        index = pd.to_datetime(
            np.asarray([row.session_open_ms for row in rows], dtype=np.int64),
            unit="ms",
            utc=True,
        ).tz_localize(None)
        columns[asset] = pd.Series([float(row.close) for row in rows], index=index, dtype=float)
    return pd.DataFrame(columns).loc[:, list(ASSETS)]


def research_current_target(dataset) -> dict[str, object]:
    prices = dataset_prices(dataset)
    cfg = RegimeKellyConfig(hmm_restarts=3, hmm_iter=250)
    features = build_features_no_dominance(prices, cfg)
    v1_raw = build_benchmark_v1(prices)
    v1_banded = research_bt.apply_band(v1_raw, 0.05)
    v1_returns, _, _ = portfolio_returns_full(prices, v1_banded)

    decision_dates = []
    clean = features.dropna()
    for dt in clean.index:
        if len(clean.loc[:dt]) < cfg.min_train_days:
            continue
        if not decision_dates or (dt - decision_dates[-1]).days >= cfg.refit_every_days:
            decision_dates.append(dt)
    if not decision_dates:
        raise RuntimeError("Reference research path has no eligible BRRK refit date")
    refit = decision_dates[-1]

    train_features = features.loc[:refit]
    fit = fit_variational_regime_model_nd(train_features, cfg, n_factors=4)
    posterior = fit.filtered_posterior(features.loc[:refit]).iloc[-1]
    distribution = fit_state_v1_distribution(v1_returns.loc[:refit], train_features, fit, cfg)
    paths = sample_v1_paths(
        posterior,
        fit,
        distribution,
        cfg,
        seed=cfg.random_seed + int(refit.strftime("%Y%m%d")),
    )
    allocation = choose_scale_corrected(paths, RISK_BUDGET)
    meta_scale = float(allocation["scale"])
    riskoff_probability = float(np.clip(posterior.get("RISK_OFF", 0.0), 0.0, 1.0))
    defensive_scale = float(1.0 - riskoff_probability * (1.0 - meta_scale))

    raw = v1_raw.loc[prices.index[-1], list(TARGET_ASSETS)].astype(float)
    target = raw * defensive_scale
    gross = float(target.sum())
    return {
        "target_weights": {asset: float(target[asset]) for asset in TARGET_ASSETS},
        "gross": gross,
        "cash": float(1.0 - gross),
        "refit": pd.Timestamp(refit).strftime("%Y-%m-%d"),
        "posterior": {state: float(value) for state, value in posterior.items()},
        "risk_state": str(posterior.astype(float).idxmax()),
        "riskoff_probability": riskoff_probability,
        "meta_scale": meta_scale,
        "defensive_scale": defensive_scale,
        "features": {name: float(features.loc[refit, name]) for name in features.columns},
    }


def assert_close(label: str, actual: float, expected: float, *, atol: float = 2e-10) -> None:
    if not math.isclose(actual, expected, rel_tol=0.0, abs_tol=atol):
        raise AssertionError(f"{label}: product={actual!r}, research={expected!r}")


def run_v1_only_parity(source_batches) -> list[dict[str, object]]:
    rows = []
    for decision in V1_ONLY_DECISIONS:
        dataset = canonicalize_research_daily_history(
            source_batches=source_batches,
            decision_timestamp=decision,
        )
        prices = dataset_prices(dataset)
        product_v1, _ = product_build_v1_raw(prices)
        research_v1 = build_benchmark_v1(prices)
        latest = prices.index[-1]
        for asset in TARGET_ASSETS:
            assert_close(
                f"V1 {decision} {asset}",
                float(product_v1.loc[latest, asset]),
                float(research_v1.loc[latest, asset]),
                atol=1e-12,
            )
        rows.append(
            {
                "decision": decision,
                "session": latest.strftime("%Y-%m-%d"),
                "weights": {asset: float(product_v1.loc[latest, asset]) for asset in TARGET_ASSETS},
                "gross": float(product_v1.loc[latest, list(TARGET_ASSETS)].sum()),
            }
        )
    return rows


def run_full_parity(source_batches) -> list[dict[str, object]]:
    config = load_product_config()
    rows = []
    for decision in FULL_BRRK_DECISIONS:
        print(f"parity decision {decision}", flush=True)
        dataset = canonicalize_research_daily_history(
            source_batches=source_batches,
            decision_timestamp=decision,
        )
        product = calculate_target(
            daily_dataset=dataset,
            account_equity_usd=10_000.0,
            current_positions={},
            approved_config=config,
        )
        reference = research_current_target(dataset)

        for asset in TARGET_ASSETS:
            assert_close(
                f"target {decision} {asset}",
                product.target_weights[asset],
                reference["target_weights"][asset],
            )
        assert_close(f"gross {decision}", product.base_gross_target, reference["gross"])
        assert_close(f"cash {decision}", product.cash_share, reference["cash"])
        assert_close(f"meta {decision}", product.meta_scale, reference["meta_scale"])
        assert_close(
            f"defensive {decision}", product.defensive_scale, reference["defensive_scale"]
        )
        assert_close(
            f"riskoff {decision}",
            product.riskoff_probability,
            reference["riskoff_probability"],
        )
        if product.regime_refit_session != reference["refit"]:
            raise AssertionError(
                f"refit {decision}: product={product.regime_refit_session} research={reference['refit']}"
            )
        if product.risk_state != reference["risk_state"]:
            raise AssertionError(
                f"risk state {decision}: product={product.risk_state} research={reference['risk_state']}"
            )
        for state, expected in reference["posterior"].items():
            assert_close(
                f"posterior {decision} {state}",
                product.risk_state_probabilities[state],
                expected,
            )
        product_features = product.feature_snapshot["regime_features"]
        for name, expected in reference["features"].items():
            assert_close(f"feature {decision} {name}", product_features[name], expected, atol=1e-12)

        rows.append(
            {
                "decision": decision,
                "target_session": product.target_session,
                "regime_refit_session": product.regime_refit_session,
                "risk_state": product.risk_state,
                "riskoff_probability": product.riskoff_probability,
                "meta_scale": product.meta_scale,
                "defensive_scale": product.defensive_scale,
                "gross": product.base_gross_target,
                "cash": product.cash_share,
                "weights": product.target_weights,
                "data_digest": product.data_digest,
            }
        )
    return rows


def main() -> None:
    source_batches = fetch_source_batches()
    report = {
        "status": "P3_2_RESEARCH_LIVE_GOLDEN_PARITY_PASS",
        "v1_only_early_history": run_v1_only_parity(source_batches),
        "full_brrk_multi_date": run_full_parity(source_batches),
    }
    risk_states = sorted({row["risk_state"] for row in report["full_brrk_multi_date"]})
    scales = [float(row["defensive_scale"]) for row in report["full_brrk_multi_date"]]
    report["coverage"] = {
        "risk_states_observed": risk_states,
        "min_defensive_scale": min(scales),
        "max_defensive_scale": max(scales),
        "decision_count": len(report["full_brrk_multi_date"]),
        "early_v1_decision_count": len(report["v1_only_early_history"]),
    }
    print("=== P3_2_TARGET_PARITY ===")
    print(json.dumps(report, indent=2, sort_keys=True))
    print("=== END_P3_2_TARGET_PARITY ===")


if __name__ == "__main__":
    main()
