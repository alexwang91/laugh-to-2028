from __future__ import annotations

import unittest

import numpy as np

from research.brrk_crypto_carry_atlas_0072.engine import (
    ASSETS,
    BASE_SEED,
    FAIL,
    HYPOTHESES,
    INCONCLUSIVE,
    INVALID,
    PASS,
    Bar,
    bh_adjust,
    build_state_rows,
    classify_from_results,
    evaluate,
    midranks,
    parse_binance_daily_klines,
)
from research.brrk_crypto_carry_atlas_0072.qualification import run_qualification, _pass_components, _synthetic_bars


class TestCarryAtlasStage4(unittest.TestCase):
    def test_timestamp_units_are_fail_closed(self):
        spot = b"1782864000000000,1,2,0.5,1.5,10,0,0,0,0,0,0\n"
        um = b"1782864000000,1,2,0.5,1.5,10,0,0,0,0,0,0\n"
        self.assertEqual(parse_binance_daily_klines(spot, "MICROSECONDS")[0].day, "2026-07-01")
        self.assertEqual(parse_binance_daily_klines(um, "MILLISECONDS")[0].day, "2026-07-01")
        with self.assertRaisesRegex(ValueError, "TIMESTAMP_UNIT_DRIFT"):
            parse_binance_daily_klines(spot, "MILLISECONDS")
        with self.assertRaisesRegex(ValueError, "TIMESTAMP_UNIT_DRIFT"):
            parse_binance_daily_klines(um, "MICROSECONDS")

    def test_midrank_exact_ties(self):
        np.testing.assert_array_equal(midranks([3.0, 1.0, 1.0, 2.0]), [4.0, 1.5, 1.5, 3.0])

    def test_complete_july_fixture_yields_21_states_each(self):
        spot, perp = _synthetic_bars()
        rows = build_state_rows(spot, perp)
        self.assertEqual(len(rows), 63)
        self.assertEqual({a: sum(r.asset == a for r in rows) for a in ASSETS}, {"BTC": 21, "ETH": 21, "SOL": 21})
        self.assertTrue(all("2026-07-08" <= r.day <= "2026-07-28" for r in rows))

    def test_missing_required_day_drops_state_without_fill(self):
        spot, perp = _synthetic_bars()
        spot["BTC"] = [b for b in spot["BTC"] if b.day != "2026-07-10"]
        rows = build_state_rows(spot, perp)
        self.assertLess(sum(r.asset == "BTC" for r in rows), 21)
        self.assertEqual(sum(r.asset == "ETH" for r in rows), 21)
        self.assertEqual(sum(r.asset == "SOL" for r in rows), 21)

    def test_bh_requires_exact_six_hypotheses(self):
        p = {h: (i + 1) / 100.0 for i, h in enumerate(HYPOTHESES)}
        q = bh_adjust(p)
        self.assertEqual(set(q), set(HYPOTHESES))
        self.assertTrue(all(0.0 <= float(q[h]) <= 1.0 for h in HYPOTHESES))
        with self.assertRaisesRegex(ValueError, "CANDIDATE_COUNT_DRIFT"):
            bh_adjust({HYPOTHESES[0]: 0.1})

    def test_terminal_classification_regimes(self):
        effects, q, loao = _pass_components()
        self.assertEqual(classify_from_results(True, True, effects, q, loao)[0], PASS)
        failed = dict(effects)
        failed[HYPOTHESES[0]] = 0.10
        self.assertEqual(classify_from_results(True, True, failed, q, loao)[0], FAIL)
        self.assertEqual(classify_from_results(True, False, effects, q, loao)[0], INCONCLUSIVE)
        undefined = dict(effects)
        undefined[HYPOTHESES[3]] = None
        self.assertEqual(classify_from_results(True, True, undefined, q, loao)[0], INCONCLUSIVE)
        self.assertEqual(classify_from_results(False, True, effects, q, loao)[0], INVALID)

    def test_scientific_evaluate_rejects_replicate_drift_before_use(self):
        with self.assertRaisesRegex(ValueError, "SCIENTIFIC_REPLICATE_COUNT_DRIFT"):
            evaluate([], reps=19999)

    def test_frozen_constants(self):
        self.assertEqual(ASSETS, ("BTC", "ETH", "SOL"))
        self.assertEqual(len(HYPOTHESES), 6)
        self.assertEqual(BASE_SEED, 720072000)

    def test_nonhistorical_qualification_passes(self):
        result = run_qualification()
        self.assertEqual(result["qualification"], "PASS")
        self.assertEqual(result["controlled_scientific_history_reads"], 0)
        self.assertEqual(result["raw_artifact_reads"], 0)
        self.assertEqual(result["source_network_fetches"], 0)
        self.assertEqual(result["stage8_attempt_consumed"], 0)
        self.assertFalse(result["production_authorized"])
        self.assertFalse(result["signature_authorized"])
        self.assertFalse(result["order_submission_authorized"])


if __name__ == "__main__":
    unittest.main()
