from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SNAPSHOT = ROOT / "research" / "leverage_0039" / "hyperliquid_margin_snapshot.json"


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def test_p4_3_margin_snapshot_hash_and_provenance_are_frozen():
    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert data["snapshot_id"] == "HYPERLIQUID-MAINNET-MARGIN-META-P4.3-V1"
    assert data["captured_at_utc"] == "2026-08-07T09:11:25Z"
    assert data["source"]["endpoint"] == "https://api.hyperliquid.xyz/info"
    assert data["source"]["request"] == {"type": "meta"}
    assert data["source"]["workflow_run_id"] == 31164707591
    assert data["source"]["artifact_id"] == 8988513159
    assert data["source"]["artifact_zip_sha256"] == (
        "9ac01e8efa08c975bebb249bf465a0fed2bd1dca17156cb9b6613521c660d881"
    )
    relevant = data["relevant_margin_inputs"]
    digest = hashlib.sha256(_canonical(relevant).encode("utf-8")).hexdigest()
    assert digest == data["relevant_margin_inputs_sha256"]
    assert digest == "38060892f1976315084de4dc4ed1c9f3885d909ffccc47bce7ad589315d8b9dd"
    assert data["raw_meta_sha256"] == (
        "ef4b108e65806d05dab615f533dd113fd86210d2e55a82a005fcad89a7f9aff8"
    )
    assert data["production_authorized"] is False


def test_p4_3_snapshot_contains_exact_target_asset_margin_tables():
    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    relevant = data["relevant_margin_inputs"]
    assets = relevant["assets"]
    assert list(assets) == ["BTC", "ETH", "SOL", "BNB"]
    assert {asset: (row["maxLeverage"], row["marginTableId"]) for asset, row in assets.items()} == {
        "BTC": (40, 56),
        "ETH": (25, 55),
        "SOL": (20, 54),
        "BNB": (10, 51),
    }
    assert all(not row["onlyIsolated"] and not row["isDelisted"] for row in assets.values())
    assert relevant["marginTables"] == {
        "51": {
            "description": "tiered 10x",
            "marginTiers": [
                {"lowerBound": "0.0", "maxLeverage": 10},
                {"lowerBound": "3000000.0", "maxLeverage": 5},
            ],
        },
        "54": {
            "description": "tiered 20x (2)",
            "marginTiers": [
                {"lowerBound": "0.0", "maxLeverage": 20},
                {"lowerBound": "70000000.0", "maxLeverage": 10},
            ],
        },
        "55": {
            "description": "tiered 25x",
            "marginTiers": [
                {"lowerBound": "0.0", "maxLeverage": 25},
                {"lowerBound": "100000000.0", "maxLeverage": 15},
            ],
        },
        "56": {
            "description": "tiered 40x",
            "marginTiers": [
                {"lowerBound": "0.0", "maxLeverage": 40},
                {"lowerBound": "150000000.0", "maxLeverage": 20},
            ],
        },
    }
