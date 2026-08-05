import unittest

import pandas as pd

from run_carry_audit_0032 import ranked_dates, relative_error


class CarryAudit0032Tests(unittest.TestCase):
    def test_ranked_dates_uses_absolute_basis_only(self):
        idx = pd.date_range("2024-01-01", periods=4, freq="D")
        basis = pd.Series([0.01, -0.20, 0.05, -0.03], index=idx)
        out = ranked_dates(basis, n=3)
        self.assertEqual(out, [idx[1], idx[2], idx[3]])

    def test_relative_error_zero_for_identical_archives(self):
        self.assertEqual(relative_error(123.45, 123.45), 0.0)
        self.assertAlmostEqual(relative_error(100.0, 100.000001), 1e-8, places=10)


if __name__ == "__main__":
    unittest.main()
