import unittest

import pandas as pd

from run_funding_data_audit import month_gaps, parse_timestamp


class FundingDataAuditTests(unittest.TestCase):
    def test_month_gap_detection(self):
        self.assertEqual(
            month_gaps(["2024-01", "2024-02", "2024-04"]),
            ["2024-03"],
        )

    def test_millisecond_and_microsecond_timestamp_detection(self):
        millis = pd.Series([1704067200000, 1704096000000])
        micros = pd.Series([1704067200000000, 1704096000000000])
        parsed_ms = parse_timestamp(millis)
        parsed_us = parse_timestamp(micros)
        self.assertEqual(str(parsed_ms.iloc[0]), "2024-01-01 00:00:00+00:00")
        self.assertEqual(str(parsed_us.iloc[1]), "2024-01-01 08:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
