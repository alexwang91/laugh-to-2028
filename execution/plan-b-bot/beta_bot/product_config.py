from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PRODUCT_CONFIG_PATH = REPO_ROOT / "config" / "product.json"


@dataclass(frozen=True)
class ProductConfig:
    schema_version: int
    product_id: str
    long_universe: tuple[str, ...]
    primary_venue: str
    canonical_timezone: str
    daily_boundary_utc: str
    initial_live_capital_usd: float
    weekly_manual_contribution_usd: float
    catastrophic_drawdown_limit: float
    operating_risk_budget: float | None
    operating_risk_budget_status: str
    leverage_policy: str
    intraday_policy: str
    production_states: tuple[str, ...]
    default_production_state: str
    strategy_release_id: str
    model_version: str
    data_version: str
    require_flat_to_long_approval: bool
    require_flat_to_short_approval: bool
    require_monitor_to_active_approval: bool
    require_first_short_approval: bool
    automatic_risk_reduction_requires_approval: bool

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> "ProductConfig":
        capital = raw["capital"]
        risk = raw["risk"]
        production = raw["production"]
        human = raw["human_approval"]
        config = cls(
            schema_version=int(raw["schema_version"]),
            product_id=str(raw["product_id"]),
            long_universe=tuple(str(x).upper() for x in raw["long_universe"]),
            primary_venue=str(raw["primary_venue"]).lower(),
            canonical_timezone=str(raw["canonical_timezone"]),
            daily_boundary_utc=str(raw["daily_boundary_utc"]),
            initial_live_capital_usd=float(capital["initial_live_capital_usd"]),
            weekly_manual_contribution_usd=float(capital["weekly_manual_contribution_usd"]),
            catastrophic_drawdown_limit=float(risk["catastrophic_drawdown_limit"]),
            operating_risk_budget=(
                None if risk["operating_risk_budget"] is None else float(risk["operating_risk_budget"])
            ),
            operating_risk_budget_status=str(risk["operating_risk_budget_status"]),
            leverage_policy=str(risk["leverage_policy"]),
            intraday_policy=str(risk["intraday_policy"]),
            production_states=tuple(str(x) for x in production["allowed_states"]),
            default_production_state=str(production["default_state"]),
            strategy_release_id=str(production["strategy_release_id"]),
            model_version=str(production["model_version"]),
            data_version=str(production["data_version"]),
            require_flat_to_long_approval=bool(human["flat_to_long"]),
            require_flat_to_short_approval=bool(human["flat_to_short"]),
            require_monitor_to_active_approval=bool(human["monitor_only_to_active"]),
            require_first_short_approval=bool(human["first_short_exposure_new_bear_phase"]),
            automatic_risk_reduction_requires_approval=bool(
                human["automatic_risk_reduction_requires_approval"]
            ),
        )
        config.validate()
        return config

    def validate(self) -> None:
        if self.schema_version != 1:
            raise ValueError("Unsupported product config schema_version")
        if self.long_universe != ("BTC", "ETH", "SOL", "BNB"):
            raise ValueError("Canonical long universe must remain BTC/ETH/SOL/BNB")
        if self.primary_venue != "hyperliquid":
            raise ValueError("Canonical primary venue must be Hyperliquid")
        if self.canonical_timezone != "UTC" or self.daily_boundary_utc != "00:00":
            raise ValueError("Canonical daily boundary must be 00:00 UTC")
        if self.initial_live_capital_usd != 2000.0:
            raise ValueError("Canonical initial live capital must be $2,000")
        if self.weekly_manual_contribution_usd != 100.0:
            raise ValueError("Canonical weekly manual contribution must be $100")
        if self.catastrophic_drawdown_limit != 0.70:
            raise ValueError("Catastrophic drawdown limit must be 70%")
        if self.operating_risk_budget is not None:
            raise ValueError("Operating risk budget must remain unfrozen until P4")
        if self.leverage_policy != "MODEL_DETERMINED":
            raise ValueError("Leverage policy must remain model-determined")
        if self.intraday_policy != "RISK_REDUCTION_ONLY":
            raise ValueError("Intraday policy must be risk-reduction-only")
        expected_states = {"ACTIVE", "MONITOR_ONLY", "SHORT_READY", "STOPPED"}
        if set(self.production_states) != expected_states:
            raise ValueError("Canonical production states are inconsistent")
        if self.default_production_state != "MONITOR_ONLY":
            raise ValueError("Phase-0 default production state must be MONITOR_ONLY")
        if not (
            self.require_flat_to_long_approval
            and self.require_flat_to_short_approval
            and self.require_monitor_to_active_approval
            and self.require_first_short_approval
        ):
            raise ValueError("Directional-risk cycle transitions must require human approval")
        if self.automatic_risk_reduction_requires_approval:
            raise ValueError("Automatic risk reduction must not require human approval")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "product_id": self.product_id,
            "long_universe": list(self.long_universe),
            "primary_venue": self.primary_venue,
            "canonical_timezone": self.canonical_timezone,
            "daily_boundary_utc": self.daily_boundary_utc,
            "initial_live_capital_usd": self.initial_live_capital_usd,
            "weekly_manual_contribution_usd": self.weekly_manual_contribution_usd,
            "catastrophic_drawdown_limit": self.catastrophic_drawdown_limit,
            "operating_risk_budget": self.operating_risk_budget,
            "operating_risk_budget_status": self.operating_risk_budget_status,
            "leverage_policy": self.leverage_policy,
            "intraday_policy": self.intraday_policy,
            "production_states": list(self.production_states),
            "default_production_state": self.default_production_state,
            "strategy_release_id": self.strategy_release_id,
            "model_version": self.model_version,
            "data_version": self.data_version,
            "require_flat_to_long_approval": self.require_flat_to_long_approval,
            "require_flat_to_short_approval": self.require_flat_to_short_approval,
            "require_monitor_to_active_approval": self.require_monitor_to_active_approval,
            "require_first_short_approval": self.require_first_short_approval,
            "automatic_risk_reduction_requires_approval": self.automatic_risk_reduction_requires_approval,
        }


def load_product_config(path: Path | None = None) -> ProductConfig:
    source = path or DEFAULT_PRODUCT_CONFIG_PATH
    raw = json.loads(source.read_text(encoding="utf-8"))
    return ProductConfig.from_mapping(raw)
