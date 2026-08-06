import json
from pathlib import Path

import pytest

from beta_bot.instrument_registry import CANONICAL_ASSETS, InstrumentRegistry, load_instrument_registry


def test_canonical_registry_loads_all_brrk_assets():
    registry = load_instrument_registry()
    assert tuple(registry.assets) == CANONICAL_ASSETS
    assert registry.venue == "hyperliquid"
    assert registry.quote_asset == "USDC"


def test_perp_precision_is_canonical_and_metadata_driven():
    registry = load_instrument_registry()
    expected = {
        "BTC": (5, 1),
        "ETH": (4, 2),
        "SOL": (2, 4),
        "BNB": (3, 3),
    }
    for asset, (sz_decimals, max_price_decimals) in expected.items():
        perp = registry.asset(asset)["perp"]
        assert perp["identity"] == asset
        assert perp["sz_decimals"] == sz_decimals
        assert perp["max_price_decimals"] == max_price_decimals
        assert perp["availability_state"] == "AVAILABLE"


def test_btc_imports_prior_spot_identity_without_reopening_research():
    registry = load_instrument_registry()
    spot = registry.asset("BTC")["spot"]
    assert spot["hypercore_token_candidate"] == "UBTC"
    assert spot["hypercore_pair_candidate"] == "UBTC/USDC"
    assert spot["identity_status"] == "VERIFIED_PRIOR_EVIDENCE"
    assert spot["evidence_decision_id"] == "ROUTER-DATA-0004"


def test_non_btc_spot_candidates_remain_non_routable_until_p2_2():
    registry = load_instrument_registry()
    for asset in ("ETH", "SOL", "BNB"):
        spot = registry.asset(asset)["spot"]
        assert spot["identity_status"] == "UNVERIFIED_PENDING_P2_2"
        assert spot["availability_state"] in {"CANDIDATE_NOT_ROUTABLE", "UNKNOWN_NOT_ROUTABLE"}


def test_registry_rejects_silent_p2_2_authorization(tmp_path: Path):
    source = Path(__file__).resolve().parents[3] / "config" / "instrument_registry.json"
    raw = json.loads(source.read_text(encoding="utf-8"))
    raw["assets"]["ETH"]["spot"]["identity_status"] = "VERIFIED"
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="ETH spot identity must remain pending P2.2"):
        load_instrument_registry(path)


def test_registry_rejects_missing_asset():
    raw = {
        "schema_version": 1,
        "registry_id": "x",
        "venue": "hyperliquid",
        "quote_asset": "USDC",
        "assets": {},
    }
    with pytest.raises(ValueError, match="BTC/ETH/SOL/BNB"):
        InstrumentRegistry.from_mapping(raw)
