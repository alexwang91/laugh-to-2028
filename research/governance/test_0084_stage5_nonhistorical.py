from __future__ import annotations

import unittest

from research.brrk_crypto_cross_sectional_factor_atlas_replacement_0084.integration_qualification import (
    run_integration_qualification,
)
from research.brrk_crypto_cross_sectional_factor_atlas_replacement_0084.qualification import (
    run_synthetic_qualification,
)


class Test0084Stage5NonhistoricalQualification(unittest.TestCase):
    def _assert_zero_result_pass(self, result: dict[str, object]) -> None:
        self.assertEqual(result["qualification"], "PASS")
        self.assertEqual(result["controlled_history_reads"], 0)
        self.assertEqual(result["scientific_source_network_fetches"], 0)
        self.assertEqual(result["stage8_attempt_consumed"], 0)
        checks = result["checks"]
        self.assertIsInstance(checks, dict)
        self.assertTrue(checks)
        self.assertTrue(all(bool(value) for value in checks.values()))

    def test_stage4_mechanics_synthetic_only(self) -> None:
        self._assert_zero_result_pass(run_synthetic_qualification())

    def test_end_to_end_interface_synthetic_only(self) -> None:
        self._assert_zero_result_pass(run_integration_qualification())


if __name__ == "__main__":
    unittest.main()
