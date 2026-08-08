from __future__ import annotations

"""Phase 8 bear-short research safety and comparison primitives.

Research only.  No exchange/executor imports and no capability to open a short.
"""

from dataclasses import dataclass
from typing import Iterable

CORE_UNIVERSE = ("BTC", "ETH", "SOL", "BNB")
P8_RESEARCH_VERSION = "BEAR-SHORT-0001-V1"


@dataclass(frozen=True)
class ShortCandidateEvidence:
    symbol: str
    contemporaneous_top20: bool
    live_liquidity_ok: bool
    reliable_perp_market: bool
    spread_depth_ok: bool
    funding_non_pathological: bool
    market_structure_ok: bool
    history_days: int


@dataclass(frozen=True)
class ShortEconomics:
    symbol: str
    after_cost_return: float
    max_adverse_excursion: float
    funding_cost: float
    execution_cost: float
    beta_to_btc: float
    crowding_score: float


def candidate_eligible(e: ShortCandidateEvidence) -> bool:
    symbol = e.symbol.upper()
    universe_ok = symbol in CORE_UNIVERSE or e.contemporaneous_top20
    return all((
        universe_ok,
        e.live_liquidity_ok,
        e.reliable_perp_market,
        e.spread_depth_ok,
        e.funding_non_pathological,
        e.market_structure_ok,
        e.history_days >= 90,
    ))


def eligible_symbols(rows: Iterable[ShortCandidateEvidence]) -> tuple[str, ...]:
    return tuple(sorted({r.symbol.upper() for r in rows if candidate_eligible(r)}))


def compare_candidate_to_benchmarks(
    candidate: ShortEconomics,
    *,
    short_btc_after_cost_return: float,
    short_brrk_after_cost_return: float,
) -> dict[str, float | bool | str]:
    """Frozen descriptive comparison; not a promotion/launch function."""
    edge_btc = candidate.after_cost_return - float(short_btc_after_cost_return)
    edge_brrk = candidate.after_cost_return - float(short_brrk_after_cost_return)
    return {
        "symbol": candidate.symbol.upper(),
        "edge_vs_short_btc": edge_btc,
        "edge_vs_short_brrk": edge_brrk,
        "beats_both_benchmarks": edge_btc > 0.0 and edge_brrk > 0.0,
        "research_only": True,
    }
