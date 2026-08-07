from __future__ import annotations

"""Deterministic Hyperliquid cross-margin liquidation model for LEVERAGE-0040.

Research-only.  Uses the frozen pre-result Hyperliquid margin snapshot and the
official maintenance-margin equations.  It does not infer spot collateral,
Portfolio Margin, route choice, leverage multiplier, or production authority.
"""

from dataclasses import dataclass
import json
import math
from pathlib import Path
from typing import Mapping


ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = ROOT / "research" / "leverage_0039" / "hyperliquid_margin_snapshot.json"
TARGET_ASSETS = ("BTC", "ETH", "SOL", "BNB")
EXPECTED_RELEVANT_HASH = "38060892f1976315084de4dc4ed1c9f3885d909ffccc47bce7ad589315d8b9dd"
BISECTION_ITERATIONS = 80


class LiquidationModelError(ValueError):
    pass


@dataclass(frozen=True)
class MarginTier:
    lower_bound_usd: float
    max_leverage: float
    maintenance_margin_rate: float
    maintenance_deduction_usd: float


@dataclass(frozen=True)
class CrossMarginState:
    account_equity_usd: float
    maintenance_margin_usd: float
    margin_buffer_usd: float
    stressed_abs_notionals_usd: dict[str, float]
    per_asset_maintenance_margin_usd: dict[str, float]
    liquidatable: bool


@dataclass(frozen=True)
class LiquidationDistance:
    liquidates_within_domain: bool
    stress_scale: float | None
    uniform_down_move_fraction: float | None
    state_at_boundary: CrossMarginState | None


def _finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise LiquidationModelError(f"{name} must be finite")
    return value


def load_frozen_snapshot(path: Path = SNAPSHOT_PATH) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("snapshot_id") != "HYPERLIQUID-MAINNET-MARGIN-META-P4.3-V1":
        raise LiquidationModelError("Unexpected Hyperliquid margin snapshot id")
    if data.get("relevant_margin_inputs_sha256") != EXPECTED_RELEVANT_HASH:
        raise LiquidationModelError("Frozen Hyperliquid margin snapshot hash mismatch")
    if data.get("production_authorized") is not False:
        raise LiquidationModelError("Margin snapshot must not carry production authorization")
    return data


def _raw_tiers_for_asset(snapshot: dict, asset: str) -> list[dict]:
    relevant = snapshot.get("relevant_margin_inputs")
    if not isinstance(relevant, dict):
        raise LiquidationModelError("Missing relevant_margin_inputs")
    assets = relevant.get("assets")
    if not isinstance(assets, dict) or asset not in assets:
        raise LiquidationModelError(f"Frozen margin snapshot missing asset {asset}")
    row = assets[asset]
    if not isinstance(row, dict):
        raise LiquidationModelError(f"Malformed margin asset row for {asset}")
    if bool(row.get("isDelisted", False)):
        raise LiquidationModelError(f"Asset {asset} is delisted in frozen snapshot")

    table_id = row.get("marginTableId")
    max_leverage = row.get("maxLeverage")
    if isinstance(table_id, bool) or not isinstance(table_id, int):
        raise LiquidationModelError(f"Invalid marginTableId for {asset}")
    if isinstance(max_leverage, bool) or not isinstance(max_leverage, int) or max_leverage <= 0:
        raise LiquidationModelError(f"Invalid maxLeverage for {asset}")

    if table_id < 50:
        if table_id != max_leverage:
            raise LiquidationModelError(
                f"Single-tier table id/max leverage disagreement for {asset}"
            )
        return [{"lowerBound": "0.0", "maxLeverage": max_leverage}]

    tables = relevant.get("marginTables")
    if not isinstance(tables, dict) or str(table_id) not in tables:
        raise LiquidationModelError(f"Referenced margin table {table_id} missing for {asset}")
    table = tables[str(table_id)]
    if not isinstance(table, dict) or not isinstance(table.get("marginTiers"), list):
        raise LiquidationModelError(f"Malformed margin table {table_id} for {asset}")
    return table["marginTiers"]


