from __future__ import annotations

from dataclasses import asdict, dataclass
from math import isfinite
from typing import Any, Iterable, Literal

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
    source: str = "Hyperliquid tier-0 base rate; no staking/referral/account-tier discount"

    def fee_bps(self, route: RouteType, style: OrderStyle) -> float:
        return float(getattr(self, f"{route}_{style}_bps"))


@dataclass(frozen=True)
class BookExecutionDiagnostics:
    reference_notional_usd: float
    target_quantity: float
    best_bid: float
    best_ask: float
    mid_price: float
    spread_bps: float
    buy_vwap: float
    sell_vwap: float
    buy_total_impact_bps: float
    sell_total_impact_bps: float
    entry_slippage_beyond_half_spread_bps: float
    exit_slippage_beyond_half_spread_bps: float
    bid_depth_usd: float
    ask_depth_usd: float
    two_sided_depth_usd: float

    @property
    def round_trip_vwap_impact_bps(self) -> float:
        return self.buy_total_impact_bps + self.sell_total_impact_bps


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
        if self.route not in {"spot", "perp"}:
            raise RouteCostError("route must be spot or perp")
        if self.order_style not in {"taker", "maker"}:
            raise RouteCostError("order_style must be taker or maker")
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
        if self.route == "spot" and (
            abs(self.entry_basis_bps) > 1e-12 or abs(self.expected_exit_basis_bps) > 1e-12
        ):
            raise RouteCostError("spot route cannot carry perp basis")


@dataclass(frozen=True)
class RouteCostEstimate:
    asset: str
    route: RouteType
    holding_hours: float
    execution_fee_bps: float
    spread_cost_bps: float
    slippage_cost_bps: float
    observed_vwap_impact_bps: float
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
    """Estimate normalized round-trip implementation cost for one long exposure.

    Sign/measurement contract:
    - positive perp funding means the long pays; negative funding is a benefit;
    - positive entry basis means perp is above verified spot. Entry basis minus
      expected exit basis is the relative-performance cost versus spot;
    - quoted spread is charged as half-spread on entry plus half-spread on exit;
    - entry/exit slippage is measured *beyond* quoted half-spread;
    - vwap_impact_bps is diagnostic and is not charged a second time;
    - fee cost is normalized to entry notional and assumes the selected order
      style on both entry and exit. P2.4 may supply different route scenarios.
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
        observed_vwap_impact_bps=observation.vwap_impact_bps,
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
    """Hours until positive long funding offsets spot's higher non-funding cost."""
    if positive_funding_bps_per_hour <= 0:
        return None
    gap = spot_nonfunding_cost_bps - perp_nonfunding_cost_bps
    if gap <= 0:
        return 0.0
    return gap / positive_funding_bps_per_hour


def funding_decimal_to_bps_per_hour(rate: float) -> float:
    """Convert Hyperliquid hourly funding decimal (e.g. 0.0000125) to bps/hour."""
    value = float(rate)
    if not isfinite(value):
        raise RouteCostError("funding rate must be finite")
    return value * 10_000.0


def average_funding_bps_per_hour(rates: Iterable[float]) -> float:
    converted = [funding_decimal_to_bps_per_hour(rate) for rate in rates]
    if not converted:
        raise RouteCostError("at least one funding observation is required")
    return sum(converted) / len(converted)


def basis_bps(*, perp_price: float, verified_spot_price: float) -> float:
    perp = float(perp_price)
    spot = float(verified_spot_price)
    if not isfinite(perp) or not isfinite(spot) or perp <= 0 or spot <= 0:
        raise RouteCostError("basis prices must be finite and positive")
    return (perp / spot - 1.0) * 10_000.0


