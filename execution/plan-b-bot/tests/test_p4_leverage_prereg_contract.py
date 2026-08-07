from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASELINE_PATH = ROOT / "research" / "leverage_0039" / "P4_1_BASELINE_FREEZE.json"
PREREG_PATH = ROOT / "research" / "leverage_0039" / "LEVERAGE-0039.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_p4_1_freezes_corrected_brrk0011_zero_to_one_baseline():
    baseline = _load(BASELINE_PATH)
    assert baseline["freeze_id"] == "P4.1-BRRK0011-CORRECTED-0-1-V1"
    assert baseline["status"] == "FROZEN_BASELINE_NO_LEVERAGE_PROMOTION"
    assert baseline["source_main_sha"] == "fee2ebd34e71f62fb8aaa9e11787aa7413f122cd"
    assert baseline["frozen_risk_layer"]["scale_domain"] == [0.0, 1.0]
    assert baseline["frozen_risk_layer"]["scenario_cvar_cdar_budget"] == 0.20
    assert baseline["frozen_risk_layer"]["production_gross_cap"] == 1.0
    assert baseline["frozen_risk_layer"]["operating_risk_budget"] is None
    assert baseline["frozen_risk_layer"]["catastrophic_drawdown_limit"] == 0.70
    assert baseline["corrected_brrk0011_result"]["max_drawdown"] == -0.33715
    assert baseline["corrected_brrk0011_result"]["average_gross_exposure"] == 0.75430
    assert baseline["historical_research_cap_hint"]["value"] == 1.30
    assert baseline["historical_research_cap_hint"]["status"] == (
        "RESEARCH_ONLY_NOT_PROMOTED_NOT_PRODUCTION_AUTHORIZED"
    )
    assert baseline["production_authorized"] is False


def test_p4_1_authority_pins_exact_frozen_base_blobs():
    baseline = _load(BASELINE_PATH)
    authority = baseline["authority"]
    assert authority["research_corrected_risk"] == {
        "path": "research/risk_metric_fix/corrected_risk.py",
        "blob_sha": "bdf7cd6cb32961765716e4cb07288739e869703e",
        "role": "F13-corrected CVaR/CDaR path-tail risk and 0-1 scale selection",
    }
    assert authority["product_target_math"]["path"] == (
        "execution/plan-b-bot/beta_bot/target_math.py"
    )
    assert authority["product_target_math"]["blob_sha"] == (
        "4a0b26943438045f2baacbe06d92650a486a8967"
    )
    assert authority["regime_config"]["path"] == "research/regime_kelly/config.py"
    assert authority["regime_config"]["blob_sha"] == (
        "eecd092ac45c5fa86992a8de2f31d470405e6b5a"
    )
    assert authority["correction_result"]["path"] == (
        "research/results/BRRK_0011_CDAR_CORRECTION_2026-08-04.md"
    )
    assert authority["correction_result"]["blob_sha"] == (
        "40cd0e90a357a2c2e5be0b9de69feaf0f1e75eaf"
    )
    assert authority["measurement_normalization"]["path"] == (
        "research/results/idle_cash_credit_0027r2.json"
    )
    assert authority["measurement_normalization"]["blob_sha"] == (
        "46b509bf1b59a9d87a9092f9708eb41e5f8e50af"
    )


def test_baseline_preserves_metric_provenance_instead_of_reconciling_cagr_labels():
    baseline = _load(BASELINE_PATH)
    correction = baseline["corrected_brrk0011_result"]
    f27 = baseline["separate_f27_measurement_anchor"]
    assert correction["metric_convention"] == "BRRK_0011_CDAR_CORRECTION_2026-08-04"
    assert correction["cagr"] == 0.65104
    assert f27["metric_convention"] == "IDLE-CASH-CREDIT-F27-R2-MEASUREMENT-FIX_RAW_CALENDAR_SPAN"
    assert f27["raw_cagr"] == 0.6516609785339962
    assert correction["cagr"] != f27["raw_cagr"]
    assert "Do not overwrite" in f27["rule"]


