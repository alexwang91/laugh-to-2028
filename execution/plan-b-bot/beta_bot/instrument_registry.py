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
        registry = cls(
            schema_version=int(raw["schema_version"]),
            registry_id=str(raw["registry_id"]),
            venue=str(raw["venue"]).lower(),
            quote_asset=str(raw["quote_asset"]).upper(),
            assets={str(k).upper(): dict(v) for k, v in raw["assets"].items()},
        )
        registry.validate()
        return registry

    def validate(self) -> None:
        if self.schema_version != 1:
            raise ValueError("Unsupported instrument registry schema_version")
        if self.venue != "hyperliquid":
            raise ValueError("Canonical instrument registry venue must be Hyperliquid")
        if self.quote_asset != "USDC":
            raise ValueError("Canonical quote asset must be USDC")
        if tuple(self.assets.keys()) != CANONICAL_ASSETS:
            raise ValueError("Instrument registry must contain BTC/ETH/SOL/BNB in canonical order")

        for asset in CANONICAL_ASSETS:
            row = self.assets[asset]
            if row.get("economic_asset") != asset:
                raise ValueError(f"Economic asset mismatch for {asset}")
            perp = row.get("perp")
            spot = row.get("spot")
            liquidity = row.get("liquidity_metrics")
            custody = row.get("custody_redemption")
            if not all(isinstance(x, dict) for x in (perp, spot, liquidity, custody)):
                raise ValueError(f"Incomplete registry row for {asset}")
            if perp.get("identity") != asset:
                raise ValueError(f"Perp identity mismatch for {asset}")
            sz_decimals = perp.get("sz_decimals")
            if isinstance(sz_decimals, bool) or not isinstance(sz_decimals, int) or sz_decimals < 0:
                raise ValueError(f"Invalid perp szDecimals for {asset}")
            expected_price_decimals = 6 - sz_decimals
            if perp.get("max_price_decimals") != expected_price_decimals:
                raise ValueError(f"Perp price precision mismatch for {asset}")
            if perp.get("availability_state") != "AVAILABLE":
                raise ValueError(f"Canonical perp must remain available for {asset}")
            if "status" not in liquidity or "status" not in custody:
                raise ValueError(f"Evidence status missing for {asset}")

        btc = self.assets["BTC"]["spot"]
        if btc.get("identity_status") != "VERIFIED_PRIOR_EVIDENCE":
            raise ValueError("BTC spot identity must import prior verification")
        if btc.get("evidence_decision_id") != "ROUTER-DATA-0004":
            raise ValueError("BTC spot identity must reference ROUTER-DATA-0004")
        if btc.get("hypercore_token_candidate") != "UBTC":
            raise ValueError("Verified BTC HyperCore token identity must remain UBTC")

        expected_unit_spot = {
            "ETH": ("UETH", "UETH/USDC", "Ethereum"),
            "SOL": ("USOL", "USOL/USDC", "Solana"),
        }
        for asset, (token, pair, native_chain) in expected_unit_spot.items():
            spot = self.assets[asset]["spot"]
            custody = self.assets[asset]["custody_redemption"]
            if spot.get("identity_status") != "VERIFIED_UNIT_NATIVE_ASSET":
                raise ValueError(f"{asset} spot identity must be verified by Unit evidence")
            if spot.get("hypercore_token_candidate") != token or spot.get("hypercore_pair_candidate") != pair:
                raise ValueError(f"{asset} Unit spot identity mismatch")
            if spot.get("native_chain") != native_chain:
                raise ValueError(f"{asset} native-chain mapping mismatch")
            if spot.get("availability_state") != "IDENTITY_VERIFIED_ROUTING_NOT_AUTHORIZED":
                raise ValueError(f"{asset} spot must remain routing-not-authorized after P2.2")
            if custody.get("status") != "VERIFIED_UNIT_NATIVE_DEPOSIT_WITHDRAWAL":
                raise ValueError(f"{asset} native deposit/withdrawal evidence must be explicit")

        bnb_spot = self.assets["BNB"]["spot"]
        bnb_custody = self.assets["BNB"]["custody_redemption"]
        if bnb_spot.get("identity_status") != "NO_VERIFIED_UNIT_NATIVE_ROUTE":
            raise ValueError("BNB must not claim a verified Unit spot route")
        if bnb_spot.get("availability_state") != "SPOT_UNAVAILABLE_PER_VALIDATED_UNIT_ROUTE":
            raise ValueError("BNB spot availability must remain unavailable under validated Unit evidence")
        if any(bnb_spot.get(k) is not None for k in ("hypercore_token_candidate", "hypercore_pair_candidate")):
            raise ValueError("BNB must not invent a HyperCore spot token or pair")
        if bnb_custody.get("status") != "NO_VERIFIED_UNIT_NATIVE_ROUTE":
            raise ValueError("BNB custody/redemption status must reflect unavailable validated route")

    def asset(self, asset: str) -> dict[str, Any]:
        key = asset.upper()
        if key not in self.assets:
            raise KeyError(f"Asset {key} is outside canonical BRRK universe")
        return self.assets[key]


def load_instrument_registry(path: Path | None = None) -> InstrumentRegistry:
    source = path or DEFAULT_INSTRUMENT_REGISTRY_PATH
    raw = json.loads(source.read_text(encoding="utf-8"))
    return InstrumentRegistry.from_mapping(raw)
