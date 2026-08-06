import copy
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from beta_bot.data_contract import DataContractError, DataContractPolicy


def raw_contract():
    repo_root = Path(__file__).resolve().parents[3]
    return json.loads((repo_root / "config" / "data_contract.json").read_text(encoding="utf-8"))


def ms(value):
    return int(datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp() * 1000)


def test_versioned_symbol_mapping_switches_at_explicit_utc_boundary():
    raw = raw_contract()
    raw["strategy_daily_close"]["source_mappings"]["BTC"] = [
        {
            "source_symbol": "BTCUSDT_OLD",
            "valid_from_utc": None,
            "valid_to_utc": "2025-01-01T00:00:00Z",
        },
        {
            "source_symbol": "BTCUSDT_NEW",
            "valid_from_utc": "2025-01-01T00:00:00Z",
            "valid_to_utc": None,
        },
    ]
    policy = DataContractPolicy.from_mapping(raw)
    assert policy.source_symbol("BTC", ms("2024-12-31T00:00:00Z")) == "BTCUSDT_OLD"
    assert policy.source_symbol("BTC", ms("2025-01-01T00:00:00Z")) == "BTCUSDT_NEW"


def test_mapping_gap_fails_when_a_consumed_session_is_uncovered():
    raw = raw_contract()
    raw["strategy_daily_close"]["source_mappings"]["BTC"] = [
        {
            "source_symbol": "BTCUSDT_OLD",
            "valid_from_utc": None,
            "valid_to_utc": "2025-01-01T00:00:00Z",
        },
        {
            "source_symbol": "BTCUSDT_NEW",
            "valid_from_utc": "2025-01-02T00:00:00Z",
            "valid_to_utc": None,
        },
    ]
    policy = DataContractPolicy.from_mapping(raw)
    with pytest.raises(DataContractError, match="resolve exactly once"):
        policy.source_symbol("BTC", ms("2025-01-01T00:00:00Z"))


def test_overlapping_mapping_periods_are_rejected_at_contract_load():
    raw = raw_contract()
    raw["strategy_daily_close"]["source_mappings"]["BTC"] = [
        {
            "source_symbol": "BTCUSDT_OLD",
            "valid_from_utc": None,
            "valid_to_utc": "2025-01-02T00:00:00Z",
        },
        {
            "source_symbol": "BTCUSDT_NEW",
            "valid_from_utc": "2025-01-01T00:00:00Z",
            "valid_to_utc": None,
        },
    ]
    with pytest.raises(DataContractError, match="Overlapping source mappings"):
        DataContractPolicy.from_mapping(raw)
