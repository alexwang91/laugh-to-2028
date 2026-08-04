import unittest

import numpy as np

from run_entry_rank_eligibility_exit import (
    apply_band_with_mandatory_rebalance,
    build_entry_rank_eligibility_exit_target,
)


class EntryRankEligibilityExitTests(unittest.TestCase):
    def test_rank_reordering_does_not_replace_eligible_incumbents(self):
        # assets: BTC, A, B, C
        eligible = np.array([
            [False, True, True, True],
            [False, True, True, True],
            [False, False, True, True],
            [False, False, True, True],
            [False, False, True, True],
        ], dtype=bool)
        rank = np.array([
            [np.nan, 3.0, 2.0, 1.0],
            [np.nan, 4.0, 3.0, 5.0],  # C becomes rank 1, but A/B stay eligible.
            [np.nan, np.nan, 1.0, 5.0],  # A loses eligibility; C fills vacancy.
            [np.nan, np.nan, 6.0, 2.0],  # B/C remain despite rank reversal.
            [np.nan, np.nan, 6.0, 2.0],
        ])
        beta = np.ones(5)
        btc_trend = np.array([1.0, 1.0, 1.0, 1.0, -1.0])

        target, selected, mandatory, events = build_entry_rank_eligibility_exit_target(
            btc_idx=0,
            beta_budget=beta,
            btc_trend=btc_trend,
            eligible=eligible,
            rank_score=rank,
            slots=2,
        )

        self.assertEqual(set(np.flatnonzero(selected[0])), {1, 2})
        self.assertEqual(set(np.flatnonzero(selected[1])), {1, 2})
        self.assertFalse(bool(mandatory[1]))
        self.assertEqual(set(np.flatnonzero(selected[2])), {2, 3})
        self.assertTrue(bool(mandatory[2]))
        self.assertEqual(set(np.flatnonzero(selected[3])), {2, 3})
        self.assertFalse(bool(mandatory[3]))
        self.assertEqual(int(selected[4].sum()), 0)
        self.assertTrue(bool(mandatory[4]))
        self.assertAlmostEqual(float(target[4, 0]), 1.0)

        event_pairs = {(row.event, row.asset_index) for row in events.itertuples()}
        self.assertIn(("entry", 1.0), event_pairs)
        self.assertIn(("entry", 2.0), event_pairs)
        self.assertIn(("exit", 1.0), event_pairs)
        self.assertIn(("entry", 3.0), event_pairs)

    def test_mandatory_rebalance_overrides_l1_band(self):
        target = np.array([
            [0.98, 0.02],
            [1.00, 0.00],
        ])
        available = np.ones_like(target, dtype=bool)

        without_force = apply_band_with_mandatory_rebalance(
            target,
            available,
            np.array([True, False]),
            band=0.05,
        )
        with_force = apply_band_with_mandatory_rebalance(
            target,
            available,
            np.array([True, True]),
            band=0.05,
        )

        # L1 change is only 0.04, so the band keeps the old target without force.
        np.testing.assert_allclose(without_force[1], [0.98, 0.02])
        # Eligibility/risk-state exit authority must still execute immediately.
        np.testing.assert_allclose(with_force[1], [1.00, 0.00])


if __name__ == "__main__":
    unittest.main()
