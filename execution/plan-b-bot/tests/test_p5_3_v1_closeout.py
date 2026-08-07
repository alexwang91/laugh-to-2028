from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
RESULT = ROOT / "research" / "results" / "p5_3_state_paths"


def test_v1_immutable_digest_and_non_authorizing_boundary() -> None:
    digest = (RESULT / "summary.sha256").read_text().strip()
    assert digest == "a2e5be8d605af5a2c8206235402fe3a66b08fd994eaa8a71e84cfb1e3cbfed8f"
    summary = json.loads((RESULT / "summary.json").read_text())
    assert summary["status"] == "ONE_TIME_FROZEN_STATE_PATH_EVIDENCE_COMPLETE"
    assert summary["selection"] == {
        "profile_selected": False,
        "state_model_production_selected": False,
        "status": "STATE_PATH_EVIDENCE_ONLY",
    }
    assert summary["production_authorized"] is False


def test_all_profiles_hit_same_false_flat_and_are_not_promotable() -> None:
    profile = pd.read_csv(RESULT / "profile_summary.csv")
    assert set(profile["profile"]) == {"EARLY", "BALANCED", "CONSERVATIVE"}
    assert set(profile["initialization_date"].astype(str)) == {"2021-01-17"}
    assert set(profile["first_flat_date"].astype(str)) == {"2021-02-23"}
    assert set(profile["classified_days"].astype(int)) == {1869}
    assert set(profile["flat_days"].astype(int)) == {1832}
    assert (profile["flat_fraction"] > 0.97).all()
    assert profile["ever_flat"].astype(bool).all()
    assert set(profile["final_state"].astype(str)) == {"FLAT"}


def test_first_flat_occurs_inside_frozen_non_top_control_with_complete_inputs() -> None:
    paths = pd.read_csv(RESULT / "daily_state_paths.csv", parse_dates=["date"])
    day = paths.loc[paths["date"].eq(pd.Timestamp("2021-02-23"))]
    assert len(day) == 3
    assert set(day["profile"]) == {"EARLY", "BALANCED", "CONSERVATIVE"}
    assert day["ordinary_inputs_complete"].astype(bool).all()
    assert set(day["minimum_calibration_depth"].astype(int)) == {57}
    assert day["exhaustion"].astype(bool).all()
    assert day["strong_exhaustion"].astype(bool).all()
    assert day["damage"].astype(bool).all()
    assert day["strong_damage"].astype(bool).all()
    assert set(day["raw_candidate_state"].astype(str)) == {"FLAT"}
    assert set(day["state"].astype(str)) == {"FLAT"}

    occupancy = pd.read_csv(RESULT / "event_state_occupancy.csv")
    control = occupancy.loc[
        occupancy["event_id"].eq("P5C-2021-JAN-FEB-HIGH-VOL")
        & occupancy["bucket"].eq("near_event")
    ]
    assert len(control) == 3
    assert set(control["event_class"].astype(str)) == {"HIGH_VOLATILITY_NON_TOP_CONTROL"}
    assert set(control["classified_rows"].astype(int)) == {7}
    assert set(control["flat_count"].astype(int)) == {6}
    assert (control["flat_fraction"].sub(6.0 / 7.0).abs() < 1e-12).all()


def test_raw_market_candidate_recovers_while_v1_final_state_remains_absorbing_flat() -> None:
    paths = pd.read_csv(RESULT / "daily_state_paths.csv", parse_dates=["date"])
    expected = {
        "2021-02-27": "DE_RISK_2",
        "2021-02-28": "NORMAL_BULL",
        "2021-03-01": "NORMAL_BULL",
        "2021-03-09": "BTC_LEADERSHIP_MATURING",
    }
    for day, raw_state in expected.items():
        rows = paths.loc[paths["date"].eq(pd.Timestamp(day))]
        assert len(rows) == 3
        assert set(rows["raw_candidate_state"].astype(str)) == {raw_state}
        assert set(rows["state"].astype(str)) == {"FLAT"}
