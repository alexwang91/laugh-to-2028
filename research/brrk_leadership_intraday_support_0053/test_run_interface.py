from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from research.brrk_leadership_intraday_support_0053 import run_once
from research.brrk_leadership_intraday_support_0053 import support_funnel as sf


class Test0053RunInterface(unittest.TestCase):
    def _measurement(self, blocks: int = 12) -> sf.FunnelMeasurement:
        def tr(name, authority, train, shadow, block, rows, complete):
            return sf.TrackSupportResult(
                name=name,
                authority=authority,
                training_support_required=train,
                shadow_support_required=shadow,
                block_length=block,
                first_training_support_timestamp="2022-01-01T00:00:00Z",
                first_shadow_origin_timestamp="2022-01-01T00:00:00Z",
                first_shadow_support_satisfied_timestamp="2023-01-01T00:00:00Z",
                calibration_activation_refit_timestamp="2023-01-15T00:00:00Z",
                first_formal_origin_timestamp="2023-01-15T00:00:00Z",
                last_formal_origin_timestamp="2026-01-01T00:00:00Z",
                formal_rows=rows,
                complete_blocks=complete,
                trailing_partial_rows=rows % block,
                formal_calendar_span_days=1082.0,
                formal_eligibility_rate=0.55,
            )
        return sf.FunnelMeasurement(
            research_id=sf.RESEARCH_ID,
            payload_sha256=sf.EXPECTED_PAYLOAD_SHA256,
            common_start="2020-08-11T04:00:00Z",
            common_end="2026-08-02T20:00:00Z",
            raw_common_bars=13097,
            feature_valid_bars=11657,
            eligible_feature_valid_bars=6400,
            pre_formal_eligibility_rate=0.549,
            max_feature_history_bars=1440,
            max_target_maturity_bars=336,
            refit_bars=168,
            tracks={
                "A": tr("A", "PRIMARY_CALENDAR_EQUIVALENT", 2190, 2190, 336, blocks * 336, blocks),
                "B": tr("B", "DIAGNOSTIC_RAW_ROW_MULTIPLICATION_ONLY", 365, 365, 56, 5000, 89),
                "C": tr("C", "DIAGNOSTIC_HYBRID_EARLIER_BURNIN_ONLY", 365, 365, 336, 5000, 14),
            },
        )

    def test_attempt_marker_precedes_real_measurement(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            payload = root / "payload.json"
            payload.write_text("{}")
            result = root / "SUPPORT_RESULT.json"
            execution = root / "EXECUTION.json"
            attempt = root / "RUN_ATTEMPT.marker"
            marker = root / "RUN_ONCE.marker"

            def fake_measure(_):
                self.assertTrue(attempt.exists(), "attempt marker must exist before measurement")
                self.assertFalse(result.exists())
                return self._measurement(12)

            with patch.object(run_once, "preflight", return_value={"git_head_sha": "abc"}), patch.object(sf, "measure_support_funnel", side_effect=fake_measure):
                out = run_once.evaluate(payload=payload, result=result, execution=execution, attempt=attempt, marker=marker, expected_head_sha="abc")
            self.assertEqual(out["classification"], "PASS_4H_CALENDAR_EQUIVALENT_SUPPORT_FEASIBLE")
            self.assertTrue(result.exists())
            self.assertTrue(execution.exists())
            self.assertTrue(marker.exists())
            self.assertFalse(json.loads(marker.read_text())["same_id_rerun_allowed"])

    def test_track_a_failure_cannot_be_rescued_by_b_or_c(self):
        measurement = self._measurement(11)
        result = run_once._result_from_measurement("abc", measurement, run_once._schema())
        self.assertEqual(result["classification"], "FAIL_4H_DOES_NOT_SOLVE_0048_SUPPORT_CONSTRAINT")
        self.assertGreater(result["measurement"]["tracks"]["B"]["complete_blocks"], 12)
        self.assertGreater(result["measurement"]["tracks"]["C"]["complete_blocks"], 12)

    def test_marker_recovery_does_not_remeasure(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            result = root / "SUPPORT_RESULT.json"
            execution = root / "EXECUTION.json"
            attempt = root / "RUN_ATTEMPT.marker"
            marker = root / "RUN_ONCE.marker"
            attempt.write_text(json.dumps({"x": 1}) + "\n")
            support_result = run_once._result_from_measurement("abc", self._measurement(12), run_once._schema())
            result.write_text(json.dumps(support_result, indent=2) + "\n")
            execution_value = {
                "research_id": sf.RESEARCH_ID,
                "git_head_sha": "abc",
                "completed_at_utc": "2026-01-01T00:00:00Z",
                "attempt_marker_sha256": run_once._sha256_file(attempt),
                "support_result_sha256": run_once._sha256_file(result),
            }
            execution.write_text(json.dumps(execution_value, indent=2) + "\n")
            with patch.object(run_once, "_verify_expected_head", return_value="abc"), patch.object(run_once, "_verify_upstream_blobs"), patch.object(sf, "measure_support_funnel", side_effect=AssertionError("must not remeasure")):
                value = run_once.recover_marker(result=result, execution=execution, attempt=attempt, marker=marker, expected_head_sha="abc")
            self.assertTrue(value["recovered_without_remeasurement"])
            self.assertTrue(marker.exists())

    def test_runtime_artifacts_absent_on_boundary_branch(self):
        here = Path(__file__).resolve().parent
        for name in ["SUPPORT_RESULT.json", "EXECUTION.json", "RUN_ATTEMPT.marker", "RUN_ONCE.marker"]:
            self.assertFalse((here / name).exists(), name)


if __name__ == "__main__":
    unittest.main()
