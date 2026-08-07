from __future__ import annotations

"""P3.2 canonical Target calculation API.

The engine consumes only the canonical P3.1 daily dataset plus approved product
configuration and account context.  It emits a deterministic long-only BRRK-0011
target with gross <= 1.  Current positions are deliberately *not* used to band,
throttle or rebalance the target; those controls belong to P3.3.
"""

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Any, Mapping

import numpy as np
import pandas as pd

from .data_contract import (
    CANONICAL_ASSETS,
    STRATEGY_SIGNAL_ASSETS,
    CanonicalDailyDataset,
)
from .product_config import ProductConfig, load_product_config
from .target_math import (
    FrozenBRRKConfig,
    TARGET_ASSETS,
    TargetMathError,
    apply_internal_v1_band,
    build_features_no_dominance,
    build_v1_raw,
    current_defensive_state,
    portfolio_returns_full,
)


TARGET_ENGINE_VERSION = "P3.2-BRRK0011-V1"
MODEL_AUTHORITY = "BRRK-0011"
EXPECTED_DATA_CONTRACT_SCHEMA = 2
EXPECTED_DATA_CONTRACT_ID = "BRRK-DATA-CONTRACT-P3.1-R1-2026-08-06"


class TargetCalculationError(RuntimeError):
    pass


