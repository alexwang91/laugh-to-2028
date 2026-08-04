from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent / "results"
FUNDING_DIR = RESULTS / "funding_pnl_0003"
ROUTER_SUMMARY = RESULTS / "router_data_0004" / "summary.json"
OUTPUT = RESULTS / "router_pnl_0005"

ASSETS = ("BTC", "ETH", "SOL", "BNB", "XRP")
VERIFIED_CLASSES = {"verified_exact", "verified_official_ui_remap"}
INITIAL_NAV = 10_000.0
DAYS_PER_YEAR = 365.25


def verified_spot_targets(router_summary: dict) -> list[str]:
    targets: list[str] = []
    for asset in ASSETS:
        item = router_summary["targets"][asset]
        classification = item["primary_spot_classification"]
        if classification in VERIFIED_CLASSES:
            targets.append(asset)
    declared = router_summary.get("decision", {}).get("verified_spot_targets")
    if declared is not None and sorted(declared) != sorted(targets):
        raise ValueError(
            f"Router summary decision mismatch: declared={declared}, derived={targets}"
        )
    return targets


def price_returns_from_equity(price_equity: pd.Series, initial_nav: float = INITIAL_NAV) -> np.ndarray:
    values = price_equity.to_numpy(dtype=float)
    if len(values) == 0:
        return np.array([], dtype=float)
    out = np.empty(len(values), dtype=float)
    out[0] = values[0] / initial_nav - 1.0
    out[1:] = values[1:] / values[:-1] - 1.0
    return out


def daily_funding_factors(
    attribution: pd.DataFrame,
    dates: pd.Series,
    perp_assets: Iterable[str],
    source: str = "HYPERLIQUID_COMMON",
) -> np.ndarray:
    perp_assets = tuple(perp_assets)
    if not perp_assets:
        return np.ones(len(dates), dtype=float)

    frame = attribution[
        (attribution["source"] == source)
        & (attribution["asset"].isin(perp_assets))
    ].copy()
    if frame.empty:
        raise ValueError(f"No funding rows for source={source} assets={perp_assets}")

    block_returns = (
        frame.groupby(["date", "block"], as_index=False)["contribution"].sum()
    )
    factors = block_returns.groupby("date")["contribution"].apply(
        lambda s: float(np.prod(1.0 + s.to_numpy(dtype=float)))
    )

    date_keys = pd.to_datetime(dates).dt.strftime("%Y-%m-%d")
    mapped = date_keys.map(factors)
    if mapped.isna().any():
        missing = date_keys[mapped.isna()].tolist()[:10]
        raise ValueError(f"Missing funding factors for dates: {missing}")
    return mapped.to_numpy(dtype=float)


def build_equity(
    price_returns: np.ndarray,
    funding_factors: np.ndarray,
    initial_nav: float = INITIAL_NAV,
) -> np.ndarray:
    if len(price_returns) != len(funding_factors):
        raise ValueError("price_returns and funding_factors must have equal length")
    nav = float(initial_nav)
    values: list[float] = []
    for price_return, funding_factor in zip(price_returns, funding_factors):
        nav *= (1.0 + float(price_return)) * float(funding_factor)
        values.append(nav)
    return np.asarray(values, dtype=float)


def metrics(nav: np.ndarray, dates: pd.Series, initial_nav: float = INITIAL_NAV) -> dict:
    if len(nav) == 0:
        raise ValueError("Empty NAV")
    timestamps = pd.to_datetime(dates)
    elapsed_days = int((timestamps.iloc[-1] - timestamps.iloc[0]).days)
    if elapsed_days <= 0:
        raise ValueError("Need a positive elapsed window")

    returns = np.empty(len(nav), dtype=float)
    returns[0] = nav[0] / initial_nav - 1.0
    returns[1:] = nav[1:] / nav[:-1] - 1.0

    peak = np.maximum.accumulate(nav)
    max_drawdown = float(np.min(nav / peak - 1.0))
    ann_vol = float(np.std(returns, ddof=1) * np.sqrt(365.0))
    sharpe = float(np.mean(returns) / np.std(returns, ddof=1) * np.sqrt(365.0))
    cagr = float((nav[-1] / initial_nav) ** (DAYS_PER_YEAR / elapsed_days) - 1.0)
    return {
        "start": timestamps.iloc[0].strftime("%Y-%m-%d"),
        "end": timestamps.iloc[-1].strftime("%Y-%m-%d"),
        "observations": int(len(nav)),
        "final_multiple": float(nav[-1] / initial_nav),
        "final_10k": float(nav[-1]),
        "cagr": cagr,
        "max_drawdown": max_drawdown,
        "ann_vol": ann_vol,
        "sharpe": sharpe,
        "calmar": float(cagr / abs(max_drawdown)),
    }


