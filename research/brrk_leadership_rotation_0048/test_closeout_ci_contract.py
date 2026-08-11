from __future__ import annotations

import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent


class CloseoutCIAttestationContractTest(unittest.TestCase):
    def test_closeout_ci_attestation_is_non_recomputing_and_green(self):
        record = json.loads((HERE / "CLOSEOUT_CI.json").read_text(encoding="utf-8"))
        self.assertEqual(record["research_id"], "BRRK-LEADERSHIP-ROTATION-0048")
        self.assertEqual(record["workflow_run_id"], 31507035505)
        self.assertEqual(record["workflow_job_id"], 93831137947)
        self.assertEqual(record["tests_run"], 33)
        self.assertEqual(record["tests_passed"], 33)
        self.assertEqual(record["tests_failed"], 0)
        self.assertEqual(record["engine_and_runner_py_compile"], "PASS")
        self.assertEqual(record["immutable_bundle_presence"], "PASS")
        self.assertEqual(record["exact_hash_binding"], "PASS")
        self.assertEqual(record["g1_stopping_rule"], "PASS")
        self.assertFalse(record["model_recomputation_performed"])
        self.assertFalse(record["historical_scientific_evaluation_performed"])
        self.assertTrue(record["temporary_workflow_removed_after_attestation"])
        for key, value in record["authority"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
