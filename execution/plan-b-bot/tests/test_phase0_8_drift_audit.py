from __future__ import annotations

import json
from pathlib import Path

import pytest

from beta_bot.config import Settings
from beta_bot.production_authority import (
    LEGACY_NORMAL_SERVICE_NEW_RISK_AUTHORIZED,
    PRODUCTION_AUTHORIZED_COMPONENTS,
    PRODUCTION_GROSS_CAP,
)


REPO_ROOT = Path(__file__).resolve().parents[3]


def _json(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


def test_audit_contract_is_fail_closed_pending_final_head_ci():
    audit = _json("config/phase0_8_drift_audit.json")
    assert audit["id"] == "PHASE-0-8-DRIFT-AUDIT-V1"
    assert audit["drift_level"] == "DRIFT_2"
    assert audit["scope"]["economic_retuning_allowed"] is False
    assert audit["scope"]["immutable_result_changes_allowed"] is False
    assert audit["scope"]["production_authorization_allowed"] is False
    assert audit["canonical_production_policy"]["gross_cap"] == 1.0
    assert audit["canonical_production_policy"]["production_authorized_components"] == []
    assert audit["canonical_production_policy"]["legacy_normal_service_new_risk_authorized"] is False


def test_legacy_execution_cannot_infer_new_risk_authority_from_trade_mode():
    assert LEGACY_NORMAL_SERVICE_NEW_RISK_AUTHORIZED is False
    assert PRODUCTION_GROSS_CAP == 1.0
    assert PRODUCTION_AUTHORIZED_COMPONENTS == ()


def test_legacy_normal_beta_cap_cannot_exceed_one():
    settings = Settings(
        network="testnet",
        trading_mode="shadow",
        coin="BTC",
        master_address=None,
        vault_address=None,
        api_private_key=None,
        external_spot_btc_qty=0.0,
        external_cash_usd=0.0,
        rebalance_band=0.05,
        min_trade_usd=100.0,
        normal_beta_cap=1.01,
        max_platform_leverage=2,
        max_slippage_bps=15.0,
        request_timeout_seconds=15.0,
        candle_lookback_days=450,
        cron_secret=None,
        live_trading_confirmation=None,
        telegram_bot_token=None,
        telegram_chat_id=None,
    )
    with pytest.raises(ValueError, match="production leverage above 1.0 is not authorized"):
        settings.validate()


def test_decision_registry_has_no_production_authorized_component():
    registry = _json("config/decision_registry.json")
    assert registry["production_authorized_components"] == []
    leverage = next(d for d in registry["decisions"] if d["id"] == "PRODUCT-LEVERAGE-2026-08-05")
    assert "Current production gross cap remains 1.0" in leverage["decision"]
    assert "NO_PROMOTION" in leverage["decision"]


def test_leverage_0040_immutable_digest_is_unchanged():
    digest = (REPO_ROOT / "research/results/leverage_0040/summary.sha256").read_text(encoding="utf-8").strip()
    assert digest == "3bb4dc46c61a5e9c7e049862575a89b2771830410ce4bc2bb25c83e469f52fc0"


def test_phase6_remains_zero_authority_and_time_evidence_is_not_backfilled():
    phase6 = _json("config/phase6_shadow_contract.json")
    assert phase6["status"] == "PASS_SHADOW_ONLY_IMPLEMENTATION_REPLAY"
    assert phase6["production_gross_cap"] == 1.0
    assert phase6["production_authorized"] is False
    assert phase6["signature_authorized"] is False
    assert phase6["order_submission_authorized"] is False
    live = phase6["acceptance"]["live_shadow_observation"]
    assert live["status"] == "MEASUREMENT_INCONCLUSIVE_TIME_DEPENDENT"
    assert live["minimum_elapsed_calendar_days"] == 14
    assert live["minimum_scheduled_decisions"] == 10


def test_phase7_remains_monitor_only_and_human_gated():
    phase7 = _json("config/phase7_launch_readiness.json")
    assert phase7["status"] == "IMPLEMENTATION_READINESS_ONLY_LAUNCH_BLOCKED"
    assert phase7["production_gross_cap"] == 1.0
    assert phase7["current_program_state"] == "MONITOR_ONLY"
    assert phase7["production_authorized"] is False
    assert "PHASE6_LIVE_ELAPSED_EVIDENCE_NOT_PASSED" in phase7["launch_blockers"]
    assert "EXPLICIT_OWNER_APPROVAL_NOT_PRESENT" in phase7["launch_blockers"]
    for boundary in (
        "MONITOR_ONLY_TO_ACTIVE",
        "FLAT_TO_LONG",
        "FLAT_TO_SHORT",
        "FIRST_SHORT_EXPOSURE_OF_NEW_BEAR_PHASE",
    ):
        assert boundary in phase7["human_approval_boundaries"]


def test_phase8_remains_trigger_absent_not_run_and_not_short_ready():
    phase8 = _json("research/bear_short_0001/BEAR-SHORT-0001.json")
    assert phase8["status"] == "PREREGISTERED_TRIGGER_ABSENT_NOT_RUN"
    assert phase8["required_trigger"] == "CONFIRMED_BEAR_TRANSITION_ARTIFACT"
    assert phase8["trigger_present"] is False
    assert phase8["selection_status"] == "NONE_TRIGGER_ABSENT"
    assert phase8["short_ready"] is False
    assert phase8["production_authorized"] is False
    assert phase8["first_real_short_authorized"] is False


def test_authoritative_handoff_docs_do_not_reopen_completed_phase_work():
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    current = (REPO_ROOT / "docs/CURRENT_STATE.md").read_text(encoding="utf-8")
    next_steps = (REPO_ROOT / "docs/NEXT_STEPS.md").read_text(encoding="utf-8")

    for text in (readme, current, next_steps):
        assert "production_authorized_components = []" in text
        assert "1.0" in text

    stale_markers = (
        "P5.4 behavior mapping | **NEXT",
        "Phase 6 integrated shadow | **NOT STARTED",
        "Phase 7 limited-capital live long | **NOT STARTED",
        "Phase 8 bear-short research | **NOT STARTED",
        "Phase 6 integrated shadow              NEXT / BASELINE ONLY",
        "Phase 7 limited-live readiness         NOT STARTED",
        "Phase 8 bear-short research            NOT STARTED",
        "MERGE P7 READINESS GATE AFTER FINAL-HEAD GREEN",
    )
    combined = "\n".join((readme, current, next_steps))
    for marker in stale_markers:
        assert marker not in combined
