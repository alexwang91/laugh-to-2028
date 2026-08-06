from types import SimpleNamespace

import beta_bot.service as service
from beta_bot.account_reconciliation import AccountReconciliationReport
from beta_bot.order_ledger import LedgerUncertainState
from beta_bot.restart_recovery import RestartRecoveryReport


class DummySettings:
    api_url = "https://example.invalid"
    coin = "BTC"
    candle_lookback_days = 450
    request_timeout_seconds = 1.0
    normal_beta_cap = 1.0
    network = "testnet"
    trading_mode = "trade"
    account_address = "0x0000000000000000000000000000000000000001"
    order_ledger_path = "/tmp/test-orders.sqlite3"
    external_spot_btc_qty = 0.0
    external_cash_usd = 0.0
    rebalance_band = 0.05
    min_trade_usd = 100.0
    max_platform_leverage = 2
    can_trade = True


def _report(*, actual_qty, target_qty, clean=False):
    reasons = () if clean else ("PERSISTENT_ORDER_RECONCILIATION_UNRESOLVED",)
    return AccountReconciliationReport(
        coin="BTC",
        actual_position_qty=actual_qty,
        target_position_qty=target_qty,
        target_gap_qty=target_qty - actual_qty,
        account_equity_usd=2000.0,
        total_margin_used_usd=100.0,
        exchange_open_order_cloids=(),
        local_active_order_cloids=(),
        recent_fill_count=0,
        blocking_reasons=reasons,
        risk_increase_allowed=clean,
    )


def _restart_report(actual_qty, *, clean=True):
    reasons = () if clean else ("RESTART_RECONCILIATION_UNCERTAIN",)
    persistent = {"blocking_unresolved_after": 0}
    if not clean:
        persistent = {
            "blocking_unresolved_after": 1,
            "reconciliation_uncertain": True,
            "error": "unknown submit result",
        }
    return RestartRecoveryReport(
        coin="BTC",
        actual_position_qty=actual_qty,
        local_position_expectation_qty=actual_qty,
        position_truth_source="fresh_clearinghouse_state",
        recovery_cases=(),
        blocking_reasons=reasons,
        blocking_unresolved_after=0 if clean else 1,
        persistent_reconciliation=persistent,
        risk_increase_allowed=clean,
    )


