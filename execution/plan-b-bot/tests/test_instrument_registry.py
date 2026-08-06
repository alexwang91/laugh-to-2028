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
    expected = {"BTC": (5, 1), "ETH": (4, 2), "SOL": (2, 4), "BNB": (3, 3)}
    for asset, (sz_decimals, max_price_decimals) in expected.items():
        perp = registry.asset(asset)["perp"]
        assert perp["identity"] == asset
        assert perp["sz_decimals"] == sz_decimals
        assert perp["max_price_decimals"] == max_price_decimals
        assert perp["availability_state"] == "AVAILABLE"


def test_btc_imports_prior_spot_identity_without_reopening_research():
    row = load_instrument_registry().asset("BTC")
    spot = row["spot"]
    assert row["route_policy"] == "SPOT_CANDIDATE_WITH_PERP_FALLBACK"
    assert spot["hypercore_token_candidate"] == "UBTC"
    assert spot["hypercore_pair_candidate"] == "UBTC/USDC"
    assert spot["identity_status"] == "VERIFIED_PRIOR_EVIDENCE"
    assert spot["evidence_decision_id"] == "ROUTER-DATA-0004"


def test_eth_and_sol_are_verified_unit_native_assets_but_not_routing_authorized():
    registry = load_instrument_registry()
    expected = {"ETH": ("UETH", "UETH/USDC", "Ethereum"), "SOL": ("USOL", "USOL/USDC", "Solana")}
    for asset, (token, pair, chain) in expected.items():
        row = registry.asset(asset)
        spot = row["spot"]
        assert row["route_policy"] == "SPOT_CANDIDATE_WITH_PERP_FALLBACK"
        assert spot["identity_status"] == "VERIFIED_UNIT_NATIVE_ASSET"
        assert spot["hypercore_token_candidate"] == token
        assert spot["hypercore_pair_candidate"] == pair
        assert spot["native_chain"] == chain
        assert spot["availability_state"] == "IDENTITY_VERIFIED_ROUTING_NOT_AUTHORIZED"
        assert row["custody_redemption"]["status"] == "VERIFIED_UNIT_NATIVE_DEPOSIT_WITHDRAWAL"


def test_bnb_is_perp_only_under_current_verified_route_set():
    row = load_instrument_registry().asset("BNB")
    spot = row["spot"]
    assert row["route_policy"] == "PERP_ONLY_CURRENT_VERIFIED_DEFAULT"
    assert row["route_policy_source"] == "ROUTER-SPOT-IDENTITY-P2.2"
    assert spot["identity_status"] == "NO_VERIFIED_UNIT_NATIVE_ROUTE"
    assert spot["availability_state"] == "SPOT_UNAVAILABLE_PER_CURRENT_VERIFIED_ROUTE_SET"
    assert spot["hypercore_token_candidate"] is None
    assert spot["hypercore_pair_candidate"] is None
    assert row["custody_redemption"]["status"] == "NO_VERIFIED_UNIT_NATIVE_ROUTE"


def test_registry_rejects_silent_routing_authorization(tmp_path: Path):
    source = Path(__file__).resolve().parents[3] / "config" / "instrument_registry.json"
    raw = json.loads(source.read_text(encoding="utf-8"))
    raw["assets"]["ETH"]["spot"]["availability_state"] = "ROUTABLE"
    path = tmp_path / "bad.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="ETH spot must remain routing-not-authorized"):
        load_instrument_registry(path)


def test_registry_rejects_invented_bnb_spot_promotion(tmp_path: Path):
    source = Path(__file__).resolve().parents[3] / "config" / "instrument_registry.json"
    raw = json.loads(source.read_text(encoding="utf-8"))
    raw["assets"]["BNB"]["spot"]["hypercore_token_candidate"] = "UBNB"
    path = tmp_path / "bad-bnb.json"
    path.write_text(json.dumps(raw), encoding="utf-8")
    with pytest.raises(ValueError, match="BNB must not invent"):
        load_instrument_registry(path)


def test_registry_rejects_missing_asset():
    raw = {"schema_version": 1, "registry_id": "x", "venue": "hyperliquid", "quote_asset": "USDC", "assets": {}}
    with pytest.raises(ValueError, match="BTC/ETH/SOL/BNB"):
        InstrumentRegistry.from_mapping(raw)
