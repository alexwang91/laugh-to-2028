from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation, ROUND_DOWN
from typing import Any, Iterable


PERP_MAX_DECIMALS = 6
SPOT_MAX_DECIMALS = 8
MAX_PRICE_SIGNIFICANT_FIGURES = 5


class InstrumentMetadataError(ValueError):
    """Raised when exchange metadata cannot support deterministic order formatting."""


@dataclass(frozen=True)
class InstrumentMetadata:
    coin: str
    sz_decimals: int
    is_spot: bool = False

    @property
    def max_price_decimals(self) -> int:
        max_decimals = SPOT_MAX_DECIMALS if self.is_spot else PERP_MAX_DECIMALS
        result = max_decimals - self.sz_decimals
        if result < 0:
            raise InstrumentMetadataError(
                f"Invalid szDecimals={self.sz_decimals} for {self.coin}"
            )
        return result


def _decimal(value: float | int | str | Decimal) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise InstrumentMetadataError(f"Invalid numeric value: {value}") from exc


def _plain(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def parse_perp_metadata(meta: dict[str, Any]) -> dict[str, InstrumentMetadata]:
    universe = meta.get("universe") if isinstance(meta, dict) else None
    if not isinstance(universe, list):
        raise InstrumentMetadataError("Hyperliquid meta.universe is missing or malformed")

    parsed: dict[str, InstrumentMetadata] = {}
    for item in universe:
        if not isinstance(item, dict):
            raise InstrumentMetadataError("Hyperliquid meta.universe contains a malformed row")
        name = item.get("name")
        sz_decimals = item.get("szDecimals")
        if not isinstance(name, str) or not name:
            raise InstrumentMetadataError("Hyperliquid metadata row has no valid name")
        if isinstance(sz_decimals, bool) or not isinstance(sz_decimals, int) or sz_decimals < 0:
            raise InstrumentMetadataError(f"Invalid szDecimals for {name}: {sz_decimals}")
        if name in parsed:
            raise InstrumentMetadataError(f"Duplicate Hyperliquid metadata row for {name}")
        parsed[name] = InstrumentMetadata(coin=name, sz_decimals=sz_decimals, is_spot=False)
    return parsed


def require_metadata(
    metadata: dict[str, InstrumentMetadata], required_coins: Iterable[str]
) -> dict[str, InstrumentMetadata]:
    required = tuple(required_coins)
    missing = [coin for coin in required if coin not in metadata]
    if missing:
        raise InstrumentMetadataError(
            f"Hyperliquid metadata is missing required instruments: {', '.join(missing)}"
        )
    return {coin: metadata[coin] for coin in required}


def format_size(
    value: float | int | str | Decimal,
    metadata: InstrumentMetadata,
) -> float:
    """Format order size to exchange szDecimals, conservatively toward zero."""
    quantity = abs(_decimal(value))
    quantum = Decimal(1).scaleb(-metadata.sz_decimals)
    rounded = quantity.quantize(quantum, rounding=ROUND_DOWN)
    if rounded <= 0:
        raise InstrumentMetadataError(
            f"Order size rounds to zero for {metadata.coin} at szDecimals={metadata.sz_decimals}"
        )
    return float(_plain(rounded))


def format_price(
    value: float | int | str | Decimal,
    metadata: InstrumentMetadata,
) -> float:
    """Apply Hyperliquid price constraints: decimal cap plus five significant figures.

    Integer prices are permitted directly. Non-integers are truncated toward zero first
    to the metadata-derived decimal cap, then to at most five significant figures.
    """
    price = _decimal(value)
    if price <= 0:
        raise InstrumentMetadataError("Price must be positive")
    if price == price.to_integral_value():
        return float(price)

    decimal_quantum = Decimal(1).scaleb(-metadata.max_price_decimals)
    capped = price.quantize(decimal_quantum, rounding=ROUND_DOWN)
    if capped <= 0:
        raise InstrumentMetadataError(
            f"Price rounds to zero for {metadata.coin} at max decimals={metadata.max_price_decimals}"
        )

    adjusted = capped.adjusted()
    sig_quantum = Decimal(1).scaleb(adjusted - MAX_PRICE_SIGNIFICANT_FIGURES + 1)
    formatted = capped.quantize(sig_quantum, rounding=ROUND_DOWN)
    if formatted <= 0:
        raise InstrumentMetadataError("Price rounds to zero under significant-figure rules")
    return float(_plain(formatted))
