from __future__ import annotations

import ast
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

    def test_repair_module_has_only_two_helpers_and_no_parameter_state(self) -> None:
        tree = ast.parse(inspect.getsource(window_compat))
        functions = [node.name for node in tree.body if isinstance(node, ast.FunctionDef)]
        self.assertEqual(functions, ["window_positions", "earliest_pulse"])

        imports: list[str] = []
        assignments: list[ast.AST] = []
        for node in tree.body:
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                # __future__.annotations is language/runtime plumbing only.
                if node.module != "__future__":
                    imports.append(str(node.module))
            elif isinstance(node, (ast.Assign, ast.AnnAssign, ast.AugAssign)):
                assignments.append(node)

        self.assertEqual(imports, ["numpy", "pandas"])
        self.assertEqual(assignments, [])
        public_callables = sorted(
            name for name, value in vars(window_compat).items()
            if not name.startswith("_") and inspect.isfunction(value) and value.__module__ == window_compat.__name__
        )
        self.assertEqual(public_callables, ["earliest_pulse", "window_positions"])


if __name__ == "__main__":
    unittest.main()
