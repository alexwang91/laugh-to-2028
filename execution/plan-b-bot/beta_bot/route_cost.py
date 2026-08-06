from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Literal

RouteType = Literal["spot", "perp"]
OrderStyle = Literal["taker", "maker"]


class RouteCostError(ValueError):
    """Route-cost inputs are incomplete or economically inconsistent."""


@dataclass(frozen=True)
class FeeSchedule:
    spot_taker_bps: float = 7.0
    spot_maker_bps: float = 4.0
    perp_taker_bps: float = 4.5
    perp_maker_bps: float = 1.5
    source: str = "Hyperliquid tier-0 base rate; no staking discount"

    def fee_bps(self, route: RouteType, style: OrderStyle) -> float:
        return float(getattr(self, f"{route}_{style}_bps"))


@dataclass(frozen=True)
class RouteObservation:
    asset: str
    route: RouteType
    notional_usd: float
    holding_hours: float
    order_style: OrderStyle
    spread_bps: float
    entry_slippage_bps: float
    exit_slippage_bps: float
    live_depth_usd: float
    vwap_impact_bps: float
    funding_bps_per_hour: float = 0.0
    entry_basis_bps: float = 0.0
    expected_exit_basis_bps: float = 0.0
    custody_redemption_bps: float = 0.0

    def validate(self) -> None:
        values = {
            "notional_usd": self.notional_usd,
            "holding_hours": self.holding_hours,
            "spread_bps": self.spread_bps,
            "entry_slippage_bps": self.entry_slippage_bps,
            "exit_slippage_bps": self.exit_slippage_bps,
            "live_depth_usd": self.live_depth_usd,
            "vwap_impact_bps": self.vwap_impact_bps,
            "funding_bps_per_hour": self.funding_bps_per_hour,
            "entry_basis_bps": self.entry_basis_bps,
            "expected_exit_basis_bps": self.expected_exit_basis_bps,
            "custody_redemption_bps": self.custody_redemption_bps,
        }
        if any(not isfinite(float(value)) for value in values.values()):
            raise RouteCostError("Route-cost inputs must be finite")
        if self.notional_usd <= 0:
            raise RouteCostError("notional_usd must be positive")
        if self.holding_hours < 0:
            raise RouteCostError("holding_hours cannot be negative")
        if self.live_depth_usd < 0:
            raise RouteCostError("live_depth_usd cannot be negative")
        for name in (
            "spread_bps",
            "entry_slippage_bps",
            "exit_slippage_bps",
            "vwap_impact_bps",
            "custody_redemption_bps",
        ):
            if float(getattr(self, name)) < 0:
                raise RouteCostError(f"{name} cannot be negative")
        if self.route == "spot" and abs(self.funding_bps_per_hour) > 1e-12:
            raise RouteCostError("spot route cannot carry perp funding")


@dataclass(frozen=True)
class RouteCostEstimate:
    asset: str
    route: RouteType
    holding_hours: float
    execution_fee_bps: float
    spread_cost_bps: float
    slippage_cost_bps: float
    vwap_impact_bps: float
    funding_cost_bps: float
    basis_cost_bps: float
    custody_redemption_bps: float
    total_cost_bps: float
    total_cost_usd: float
    notional_to_depth_ratio: float | None

    def to_dict(self) -> dict:
        return asdict(self)


