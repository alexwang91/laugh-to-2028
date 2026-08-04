import unittest

from run_tsmom_perp_universe_audit import classify, month_number


class PerpUniverseAuditTests(unittest.TestCase):
    def test_classify(self):
        self.assertEqual(classify("BTCUSDT"), "ordinary_usdt_candidate")
        self.assertEqual(classify("USDCUSDT"), "stable_base")
        self.assertEqual(classify("BTCUPUSDT"), "leveraged_token_like")
        self.assertEqual(classify("BTCUSD"), "non_usdt")

    def test_month_number(self):
        self.assertEqual(month_number("2024-01"), 2024*12+1)
        self.assertEqual(month_number("2024-03")-month_number("2023-12"), 3)
        self.assertIsNone(month_number(None))


if __name__ == "__main__":
    unittest.main()