def analyze_l2_book(book: dict[str, Any], *, notional_usd: float) -> BookExecutionDiagnostics:
    """Compute reproducible taker execution geometry from a Hyperliquid l2Book snapshot.

    Hyperliquid returns bids in levels[0] and asks in levels[1]. The API exposes
    at most 20 levels per side, so inability to fill the target quantity from the
    returned snapshot is treated as an explicit capacity failure rather than
    extrapolating unseen liquidity.
    """
    if not isfinite(float(notional_usd)) or notional_usd <= 0:
        raise RouteCostError("notional_usd must be positive")
    levels = book.get("levels") if isinstance(book, dict) else None
    if not isinstance(levels, list) or len(levels) != 2:
        raise RouteCostError("l2Book must contain bid and ask levels")
    bids = _parse_levels(levels[0], side="bid")
    asks = _parse_levels(levels[1], side="ask")
    if not bids or not asks:
        raise RouteCostError("l2Book requires non-empty bid and ask sides")
    bids.sort(key=lambda x: x[0], reverse=True)
    asks.sort(key=lambda x: x[0])
    best_bid = bids[0][0]
    best_ask = asks[0][0]
    if best_bid >= best_ask:
        raise RouteCostError("l2Book is crossed or locked")
    mid = (best_bid + best_ask) / 2.0
    target_quantity = notional_usd / mid
    buy_vwap = _vwap_for_quantity(asks, target_quantity)
    sell_vwap = _vwap_for_quantity(bids, target_quantity)
    spread_bps = (best_ask - best_bid) / mid * 10_000.0
    half_spread_bps = spread_bps / 2.0
    buy_total = max((buy_vwap - mid) / mid * 10_000.0, 0.0)
    sell_total = max((mid - sell_vwap) / mid * 10_000.0, 0.0)
    entry_beyond = max(buy_total - half_spread_bps, 0.0)
    exit_beyond = max(sell_total - half_spread_bps, 0.0)
    bid_depth = sum(px * qty for px, qty in bids)
    ask_depth = sum(px * qty for px, qty in asks)
    return BookExecutionDiagnostics(
        reference_notional_usd=float(notional_usd),
        target_quantity=target_quantity,
        best_bid=best_bid,
        best_ask=best_ask,
        mid_price=mid,
        spread_bps=spread_bps,
        buy_vwap=buy_vwap,
        sell_vwap=sell_vwap,
        buy_total_impact_bps=buy_total,
        sell_total_impact_bps=sell_total,
        entry_slippage_beyond_half_spread_bps=entry_beyond,
        exit_slippage_beyond_half_spread_bps=exit_beyond,
        bid_depth_usd=bid_depth,
        ask_depth_usd=ask_depth,
        two_sided_depth_usd=min(bid_depth, ask_depth),
    )


def observation_from_l2_book(
    *,
    asset: str,
    route: RouteType,
    book: dict[str, Any],
    notional_usd: float,
    holding_hours: float,
    order_style: OrderStyle = "taker",
    funding_bps_per_hour: float = 0.0,
    entry_basis_bps: float = 0.0,
    expected_exit_basis_bps: float = 0.0,
    custody_redemption_bps: float = 0.0,
) -> RouteObservation:
    diagnostics = analyze_l2_book(book, notional_usd=notional_usd)
    return RouteObservation(
        asset=asset,
        route=route,
        notional_usd=notional_usd,
        holding_hours=holding_hours,
        order_style=order_style,
        spread_bps=diagnostics.spread_bps,
        entry_slippage_bps=diagnostics.entry_slippage_beyond_half_spread_bps,
        exit_slippage_bps=diagnostics.exit_slippage_beyond_half_spread_bps,
        live_depth_usd=diagnostics.two_sided_depth_usd,
        vwap_impact_bps=diagnostics.round_trip_vwap_impact_bps,
        funding_bps_per_hour=funding_bps_per_hour,
        entry_basis_bps=entry_basis_bps,
        expected_exit_basis_bps=expected_exit_basis_bps,
        custody_redemption_bps=custody_redemption_bps,
    )


def _parse_levels(raw: Any, *, side: str) -> list[tuple[float, float]]:
    if not isinstance(raw, list):
        raise RouteCostError(f"l2Book {side} levels must be a list")
    parsed: list[tuple[float, float]] = []
    for level in raw:
        if not isinstance(level, dict):
            raise RouteCostError(f"l2Book {side} level must be an object")
        try:
            px = float(level["px"])
            qty = float(level["sz"])
        except (KeyError, TypeError, ValueError) as exc:
            raise RouteCostError(f"invalid l2Book {side} level") from exc
        if not isfinite(px) or not isfinite(qty) or px <= 0 or qty <= 0:
            raise RouteCostError(f"invalid l2Book {side} price/size")
        parsed.append((px, qty))
    return parsed


def _vwap_for_quantity(levels: list[tuple[float, float]], quantity: float) -> float:
    remaining = quantity
    filled = 0.0
    notional = 0.0
    for px, available in levels:
        take = min(remaining, available)
        filled += take
        notional += take * px
        remaining -= take
        if remaining <= max(quantity * 1e-12, 1e-15):
            break
    if remaining > max(quantity * 1e-12, 1e-15) or filled <= 0:
        raise RouteCostError("target notional exceeds returned l2Book depth")
    return notional / filled
