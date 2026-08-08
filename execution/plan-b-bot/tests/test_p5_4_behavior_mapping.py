from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from research.cycle_exit.p5_4_behavior_mapping import (
    ASSETS,
    P54MappingError,
    apply_candidate_to_targets,
    apply_multiplier_to_target,
    assert_relative_ranking_preserved,
    candidate_ids,
    load_contract,
    multiplier_for_state,
)


def test_candidate_ids_are_exactly_preregistered_family():
    assert candidate_ids() == ("HARD_ONLY", "GENTLE", "BALANCED", "DEFENSIVE")


def test_every_candidate_matches_frozen_contract_values():
    c = load_contract()
    for row in c["candidate_maps"]:
        for state, expected in row["multipliers"].items():
            assert multiplier_for_state(row["id"], state, c) == expected
    for candidate in candidate_ids(c):
        assert multiplier_for_state(candidate, "DATA_INSUFFICIENT", c) == 0.0


def test_scalar_mapping_never_increases_gross_or_changes_proportions():
    target = {"BTC": 0.40, "ETH": 0.30, "SOL": 0.20, "BNB": 0.10}
    out = apply_multiplier_to_target(target, 0.55)
    assert np.isclose(sum(out.values()), 0.55)
    for asset in ASSETS:
        assert np.isclose(out[asset], target[asset] * 0.55)


def test_frame_mapping_preserves_relative_ranking_and_unit_gross():
    idx = pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"])
    targets = pd.DataFrame(
        [[0.4,0.3,0.2,0.1],[0.2,0.4,0.3,0.1],[0.1,0.2,0.6,0.1],[0.25,0.25,0.25,0.25]],
        index=idx,
        columns=ASSETS,
    )
    states = pd.Series(["NORMAL_BULL", "LATE_BULL_ROTATION", "DE_RISK_1", "FLAT"], index=idx)
    adjusted, m = apply_candidate_to_targets(targets, states, "BALANCED")
    assert list(m) == [1.0, 0.90, 0.55, 0.0]
    assert (adjusted.abs().sum(axis=1) <= targets.abs().sum(axis=1) + 1e-12).all()
    assert_relative_ranking_preserved(targets, adjusted, m)


def test_flat_and_data_insufficient_zero_targets():
    idx = pd.to_datetime(["2026-01-01", "2026-01-02"])
    targets = pd.DataFrame([[0.4,0.3,0.2,0.1],[0.4,0.3,0.2,0.1]], index=idx, columns=ASSETS)
    states = pd.Series(["FLAT", "DATA_INSUFFICIENT"], index=idx)
    adjusted, m = apply_candidate_to_targets(targets, states, "GENTLE")
    assert list(m) == [0.0, 0.0]
    assert np.allclose(adjusted.to_numpy(), 0.0)


def test_rejects_gross_above_one_and_short_target():
    try:
        apply_multiplier_to_target({"BTC":0.6,"ETH":0.4,"SOL":0.1,"BNB":0.0}, 0.5)
        raise AssertionError("expected gross error")
    except P54MappingError:
        pass
    try:
        apply_multiplier_to_target({"BTC":0.4,"ETH":0.3,"SOL":-0.1,"BNB":0.1}, 0.5)
        raise AssertionError("expected long-only error")
    except P54MappingError:
        pass
