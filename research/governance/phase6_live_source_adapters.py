from __future__ import annotations

"""Source-boundary adapters for Phase-6 public/read-only live observations.

Raw response bytes are preserved by the collector before these adapters run.
This module does not alter the frozen P3.1 canonical contract. It only maps a
known Hyperliquid transport timestamp detail (tens of milliseconds after the
nominal hourly funding slot) onto the exact hourly slot required by P3.1, with a
strict one-second maximum tolerance and fail-closed behavior outside it.
"""

import sys
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[2]
BOT_ROOT = ROOT / "execution" / "plan-b-bot"
if str(BOT_ROOT) not in sys.path:
    sys.path.insert(0, str(BOT_ROOT))

from beta_bot.data_contract import (  # noqa: E402
    HOUR_MS,
    DataContractError,
    canonicalize_funding_history,
)


HYPERLIQUID_FUNDING_SLOT_JITTER_TOLERANCE_MS = 1_000


def normalize_hyperliquid_funding_records(
    records: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for record in records:
        try:
            raw_time = int(record["time"])
        except (KeyError, TypeError, ValueError) as exc:
            raise DataContractError("Malformed Hyperliquid funding time") from exc
        nearest_slot = ((raw_time + HOUR_MS // 2) // HOUR_MS) * HOUR_MS
        jitter = abs(raw_time - nearest_slot)
        if jitter > HYPERLIQUID_FUNDING_SLOT_JITTER_TOLERANCE_MS:
            raise DataContractError(
                f"Hyperliquid funding timestamp jitter exceeds tolerance: {jitter}ms"
            )
        row = dict(record)
        row["time"] = nearest_slot
        normalized.append(row)
    return normalized


def canonicalize_hyperliquid_funding_history(
    *,
    asset: str,
    records: Iterable[Mapping[str, Any]],
    router_as_of: object,
    policy: object,
) -> object:
    return canonicalize_funding_history(
        asset=asset,
        records=normalize_hyperliquid_funding_records(records),
        router_as_of=router_as_of,
        policy=policy,
    )
