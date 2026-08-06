import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_CONFIG = REPO_ROOT / "config" / "product.json"
DECISION_REGISTRY = REPO_ROOT / "config" / "decision_registry.json"
DATA_CONTRACT = REPO_ROOT / "config" / "data_contract.json"


class ProductContractIntegrationTest(unittest.TestCase):
    def test_research_reads_same_canonical_product_config(self):
        product = json.loads(PRODUCT_CONFIG.read_text(encoding="utf-8"))
        self.assertEqual(product["long_universe"], ["BTC", "ETH", "SOL", "BNB"])
        self.assertEqual(product["primary_venue"], "hyperliquid")
        self.assertEqual(product["canonical_timezone"], "UTC")
        self.assertEqual(product["daily_boundary_utc"], "00:00")
        self.assertEqual(product["capital"]["initial_live_capital_usd"], 2000.0)
        self.assertEqual(product["capital"]["weekly_manual_contribution_usd"], 100.0)
        self.assertEqual(product["risk"]["catastrophic_drawdown_limit"], 0.70)
        self.assertIsNone(product["risk"]["operating_risk_budget"])
        self.assertEqual(product["risk"]["leverage_policy"], "MODEL_DETERMINED")

    def test_research_and_live_share_one_p3_1_data_contract(self):
        contract = json.loads(DATA_CONTRACT.read_text(encoding="utf-8"))
        self.assertEqual(contract["contract_id"], "BRRK-DATA-CONTRACT-P3.1-2026-08-06")
        self.assertEqual(contract["canonical_assets"], ["BTC", "ETH", "SOL", "BNB"])
        self.assertEqual(contract["decision_boundary"]["timezone"], "UTC")
        self.assertEqual(contract["decision_boundary"]["time"], "00:00:00")

        daily = contract["strategy_daily_close"]
        self.assertEqual(daily["source_id"], "BINANCE_SPOT_KLINES_V1")
        self.assertEqual(daily["interval"], "1d")
        self.assertEqual(daily["time_zone"], "0")
        self.assertFalse(daily["forward_fill"])
        self.assertEqual(daily["missing_policy"], "FAIL_CLOSED_NO_TARGET")
        self.assertEqual(
            {asset: rows[0]["source_symbol"] for asset, rows in daily["source_mappings"].items()},
            {
                "BTC": "BTCUSDT",
                "ETH": "ETHUSDT",
                "SOL": "SOLUSDT",
                "BNB": "BNBUSDT",
            },
        )

        funding = contract["router_market_inputs"]["funding"]
        self.assertEqual(funding["canonical_unit"], "bps_per_hour")
        self.assertEqual(funding["lookback_completed_hours"], 24)
        self.assertEqual(
            contract["authorization"],
            "DATA_CONTRACT_ONLY_NO_TARGET_OR_PRODUCTION_AUTHORIZATION",
        )

    def test_decision_registry_contains_required_status_classes(self):
        registry = json.loads(DECISION_REGISTRY.read_text(encoding="utf-8"))
        statuses = {decision["status"] for decision in registry["decisions"]}
        self.assertIn("ACCEPTED_RESEARCH_TARGET", statuses)
        self.assertIn("REJECTED_STOPPED", statuses)
        self.assertIn("SHADOW_ONLY", statuses)
        self.assertEqual(registry["production_authorized_components"], [])

    def test_stopped_lines_are_explicitly_registered(self):
        registry = json.loads(DECISION_REGISTRY.read_text(encoding="utf-8"))
        by_id = {decision["id"]: decision for decision in registry["decisions"]}
        for decision_id in [
            "PIT-ALPHA-0016-0018",
            "TSMOM-ALPHA-0029",
            "FUNDING-PNL-0003",
            "CARRY-PNL-0031-CARRY-RF-0036",
            "CARRY-STACK-0033",
        ]:
            self.assertEqual(by_id[decision_id]["status"], "REJECTED_STOPPED")

    def test_p1_1_order_identity_is_registered_without_production_authorization(self):
        registry = json.loads(DECISION_REGISTRY.read_text(encoding="utf-8"))
        by_id = {decision["id"]: decision for decision in registry["decisions"]}

        self.assertEqual(by_id["EXEC-ORDER-ID-P1.1"]["status"], "IMPLEMENTATION_VERIFIED")
        self.assertEqual(by_id["EXEC-ORDER-ID-P1.1"]["scope"], "execution_identity")
        self.assertEqual(registry["production_authorized_components"], [])


if __name__ == "__main__":
    unittest.main()
