import unittest

from run_router_data_audit import (
    book_summary,
    candidate_matches,
    classify_candidate,
    marketable_vwap,
    spot_api_coin,
)


class RouterDataAuditTests(unittest.TestCase):
    def setUp(self):
        self.book = {
            "coin": "TEST",
            "time": 1,
            "levels": [
                [
                    {"px": "99", "sz": "10", "n": 1},
                    {"px": "98", "sz": "20", "n": 1},
                ],
                [
                    {"px": "101", "sz": "10", "n": 1},
                    {"px": "102", "sz": "20", "n": 1},
                ],
            ],
        }

    def test_book_summary_and_spread(self):
        summary = book_summary(self.book)
        self.assertEqual(summary["best_bid"], 99.0)
        self.assertEqual(summary["best_ask"], 101.0)
        self.assertEqual(summary["mid"], 100.0)
        self.assertAlmostEqual(summary["spread_bps"], 200.0)

    def test_buy_vwap_consumes_asks_and_reports_partial_fill(self):
        full = marketable_vwap(self.book, "buy", 2030.0)
        self.assertTrue(full["fully_fillable_in_returned_book"])
        self.assertAlmostEqual(full["base_filled"], 20.0)
        self.assertAlmostEqual(full["vwap"], 101.5)
        self.assertAlmostEqual(full["slippage_bps"], 150.0)

        partial = marketable_vwap(self.book, "buy", 5000.0)
        self.assertFalse(partial["fully_fillable_in_returned_book"])
        self.assertGreater(partial["unfilled_notional"], 0.0)
        self.assertEqual(partial["levels_used"], 2)

    def test_sell_vwap_consumes_bids(self):
        result = marketable_vwap(self.book, "sell", 1970.0)
        self.assertTrue(result["fully_fillable_in_returned_book"])
        self.assertAlmostEqual(result["base_filled"], 20.0)
        self.assertAlmostEqual(result["vwap"], 98.5)
        self.assertAlmostEqual(result["slippage_bps"], 150.0)

    def test_spot_api_coin_mapping(self):
        self.assertEqual(spot_api_coin({"name": "PURR/USDC", "index": 0}), "PURR/USDC")
        self.assertEqual(spot_api_coin({"name": "@107", "index": 107}), "@107")
        self.assertEqual(spot_api_coin({"name": "UBTC/USDC", "index": 107}), "@107")

    def test_candidate_matching_and_classification(self):
        exact = {
            "name": "ETH",
            "fullName": "Ether",
            "isCanonical": True,
            "evmContract": None,
        }
        pair = {"isCanonical": True}
        self.assertTrue(candidate_matches("ETH", exact))
        classification, _ = classify_candidate("ETH", exact, pair)
        self.assertEqual(classification, "verified_exact")

        ubtc = {
            "name": "UBTC",
            "fullName": "Bitcoin",
            "isCanonical": False,
            "evmContract": "0x123",
        }
        classification, _ = classify_candidate("BTC", ubtc, {"isCanonical": False})
        self.assertEqual(classification, "verified_official_ui_remap")

        wrapped = {
            "name": "WETH",
            "fullName": "Wrapped ETH",
            "isCanonical": False,
            "evmContract": "0x456",
        }
        classification, _ = classify_candidate("ETH", wrapped, pair)
        self.assertEqual(classification, "candidate_wrapped_or_bridged")


if __name__ == "__main__":
    unittest.main()
