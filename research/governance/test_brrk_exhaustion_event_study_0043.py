from __future__ import annotations

import inspect
from pathlib import Path
import unittest

from research.governance import brrk_exhaustion_event_study as audit


class BRRKExhaustionEventStudy0043Tests(unittest.TestCase):
    def test_identity_and_fixed_taxonomy(self) -> None:
        self.assertEqual(audit.AUDIT_ID, "BRRK-EXHAUSTION-EVENT-STUDY-0043")
        self.assertEqual(audit.DOWNSIDE_PANELS, (0.10, 0.15, 0.20))
        self.assertEqual(audit.PRIMARY_DOWNSIDE, 0.15)
        self.assertEqual(audit.FRESH_HIGH, 0.02)
        self.assertEqual(audit.TREND_HORIZONS, (20, 60, 120, 240))
        self.assertEqual(audit.TREND_WEIGHTS, (0.15, 0.25, 0.30, 0.30))

    def test_user_anchors_are_sanity_checks_only(self) -> None:
        self.assertEqual(
            audit.ANCHORS,
            ("2023-12-25", "2024-03-31", "2024-11-24", "2025-01-26", "2025-10-06"),
        )
        source = inspect.getsource(audit.detect_candidates)
        for anchor in audit.ANCHORS:
            self.assertNotIn(anchor, source)

    def test_no_portfolio_mutation_or_economic_simulator(self) -> None:
        source = inspect.getsource(audit)
        self.assertNotIn("create_order", source)
        self.assertNotIn("submit_order", source)
        self.assertNotIn("run_portfolio(", source)
        self.assertNotIn("simulate(", source)
        self.assertNotIn("target_weights =", source)

    def test_warning_thresholds_are_fixed_panel_not_selected(self) -> None:
        source = inspect.getsource(audit.run)
        self.assertIn("for q in (0.70, 0.80, 0.90)", source)
        self.assertNotIn("best_q", source)
        self.assertNotIn("argmax", source)

    def test_recovery_is_separate_from_advance_score(self) -> None:
        source = inspect.getsource(audit.build_features)
        self.assertIn('scores["EXHAUSTION_SCORE"] = scores[list(families)].mean', source)
        self.assertNotIn("F8", source)

    def test_current_state_preserves_closed_diagnostic(self) -> None:
        root = Path(__file__).resolve().parents[2]
        text = (root / "docs/CURRENT_STATE.md").read_text(encoding="utf-8")
        self.assertIn("BRRK-EXHAUSTION-EVENT-STUDY-0043 — complete diagnostic", text)
        self.assertIn("workflow run                         31381953131 / attempt 1", text)
        self.assertIn("7–14 day exhaustion-ranking signal appears feasible", text)
        self.assertIn("ID 0043 is closed against result-informed pruning, reweighting, threshold rescue", text)


if __name__ == "__main__":
    unittest.main()
