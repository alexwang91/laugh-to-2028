from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import urllib.request


INFO_URL = "https://api.hyperliquid.xyz/info"
TARGET_ASSETS = ("BTC", "ETH", "SOL", "BNB")


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _sha256(value: object) -> str:
    return hashlib.sha256(_canonical(value).encode("utf-8")).hexdigest()


def fetch_meta() -> dict:
    payload = json.dumps({"type": "meta"}).encode("utf-8")
    request = urllib.request.Request(
        INFO_URL,
        data=payload,
        headers={"Content-Type": "application/json", "User-Agent": "laugh-to-2028-p4.3-snapshot/1"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"Hyperliquid info endpoint returned HTTP {response.status}")
        body = response.read()
    parsed = json.loads(body)
    if not isinstance(parsed, dict):
        raise RuntimeError("Hyperliquid meta response is not an object")
    return parsed


def build_snapshot(meta: dict, *, captured_at_utc: str) -> dict:
    universe = meta.get("universe")
    if not isinstance(universe, list):
        raise RuntimeError("Hyperliquid meta.universe is missing or malformed")

    selected: dict[str, dict] = {}
    referenced_table_ids: set[int] = set()
    for row in universe:
        if not isinstance(row, dict):
            continue
        name = row.get("name")
        if name not in TARGET_ASSETS:
            continue
        max_leverage = row.get("maxLeverage")
        margin_table_id = row.get("marginTableId", max_leverage)
        if isinstance(max_leverage, bool) or not isinstance(max_leverage, int):
            raise RuntimeError(f"{name} meta row has invalid maxLeverage={max_leverage!r}")
        if isinstance(margin_table_id, bool) or not isinstance(margin_table_id, int):
            raise RuntimeError(f"{name} meta row has invalid marginTableId={margin_table_id!r}")
        selected[name] = {
            "name": name,
            "szDecimals": row.get("szDecimals"),
            "maxLeverage": max_leverage,
            "marginTableId": margin_table_id,
            "onlyIsolated": bool(row.get("onlyIsolated", False)),
            "isDelisted": bool(row.get("isDelisted", False)),
        }
        referenced_table_ids.add(margin_table_id)

    missing = [asset for asset in TARGET_ASSETS if asset not in selected]
    if missing:
        raise RuntimeError(f"Hyperliquid meta missing required assets: {missing}")

    raw_tables = meta.get("marginTables", [])
    if not isinstance(raw_tables, list):
        raise RuntimeError("Hyperliquid meta.marginTables is malformed")

    tables: dict[str, object] = {}
    for row in raw_tables:
        if not isinstance(row, list) or len(row) != 2:
            raise RuntimeError(f"Malformed marginTables row: {row!r}")
        table_id, table = row
        if isinstance(table_id, bool) or not isinstance(table_id, int):
            raise RuntimeError(f"Malformed margin table id: {table_id!r}")
        if table_id in referenced_table_ids:
            tables[str(table_id)] = table

    # Hyperliquid documents that IDs below 50 denote a single tier whose max leverage
    # equals the ID. Such IDs need not appear in marginTables. Preserve this rule
    # explicitly instead of inventing a synthetic API row.
    missing_tables = sorted(
        table_id for table_id in referenced_table_ids if table_id >= 50 and str(table_id) not in tables
    )
    if missing_tables:
        raise RuntimeError(f"Referenced tiered margin tables missing from meta: {missing_tables}")

    relevant = {
        "assets": {asset: selected[asset] for asset in TARGET_ASSETS},
        "marginTables": tables,
        "singleTierRule": "marginTableId < 50 => single tier with maxLeverage equal to marginTableId",
    }
    return {
        "schema_version": 1,
        "snapshot_id": "HYPERLIQUID-MAINNET-MARGIN-META-P4.3-V1",
        "captured_at_utc": captured_at_utc,
        "source": {
            "endpoint": INFO_URL,
            "request": {"type": "meta"},
            "network": "mainnet",
        },
        "target_assets": list(TARGET_ASSETS),
        "relevant_margin_inputs": relevant,
        "relevant_margin_inputs_sha256": _sha256(relevant),
        "raw_meta_sha256": _sha256(meta),
        "raw_meta": meta,
        "production_authorized": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    captured_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    snapshot = build_snapshot(fetch_meta(), captured_at_utc=captured_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"snapshot_id={snapshot['snapshot_id']}")
    print(f"captured_at_utc={snapshot['captured_at_utc']}")
    print(f"relevant_margin_inputs_sha256={snapshot['relevant_margin_inputs_sha256']}")
    print(f"raw_meta_sha256={snapshot['raw_meta_sha256']}")
    for asset, row in snapshot["relevant_margin_inputs"]["assets"].items():
        print(
            f"asset={asset} maxLeverage={row['maxLeverage']} "
            f"marginTableId={row['marginTableId']} onlyIsolated={row['onlyIsolated']}"
        )


if __name__ == "__main__":
    main()
