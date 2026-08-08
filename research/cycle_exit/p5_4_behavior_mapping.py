from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = ROOT / "research" / "cycle_exit" / "p5_4_behavior_mapping_contract.json"
ASSETS = ("BTC", "ETH", "SOL", "BNB")


class P54MappingError(ValueError):
    pass


def load_contract() -> dict:
    c = json.loads(CONTRACT_PATH.read_text())
    if c.get("contract_id") != "P5.4-FIXED-STATE-GROSS-BEHAVIOR-V1":
        raise P54MappingError("unexpected P5.4 contract")
    if c.get("status") != "PREREGISTERED_BEFORE_ANY_P5_5_ECONOMIC_EVALUATION":
        raise P54MappingError("P5.4 contract not frozen")
    return c


def candidate_ids(contract: dict | None = None) -> tuple[str, ...]:
    c = contract or load_contract()
    return tuple(row["id"] for row in c["candidate_maps"])


def multiplier_for_state(candidate_id: str, market_state: str, contract: dict | None = None) -> float:
    c = contract or load_contract()
    if market_state == "DATA_INSUFFICIENT":
        return float(c["composition"]["data_insufficient_multiplier"])
    rows = {row["id"]: row for row in c["candidate_maps"]}
    if candidate_id not in rows:
        raise P54MappingError(f"unknown candidate_id={candidate_id}")
    mapping = rows[candidate_id]["multipliers"]
    if market_state not in mapping:
        raise P54MappingError(f"unknown market_state={market_state}")
    value = float(mapping[market_state])
    if not np.isfinite(value) or not 0.0 <= value <= 1.0:
        raise P54MappingError("invalid frozen multiplier")
    return value


def apply_multiplier_to_target(target: Mapping[str, float], multiplier: float) -> dict[str, float]:
    m = float(multiplier)
    if not np.isfinite(m) or not 0.0 <= m <= 1.0:
        raise P54MappingError("multiplier must be finite in [0,1]")
    missing = [a for a in ASSETS if a not in target]
    extra = [a for a in target if a not in ASSETS]
    if missing or extra:
        raise P54MappingError(f"target must contain exactly {ASSETS}; missing={missing} extra={extra}")
    base = {a: float(target[a]) for a in ASSETS}
    if any(not np.isfinite(v) for v in base.values()):
        raise P54MappingError("target contains non-finite values")
    if any(v < -1e-12 for v in base.values()):
        raise P54MappingError("P5.4 V1 is long-only")
    gross = sum(abs(v) for v in base.values())
    if gross > 1.0 + 1e-9:
        raise P54MappingError("frozen BRRK target gross exceeded 1.0")
    out = {a: base[a] * m for a in ASSETS}
    if sum(abs(v) for v in out.values()) > gross + 1e-12:
        raise P54MappingError("P5.4 multiplier increased gross")
    return out


def apply_candidate_to_targets(
    targets: pd.DataFrame,
    market_states: pd.Series,
    candidate_id: str,
    contract: dict | None = None,
) -> tuple[pd.DataFrame, pd.Series]:
    c = contract or load_contract()
    missing = [a for a in ASSETS if a not in targets.columns]
    extra = [a for a in targets.columns if a not in ASSETS]
    if missing or extra:
        raise P54MappingError(f"targets must contain exactly {ASSETS}; missing={missing} extra={extra}")
    if not targets.index.equals(market_states.index):
        raise P54MappingError("targets and market_states indexes must match exactly")
    t = targets.loc[:, ASSETS].astype(float)
    if not np.isfinite(t.to_numpy()).all():
        raise P54MappingError("targets contain non-finite values")
    if (t < -1e-12).any().any():
        raise P54MappingError("P5.4 V1 is long-only")
    if (t.abs().sum(axis=1) > 1.0 + 1e-9).any():
        raise P54MappingError("frozen BRRK target gross exceeded 1.0")

    multipliers = market_states.astype(str).map(lambda s: multiplier_for_state(candidate_id, s, c)).astype(float)
    out = t.mul(multipliers, axis=0)
    if (out.abs().sum(axis=1) > t.abs().sum(axis=1) + 1e-12).any():
        raise P54MappingError("P5.4 increased gross")
    return out, multipliers


def assert_relative_ranking_preserved(base: pd.DataFrame, adjusted: pd.DataFrame, multipliers: pd.Series) -> None:
    if not base.index.equals(adjusted.index) or not base.index.equals(multipliers.index):
        raise P54MappingError("ranking audit indexes differ")
    for dt in base.index:
        m = float(multipliers.loc[dt])
        b = base.loc[dt, list(ASSETS)].astype(float)
        a = adjusted.loc[dt, list(ASSETS)].astype(float)
        if m == 0.0:
            if not np.allclose(a.to_numpy(), 0.0, rtol=0.0, atol=1e-12):
                raise P54MappingError(f"zero multiplier did not zero target at {dt}")
            continue
        if not np.allclose(a.to_numpy(), b.to_numpy() * m, rtol=0.0, atol=1e-12):
            raise P54MappingError(f"scalar mapping drift at {dt}")
        if list(b.sort_values(kind="stable").index) != list(a.sort_values(kind="stable").index):
            raise P54MappingError(f"relative ranking changed at {dt}")