def margin_tiers(asset: str, snapshot: dict | None = None) -> tuple[MarginTier, ...]:
    if asset not in TARGET_ASSETS:
        raise LiquidationModelError(f"Unsupported asset {asset}")
    snapshot = snapshot or load_frozen_snapshot()
    raw = _raw_tiers_for_asset(snapshot, asset)
    if not raw:
        raise LiquidationModelError(f"No margin tiers for {asset}")

    parsed: list[tuple[float, float, float]] = []
    for index, row in enumerate(raw):
        if not isinstance(row, dict):
            raise LiquidationModelError(f"Malformed tier row for {asset}")
        lower = _finite(f"{asset}.tier[{index}].lowerBound", row.get("lowerBound"))
        lev = _finite(f"{asset}.tier[{index}].maxLeverage", row.get("maxLeverage"))
        if lower < 0.0 or lev <= 0.0:
            raise LiquidationModelError(f"Invalid tier values for {asset}")
        mmr = 1.0 / (2.0 * lev)
        parsed.append((lower, lev, mmr))

    parsed.sort(key=lambda x: x[0])
    if parsed[0][0] != 0.0:
        raise LiquidationModelError(f"First margin tier for {asset} must begin at zero")
    if any(parsed[i][0] <= parsed[i - 1][0] for i in range(1, len(parsed))):
        raise LiquidationModelError(f"Margin tier lower bounds are not strictly increasing for {asset}")

    out: list[MarginTier] = []
    deduction = 0.0
    previous_mmr = parsed[0][2]
    for index, (lower, lev, mmr) in enumerate(parsed):
        if index:
            deduction += lower * (mmr - previous_mmr)
        out.append(
            MarginTier(
                lower_bound_usd=lower,
                max_leverage=lev,
                maintenance_margin_rate=mmr,
                maintenance_deduction_usd=deduction,
            )
        )
        previous_mmr = mmr
    return tuple(out)


def active_margin_tier(asset: str, abs_notional_usd: float, snapshot: dict | None = None) -> MarginTier:
    notional = _finite("abs_notional_usd", abs_notional_usd)
    if notional < 0.0:
        raise LiquidationModelError("abs_notional_usd cannot be negative")
    tiers = margin_tiers(asset, snapshot)
    active = tiers[0]
    for tier in tiers[1:]:
        if notional >= tier.lower_bound_usd:
            active = tier
        else:
            break
    return active


def maintenance_margin_usd(asset: str, abs_notional_usd: float, snapshot: dict | None = None) -> float:
    notional = _finite("abs_notional_usd", abs_notional_usd)
    if notional < 0.0:
        raise LiquidationModelError("abs_notional_usd cannot be negative")
    if notional == 0.0:
        return 0.0
    tier = active_margin_tier(asset, notional, snapshot)
    margin = notional * tier.maintenance_margin_rate - tier.maintenance_deduction_usd
    if margin < -1e-8:
        raise LiquidationModelError("Computed negative maintenance margin")
    return float(max(margin, 0.0))


def evaluate_cross_margin_state(
    *,
    current_cross_account_equity_usd: float,
    current_long_perp_notionals_usd: Mapping[str, float],
    relative_mark_returns: Mapping[str, float],
    snapshot: dict | None = None,
) -> CrossMarginState:
    """Evaluate cross-margin equity/maintenance after a mark-price stress.

    LEVERAGE-0040 V1 is long-only.  Notionals are positive current mark notionals;
    relative returns apply to the same fixed position sizes.
    """

    snapshot = snapshot or load_frozen_snapshot()
    equity0 = _finite("current_cross_account_equity_usd", current_cross_account_equity_usd)
    if equity0 <= 0.0:
        raise LiquidationModelError("current_cross_account_equity_usd must be positive")
    if set(current_long_perp_notionals_usd) - set(TARGET_ASSETS):
        raise LiquidationModelError("Unsupported asset in perp notionals")
    if set(relative_mark_returns) != set(current_long_perp_notionals_usd):
        raise LiquidationModelError("Stress returns must exactly match provided perp notionals")

    stressed_notionals: dict[str, float] = {}
    per_asset_mm: dict[str, float] = {}
    pnl = 0.0
    for asset, raw_notional in current_long_perp_notionals_usd.items():
        notional = _finite(f"{asset}.notional", raw_notional)
        if notional < 0.0:
            raise LiquidationModelError("LEVERAGE-0040 liquidation V1 rejects short notionals")
        r = _finite(f"{asset}.relative_mark_return", relative_mark_returns[asset])
        if r <= -1.0:
            raise LiquidationModelError("relative_mark_return must remain greater than -1")
        pnl += notional * r
        stressed = notional * (1.0 + r)
        stressed_notionals[asset] = float(stressed)
        per_asset_mm[asset] = maintenance_margin_usd(asset, stressed, snapshot)

    equity = float(equity0 + pnl)
    total_mm = float(sum(per_asset_mm.values()))
    buffer = float(equity - total_mm)
    return CrossMarginState(
        account_equity_usd=equity,
        maintenance_margin_usd=total_mm,
        margin_buffer_usd=buffer,
        stressed_abs_notionals_usd=stressed_notionals,
        per_asset_maintenance_margin_usd=per_asset_mm,
        liquidatable=bool(equity <= total_mm),
    )


