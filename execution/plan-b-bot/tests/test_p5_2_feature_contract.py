from __future__ import annotations

import json
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
P5 = ROOT / "research" / "cycle_exit"
if str(P5) not in sys.path:
    sys.path.insert(0, str(P5))

import p5_2_features as features
import run_p5_2_feature_evidence as runner


CONTRACT_PATH = P5 / "p5_2_feature_contract.json"


def _contract() -> dict:
    return json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))


def _synthetic_daily() -> pd.DataFrame:
    idx = pd.date_range("2020-10-01", "2021-04-30", freq="D")
    x = np.arange(len(idx), dtype=float)
    return pd.DataFrame(
        {
            "BTC": 100.0 * np.exp(0.002 * x + 0.02 * np.sin(x / 8)),
            "ETH": 10.0 * np.exp(0.0023 * x + 0.03 * np.sin(x / 9)),
            "SOL": 2.0 * np.exp(0.0028 * x + 0.04 * np.sin(x / 7)),
            "BNB": 5.0 * np.exp(0.0021 * x + 0.02 * np.sin(x / 11)),
            "XRP": 1.0 * np.exp(0.0018 * x + 0.05 * np.sin(x / 6)),
        },
        index=idx,
    )


def _synthetic_4h() -> pd.Series:
    idx = pd.date_range("2020-10-01 04:00:00", "2021-04-30 00:00:00", freq="4h")
    x = np.arange(len(idx), dtype=float)
    return pd.Series(100.0 * np.exp(0.0003 * x + 0.01 * np.sin(x / 5)), index=idx)


def test_contract_is_frozen_and_non_production():
    contract = runner._load_contract()
    assert contract["contract_id"] == "P5.2-FEATURE-FAMILIES-V1"
    assert contract["status"] == "FROZEN_BEFORE_FIRST_FEATURE_EVIDENCE_RUN"
    assert contract["base_main"] == "86497cdd663a89ca4d54c898b7acbac1cc07d836"
    assert contract["taxonomy_contract"] == "P5.1-EVENT-TAXONOMY-V1"
    assert contract["research_integrity"]["production_authorization"] == "NONE"
    assert contract["run_once"]["authorized_under_standing_research_authorization"] is True


def test_available_feature_ids_match_implementation_exactly():
    contract = _contract()
    declared = features.family_map(contract)
    assert set(declared) == set(features.AVAILABLE_FEATURES)
    assert len(declared) == len(features.AVAILABLE_FEATURES)


def test_pending_features_remain_explicit_data_source_gaps():
    contract = _contract()
    pending = {
        item["id"]
        for family in contract["feature_families"].values()
        for item in family.get("pending", [])
    }
    assert "btc_dominance" in pending
    assert "broad_market_breadth" in pending
    assert "historical_open_interest" in pending
    assert "liquidation_proxy" in pending
    assert all(
        item["status"] == "DATA_SOURCE_PENDING"
        for family in contract["feature_families"].values()
        for item in family.get("pending", [])
    )


def test_feature_panel_is_causal_and_complete_after_warmup():
    daily = _synthetic_daily()
    btc4h = _synthetic_4h()
    panel = features.build_feature_panel(daily, btc4h)
    assert tuple(panel.columns) == features.AVAILABLE_FEATURES
    mature = panel.loc["2021-02-01":]
    assert mature.notna().mean().min() > 0.95
    assert panel["canonical5_outperformance_breadth_20d"].dropna().between(0, 1).all()
    assert panel["alt_outperformance_breadth_20d"].dropna().between(0, 1).all()
    assert panel["high_beta_participation_20d"].dropna().between(0, 1).all()


def test_daily_boundary_uses_completed_4h_bar_only():
    daily_idx = pd.date_range("2021-01-01", periods=60, freq="D")
    four_h_idx = pd.date_range("2020-12-20 04:00:00", "2021-03-01 00:00:00", freq="4h")
    s = pd.Series(np.linspace(100.0, 200.0, len(four_h_idx)), index=four_h_idx)
    aligned = features._aligned_4h_rsi(s, daily_idx, 14)
    raw_rsi = features.wilder_rsi(s, 14)
    for day in daily_idx:
        assert aligned.loc[day] == raw_rsi.reindex([day]).iloc[0]


def test_price_rsi_divergence_is_bounded():
    daily = _synthetic_daily()
    panel = features.build_feature_panel(daily, _synthetic_4h())
    divergence = panel["btc_price_rsi_rank_divergence_20d"].dropna()
    assert divergence.between(-1.0, 1.0).all()


def test_feature_builder_rejects_missing_daily_data():
    daily = _synthetic_daily().drop(pd.Timestamp("2021-01-15"))
    try:
        features.build_feature_panel(daily, _synthetic_4h())
    except ValueError as exc:
        assert "contiguous" in str(exc)
    else:
        raise AssertionError("missing daily observation must fail closed")
