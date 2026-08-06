"""Research-side adapter for the canonical P3.1 data contract.

This module intentionally contains no independent transformation logic. It makes
research replays consume the exact same implementation that the live package will
consume in P3.2, preventing research/live drift from duplicated candle handling.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
EXECUTION_PACKAGE_ROOT = REPO_ROOT / "execution" / "plan-b-bot"
if str(EXECUTION_PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(EXECUTION_PACKAGE_ROOT))

from beta_bot.data_contract import (  # noqa: E402
    CanonicalDailyDataset,
    DataContractPolicy,
    build_canonical_daily_dataset,
    load_data_contract,
)


def load_research_data_contract() -> DataContractPolicy:
    return load_data_contract(REPO_ROOT / "config" / "data_contract.json")


def canonicalize_research_daily_history(
    *,
    source_batches: dict[str, Sequence[tuple[str, Sequence[Sequence[object]]]]],
    decision_timestamp: str,
) -> CanonicalDailyDataset:
    """Canonicalize historical BRRK daily data using the shared P3.1 implementation."""
    return build_canonical_daily_dataset(
        source_batches=source_batches,
        decision_timestamp=decision_timestamp,
        policy=load_research_data_contract(),
    )