def estimate_route_cost(
    observation: RouteObservation,
    *,
    fees: FeeSchedule | None = None,
) -> RouteCostEstimate:
    """Estimate round-trip implementation cost for one economic long exposure.

    Sign conventions:
    - positive perp funding means the long pays and is a cost;
    - negative funding is a benefit and reduces total cost;
    - positive entry basis means perp trades above spot; if expected exit basis is
      lower, the compression is a cost to the long. Basis cost is therefore
      entry_basis_bps - expected_exit_basis_bps.
    - spread is charged as half-spread on entry plus half-spread on exit, so the
      round-trip spread contribution equals one observed full spread.
    """
    observation.validate()
    fee_schedule = fees or FeeSchedule()
    execution_fee_bps = 2.0 * fee_schedule.fee_bps(
        observation.route, observation.order_style
    )
    spread_cost_bps = observation.spread_bps
    slippage_cost_bps = observation.entry_slippage_bps + observation.exit_slippage_bps
    funding_cost_bps = (
        observation.funding_bps_per_hour * observation.holding_hours
        if observation.route == "perp"
        else 0.0
    )
    basis_cost_bps = (
        observation.entry_basis_bps - observation.expected_exit_basis_bps
        if observation.route == "perp"
        else 0.0
    )
    custody_cost_bps = observation.custody_redemption_bps if observation.route == "spot" else 0.0
    total_cost_bps = (
        execution_fee_bps
        + spread_cost_bps
        + slippage_cost_bps
        + observation.vwap_impact_bps
        + funding_cost_bps
        + basis_cost_bps
        + custody_cost_bps
    )
    depth_ratio = (
        observation.notional_usd / observation.live_depth_usd
        if observation.live_depth_usd > 0
        else None
    )
    return RouteCostEstimate(
        asset=observation.asset.upper(),
        route=observation.route,
        holding_hours=observation.holding_hours,
        execution_fee_bps=execution_fee_bps,
        spread_cost_bps=spread_cost_bps,
        slippage_cost_bps=slippage_cost_bps,
        vwap_impact_bps=observation.vwap_impact_bps,
        funding_cost_bps=funding_cost_bps,
        basis_cost_bps=basis_cost_bps,
        custody_redemption_bps=custody_cost_bps,
        total_cost_bps=total_cost_bps,
        total_cost_usd=observation.notional_usd * total_cost_bps / 10_000.0,
        notional_to_depth_ratio=depth_ratio,
    )


@dataclass(frozen=True)
class RouteComparison:
    asset: str
    holding_hours: float
    spot: RouteCostEstimate
    perp: RouteCostEstimate
    spot_minus_perp_bps: float
    lower_cost_route: RouteType | Literal["tie"]

    def to_dict(self) -> dict:
        return {
            "asset": self.asset,
            "holding_hours": self.holding_hours,
            "spot": self.spot.to_dict(),
            "perp": self.perp.to_dict(),
            "spot_minus_perp_bps": self.spot_minus_perp_bps,
            "lower_cost_route": self.lower_cost_route,
        }


def compare_spot_perp(
    spot: RouteObservation,
    perp: RouteObservation,
    *,
    fees: FeeSchedule | None = None,
) -> RouteComparison:
    if spot.route != "spot" or perp.route != "perp":
        raise RouteCostError("compare_spot_perp requires spot then perp observations")
    if spot.asset.upper() != perp.asset.upper():
        raise RouteCostError("spot/perp observations must represent the same asset")
    if abs(spot.notional_usd - perp.notional_usd) > 1e-9:
        raise RouteCostError("spot/perp comparison requires equal economic notional")
    if abs(spot.holding_hours - perp.holding_hours) > 1e-9:
        raise RouteCostError("spot/perp comparison requires equal holding horizon")
    spot_cost = estimate_route_cost(spot, fees=fees)
    perp_cost = estimate_route_cost(perp, fees=fees)
    difference = spot_cost.total_cost_bps - perp_cost.total_cost_bps
    lower: RouteType | Literal["tie"]
    if abs(difference) <= 1e-9:
        lower = "tie"
    else:
        lower = "spot" if difference < 0 else "perp"
    return RouteComparison(
        asset=spot.asset.upper(),
        holding_hours=spot.holding_hours,
        spot=spot_cost,
        perp=perp_cost,
        spot_minus_perp_bps=difference,
        lower_cost_route=lower,
    )


def funding_break_even_hours(
    *,
    spot_nonfunding_cost_bps: float,
    perp_nonfunding_cost_bps: float,
    positive_funding_bps_per_hour: float,
) -> float | None:
    """Hours until positive long funding offsets spot's higher non-funding cost.

    Returns 0 when spot is already cheaper before funding and None when positive
    funding cannot produce a crossover.
    """
    if positive_funding_bps_per_hour <= 0:
        return None
    gap = spot_nonfunding_cost_bps - perp_nonfunding_cost_bps
    if gap <= 0:
        return 0.0
    return gap / positive_funding_bps_per_hour
