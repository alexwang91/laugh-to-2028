import io
import unittest
import zipfile

import pandas as pd

from run_carry_data_0030 import distribution, month_gaps, parse_kline_payload, timestamp_unit


class CarryData0030Tests(unittest.TestCase):
    def _zip_csv(self, text: str) -> bytes:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("sample.csv", text)
        return buf.getvalue()

    def test_timestamp_unit_ms_and_us(self):
        self.assertEqual(timestamp_unit(pd.Series([1640995200000, 1641081600000])), "ms")
        self.assertEqual(timestamp_unit(pd.Series([1640995200000000, 1641081600000000])), "us")

    def test_parse_kline_payload_accepts_headerless_binance_shape(self):
        payload = self._zip_csv(
            "1640995200000,100,110,90,105,10,1641081599999,1000,100,5,500,0\n"
            "1641081600000,105,120,100,115,12,1641167999999,1300,120,6,650,0\n"
        )
        frame = parse_kline_payload(payload)
        self.assertEqual(len(frame), 2)
        self.assertEqual(str(frame.index[0].date()), "2022-01-01")
        self.assertAlmostEqual(float(frame.iloc[0]["close"]), 105.0)
        self.assertAlmostEqual(float(frame.iloc[1]["quote_volume"]), 1300.0)

    def test_month_gaps_are_internal_only(self):
        self.assertEqual(month_gaps(["2024-01", "2024-03", "2024-04"]), ["2024-02"])
        self.assertEqual(month_gaps(["2024-01"]), [])
        self.assertEqual(month_gaps([]), [])

    def test_distribution_is_deterministic(self):
        out = distribution(pd.Series([-0.02, 0.0, 0.01, 0.03]))
        self.assertAlmostEqual(out["median"], 0.005)
        self.assertAlmostEqual(out["mean"], 0.005)
        self.assertEqual(out["min"], -0.02)
        self.assertEqual(out["max"], 0.03)


if __name__ == "__main__":
    unittest.main()
