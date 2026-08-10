from __future__ import annotations

import inspect
import unittest

import numpy as np
import pandas as pd

from research.brrk_exhaustion_pulse_0046 import run_once as p0046_run
from research.brrk_exhaustion_pulse_0046 import window_compat
from research.brrk_exhaustion_trigger_0045 import run_once as t0045


class TestBrrkExhaustionPulse0046WindowRepair(unittest.TestCase):
    def setUp(self) -> None:
        self.index = pd.date_range("2024-01-01", periods=40, freq="D")

    def _assert_same_positions(self, peak: pd.Timestamp, bounds: tuple[int, int]) -> None:
        self.assertEqual(
            window_compat.window_positions(self.index, peak, bounds),
            t0045._window_positions(self.index, peak, bounds),
        )

    def test_window_positions_exactly_match_immutable_0045(self) -> None:
        cases = [
            (pd.Timestamp("2023-12-15"), (-14, -7)),  # absent peak -> []
            (self.index[25], (-14, -7)),              # normal PRE14_7
            (self.index[5], (-14, 0)),                # left-edge clipping
            (self.index[-2], (-7, 3)),                # right-edge clipping
            (self.index[0], (-21, 0)),                # single clipped position
        ]
        for peak, bounds in cases:
            with self.subTest(peak=peak, bounds=bounds):
                self._assert_same_positions(peak, bounds)

    def test_absent_peak_is_no_pulse_no_onset_not_event_filter(self) -> None:
        pulse = np.ones(len(self.index), dtype=bool)
        absent = pd.Timestamp("2023-02-03")
        self.assertEqual(window_compat.window_positions(self.index, absent, (-21, 0)), [])
        self.assertEqual(window_compat.earliest_pulse(pulse, self.index, absent, (-21, 0)), (None, None))

    def test_earliest_pulse_uses_first_position_in_clipped_session_window(self) -> None:
        peak = self.index[5]
        positions = window_compat.window_positions(self.index, peak, (-14, 0))
        pulse = np.zeros(len(self.index), dtype=bool)
        pulse[positions[1]] = True
        pulse[positions[-1]] = True
        date, lead = window_compat.earliest_pulse(pulse, self.index, peak, (-14, 0))
        self.assertEqual(date, str(self.index[positions[1]].date()))
        self.assertEqual(lead, int(self.index.get_loc(peak) - positions[1]))

    def test_repair_is_applied_only_after_lock_validation_and_before_run_locked(self) -> None:
        src = inspect.getsource(p0046_run.evaluate)
        validate_pos = src.index("calibration.validate_lock")
        import_pos = src.index('importlib.import_module("research.brrk_exhaustion_pulse_0046.evaluation")')
        window_bind_pos = src.index("evaluation._window_positions = window_compat.window_positions")
        onset_bind_pos = src.index("evaluation._earliest_pulse = window_compat.earliest_pulse")
        run_pos = src.index("evaluation.run_locked")
        self.assertLess(validate_pos, import_pos)
        self.assertLess(import_pos, window_bind_pos)
        self.assertLess(window_bind_pos, onset_bind_pos)
        self.assertLess(onset_bind_pos, run_pos)

    def test_repair_module_contains_no_research_degrees_of_freedom(self) -> None:
        src = inspect.getsource(window_compat)
        forbidden = (
            "threshold",
            "VAR",
            "bootstrap",
            "S1_",
            "S2_",
            "S3_",
            "S4_",
            "TRUE_EXHAUSTION",
            "CONTINUATION_FALSE_TOP",
            "episode",
            "gross",
            "portfolio",
        )
        for token in forbidden:
            self.assertNotIn(token, src)


if __name__ == "__main__":
    unittest.main()
