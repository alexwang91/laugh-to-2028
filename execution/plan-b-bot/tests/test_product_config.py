import json

import pytest

from beta_bot.config import Settings
from beta_bot.product_config import DEFAULT_PRODUCT_CONFIG_PATH, load_product_config


def test_canonical_product_config_contract():
    product = load_product_config()

    assert product.long_universe == ("BTC", "ETH", "SOL", "BNB")
    assert product.primary_venue == "hyperliquid"
    assert product.canonical_timezone == "UTC"
    assert product.daily_boundary_utc == "00:00"
    assert product.initial_live_capital_usd == 2000.0
    assert product.weekly_manual_contribution_usd == 100.0
    assert product.catastrophic_drawdown_limit == 0.70
    assert product.operating_risk_budget is None
    assert product.leverage_policy == "MODEL_DETERMINED"
    assert product.intraday_policy == "RISK_REDUCTION_ONLY"
    assert product.default_production_state == "MONITOR_ONLY"


def test_product_config_round_trip_is_json_serializable():
    product = load_product_config()
    serialized = json.dumps(product.to_dict(), sort_keys=True)
    assert '"product_id": "brkk-laugh-to-2028"' in serialized


def test_execution_settings_default_coin_comes_from_canonical_product(monkeypatch):
    monkeypatch.delenv("COIN", raising=False)
    settings = Settings.from_env()
    assert settings.coin == load_product_config().long_universe[0] == "BTC"


def test_execution_rejects_coin_outside_canonical_universe(monkeypatch):
    monkeypatch.setenv("COIN", "DOGE")
    with pytest.raises(ValueError, match="outside the canonical BRRK long universe"):
        Settings.from_env()


def test_execution_capability_is_distinct_from_product_universe(monkeypatch):
    monkeypatch.setenv("COIN", "ETH")
    with pytest.raises(ValueError, match="current execution implementation is BTC-only"):
        Settings.from_env()


def test_trade_mode_requires_explicit_durable_ledger(monkeypatch, tmp_path):
    monkeypatch.setenv("TRADING_MODE", "trade")
    monkeypatch.setenv("HL_MASTER_ADDRESS", "0x0000000000000000000000000000000000000001")
    monkeypatch.setenv("HL_API_PRIVATE_KEY", "test-only-not-a-real-key")
    monkeypatch.delenv("ORDER_LEDGER_PATH", raising=False)
    monkeypatch.delenv("ORDER_LEDGER_DURABLE_STORAGE", raising=False)
    with pytest.raises(ValueError, match="ORDER_LEDGER_PATH"):
        Settings.from_env()

    monkeypatch.setenv("ORDER_LEDGER_PATH", str(tmp_path / "orders.sqlite3"))
    with pytest.raises(ValueError, match="ORDER_LEDGER_DURABLE_STORAGE"):
        Settings.from_env()

    monkeypatch.setenv("ORDER_LEDGER_DURABLE_STORAGE", "true")
    settings = Settings.from_env()
    assert settings.can_trade
    assert settings.order_ledger_durable_storage is True


def test_vercel_trade_mode_fails_closed_for_local_sqlite(monkeypatch, tmp_path):
    monkeypatch.setenv("TRADING_MODE", "trade")
    monkeypatch.setenv("HL_MASTER_ADDRESS", "0x0000000000000000000000000000000000000001")
    monkeypatch.setenv("HL_API_PRIVATE_KEY", "test-only-not-a-real-key")
    monkeypatch.setenv("ORDER_LEDGER_PATH", str(tmp_path / "orders.sqlite3"))
    monkeypatch.setenv("ORDER_LEDGER_DURABLE_STORAGE", "true")
    monkeypatch.setenv("VERCEL", "1")
    with pytest.raises(ValueError, match="disabled on Vercel"):
        Settings.from_env()


def test_default_product_config_file_exists():
    assert DEFAULT_PRODUCT_CONFIG_PATH.is_file()
