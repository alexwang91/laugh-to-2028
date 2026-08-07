from __future__ import annotations

"""P3.3 target-to-position rebalance and turnover controls.

This module is deliberately downstream of P3.2. It never recomputes or edits the
BRRK target. The theoretical deviation from the P3.2 target is always measured;
the explicit L1 weight band decides whether that deviation becomes a control
move. Venue minimum notional, quantity precision, routing and order submission
remain downstream execution concerns.
"""

from dataclasses import asdict, dataclass
import hashlib
import json
import math
from pathlib import Path
from typing import Any, Mapping

from .data_contract import CANONICAL_ASSETS
from .target_engine import TARGET_ENGINE_VERSION, TargetCalculationResult


REBALANCE_CONTROL_VERSION = "P3.3-L1-BAND-V1"
FROZEN_REBALANCE_BAND = 0.05
FROZEN_SAFETY_OVERRIDES = {
    "current_short_position": "REBALANCE_TO_P3_2_TARGET_REGARDLESS_OF_BAND",
    "current_gross_above_one": "REBALANCE_TO_P3_2_TARGET_REGARDLESS_OF_BAND",
}
DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[3] / "config" / "rebalance_policy.json"
_EPS = 1e-12


class RebalanceControlError(RuntimeError):
    pass


def _finite_float(value: object, *, field: str) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise RebalanceControlError(f"{field} must be numeric") from exc
    if not math.isfinite(parsed):
        raise RebalanceControlError(f"{field} must be finite")
    return parsed


@dataclass(frozen=True)
class RebalancePolicy:
    schema_version: int
    policy_id: str
    target_gap_metric: str
    rebalance_band: float
    boundary_rule: str
    safety_overrides: dict[str, str]
    minimum_trade_notional_role: str
    authorization: str

    def validate(self) -> None:
        if self.schema_version != 1:
            raise RebalanceControlError("Unsupported rebalance policy schema")
        if self.policy_id != REBALANCE_CONTROL_VERSION:
            raise RebalanceControlError(
                f"Unexpected policy id {self.policy_id!r}; expected {REBALANCE_CONTROL_VERSION!r}"
            )
        if self.target_gap_metric != "L1_ABSOLUTE_WEIGHT_GAP":
            raise RebalanceControlError("P3.3 requires L1 absolute weight-gap banding")
        if not math.isfinite(self.rebalance_band) or not math.isclose(
            self.rebalance_band,
            FROZEN_REBALANCE_BAND,
            rel_tol=0.0,
            abs_tol=1e-15,
        ):
            raise RebalanceControlError(
                f"{REBALANCE_CONTROL_VERSION} freezes rebalance_band at {FROZEN_REBALANCE_BAND}"
            )
        if self.boundary_rule != "REBALANCE_WHEN_L1_GAP_GTE_BAND":
            raise RebalanceControlError("Unexpected P3.3 band boundary rule")
        if self.safety_overrides != FROZEN_SAFETY_OVERRIDES:
            raise RebalanceControlError("P3.3 safety override policy drift detected")
        if self.minimum_trade_notional_role != (
            "DOWNSTREAM_ORDER_FEASIBILITY_ONLY_NOT_P3_3_PORTFOLIO_GATE"
        ):
            raise RebalanceControlError("Minimum-trade role drift detected")
        if self.authorization != "REBALANCE_CONTROL_ONLY_NO_PRODUCTION_AUTHORIZATION":
            raise RebalanceControlError("Unexpected rebalance policy authorization")


def load_rebalance_policy(path: Path | None = None) -> RebalancePolicy:
    raw = json.loads((path or DEFAULT_POLICY_PATH).read_text(encoding="utf-8"))
    policy = RebalancePolicy(
        schema_version=int(raw["schema_version"]),
        policy_id=str(raw["policy_id"]),
        target_gap_metric=str(raw["target_gap_metric"]),
        rebalance_band=float(raw["rebalance_band"]),
        boundary_rule=str(raw["boundary_rule"]),
        safety_overrides={str(k): str(v) for k, v in raw["safety_overrides"].items()},
        minimum_trade_notional_role=str(raw["minimum_trade_notional_role"]),
        authorization=str(raw["authorization"]),
    )
    policy.validate()
    return policy


