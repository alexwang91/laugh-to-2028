from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(name: str):
    return json.loads((HERE / name).read_text(encoding="utf-8"))


def canonical_sha(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")
    ).hexdigest()


class ImmutableCloseoutContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = load("METHOD_RESULT.json")
        cls.execution = load("EXECUTION.json")
        cls.attempt = load("RUN_ATTEMPT.marker")
        cls.marker = load("RUN_ONCE.marker")
        cls.closeout = load("CLOSEOUT.json")

    def test_result_identity_and_classification(self):
        self.assertEqual(self.result["research_id"], "BRRK-LEADERSHIP-4H-NATIVE-READINESS-0054")
        self.assertEqual(self.result["classification"], "FAIL_4H_NATIVE_TRAINING_PRECISION_NOT_ESTABLISHED")
        self.assertEqual(self.closeout["result_status"], self.result["classification"])
        self.assertEqual(
            self.closeout["closeout_status"],
            "FAIL_4H_NATIVE_TRAINING_PRECISION_NOT_ESTABLISHED / CLOSED",
        )

    def test_runtime_hash_chain_is_exact(self):
        self.assertEqual(self.execution["attempt_marker_sha256"], canonical_sha(self.attempt))
        self.assertEqual(self.execution["method_result_sha256"], canonical_sha(self.result))
        self.assertEqual(self.marker["attempt_marker_sha256"], canonical_sha(self.attempt))
        self.assertEqual(self.marker["method_result_sha256"], canonical_sha(self.result))
        self.assertEqual(self.marker["execution_sha256"], canonical_sha(self.execution))
        locked = self.closeout["hash_locked_result_identity"]
        self.assertEqual(locked["attempt_marker_sha256"], canonical_sha(self.attempt))
        self.assertEqual(locked["method_result_sha256"], canonical_sha(self.result))
        self.assertEqual(locked["execution_sha256"], canonical_sha(self.execution))

    def test_training_failure_is_binding_and_downstream_gates_absent(self):
        m = self.result["measurement"]
        self.assertIsNone(m["training_readiness"])
        self.assertIsNone(m["calibration_readiness"])
        self.assertIsNone(m["reserved_support"])
        records = m["training_records"]
        self.assertGreater(len(records), 0)
        eligible = [r for r in records if r["p90_width"] is not None]
        self.assertGreater(len(eligible), 0)
        self.assertEqual(sum(bool(r["passed"]) for r in eligible), 0)
        self.assertGreaterEqual(max(r["matured_eligible_count"] for r in records), 672)
        self.assertGreater(min(r["p90_width"] for r in eligible), 0.10)
        self.assertGreater(min(r["max_width"] for r in eligible), 0.20)
        downstream = self.closeout["downstream_gate_status"]
        self.assertFalse(downstream["calibration_stage_eligible"])
        self.assertFalse(downstream["reserved_suffix_support_stage_eligible"])
        self.assertFalse(downstream["new_predictive_study_unlocked_by_0054"])
        self.assertFalse(downstream["0049_concentration_unlocked"])

    def test_numerical_identification_was_not_the_binding_failure(self):
        first = self.closeout["training_precision_evidence"]["first_hac_eligible_refit"]
        self.assertGreaterEqual(first["matured_eligible_count"], 672)
        self.assertGreater(first["hac_min_eigenvalue"], 0.0)
        self.assertGreater(first["hessian_min_eigenvalue"], 0.0)
        self.assertGreater(first["p90_width"], 0.10)
        self.assertGreater(first["max_width"], 0.20)

    def test_post_2022_firewall_and_no_predictive_or_portfolio_authority(self):
        for value in (self.result["authority"], self.execution, self.closeout["authority"]):
            self.assertFalse(value["post_2022_target_values_read"])
            self.assertFalse(value["predictive_performance_metrics_executed"])
            self.assertFalse(value["portfolio_economics_executed"])
            self.assertFalse(value["production_authorized"])
        self.assertFalse(self.closeout["scientific_implication"]["independent_oos_claim_allowed"])
        self.assertTrue(self.closeout["scientific_implication"]["post_2022_target_suffix_preserved_from_0054"])

    def test_closed_to_same_id_rerun_retuning_rescue(self):
        self.assertEqual(
            self.marker["status"],
            "VALID_METHODOLOGY_MEASUREMENT_COMPLETE_CLOSED_TO_SAME_ID_RERUN",
        )
        self.assertTrue(self.marker["finalized_without_remeasurement"])
        for key in ("same_id_rerun_allowed", "same_id_retuning_allowed", "same_id_rescue_allowed"):
            self.assertFalse(self.marker[key])
            self.assertFalse(self.closeout["closure"][key])

    def test_no_forbidden_result_artifacts_or_current_state_drift(self):
        forbidden = ["PREDICTIVE_RESULT.json", "PORTFOLIO_RESULT.json", "WINNER_LABELS.json"]
        self.assertFalse([name for name in forbidden if (HERE / name).exists()])
        state = (ROOT / "docs/CURRENT_STATE.md").read_text(encoding="utf-8")
        required = [
            "FAIL_4H_NATIVE_TRAINING_PRECISION_NOT_ESTABLISHED / CLOSED",
            "production_authorized_components = []",
            "production_authorized = false",
            "signature_authorized = false",
            "order_submission_authorized = false",
            "BRRK intraday support 0053             FAIL_4H_DOES_NOT_SOLVE_0048_SUPPORT_CONSTRAINT / CLOSED",
            "BRRK leadership rotation 0048         MEASUREMENT_INCONCLUSIVE_INSUFFICIENT_SUPPORT / CLOSED",
        ]
        missing = [item for item in required if item not in state]
        self.assertFalse(missing, missing)


if __name__ == "__main__":
    unittest.main()
