from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "research" / "governance" / "prospective_five_gate_lifecycle_v1.json"


class ProspectiveFiveGateLifecycleV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))

    def test_exact_ten_logical_stages_preserved(self) -> None:
        self.assertEqual(
            self.contract["logical_stages"],
            [
                "OWNER-FIRST",
                "DESIGN",
                "PREREGISTRATION",
                "IMPLEMENTATION",
                "NONHISTORICAL QUALIFICATION",
                "CONTROLLED BOUNDARY",
                "ZERO-RESULT PREFLIGHT",
                "UNIQUE CONTROLLED ATTEMPT",
                "RESULT",
                "IMMUTABLE CLOSEOUT",
            ],
        )
        self.assertEqual(self.contract["logical_stage_count"], 10)

    def test_exact_five_gate_partition(self) -> None:
        gates = self.contract["merge_gates"]
        self.assertEqual([row["gate"] for row in gates], ["SPEC_FREEZE", "BUILD", "ARM", "RUN", "SEAL"])
        flattened = [stage for row in gates for stage in row["logical_stages"]]
        self.assertEqual(flattened, self.contract["logical_stages"])
        self.assertEqual(self.contract["merge_gate_count"], 5)

    def test_strict_prospective_boundary(self) -> None:
        self.assertEqual(self.contract["status"], "PROSPECTIVE_NEW_IDS_ONLY")
        self.assertFalse(self.contract["applies_to_preexisting_research_ids"])
        self.assertFalse(self.contract["transfers_historical_lifecycle_credit"])
        self.assertIn("EXPLICITLY_ADOPTING_NEW_RESEARCH_IDS_ONLY", self.contract["activation"])

    def test_runner_and_exactly_once_guards_remain_strict(self) -> None:
        self.assertEqual(self.contract["required_controlled_runner"], "CONTROLLED_RESEARCH_RUNNER_V1")
        self.assertGreaterEqual(self.contract["minimum_runner_consecutive_synthetic_lifecycles"], 20)
        self.assertFalse(self.contract["pre_marker_payload_read_allowed"])
        self.assertTrue(self.contract["marker_before_controlled_payload_read_required"])
        self.assertTrue(self.contract["exactly_once_scientific_engine_required"])
        self.assertFalse(self.contract["same_id_rescue_after_consumed_attempt_allowed"])
        self.assertFalse(self.contract["result_informed_retuning_allowed"])
        self.assertFalse(self.contract["development_history_may_be_called_independent_oos"])

    def test_parallelism_does_not_grant_production_authority(self) -> None:
        self.assertTrue(self.contract["independent_tracks_may_run_in_parallel_without_declared_dependency"])
        self.assertFalse(self.contract["production_authorized"])
        self.assertFalse(self.contract["signature_authorized"])
        self.assertFalse(self.contract["order_submission_authorized"])


if __name__ == "__main__":
    unittest.main()
