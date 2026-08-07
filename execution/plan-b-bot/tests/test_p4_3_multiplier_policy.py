from __future__ import annotations

import json
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research" / "leverage_0040"
if str(RESEARCH) not in sys.path:
    sys.path.insert(0, str(RESEARCH))

from multiplier_policy import (  # noqa: E402
    ALLOWED_CAPS,
    MultiplierPolicyError,
    final_scale,
    leverage_multiplier,
)


ADDENDUM = ROOT / "research" / "leverage_0040" / "LEVERAGE-0040-PRE-RUN-ADDENDUM-V1.json"


def test_multiplier_policy_is_frozen_before_first_result():
    data = json.loads(ADDENDUM.read_text(encoding="utf-8"))
    assert data["addendum_id"] == "LEVERAGE-0040-PRE-RUN-ADDENDUM-V1"
    assert data["status"] == "FROZEN_BEFORE_FIRST_0040_SEARCH"
    assert data["result_observation_before_freeze"] is False
    assert data["leverage_search_run"] is False
    assert data["production_authorized"] is False
    policy = data["multiplier_policy"]
    assert policy["policy_id"] == "P4.3-DEFENSIVE-MONOTONE-MULTIPLIER-V1"
    assert policy["allowed_inputs"] == ["frozen_defensive_scale", "candidate_research_cap"]
    assert policy["formula"] == (
        "leverage_multiplier = 1 + (candidate_research_cap - 1) * frozen_defensive_scale"
    )


def test_cap_one_is_identity_for_every_defensive_state():
    for defensive in (0.0, 1e-9, 0.1, 0.5, 0.999999, 1.0):
        assert leverage_multiplier(
            frozen_defensive_scale=defensive,
            candidate_research_cap=1.0,
        ) == 1.0
        assert final_scale(
            frozen_defensive_scale=defensive,
            candidate_research_cap=1.0,
        ) == pytest.approx(defensive)


def test_extra_leverage_fades_monotonically_with_defensive_derisking():
    cap = 1.30
    defensive_states = [0.0, 0.1, 0.25, 0.5, 0.75, 1.0]
    multipliers = [
        leverage_multiplier(frozen_defensive_scale=d, candidate_research_cap=cap)
        for d in defensive_states
    ]
    final_scales = [
        final_scale(frozen_defensive_scale=d, candidate_research_cap=cap)
        for d in defensive_states
    ]
    assert multipliers == sorted(multipliers)
    assert final_scales == sorted(final_scales)
    assert multipliers[0] == 1.0
    assert final_scales[0] == 0.0
    assert multipliers[-1] == pytest.approx(cap)
    assert final_scales[-1] == pytest.approx(cap)


def test_formula_has_no_threshold_and_matches_frozen_closed_form():
    for cap in ALLOWED_CAPS:
        for defensive in (0.03, 0.2, 0.5, 0.9):
            expected_multiplier = 1.0 + (cap - 1.0) * defensive
            expected_final = defensive + (cap - 1.0) * defensive**2
            assert leverage_multiplier(
                frozen_defensive_scale=defensive,
                candidate_research_cap=cap,
            ) == pytest.approx(expected_multiplier)
            assert final_scale(
                frozen_defensive_scale=defensive,
                candidate_research_cap=cap,
            ) == pytest.approx(expected_final)


def test_rejects_non_preregistered_cap_or_invalid_defensive_scale():
    with pytest.raises(MultiplierPolicyError, match="one of"):
        leverage_multiplier(frozen_defensive_scale=0.5, candidate_research_cap=1.15)
    with pytest.raises(MultiplierPolicyError, match=r"\[0,1\]"):
        leverage_multiplier(frozen_defensive_scale=1.01, candidate_research_cap=1.20)
    with pytest.raises(MultiplierPolicyError, match=r"\[0,1\]"):
        leverage_multiplier(frozen_defensive_scale=-0.01, candidate_research_cap=1.20)


def test_addendum_forbids_post_result_policy_rescue_and_new_signal_inputs():
    data = json.loads(ADDENDUM.read_text(encoding="utf-8"))
    policy = data["multiplier_policy"]
    forbidden = "\n".join(policy["forbidden_inputs"])
    assert "future returns" in forbidden
    assert "funding" in forbidden
    assert "HMM" in forbidden
    assert "P5" in forbidden
    assert "EXPOSURE-SMOOTH-0038" in forbidden
    assert "historically selected threshold" in forbidden
    assert "new experiment ID" in data["post_result_rule"]
