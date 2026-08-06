from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INSTRUMENT_REGISTRY_PATH = REPO_ROOT / "config" / "instrument_registry.json"
CANONICAL_ASSETS = ("BTC", "ETH", "SOL", "BNB")

@dataclass(frozen=True)
class InstrumentRegistry:
    schema_version: int
    registry_id: str
    venue: str
    quote_asset: str
    assets: dict[str, dict[str, Any]]

    @classmethod
    def from_mapping(cls, raw: dict[str, Any]) -> "InstrumentRegistry":
        registry = cls(int(raw["schema_version"]), str(raw["registry_id"]), str(raw["venue"]).lower(), str(raw["quote_asset"]).upper(), {str(k).upper(): dict(v) for k, v in raw["assets"].items()})
        registry.validate()
        return registry

    def validate(self) -> None:
        if self.schema_version != 1: raise ValueError("Unsupported instrument registry schema_version")
        if self.venue != "hyperliquid": raise ValueError("Canonical instrument registry venue must be Hyperliquid")
        if self.quote_asset != "USDC": raise ValueError("Canonical quote asset must be USDC")
        if tuple(self.assets.keys()) != CANONICAL_ASSETS: raise ValueError("Instrument registry must contain BTC/ETH/SOL/BNB in canonical order")
        for asset in CANONICAL_ASSETS:
            row = self.assets[asset]
            if row.get("economic_asset") != asset: raise ValueError(f"Economic asset mismatch for {asset}")
            if not isinstance(row.get("route_policy"), str): raise ValueError(f"Route policy missing for {asset}")
            perp, spot, liquidity, custody = row.get("perp"), row.get("spot"), row.get("liquidity_metrics"), row.get("custody_redemption")
            if not all(isinstance(x, dict) for x in (perp, spot, liquidity, custody)): raise ValueError(f"Incomplete registry row for {asset}")
            if perp.get("identity") != asset: raise ValueError(f"Perp identity mismatch for {asset}")
            sz = perp.get("sz_decimals")
            if isinstance(sz, bool) or not isinstance(sz, int) or sz < 0: raise ValueError(f"Invalid perp szDecimals for {asset}")
            if perp.get("max_price_decimals") != 6 - sz: raise ValueError(f"Perp price precision mismatch for {asset}")
            if perp.get("availability_state") != "AVAILABLE": raise ValueError(f"Canonical perp must remain available for {asset}")
            if "status" not in liquidity or "status" not in custody: raise ValueError(f"Evidence status missing for {asset}")

        btc = self.assets["BTC"]
        if btc.get("route_policy") != "SPOT_CANDIDATE_WITH_PERP_FALLBACK": raise ValueError("BTC route policy must preserve spot candidate with perp fallback")
        if btc["spot"].get("identity_status") != "VERIFIED_PRIOR_EVIDENCE" or btc["spot"].get("evidence_decision_id") != "ROUTER-DATA-0004" or btc["spot"].get("hypercore_token_candidate") != "UBTC": raise ValueError("BTC prior spot verification is inconsistent")

        for asset, token, pair, chain in (("ETH","UETH","UETH/USDC","Ethereum"),("SOL","USOL","USOL/USDC","Solana")):
            row = self.assets[asset]; spot = row["spot"]
            if row.get("route_policy") != "SPOT_CANDIDATE_WITH_PERP_FALLBACK": raise ValueError(f"{asset} route policy must preserve spot candidate with perp fallback")
            if spot.get("identity_status") != "VERIFIED_UNIT_NATIVE_ASSET" or spot.get("hypercore_token_candidate") != token or spot.get("hypercore_pair_candidate") != pair or spot.get("native_chain") != chain: raise ValueError(f"{asset} Unit spot identity mismatch")
            if spot.get("availability_state") != "IDENTITY_VERIFIED_ROUTING_NOT_AUTHORIZED": raise ValueError(f"{asset} spot must remain routing-not-authorized after P2.2")
            if row["custody_redemption"].get("status") != "VERIFIED_UNIT_NATIVE_DEPOSIT_WITHDRAWAL": raise ValueError(f"{asset} native deposit/withdrawal evidence must be explicit")

        bnb = self.assets["BNB"]; spot = bnb["spot"]
        if bnb.get("route_policy") != "PERP_ONLY_CURRENT_VERIFIED_DEFAULT": raise ValueError("BNB must remain perp-only under the current verified route set")
        if bnb.get("route_policy_source") != "ROUTER-SPOT-IDENTITY-P2.2": raise ValueError("BNB current default must reference P2.2 evidence")
        if spot.get("identity_status") != "NO_VERIFIED_UNIT_NATIVE_ROUTE" or spot.get("availability_state") != "SPOT_UNAVAILABLE_PER_CURRENT_VERIFIED_ROUTE_SET": raise ValueError("BNB spot state must reflect the current verified route set")
        if any(spot.get(k) is not None for k in ("hypercore_token_candidate", "hypercore_pair_candidate")): raise ValueError("BNB must not invent a spot token or pair")
        if bnb["custody_redemption"].get("status") != "NO_VERIFIED_UNIT_NATIVE_ROUTE": raise ValueError("BNB custody/redemption status must remain evidence-scoped")

    def asset(self, asset: str) -> dict[str, Any]:
        key = asset.upper()
        if key not in self.assets: raise KeyError(f"Asset {key} is outside canonical BRRK universe")
        return self.assets[key]

def load_instrument_registry(path: Path | None = None) -> InstrumentRegistry:
    source = path or DEFAULT_INSTRUMENT_REGISTRY_PATH
    return InstrumentRegistry.from_mapping(json.loads(source.read_text(encoding="utf-8")))
