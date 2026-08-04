import unittest

from run_asym_beta_0024 import daily_cap


class DailyCapTests(unittest.TestCase):
    def test_daily_layer_cannot_increase_above_monthly(self):
        self.assertAlmostEqual(daily_cap(0.30, 0.45), 0.30)

    def test_daily_layer_can_reduce(self):
        self.assertAlmostEqual(daily_cap(0.30, 0.12), 0.12)

    def test_daily_layer_can_release_cap_without_exceeding_monthly(self):
        reduced = daily_cap(0.30, 0.10)
        recovered = daily_cap(0.30, 0.25)
        self.assertAlmostEqual(reduced, 0.10)
        self.assertAlmostEqual(recovered, 0.25)
        self.assertLessEqual(recovered, 0.30)

    def test_negative_values_are_clipped(self):
        self.assertEqual(daily_cap(0.30, -0.10), 0.0)


if __name__ == "__main__":
    unittest.main()
