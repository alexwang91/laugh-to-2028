import unittest
import pandas as pd
from run_tsmom_pit_eligibility import MIN_DAYS, QVOL_FLOOR, contiguous_run_length, eligibility_for_history


class EligibilityTests(unittest.TestCase):
    def test_240th_contiguous_bar_is_first_possible(self):
        idx = pd.date_range("2024-01-01", periods=MIN_DAYS, freq="D")
        df = pd.DataFrame({"quote_volume": QVOL_FLOOR + 1}, index=idx)
        out = eligibility_for_history(df)
        self.assertFalse(bool(out.iloc[-2]["eligible"]))
        self.assertTrue(bool(out.iloc[-1]["eligible"]))

    def test_gap_resets_contiguous_age(self):
        a = pd.date_range("2024-01-01", periods=MIN_DAYS, freq="D")
        b = pd.date_range(a[-1] + pd.Timedelta(days=2), periods=3, freq="D")
        run = contiguous_run_length(a.append(b))
        self.assertEqual(int(run.loc[a[-1]]), MIN_DAYS)
        self.assertEqual(int(run.loc[b[0]]), 1)

    def test_low_volume_blocks_eligibility(self):
        idx = pd.date_range("2024-01-01", periods=MIN_DAYS, freq="D")
        df = pd.DataFrame({"quote_volume": QVOL_FLOOR + 1}, index=idx)
        df.loc[idx[-1], "quote_volume"] = QVOL_FLOOR - 1
        out = eligibility_for_history(df)
        self.assertFalse(bool(out.iloc[-1]["eligible"]))

    def test_eligibility_is_effective_next_day(self):
        idx = pd.date_range("2024-01-01", periods=MIN_DAYS, freq="D")
        df = pd.DataFrame({"quote_volume": QVOL_FLOOR + 1}, index=idx)
        out = eligibility_for_history(df)
        self.assertEqual(out.iloc[-1]["effective_date"], idx[-1] + pd.Timedelta(days=1))


if __name__ == "__main__":
    unittest.main()
