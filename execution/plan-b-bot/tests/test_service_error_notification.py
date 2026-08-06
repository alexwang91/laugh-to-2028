from types import SimpleNamespace

import pytest

from beta_bot import service


def test_strategy_cycle_failure_is_notified_and_reraised(monkeypatch):
    sent = []
    settings = SimpleNamespace(network="testnet", trading_mode="shadow", coin="BTC")

    def fail_core(_settings):
        raise RuntimeError("second-leg-or-other-execution-failure")

    monkeypatch.setattr(service, "_run_strategy_core", fail_core)
    monkeypatch.setattr(service, "send_telegram", lambda _settings, payload: sent.append(payload))

    with pytest.raises(RuntimeError, match="second-leg-or-other-execution-failure"):
        service.run_strategy(settings)

    assert len(sent) == 1
    assert sent[0]["result"] == "strategy_cycle_failed"
    assert sent[0]["error"]["type"] == "RuntimeError"
    assert "second-leg-or-other-execution-failure" in sent[0]["error"]["message"]


def test_notification_failure_does_not_mask_original_execution_error(monkeypatch):
    settings = SimpleNamespace(network="testnet", trading_mode="shadow", coin="BTC")

    def fail_core(_settings):
        raise RuntimeError("authoritative-execution-error")

    def fail_notify(_settings, _payload):
        raise OSError("telegram-down")

    monkeypatch.setattr(service, "_run_strategy_core", fail_core)
    monkeypatch.setattr(service, "send_telegram", fail_notify)

    with pytest.raises(RuntimeError, match="authoritative-execution-error"):
        service.run_strategy(settings)
