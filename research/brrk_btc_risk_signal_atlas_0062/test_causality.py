import unittest
import numpy as np
import pandas as pd
from research.brrk_btc_risk_signal_atlas_0062 import engine
from research.brrk_btc_risk_signal_atlas_0062.test_dimensions import toy_frames


class Causality(unittest.TestCase):
    def test_future_rows_cannot_change_past_signals(self):
        base = toy_frames(460)
        cells1, families1, _ = engine.build_signal_atlas(base)
        cutoff = 360
        changed = {a: f.copy() for a, f in base.items()}
        for frame in changed.values():
            rows = frame.index[cutoff+1:]
            factor = np.linspace(1.0, 1.8, len(rows))
            frame.loc[rows, "open"] *= factor
            frame.loc[rows, "close"] *= factor
            frame.loc[rows, "high"] = np.maximum(frame.loc[rows, "open"], frame.loc[rows, "close"])*1.02
            frame.loc[rows, "low"] = np.minimum(frame.loc[rows, "open"], frame.loc[rows, "close"])*0.98
            frame.loc[rows, "volume"] *= factor
            frame.loc[rows, "quote_volume"] = frame.loc[rows, "volume"]*frame.loc[rows, "close"]
        cells2, families2, _ = engine.build_signal_atlas(changed)
        pd.testing.assert_frame_equal(cells1.iloc[:cutoff+1], cells2.iloc[:cutoff+1], check_exact=True)
        pd.testing.assert_frame_equal(families1.iloc[:cutoff+1], families2.iloc[:cutoff+1], check_exact=True)


if __name__ == "__main__":
    unittest.main()