def stress_ray_liquidation_distance(
    *,
    current_cross_account_equity_usd: float,
    current_long_perp_notionals_usd: Mapping[str, float],
    stress_direction: Mapping[str, float],
    max_stress_scale: float | None = None,
    snapshot: dict | None = None,
) -> LiquidationDistance:
    """Find the first liquidation point along a fixed relative-return stress ray."""

    snapshot = snapshot or load_frozen_snapshot()
    if not current_long_perp_notionals_usd:
        return LiquidationDistance(False, None, None, None)
    if set(stress_direction) != set(current_long_perp_notionals_usd):
        raise LiquidationModelError("stress_direction must match provided perp notionals")

    direction = {asset: _finite(f"{asset}.stress_direction", value) for asset, value in stress_direction.items()}
    if not any(value < 0.0 for value in direction.values()):
        raise LiquidationModelError("stress ray must contain an adverse negative return component")

    start = evaluate_cross_margin_state(
        current_cross_account_equity_usd=current_cross_account_equity_usd,
        current_long_perp_notionals_usd=current_long_perp_notionals_usd,
        relative_mark_returns={asset: 0.0 for asset in current_long_perp_notionals_usd},
        snapshot=snapshot,
    )
    if start.liquidatable:
        raise LiquidationModelError("Starting cross-margin state is already liquidatable")

    price_positive_limit = min(
        (1.0 - 1e-12) / (-value)
        for value in direction.values()
        if value < 0.0
    )
    if max_stress_scale is None:
        high = price_positive_limit
    else:
        high = min(_finite("max_stress_scale", max_stress_scale), price_positive_limit)
        if high <= 0.0:
            raise LiquidationModelError("max_stress_scale must be positive")

    def state(scale: float) -> CrossMarginState:
        return evaluate_cross_margin_state(
            current_cross_account_equity_usd=current_cross_account_equity_usd,
            current_long_perp_notionals_usd=current_long_perp_notionals_usd,
            relative_mark_returns={asset: scale * direction[asset] for asset in direction},
            snapshot=snapshot,
        )

    high_state = state(high)
    if not high_state.liquidatable:
        return LiquidationDistance(False, None, None, high_state)

    low = 0.0
    for _ in range(BISECTION_ITERATIONS):
        midpoint = 0.5 * (low + high)
        if state(midpoint).liquidatable:
            high = midpoint
        else:
            low = midpoint
    boundary = state(high)

    uniform = None
    values = list(direction.values())
    if values and all(math.isclose(value, -1.0, rel_tol=0.0, abs_tol=1e-15) for value in values):
        uniform = float(high)
    return LiquidationDistance(True, float(high), uniform, boundary)


def uniform_long_down_liquidation_distance(
    *,
    current_cross_account_equity_usd: float,
    current_long_perp_notionals_usd: Mapping[str, float],
    snapshot: dict | None = None,
) -> LiquidationDistance:
    return stress_ray_liquidation_distance(
        current_cross_account_equity_usd=current_cross_account_equity_usd,
        current_long_perp_notionals_usd=current_long_perp_notionals_usd,
        stress_direction={asset: -1.0 for asset in current_long_perp_notionals_usd},
        snapshot=snapshot,
    )
