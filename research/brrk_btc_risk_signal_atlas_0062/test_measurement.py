import unittest
import numpy as np
import pandas as pd
from research.brrk_btc_risk_signal_atlas_0062 import engine


class Measurement(unittest.TestCase):
    def test_targets(self):
        idx = pd.date_range("2026-01-01", periods=70, freq="D")
        rising = pd.Series(np.exp(0.01*np.arange(70)), index=idx)
        a = engine.build_targets(rising)
        self.assertAlmostEqual(a.iloc[0]["T1_CASH_ADVANTAGE@5"], -0.05, places=12)
        self.assertAlmostEqual(a.iloc[0]["T1_CASH_ADVANTAGE@20"], -0.20, places=12)
        self.assertAlmostEqual(a.iloc[0]["T2_MAX_ADVERSE_EXCURSION@20"], 0.0, places=12)
        falling = pd.Series(np.exp(-0.01*np.arange(70)), index=idx)
        b = engine.build_targets(falling)
        self.assertAlmostEqual(b.iloc[0]["T1_CASH_ADVANTAGE@5"], 0.05, places=12)
        self.assertAlmostEqual(b.iloc[0]["T2_MAX_ADVERSE_EXCURSION@5"], 0.05, places=12)

    def test_tie_rank_and_blocks(self):
        z = engine._average_rank_z(pd.Series([1.0, 2.0, 2.0, 4.0]))
        self.assertAlmostEqual(z[1], z[2], places=14)
        self.assertAlmostEqual(float(np.mean(z)), 0.0, places=14)
        blocks = engine._count_balanced_blocks(1003, 4)
        self.assertEqual([int((blocks == i).sum()) for i in range(4)], [251, 251, 251, 250])

    def test_mbb_seed_determinism(self):
        n = 300
        x = np.linspace(-1.0, 1.0, n)
        families = pd.DataFrame({f: x + 0.01*(i+1)*np.sin(np.arange(n)/11.0) for i, f in enumerate(engine.ALL_FAMILIES)})
        names = sorted({t for _, ts in engine._track_defs().values() for t in ts})
        targets = pd.DataFrame({t: x + 0.02*(i+1)*np.cos(np.arange(n)/17.0) for i, t in enumerate(names)})
        tracks = engine._track_defs()
        observed = {k: min(engine._spearman(families[f], targets[t]) for t in ts) for k, (f, ts) in tracks.items()}
        a = engine._bootstrap_global_lcb(families, targets, tracks, observed, block_length=60, replicates=12, seed=620062)
        b = engine._bootstrap_global_lcb(families, targets, tracks, observed, block_length=60, replicates=12, seed=620062)
        self.assertEqual(a, b)
        self.assertEqual(len(a[1]), 34)


if __name__ == "__main__":
    unittest.main()
