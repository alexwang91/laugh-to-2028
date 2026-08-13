import unittest
from collections import Counter
import numpy as np
import pandas as pd
from research.brrk_btc_risk_signal_atlas_0062 import engine


def toy_frames(n=420):
    idx = pd.date_range("2024-01-01", periods=n, freq="D")
    out = {}
    for j, asset in enumerate(("BTC", "ETH", "SOL")):
        t = np.arange(n, dtype=float)
        close = np.exp(4.0 + 0.001*t + 0.08*np.sin(t/(13.0+j)))
        open_ = close*(1.0 + 0.002*np.sin(t/5.0+j))
        high = np.maximum(open_, close)*1.01
        low = np.minimum(open_, close)*0.99
        volume = 1000.0 + 100.0*np.sin(t/7.0+j) + t
        out[asset] = pd.DataFrame({"open":open_,"high":high,"low":low,"close":close,"volume":volume,"quote_volume":volume*close,"trades":1000.0+t}, index=idx)
    return out


class Dimensions(unittest.TestCase):
    def test_frozen_dimensions(self):
        cells, families, meta = engine.build_signal_atlas(toy_frames())
        self.assertEqual(cells.shape[1], 185)
        self.assertEqual(families.shape[1], 17)
        self.assertEqual(len(engine._track_defs()), 34)
        counts = Counter(m.family for m in meta.values())
        self.assertEqual(sum(counts.values()), 185)
        self.assertEqual(counts["F05_VOL_ADJUSTED_TREND_GUARDS"], 25)
        self.assertEqual(counts["F24_FIXED_LOW_ORDER_INTERACTIONS"], 6)


if __name__ == "__main__":
    unittest.main()