def _install_common(monkeypatch, *, current_qty, target_qty):
    snapshot = SimpleNamespace(
        closes=[100.0] * 300,
        mark_price=100.0,
        current_hourly_funding=0.0,
        funding_apr_24h=0.0,
        last_candle_start_ms=1_785_888_000_000,
    )
    signal = SimpleNamespace(target_beta=0.5, to_dict=lambda: {"target_beta": 0.5})
    product = SimpleNamespace(
        strategy_release_id="candidate-p1-8",
        model_version="m1",
        data_version="d1",
    )
    plan = SimpleNamespace(
        target_perp_qty=target_qty,
        should_rebalance=True,
        rebalance_reason="rebalance_required",
        target_clamped_by_leverage=False,
        requested_target_perp_notional_usd=target_qty * snapshot.mark_price,
        target_perp_notional_usd=target_qty * snapshot.mark_price,
        to_dict=lambda: {
            "target_perp_qty": target_qty,
            "should_rebalance": True,
            "target_clamped_by_leverage": False,
        },
    )
    state = {
        "marginSummary": {"accountValue": "2000", "totalMarginUsed": "100"},
        "assetPositions": [{"position": {"coin": "BTC", "szi": str(current_qty)}}],
    }

    monkeypatch.setattr(service, "load_product_config", lambda: product)
    monkeypatch.setattr(service, "fetch_market_snapshot", lambda **_kwargs: snapshot)
    monkeypatch.setattr(service, "build_signal", lambda *_args, **_kwargs: signal)
    monkeypatch.setattr(service, "fetch_user_state", lambda *_args, **_kwargs: state)
    monkeypatch.setattr(service, "build_portfolio_plan", lambda **_kwargs: plan)
    monkeypatch.setattr(service, "send_telegram", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(service, "normal_new_risk_disabled", lambda _settings: False)
    monkeypatch.setattr(
        service,
        "_restart_recovery",
        lambda *_args, **_kwargs: _restart_report(current_qty),
    )


def test_unexplained_reconciliation_blocks_risk_increase(monkeypatch):
    _install_common(monkeypatch, current_qty=0.25, target_qty=0.4)
    monkeypatch.setattr(
        service,
        "_restart_recovery",
        lambda *_args, **_kwargs: _restart_report(0.25, clean=False),
    )
    monkeypatch.setattr(
        service,
        "_account_reconciliation",
        lambda *_args, **_kwargs: _report(actual_qty=0.25, target_qty=0.4),
    )
    submitted = []
    monkeypatch.setattr(service, "execute_target_position", lambda *_args, **_kwargs: submitted.append(True))

    payload = service.run_strategy(DummySettings())

    assert submitted == []
    assert payload["result"] == "trade_blocked_account_reconciliation"
    assert payload["risk_increase_blocked"] is True


def test_same_direction_reduce_remains_available_during_reconciliation_uncertainty(monkeypatch):
    _install_common(monkeypatch, current_qty=0.5, target_qty=0.2)
    monkeypatch.setattr(service, "_restart_recovery", lambda *_args, **_kwargs: _restart_report(0.5, clean=False))
    monkeypatch.setattr(service, "reconcile_persistent_orders", lambda _settings: (_ for _ in ()).throw(LedgerUncertainState("unknown submit result")))
    monkeypatch.setattr(service, "_account_reconciliation", lambda *_args, **_kwargs: _report(actual_qty=0.5, target_qty=0.2))
    submitted = []
    monkeypatch.setattr(service, "execute_target_position", lambda *_args, **_kwargs: submitted.append(True) or [{"action": "reduce", "status": "filled"}])

    payload = service.run_strategy(DummySettings())

    assert submitted == [True]
    assert payload["risk_increase_blocked"] is False
    assert payload["reconciliation_override"] == "REDUCE_RISK_ACTION_ALLOWED"


def test_new_risk_kill_switch_blocks_clean_risk_increase(monkeypatch):
    _install_common(monkeypatch, current_qty=0.25, target_qty=0.4)
    monkeypatch.setattr(service, "normal_new_risk_disabled", lambda _settings: True)
    monkeypatch.setattr(service, "_account_reconciliation", lambda *_args, **_kwargs: _report(actual_qty=0.25, target_qty=0.4, clean=True))
    submitted = []
    monkeypatch.setattr(service, "execute_target_position", lambda *_args, **_kwargs: submitted.append(True))

    payload = service.run_strategy(DummySettings())

    assert submitted == []
    assert payload["result"] == "trade_blocked_new_risk_kill_switch"
    assert payload["new_risk_kill_switch_active"] is True
    assert payload["risk_increase_blocked"] is True


def test_new_risk_kill_switch_preserves_same_direction_reduction(monkeypatch):
    _install_common(monkeypatch, current_qty=0.5, target_qty=0.2)
    monkeypatch.setattr(service, "normal_new_risk_disabled", lambda _settings: True)
    monkeypatch.setattr(service, "_account_reconciliation", lambda *_args, **_kwargs: _report(actual_qty=0.5, target_qty=0.2, clean=True))
    monkeypatch.setattr(service, "reconcile_persistent_orders", lambda _settings: {"blocking_unresolved_after": 0})
    submitted = []
    monkeypatch.setattr(service, "execute_target_position", lambda *_args, **_kwargs: submitted.append(True) or [{"action": "reduce", "status": "filled"}])

    payload = service.run_strategy(DummySettings())

    assert submitted == [True]
    assert payload["risk_increase_blocked"] is False
    assert payload["reconciliation_override"] == "REDUCE_RISK_ACTION_ALLOWED"