def test_leverage_0039_is_preregistered_before_any_search_result():
    prereg = _load(PREREG_PATH)
    assert prereg["experiment_id"] == "LEVERAGE-0039"
    assert prereg["status"] == "PREREGISTERED_BEFORE_FIRST_RUN"
    assert prereg["baseline_freeze_id"] == "P4.1-BRRK0011-CORRECTED-0-1-V1"
    assert "results" not in prereg
    assert "selected_candidate" not in prereg
    assert prereg["production_authorized"] is False


def test_leverage_0039_search_domain_cannot_silently_expand():
    prereg = _load(PREREG_PATH)
    structural = prereg["only_structural_change"]
    assert structural["baseline_upper_bound"] == 1.0
    assert structural["candidate_upper_bounds"] == [1.0, 1.10, 1.20, 1.30]
    assert max(structural["candidate_upper_bounds"]) == 1.30
    assert prereg["why_search_stops_at_1_30"]["value"] == 1.30
    assert prereg["fixed_model"]["scenario_cvar_cdar_budget"] == 0.20
    assert prereg["fixed_model"]["no_short_targets"] is True


def test_operating_and_catastrophic_risk_budgets_are_separate():
    prereg = _load(PREREG_PATH)
    budgets = prereg["operating_drawdown_candidate_budgets"]
    catastrophe = prereg["catastrophic_drawdown_limit"]
    assert budgets == [0.35, 0.40, 0.45, 0.50]
    assert min(budgets) > abs(prereg["baseline"]["historical_result_max_drawdown"])
    assert max(budgets) < catastrophe
    assert catastrophe == 0.70
    assert "never an operating candidate" in prereg["operating_budget_rule"]


def test_cost_funding_stress_and_liquidation_gates_are_frozen():
    prereg = _load(PREREG_PATH)
    assert prereg["transaction_cost_treatment"]["cost_bps_per_abs_weight_change_grid"] == [
        5.0,
        10.0,
        20.0,
        50.0,
    ]
    funding = prereg["funding_treatment"]
    assert funding["signal_use"] == "FORBIDDEN"
    assert funding["threshold_optimization"] == "FORBIDDEN"
    assert [panel["name"] for panel in funding["mandatory_panels"]] == [
        "HYPERLIQUID_NATIVE_ALL_PERP_COMMON_WINDOW",
        "BINANCE_FULL_HISTORY_PROXY",
    ]
    assert prereg["liquidation_distance"]["required"] is True
    assert prereg["liquidation_distance"]["missing_model_rule"] == "FAIL_CLOSED_NO_PROMOTION"
    assert prereg["synthetic_stress_suite"]["uniform_one_day_gap_returns"] == [
        -0.10,
        -0.20,
        -0.30,
        -0.40,
        -0.50,
    ]


def test_all_roadmap_stress_eras_are_explicitly_registered():
    prereg = _load(PREREG_PATH)
    names = [row["name"] for row in prereg["historical_stress_windows"]]
    assert names == [
        "2021_SPRING_CRASH",
        "2021_NOV_BEAR_TRANSITION",
        "2022_SEVERE_DRAWDOWN",
        "2024_APRIL_MASKING_EPISODE",
        "2025_MULTI_PEAK_DELEVERAGING",
        "RECENT_2026_TO_FROZEN_END",
    ]
    early = prereg["historical_stress_windows"][0]
    assert early["mode"] == "PRE_BRRK_CONSERVATIVE_PROXY"
    assert "do not label this full-BRRK OOS performance" in early["rule"]


def test_p4_prereg_forbids_scope_smuggling_and_production_authorization():
    prereg = _load(PREREG_PATH)
    forbidden = "\n".join(prereg["forbidden"])
    assert "F23" in forbidden
    assert "EXPOSURE-SMOOTH-0038" in forbidden
    assert "shorts" in forbidden
    assert "XRP" in forbidden
    assert "P5" in forbidden
    assert "production" in forbidden.lower()
    assert prereg["deployment_cap_rule"]["research_only"] is True
    assert "fresh evidence" in prereg["deployment_cap_rule"]["raising_rule"]