def scenario_equity(
    price_returns: np.ndarray,
    dates: pd.Series,
    attribution: pd.DataFrame,
    spot_assets: Iterable[str],
) -> np.ndarray:
    spot_assets = set(spot_assets)
    perp_assets = [asset for asset in ASSETS if asset not in spot_assets]
    factors = daily_funding_factors(attribution, dates, perp_assets)
    return build_equity(price_returns, factors)


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)

    equity = pd.read_csv(FUNDING_DIR / "common_window_daily_equity.csv")
    attribution = pd.read_csv(FUNDING_DIR / "block_asset_funding_attribution.csv")
    router_summary = json.loads(ROUTER_SUMMARY.read_text())

    dates = equity["date"]
    price_returns = price_returns_from_equity(equity["PRICE_ONLY"])
    verified = verified_spot_targets(router_summary)

    scenarios = {
        "PRICE_ONLY": np.asarray(equity["PRICE_ONLY"], dtype=float),
        "HYPERLIQUID_ALL_PERP_NATIVE": scenario_equity(
            price_returns, dates, attribution, []
        ),
        "STRICT_VERIFIED_SPOT": scenario_equity(
            price_returns, dates, attribution, verified
        ),
        "COUNTERFACTUAL_BTC_ETH_SPOT": scenario_equity(
            price_returns, dates, attribution, ["BTC", "ETH"]
        ),
        "COUNTERFACTUAL_BTC_SOL_SPOT": scenario_equity(
            price_returns, dates, attribution, ["BTC", "SOL"]
        ),
        "COUNTERFACTUAL_BTC_ETH_SOL_SPOT": scenario_equity(
            price_returns, dates, attribution, ["BTC", "ETH", "SOL"]
        ),
        "THEORETICAL_ALL_SPOT": scenario_equity(
            price_returns, dates, attribution, ASSETS
        ),
    }

    persisted_all_perp = np.asarray(equity["HYPERLIQUID_ALL_PERP_NATIVE"], dtype=float)
    reconstruction_error = float(
        np.max(np.abs(scenarios["HYPERLIQUID_ALL_PERP_NATIVE"] - persisted_all_perp))
    )
    if reconstruction_error > 1e-3:
        raise RuntimeError(
            f"All-perp reconstruction mismatch: max absolute error={reconstruction_error}"
        )

    output_equity = pd.DataFrame({"date": dates})
    for name, nav in scenarios.items():
        output_equity[name] = nav
    output_equity.to_csv(OUTPUT / "daily_equity.csv", index=False)

    scenario_metrics = {
        name: metrics(nav, dates)
        for name, nav in scenarios.items()
    }
    report = {
        "experiment_id": "ROUTER-PNL-0005-STRICT-VERIFIED-SPOT",
        "status": "EXPLORATORY_POST_AUDIT_ACCOUNTING",
        "promotion_evidence": False,
        "reason_not_preregistered": (
            "This deterministic accounting diagnostic was computed after ROUTER-DATA-0004 "
            "results were observed. It is retained for implementation attribution and must "
            "not be represented as preregistered router-promotion evidence."
        ),
        "trading_target_changes": False,
        "price_return_source": "research/results/funding_pnl_0003/common_window_daily_equity.csv::PRICE_ONLY",
        "funding_attribution_source": "research/results/funding_pnl_0003/block_asset_funding_attribution.csv",
        "router_classification_source": "research/results/router_data_0004/summary.json",
        "verified_spot_assets": verified,
        "strict_perp_assets": [asset for asset in ASSETS if asset not in verified],
        "historical_spot_fee_basis_slippage": "NOT_INCLUDED",
        "interpretation": (
            "STRICT_VERIFIED_SPOT is a funding-only implementation accounting result. "
            "It preserves frozen price returns and the original backtest trading-cost assumption, "
            "sets funding to zero only for currently verified spot assets, and retains native "
            "Hyperliquid funding for all other targets."
        ),
        "candidate_counterfactuals_are_promotion_evidence": False,
        "all_perp_reconstruction_max_abs_error": reconstruction_error,
        "metrics": scenario_metrics,
    }
    (OUTPUT / "summary.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
