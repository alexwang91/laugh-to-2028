import importlib.util
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("engine0060", HERE / "engine.py")
E = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(E)


def frame(n=900, seed=7):
    rng = np.random.default_rng(seed)
    r = 0.0004 + 0.012 * rng.normal(size=n)
    p = 100.0 * np.exp(np.cumsum(r))
    return pd.DataFrame({"close": p}, index=pd.date_range("2020-01-01", periods=n, freq="D"))


def test_payload_identity_guard():
    with pytest.raises(ValueError):
        E.validate_payload_identity("bad")
    E.validate_payload_identity(E.EXPECTED_PAYLOAD_SHA256)


def test_frame_contract_rejects_tzaware_and_nonpositive():
    f = frame(20)
    g = f.copy(); g.index = g.index.tz_localize("UTC")
    with pytest.raises(ValueError): E.validate_price_frame(g, False)
    h = f.copy(); h.iloc[3, 0] = 0
    with pytest.raises(ValueError): E.validate_price_frame(h, False)


def test_trend_component_constant_is_nan_after_validity():
    p = pd.Series(np.ones(300), index=pd.date_range("2020-01-01", periods=300))
    x = E._trend_component(p, 20)
    assert x.dropna().empty


def test_persistence_resets_on_false_and_invalid():
    idx = pd.date_range("2020-01-01", periods=6)
    fast = pd.Series([0, 0, 2, np.nan, 0, 0], index=idx, dtype=float)
    slow = pd.Series([1, 1, 1, 1, 1, 1], index=idx, dtype=float)
    got = E._disagreement_persistence(fast, slow)
    assert got.iloc[:3].tolist() == [1.0, 2.0, 0.0]
    assert np.isnan(got.iloc[3]) and got.iloc[4] == 1.0 and got.iloc[5] == 2.0


def test_recent_high_age_uses_most_recent_tie():
    x = np.arange(60, dtype=float)
    x[50] = 100; x[55] = 100
    assert E._recent_high_age(x) == 4.0


def test_semivol_requires_both_signs():
    assert np.isnan(E._semivol_log_ratio(np.ones(20)))
    x = np.array([-2.0] * 10 + [1.0] * 10)
    assert E._semivol_log_ratio(x) == pytest.approx(np.log(2.0))


def test_causal_z_no_future_leakage():
    s = pd.Series(np.arange(400, dtype=float))
    z1 = E.causal_z(s)
    s2 = s.copy(); s2.iloc[350:] += 10000
    z2 = E.causal_z(s2)
    pd.testing.assert_series_equal(z1.iloc[:350], z2.iloc[:350])


def test_state_panel_strict_required_coordinates():
    f = frame(900)
    s = E.build_state_panel(f, False)
    assert {"A1", "A2", "A3", "S"}.issubset(s.columns)
    assert s["S"].notna().sum() > 100
    valid = s["S"].notna()
    required = ["A1a_z","A1b_z","A2a_z","A2b_z","A2c_z","A3a_z","A3b_z","A3c_z"]
    assert s.loc[valid, required].notna().all().all()


def test_terminal_loss_and_adverse_excursion_exact():
    idx = pd.date_range("2020-01-01", periods=260)
    p = np.full(260, 100.0)
    p[1:21] = np.linspace(99, 80, 20)
    f = pd.DataFrame({"close":p}, index=idx)
    t = E.build_target_panel(f, False)
    assert t.loc[idx[0], "terminal_loss_20"] == pytest.approx(-np.log(0.8))
    assert t.loc[idx[0], "adverse_excursion_20"] == pytest.approx(-np.log(0.8))


def test_adverse_excursion_detects_intrahorizon_loss_when_terminal_recovers():
    idx = pd.date_range("2020-01-01", periods=260)
    p = np.full(260, 100.0); p[10] = 70.0; p[20] = 105.0
    f = pd.DataFrame({"close":p}, index=idx)
    t = E.build_target_panel(f, False)
    assert t.loc[idx[0], "terminal_loss_20"] == 0.0
    assert t.loc[idx[0], "adverse_excursion_20"] == pytest.approx(-np.log(0.7))


def test_assign_blocks_equal_as_possible():
    ids = E._assign_blocks(10)
    assert [(ids == b).sum() for b in range(1,5)] == [3,3,2,2]


def test_spearman_average_ties_and_constant_nan():
    assert E.spearman(np.array([1,1,2,3]), np.array([1,2,3,4])) > 0
    assert np.isnan(E.spearman(np.ones(4), np.arange(4)))


def test_mbb_is_deterministic_and_length_preserving():
    a = E._mbb_indices(100, 20, np.random.default_rng(5))
    b = E._mbb_indices(100, 20, np.random.default_rng(5))
    assert len(a) == 100 and np.array_equal(a,b)


def test_classification_precedence():
    pos = {k:0.1 for k in E.TARGET_KEYS}
    neg = pos.copy(); neg[E.TARGET_KEYS[0]] = -0.01
    assert E.classify(100, pos, 4, pos)[0] == E.CLASS_SUPPORT
    assert E.classify(1500, neg, 4, pos)[0] == E.CLASS_INFO
    assert E.classify(1500, pos, 2, pos)[0] == E.CLASS_TEMPORAL
    l = pos.copy(); l[E.TARGET_KEYS[0]] = -0.01
    assert E.classify(1500, pos, 4, l)[0] == E.CLASS_DEP
    assert E.classify(1500, pos, 4, pos)[0] == E.CLASS_PASS


def test_small_synthetic_end_to_end_without_real_calendar():
    f = frame(900, seed=19)
    out = E.evaluate(f, E.EXPECTED_PAYLOAD_SHA256, require_frozen_calendar=False, bootstrap_reps=8)
    assert out["research_id"] == E.RESEARCH_ID
    assert out["actual_variants_evaluated"] == 1
    assert len(out["full_sample_rho_by_target"]) == 8
    assert len(out["origin_panel"]) == out["shared_origin_count"]
    assert out["production_authorized"] is False


def test_engine_has_no_real_loader_or_network_import():
    text = (HERE / "engine.py").read_text()
    forbidden = ["frames_from_market_evidence", "requests.get", "MARKET_EVIDENCE.json", "urllib", "http://", "https://"]
    assert not any(x in text for x in forbidden)