def _normalize_current_positions(current_positions_notional_usd: Mapping[str, object]) -> dict[str, float]:
    normalized_input = {str(asset).upper(): value for asset, value in current_positions_notional_usd.items()}
    unknown = sorted(set(normalized_input) - set(CANONICAL_ASSETS))
    if unknown:
        raise RebalanceControlError(
            "Current positions contain assets outside the P3.2 target universe: " + ",".join(unknown)
        )
    return {
        asset: _finite_float(normalized_input.get(asset, 0.0), field=f"current_positions[{asset}]")
        for asset in CANONICAL_ASSETS
    }


def _validate_upstream_target(target: TargetCalculationResult) -> dict[str, float]:
    if target.target_engine_version != TARGET_ENGINE_VERSION:
        raise RebalanceControlError(
            f"P3.3 requires {TARGET_ENGINE_VERSION}; got {target.target_engine_version!r}"
        )
    if target.production_authorized:
        raise RebalanceControlError("P3.3 cannot consume a production-authorized target mutation")
    if tuple(target.target_weights) != tuple(CANONICAL_ASSETS):
        raise RebalanceControlError("P3.2 target asset order/universe drift detected")
    weights = {
        asset: _finite_float(target.target_weights[asset], field=f"target_weights[{asset}]")
        for asset in CANONICAL_ASSETS
    }
    if any(value < -_EPS for value in weights.values()):
        raise RebalanceControlError("P3.3 cannot consume a short P3.2 target")
    gross = sum(abs(value) for value in weights.values())
    if gross > 1.0 + _EPS:
        raise RebalanceControlError("P3.3 cannot consume a P3.2 target with gross above 1")
    if not math.isclose(gross, float(target.base_gross_target), rel_tol=0.0, abs_tol=1e-10):
        raise RebalanceControlError("P3.2 target gross does not match target weights")
    return weights


@dataclass(frozen=True)
class RebalanceControlPlan:
    decision_timestamp: str
    upstream_target_digest: str
    upstream_target_engine_version: str
    upstream_model_authority: str
    control_version: str
    policy_id: str
    rebalance_band: float
    boundary_rule: str
    account_equity_usd: float
    upstream_target_account_equity_usd: float
    model_target_weights: dict[str, float]
    model_target_notionals_usd: dict[str, float]
    current_position_weights: dict[str, float]
    current_position_notionals_usd: dict[str, float]
    theoretical_gap_weights: dict[str, float]
    theoretical_gap_notionals_usd: dict[str, float]
    l1_target_gap: float
    theoretical_turnover_weight: float
    current_gross_weight: float
    target_gross_weight: float
    current_net_weight: float
    target_net_weight: float
    safety_override_reasons: tuple[str, ...]
    should_rebalance: bool
    rebalance_reason: str
    post_control_desired_weights: dict[str, float]
    post_control_desired_notionals_usd: dict[str, float]
    proposed_delta_weights: dict[str, float]
    proposed_delta_notionals_usd: dict[str, float]
    control_turnover_weight: float
    suppressed_gap_weights: dict[str, float]
    minimum_trade_notional_role: str
    production_authorized: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)

    def digest(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("utf-8")).hexdigest()