def _finite_float(value: object, *, field: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise TargetCalculationError(f"{field} must be numeric") from exc
    if not math.isfinite(parsed):
        raise TargetCalculationError(f"{field} must be finite")
    return parsed


def _json_float(value: object) -> float | None:
    parsed = float(value)
    return parsed if math.isfinite(parsed) else None


def _normalize_positions(current_positions: Mapping[str, object]) -> dict[str, float]:
    unknown = sorted(set(str(asset).upper() for asset in current_positions) - set(CANONICAL_ASSETS))
    if unknown:
        raise TargetCalculationError(
            "Current positions contain assets outside the approved target universe: "
            + ",".join(unknown)
        )
    normalized = {asset: 0.0 for asset in CANONICAL_ASSETS}
    for asset, value in current_positions.items():
        key = str(asset).upper()
        normalized[key] = _finite_float(value, field=f"current_positions[{key}]")
    return normalized


def _validate_product_config(config: ProductConfig) -> None:
    config.validate()
    if config.long_universe != CANONICAL_ASSETS:
        raise TargetCalculationError("Approved product target universe must remain BTC/ETH/SOL/BNB")
    if not config.model_version.startswith("BRRK-0011"):
        raise TargetCalculationError("Approved product model authority must remain BRRK-0011")
    if config.operating_risk_budget is not None:
        raise TargetCalculationError("P3.2 must not freeze or consume the P4 operating risk budget")


def _prices_from_dataset(dataset: CanonicalDailyDataset) -> pd.DataFrame:
    if dataset.schema_version != EXPECTED_DATA_CONTRACT_SCHEMA:
        raise TargetCalculationError("P3.2 requires P3.1 schema v2 canonical daily data")
    if dataset.contract_id != EXPECTED_DATA_CONTRACT_ID:
        raise TargetCalculationError(
            f"Unexpected data contract id {dataset.contract_id!r}; expected {EXPECTED_DATA_CONTRACT_ID!r}"
        )
    if set(dataset.closes_by_asset) != set(STRATEGY_SIGNAL_ASSETS):
        raise TargetCalculationError("Canonical daily dataset must contain BTC/ETH/SOL/BNB/XRP")

    reference_sessions: tuple[int, ...] | None = None
    columns: dict[str, pd.Series] = {}
    for asset in STRATEGY_SIGNAL_ASSETS:
        rows = dataset.closes_by_asset[asset]
        sessions = tuple(int(row.session_open_ms) for row in rows)
        if not sessions:
            raise TargetCalculationError(f"Canonical history is empty for {asset}")
        if reference_sessions is None:
            reference_sessions = sessions
        elif sessions != reference_sessions:
            raise TargetCalculationError("Canonical strategy-signal assets are not session-aligned")
        values = np.asarray([float(row.close) for row in rows], dtype=float)
        if not np.all(np.isfinite(values)) or np.any(values <= 0):
            raise TargetCalculationError(f"Canonical closes for {asset} must be finite and positive")
        index = pd.to_datetime(np.asarray(sessions, dtype=np.int64), unit="ms", utc=True).tz_localize(None)
        columns[asset] = pd.Series(values, index=index, dtype=float)

    prices = pd.DataFrame(columns).loc[:, list(STRATEGY_SIGNAL_ASSETS)].sort_index()
    if prices.index.has_duplicates:
        raise TargetCalculationError("Canonical history contains duplicate sessions")
    if int(dataset.latest_session_open_ms) != int(reference_sessions[-1]):
        raise TargetCalculationError("Dataset latest_session_open_ms does not match the final canonical row")

    decision = pd.Timestamp(dataset.decision_timestamp)
    if decision.tzinfo is None:
        raise TargetCalculationError("Canonical decision timestamp must be timezone-aware UTC")
    decision = decision.tz_convert("UTC")
    if decision.hour or decision.minute or decision.second or decision.microsecond:
        raise TargetCalculationError("P3.2 decision timestamp must be exactly 00:00:00 UTC")
    latest_allowed_ms = int(decision.timestamp() * 1000) - 86_400_000
    if int(dataset.latest_session_open_ms) != latest_allowed_ms:
        raise TargetCalculationError("P3.2 target must consume exactly the completed D-1 UTC daily session")
    return prices


@dataclass(frozen=True)
class TargetCalculationResult:
    decision_timestamp: str
    target_session: str
    target_weights: dict[str, float]
    relative_weights: dict[str, float]
    cash_share: float
    base_gross_target: float
    risk_state: str
    risk_state_probabilities: dict[str, float]
    riskoff_probability: float
    meta_scale: float
    defensive_scale: float
    regime_refit_session: str
    feature_snapshot: dict[str, Any]
    account_equity_usd: float
    current_positions_notional_usd: dict[str, float]
    data_contract_schema: int
    data_contract_id: str
    data_digest: str
    approved_product_id: str
    approved_config_model_version: str
    model_authority: str = MODEL_AUTHORITY
    target_engine_version: str = TARGET_ENGINE_VERSION
    production_authorized: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "decision_timestamp": self.decision_timestamp,
            "target_session": self.target_session,
            "target_weights": dict(self.target_weights),
            "relative_weights": dict(self.relative_weights),
            "cash_share": self.cash_share,
            "base_gross_target": self.base_gross_target,
            "risk_state": self.risk_state,
            "risk_state_probabilities": dict(self.risk_state_probabilities),
            "riskoff_probability": self.riskoff_probability,
            "meta_scale": self.meta_scale,
            "defensive_scale": self.defensive_scale,
            "regime_refit_session": self.regime_refit_session,
            "feature_snapshot": self.feature_snapshot,
            "account_equity_usd": self.account_equity_usd,
            "current_positions_notional_usd": dict(self.current_positions_notional_usd),
            "data_contract_schema": self.data_contract_schema,
            "data_contract_id": self.data_contract_id,
            "data_digest": self.data_digest,
            "approved_product_id": self.approved_product_id,
            "approved_config_model_version": self.approved_config_model_version,
            "model_authority": self.model_authority,
            "target_engine_version": self.target_engine_version,
            "production_authorized": self.production_authorized,
        }

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def calculate_target(
    *,
    daily_dataset: CanonicalDailyDataset,
    account_equity_usd: object,
    current_positions: Mapping[str, object],
    approved_config: ProductConfig | None = None,
) -> TargetCalculationResult:
    """Calculate the frozen P3.2 BRRK target for one 00:00 UTC decision.

    Timing convention is explicit: a decision at D 00:00 UTC consumes canonical
    daily closes only through D-1.  The raw V1 target on D-1 becomes the decision-D
    target, matching the frozen research convention where target row t is held over
    the following day's return.
    """
    config = approved_config or load_product_config()
    _validate_product_config(config)
    equity = _finite_float(account_equity_usd, field="account_equity_usd")
    if equity <= 0:
        raise TargetCalculationError("account_equity_usd must be positive")
    positions = _normalize_positions(current_positions)
    prices = _prices_from_dataset(daily_dataset)

    frozen = FrozenBRRKConfig()
    if tuple(frozen.assets) != tuple(STRATEGY_SIGNAL_ASSETS):
        raise TargetCalculationError("Frozen BRRK feature universe drift detected")
    if tuple(TARGET_ASSETS) != tuple(CANONICAL_ASSETS):
        raise TargetCalculationError("Frozen BRRK target universe drift detected")

    try:
        v1_raw, diagnostics = build_v1_raw(prices)
        features = build_features_no_dominance(prices, frozen)
        v1_model_weights = apply_internal_v1_band(v1_raw)
        v1_returns = portfolio_returns_full(prices, v1_model_weights)
        defensive = current_defensive_state(prices, features, v1_returns, frozen)
    except (TargetMathError, ValueError, FloatingPointError) as exc:
        raise TargetCalculationError(f"Frozen BRRK target calculation failed: {exc}") from exc

    target_date = prices.index[-1]
    raw_row = v1_raw.loc[target_date, list(CANONICAL_ASSETS)].astype(float)
    raw_gross = float(raw_row.abs().sum())
    if raw_gross > 1.0 + 1e-10:
        raise TargetCalculationError(f"Frozen V1 gross exceeded P3.2 cap: {raw_gross}")
    if (raw_row < -1e-12).any():
        raise TargetCalculationError("Frozen P3.2 V1 produced a short target")

    defensive_scale = float(defensive["defensive_scale"])
    target_row = raw_row * defensive_scale
    target_row = target_row.clip(lower=0.0)
    gross = float(target_row.sum())
    if gross > 1.0 + 1e-10:
        raise TargetCalculationError(f"P3.2 target gross exceeded 1.0: {gross}")
    gross = float(np.clip(gross, 0.0, 1.0))
    cash_share = float(np.clip(1.0 - gross, 0.0, 1.0))

    if gross > 1e-15:
        relative = {asset: float(target_row[asset] / gross) for asset in CANONICAL_ASSETS}
    else:
        relative = {asset: 0.0 for asset in CANONICAL_ASSETS}
    target_weights = {asset: float(target_row[asset]) for asset in CANONICAL_ASSETS}

    latest_scores = diagnostics["scores"].loc[target_date]
    latest_trend = diagnostics["trend"]
    v1_snapshot = {
        "raw_gross_before_defense": raw_gross,
        "raw_weights": {asset: float(raw_row[asset]) for asset in CANONICAL_ASSETS},
        "btc_beta": _json_float(diagnostics["beta"].loc[target_date]),
        "btc_trend": _json_float(diagnostics["btc_trend"].loc[target_date]),
        "btc_vol": _json_float(diagnostics["btc_vol"].loc[target_date]),
        "scores": {asset: _json_float(latest_scores[asset]) for asset in ("ETH", "SOL", "BNB")},
        "asset_trends": {
            asset: _json_float(latest_trend[asset].loc[target_date]) for asset in CANONICAL_ASSETS
        },
    }
    refit_date = pd.Timestamp(defensive["refit_date"])
    feature_snapshot = {
        "signal_session": target_date.strftime("%Y-%m-%d"),
        "regime_refit_session": refit_date.strftime("%Y-%m-%d"),
        "regime_features": defensive["feature_snapshot"],
        "v1": v1_snapshot,
        "internal_model_return_band": 0.05,
        "internal_model_return_cost_bps": 5.0,
        "internal_band_is_not_p3_3_execution_control": True,
        "hmm_converged": bool(defensive["converged"]),
        "pca_explained_variance": float(defensive["pca_variance"]),
    }

    return TargetCalculationResult(
        decision_timestamp=daily_dataset.decision_timestamp,
        target_session=target_date.strftime("%Y-%m-%d"),
        target_weights=target_weights,
        relative_weights=relative,
        cash_share=cash_share,
        base_gross_target=gross,
        risk_state=str(defensive["risk_state"]),
        risk_state_probabilities={
            state: float(value) for state, value in defensive["posterior"].items()
        },
        riskoff_probability=float(defensive["riskoff_probability"]),
        meta_scale=float(defensive["meta_scale"]),
        defensive_scale=defensive_scale,
        regime_refit_session=refit_date.strftime("%Y-%m-%d"),
        feature_snapshot=feature_snapshot,
        account_equity_usd=equity,
        current_positions_notional_usd=positions,
        data_contract_schema=daily_dataset.schema_version,
        data_contract_id=daily_dataset.contract_id,
        data_digest=daily_dataset.digest(),
        approved_product_id=config.product_id,
        approved_config_model_version=config.model_version,
    )
