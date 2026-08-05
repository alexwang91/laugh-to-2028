import unittest

from run_carry_impl_0034 import reserve_for_candidate, reserve_rows


class CarryImpl0034Tests(unittest.TestCase):
    def test_reserve_rows_maps_exact_token_index_and_ltv(self):
        token_by_index = {
            0: {"index": 0, "name": "USDC", "isCanonical": True},
            150: {"index": 150, "name": "HYPE", "isCanonical": True},
            999: {"index": 999, "name": "UBTC", "isCanonical": False},
        }
        payload = [
            [0, {"ltv": "0", "balance": "1000", "borrowYearlyRate": "0.05", "oraclePx": "1", "totalSupplied": "1000", "totalBorrowed": "100", "utilization": "0.1", "supplyYearlyRate": "0.004"}],
            [150, {"ltv": "0.5", "balance": "25", "borrowYearlyRate": "0.05", "oraclePx": "40", "totalSupplied": "25", "totalBorrowed": "0", "utilization": "0", "supplyYearlyRate": "0"}],
            [999, {"ltv": "0.7", "balance": "2", "borrowYearlyRate": "0.04", "oraclePx": "100000", "totalSupplied": "2", "totalBorrowed": "0.1", "utilization": "0.05", "supplyYearlyRate": "0.002"}],
        ]
        rows, by_token = reserve_rows(payload, token_by_index)
        self.assertEqual(len(rows), 3)
        self.assertFalse(by_token[0]["collateral_capable_by_ltv"])
        self.assertTrue(by_token[150]["collateral_capable_by_ltv"])
        self.assertTrue(by_token[999]["collateral_capable_by_ltv"])
        self.assertEqual(by_token[999]["token_name"], "UBTC")

    def test_candidate_collateral_uses_exact_base_token_index(self):
        reserve_by_token = {
            7: {"token_index": 7, "token_name": "UBTC", "ltv": 0.7, "collateral_capable_by_ltv": True},
            8: {"token_index": 8, "token_name": "UETH", "ltv": 0.0, "collateral_capable_by_ltv": False},
        }
        btc_candidate = {"base_token_index": 7}
        eth_candidate = {"base_token_index": 8}
        self.assertTrue(reserve_for_candidate(btc_candidate, reserve_by_token)["collateral_capable_by_ltv"])
        self.assertFalse(reserve_for_candidate(eth_candidate, reserve_by_token)["collateral_capable_by_ltv"])
        self.assertIsNone(reserve_for_candidate({"base_token_index": 9}, reserve_by_token))
        self.assertIsNone(reserve_for_candidate(None, reserve_by_token))

    def test_malformed_reserve_payload_hard_fails(self):
        with self.assertRaises(RuntimeError):
            reserve_rows({"not": "a list"}, {})
        with self.assertRaises(RuntimeError):
            reserve_rows([[1]], {})


if __name__ == "__main__":
    unittest.main()
