from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from research.governance.phase6_live_valuation import (
    Phase6ValuationError,
    contract_snapshot,
    derive_standard_account_valuation,
    validate_valuation_contract,
)

ROOT = Path(__file__).resolve().parents[2]


class Phase6LiveValuationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.contract = json.loads(
            (ROOT / "research/governance/phase6_live_valuation_contract.json").read_text(encoding="utf-8")
        )
        self.registry = json.loads((ROOT / "config/instrument_registry.json").read_text(encoding="utf-8"))
        self.spot = {
            "balances": [
                {"coin": "USDC", "token": 0, "total": "1000", "hold": "100", "entryNtl": "0"},
                {"coin": "UBTC", "token": 10, "total": "0.01", "hold": "0", "entryNtl": "900"},
                {"coin": "UETH", "token": 11, "total": "0.2", "hold": "0", "entryNtl": "500"},
                {"coin": "USOL", "token": 12, "total": "1.0", "hold": "0", "entryNtl": "100"},
            ]
        }
        self.perp = {
            "marginSummary": {"accountValue": "5000"},
            "assetPositions": [
                {"position": {"coin": "BTC", "szi": "0.02", "positionValue": "2000"}},
                {"position": {"coin": "ETH", "szi": "-0.5", "positionValue": "1500"}},
                {"position": {"coin": "BNB", "szi": "1", "positionValue": "600"}},
            ],
        }
        self.marks = {"UBTC": 100000.0, "UETH": 3000.0, "USOL": 150.0}

    def test_repository_contract_is_frozen_and_zero_authority(self) -> None:
        snapshot = contract_snapshot()
        self.assertEqual(snapshot["contract_id"], "PHASE6-LIVE-VALUATION-V1")
        self.assertEqual(snapshot["supported_user_abstraction"], "disabled")
        self.assertFalse(snapshot["production_authorized"])
        self.assertFalse(snapshot["signature_authorized"])
        self.assertFalse(snapshot["order_submission_authorized"])

    def test_standard_mapping_aggregates_spot_and_signed_perp_exposure(self) -> None:
        result = derive_standard_account_valuation(
            user_abstraction="disabled",
            spot_state=self.spot,
            perp_state=self.perp,
            spot_mark_by_token=self.marks,
        )
        self.assertEqual(result["perp_account_equity_usd"], 5000.0)
        self.assertEqual(result["spot_mark_to_market_usd"], 2750.0)
        self.assertEqual(result["account_equity_usd"], 7750.0)
        self.assertEqual(
            result["current_positions_notional_usd"],
            {"BTC": 3000.0, "ETH": -900.0, "SOL": 150.0, "BNB": 600.0},
        )

    def test_non_standard_modes_fail_closed(self) -> None:
        for mode in ("unifiedAccount", "portfolioMargin", "default", "dexAbstraction"):
            with self.subTest(mode=mode):
                with self.assertRaises(Phase6ValuationError):
                    derive_standard_account_valuation(
                        user_abstraction=mode,
                        spot_state=self.spot,
                        perp_state=self.perp,
                        spot_mark_by_token=self.marks,
                    )

    def test_unknown_nonzero_spot_or_perp_asset_fails_closed(self) -> None:
        spot = copy.deepcopy(self.spot)
        spot["balances"].append({"coin": "HYPE", "total": "1", "hold": "0"})
        with self.assertRaises(Phase6ValuationError):
            derive_standard_account_valuation(
                user_abstraction="disabled", spot_state=spot, perp_state=self.perp, spot_mark_by_token=self.marks
            )
        perp = copy.deepcopy(self.perp)
        perp["assetPositions"].append({"position": {"coin": "XRP", "szi": "1", "positionValue": "10"}})
        with self.assertRaises(Phase6ValuationError):
            derive_standard_account_valuation(
                user_abstraction="disabled", spot_state=self.spot, perp_state=perp, spot_mark_by_token=self.marks
            )

    def test_bnb_spot_is_not_silently_accepted(self) -> None:
        spot = copy.deepcopy(self.spot)
        spot["balances"].append({"coin": "BNB", "total": "1", "hold": "0"})
        with self.assertRaises(Phase6ValuationError):
            derive_standard_account_valuation(
                user_abstraction="disabled", spot_state=spot, perp_state=self.perp, spot_mark_by_token=self.marks
            )

    def test_duplicate_identity_and_invalid_equity_fail_closed(self) -> None:
        spot = copy.deepcopy(self.spot)
        spot["balances"].append({"coin": "USDC", "total": "1", "hold": "0"})
        with self.assertRaises(Phase6ValuationError):
            derive_standard_account_valuation(
                user_abstraction="disabled", spot_state=spot, perp_state=self.perp, spot_mark_by_token=self.marks
            )
        perp = copy.deepcopy(self.perp)
        perp["marginSummary"]["accountValue"] = "-99999"
        with self.assertRaises(Phase6ValuationError):
            derive_standard_account_valuation(
                user_abstraction="disabled", spot_state=self.spot, perp_state=perp, spot_mark_by_token=self.marks
            )

    def test_hold_is_included_in_total_ownership_but_must_not_exceed_total(self) -> None:
        first = derive_standard_account_valuation(
            user_abstraction="disabled", spot_state=self.spot, perp_state=self.perp, spot_mark_by_token=self.marks
        )
        changed = copy.deepcopy(self.spot)
        changed["balances"][0]["hold"] = "900"
        second = derive_standard_account_valuation(
            user_abstraction="disabled", spot_state=changed, perp_state=self.perp, spot_mark_by_token=self.marks
        )
        self.assertEqual(first["account_equity_usd"], second["account_equity_usd"])
        changed["balances"][0]["hold"] = "1001"
        with self.assertRaises(Phase6ValuationError):
            derive_standard_account_valuation(
                user_abstraction="disabled", spot_state=changed, perp_state=self.perp, spot_mark_by_token=self.marks
            )

    def test_contract_cannot_silently_enable_unified_or_change_bnb_policy(self) -> None:
        contract = copy.deepcopy(self.contract)
        contract["supported_account_mode"]["required_value"] = "unifiedAccount"
        with self.assertRaises(Phase6ValuationError):
            validate_valuation_contract(contract, instrument_registry=self.registry)
        registry = copy.deepcopy(self.registry)
        registry["assets"]["BNB"]["route_policy"] = "SPOT_CANDIDATE_WITH_PERP_FALLBACK"
        with self.assertRaises(Phase6ValuationError):
            validate_valuation_contract(self.contract, instrument_registry=registry)


if __name__ == "__main__":
    unittest.main()