def calculate_rebalance_control(
    *,
    target: TargetCalculationResult,
    account_equity_usd: object,
    current_positions_notional_usd: Mapping[str, object],
    policy: RebalancePolicy | None = None,
) -> RebalanceControlPlan:
    """Apply the explicit P3.3 control band to an immutable P3.2 target.

    The theoretical target gap is always returned, even when the band suppresses
    action. If current state already violates frozen pre-P4 boundaries (short
    exposure or gross > 1), the safety repair bypasses the churn band.
    """
    active_policy = policy or load_rebalance_policy()
    active_policy.validate()
    equity = _finite_float(account_equity_usd, field="account_equity_usd")
    if equity <= 0:
        raise RebalanceControlError("account_equity_usd must be positive")

    target_weights = _validate_upstream_target(target)
    current_notionals = _normalize_current_positions(current_positions_notional_usd)
    current_weights = {asset: current_notionals[asset] / equity for asset in CANONICAL_ASSETS}
    target_notionals = {asset: target_weights[asset] * equity for asset in CANONICAL_ASSETS}

    gap_weights = {asset: target_weights[asset] - current_weights[asset] for asset in CANONICAL_ASSETS}
    gap_notionals = {asset: target_notionals[asset] - current_notionals[asset] for asset in CANONICAL_ASSETS}
    l1_gap = float(sum(abs(value) for value in gap_weights.values()))
    current_gross = float(sum(abs(value) for value in current_weights.values()))
    target_gross = float(sum(abs(value) for value in target_weights.values()))
    current_net = float(sum(current_weights.values()))
    target_net = float(sum(target_weights.values()))

    safety_reasons: list[str] = []
    if any(value < -_EPS for value in current_weights.values()):
        safety_reasons.append("current_short_position")
    if current_gross > 1.0 + _EPS:
        safety_reasons.append("current_gross_above_one")

    if safety_reasons:
        should_rebalance = True
        reason = "safety_override_to_p3_2_target"
    elif l1_gap + _EPS >= active_policy.rebalance_band:
        should_rebalance = True
        reason = "outside_or_at_l1_target_gap_band"
    else:
        should_rebalance = False
        reason = "inside_l1_target_gap_band"

    if should_rebalance:
        desired_weights = dict(target_weights)
        desired_notionals = dict(target_notionals)
        delta_weights = dict(gap_weights)
        delta_notionals = dict(gap_notionals)
        suppressed = {asset: 0.0 for asset in CANONICAL_ASSETS}
    else:
        desired_weights = dict(current_weights)
        desired_notionals = dict(current_notionals)
        delta_weights = {asset: 0.0 for asset in CANONICAL_ASSETS}
        delta_notionals = {asset: 0.0 for asset in CANONICAL_ASSETS}
        suppressed = dict(gap_weights)

    control_turnover = float(sum(abs(value) for value in delta_weights.values()))

    return RebalanceControlPlan(
        decision_timestamp=target.decision_timestamp,
        upstream_target_digest=target.digest(),
        upstream_target_engine_version=target.target_engine_version,
        upstream_model_authority=target.model_authority,
        control_version=REBALANCE_CONTROL_VERSION,
        policy_id=active_policy.policy_id,
        rebalance_band=active_policy.rebalance_band,
        boundary_rule=active_policy.boundary_rule,
        account_equity_usd=equity,
        upstream_target_account_equity_usd=float(target.account_equity_usd),
        model_target_weights=target_weights,
        model_target_notionals_usd=target_notionals,
        current_position_weights=current_weights,
        current_position_notionals_usd=current_notionals,
        theoretical_gap_weights=gap_weights,
        theoretical_gap_notionals_usd=gap_notionals,
        l1_target_gap=l1_gap,
        theoretical_turnover_weight=l1_gap,
        current_gross_weight=current_gross,
        target_gross_weight=target_gross,
        current_net_weight=current_net,
        target_net_weight=target_net,
        safety_override_reasons=tuple(safety_reasons),
        should_rebalance=should_rebalance,
        rebalance_reason=reason,
        post_control_desired_weights=desired_weights,
        post_control_desired_notionals_usd=desired_notionals,
        proposed_delta_weights=delta_weights,
        proposed_delta_notionals_usd=delta_notionals,
        control_turnover_weight=control_turnover,
        suppressed_gap_weights=suppressed,
        minimum_trade_notional_role=active_policy.minimum_trade_notional_role,
    )
